'''
Finds where trials begins by loading in the additional files
'''

import openephys as oe 
import numpy as np 
import pandas
import os
import psutil

def find_trials(home_dir, *,add_chan_prefix='100_ADC', add_chans_nums=[2,3,4,5], fs=30000, trial_size=5, tofile=True):
	additional_channels = [add_chan_prefix + '%d.continuous' % i for i in add_chans_nums]
	add_chans = []
	for i in additonal_channels:
		chan= oe.loadContinuous2(os.path.join(home_dir, i))
		data = chan['data']
		add_chans.append(data)
	summed_valves = np.sum(add_chans, axis=0)
	starts = []

	prev_value = -trial_size*fs

	for index, i in enumerate(summed_valves):
		if i > 1 and index-prev_value > 1.1*(trial_size*fs):
			starts.append(index)
			prev_value = index
	starts = np.array(starts)

	if tofile:
		starts.tofile(os.path.join(home_dir, 'trial_starts.npy'))
	return starts

if __name__ == '__main__':

	available_cpu_count = len(psutil.Process().cpu_affinity())
	os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)


	home_dir = '/home/tom/d/Recordings/190410/2019-04-10_15-04-49'

	find_trials(home_dir)