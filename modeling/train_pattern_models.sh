#!/bin/bash
cd "$(dirname $0)/.."
step_gen/finetune.sh --model_name_or_path facebook/bart-large --data_dir data/wiki/hearst_metonyms_s2s --output_dir trained_models/bart_large_subst_orig_only --overwrite_output_dir --num_train_epochs 1 --evaluation_strategy no
step_gen/finetune.sh --model_name_or_path facebook/bart-large --data_dir data/wiki/hearst_metonyms_s2s_2x_para --output_dir trained_models/bart_large_subst_para_only --overwrite_output_dir --num_train_epochs 1 --evaluation_strategy no
step_gen/finetune.sh --model_name_or_path facebook/bart-large --data_dir data/wiki/hearst_metonyms_s2s_2x_para_plus_orig --output_dir trained_models/bart_large_subst_plus_para --overwrite_output_dir --num_train_epochs 1 --evaluation_strategy no
step_gen/finetune.sh --model_name_or_path facebook/bart-large --data_dir data/wiki/contrapositive_s2s --output_dir trained_models/bart_large_contra_orig_only --overwrite_output_dir --num_train_epochs 1 --evaluation_strategy no
step_gen/finetune.sh --model_name_or_path facebook/bart-large --data_dir data/wiki/contrapositive_s2s_2x_para --output_dir trained_models/bart_large_contra_para_only --overwrite_output_dir --num_train_epochs 1 --evaluation_strategy no
step_gen/finetune.sh --model_name_or_path facebook/bart-large --data_dir data/wiki/contrapositive_s2s_2x_para_plus_orig --output_dir trained_models/bart_large_contra_plus_para --overwrite_output_dir --num_train_epochs 1 --evaluation_strategy no