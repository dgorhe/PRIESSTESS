import os
import pickle
import sys

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from skopt import BayesSearchCV
from skopt.space import Real

try:
    trainfile = sys.argv[1]
    pred_loss = float(sys.argv[2])
except IndexError:
    sys.stderr.write("Error: Missing required arguments\n")
    sys.stderr.write("Usage: PRIESSTESS_logistic_regression.py <trainfile> <pred_loss>\n")
    sys.exit(1)
except ValueError:
    sys.stderr.write("Error: pred_loss must be a number\n")
    sys.exit(1)

if not os.path.exists(trainfile):
    sys.stderr.write(f"Error: Training file '{trainfile}' not found\n")
    sys.exit(1)

pred_loss = (100 - pred_loss) / 100

try:
    trainset = np.loadtxt(trainfile, delimiter="\t", skiprows=1)
except (IOError, ValueError) as e:
    sys.stderr.write(f"Error reading training file '{trainfile}': {e}\n")
    sys.exit(1)

X = trainset[:, 1 : len(trainset[0])]
Y = trainset[:, 0]

scaler = StandardScaler()
scaler.fit(X)
X = scaler.transform(X)

Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=0.2, random_state=42)

try:
    afile = open(trainfile, "r")
    alph = afile.readline().strip().split("\t")[1:]
    afile.close()
except IOError as e:
    sys.stderr.write(f"Error reading alphabet from file: {e}\n")
    sys.exit(1)

# PREPARE TO RUN LOGISTIC REGRESSION
lr = LogisticRegression(solver="saga", penalty="l1", warm_start=True)

# DEFINE PARAMETER GRID
param_grid = {
    "penalty": ["l1"],
    "solver": ["saga"],
    "C": Real(low=1e-6, high=100, prior="log-uniform"),
}

# SET UP OPTIMIZER
opt = BayesSearchCV(lr, param_grid, n_iter=30, random_state=1234, verbose=0, n_jobs=1)

try:
    # FIT PARAMETERS
    opt.fit(Xtrain, Ytrain)

    # REDO LOGISTIC REGRESSION ON TRAIN DATA WITH BEST PARAMETERS
    lr = LogisticRegression(**opt.best_params_)
    lr.fit(Xtrain, Ytrain)

    # GET AUROC
    aurocs = []
    numcoef = []
    Cvalues = []

    auroc = roc_auc_score(Ytest, lr.predict_proba(Xtest)[:, 1])
    aurocs.append(auroc)
    numcoef.append(len([i for i in lr.coef_[0] if i != 0]))
    Cvalues.append(lr.C)

    lr = LogisticRegression(solver="saga", penalty="l1", C=Cvalues[0], warm_start=False)

    currauroc = auroc
    while currauroc > 0.50:
        currC = lr.C
        lr.C = 3 * currC / 4
        lr.fit(Xtrain, Ytrain)
        currauroc = roc_auc_score(Ytest, lr.predict_proba(Xtest)[:, 1])
        aurocs.append(currauroc)
        numcoef.append(len([i for i in lr.coef_[0] if i != 0]))
        Cvalues.append(lr.C)

    auroc_cutoff = ((aurocs[0] - 0.5) * pred_loss) + 0.5
    aurocs = np.array(aurocs)
    index = np.argwhere(aurocs > auroc_cutoff)[-1][0]
    C = Cvalues[index]

    lr = LogisticRegression(solver="saga", penalty="l1", warm_start=False, C=C)
    lr.fit(X, Y)

    pickle.dump(lr, open("PRIESSTESS_model.sav", "wb"))
    ifile = open("PRIESSTESS_model_weights.tab", "w")
    for i in range(len(lr.coef_[0])):
        ifile.write(alph[i] + "\t" + str(lr.coef_[0][i]) + "\n")
    ifile.close()

except Exception as e:
    sys.stderr.write(f"Error during model training: {e}\n")
    sys.exit(1)
