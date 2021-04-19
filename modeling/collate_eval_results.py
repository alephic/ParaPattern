import argparse
import os
import sys
import json

def erase_if_present(s, r):
    i = s.find(r)
    if i != -1:
        return s[:i] + s[i+len(r):]
    return s

if __name__ == "__main__":
    tables = {}
    derived_metrics = [
        ('ppl_target_minus_repeat', lambda m: m['ppl_target'] - m['ppl_repeat'])
    ]
    split_prefixes = set()
    for split_name in os.listdir(sys.argv[1]):
        split_prefix = split_name[:split_name.find('_')+1]
        split_prefixes.add(split_prefix)
        for model_name in os.listdir(os.path.join(sys.argv[1], split_name)):
            with open(os.path.join(sys.argv[1], split_name, model_name, 'metrics.json')) as metrics_file:
                model_name = erase_if_present(model_name, split_prefix)
                metrics = json.load(metrics_file)
                for metric_name, metric_fn in derived_metrics:
                    metrics[metric_name] = metric_fn(metrics)
                for metric, value in metrics.items():
                    if metric not in tables:
                        tables[metric] = ({}, set(), set())
                    table, split_names, model_names = tables[metric]
                    table[split_name, model_name] = value
                    split_names.add(split_name)
                    model_names.add(model_name)
    for table_metric_name, (table, split_names, model_names) in tables.items():
        mean_split_names = []
        for split_prefix in split_prefixes:
            mean_split_name = split_prefix+'mean'
            mean_split_names.append(mean_split_name)
            for model_name in model_names:
                total = 0
                count = 0
                for split_name in split_names:
                    if split_name.startswith(split_prefix):
                        total += table[split_name, model_name]
                        count += 1
                table[mean_split_name, model_name] = total/count
        split_names.update(mean_split_names)
        with open(os.path.normpath(sys.argv[1])+'_'+table_metric_name+'.tsv', mode='w') as table_file:
            split_names_sorted = sorted(split_names)
            table_file.write('\t'.join(['-']+split_names_sorted)+'\n')
            for model_name in sorted(model_names):
                table_file.write(model_name+'\t')
                table_file.write('\t'.join(map(str, (table[split_name, model_name] for split_name in split_names_sorted))))
                table_file.write('\n')
