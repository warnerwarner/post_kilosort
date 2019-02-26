#!/bin/bash
# 
#SBATCH --job-name=spike_plotter
#SBATCH --array=2,5,13,14,20,37,47,51,65,66		## N_TASKS_TOTAL: SET THIS TO THE NUMBER OF INDEPENDENT JOBS,TYPICLLAY 100,SEE BELOW N_TASKS_TOTAL
#SBATCH --output=/home/camp/warnert/outputs/output_%a.txt	## 
#SBATCH --error=/home/camp/warnert/outputs/error_%a.txt
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem=30G
#SBATCH --partition=compute
#

python plot_cluster_spikes.py $SLURM_ARRAY_TASK_ID