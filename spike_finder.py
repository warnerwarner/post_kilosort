import openephys as oe
import numpy as np
import matplotlib.pyplot as plt
import os
import psutil
from scipy import signal
import numpy as np


def bandpass_data(data, fs= 30000, highcut=6000, lowcut = 300, order = 3):
	nyq = 0.5*fs
	low = lowcut/nyq 
	high = highcut/nyq 
	sos = signal.butter(3, [low, high], analog=False, btype='band', output = 'sos')
	y = signal.sosfiltfilt(sos, data)
	return y

def spike_find(bp_data):
	spike_times = []
	sd = np.median(abs(bp_data)/0.6745)
	data_times = []
	prev_spike = -30
	for index, j in enumerate(bp_data):
		if j < -4*sd and index-prev_spike > 30:
			data_times.append(index)
			prev_spike = index
	spike_times.append(data_times)
	return spike_times


available_cpu_count = len(psutil.Process().cpu_affinity())
os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)



chans = [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 1]

home_dir = '/home/camp/warnert/working/Recordings/190211/2019-02-11_16-35-46'

all_spike_times = []
for chan in chans:
	channel_base = os.path.join(home_dir, '100_CH%d.continuous' % chan)

	chan_rec = oe.loadContinuous2(channel_base)

	data =chan_rec['data']
	bp_data = bandpass_data(data)
	spike_times = spike_find(bp_data)
	all_spike_times.append(spike_times)

all_spike_times = np.array(all_spike_times)
np.save(os.path.join(home_dir, 'channel_spike_times.npy'), all_spike_times)