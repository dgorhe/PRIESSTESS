"""Tests for utility scripts log2.py and log2_scinot.py."""
import subprocess
import sys
from pathlib import Path

import pytest

# Get the bin directory
BIN_DIR = Path(__file__).parent.parent / "bin"


class TestLog2:
    """Tests for log2.py utility."""

    def test_log2_basic(self):
        """Test log2 of basic numbers."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2.py"), "8"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert float(result.stdout.strip()) == pytest.approx(3.0)

    def test_log2_power_of_two(self):
        """Test log2 of various powers of 2."""
        for num, expected in [(1, 0.0), (2, 1.0), (4, 2.0), (16, 4.0), (1024, 10.0)]:
            result = subprocess.run(
                [sys.executable, str(BIN_DIR / "utils" / "log2.py"), str(num)],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            assert float(result.stdout.strip()) == pytest.approx(expected)

    def test_log2_float(self):
        """Test log2 with floating point numbers."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2.py"), "2.5"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        value = float(result.stdout.strip())
        assert value == pytest.approx(1.3219, abs=0.001)

    def test_log2_missing_argument(self):
        """Test log2 with missing argument."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2.py")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Missing required argument" in result.stderr

    def test_log2_invalid_number(self):
        """Test log2 with invalid input."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2.py"), "not_a_number"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "not a valid number" in result.stderr

    def test_log2_negative_number(self):
        """Test log2 with negative number (should fail)."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2.py"), "-5"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "positive number" in result.stderr


class TestLog2Scinot:
    """Tests for log2_scinot.py utility."""

    def test_log2_scinot_basic(self):
        """Test log2_scinot with basic scientific notation."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2_scinot.py"), "1e3"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        value = float(result.stdout.strip())
        # log2(1*10^3) = log2(1) + 3*log2(10)
        expected = 0 + 3 * 3.32193
        assert value == pytest.approx(expected, abs=0.01)

    def test_log2_scinot_with_mantissa(self):
        """Test log2_scinot with mantissa and exponent."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2_scinot.py"), "2e2"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        value = float(result.stdout.strip())
        # log2(2*10^2) = log2(2) + 2*log2(10)
        expected = 1.0 + 2 * 3.32193
        assert value == pytest.approx(expected, abs=0.01)

    def test_log2_scinot_regular_number(self):
        """Test log2_scinot with regular (non-scientific) notation."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2_scinot.py"), "16"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert float(result.stdout.strip()) == pytest.approx(4.0)

    def test_log2_scinot_comma_separator(self):
        """Test log2_scinot with comma as decimal separator."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2_scinot.py"), "1,6e-300"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Should not crash and should compute something
        value = float(result.stdout.strip())
        assert isinstance(value, float)

    def test_log2_scinot_negative_exponent(self):
        """Test log2_scinot with negative exponent."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2_scinot.py"), "1e-10"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        value = float(result.stdout.strip())
        # log2(1*10^-10) = 0 + (-10)*log2(10)
        expected = -10 * 3.32193
        assert value == pytest.approx(expected, abs=0.01)

    def test_log2_scinot_missing_argument(self):
        """Test log2_scinot with missing argument."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2_scinot.py")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Missing required argument" in result.stderr

    def test_log2_scinot_invalid_format(self):
        """Test log2_scinot with invalid number format."""
        result = subprocess.run(
            [sys.executable, str(BIN_DIR / "utils" / "log2_scinot.py"), "not_valid"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Invalid number format" in result.stderr
