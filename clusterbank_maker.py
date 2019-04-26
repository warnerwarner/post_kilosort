import numpy as np
import os
import pickle
import csv
import psutil

def make_clusterbank(home_dir, *, dump=True, kilosort2=False):
	'''
	Makes clusterbanks with info about the clusters isolated from kilosort

	Arguments:
	home_dir:
		The directory that the kilosort outputs are stored

	Optional arguments:
	dump:
		Dump the clusterbank in a location
	kilosort2:
		If kilosort 2 has been run on the data
	'''
	date = home_dir.split('/')[6]

	# Read in the cluster classifications
	cluster_tsv = os.path.join(home_dir, 'cluster_group.tsv')
	tsv_read = csv.reader(open(cluster_tsv, 'r'), delimiter='\t')


	if kilosort2:
		KSlabels_tsv = list(csv.reader(open(os.path.join(home_dir, 'cluster_KSLabel.tsv'), 'r'), delimiter='\t'))
		cluster_contam_tsv = list(csv.reader(open(os.path.join(home_dir, 'cluster_ContamPct.tsv'), 'r'), delimiter='\t'))
		cluster_amp_tsv = list(csv.reader(open(os.path.join(home_dir, 'cluster_Amplitude.tsv'), 'r'), delimiter='\t'))
		
		KSlabels = {}
		cluster_contam = {}
		cluster_amp = {}
		for i, j, k in zip(KSlabels_tsv, cluster_contam_tsv, cluster_amp_tsv):
			KSlabels[int(i[0])] = float(i[1])
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
	cluster_contam = csv.read(open(os.path.join(home_dir, 'cluster_ContamPct.tsv')), delimiter='\t')
	cluster_amp = csv.read(open(os.path.join(home_dir, 'cluster_Amplitude.tsv')), delimiter='\t')



	# Dictionary to hold the actual information for the clusters
	good_units = {}
	noise_units = {}
	mua_units = {}

	# Run through all the clusters
	for cluster in all_clusters:
		c_times = times[(clusters==cluster)]
		c_template_ids = spike_templates[(clusters==cluster)]
		c_templates = templates[np.unique(c_template_ids)]
		max_chan = 0
		template_maxes = {}
		for clus_temp in c_templates:
			# Used only if a cluster comes from a merge
			chan_sums = [abs(sum(j)) for j in clus_temp.T]
			template_maxes[max(chan_sums)] = np.argmax(chan_sums)
		chan_max = template_maxes[max(template_maxes.keys())]
		file_max = int(chan_map[chan_max]) + 1

		if kilosort2:
			amp = cluster_amp[cluster]
			contamination = cluster_contam[cluster]
			ks_label = KSlabels[cluster]
		else:
			amp = None
			contamination = None
			ks_label = None

		if cluster in good_clusters:
			good_units[cluster] = {'contamination':contam,'amplitude':amp,'max_chan':chan_max, 'file_max':file_max, 'KSlabel':ks_label, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}
		elif cluster in mua_clusters:
			mua_units[cluster] = {'contamination':contam,'amplitude':amp,'max_chan':chan_max, 'file_max':file_max,  'KSlabel':ks_label, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}
		elif cluster in noise_clusters:
			noise_units[cluster] = {'contamination':contam,'amplitude':amp,'max_chan':chan_max,'file_max':file_max,  'KSlabel':ks_label, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}


	# Turn all the unit dicts into one big dict
	cluster_dict = {'header':header, 'good_units':good_units, 'mua_units':mua_units, 'noise_units':noise_units, 'chan_dict':chan_dict}
	if dump:
		pickle.dump(cluster_dict, open(os.path.join(home_dir, 'clusterbank.pkl'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
	
	return cluster_dict

if __name__ == '__main__':

	available_cpu_count = len(psutil.Process().cpu_affinity())
	os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)


	home_dir = "/home/camp/warnert/working/Recordings/190211/2019-02-11_16-35-46"


	# And ump it all
	pickle.dump(cluster_dict, open(os.path.join(home_dir, 'clusterbank.pkl'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)