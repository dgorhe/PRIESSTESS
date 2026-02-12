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

.PHONY: all clean parse_secondary_structure

all: parse_secondary_structure

parse_secondary_structure: $(BIN)

$(BIN): $(SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<
	@echo "Built $@ for $(UNAME_S) ($(shell uname -m))"

clean:
	rm -f $(BIN)
