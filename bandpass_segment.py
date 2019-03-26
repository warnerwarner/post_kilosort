'''
Bandpass a snippet of a recording to compare the signal mainly cause I can't figure out the channel map cause dumb
'''

import openephys as oe
from spike_finder import bandpass_data
import os
import psutil
import numpy as np
import sys

available_cpu_count = len(psutil.Process().cpu_affinity())
os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)


chan_num = list(sys.argv)[1]
chan_num = int(chan_num)

home_dir = '/home/camp/warnert/working/Recordings/190325/2019-03-25_16-57-37'

chan = oe.loadContinuous2(os.path.join(home_dir, '100_CH%d.continuous' % chan_num))
data = chan['data']

snippet_size = 1000000

bp_data = bandpass_data(data[:snippet_size])

output_loc = os.path.join(home_dir, 'bandpassed_snippets')
if not os.path.isdir(output_loc):
	os.mkdir(output_loc)

np.save(os.path.join(output_loc, 'bps_CH%d.npy' % chan_num), bp_data)
