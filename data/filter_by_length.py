
import sys

if __name__ == "__main__":
    cutoff_len = int(sys.argv[2])
    with open(sys.argv[1]) as f:
        for line in f:
            if len(line.split(' ')) <= cutoff_len:
                print(line, end='')
