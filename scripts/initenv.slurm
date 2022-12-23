#!/bin/bash 

#SBATCH --partition=amilan
#SBATCH --job-name=initenv
#SBATCH --output=initenv.out
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1    # note this can't be too big or you will overrun your storage when decompressing

# module load slurm/summit to access summit scheduler

# setup => write subreddits to targets.txt, or other targets like author names

module load gnu_parallel
source /curc/sw/anaconda3/latest
cd /scratch/alpine/abha4861/RobotEconomist
conda env remove -n econ
conda env create -f config/econ.yml
conda activate econ
python -m spacy download en_core_web_sm
