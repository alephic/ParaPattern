import sys
import os.path

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        lines = f.readlines()
        header = lines[0]
        lines = lines[1:]
        sorted_lines = sorted(lines, reverse=True, key=lambda line: float(line.split('\t')[-1]))
        with open(os.path.splitext(sys.argv[1])[0]+'_sorted.tsv', mode='w') as f_out:
            f_out.write(header)
            for line in sorted_lines:
                f_out.write(line)
        with open(os.path.splitext(sys.argv[1])[0]+'_scores.tsv', mode='w') as f_scores:
            f_scores.write('ID\tscore\n')
            for i, line in enumerate(sorted_lines):
                f_scores.write(str(i)+line[line.rfind('\t'):])