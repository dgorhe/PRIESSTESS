"""Tests for PFM_scan.py."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

BIN_DIR = Path(__file__).parent.parent / "bin"


class TestPFMScan:
    """Tests for the PFM_scan.py script."""

    def test_pfm_scan_basic(self, temp_dir, simple_fasta, simple_pfm):
        """Test basic PFM scanning."""
        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "PFM_scan.py"),
                "-a",
                "seq-4",
                "-f",
                simple_fasta,
                "-p",
                simple_pfm.replace("_1.txt", ""),
                "-n",
                "1",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 0

        # Check output file was created
        output_file = os.path.join(temp_dir, "test_PFM_scan_sum_top_1.tab")
        assert os.path.exists(output_file)

        # Check output format
        with open(output_file) as f:
            lines = f.readlines()
        assert len(lines) == 4  # header + 3 sequences
        assert "seq_id" in lines[0]
        assert "test_motif" in lines[0]

    def test_pfm_scan_topn_parameter(self, temp_dir, simple_fasta, simple_pfm):
        """Test with different topN values."""
        for topn in [1, 2, 5]:
            result = subprocess.run(
                [
                    sys.executable,
                    str(BIN_DIR / "PFM_scan.py"),
                    "-a",
                    "seq-4",
                    "-f",
                    simple_fasta,
                    "-p",
                    simple_pfm.replace("_1.txt", ""),
                    "-n",
                    str(topn),
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )
            assert result.returncode == 0

    def test_pfm_scan_missing_arguments(self, temp_dir):
        """Test with missing required arguments."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "PFM_scan.py")],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode != 0  # Should fail

    def test_pfm_scan_invalid_alphabet(self, temp_dir, simple_fasta, simple_pfm):
        """Test with invalid alphabet."""
        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "PFM_scan.py"),
                "-a",
                "invalid-alphabet",
                "-f",
                simple_fasta,
                "-p",
                simple_pfm.replace("_1.txt", ""),
                "-n",
                "1",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 1
        assert "Invalid alphabet" in result.stderr

    def test_pfm_scan_fasta_not_found(self, temp_dir, simple_pfm):
        """Test with non-existent FASTA file."""
        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "PFM_scan.py"),
                "-a",
                "seq-4",
                "-f",
                "nonexistent.fa",
                "-p",
                simple_pfm.replace("_1.txt", ""),
                "-n",
                "1",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 1
        assert "not found" in result.stderr

    def test_pfm_scan_topn_invalid(self, temp_dir, simple_fasta, simple_pfm):
        """Test with invalid topN value."""
        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "PFM_scan.py"),
                "-a",
                "seq-4",
                "-f",
                simple_fasta,
                "-p",
                simple_pfm.replace("_1.txt", ""),
                "-n",
                "0",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 1
        assert "greater than 0" in result.stderr

    def test_pfm_scan_no_pfm_files(self, temp_dir, simple_fasta):
        """Test when no PFM files match the prefix."""
        result = subprocess.run(
            [
                sys.executable,
                str(BIN_DIR / "PFM_scan.py"),
                "-a",
                "seq-4",
                "-f",
                simple_fasta,
                "-p",
                "nonexistent_prefix",
                "-n",
                "1",
            ],
            capture_output=True,
            text=True,
            cwd=temp_dir,
        )
        assert result.returncode == 1
        assert "No PFM files found" in result.stderr

    def test_pfm_scan_all_alphabets(self, temp_dir, simple_fasta, simple_pfm):
        """Test with different alphabet types."""
        for alphabet in ["seq-4", "struct-2", "struct-4", "seq-struct-8"]:
            # Note: this will only work with alphabets that match the PFM content
            # For a complete test, we'd need to create PFMs for each alphabet
            result = subprocess.run(
                [
                    sys.executable,
                    str(BIN_DIR / "PFM_scan.py"),
                    "-a",
                    alphabet,
                    "-f",
                    simple_fasta,
                    "-p",
                    simple_pfm.replace("_1.txt", ""),
                    "-n",
                    "1",
                ],
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )
            # May fail due to invalid characters, but shouldn't crash with bad alphabet error
            if result.returncode != 0:
                # If it fails, make sure it's not due to bad alphabet
                assert "Invalid alphabet" not in result.stderr
