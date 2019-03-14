import openephys as oe
import numpy as np
import matplotlib.pyplot as plt
import os
import psutil
from scipy import signal
import numpy as np


def bandpass_data(datas, fs= 30000, highcut=6000, lowcut = 300, order = 3):
	nyq = 0.5*fs
	low = lowcut/nyq 
	high = highcut/nyq 
	sos = signal.butter(3, [low, high], analog=False, btype='band', output = 'sos')
	y = signal.sosfiltfilt(sos, data)

def spike_find(datas):
	spike_times = []
	for i in datas:
		sd = np.median(abs(i)/0.6745)
		data_times = []
		prev_spike = -30
		for index, j in enumerate(i):
			if j < -4*sd and index-prev_spike > 30:
				data_times.append(index)
				prev_spike = index
		spike_times.append(data_times)
	return spike_times

jULIE_loc = 
nn_loc = 

jULIE_chans = [25, 26, 27, 28, 29]
nn_chans = [8, 7, 11, 6, 5]

repeat = list(sys.argv)[1]
length = 18000000


jULIE_data = [oe.loadContinuous2(os.path.join(jULIE_loc, '100_CH%d.continuous' % i))['data'][repeat*length:length*(repeat+1)] for i in jULIE_chans]
nn_data = [oe.loadContinuous2(os.path.join(nn_loc, '100_CH%d.continuous' % i))['data'][repeat*length:length*(repeat+1)] for i in nn_chans]


bp_j = bandpass_data(jULIE_data)
bp_n = bandpass_data(nn_data)


311488512
132733952
