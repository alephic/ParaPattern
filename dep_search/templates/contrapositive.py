
from dep_search.templates.common import *
import dep_search.struct_query as sq

class ContrapositiveTemplate(Pattern):
    def rewrite(self, match_vars):
        subj = match_vars[0]
        restr = match_vars[1]
        pred = match_vars[2]
        #original : X that Y is Z
        # check for list of nps in predicate arg
        if pred.lemma in {'include'}:
            return None
        if pred.right_children is not None:
            for c in pred.right_children:
                if c.right_children is not None:
                    for cc in c.right_children:
                        if c.label == 'conj':
                            return None

        out_restr = swap_child(pred, subj,
            sq.Head(label='nsubj', category='WDT', lemma='that')
        )
        
        out_restr = filter_children(out_restr, lambda c: c.lemma == '.')

        left_adjuncts = []
        if out_restr.left_children is not None:
            for i, l_c in enumerate(out_restr.left_children):
                if l_c.label == 'nsubj':
                    break
                if l_c.lemma == ',':
                    left_adjuncts = out_restr.left_children[:i+1]
            out_restr.left_children = out_restr.left_children[len(left_adjuncts):]

        if out_restr.lemma == 'be':
            is_neg = False
            if out_restr.right_children is not None:
                for c in out_restr.right_children:
                    if c.lemma == 'not':
                        is_neg = True
                        break
            if is_neg:
                out_restr = filter_children(out_restr, lambda c: c.lemma == 'not')
            else:
                out_restr.right_children = [
                    sq.Head(label='neg', category='RB', lemma='not')
                ] + (out_restr.right_children or [])
        else:
            is_neg = False
            if out_restr.left_children is not None:
                for c in out_restr.left_children:
                    if c.lemma == 'not':
                        is_neg = True
                        break
            if is_neg:
                out_restr = filter_children(out_restr, lambda c: c.lemma == 'not' or c.label == 'aux')
            else:
                out_restr.left_children = out_restr.left_children + [
                    sq.Head(label='aux', category='VBP', lemma='do'),
                    sq.Head(label='neg', category='RB', lemma='not')
                ]
        
        if restr.parent.category == 'IN':
            # "with" case
            out_subj = swap_child(subj, restr.parent, out_restr)
            out_pred = sq.Head(
                label='ROOT', category='VB', lemma='have',
                left_children=[
                    out_subj,
                    sq.Head(label='aux', category='VBP', lemma='do'),
                    sq.Head(label='neg', category='RB', lemma='not')
                ],
                right_children=[restr]
            )
        else:
            out_subj = swap_child(subj, restr, out_restr)
            if restr.lemma == 'be':
                is_neg = False
                if restr.right_children is not None:
                    for c in restr.right_children:
                        if c.lemma == 'not':
                            is_neg = True
                            break
                out_pred = sq.Head(
                    label='ROOT', category='VBP', lemma=restr.lemma,
                    left_children=[out_subj],
                    right_children=[r_c for r_c in restr.right_children if r_c.lemma != 'not'] if is_neg else
                        [sq.Head(label='neg', category='RB', lemma='not')]+(restr.right_children or [])
                )
            else:
                is_neg = False
                if restr.left_children is not None:
                    for c in restr.left_children:
                        if c.lemma == 'not':
                            is_neg = True
                            break
                out_pred = sq.Head(
                    label='ROOT', category='VB', lemma=restr.lemma,
                    left_children=[l_c for l_c in restr.left_children if l_c.lemma != 'not' and l_c.label != 'aux'] if is_neg else
                        [
                            out_subj,
                            sq.Head(label='aux', category='VBP', lemma='do'),
                            sq.Head(label='neg', category='RB', lemma='not')
                        ],
                    right_children=restr.right_children
                )
            out_pred.left_children = left_adjuncts + (out_pred.left_children or [])
        return (flatten(pred), flatten(out_pred)+'.')

def scrape_contrapositive_instances(idx):
    qs = (
        sq.parse_query("[nsubj:NNS$0 <[nsubj:WDT'that' > relcl:VBP$1]] > ROOT:VBP$2"),
        sq.parse_query("[nsubj:NNS$0 <[prep:IN'with' < pobj:$1]] > ROOT:VBP$2")
    )
    for pat in map(ContrapositiveTemplate, qs):
        yield from pat.scrape(idx)