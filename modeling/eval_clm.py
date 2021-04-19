
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys
import transformers
import torch
import argparse
import os.path
from modeling.utils import chunks
import torch
import json
from tqdm import tqdm
import math
from pathlib import Path
from bleurt import score
import numpy as np

def capitalize(s):
    s = s.lstrip()
    return s[0].upper() + s[1:]

def get_repeated_form(s):
    idx = s.rfind(' Therefore,')
    if idx != -1:
        s = s[:idx]
    return s[0].lower() + s[1:]

def strip_dataset_type(path):
    return os.path.splitext(path)[0]

def run_eval(model, tokenizer, dataset, args):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    total_loss = 0
    total_loss_repeat = 0
    batch_count = 0
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    outputs = []
    metrics = {}
    for batch in tqdm(list(chunks(dataset, args.batch_size))):
        inputs_prompt_only = tokenizer.batch_encode_plus([ex['prompt'] for ex in batch], return_tensors='pt', padding=True, truncation=True).to(device)
        targets = tokenizer.batch_encode_plus([ex['answer'] for ex in batch], return_tensors='pt', padding=True, truncation=True).to(device)
        inputs_all = tokenizer.batch_encode_plus([ex['prompt']+' '+ex['answer'] for ex in batch], return_tensors='pt', padding=True, truncation=True).to(device)
        inputs_repeat = tokenizer.batch_encode_plus([ex['prompt']+' '+get_repeated_form(ex['prompt']) for ex in batch], return_tensors='pt', padding=True, truncation=True).to(device)
        labels = inputs_all['input_ids'].clone()
        labels[labels == tokenizer.pad_token_id] = -100
        labels[:, :inputs_prompt_only['input_ids'].shape[1]][inputs_prompt_only['input_ids'] != tokenizer.pad_token_id] = -100
        loss = model(
            input_ids=inputs_all.input_ids,
            attention_mask=inputs_all.attention_mask,
            labels=labels,
            use_cache=False
        )[0]
        loss = loss.item()
        total_loss += loss
        labels_repeat = inputs_repeat['input_ids'].clone()
        labels_repeat[labels_repeat == tokenizer.pad_token_id] = -100
        labels_repeat[:, :inputs_prompt_only['input_ids'].shape[1]][inputs_prompt_only['input_ids'] != tokenizer.pad_token_id] = -100
        loss_repeat = model(
            input_ids=inputs_repeat.input_ids,
            attention_mask=inputs_repeat.attention_mask,
            labels=labels_repeat,
            use_cache=False
        )[0]
        loss_repeat = loss_repeat.item()
        total_loss_repeat += loss_repeat
        batch_count += 1
        generated = model.generate(
            input_ids = inputs_prompt_only.input_ids,
            attention_mask = inputs_prompt_only.attention_mask,
            max_length = labels.shape[1],
            top_p = args.top_p,
            do_sample = True,
            num_return_sequences = args.num_samples
        )
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        for ex, ex_decoded in zip(batch, chunks(decoded, args.num_samples)):
            outputs.append([ex['prompt'], ex['answer'], *(e[len(ex['prompt']):] for e in ex_decoded)])

    metrics['ppl_target'] = math.exp(total_loss/batch_count)
    metrics['ppl_repeat'] = math.exp(total_loss_repeat/batch_count)

    return outputs, metrics

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('model_path', type=str)
    p.add_argument('data_path', type=str)
    p.add_argument('--output_dir', type=str, default='predictions')
    p.add_argument('--batch_size', type=int, default=8)
    p.add_argument('--top_p', type=float, default=0.9)
    p.add_argument('--num_samples', type=int, default=10)
    args = p.parse_args()
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    model = transformers.AutoModelForCausalLM.from_pretrained(args.model_path)
    tokenizer = transformers.AutoTokenizer.from_pretrained(args.model_path, use_fast=False)
    with open(args.data_path) as data_file:
        dataset = json.load(data_file)
    model.to(device)
    model.eval()
    outputs, metrics = run_eval(model, tokenizer, dataset, args)

    # compute BLEURT
    references = []
    candidates = []
    for row in outputs:
        reference = capitalize(row[1])
        for sample in row[2:]:
            references.append(reference)
            candidates.append(capitalize(sample))
    scorer = score.BleurtScorer("bleurt/bleurt-base-128")
    bleurt_scores = scorer.score(references=references, candidates=candidates)
    metrics['bleurt_mean'] = np.mean(bleurt_scores)
    metrics['bleurt_std'] = np.mean([np.std(samples) for samples in chunks(bleurt_scores, args.num_samples)])
    
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