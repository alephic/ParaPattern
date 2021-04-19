
import lemminflect
import dep_search.struct_query as sq

PUNCT = [c for c in '.?!:;,']
VOWELS = 'aeiouAEIOU'

QUAL_BLACKLIST = frozenset(['other', 'many', 'some', 'few', 'most', 'several', 'certain', 'particular', 'various', 'multiple', 'specific'])

class Token:
    def __init__(self, text, join_left=False, join_right=False):
        self.text = text
        self.join_left = join_left
        self.join_right = join_right

def remove_child(head: sq.Head, child: sq.Head):
    pruned = head.copy()
    if pruned.left_children is not None:
        for i, c in enumerate(head.left_children):
            if c is child:
                del pruned.left_children[i]
                if len(pruned.left_children) == 0:
                    pruned.left_children = None
                return pruned
    if pruned.right_children is not None:
        for i, c in enumerate(head.right_children):
            if c is child:
                del pruned.right_children[i]
                if len(pruned.right_children) == 0:
                    pruned.right_children = None
                return pruned
    return head

def filter_children(head: sq.Head, f):
    pruned = head.copy()
    if pruned.left_children is not None:
        pruned.left_children = [c for c in pruned.left_children if not f(c)]
        if len(pruned.left_children) == 0:
            pruned.left_children = None
    if pruned.right_children is not None:
        pruned.right_children = [c for c in pruned.right_children if not f(c)]
        if len(pruned.right_children) == 0:
            pruned.right_children = None
    return pruned

def swap_child(head: sq.Head, child: sq.Head, subst: sq.Head):
    if head.left_children is not None:
        for i, c in enumerate(head.left_children):
            if c is child:
                pruned = head.copy()
                pruned.left_children[i] = subst
                return pruned
    if head.right_children is not None:
        for i, c in enumerate(head.right_children):
            if c is child:
                pruned = head.copy()
                pruned.right_children[i] = subst
                return pruned
    return head

def get_left_child_by_label(head: sq.Head, label: str):
    if head.left_children is not None:
        for c in head.left_children:
            if c.label == label:
                return c
    return None

def get_right_child_by_label(head: sq.Head, label: str):
    if head.right_children is not None:
        for c in head.right_children:
            if c.label == label:
                return c
    return None

def linearize(head: sq.Head):
    t = Token(head.lemma)
    if head.original is None or head.category != head.original.tag_:
        if head.category == 'DT':
            if head.lemma == 'a':
                after = False
                for c in (*(head.parent.left_children or []), head.parent):
                    if c is head:
                        after = True
                    elif after:
                        if c is not head.parent:
                            while c.left_children is not None:
                                c = c.left_children[0]
                        if c.lemma[0] in VOWELS:
                            t.text = 'an'
                        break
        elif head.category in PUNCT:
            t.join_left = True
        else:
            inflections = lemminflect.getInflection(head.lemma, head.category)
            if len(inflections) > 1 and head.lemma == 'be' and head.category == 'VBP':
                t.text = 'are'
            elif len(inflections) > 0:
                t.text = inflections[0]
    else:
        t.text = head.original.text
        t.join_left = head.original.i > 0 and head.original.doc[head.original.i-1].whitespace_ == '' and not t.text.isalnum()
        t.join_right = head.original.whitespace_ == '' and not t.text.isalnum()
    if head.lemma.islower() or (head.lemma == '-PRON-' and t.text != 'I'):
        t.text = t.text.lower()

    if head.left_children is not None:
        for child in head.left_children:
            yield from linearize(child)
    yield t
    if head.right_children is not None:
        for child in head.right_children:
            yield from linearize(child)

def join_tokens(tokens):
    chunks = []
    last_join = True
    for t in tokens:
        chunks.append(' '+t.text if not (t.join_left or last_join) else t.text)
        last_join = t.join_right
    return ''.join(chunks)

def flatten(head):
    return join_tokens(linearize(head))
def capitalize(s):
    return s[0].upper() + s[1:]

class Pattern:
    def __init__(self, query):
        self.query = query
    
    def rewrite(self, match_vars):
        raise NotImplementedError()

    def scrape(self, idx):
        for _, m_vars in self.query.search(idx):
            output = self.rewrite(m_vars)
            if output is not None:
                yield output

class SimpleSubjFilterPattern(Pattern):
    def rewrite(self, match_vars):
        pred = match_vars[2]
        subj = match_vars[0]
        restr = match_vars[1]
        if (subj.lemma.lower() in QUAL_BLACKLIST) or any(c.lemma.lower() in QUAL_BLACKLIST for c in subj.children):
            return None
        return (str(pred.original.sent),)