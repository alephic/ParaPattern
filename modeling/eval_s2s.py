
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys
import transformers
import torch
import argparse
import os.path
from modeling.utils import Seq2SeqDataset, Seq2SeqDataCollator, chunks
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
import math
import modeling.tweaks as tweaks
from pathlib import Path
import json
from bleurt import score
import numpy as np

def strip_dataset_type(path):
    if path.endswith('_s2s'):
        return path[:-4]
    return path

class ArgWrapper:
    def __init__(self, d):
        self.d = d
    def __getattr__(self, attr):
        return self.d.get(attr)

def run_eval(model, tokenizer, dataset, device, gen_args):
    data_loader = DataLoader(
        dataset, gen_args.batch_size,
        collate_fn=Seq2SeqDataCollator(
            tokenizer,
            ArgWrapper({
                'max_source_length': gen_args.max_input_length,
                'max_target_length': gen_args.max_output_length
            })
        )
    )
    total_loss = 0
    total_loss_repeat = 0
    batch_count = 0
    loss_fn = torch.nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)
    outputs = []
    metrics = {}
    for batch in tqdm(data_loader):
        batch = {k: (v.to(device) if isinstance(v, torch.Tensor) else v) for k, v in batch.items()}
        batch_repeat = dict(batch)
        batch_repeat['labels'] = batch['input_ids'][:, 1:].contiguous()
        logits = model(**batch, use_cache=False)[1]
        loss = loss_fn(logits.view(-1, logits.shape[-1]), batch['labels'].view(-1))
        loss = loss.item()
        del logits
        total_loss += loss
        logits_repeat = model(**batch_repeat, use_cache=False)[1]
        loss_repeat = loss_fn(logits_repeat.view(-1, logits_repeat.shape[-1]), batch_repeat['labels'].view(-1))
        loss_repeat = loss_repeat.item()
        del logits_repeat
        total_loss_repeat += loss_repeat
        batch_count += 1
        generated = model.generate(
            input_ids = batch['input_ids'],
            attention_mask = batch['attention_mask'],
            top_p = gen_args.top_p,
            do_sample = True,
            num_return_sequences = gen_args.num_samples
        )
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        input_text = tokenizer.batch_decode(batch['input_ids'], skip_special_tokens=True)
        label_text = tokenizer.batch_decode(batch['labels'], skip_special_tokens=True)
        for ex_input, ex_label, ex_decoded in zip(input_text, label_text, chunks(decoded, gen_args.num_samples)):
            outputs.append([ex_input, ex_label, *ex_decoded])
        if gen_args.verbose:
            decoded = tokenizer.batch_decode(generated, skip_special_tokens=not gen_args.show_special_tokens)
            input_text = tokenizer.batch_decode(batch['input_ids'], skip_special_tokens=not gen_args.show_special_tokens)
            label_text = tokenizer.batch_decode(batch['labels'], skip_special_tokens=not gen_args.show_special_tokens)
            for ex_input, ex_label, ex_decoded in zip(input_text, label_text, chunks(decoded, gen_args.num_samples)):
                print('\nInput:', repr(ex_input))
                print('Target:   ', repr(ex_label))
                print('Predicted:', repr(ex_decoded))

    metrics['ppl_target'] = math.exp(total_loss/batch_count)
    metrics['ppl_repeat'] = math.exp(total_loss_repeat/batch_count)
    
    return outputs, metrics

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('model_path', type=str)
    p.add_argument('data_path', type=str)
    p.add_argument('--output_dir', type=str, default='predictions')
    p.add_argument('--batch_size', type=int, default=8)
    p.add_argument('--do_test', action='store_true')
    p.add_argument('--max_input_length', type=int, default=256)
    p.add_argument('--max_output_length', type=int, default=128)
    p.add_argument('--top_p', type=float, default=0.9)
    p.add_argument('--num_samples', type=int, default=10)
    p.add_argument('--device', type=str, default=None)
    p.add_argument('--show_special_tokens', action='store_true')
    p.add_argument('--verbose', action='store_true')
    args = p.parse_args()
    device = torch.device(args.device or ('cuda:0' if torch.cuda.is_available else 'cpu'))
    model = transformers.AutoModelForSeq2SeqLM.from_pretrained(args.model_path)
    tokenizer = transformers.AutoTokenizer.from_pretrained(args.model_path, use_fast=False)
    tweaks.patch_bart_tokenizer(tokenizer)
    model.config.update({
        'early_stopping': True,
        'max_length': args.max_output_length,
        'min_length': 8,
        'prefix': '',
        'decoder_start_token_id': tokenizer.bos_token_id
    })
    split = 'test' if args.do_test else 'val'
    dataset = Seq2SeqDataset(
        tokenizer,
        args.data_path,
        args.max_input_length,
        args.max_output_length,
        type_path=split
    )
    model.to(device)
    model.eval()
    outputs, metrics = run_eval(model, tokenizer, dataset, device, args)

    # compute BLEURT
    references = []
    candidates = []
    for row in outputs:
        reference = row[1]
        for sample in row[2:]:
            references.append(reference)
            candidates.append(sample)
    scorer = score.BleurtScorer("bleurt/bleurt-base-128")
    bleurt_scores = scorer.score(references=references, candidates=candidates)
    metrics['bleurt_mean'] = np.mean(bleurt_scores)
    metrics['bleurt_std'] = np.mean([np.std(samples) for samples in chunks(bleurt_scores, args.num_samples)])

    if args.verbose:
        print(metrics)

    out_dir = Path(os.path.join(
        args.output_dir,
        os.path.basename(os.path.normpath(strip_dataset_type(args.data_path))),
        os.path.basename(os.path.normpath(args.model_path))
    ))
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs_filename = out_dir / "outputs.tsv"
    metrics_filename = out_dir / "metrics.json"
    with open(str(outputs_filename), mode='w') as outputs_file:
        outputs_file.write("Input\tTarget\t"+'\t'.join(f"Prediction {i+1}" for i in range(args.num_samples))+"\tMean BLEURT\n")
        for row, ex_scores in zip(outputs, chunks(bleurt_scores, args.num_samples)):
            outputs_file.write("\t".join(map(repr, row)))
            outputs_file.write("\t"+str(np.mean(ex_scores)))
            outputs_file.write('\n')
    with open(str(metrics_filename), mode='w') as metrics_file:
        json.dump(metrics, metrics_file)


