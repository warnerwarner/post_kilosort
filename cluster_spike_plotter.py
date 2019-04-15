'''
Plots all those nice cluster spike plots to compare and the spikes that are isolated using kilosort
'''

import os
import sys
import psutil
import numpy as np
import matplotlib.pyplot as plt
import pickle
import openephys as oe

def spike_plot(data, spike_times, cluster_num, channel_num, output_loc, *, pre_spike_length=30, post_spike_length=60):
	'''
	Plots all spikes from a channel associated with a cluster and then plots the average spike on top

	Arguments:
	data: 
		The raw data, single channel array - should be at 30kHz for correct x axis
	spike_times:
		The times at which the unit's spikes occur
	cluster_num:
		The number of the cluster, for the title of the plot
	channel_num:
		The data channel passed to the function, for the title of the plot
	output_loc:
		The output location for the plot

	Optional arguments:
	pre_spike_length:
		The length of the window (in samples) before the spike to be plotted, default=30 (1ms)
	post_spike_length:
		The length of the window (in samples) after the spike to be plotted default=60 (2ms)
	'''
	cluster_spikes = []
	for i in times:
		spike = data[int(i-pre_spike_length):int(i+post_spike_length)]
		cluster_spikes.append(spike - np.median(spike))
	x = np.arange(0, int((pre_spike_length+post_spike_length)/30), 1/30)
	cluster_spikes = np.array(cluster_spikes)
	plt.plot(cluster_spikes.T, color='gray')
	plt.plot(np.mean(cluster_spikes, axis=0))
	plt.xlabel('Time (ms)')
	plt.ylabel('Voltage ($\mu$V)')
	plt.title('Cluster %d channel %d' % (cluster_num, channel_num))
	plt.savefig(output_loc, dpi=300)

def raster_plot(trial_starts, spike_times, output_loc, *, trial_length=5, fs = 30000):
	'''
	Plots a raster plot for a cluster

	Arguments:
	trial_starts:
		The times at which trials begin
	spike_times:
		The times at which the cluster spikes
	output_loc:
		The location for the plot to be saved

	Optional arguments:
	trial_length: 
		The length of the trails that are being plotted in seconds (default=5)
	fs:
		Sampling frequency of the recording (default=30KHz)
	'''
	trial_spike_times = []
	for i in trial_starts:
		trial_spike_times.append((cluster_spikes[(cluster_spikes > i-trial_length*fs)& (cluster_spikes < i + 2*trial_length*fs)] - float(i))/fs)
	plt.eventplot(trial_spike_times)
	plt.ylabel('Trial')
	plt.xlabel('Time (s)')
	plt.axvline(0, color='r')
	plt.axvline(trial_length, color='r')
	plt.savefig(output_loc, dpi=300)

def together_plot(data, spike_times, trial_starts, cluster_num, channel_num, output_loc, *, pre_spike_length= 30, post_spike_length=60, trial_length=5, fs=30000):
	'''
	Plots a double figure with the avg spike plot and the raster plot

	Arguments:
	data:
		The data from the channel for the spikes to be plotted
	spike_times:
		Times at which the cluster spiked
	trial_starts:
		Times at which the trials started
	cluster_num:
		The number of the cluster (for use in the plot title)
	channel_num:
		The number of the channel (for use in the plot title)
	output_loc:
		Location to save the plot

	Optional arguments:
	pre_spike_length:
		The length of plot to include before the spike event in samples (default=30)
	post_spike_length:
		The length of plot to include after the spike event in samples (default=60)
	trial_length:
		Length of the trials during the recording in seconds (default=5)
	fs:
		Sampling frequency of the recording (default=30kHz)
	'''
	fig, ax = plt.subplots(1, 2)
	cluster_spikes = []
	for i in spike_times:
		spike = data[int(i-pre_spike_length):int(i+post_spike_length)]
		cluster_spikes.append(spike - np.median(spike))
	x = np.arange(0, int((pre_spike_length+post_spike_length)/30), 1/30)
	cluster_spikes = np.array(cluster_spikes)


	trial_spike_times= []
	for i in trial_starts:
		trial_spike_times.append((spike_times[(spike_times > i - trial_length*fs) & (spike_times < i + 2*trial_length*fs)] - float(i))/fs)

	ax[0].plot(x, cluster_spikes.T, color='gray')
	ax[0].plot(np.mean(cluster_spikes, axis=0))
	ax[0].set_xlabel('Time (ms)')
	ax[0].set_ylabel('Voltage ($\mu$V)')
	ax[0].set_title('Cluster %d, channel %d' % (cluster_num, channel_num))

	ax[1].eventplot(trial_spike_times, colors='k')
	ax[1].set_ylabel('Trial number')
	ax[1].set_xlabel('Time (s)')
	ax[1].axvline(0, color='r')
	ax[1].axvline(5, color='r')
	plt.savefig(output_loc, dpi=300)




if __name__ == '__main__':
	#magic code
	available_cpu_count = len(psutil.Process().cpu_affinity())
	os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)

	# Location of data
	home_dir = '/home/camp/warnert/working/Recordings/190410/2019-04-10_15-04-49'

	# Location of phy channel map
	chan_map = np.load(os.path.join(home_dir, 'channel_map.npy'))

	# Clusterbank and good clusters
	clusterbank = pickle.Unpickler(open(os.path.join(home_dir, 'clusterbank.pkl'), 'rb')).load()
	good_clusters = clusterbank['good_units']

	# Taking the chosen unit from the index of the good clusters
	chosen_unit_index = list(sys.argv)[1]
	chosen_unit_index = int(chosen_unit_index)
	cluster_num = good_clusters.values[chosen_unit_index]

	# Open the single cluster info
	cluster= good_clusters[cluster_num]
	spike_times = cluster['times']

	# Load the trial starts
	trial_starts = np.fromfile(os.path.join(home_dir, 'trial_starts.npy'), dtype=np.int)

	full_trials = trial_starts[1:113] # Missed first one and mouse died during final iteration kept the first of the final iteration to keep repeats equal

	# Map the channel number using the channel map
	channel_num = cluster['max_chan']
	channel_num = int(chan_map[channel_num])

	#Load all the data
	data = oe.loadContinuous2(os.path.join(home_dir, '100_CH%d.continuous' % channel_num + 1))['data']

	#Make the output if it doesn't exit
	output_dir = os.path.join(home_dir, 'unit_plots')
	if not os.path.isdir(output_dir):
		os.mkdir(output_dir)

	#Do all the stuff
	together_plot(data, spike_times, full_trials, cluster_num, channel_num+1, os.path.join(output_dir, '%d_cluster.png' % cluster_num))