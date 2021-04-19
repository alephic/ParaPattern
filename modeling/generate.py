
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import transformers
import argparse
import sys
import modeling.tweaks as tweaks

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('model', type=str)
    p.add_argument('prompt', type=str)
    p.add_argument('--show_special_tokens', action='store_true')
    
    args = p.parse_args()

    m = transformers.AutoModelForSeq2SeqLM.from_pretrained(args.model)
    t = transformers.AutoTokenizer.from_pretrained(args.model, use_fast=False)
    tweaks.patch_bart_tokenizer(t)
    m.config.update({
        'early_stopping': True,
        'max_length': 128,
        'min_length': 8,
        'prefix': '',
        'decoder_start_token_id': t.bos_token_id
    })
    inputs = t([args.prompt], return_tensors='pt')
    m.eval()
    ids = m.generate(
        inputs['input_ids'], do_sample=True, top_p=0.9,
        decoder_start_token_id = t.bos_token_id
    )
    print([t.decode(g, skip_special_tokens=not args.show_special_tokens, clean_up_tokenization_spaces=False) for g in ids])