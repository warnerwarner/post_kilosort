'''
Finds where trials begins by loading in the additional files
'''

import openephys as oe 
import numpy as np 
import pandas
import os
import psutil

def find_trials(home_dir, *,add_chan_prefix='100_ADC', add_chans_nums=[2,3,4,5], fs=30000, trial_size=5, tofile=True):
	'''
	Finds trials in a recording

	Arguments:
	home_dir:
		The directory that the continuous files are stored in

	Optional arguments:
	add_chan_prefix:
		The prefix for the addition channels, if everything is working it should be 100_ADC but a few of the recordings went a bit weird
	add_chans_nums:
		The numbers of the valve channels default is 2,3,4,5
	fs:
		The sampling rate of the additional channels 
	trial_size:
		Size of the trials, if the trials are of multiple lengths take the trials with the longest window, however, as long as there is a sizable window between trials it should be fine
	tofile:
		Save the starts to a numpy array file or not
	'''

	# Add the channels prefix to the channel numbers
	additional_channels = [add_chan_prefix + '%d.continuous' % i for i in add_chans_nums]
	add_chans = []

	# Run through all the additional files
	for i in additional_channels:
		chan= oe.loadContinuous2(os.path.join(home_dir, i))
		data = chan['data']
		add_chans.append(data)
	# Sum all the channels together pairwise so that the array goes from a (4, t) to a t array
	summed_valves = np.sum(add_chans, axis=0)
	starts = []

	# Set the initial previous trial start to be negative
	prev_value = -trial_size*fs

	# Run through all the t values in the summed array
	# if they're larger than 1 and further than the trial size (times 1.1) from the previous then add them to the array
	for index, i in enumerate(summed_valves):
		if i > 1 and index-prev_value > 1.1*(trial_size*fs):
			starts.append(index)
			prev_value = index

	# Turn into a numpy array
	starts = np.array(starts)

	if tofile:
		starts.tofile(os.path.join(home_dir, 'trial_starts.npy'))
	return starts

if __name__ == '__main__':

	available_cpu_count = len(psutil.Process().cpu_affinity())
	os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)


	home_dir = '/home/tom/d/Recordings/190410/2019-04-10_15-04-49'

	find_trials(home_dir)