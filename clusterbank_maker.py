import numpy as np
import os
import pickle


home_dir = "/home/tom/d/Open_ephys_testing_ground_data/190222/2019-02-22_14-15-45"

good_clusters = [2, 5, 13, 14, 20, 37, 47, 51, 65, 66]

header = {'home_dir':home_dir, 'date':190222, 'good_clusters':good_clusters}

times = np.load(os.path.join(home_dir, 'spike_times.npy'))
clusters = np.load(os.path.join(home_dir, 'spike_clusters.npy'))
spike_templates = np.load(os.path.join(home_dir, 'spike_templates.npy'))
templates = np.load(os.path.join(home_dir, 'templates.npy'))
templates_ind = np.load(os.path.join(home_dir, 'templates_ind.npy'))
chan_positions = np.load(os.path.join(home_dir, 'channel_positions.npy'))
chan_map = np.load(os.path.join(home_dir, 'channel_map.npy'))

chan_dict = dict(zip(chan_map.T[0]+1, chan_positions))


units = {}

for cluster in good_clusters:
	c_times = times[(clusters==cluster)]
	c_template_ids = spike_templates[(clusters==cluster)]
	c_templates = templates[np.unique(c_template_ids)]
	max_chan = 0
	template_maxes = {}
	for clus_temp in c_templates:
		chan_sums = [abs(sum(j)) for j in clus_temp.T]
		print(len(chan_sums))
		template_maxes[max(chan_sums)] = np.argmax(chan_sums)+1 
	chan_max = template_maxes[max(template_maxes.keys())]
	units[cluster] = {'max_chan':chan_max, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}

cluster_dict = {'header':header, 'units':units, 'chan_dict':chan_dict}

pickle.dump(cluster_dict, open(os.path.join(home_dir, 'clusterbank.pkl'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)