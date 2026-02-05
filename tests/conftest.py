"""Shared pytest fixtures for PRIESSTESS tests."""
import os
import pickle
import tempfile
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def test_data_dir():
    """Get the path to the test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def tiny_fg_file(test_data_dir):
    """Get path to tiny foreground test data."""
    return str(test_data_dir / "tiny_fg.tab")


@pytest.fixture
def tiny_bg_file(test_data_dir):
    """Get path to tiny background test data."""
    return str(test_data_dir / "tiny_bg.tab")


@pytest.fixture
def synthetic_training_data(temp_dir):
    """Create synthetic training data file for testing."""
    n_samples = 20
    n_features = 10

    # Create data: first column is binary label, rest are features
    X = np.random.randn(n_samples, n_features)
    y = np.random.randint(0, 2, n_samples)
    data = np.column_stack([y, X])

    # Create header with feature names
    header = "label\t" + "\t".join([f"feature_{i}" for i in range(n_features)])
    filepath = os.path.join(temp_dir, "training_data.tab")

    # Save with header
    with open(filepath, "w") as f:
        f.write(header + "\n")
        np.savetxt(f, data, delimiter="\t", fmt="%g")

    return filepath


@pytest.fixture
def synthetic_model(temp_dir, synthetic_training_data):
    """Create a synthetic logistic regression model for testing."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    # Load training data
    data = np.loadtxt(synthetic_training_data, delimiter="\t", skiprows=1)
    X = data[:, 1:]
    y = data[:, 0]

    # Train a simple model
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    lr = LogisticRegression(solver="lbfgs", max_iter=1000)
    lr.fit(X_scaled, y)

    # Save model
    model_path = os.path.join(temp_dir, "test_model.sav")
    pickle.dump(lr, open(model_path, "wb"))

    return model_path


@pytest.fixture
def simple_fasta(temp_dir):
    """Create a simple FASTA file for testing."""
    fasta_content = """>seq1
ACGUACGUACGU
>seq2
GCUAGCUAGCUA
>seq3
UGACUGACUGAC
"""
    filepath = os.path.join(temp_dir, "test.fa")
    with open(filepath, "w") as f:
        f.write(fasta_content)
    return filepath


@pytest.fixture
def simple_pfm(temp_dir):
    """Create a simple PFM file for testing."""
    pfm_content = """A\t0.7\t0.1\t0.1
C\t0.1\t0.7\t0.1
G\t0.1\t0.1\t0.7
U\t0.1\t0.1\t0.1
"""
    filepath = os.path.join(temp_dir, "test_motif_1.txt")
    with open(filepath, "w") as f:
        f.write(pfm_content)
    return filepath
