"""Integration tests for PRIESSTESS scripts."""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

BIN_DIR = Path(__file__).parent.parent / "bin"


@pytest.mark.integration
class TestIntegration:
    """Integration tests with mocked external tools."""

    @pytest.mark.skip(reason="Requires actual annotated sequences with correct format")
    def test_annotate_then_scan(self, temp_dir):
        """Test pipeline: annotate alphabets then scan with PFM."""
        # Create input for annotate_alphabets
        anno_input = os.path.join(temp_dir, "sequences.tab")
        with open(anno_input, "w") as f:
            f.write("ACGU\t.((.)\tEHRRE\n")
            f.write("UGCA\t((..)\tMPPLE\n")

        # Run annotate_alphabets
        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "annotate_alphabets.py"),
                anno_input,
                os.path.join(temp_dir, "anno"),
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 0

        # Verify output exists
        anno_output = os.path.join(temp_dir, "anno_alphabet_annotations.tab")
        assert os.path.exists(anno_output)

    @pytest.mark.skip(reason="Requires skopt which may not be installed in test environment")
    def test_model_training_and_testing_integration(self, temp_dir):
        """Test model training and evaluation pipeline."""
        # Create synthetic training data
        n_samples = 50
        n_features = 10
        X = np.random.randn(n_samples, n_features)
        y = np.random.randint(0, 2, n_samples)
        data = np.column_stack([y, X])

        train_file = os.path.join(temp_dir, "train_data.tab")
        with open(train_file, "w") as f:
            f.write("label\t" + "\t".join([f"feature_{i}" for i in range(n_features)]) + "\n")
            np.savetxt(f, data, delimiter="\t", fmt="%.6f")

        # Train model
        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "PRIESSTESS_logistic_regression.py"),
                train_file,
                "10",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 0

        # Check model files were created
        assert os.path.exists(os.path.join(temp_dir, "PRIESSTESS_model.sav"))
        assert os.path.exists(os.path.join(temp_dir, "PRIESSTESS_model_weights.tab"))

        # Test the model
        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "test_PRIESSTESS_model.py"),
                train_file,
                train_file,
                os.path.join(temp_dir, "PRIESSTESS_model.sav"),
                "integration_test",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 0

        # Verify AUROC output
        auroc_file = os.path.join(temp_dir, "test_PRIESSTESS_model_ON_integration_test_auroc.tab")
        assert os.path.exists(auroc_file)

        with open(auroc_file) as f:
            auroc = float(f.read().strip())
        assert 0 <= auroc <= 1

    def test_error_propagation(self, temp_dir):
        """Test that errors are properly reported through the pipeline."""
        # Try to evaluate a non-existent model
        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "test_PRIESSTESS_model.py"),
                "nonexistent1.tab",
                "nonexistent2.tab",
                "nonexistent.model",
                "test",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 1
        assert "Error" in result.stderr

    def test_utility_functions_composition(self):
        """Test that utility functions work together."""
        import subprocess

        # Test log2 of a power of 10
        result1 = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2.py"), "1000"],
            capture_output=True,
            text=True,
        )
        assert result1.returncode == 0
        log2_result = float(result1.stdout.strip())

        # Compare with log2_scinot
        result2 = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2_scinot.py"), "1e3"],
            capture_output=True,
            text=True,
        )
        assert result2.returncode == 0
        scinot_result = float(result2.stdout.strip())

        # Results should be very close
        assert log2_result == pytest.approx(scinot_result, abs=0.01)
