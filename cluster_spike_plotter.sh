#!/bin/bash
# 
#SBATCH --job-name=plotting_spikes
#SBATCH --array=0-29		## N_TASKS_TOTAL: SET THIS TO THE NUMBER OF INDEPENDENT JOBS,TYPICLLAY 100,SEE BELOW N_TASKS_TOTAL
#SBATCH --output=/home/camp/warnert/outputs/output_%a.txt	## 
#SBATCH --error=/home/camp/warnert/outputs/error_%a.txt
#SBATCH --ntasks=1
#SBATCH --time=1:00:00
#SBATCH --mem=25G
#SBATCH --partition=compute
#

python cluster_spike_plotter.py $SLURM_ARRAY_TASK_ID
