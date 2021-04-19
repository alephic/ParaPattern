
from collections import defaultdict
from tqdm import tqdm
import spacy
import gzip
import pickle

def get_doc_texts(path):
    with open(path) as f:
        doclines = []
        for line in f:
            line = line.rstrip()
            if line.endswith('.'):
                doclines.append(line)
            elif len(doclines) > 0:
                doctext = ' '.join(doclines)
                doclines.clear()
                yield doctext
        if len(doclines) > 0:
            doctext = ' '.join(doclines)
            doclines.clear()
            yield doctext

def get_sentences(paths, nlp=None, limit=160000):
    if nlp is None:
        nlp = spacy.load('en_core_web_sm')
    chunk = []
    for path in paths:
        for doc_text in get_doc_texts(path):
            chunk.extend(nlp(doc_text).sents)
            while len(chunk) >= limit:
                next_chunk = chunk[limit:]
                chunk = chunk[:limit]
                yield chunk
                chunk = next_chunk
    if len(chunk) > 0:
        yield chunk

def get_cached_sentences(paths, limit=8000):
    chunk = []
    for path in paths:
        with gzip.open(path, mode='rb') as f:
            docs_bytes = pickle.load(f)
            for i in range(len(docs_bytes)):
                voc_bytes, doc_bytes = docs_bytes[i]
                voc = pickle.loads(voc_bytes)
                doc = spacy.tokens.Doc(voc)
                doc = doc.from_bytes(doc_bytes, exclude=['sentiment', 'tensor', 'vocab'])
                chunk.extend(doc.sents)
                docs_bytes[i] = None
                del doc
                del voc
                while len(chunk) >= limit:
                    next_chunk = chunk[limit:]
                    chunk = chunk[:limit]
                    yield chunk
                    chunk = next_chunk
            del docs_bytes
        del f
    if len(chunk) > 0:
        yield chunk
    
class Index:
    def __init__(self, sentences):
        self.d_lemma = defaultdict(list)
        self.d_label_tag = defaultdict(list)
        self.string_store = None
        for s in sentences:
            self.add_sent(s)
    def add_sent(self, sent):
        if self.string_store is None:
            self.string_store = sent.doc.vocab.strings
        for tok in sent:
            self.d_lemma[tok.lemma].append(tok)
            self.d_label_tag[(tok.dep, tok.tag)].append(tok)
    def get_tokens_by_lemma(self, lemma):
        return self.d_lemma[self.string_store[lemma]]
    def get_tokens_by_label_and_tag(self, label, tag):
        return self.d_label_tag[(self.string_store[label], self.string_store[tag])]
