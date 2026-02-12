# PRIESSTESS

PRIESSTESS (Predictive RBP-RNA InterpretablE Sequence-Structure moTif regrESSion) is a universal RNA motif-finding method that is applicable to diverse _in vitro_ RNA binding datasets. PRIESSTESS captures sequence specificity, structure specitifity, bipartite binding, and multiple distinct motifs.

PRIESSTESS consists of two steps. The first step generates a large collection of enriched motifs encompassing both RNA sequence and structure. The second step produces an aggregate model, which combines the motif scores into a single value, and gauges the relative importance of each motif.

Laverty, K.U., Jolma, A., Pour, S.E., Zheng, H., Ray, D., Morris, Q.D., Hughes, T.R. PRIESSTESS: interpretable, high-performing models of the sequence and structure preferences of RNA binding proteins. _Nucleic Acids Research_. 2022 https://doi.org/10.1093/nar/gkac694

## Installation

### Prerequisites: Installing make and gcc

Before installing PRIESSTESS, you need to have `make` and `gcc` (or a compatible C++ compiler) installed on your system. Follow the instructions for your operating system below.

#### macOS

1. **Install Xcode Command Line Tools** (includes `make` and `clang++`, which is compatible with gcc):

   ```bash
   xcode-select --install
   ```

   Follow the prompts in the pop-up window to complete the installation.

2. **Alternatively, install GCC via Homebrew** (if you prefer GCC over clang):

   ```bash
   # Install Homebrew if you don't have it
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   # Install GCC
   brew install gcc
   ```

3. **Verify installation**:
   ```bash
   make --version
   gcc --version  # or clang++ --version if using Xcode tools
   ```

#### Linux

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install build-essential
```

**Fedora/RHEL/CentOS:**

```bash
# For Fedora/RHEL 8+ and CentOS 8+
sudo dnf install gcc gcc-c++ make

# For older RHEL/CentOS 7
sudo yum install gcc gcc-c++ make
```

**Arch Linux:**

```bash
sudo pacman -S base-devel
```

**Verify installation**:

```bash
make --version
gcc --version
```

#### Windows

**Option 1: Using WSL (Windows Subsystem for Linux) - Recommended**

1. Install WSL2 following [Microsoft's official guide](https://docs.microsoft.com/en-us/windows/wsl/install)
2. Once WSL is installed, open a WSL terminal and follow the **Linux (Ubuntu/Debian)** instructions above

**Option 2: Using MSYS2**

1. Download and install [MSYS2](https://www.msys2.org/)
2. Open MSYS2 terminal and run:
   ```bash
   pacman -Syu
   pacman -S base-devel gcc
   ```

**Option 3: Using MinGW-w64**

1. Download [MinGW-w64](https://www.mingw-w64.org/downloads/)
2. Install and add to PATH
3. Install `make` separately or use `mingw32-make`

**Verify installation**:

```bash
make --version
gcc --version
```

### Quick Start with Conda (Recommended)

Once `make` and `gcc` are installed, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/dgorhe/PRIESSTESS.git
   cd PRIESSTESS
   ```
2. Compile the `parse_secondary_structure_v2` utility for your system (required; the binary is not distributed since it must be built for your OS and architecture):

   ```bash
   make
   ```

3. Ensure the PRIESSTESS code has executable permissions

   ```bash
   chmod +x PRIESSTESS PRIESSTESS_scan
   chmod -R +x bin/
   ```

4. Add PRIESSTESS to your PATH:

   ```bash
   # For bash/zsh (Linux/macOS/WSL)
   echo "export PATH=\"\$PATH:$(pwd)\"" >> ~/.bashrc  # or ~/.zshrc
   source ~/.bashrc  # or source ~/.zshrc

   # For Windows PowerShell
   # Add the PRIESSTESS directory to your PATH environment variable manually
   ```

5. Create and activate the conda environment

   ```bash
   conda env create -f env.yaml
   conda activate priesstess
   ```

6. Verify installation:
   ```bash
   PRIESSTESS --help
   ```

### Manual Installation

Download PRIESSTESS and add path to main directory to bash profile. Ensure that the directory is named "PRIESSTESS".

### Requirements

- `make` and C++ compiler (gcc/g++ or clang++) for building `parse_secondary_structure_v2` utility (see Prerequisites section above)

The conda environment (env.yaml) includes all dependencies. If not using conda, ensure:

- RNAfold (version 2.4.11 or later)
- STREME (version 5.3.0 or later)
- Python 3.8
- scikit-learn 0.23.2
- scikit-optimize 0.8.1

