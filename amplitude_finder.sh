#!/bin/bash
# 
#SBATCH --job-name=amplitude_finder
#SBATCH --array=0,6,8,9,14,15,16,17,18,19,22,25,26,28,30,32,34,38,43,45,53,74,76,77,78,80,88,89,92,93,94,98,106,110,111,112,113,114,115,116,119,126,127,128,129,130,132,133,142,143,144,145,146,147	## N_TASKS_TOTAL: SET THIS TO THE NUMBER OF INDEPENDENT JOBS,TYPICLLAY 100,SEE BELOW N_TASKS_TOTAL
#SBATCH --output=/home/camp/warnert/outputs/output_%a.txt	## 
#SBATCH --error=/home/camp/warnert/outputs/error_%a.txt
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem=30G
#SBATCH --partition=compute
#

python amplitude_finder.py $SLURM_ARRAY_TASK_ID