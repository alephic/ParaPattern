from types import MethodType
from typing import Optional, List
from contextlib import contextmanager

def add_diversion(method, aux_fn):
    def f(self, *args, **kwargs):
        aux_fn(*args, **kwargs)
        return method(*args, **kwargs)
    setattr(method.__self__.__class__, method.__name__, f)
    setattr(method.__self__, method.__name__, MethodType(f, method.__self__))

def build_inputs_with_special_tokens_patched(
        self, token_ids_0: List[int], token_ids_1: Optional[List[int]] = None
    ) -> List[int]:
        """
        Build model inputs from a sequence or a pair of sequence for sequence classification tasks by concatenating and
        adding special tokens. A RoBERTa sequence has the following format:
        - single sequence: ``<s> X </s>``
        - pair of sequences: ``<s> A </s></s> B </s>``
        Args:
            token_ids_0 (:obj:`List[int]`):
                List of IDs to which the special tokens will be added.
            token_ids_1 (:obj:`List[int]`, `optional`):
                Optional second list of IDs for sequence pairs.
        Returns:
            :obj:`List[int]`: List of `input IDs <../glossary.html#input-ids>`__ with the appropriate special tokens.
        """
        if token_ids_1 is None:
            if self.in_target_mode:
                return token_ids_0 + [self.sep_token_id]
            else:
                return [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        cls = [self.cls_token_id]
        sep = [self.sep_token_id]
        return cls + token_ids_0 + sep + sep + token_ids_1 + sep

@contextmanager
def as_target_tokenizer_patched(self):
    self.in_target_mode = True
    yield
    self.in_target_mode = False

def patch_bart_tokenizer(tokenizer):
    tokenizer.add_prefix_space = True
    tokenizer.in_target_mode = False
    tokenizer.as_target_tokenizer = MethodType(as_target_tokenizer_patched, tokenizer)
    tokenizer.build_inputs_with_special_tokens = MethodType(build_inputs_with_special_tokens_patched, tokenizer)