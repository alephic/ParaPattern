import json
import sys
import os.path

def capitalize(s):
    return s[0].upper() + s[1:]

if __name__ == "__main__":
    with open(sys.argv[1], encoding='utf8') as f:
        basepath = os.path.splitext(sys.argv[1])[0]
        with open(basepath+'.source', mode='w', encoding='utf8') as sourcefile:
            with open(basepath+'.target', mode='w', encoding='utf8') as targetfile:        
                for line in f:
                    l = list(map(capitalize, json.loads(line)))
                    sourcefile.write(' '.join(l[:-1])+'\n')
                    targetfile.write(l[-1]+'\n')