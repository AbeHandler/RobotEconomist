#!/usr/bin/env bash

# 1. looks for txt files in data/$corpus/txt
# 2. splits the files into file lists 
# 3. runs spacy on each file list and makes a doc bin per file list
# 4. merges all the little doc bins into big docbins in data/corpus/spacy

set -e

corpus=$1

echo "[*] running scripts/process_corpus_locally_with_spacy.sh on data/"$corpus

find "data/"$corpus"/txt" -type f > "tmp/"$corpus".txt"

split -l 500 "tmp/"$corpus".txt" "tmp/"$corpus"/splits/"

find "tmp/""$corpus""/splits" -type f | conda run --no-capture-output -n econ clean -e ".docbin" -o "tmp/"$corpus"/proc" | parallel --eta -j 4 "conda run --no-capture-output -n econ python -m scripts.file_list_2_docbin {} '$corpus'"

python -m scripts.merge_doc_bins --corpus "$corpus" --path-to-unmerged-doc-bins "tmp/""$corpus""/proc" --path-to-merged-doc-bins "data/""$corpus""/spacy"