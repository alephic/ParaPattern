
import spacy
import json
import re

var_name_pattern = re.compile(r':([a-zA-Z0-9]+)')


def anon_var_name_gen():
    i = 0
    while True:
        yield f'${i}'
        i += 1

class QueryTokenProperties:
    def __init__(self):
        self.var_name = None
        self.match_lemma = True

class SentenceQuery:
    def __init__(self, nlp, ex_text_marked):
        ex_text_clean = ''
        var_bounds = []
        anon_gen = anon_var_name_gen()
        in_var = False
        var_start = 0
        marks = {}
        i = 0
        while i < len(ex_text_marked):
            char = ex_text_marked[i]
            if char == '_':
                marks[len(ex_text_clean)] = '_'
            elif char == '[':
                in_var = True
                var_start = len(ex_text_clean)
            elif in_var and char == ']':
                if m := var_name_pattern.match(ex_text_marked, pos=i+1):
                    var_name = m.group(1)
                    i = m.end()
                else:
                    var_name = next(anon_gen)
                    i += 1
                var_bounds.append((var_name, var_start, len(ex_text_clean)))
                continue
            else:
                ex_text_clean += char
            i += 1
        
        ex_parsed = nlp(ex_text_clean)
        self.ex = next(ex_parsed.sents)
        self.token_properties = [QueryTokenProperties() for _ in self.ex]
        i = 0
        for (var_name, var_start, var_end) in var_bounds:
            while self.ex[i].idx < var_start:
                i += 1
                if i >= len(self.ex):
                    raise RuntimeError('Malformed query')
            while self.ex[i].idx < var_end:
                self.token_properties[i].var_name = var_name
                i += 1
                if i >= len(self.ex):
                    raise RuntimeError('Malformed query')
        
        for t in self.ex:
            if marks.get(t.idx) == '_':
                self.token_properties[t.i].match_lemma = False

        max_anchor_depth = -1
        self.anchor = None
        for t in self.ex:
            if (self.token_properties[t.i].var_name is not None) and self.token_properties[t.head.i].var_name is None:
                anchor_depth = len(list(t.head.ancestors))
                if anchor_depth > max_anchor_depth:
                    if all(self.token_properties[ancestor.i].var_name is None for ancestor in t.ancestors):
                        max_anchor_depth = anchor_depth
                        self.anchor = t.head
        if self.anchor is None: # no variables
            for t in self.ex:
                anchor_depth = len(list(t.ancestors))
                if anchor_depth > max_anchor_depth:
                    max_anchor_depth = anchor_depth
                    self.anchor = t

    def search(self, idx):
        for match_tok in idx.get_tokens_by_lemma(self.anchor.lemma_):
            match_root = match_tok.sent.root
            var_matches = {}
            is_match = True
            fringe = [(self.ex.root, match_root)]
            while len(fringe) > 0 and is_match:
                qt, mt = fringe.pop()
                qt_props = self.token_properties[qt.i]
                if qt_props.var_name is not None:
                    if qt_props.var_name not in var_matches:
                        var_matches[qt_props.var_name] = mt
                elif qt_props.match_lemma and qt.lemma_ != mt.lemma_:
                    is_match = False
                    break
                mc_by_dep = {mc.dep_: mc for mc in mt.children}
                for qc in qt.children:
                    if ((qc_var := self.token_properties[qc.i].var_name) is not None) and qc_var == qt_props.var_name:
                        continue
                    if (mc := mc_by_dep.get(qc.dep_)) is not None:
                        fringe.append((qc, mc))
                    else:
                        is_match = False
                        break
            if is_match:
                yield (match_root, var_matches)
    @staticmethod
    def extend_match(m):
        match_root, var_matches = m
        vars_by_lemma = {var_match.lemma_: var_name for var_name, var_match in var_matches.items() if var_match.lemma_ != '-PRON-'}
        for sent in match_root.doc.sents:
            if sent.root != match_root:
                for tok in sent:
                    if (var_name := vars_by_lemma.get(tok.lemma_)) is not None:
                        yield (var_name, tok)

def process_sentence_queries(query_exs_marked, txt_paths, out_path):
    nlp = spacy.load('en_core_web_sm')
    qs = [Query(nlp, query_text) for query_text in query_exs_marked]
    for idx in map(Index, get_sentences(nlp, txt_paths)):
        with open(out_path, mode='w') as f:
            for q in qs:
                for m in q.match(idx):
                    m_obj = {'match': repr(m[0].sent)}
                    extended = []
                    m_obj['extensions'] = extended
                    for m2 in SentenceQuery.extend_match(m):
                        extended.append(repr(m2[1].sent))
                    if len(extended) > 0:
                        f.write(json.dumps(m_obj))
                        f.write('\n')
        
            