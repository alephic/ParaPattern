
import dep_search.struct_query as sq
from dep_search.templates.common import *

class HearstPattern(Pattern):
    def rewrite(self, match_vars):
        tgt_gen = match_vars[0]
        tgt_sp = match_vars[1]
        pred = match_vars[2]
        if (tgt_gen.lemma.lower() in QUAL_BLACKLIST) or any(c.lemma.lower() in QUAL_BLACKLIST for c in tgt_gen.children):
            return None
        conj_filter = lambda c: c.category in [',', ':', '-LRB-', '-RRB-'] or c.label in ['conj', 'cc']
        tgt_clean = filter_children(remove_child(tgt_gen, tgt_sp.parent), conj_filter)
        tgt_sp = filter_children(tgt_sp, conj_filter)
        tgt_sp.label = tgt_gen.label
        verb_form_sp = 'VBP' if tgt_sp.category == 'NNS' else 'VBZ'
        gen_stmt = swap_child(pred, tgt_gen, tgt_clean)
        dobj_inst = filter_children(tgt_clean, lambda c: c.label == 'det')
        dobj_inst.category = 'NN'
        dobj_inst.add_left_child(sq.Head(category='DT', lemma='a', label='det'))
        period = sq.Head(category='.', lemma='.', label='punct')
        inst_stmt = sq.Head(category=verb_form_sp, lemma='be', label='ROOT', left_children=[tgt_sp], right_children=[dobj_inst, period])
        out_stmt = swap_child(pred, tgt_gen, tgt_sp)
        out_stmt.category = verb_form_sp if tgt_gen.label == 'nsubj' else pred.category
        for c in out_stmt.children:
            if c.label == 'conj' and c.category == pred.category and not any(c2.label == 'nsubj' for c2 in c.children):
                c.category = verb_form_sp
        if pred.lemma == 'be':
            for c in out_stmt.right_children or []:
                if c.label == 'attr' and c.category == 'NNS':
                    c.category = 'NN'
                    c.add_left_child(sq.Head(category='DT', lemma='a', label='det'))
        return (flatten(inst_stmt), flatten(gen_stmt), flatten(out_stmt))

def scrape_hearst_instances(idx):
    qs = (
        sq.parse_query("[nsubj:NNS$0 <[amod:'such' > prep:IN'as' < pobj:$1]]> ROOT:VBP$2"),
        sq.parse_query("[nsubj:NNS$0 < prep:IN'like' < pobj:$1]> ROOT:VBP$2"),
        sq.parse_query("[nsubj:NNS$0 < prep:VBG'include' < pobj:$1]> ROOT:VBP$2"),
        sq.parse_query("ROOT:VBP$2 <[dobj:NNS$0 <[amod:'such' > prep:IN'as' < pobj:$1]]"),
        sq.parse_query("ROOT:VBP$2 <[dobj:NNS$0 < prep:IN'like' < pobj:$1]"),
        sq.parse_query("ROOT:VBP$2 <[dobj:NNS$0 < prep:VBG'include' < pobj:$1]")
    )
    for pat in map(HearstPattern, qs):
        yield from pat.scrape(idx)