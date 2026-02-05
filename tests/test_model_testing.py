"""Tests for test_PRIESSTESS_model.py script."""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

BIN_DIR = Path(__file__).parent.parent / "bin"


class TestPRIESTESSModelTesting:
    """Tests for the test_PRIESSTESS_model.py script."""

    def test_model_testing_basic(self, temp_dir, synthetic_training_data, synthetic_model):
        """Test basic model evaluation."""
        # Use same training data as test data for simplicity
        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "test_PRIESSTESS_model.py"),
                synthetic_training_data,
                synthetic_training_data,
                synthetic_model,
                "test_data",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 0

        # Check output file was created
        output_file = os.path.join(
            temp_dir, "test_test_model_ON_test_data_auroc.tab"
        )
        assert os.path.exists(output_file)

        # Read AUROC value
        with open(output_file) as f:
            auroc = float(f.read().strip())
        assert 0 <= auroc <= 1

    def test_model_testing_missing_arguments(self, temp_dir):
        """Test with missing arguments."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "test_PRIESSTESS_model.py")],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 1
        assert "Missing required arguments" in result.stderr

    def test_model_testing_file_not_found(self, temp_dir, synthetic_model):
        """Test with non-existent training file."""
        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "test_PRIESSTESS_model.py"),
                "nonexistent_train.tab",
                "nonexistent_test.tab",
                synthetic_model,
                "test_data",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 1
        assert "not found" in result.stderr

    def test_model_testing_invalid_data_format(self, temp_dir, synthetic_model):
        """Test with invalid data format."""
        # Create file with non-numeric data
        bad_data_file = os.path.join(temp_dir, "bad_data.tab")
        with open(bad_data_file, "w") as f:
            f.write("label\tfeature1\tfeature2\n")
            f.write("not_a_number\tinvalid\tdata\n")

        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "test_PRIESSTESS_model.py"),
                bad_data_file,
                bad_data_file,
                synthetic_model,
                "test_data",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 1
        assert "Error" in result.stderr

    def test_model_testing_feature_mismatch(self, temp_dir, synthetic_model):
        """Test with mismatched feature counts."""
        # Create train file with 10 features
        train_file = os.path.join(temp_dir, "train.tab")
        train_data = np.random.randn(10, 11)  # 10 samples, 10 features + 1 label
        with open(train_file, "w") as f:
            f.write("label\t" + "\t".join([f"f{i}" for i in range(10)]) + "\n")
            np.savetxt(f, train_data, delimiter="\t", fmt="%.6f")

        # Create test file with 5 features (mismatch!)
        test_file = os.path.join(temp_dir, "test.tab")
        test_data = np.random.randn(5, 6)  # 5 samples, 5 features + 1 label
        with open(test_file, "w") as f:
            f.write("label\t" + "\t".join([f"f{i}" for i in range(5)]) + "\n")
            np.savetxt(f, test_data, delimiter="\t", fmt="%.6f")

        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "test_PRIESSTESS_model.py"),
                train_file,
                test_file,
                synthetic_model,
                "test_data",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 1
        assert "mismatch" in result.stderr.lower()

    def test_model_testing_invalid_model(self, temp_dir, synthetic_training_data):
        """Test with invalid model file."""
        bad_model = os.path.join(temp_dir, "bad_model.sav")
        with open(bad_model, "w") as f:
            f.write("not a valid pickle")

        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "test_PRIESSTESS_model.py"),
                synthetic_training_data,
                synthetic_training_data,
                bad_model,
                "test_data",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 1
        assert "Error loading model" in result.stderr
