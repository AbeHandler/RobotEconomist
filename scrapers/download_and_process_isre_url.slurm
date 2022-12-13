#!/bin/bash

#SBATCH --partition=amilan
#SBATCH --job-name=process_mnsc_url
#SBATCH --output=informs.out
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1    # note this can't be too big or you will overrun your storage when decompressing

# module load slurm/summit to access summit scheduler

module load gnu_parallel
source /curc/sw/anaconda3/latest
conda activate econ
cd /scratch/alpine/abha4861/RobotEconomist/scrapers

CODE=isre

python informs_abstracts_downloader.py $CODE
gzip $CODE".abstracts.jsonl"
python process_abstracts_to_sentences.py -code $CODE
gzip $CODE".sentences.jsonl"
