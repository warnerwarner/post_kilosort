#!/bin/bash
# 
#SBATCH --job-name=spike_finder
#SBATCH --array=[16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,1]		## N_TASKS_TOTAL: SET THIS TO THE NUMBER OF INDEPENDENT JOBS,TYPICLLAY 100,SEE BELOW N_TASKS_TOTAL
#SBATCH --output=/home/camp/warnert/outputs/output_%a.txt	## 
#SBATCH --error=/home/camp/warnert/outputs/error_%a.txt
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem=50G
#SBATCH --partition=compute
#

python spike_finder.py $SLURM_ARRAY_TASK_ID