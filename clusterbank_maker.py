'''
Functions and whatnot related to creating a clusterbank dictionary for a data set
'''
import numpy as np
import os
import pickle
import csv
from tqdm import tqdm
import psutil
from cluster_spike_plotter import *

def make_clusterbank_basic(home_dir, *, dump=True, kilosort2=True):
	'''
	Makes clusterbanks with info about the clusters isolated from kilosort

	Arguments:
	home_dir:
		The directory that the kilosort outputs are stored

	Optional arguments:
	dump:
		Dump the clusterbank in a location
	kilosort2:
		If kilosort 2 has been run on the data default = Ture
	'''

	# Find the date of the recording (won't work if it doesn't follow this format)
	date = home_dir.split('/')[6]

	# Read in the cluster classifications
	cluster_tsv = os.path.join(home_dir, 'cluster_group.tsv')
	tsv_read = csv.reader(open(cluster_tsv, 'r'), delimiter='\t')

	# Read in the additional kilosort2 labels, which are if the units are 'good', their contamination, and their amplitude (though the amplitude one seems a little off...)
	if kilosort2:
		KSlabels_tsv = list(csv.reader(open(os.path.join(home_dir, 'cluster_KSLabel.tsv'), 'r'), delimiter='\t'))
		cluster_contam_tsv = list(csv.reader(open(os.path.join(home_dir, 'cluster_ContamPct.tsv'), 'r'), delimiter='\t'))
		cluster_amp_tsv = list(csv.reader(open(os.path.join(home_dir, 'cluster_Amplitude.tsv'), 'r'), delimiter='\t'))
		
		KSlabels = {}
		cluster_contam = {}
		cluster_amp = {}
		for i, j, k in zip(KSlabels_tsv[1:], cluster_contam_tsv[1:], cluster_amp_tsv[1:]):
			KSlabels[int(i[0])] = i[1]
			cluster_contam[int(j[0])] = float(j[1])
			cluster_amp[int(k[0])] = float(k[1])


	# Hold the good, bad and ugly clusters
	good_clusters = []
	mua_clusters = []
	noise_clusters = []
	for i in tsv_read:
		if i[1] == 'good':
			good_clusters.append(int(i[0]))
		elif i[1] == 'mua':
			mua_clusters.append(int(i[0]))
		elif i[1] == 'noise':
			noise_clusters.append(int(i[0]))


	# Concatenate all the clusters together for the loop
	all_clusters= np.concatenate((good_clusters, mua_clusters, noise_clusters))

	# Make a nice little header	
	header = {'home_dir':home_dir, 'date':date, 'kilosort2':kilosort2, 'good_clusters':good_clusters, 'mua_clusters':mua_clusters, 'noise_clusters':noise_clusters}

	# Load in all the post kilosort stuff
	times = np.load(os.path.join(home_dir, 'spike_times.npy'))
	clusters = np.load(os.path.join(home_dir, 'spike_clusters.npy'))
	spike_templates = np.load(os.path.join(home_dir, 'spike_templates.npy'))
	templates = np.load(os.path.join(home_dir, 'templates.npy'))
	templates_ind = np.load(os.path.join(home_dir, 'templates_ind.npy'))
	chan_positions = np.load(os.path.join(home_dir, 'channel_positions.npy'))
	chan_map = np.load(os.path.join(home_dir, 'channel_map.npy'))
	chan_dict = dict(zip(chan_map.T[0]+1, chan_positions))




	# Dictionary to hold the actual information for the clusters
	good_units = {}
	noise_units = {}
	mua_units = {}

	# Run through all the clusters
	for cluster in all_clusters:

		c_times = times[(clusters==cluster)]
		c_template_ids = spike_templates[(clusters==cluster)]
		c_templates = templates[np.unique(c_template_ids)]

		if kilosort2:
			amp = cluster_amp[cluster]
			contam = cluster_contam[cluster]
			ks_label = KSlabels[cluster]
		else:
			amp = None
			contam = None
			ks_label = None

		if cluster in good_clusters:
			good_units[cluster] = {'KScontamination':contam,'KSamplitude':amp, 'KSlabel':ks_label, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}
		elif cluster in mua_clusters:
			mua_units[cluster] = {'KScontamination':contam,'KSamplitude':amp,   'KSlabel':ks_label, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}
		elif cluster in noise_clusters:
			noise_units[cluster] = {'KScontamination':contam,'KSamplitude':amp,'file_max':file_max,  'KSlabel':ks_label, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}


	# Turn all the unit dicts into one big dict
	cluster_dict = {'header':header, 'good_units':good_units, 'mua_units':mua_units, 'noise_units':noise_units, 'chan_dict':chan_dict}
	if dump:
		pickle.dump(cluster_dict, open(os.path.join(home_dir, 'clusterbank_basic.pkl'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
	
	return cluster_dict

def find_amplitudes(data_loc, num_of_chans,  spike_times, *, dat=False, bitvolts=0.195, order='F'):
	'''
	Finds the amplitudes of a unit's spikes and returns them as an array of length num_of_spikes

	Arguments:
	data_loc:
		Location of the data folder/file
	num_of_chans:
		How many channels are present in the recording
	spike_times:
		The times that the unit spiked

	Optional arguments:
	dat:
		Should the dat file be used - useful for a single instance to save memory but is v slow when used in parallel
	bitvolts:
		The value to change from bits to microvolts
	order:
		Order of the dat file (if it is used)
	'''

	# If dat load in the file and reshape else, load in all the continuous files
	if dat:
		dat_file = np.memmap(data_loc, dtype=np.int16)
		time_length = int(len(dat_file)/num_of_chans)
		datas = dat_file.reshape((num_of_chans, time_length), order=order)
	else:
		datas = [oe.loadContinuous2(os.path.join(data_loc, '100_CH%d.continuous' % i))['data'] for i in range(1, num_of_chans+1)]
	
	# Array to hold the spikes for the cluster across all channels
	cluster_spikes = []
	for i in tqdm(range(num_of_chans)):
		# Find the spikes for that channel in the data structure
		cluster_spikes.append(find_cluster_spikes(datas[i], spike_times)[1])

	# Find the maximum channel of the average spike
	max_cluster_chan = find_max_chan(cluster_spikes)

	# If using the dat file, scale by the bitvolts
	if dat:
		amps = [min(i)*bitvolts for i in cluster_spikes[max_cluster_chan]]
	else:
		amps = [min(i) for i in cluster_spikes[max_cluster_chan]]
	return amps, max_cluster_chan

def find_max_chan(cluster_spikes):
	'''
	Finds the average maximal spike across all channels and returns the channel number (in python notation so 0 index) and the average spike of that channel

	Arguments:
	cluster_spikes:
		Array of chans x num_of_spikes x spike_window containing all the spikes, across all channels over a window
	'''
	mean_cluster_spikes = [np.mean(i, axis=0) for i in cluster_spikes]
	max_cluster_chan = np.argmin([min(i) for i in mean_cluster_spikes])
	return max_cluster_chan

def make_clusterbank_full(home_dir, num_of_chans, *, unit_types='good_units', kilosort2=True, dump=True, dat=False,bitvolts=0.195, order='F', dat_name='100_CHs.dat'):
	'''
	Makes a clusterbank with all the information of all the units
	
	Arguments:
	home_dir:
		The directory which contains all the data and the kilosort information
	num_of_chans:
		number of channels in a recording

	Optional arguments:
	kilosort2:
		If kilosort2 has been run on the data, if not will assume kilosort1
	dump:
		If the clusterbank should be dumped as a pickle afterwards
	dat:
		Should the dat file and memmap be used for the data location
	bitvolts:
		The ratio between raw bits extracted from a dat file, and bitvolts
	order:
		Order of the dat file, default F
	dat_name:
		Name of the dat file
	'''

	# Set the location of the data file(s)
	if dat:
		data_loc = os.path.join(home_dir, dat_name)

	else:
		data_loc = home_dir



	# Make a basic_clusterbank
	clusterbank_basic = make_clusterbank_basic(home_dir, dump=False, kilosort2=kilosort2)
	print('Done making basic clusterbank')


	if unit_types == 'all':
		unit_types = ['good_units', 'mua_units', 'noise_units']
	elif isinstance(unit_types, str):
		unit_types = [unit_types]

	# Runs through the units types in the basic clusterbank and only selects the good, bad and mua
	for unit_type in unit_types:
		# Run through all the units in that type
		for cluster_num in clusterbank_basic[unit_type]:
			print('Doing cluster', cluster_num)
			cluster = clusterbank_basic[unit_type][cluster_num]
			spike_times = cluster['times']
			print('Finding amps for', len(spike_times), 'spikes')
			amps, max_cluster_chan = find_amplitudes(data_loc, num_of_chans, spike_times, dat = dat, bitvolts=bitvolts, order=order)
			cluster['amps'] = amps
			cluster['max_chan'] = max_cluster_chan
	if dump:
		pickle.dump(clusterbank_basic, open(os.path.join(home_dir, 'clusterbank_full.pkl'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
	return clusterbank_basic

def make_clusterbank_load_amps(home_dir, num_of_chans, *, unit_types='good_units', amp_loc = 'cluster_amplitudes', kilosort2=True, dump=True):
	'''
	Make a full clusterbank by loading the amplitudes already saved from the find amplitudes 

	Arguments:
	home_dir:
		The home directory with all the data in
	num_of_chans:
		Number of channels present in the recording

	Optional arguments:
	unit_types:
		The types of units to be transformed to the clusterbank, default='good'
	amp_loc:
		The location of the amplitudes already calculated - assumed that all the cluster's amplitudes have been calculated in serpate files
	kilosort2:
		If kilosort2 has been used
	dump:
		Dump the clusterbank as a pickled object
	'''

	# Make the basic clusterbank
	clusterbank_basic = make_clusterbank_basic(home_dir, dump=False, kilosort2=kilosort2)

	# If it all then translate to all three unit types or if it is a single type then cast to a list so it doesn't break everything
	if unit_types == 'all':
		unit_types = ['good_units', 'mua_units', 'noise_units']
	elif isinstance(unit_types, str):
		unit_types = [unit_types]

	# Run the unit types
	for unit_type in unit_types:
		print('Doing', unit_type, 'now')
		for cluster_num in clusterbank_basic[unit_type]:
			print('Doing cluster', cluster_num)
			cluster = clusterbank_basic[unit_type][cluster_num]
			spike_times = cluster['times']

			# Load in the amplitude for this cluster
			amps_dict_loc = os.path.join(home_dir, amp_loc, 'cluster_%d.pkl' % int(cluster_num))
			amps_dict = pickle.Unpickler(open(amps_dict_loc, 'rb')).load()
			cluster['amps'] = amps_dict['amps']
			cluster['max_chan'] = amps_dict['max_cluster_chan']
	if dump:
		pickle.dump(clusterbank_basic, open(os.path.join(home_dir, 'clusterbank_full.pkl'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
	return clusterbank_basic



if __name__ == '__main__':

	available_cpu_count = len(psutil.Process().cpu_affinity())
	os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)


	home_dir = "/home/camp/warnert/working/Recordings/190211/2019-02-11_16-35-46"


	# And ump it all
	pickle.dump(cluster_dict, open(os.path.join(home_dir, 'clusterbank.pkl'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)