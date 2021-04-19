import re
from typing import Callable, List, Tuple, Optional, TypeVar

T = TypeVar('T')

negate_pattern = re.compile(r'\s*!\s*')
name_pattern = re.compile(r'\s*([^\s$()[\]<>,]+)\s*')
label_pattern = re.compile(r'\s*([^\s$[\]:\'"<>]+)\s*:\s*')
cat_pattern = re.compile(r'\s*([^\s$[\]:\'"<>]+)\s*')
index_pattern = re.compile(r'\s*\$([0-9]+)\s*')
comma_sep_pattern = re.compile(r'\s*,\s*')
spaces_pattern = re.compile(r'\s*')
str_pattern = re.compile(r'\s*("([^\\"]|\\.)*"|\'([^\\\']|\\.)*\')\s*')
escape_pattern = re.compile(r'\\(.)')
arg_start_pattern = re.compile(r'\s*\(\s*')
arg_end_pattern = re.compile(r'\s*\)\s*')
mod_start_pattern = re.compile(r'\s*\[\s*')
mod_end_pattern = re.compile(r'\s*\]\s*')
ax_start_pattern = re.compile(r'\s*<\s*')
ax_end_pattern = re.compile(r'\s*>\s*')
#set_start_pattern = re.compile(r'\s*\{\s*')
#set_end_pattern = re.compile(r'\s*\}\s*')

def skip(text: str, pattern: re.Pattern, pos: int) -> int:
    m = pattern.match(text, pos=pos)
    return pos if m is None else m.end()

def parse_list(text: str, parse_el: Callable[[str, int], Tuple[Optional[T], int]], sep_pattern: re.Pattern, pos: int) -> Tuple[Optional[List[T]], int]:
    l = []
    while True:
        el, pos2 = parse_el(text, pos)
        if el is None:
            break
        else:
            pos = pos2
            l.append(el)
            smatch = sep_pattern.match(text, pos=pos)
            if smatch is None:
                break
            else:
                pos = smatch.end()
    return l, pos

class Head:
    def __init__(self, label: Optional[str] = None, category: Optional[str] = None, lemma: Optional[str] = None, index: Optional[int] = None, left_children: Optional[List['Head']] = None, right_children: Optional[List['Head']] = None, parent: Optional['Head'] = None, negate: bool = False, original = None):
        self.label = label
        self.category = category
        self.lemma = lemma
        self.index = index
        self.left_children = left_children
        self.right_children = right_children
        self.parent = parent
        self.negate = negate
        self.original = original

    @property
    def left_children(self):
        return self._left_children
    @left_children.setter
    def left_children(self, children):
        if children is not None:
            for child in children:
                child.parent = self
        self._left_children = children
    @left_children.deleter
    def left_children(self):
        del self._left_children
    
    @property
    def right_children(self):
        return self._right_children
    @right_children.setter
    def right_children(self, children):
        if children is not None:
            for child in children:
                child.parent = self
        self._right_children = children
    @right_children.deleter
    def right_children(self):
        del self._right_children

    @property
    def children(self):
        if self._left_children is not None:
            yield from iter(self._left_children)
        if self._right_children is not None:
            yield from iter(self._right_children)
    
    def add_left_child(self, child, pos=0):
        if self._left_children is None:
            self.left_children = [child]
        else:
            self._left_children.insert(pos, child)
            child.parent = self
    
    def add_right_child(self, child, pos=0):
        if self._right_children is None:
            self.right_children = [child]
        else:
            self._right_children.insert(pos, child)
            child.parent = self

    def copy_bare(self):
        return Head(label=self.label, category=self.category, lemma=self.lemma, index=self.index, negate=self.negate, original=self.original)
    def copy(self):
        copied = self.copy_bare()
        if self.left_children is not None:
            copied.left_children = [c.copy() for c in self.left_children]
        if self.right_children is not None:
            copied.right_children = [c.copy() for c in self.right_children]
        return copied

    @staticmethod
    def _parse_bare(text: str, pos: int=0) -> Tuple[Optional['Head'], int]:
        h = Head()
        if (m := negate_pattern.match(text, pos=pos)) is not None:
            h.negate = True
            pos = m.end()
        if (m := label_pattern.match(text, pos=pos)) is not None:
            h.label = m.group(1)
            pos = m.end()
        if (m := cat_pattern.match(text, pos=pos)) is not None:
            h.category = m.group(1)
            pos = m.end()
        if (m := str_pattern.match(text, pos=pos)) is not None:
            h.lemma = escape_pattern.sub('\\1', m.group(1)[1:-1])
            pos = m.end()
        if (m := index_pattern.match(text, pos=pos)) is not None:
            h.index = int(m.group(1))
            pos = m.end()
        if h.category is None and h.lemma is None and h.index is None:
            return None, pos
        return h, pos

    @staticmethod
    def parse(text: str, pos: int=0) -> Tuple[Optional['Head'], int]:
        # parse lefts
        left_children = None
        if (m := mod_start_pattern.match(text, pos=pos)) is not None:
            pos = m.end()
            left_children, pos = parse_list(text, Head.parse, spaces_pattern, pos)
            if left_children is None:
                return None, pos
            if (m := mod_end_pattern.match(text, pos=pos)) is None:
                return None, pos
            else:
                pos = m.end()
            if (m := ax_end_pattern.match(text, pos=pos)) is None:
                return None, pos
            else:
                pos = m.end()
        h, pos = Head._parse_bare(text, pos=pos)
        if h is None:
            return None, pos
        h.left_children = left_children
        while True:
            if (m := ax_end_pattern.match(text, pos=pos)) is None:
                break
            else:
                pos = m.end()
            h2, pos = Head._parse_bare(text, pos=pos)
            if h2 is None:
                return None, pos
            else:
                h2.left_children = [h]
                h = h2
        # parse rights
        hr = h
        while True:
            if (m := ax_start_pattern.match(text, pos=pos)) is None:
                break
            else:
                pos = m.end()
            if (m := mod_start_pattern.match(text, pos=pos)) is not None:
                pos = m.end()
                right_children, pos = parse_list(text, Head.parse, spaces_pattern, pos)
                if right_children is None:
                    return None, pos
                else:
                    hr.right_children = right_children
                if (m := mod_end_pattern.match(text, pos=pos)) is None:
                    return None, pos
                else:
                    pos = m.end()
                    break
            else:
                h2, pos = Head._parse_bare(text, pos=pos)
                if h2 is None:
                    return None, pos
                hr.right_children = [h2]
                hr = h2
        return h, pos
    
    @staticmethod
    def from_spacy(token):
        left_children = []
        right_children = []
        for c in token.children:
            h = Head.from_spacy(c)
            if c.i < token.i:
                left_children.append(h)
            else:
                right_children.append(h)
        left_children = None if len(left_children) == 0 else left_children
        right_children = None if len(right_children) == 0 else right_children
        return Head(label=token.dep_, category=token.tag_, lemma=token.lemma_, index=None, left_children=left_children, right_children=right_children, original=token)

    def __repr__(self):
        lcs = ''
        if self.left_children is not None:
            if len(self.left_children) == 1 and self.left_children[0].right_children is None:
                lcs = f'{repr(self.left_children[0])} > '
            else:
                lcs = f'[{" ".join(map(repr, self.left_children))}]> '
        rcs = ''
        if self.right_children is not None:
            if len(self.right_children) == 1 and self.right_children[0].left_children is None:
                rcs = f' < {repr(self.right_children[0])}'
            else:
                rcs = f' <[{" ".join(map(repr, self.right_children))}]'
        
        ns = '!' if self.negate else ''
        lbs = '' if self.label is None else f'{self.label}:'
        cs = self.category or ''
        ls = '' if self.lemma is None else repr(self.lemma)
        idxs = '' if self.index is None else f'${self.index}'
        return f'{lcs}{ns}{lbs}{cs}{ls}{idxs}{rcs}'
    
    def matches(self, other: 'Head') -> bool:
        if self.category is not None and self.category != other.category:
            return False
        if self.lemma is not None and self.lemma != other.lemma:
            return False
        if self.label is not None and self.label != other.label:
            return False
        return True

