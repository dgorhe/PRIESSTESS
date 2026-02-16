# Makefile for PRIESSTESS
# Compiles parse_secondary_structure_v2 for the current platform (avoids exec errors
# from binaries compiled for a different OS/architecture, e.g. Linux x86 on macOS)

UNAME_S := $(shell uname -s)

# Use g++ for C++; on macOS, g++ may be aliased to clang++ if GNU toolchain not installed.
# Override with: make CXX=/path/to/g++
CXX ?= g++
CXXFLAGS := -Wall -O2 -std=c++98

SRC := bin/utils/parse_secondary_structure_v2.cpp
BIN := bin/utils/parse_secondary_structure_v2

# Python: black + isort (pyproject.toml), flake8 (.flake8)
PYTHON_DIRS := bin tests

# Shell scripts for shellcheck + shfmt
SHELL_SCRIPTS := run_priesstess.sh run_priesstess_parallel.sh \
	bin/fold_and_annotate.sh bin/PRIESSTESS_scanning.sh \
	bin/utils/extract_lines_from_file.sh bin/utils/transpose_file.sh

.PHONY: all clean parse_secondary_structure lint format lint-python format-python lint-shell format-shell

all: parse_secondary_structure

parse_secondary_structure: $(BIN)

$(BIN): $(SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<
	@echo "Built $@ for $(UNAME_S) ($(shell uname -m))"

clean:
	rm -f $(BIN)

# --- Linting ---
lint: lint-python lint-shell

lint-python:
	flake8 $(PYTHON_DIRS)

lint-shell:
	shellcheck $(SHELL_SCRIPTS)

# --- Formatting ---
format: format-python format-shell

format-python:
	black --line-length 120 $(PYTHON_DIRS)
	isort --line-length 120 $(PYTHON_DIRS)

format-shell:
	shfmt -w $(SHELL_SCRIPTS)
