#!/bin/bash

#SBATCH --partition=amilan
#SBATCH --job-name=spacy_pipeline
#SBATCH --output=pipeline.%j.out
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=32GB

set -e
source /curc/sw/anaconda3/latest
module load anaconda
module load gnu_parallel

my_parallel="parallel --eta --delay .2 -j $SLURM_NTASKS"
my_srun="srun --export=all --exclusive -n1 --cpus-per-task=1 --mem-per-cpu 2G --cpu-bind=cores"

# 1. looks for txt files in data/$corpus/txt
# 2. splits the files into file lists
# 3. runs spacy on each file list and makes a doc bin per file list
# 4. merges all the little doc bins into big docbins in data/corpus/spacy

set -e

corpus="s2orcfull"

echo "[*] running scripts/process_corpus_locally_with_spacy.sh on data/"$corpus

# find "data/"$corpus"/txt" -type f > "tmp/"$corpus".txt"

# split -l 500 "tmp/"$corpus".txt" "tmp/"$corpus"/splits/"

# find "tmp/""$corpus""/splits" -type f | conda run --no-capture-output -n econ clean -e ".docbin" -o "tmp/"$corpus"/proc" | $my_parallel "$my_srun conda run --no-capture-output -n econ python -m scripts.file_list_2_docbin {} '$corpus'"

conda run -n econ python -m scripts.merge_doc_bins --corpus "$corpus" --path-to-unmerged-doc-bins "tmp/""$corpus""/proc" --path-to-merged-doc-bins "data/""$corpus""/spacy"
