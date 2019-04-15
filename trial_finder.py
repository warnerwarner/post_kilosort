'''
Finds where trials begins by loading in the additional files
'''

import openephys as oe 
import numpy as np 
import pandas
import os
import psutil

available_cpu_count = len(psutil.Process().cpu_affinity())
os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)


home_dir = '/home/camp/warnert/working/Recordings/190211/2019-02-11_16-35-46'

additonal_channels = ['100_ADC%d.continuous' % i for i in range(2, 6)]
add_chans = []


for i in additonal_channels:
	chan= oe.loadContinuous2(os.path.join(home_dir, i))
	data = chan['data']
	add_chans.append(data)


summed_valves = np.sum(add_chans, axis=0)

starts = []

fs = 30000
trial_size = 5 # In seconds


prev_value = - trial_size*fs


for index, i in enumerate(summed_valves):
	if i > 1 and index - prev_value > 1.1*(trial_size*fs):
		starts.append(index)
		prev_value = index

starts = np.array(starts)

starts.tofile(os.path.join(home_dir, 'trial_starts.npy'))

		