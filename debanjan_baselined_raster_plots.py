'''
Creates baseline subtracted psths, used with debanjan
'''

import openephys as oe
import numpy as np
import pickle
import sys
from cluster_spike_plotter import *
from clusterbank_maker import *
from trial_finder import *
import matplotlib.pyplot as plt
import os
import time
from scipy.signal import find_peaks


def find_good_resps(respiration, peaks, *, trial_length=2, extra_window=5, fs=30000, width = 22000):
	'''
	Finds the starts and ends of respiration cycles which are not too gaspy and aren't inside a trial
	Arguments:
	respiration:
		respiration trace
	peaks
		The peaks for the respiration, needs to be finessed for each recording

	Optional arguments:
	trial_length:
		Length of the trial in seconds
	extra_window:
		Additional length which a repiration must be away from a trial
	fs:
		Sampling frequency
	width:
		Width between the beginning and the end of the end of the respiration trial
	'''
	starts = []
	ends = []
	for start, end in zip(peaks[0][:-1], peaks[0][1:]):
		in_trial = False
		#diffs.append(j-i)
		if end-start < 22000:
			for trial in trial_starts:
				if 0 < start - trial < fs*(trial_length + extra_window) or 0 < end - trial < fs*(trial_length + extra_window):

					in_trial = True

			if not in_trial:
				starts.append(i)
				ends.append(j)
	return starts, ends



def baselined_psth():
	'''
	Makes a baseline subtracted psth
	'''
	trial_spikes = find_trial_spike_times(trial_starts, cluster_spikes, trial_length=trial_length)
	for index, trial in enumerate(trial_spikes):
		count = np.bincount(np.digitize(trial, trial_time, right=1))/bin_size
		while len(count) < len(trial_time) + 1:
			count = np.append(count, 0)
		trial_start = trial_starts[index]
		trial_resp = resp[trial_start - pre_trial_resp_window*fs:trial_start+fs*(post_trial_resp_window+trial_length)]
		trial_peaks = find_peaks(trial_resp, height=[1.4, 2.2], distance=13000)
		trial_sniff_spikes = []
		for i, j in zip(trial_peaks[0][:-1], trial_peaks[0][1:]):
			trial_sniff_spikes.extend([(k*(j-i) + i)/fs - 3 for k in sniff_spikes])
		sniff_trial_time = np.arange(-pre_trial_resp_window, trial_length+post_trial_resp_window, bin_size)
		


# Set the directories and load in the starts and the respiration
home_dir = '/home/camp/warnert/working/Recordings/190222/2019-02-22_14-15-45'
fs = 30000
trial_length = 2
extra_window = 5
num_of_repeats = 21
bin_size = 0.05
pre_trial_resp_window = 3
post_trial_resp_window = 3
trial_types = ['Corr/anticorr', 'Odour A', 'Odour B', 'Blank']




clusterbank = make_clusterbank_basic(home_dir, 32)
gclusterbank = clusterbank['good']
if os.path.isfile(os.path.join(home_dir, 'trial_starts.npy')):
	trial_starts = np.fromfile(os.path.join(home_dir, 'trial_starts.npy'), dtype= np.int)
else:
	trial_starts = find_trials(home_dir, trial_size=trial_length)
resp = oe.loadContinuous2(os.path.join(home_dir, '100_ADC1.continuous'))['data']


# Go through and find the order and the indexes of the trials by the experiment type

trial_names = ['10Hz anticorr', '5Hz blank', '15Hz A', '2Hz B', '2Hz anticorr', '20Hz blank', 
				'20Hz anticorr', '5Hz B', '20Hz A', '20Hz B', '2Hz blank', '2Hz corr', 
				'10Hz B', '2Hz A', '10Hz blank', '15Hz blank', '10Hz corr', '10Hz A', 
				'5Hz A', '15Hz B', '20Hz corr']

ac_trials = [index for index, i in enuermate(trial_names) if 'corr' in i]
A_trials = [index for index, i in enumerate(trial_names) if 'A' in i]
B_trials = [index for index, i in enumerate(trial_names) if 'B' in i]
blank_trials = [index for index, i in enumerate(trial_names) if 'blank' in i]

for i in ac_trials:
	print(i, trial_names[i])
trial_groups = [ac_trials, A_trials, B_trials, blank_trials]

peaks = find_peaks(resp, height=[1.4, 2.2], distance=13000, prominence=0.1)

starts, ends = find_good_resps(resp, peaks)

trial_time = np.arange(-trial_length, 2*trial_length, bin_size)
