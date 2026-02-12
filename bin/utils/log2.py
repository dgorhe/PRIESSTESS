import math
import sys

if __name__ == "__main__":
    try:
        # takes a float or an integer
        num = sys.argv[1]
        result = float(num)
        if result <= 0:
            sys.stderr.write("Error: log2 requires a positive number\n")
            sys.exit(1)
        print(math.log(result, 2))
    except IndexError:
        sys.stderr.write("Error: Missing required argument\n")
        sys.stderr.write("Usage: log2.py <number>\n")
        sys.exit(1)
    except ValueError:
        sys.stderr.write(f"Error: '{num}' is not a valid number\n")
        sys.exit(1)
