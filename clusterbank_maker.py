import numpy as np
import os
import pickle
import csv
import psutil


available_cpu_count = len(psutil.Process().cpu_affinity())
os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)


home_dir = "/home/camp/warnert/working/Recordings/190410/2019-04-10_15-04-49"
date = home_dir.split('/')[6]

# Read in the cluster classifications
cluster_tsv = os.path.join(home_dir, 'cluster_group.tsv')
tsv_read = csv.reader(open(cluster_tsv, 'r'), delimiter='\t')

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
header = {'home_dir':home_dir, 'date':date, 'good_clusters':good_clusters, 'mua_clusters':mua_clusters, 'noise_clusters':noise_clusters}

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
	max_chan = 0
	template_maxes = {}
	for clus_temp in c_templates:
		# Used only if a cluster comes from a merge
		chan_sums = [abs(sum(j)) for j in clus_temp.T]
		template_maxes[max(chan_sums)] = np.argmax(chan_sums)
	chan_max = template_maxes[max(template_maxes.keys())]
	if cluster in good_clusters:
		good_units[cluster] = {'max_chan':chan_max, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}
	elif cluster in mua_clusters:
		mua_units[cluster] = {'max_chan':chan_max, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}
	elif cluster in noise_clusters:
		noise_units[cluster] = {'max_chan':chan_max, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}


# Turn all the unit dicts into one big dict
cluster_dict = {'header':header, 'good_units':good_units, 'mua_units':mua_units, 'noise_units':noise_units, 'chan_dict':chan_dict}

# And ump it all
pickle.dump(cluster_dict, open(os.path.join(home_dir, 'clusterbank.pkl'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)