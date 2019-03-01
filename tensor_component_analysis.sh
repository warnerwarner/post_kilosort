#!/bin/bash
# 
#SBATCH --job-name=tca
#SBATCH --array=1-50		## N_TASKS_TOTAL: SET THIS TO THE NUMBER OF INDEPENDENT JOBS,TYPICLLAY 100,SEE BELOW N_TASKS_TOTAL
#SBATCH --output=/home/camp/warnert/outputs/output_%a.txt	## 
#SBATCH --error=/home/camp/warnert/outputs/error_%a.txt
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem=250G
#SBATCH --partition=compute
#

python tensor_component_analysis.py $SLURM_ARRAY_JOB_ID $SLURM_ARRAY_TASK_ID