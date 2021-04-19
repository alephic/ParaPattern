
import sys
import os.path

if __name__ == "__main__":
    with open(sys.argv[1], encoding='utf8') as f:
        basepath = os.path.splitext(sys.argv[1])[0]
        with open(os.path.join(basepath+'_s2s', 'val.source'), mode='w', encoding='utf8') as sourcefile:
            with open(os.path.join(basepath+'_s2s', 'val.target'), mode='w', encoding='utf8') as targetfile:        
                for line in f:
                    s, t = line.rstrip().rsplit(' Therefore, ', maxsplit=1)
                    s = s.strip()
                    t = t.strip()
                    t = t[0].upper() + t[1:]
                    sourcefile.write(s+'\n')
                    targetfile.write(t+'\n')
                