import openephys as oe
import numpy as np
import os
import sys
from cluster_spike_plotter import *
from clusterbank_maker import *

home_dir = ''

num_of_chans= 64
bit_volts=0.195

clusterbank = make_clusterbank_full(home_dir, num_of_chans)

data_loc = os.path.join(home_dir, '100_CHs.dat')
trial_starts = np.fromfile(os.path.join(home_dir, 'trial_starts.npy'), dtype=np.int)

for cluster_num in clusterbank['good_units']:
	cluster = clusterbank['good_units'][cluster_num]
	data_chan = int(cluster['max_chan'] +1 )
	spike_times = cluster['times']
 	data = oe.loadContinuous2(os.path.join(home_dir, '100_CH%d.continuous' % data_chan))['data']
	x, cluster_spikes = find_cluster_spikes(data, spike_times)

	trial_spike_times = find_trial_spike_times(trial_starts)	
