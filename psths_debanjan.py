import numpy as np
import pickle
import sys
from cluster_spike_plotter import *
from clusterbank_maker import *
from trial_finder import *
import matplotlib.pyplot as plt
import os
from scipy.signal import find_peaks


def find_trial_cluster_spikes(clusterbank, num_of_exps, trial_starts, *, trial_length = 2):
	'''
	Finds the spikes for all the experiments
	'''
	
	for experiment_num in range(num_of_exps):
		print(experiment_num)
		trial_cluster_spikes = []
		for index, cluster_num in enumerate(clusterbank):
			cluster = clusterbank[cluster_num]
			trial_cluster_spikes.append(find_trial_spike_times(trial_starts[experiment_num::num_of_exps], cluster['times'], trial_length=trial_length))

	return trial_cluster_spikes


def raster_plots(clusterbank, num_of_trials, *, savefig=True, save_loc = 'conditional_raster_plots'):
	'''
	Plots a set of raster plots for each of the clusters for each experimental trials

	Arguments:
	cluserbank:
		The clusterbank to be plotted
	num_of_trials:
		Number of trials

	Optional arguments:
	savefig:
		Should the fig be saved?
	save_loc:
		The location of the figure to be saved
	'''
	for experiment_num in range(num_of_trials):
		print(experiment_num)
		trial_cluster_spikes = []
		for index, cluster_num in enumerate(clusterbank):
			cluster = clusterbank[cluster_num]
			trial_cluster_spikes.append(find_trial_spike_times(trial_starts[experiment_num::num_of_trials], cluster['times'], trial_length = 2))





# Directory for the data location, trialbank and the number of channels
home_dir = ''
trialbank_loc = ''
chan_number = 32


clusterbank = make_clusterbank_basic(home_dir, 32)
trialbank = pickle.Unpickler(open(trialbank_loc, 'rb')).load()


# The order of the trials played to the mouse
trial_names = ['10Hz anticorr', '5Hz blank', '15Hz A', '2Hz B', '2Hz anticorr', '20Hz blank', '20Hz anticorr', '5Hz B', '20Hz A', '20Hz B', '2Hz blank', '2Hz corr', '10Hz B', '2Hz A', '10Hz blank', '15Hz blank', '10Hz corr', '10Hz A', '5Hz A', '15Hz B', '20Hz corr']
ac_trials = [index for index, i in enumerate(trial_names)if 'corr' in i ]
A_trials  = [index for index, i in enumerate(trial_names) if 'A' in i and 'corr' not in i]
B_trials = [index for index, i in enumerate(trial_names) if 'B' in i and 'corr' not in i]
blank_trials = [index for index, i in enumerate(trial_names) if 'blank' in i]
for i in ac_trials:
    print(i, trial_names[i])
trial_groups = [ac_trials, A_trials, B_trials, blank_trials]

