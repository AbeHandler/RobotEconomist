#!/bin/bash

#SBATCH --partition=amilan
#SBATCH --job-name=codes
#SBATCH --output=codes.out
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1    # note this can't be too big or you will overrun your storage when decompressing

# module load slurm/summit to access summit scheduler

module load gnu_parallel
source /curc/sw/anaconda3/latest
conda activate econ
cd /scratch/alpine/abha4861/RobotEconomist/scrapers

./download_informs_abstracts.sh mnsc