class Query:
    def __init__(self, head):
        self.head = head
        anchor_lemma = None
        anchor_label_tag = None
        fringe = [head]
        while len(fringe) > 0:
            curr = fringe.pop()
            if curr.negate:
                continue
            if curr.lemma is not None:
                anchor_lemma = curr
                break
            elif curr.label is not None and curr.category is not None:
                anchor_label_tag = curr
            fringe.extend(curr.children)
        self.anchor = anchor_lemma or anchor_label_tag

    def match(self, mt: Head):
        # back up to the head of the pattern
        curr_m = mt
        curr_q = self.anchor
        while curr_q.parent is not None:
            curr_q = curr_q.parent
            curr_m = curr_m.head
        curr_m = Head.from_spacy(curr_m)
        if not curr_q.matches(curr_m):
            return None
        fringe = [(curr_q, curr_m)]
        is_match = True
        var_matches = {}
        while len(fringe) > 0:
            curr_q, curr_m = fringe.pop()
            if curr_q.index is not None:
                var_matches[curr_q.index] = curr_m
            cs_q = curr_q.left_children or []
            cs_m = curr_m.left_children or []
            i = 0
            for c_q in cs_q:
                if c_q.negate:
                    if any(c_q.matches(c_m) for c_m in cs_m):
                        is_match = False
                        break
                else:
                    while i < len(cs_m) and not c_q.matches(cs_m[i]):
                        i += 1
                    if i == len(cs_m):
                        is_match = False
                        break
                    else:
                        fringe.append((c_q, cs_m[i]))
            cs_q = curr_q.right_children or []
            cs_m = curr_m.right_children or []
            i = 0
            for c_q in cs_q:
                if c_q.negate:
                    if any(c_q.matches(c_m) for c_m in cs_m):
                        is_match = False
                        break
                else:
                    while i < len(cs_m) and not c_q.matches(cs_m[i]):
                        i += 1
                    if i == len(cs_m):
                        is_match = False
                        break
                    else:
                        fringe.append((c_q, cs_m[i]))
            if not is_match:
                break
        if is_match:
            return var_matches
    
    def search(self, idx):
        if self.anchor.lemma is None:
            mts = idx.get_tokens_by_label_and_tag(self.anchor.label, self.anchor.category)
        else:
            mts = idx.get_tokens_by_lemma(self.anchor.lemma)
        for mt in mts:
            var_matches = self.match(mt)
            if var_matches is not None:
                yield mt, var_matches


def parse_query(s):
    return Query(Head.parse(s)[0])

