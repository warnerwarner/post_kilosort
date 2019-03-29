#!/bin/bash
# 
#SBATCH --job-name=spike_plotter
#SBATCH --array=1-20
#SBATCH --output=/home/camp/warnert/outputs/output_%a.txt	## 
#SBATCH --error=/home/camp/warnert/outputs/error_%a.txt
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem=100G
#SBATCH --partition=compute
#

python simple_vs_plume_tca.py $SLURM_ARRAY_TASK_ID $SLURM_ARRAY_JOB_ID