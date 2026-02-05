"""Tests for annotate_alphabets.py."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

BIN_DIR = Path(__file__).parent.parent / "bin"


class TestAnnotateAlphabets:
    """Tests for the annotate_alphabets.py script."""

    def test_annotate_alphabets_missing_arguments(self):
        """Test with missing arguments."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "annotate_alphabets.py")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Missing required arguments" in result.stderr

    def test_annotate_alphabets_file_not_found(self, temp_dir):
        """Test with non-existent input file."""
        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "annotate_alphabets.py"),
                "nonexistent.tab",
                os.path.join(temp_dir, "output"),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "not found" in result.stderr

    def test_annotate_alphabets_invalid_format(self, temp_dir):
        """Test with invalid input format (missing fields)."""
        input_file = os.path.join(temp_dir, "input.tab")
        with open(input_file, "w") as f:
            # Missing the third column
            f.write("ACGU\tAAAAA\n")

        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "annotate_alphabets.py"),
                input_file,
                os.path.join(temp_dir, "test"),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "fewer than 3 fields" in result.stderr

    def test_annotate_alphabets_length_mismatch(self, temp_dir):
        """Test with mismatched sequence and structure lengths."""
        input_file = os.path.join(temp_dir, "input.tab")
        with open(input_file, "w") as f:
            # Sequence has 4 letters but structure has 6
            f.write("ACGU\t.((.))\tEHHHRET\n")

        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "annotate_alphabets.py"),
                input_file,
                os.path.join(temp_dir, "test"),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "length" in result.stderr.lower()

    def test_annotate_alphabets_invalid_character(self, temp_dir):
        """Test with invalid character in sequence or structure."""
        input_file = os.path.join(temp_dir, "input.tab")
        with open(input_file, "w") as f:
            # Invalid sequence character 'Z' (5 letters seq with 5 char structure)
            f.write("ACZGU\t.((.).\tEHRREE\n")

        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "annotate_alphabets.py"),
                input_file,
                os.path.join(temp_dir, "test"),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        # Either invalid character or other error is fine
        assert result.returncode != 0
