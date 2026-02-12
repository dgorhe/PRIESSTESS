import os
import sys

####
# This python script requires:

# 1. A tab-delimited file in the format
# RNA sequence    dot-bracket structure    7-letter structure annotation
# Ex.
# GACUACGAUAGUU\t.(((.....))).\tELLLHHHHHRRRE
# GCCCCUAACACGU\t.............\tEEEEEEEEEEEEE

# 2. A prefix for the output file

# The script returns:

# A tab-delimited file called "prefix_alphabet_annotations.tab"
# Which contains a probe ID and each of the 7 alphabet annotations in the order
# probe_ID  seq-4  seq-struct-8  seq-struct-16  seq-struct-28  struct-2
# struct-4  struct-7
####

# Define conversion from sequence (4-letter) alphabet and 7-letter structure
# alphabet to 28-letter alphabet
letters_28 = list("ABCDEFGHIJKLMNOPQRSTUVWXYZab")

seq_struct_28_combos = [
    c1 + c2 for c1 in ["A", "C", "G", "U"] for c2 in ["B", "E", "H", "L", "M", "R", "T"]
]
combo2letter_seq_struct_28 = dict()
for i in range(len(seq_struct_28_combos)):
    combo2letter_seq_struct_28[seq_struct_28_combos[i]] = letters_28[i]

# Convert 28 letter seq-struct to 16 letter seq-struct
# The 16-letter alphabet contains the letters A-P
# The following list contains the 16 letters as they match the 28 letter alphabet
letters_16 = list("DCBADADHGFEHEHLKJILILPONMPMP")
seq_struct_28_convert_16 = dict()
for i in range(len(letters_28)):
    seq_struct_28_convert_16[letters_28[i]] = letters_16[i]

# Convert 28 letter seq-struct to 8 letter seq-struct
# The 8-letter alphabet contains the letters A-H
# The following list contains the 8 letters as they match the 28 letter alphabet
letters_8 = list("AAABABACCCDCDCEEEFEFEGGGHGHG")
seq_struct_28_convert_8 = dict()
for i in range(len(letters_28)):
    seq_struct_28_convert_8[letters_28[i]] = letters_8[i]

# Converting 7-letter struct alphabet to 4-letter struct alphabet
struct_7_convert_4 = {"B": "M", "E": "U", "H": "L", "L": "P", "M": "M", "R": "P", "T": "M"}

# Converting 4-letter struct alphabet to 2-letter struct alphabet
struct_4_convert_2 = {"P": "P", "L": "U", "U": "U", "M": "U"}

if __name__ == "__main__":
    # Read in filename and prefix
    try:
        filename = sys.argv[1]
        prefix = sys.argv[2]
    except IndexError:
        sys.stderr.write("Error: Missing required arguments\n")
        sys.stderr.write("Usage: annotate_alphabets.py <filename> <prefix>\n")
        sys.exit(1)

    if not os.path.exists(filename):
        sys.stderr.write(f"Error: Input file '{filename}' not found\n")
        sys.exit(1)

    # Read all lines in file
    try:
        filein = open(filename, "r")
        lines = filein.readlines()
        filein.close()
    except IOError as e:
        sys.stderr.write(f"Error reading input file: {e}\n")
        sys.exit(1)

    if not lines:
        sys.stderr.write("Error: Input file is empty\n")
        sys.exit(1)

    # Open output file
    try:
        fileout = open(prefix + "_alphabet_annotations.tab", "w")
    except IOError as e:
        sys.stderr.write(f"Error creating output file: {e}\n")
        sys.exit(1)

    try:
        # For each line use the sequence and 7-letter alphabet
        # To convert to all other alphabets
        for i in range(len(lines)):
            line_data = lines[i]
            parts = line_data.strip().split("\t")
            if len(parts) < 3:
                sys.stderr.write(f"Error: Line {i + 1} has fewer than 3 fields\n")
                sys.exit(1)

            seq_4 = parts[0]
            struct_7 = parts[2]

            if len(seq_4) != len(struct_7):
                sys.stderr.write(
                    f"Error: Line {i + 1}: "
                    f"sequence length ({len(seq_4)}) != structure length ({len(struct_7)})\n"
                )
                sys.exit(1)

            N = range(len(struct_7))

            seq_struct_28 = "".join([combo2letter_seq_struct_28[seq_4[i] + struct_7[i]] for i in N])
            seq_struct_16 = "".join([seq_struct_28_convert_16[seq_struct_28[i]] for i in N])
            seq_struct_8 = "".join([seq_struct_28_convert_8[seq_struct_28[i]] for i in N])
            struct_4 = "".join([struct_7_convert_4[struct_7[i]] for i in N])
            struct_2 = "".join([struct_4_convert_2[struct_4[i]] for i in N])

            # Write all annotations to file + ID based on line number
            fileout.write(
                prefix
                + "_"
                + str(i + 1)
                + "\t"
                + "\t".join(
                    [
                        seq_4,
                        seq_struct_8,
                        seq_struct_16,
                        seq_struct_28,
                        struct_2,
                        struct_4,
                        struct_7,
                    ]
                )
                + "\n"
            )

    except KeyError as e:
        sys.stderr.write(f"Error: Invalid character in sequence or structure: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error processing data: {e}\n")
        sys.exit(1)
    finally:
        # Close output file
        fileout.close()
