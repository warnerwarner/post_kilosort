import openephys as oe
import numpy as np
import os
import sys
from cluster_spike_plotter import *
from clusterbank_maker import *
import psutil

# Magic code - but doesnt seem to do much this time
available_cpu_count = len(psutil.Process().cpu_affinity())
os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)


home_dir = '/home/camp/warnert/working/Recordings/190222/2019-02-22_14-15-45'

num_of_chans= 32
bit_volts=0.195

clusterbank = pickle.Unpickler(open(os.path.join(home_dir, 'clusterbank_full.pkl'), 'rb')).load()


trial_starts = np.fromfile(os.path.join(home_dir, 'trial_starts.npy'), dtype=np.int)
window_size = 100
bin_size = 1
trial_length = 5
#data = oe.loadContinuous2(os.path.join(home_dir, '100_CH1.continuous'))['data']

for cluster_num in clusterbank['good_units']:
	cluster = clusterbank['good_units'][cluster_num]
	data_chan = int(cluster['max_chan'] +1 )
	spike_times = cluster['times']
	data = oe.loadContinuous2(os.path.join(home_dir, '100_CH%d.continuous' % data_chan))['data']
	spike_x, cluster_spikes = find_cluster_spikes(data, spike_times)

	cluster_times = [int(i[0]) for i in cluster['times']]
	cluster_times = np.array(cluster_times)

	bins = spike_correlation(cluster_times)
	trial_spike_times = find_trial_spike_times(trial_starts, cluster['times'])
	recording_len = len(data)
	output_dir = os.path.join(home_dir, 'cluster_plots')
	if not os.path.isdir(output_dir):
		os.mkdir(output_dir)
	output_loc = os.path.join(output_dir, 'cluster_%d.png' % cluster_num)
	
	together_plot(spike_x, cluster_spikes, bins, window_size, bin_size, trial_spike_times, trial_length, cluster_num, cluster, recording_len, output_loc)
	plt.clf()