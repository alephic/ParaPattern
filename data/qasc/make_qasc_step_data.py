
import json
import re

dup_pattern = re.compile(r'[A-Za-z ]+ [A-Z][a-z]+ [A-Za-z,\- ]+\.')

def clean(text, capitalize=True):
    text = text.strip(' .') + '.'
    text = (text[0].upper() if capitalize else text[0].lower()) + text[1:]
    if dup_pattern.match(text):
        num_leading_capitals = 0
        words = text.split()
        cut = 0
        for n in range(1, len(words)):
            dup_count = 1
            while dup_count*n < len(words):
                if words[n*dup_count:n*(dup_count+1)] == words[:n]:
                    dup_count += 1
                    cut = n*(dup_count - 1)
                else:
                    break
        words = words[cut:]
        for i in range(len(words)):
            if not words[i][0].isupper():
                words = words[i-1:]
                break
        text = ' '.join(words)
    return text

if __name__ == "__main__":
    a = []
    with open('data/full/QASC_Dataset/dev.jsonl') as f:
        for line in f:
            j = json.loads(line)
            prompt = f"{clean(j['fact1'])} {clean(j['fact2'])} Therefore,"
            answer = clean(j['combinedfact'], capitalize=False)
            a.append({'prompt': prompt, 'answer': answer})
    with open('data/step/qasc/qasc_dev_dedup.json', mode='w') as f2:
        json.dump(a, f2, indent=4)