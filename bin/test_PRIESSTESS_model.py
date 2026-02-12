import os
import pickle
import sys

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

try:
    trainfile = sys.argv[1]
    testfile = sys.argv[2]
    trainmodel = sys.argv[3]
    test_name = sys.argv[4]
except IndexError:
    sys.stderr.write("Error: Missing required arguments\n")
    sys.stderr.write("Usage: test_PRIESSTESS_model.py <trainfile> <testfile> <model> <test_name>\n")
    sys.exit(1)

# Validate file existence
for filepath, name in [(trainfile, "training"), (testfile, "test"), (trainmodel, "model")]:
    if not os.path.exists(filepath):
        sys.stderr.write(f"Error: {name.capitalize()} file '{filepath}' not found\n")
        sys.exit(1)

# Load in data
try:
    trainset = np.loadtxt(trainfile, delimiter="\t", skiprows=1)
except (IOError, ValueError) as e:
    sys.stderr.write(f"Error reading training file '{trainfile}': {e}\n")
    sys.exit(1)

try:
    testset = np.loadtxt(testfile, delimiter="\t", skiprows=1)
except (IOError, ValueError) as e:
    sys.stderr.write(f"Error reading test file '{testfile}': {e}\n")
    sys.exit(1)

Xtrain = trainset[:, 1 : len(trainset[0])]
Xtest = testset[:, 1 : len(testset[0])]
Ytest = testset[:, 0]

# Validate data shapes match
if Xtrain.shape[1] != Xtest.shape[1]:
    sys.stderr.write(
        f"Error: Feature count mismatch (train: {Xtrain.shape[1]}, test: {Xtest.shape[1]})\n"
    )
    sys.exit(1)

# Scale test values to the same scale as training values
scaler = StandardScaler()
scaler.fit(Xtrain)
Xtest = scaler.transform(Xtest)

# Load in the model
try:
    lr = pickle.load(open(trainmodel, "rb"))
except (pickle.UnpicklingError, IOError) as e:
    sys.stderr.write(f"Error loading model '{trainmodel}': {e}\n")
    sys.exit(1)

# Calculate AUROC
try:
    auroc = roc_auc_score(Ytest, lr.predict_proba(Xtest)[:, 1])
except Exception as e:
    sys.stderr.write(f"Error calculating AUROC: {e}\n")
    sys.exit(1)

# Write AUROC to file
outprefix = "test_" + trainmodel.split("/")[-1][:-4]
try:
    ifile = open(outprefix + "_ON_" + test_name + "_auroc.tab", "w")
    ifile.write(str(auroc) + "\n")
    ifile.close()
except IOError as e:
    sys.stderr.write(f"Error writing output file: {e}\n")
    sys.exit(1)
