import json
import sys

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        with open(sys.argv[2]+'.source', mode='w') as source_file:
            with open(sys.argv[2]+'.target', mode='w') as target_file:
                for line in f:
                    obj = json.loads(line)
                    if obj['genre'] == "telephone":
                        continue
                    if obj['gold_label'] == "entailment":
                        source_file.write(obj['sentence1']+'\n')
                        target_file.write(obj['sentence2']+'\n')
