
import transformers
import argparse
import os.path
import torch
from tqdm import tqdm

def chunk(it, n):
    c = []
    for x in it:
        c.append(x)
        if len(c) == n:
            yield c
            c = []
    if len(c) > 0:
        yield c

def get_paraphrases(sents, model, tokenizer, device, gen_args):
    batch = tokenizer.prepare_seq2seq_batch(
        sents,
        truncation=True,
        padding=True,
        max_length=gen_args.max_length,
        return_tensors='pt'
    ).to(device)

    outputs = model.generate(
        **batch,
        top_p=gen_args.top_p,
        num_beams=gen_args.num_beams,
        do_sample=True,
        max_length=gen_args.max_length
    )

    return tokenizer.batch_decode(outputs, skip_special_tokens=True)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('data_path', type=str)
    p.add_argument('--ratio', type=int, default=2)
    p.add_argument('--model_name', type=str, default='tuner007/pegasus_paraphrase')
    p.add_argument('--batch_size', type=int, default=16)
    p.add_argument('--top_p', type=float, default=0.9)
    p.add_argument('--num_beams', type=int, default=1)
    p.add_argument('--max_length', type=int, default=60)
    p.add_argument('--device', type=str, default=None)
    args = p.parse_args()

    device = torch.device(args.device or ('cuda:0' if torch.cuda.is_available() else 'cpu'))

    model = transformers.AutoModelForSeq2SeqLM.from_pretrained(args.model_name)
    tokenizer = transformers.AutoTokenizer.from_pretrained(args.model_name)

    model.to(device)

    with open(args.data_path+'.source') as source_file:
        with open(args.data_path+'.target') as target_file:
            with open(args.data_path+'_para.source', mode='w') as para_source_file:
                with open(args.data_path+'_para.target', mode='w') as para_target_file:
                    in_sents = [
                        [(s + '.' if not s.endswith('.') else s) for s in l.rstrip().split('. ')] \
                            for l in source_file
                    ]
                    all_paras = [[] for _ in range(args.ratio)]
                    for c in tqdm(list(chunk((s for ex_in in in_sents for s in ex_in), args.batch_size)), desc='chunk'):
                        for paras in all_paras:
                            paras.extend(get_paraphrases(c, model, tokenizer, device, args))
                    i = 0
                    for ex_in, t in zip(in_sents, target_file):
                        for paras in all_paras:
                            para_source_file.write(' '.join(paras[i:i+len(ex_in)])+'\n')
                            para_target_file.write(t)
                        i += len(ex_in)
