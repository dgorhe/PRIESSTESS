import math
import sys

if __name__ == "__main__":
    try:
        # takes a number in the format 1.6e-300 or 4e3 and takes log2
        # now also works if the number is not in scientific notation
        num = sys.argv[1]
        # For some users, numbers are in the format "1,6e-300" instead of "1.6e-300"
        if "," in num:
            num = num.replace(",", ".")
        if "e" in num:
            num_vec = num.split("e")
            mantissa = float(num_vec[0])
            exponent = float(num_vec[1])
            if mantissa <= 0:
                sys.stderr.write("Error: mantissa must be positive\n")
                sys.exit(1)
            print(math.log(mantissa, 2) + (exponent * math.log(10, 2)))
        else:
            result = float(num)
            if result <= 0:
                sys.stderr.write("Error: log2 requires a positive number\n")
                sys.exit(1)
            print(math.log(result, 2))
    except IndexError:
        sys.stderr.write("Error: Missing required argument\n")
        sys.stderr.write("Usage: log2_scinot.py <number>\n")
        sys.exit(1)
    except ValueError:
        sys.stderr.write("Error: Invalid number format\n")
        sys.exit(1)
