
cd "$(dirname $0)/.."
# Subst probe, no para
python3.8 -m modeling.eval_s2s trained_models/bart_large_subst_orig_only data/contrast/subst_test/subst_control_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_subst_orig_only data/contrast/subst_test/subst_test_n_syn_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_subst_orig_only data/contrast/subst_test/subst_test_v_syn_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_subst_orig_only data/contrast/subst_test/subst_test_nv_syn_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_subst_orig_only data/contrast/subst_test/subst_test_num_agreement_s2s --output_dir predictions/contrast
# Subst probe, with para
python3.8 -m modeling.eval_s2s trained_models/bart_large_subst_plus_para data/contrast/subst_test/subst_control_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_subst_plus_para data/contrast/subst_test/subst_test_n_syn_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_subst_plus_para data/contrast/subst_test/subst_test_v_syn_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_subst_plus_para data/contrast/subst_test/subst_test_nv_syn_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_subst_plus_para data/contrast/subst_test/subst_test_num_agreement_s2s --output_dir predictions/contrast
# Subst probe, MNLI
python3.8 -m modeling.eval_s2s trained_models/bart_large_mnli data/contrast/subst_test/subst_control_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_mnli data/contrast/subst_test/subst_test_n_syn_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_mnli data/contrast/subst_test/subst_test_v_syn_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_mnli data/contrast/subst_test/subst_test_nv_syn_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_mnli data/contrast/subst_test/subst_test_num_agreement_s2s --output_dir predictions/contrast
# Subst probe, zero-shot
python3.8 -m modeling.eval_clm gpt2-large data/contrast/subst_test/subst_control.json --output_dir predictions/contrast
python3.8 -m modeling.eval_clm gpt2-large data/contrast/subst_test/subst_test_n_syn.json --output_dir predictions/contrast
python3.8 -m modeling.eval_clm gpt2-large data/contrast/subst_test/subst_test_v_syn.json --output_dir predictions/contrast
python3.8 -m modeling.eval_clm gpt2-large data/contrast/subst_test/subst_test_nv_syn.json --output_dir predictions/contrast
python3.8 -m modeling.eval_clm gpt2-large data/contrast/subst_test/subst_test_num_agreement.json --output_dir predictions/contrast
# Contra probe, no para
python3.8 -m modeling.eval_s2s trained_models/bart_large_contra_orig_only data/contrast/contrapositive_test/contra_control_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_contra_orig_only data/contrast/contrapositive_test/contra_test_postnominal_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_contra_orig_only data/contrast/contrapositive_test/contra_test_prenominal_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_contra_orig_only data/contrast/contrapositive_test/contra_test_negation_s2s --output_dir predictions/contrast
# Contra probe, with para
python3.8 -m modeling.eval_s2s trained_models/bart_large_contra_plus_para data/contrast/contrapositive_test/contra_control_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_contra_plus_para data/contrast/contrapositive_test/contra_test_postnominal_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_contra_plus_para data/contrast/contrapositive_test/contra_test_prenominal_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_contra_plus_para data/contrast/contrapositive_test/contra_test_negation_s2s --output_dir predictions/contrast
# Contra probe, MNLI
python3.8 -m modeling.eval_s2s trained_models/bart_large_mnli data/contrast/contrapositive_test/contra_control_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_mnli data/contrast/contrapositive_test/contra_test_postnominal_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_mnli data/contrast/contrapositive_test/contra_test_prenominal_s2s --output_dir predictions/contrast
python3.8 -m modeling.eval_s2s trained_models/bart_large_mnli data/contrast/contrapositive_test/contra_test_negation_s2s --output_dir predictions/contrast
# Contra probe, zero-shot
python3.8 -m modeling.eval_clm gpt2-large data/contrast/contrapositive_test/contra_control.json --output_dir predictions/contrast
python3.8 -m modeling.eval_clm gpt2-large data/contrast/contrapositive_test/contra_test_postnominal.json --output_dir predictions/contrast
python3.8 -m modeling.eval_clm gpt2-large data/contrast/contrapositive_test/contra_test_prenominal.json --output_dir predictions/contrast
python3.8 -m modeling.eval_clm gpt2-large data/contrast/contrapositive_test/contra_test_negation.json --output_dir predictions/contrast