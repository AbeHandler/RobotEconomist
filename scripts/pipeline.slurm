#!/bin/bash

#SBATCH --partition=amilan
#SBATCH --job-name=spacy_pipeline
#SBATCH --output=pipeline.%j.out
#SBATCH --qos=long
#SBATCH --time=7-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=8GB

set -e
source /curc/sw/anaconda3/latest
module load anaconda
module load gnu_parallel

conda run -n econ python -m src.pipelines.pipeline
