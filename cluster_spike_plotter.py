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

def find_cluster_spikes(data, spike_times, *, pre_spike_length = 30, post_spike_length = 60):
	'''
	Finds all the spikes for a cluster and returns them as a Nxt array where N is number of spikes and t is the number of time points

	Arguments:
	data:
		The recorded channel
	spike_times:
		Times at which the cluster is believed to have spiked
	'''
	cluster_spikes = []
	for i in spike_times:
		spike = data[int(i-pre_spike_length):int(i+post_spike_length)]
		cluster_spikes.append(spike - np.median(spike))
	x = np.arange(0, int((pre_spike_length+post_spike_length)/30), 1/30)
	cluster_spikes = np.array(cluster_spikes)

	return x, cluster_spikes

def find_trial_spike_times(trial_starts, spike_times, *, trial_length=5, fs=30000, pre_trial_length=1, post_trial_length=1):
	'''
	Finds spikes that are present in, or in a window around a trial and returns then as an k x t array

	Arguments:
	trial_starts:
		Times the trials start
	spike_times:
		Times that spikes are found

	Optional arguments:
	trial_length:
		Length of the trials
	fs:
		Sampling frequency
	pre_trial_length:
		The length, as a function of the trial_length that is be included pre stimuli
	post_trial_length:
		The length, as a function of the trial_length that is to be included post stimuli
	'''
	trial_spike_times = []
	for i in trial_starts:
		init = i - trial_length*fs*pre_trial_length
		end = i + trial_length*fs + trial_length*fs*post_trial_length
		reset_spike_times = spike_times[(spike_times > init)& (spike_times < end)] - float(i)
		trial_spike_times.append(reset_spike_times/fs)
	return trial_spike_times


def spike_plot(x, cluster_spikes, cluster_num, channel_num, output_loc):
	'''
	Plots all spikes from a channel associated with a cluster and then plots the average spike on top

	Arguments:
	x:
		The x axis, should be time
	cluster_spikes:
		The snipped spikes from a cluster
	cluster_num:
		The number of the cluster, for the title of the plot
	channel_num:
		The data channel passed to the function, for the title of the plot
	output_loc:
		The output location for the plot
	'''
	plt.plot(x, cluster_spikes.T, color='gray')
	plt.plot(x, np.mean(cluster_spikes, axis=0))
	plt.xlabel('Time (ms)')
	plt.ylabel('Voltage ($\mu$V)')
	plt.title('Cluster %d channel %d' % (cluster_num, channel_num))
	plt.savefig(output_loc, dpi=300)

def raster_plot(trial_spike_times, output_loc):
	'''
	Plots a raster plot for a cluster

	Arguments:
	trial_spike_times:
		The times at which the cluster spikes during trials, has been rescaled for lower sampling rate
	output_loc:
		The location for the plot to be saved
	'''
	plt.eventplot(trial_spike_times)
	plt.ylabel('Trial')
	plt.xlabel('Time (s)')
	plt.axvline(0, color='r')
	plt.axvline(trial_length, color='r')
	plt.savefig(output_loc, dpi=300)

def together_plot(x, cluster_spikes, trial_spike_times, cluster_num, channel_num, output_loc, *, plot_limits=True):
	'''
	Plots a double figure with the avg spike plot and the raster plot

	Arguments:
	x:
		Time series for the spike plot
	cluster_spikes:
		Array of arrays of channel recordings from around the spikes detected and assigned to this cluster
	trial_spike_times:
		Times the unit spiked during a trial
	cluster_num:
		The number of the cluster (for use in the plot title)
	channel_num:
		The number of the channel (for use in the plot title)
	output_loc:
		Location to save the plot

	Optional arguments:
	plot_limits:
		Set the y limits of the plots, on True weights it on the maximum negative value of the spike
	'''
	fig, ax = plt.subplots(1, 2, figsize=(10, 4))

	avg_spike = np.mean(cluster_spikes, axis=0)
	ax[0].plot(x, cluster_spikes.T, color='gray')
	ax[0].plot(x,avg_spike)
	ax[0].set_xlabel('Time (ms)')
	ax[0].set_ylabel('Voltage ($\mu$V)')
	if plot_limits:
		ax[0].set_ylim([min(avg_spike)*1.1, -min(avg_spike)*0.3])

	ax[1].eventplot(trial_spike_times, colors='k')
	ax[1].set_ylabel('Trial number')
	ax[1].set_xlabel('Time (s)')
	ax[1].axvline(0, color='r')
	ax[1].axvline(5, color='r')
	plt.title('Cluster %d, channel %d' % (cluster_num, channel_num))
	plt.savefig(output_loc, dpi=300)

def cluster_comparision(clusters, all_cluster_spikes):
	'''
	Compares all the clusters in a recording
	'''
	cluster_comparision = {}
	spike_number = []

	for cluster_num in clusters:
		cluster = clusters[cluster_num]	
		number_of_spikes = len(cluster['times'])
		cluster_spikes = all_cluster_spikes[cluster_num]
		#amps = [np.]


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

	print(home_dir)

	for cluster_num in good_clusters:

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
		data = oe.loadContinuous2(os.path.join(home_dir, '100_CH%d.continuous' % (channel_num + 1)))['data']

		#Make the output if it doesn't exit
		output_dir = os.path.join(home_dir, 'unit_plots')
		if not os.path.isdir(output_dir):
			os.mkdir(output_dir)

		#Do all the stuff
		cluster_spikes = together_plot(data, spike_times, full_trials, cluster_num, channel_num+1, os.path.join(output_dir, '%d_cluster.png' % cluster_num))
		print('Done', cluster_num)