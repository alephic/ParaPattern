
import json
import sys
from os.path import splitext

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        with open(splitext(sys.argv[1])[0]+'.json', mode='w') as f_out:
            exs = []
            for line in f:
                p, a = line.strip().split('Therefore, ')
                p += "Therefore,"
                exs.append({'prompt':p, 'answer':a})
            json.dump(exs, f_out)
