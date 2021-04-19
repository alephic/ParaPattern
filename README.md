
# Flexible Operations for Natural Language Deduction
## a.k.a. ParaPattern

[Kaj Bostrom](https://bostromk.net/), [Lucy Zhao](https://github.com/xyz-zy), [Swarat Chaudhuri](https://www.cs.utexas.edu/~swarat/), and [Greg Durrett](https://www.cs.utexas.edu/~gdurrett/)

This repository contains all the code needed to replicate the experiments from the paper, and additionally provides a set of tools to
put together new natural language deduction operations from scratch.

In the [`data/`](data/) folder, you'll find all the data used to train and evaluate our models, already preprocessed and ready to go, with the exception of the MNLI dataset due to its size - if you want to replicate our MNLI-BART baseline, you'll need to download a copy of MNLI and run [`data/mnli/filter.py`](data/mnli/filter.py) for yourself.
The `data` folder also contains several generic conversion scripts, which you may find useful for processing operation training examples, as well as [`paraphrase.py`](data/paraphrase.py), which does automatic paraphrase generation if you pass it a path to a suitable sequence-to-sequence paraphrasing model checkpoint, e.g. <https://huggingface.co/tuner007/pegasus_paraphrase>

In the [`modeling/`](modeling/) folder, you'll find the fine-tuning code needed to train operation models, as well as scripts to run all the evaluations described in the paper. Just make sure you're on [`transformers`](https://github.com/huggingface/transformers) version 4.2.1, not the latest version, since several of the scripts are carefully built around bugs that have since been patched out of the library.

If you have access to multiple GPUs, you can change the `--nproc_per_node` argument in [`finetune.sh`](modeling/finetune.sh) from 1 to whatever number of GPUs you want to use for training.

In the [`dep_search/`](dep_search/) folder, you'll find tools to perform bulk dependency parsing using `spaCy`, as well as scripts to index the resulting stream of dependency trees and scrape them using dependency patterns. For reference, the templates used in the paper live in [`dep_search/templates/`](dep_search/templates/). If you want to write your own templates, a good place to start is playing around with the dependency pattern DSL using `dep_search.struct_query.parse_query` - if you're wondering how to express a given syntactic pattern, you can start by calling `dep_search.struct_query.Head.from_spacy` on a `spaCy` token; this will construct a syntactic pattern without any slots from that token's dependency subtree. Printing patterns this way is a great way to familiarize yourself with dependency structure if you need to brush up on that stuff (I can never remember what POS tag/arc label conventions `spaCy` uses so I was printing out a lot of these trees while I was developing the templates we used in the paper).

Unfortunately, I never got around to optimizing the syntactic search process all that well, so for large free-text corpora (~=100M sentences or more) it can take a day or two to do a full run of parsing and indexing using [`dep_search/scrape.py`](dep_search/scrape.py). I find a good way to iterate on a pattern is to start by casting a really broad net, and then narrow down your pattern on a subset of those results so that you don't have to re-index your whole original corpus each time you make a small change to a template.