
from dep_search.index import *
import dep_search.struct_query as sq
from typing import List
import spacy
import sys
import random
import argparse
import glob
import json
import os.path
from dep_search.templates.hearst import scrape_hearst_instances
from dep_search.templates.contrapositive import scrape_contrapositive_instances

def scrape_all(idx):
    yield from scrape_hearst_instances(idx)

def scrape_restr_rel_sentences(idx):
    qs = (
        sq.parse_query("[nsubj:NNS$0 <[nsubj:WDT'that' > relcl:VBP$1]] > ROOT:VBP$2"),
        sq.parse_query("[nsubj:NNS$0 <[prep:IN'with' < pobj:$1]] > ROOT:VBP$2")
    )
    for pat in map(SimpleSubjFilterPattern, qs):
        yield from pat.scrape(idx)

def create_jsonl_line(ss):
    return json.dumps([*ss])+'\n'

def create_txt_line(ss):
    inputs = ' '.join(map(capitalize, ss[:-1]))

    return f'{inputs} Therefore, {ss[-1]}\n'

if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument('input_path', type=str)
    argp.add_argument('output_path', type=str)
    argp.add_argument('--pattern', type=str, default='all')
    argp.add_argument('--output_format', type=str, default=None)
    argp.add_argument('--shuffle_inputs', action='store_true')
    args = argp.parse_args()
    last = None
    scrape_fn = {
        'all': scrape_all,
        'hearst': scrape_hearst_instances,
        'restr': scrape_restr_rel_sentences,
        'contra': scrape_contrapositive_instances
    }[args.pattern]
    out_fmt = args.output_format or os.path.splitext(args.output_path)[1][1:]
    fmt_fn = {'jsonl':create_jsonl_line, 'txt': create_txt_line}[out_fmt]
    if args.input_path.endswith('.jsonl'):
        nlp = spacy.load('en_core_web_sm')
        sents = []
        with open(args.input_path) as f:
            for line in f:
                line_sents = json.loads(line)
                for sent in line_sents:
                    sents.append(next(nlp(sent).sents))
        chunk_iter = [sents]
    else:
        chunk_iter = get_sentences(tqdm(glob.glob(os.path.join(args.input_path, '*.txt')), desc='File', position=1))
    with open(args.output_path, mode='w') as f_out:
        for chunk in tqdm(chunk_iter, desc='Chunk', position=0):
            idx = Index(chunk)
            for ss in scrape_fn(idx):
                if args.shuffle_inputs:
                    inputs = list(ss[:-1])
                    random.shuffle(inputs)
                    ss = (*inputs, ss[-1])
                line = fmt_fn(ss)
                if line != last:
                    f_out.write(line)
                last = line
            del idx
            del chunk
