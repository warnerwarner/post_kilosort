#!/bin/bash
# 
#SBATCH --job-name=finding_spikes
#SBATCH --array=1-64		## N_TASKS_TOTAL: SET THIS TO THE NUMBER OF INDEPENDENT JOBS,TYPICLLAY 100,SEE BELOW N_TASKS_TOTAL
#SBATCH --output=/home/camp/warnert/outputs/output_%a.txt	## 
#SBATCH --error=/home/camp/warnert/outputs/error_%a.txt
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem=20G
#SBATCH --partition=compute
#
python bandpass_segment.py $SLURM_ARRAY_TASK_ID