**Important**: PRIESSTESS was tested with scikit-learn 0.23.2. Some users report needing version 0.22 for compatibility. See [Issue #2](/../../issues/2).

## Usage

### Train a PRIESSTESS model

`PRIESSTESS -fg foreground_file -bg background_file [OPTIONS]`

The foreground_file and background_file must contain 1 probe sequence per line containing only characters A, C, G, U and N. Files must be either uncompressed or gzipped. To convert a fasta to the correct format use:

`awk 'NR%2==0' fasta_file.fa > correct_format.txt`

#### OPTIONS

`-h, --help` Print help and exit

`-o` Path to existing output directory. A new directory called PRIESSTESS_output will be created in this directory to hold output. Default: current directory.

`-f5` 5' constant flanking sequence to be added to 5' end of all probes in fg and bg files OR if -flanksIn flag is used can also be a number. Ex: GGAUUGUAACCUAUCUGUA OR 19 Default: None

`-f3` 3' constant flanking sequence to be added to 3' end of all probes in fg and bg files OR if -flanksIn flag is used can also be a number. Ex: GGAUUGUAACCUAUCUGUA OR 19 Default: None

`-flanksIn` Indcates that 5' and 3' constant flanking sequences defined above are included in the probe sequences (-fg and -bg files). If the flag is not used, the flanks defined by -f5 and -f3 will be added by PRIESSTESS.

`-t` Folding temperature - passed to RNAfold. Default: 37

`-alph` Alphabet annotations to use in model. Default: 1,2,3,4,5,6,7 Ex. to use only the 1st & 4th alphabet type: 1,4

Alphabets annotations:

1: sequence (4-letter)

2: sequence-structure (8-letter) (4-letter sequence X 2-letter structure)

3: sequence-structure (16-letter) (4-letter sequence X 4-letter structure)

4: sequence-structure (28-letter) (4-letter sequence X 7-letter structure)

5: structure (2-letter)

6: structure (4-letter)

7: structure (7-letter)

`-N` The number of probes to use for PRIESSTESS from each of the forgeground and background files. This number will be aportioned between train and test sets. Default: The number of probes in the smaller two files.

`-stremeP` Percentage of probes to provide to STREME for enriched motif identification. Default: 50

`-logregP` Percentage of probes to use for training of the logistic regression model. Default: 25

`-testingP` Percentage of probes to hold out for testing. Default: 25

`-minw` Minimum motif width - passed to STREME. Width should be between 3 and 6. Default: 4

`-maxw` Maximum motif width - passed to STREME. Width should be between 6 and 9. Default: 6

`-maxAmotifs` Maximum number of motifs per alphabet to be used to train logistic regression models. Should be between 1 and 99. Default: 40

`-scoreN` Number of motif hits to sum when scoring sequences. A value of 1 is equivalent to the max. Default: 4

`-predLoss` Loss of predictive power during simplification of logistic regression model, as percentage: final_AUROC = (initial_AUROC - 0.5)\*predLoss + 0.5. Should be between 1 and 99. Default: 10

`-noCleanup` Do not remove intermediate files created by PRIESSTESS. If this flag is not used intermediate files will be removed after usage

### Scanning with a PRIESSTESS model

`PRIESSTESS_scan -fg foreground_file -bg background_file [OPTIONS]`

The foreground_file and background_file must contain 1 probe sequence per line containing only characters A, C, G, U and N. Files must be either uncompressed or gzipped. To convert a fasta to the correct format use:

`awk 'NR%2==0' fasta_file.fa > correct_format.txt`

#### OPTIONS

`-h, --help` Print help and exit

`-p` Path to PRIESSTESS_output directory containing the model to apply to the test data. Default: ./PRIESSTESS_output

`-testName` A name to use when creating directories and files with results. Ex. K562_RBFOX2_clip Default: test_data

`-f5` 5' constant flanking sequence to be added to 5' end of all probes in fg and bg files OR if -flanksIn flag is used can also be a number. Ex: GGAUUGUAACCUAUCUGUA OR 19 Default: None

`-f3` 3' constant flanking sequence to be added to 3' end of all probes in fg and bg files OR if -flanksIn flag is used can also be a number. Ex: GGAUUGUAACCUAUCUGUA OR 19 Default: None

`-flanksIn` Indcates that 5' and 3' constant flanking sequences defined above are included in the probe sequences (-fg and -bg files). If the flag is not used, the flanks defined by -f5 and -f3 will be added by PRIESSTESS.

`-t` Folding temperature - passed to RNAfold. Default: 37

`-noCleanup` Do not remove intermediate files created by PRIESSTESS. If this flag is not used intermediate files will be removed after usage

## Development

### Setting Up Development Environment

Install with development dependencies using the provided conda environment:

```bash
conda env create -f env.yaml
conda activate priesstess
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=bin --cov-report=html

# Run only fast unit tests (skip slow integration tests)
pytest -m "not slow"
```

Test reports will be generated in `htmlcov/index.html`.

### Code Quality

**Format code:**

```bash
black bin/
isort bin/
```

**Lint code:**

```bash
flake8 bin/
shellcheck PRIESSTESS PRIESSTESS_scan bin/*.sh
```

### Contributing

Before submitting pull requests:

1. Ensure all tests pass (`pytest`)
2. Format code with black/isort
3. Verify linting passes (flake8, shellcheck)
4. Update tests if adding new features

## Troubleshooting

### Scikit-learn Compatibility

If you encounter sklearn API errors:

```bash
conda install scikit-learn=0.22
```

See [Issue #2](/../../issues/2) for details.

### Tool Not Found Errors

Ensure external tools are in your PATH:

```bash
which RNAfold  # Should show path to RNAfold
which streme   # Should show path to STREME
```

If tools are missing, reinstall the conda environment or manually install:

- ViennaRNA package (provides RNAfold)
- MEME suite (provides STREME)

### Tests Failing

Make sure you're in the repository root and have activated the conda environment:

```bash
conda activate priesstess
pytest
```
