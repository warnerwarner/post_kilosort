import numpy as np
import os
import pickle
import csv


home_dir = "/home/camp/warnert/working/Recordings/190325/2019-03-25_16-57-37"

cluster_tsv = os.path.join(home_dir, 'cluster_group.tsv')

tsv_read = csv.reader(open(cluster_tsv, 'r'), delimiter='\t')

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

print(good_clusters)

all_clusters= np.concatenate((good_clusters, mua_clusters, noise_clusters))
header = {'home_dir':home_dir, 'date':190325, 'good_clusters':good_clusters, 'mua_clusters':mua_clusters, 'noise_clusters':noise_clusters}

times = np.load(os.path.join(home_dir, 'spike_times.npy'))
clusters = np.load(os.path.join(home_dir, 'spike_clusters.npy'))
spike_templates = np.load(os.path.join(home_dir, 'spike_templates.npy'))
templates = np.load(os.path.join(home_dir, 'templates.npy'))
templates_ind = np.load(os.path.join(home_dir, 'templates_ind.npy'))
chan_positions = np.load(os.path.join(home_dir, 'channel_positions.npy'))
chan_map = np.load(os.path.join(home_dir, 'channel_map.npy'))

chan_dict = dict(zip(chan_map.T[0]+1, chan_positions))


good_units = {}
noise_units = {}
mua_units = {}

print(all_clusters)

for cluster in all_clusters:
	c_times = times[(clusters==cluster)]
	c_template_ids = spike_templates[(clusters==cluster)]
	c_templates = templates[np.unique(c_template_ids)]
	max_chan = 0
	template_maxes = {}
	for clus_temp in c_templates:
		chan_sums = [abs(sum(j)) for j in clus_temp.T]
		print(len(chan_sums))
		template_maxes[max(chan_sums)] = np.argmax(chan_sums)
	chan_max = template_maxes[max(template_maxes.keys())]
	if cluster in good_clusters:
		print('here')
		good_units[cluster] = {'max_chan':chan_max, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}
	elif cluster in mua_clusters:
		mua_units[cluster] = {'max_chan':chan_max, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}
	elif cluster in noise_clusters:
		noise_units[cluster] = {'max_chan':chan_max, 'unique_temps_ids':np.unique(c_template_ids), 'times':c_times, 'template_ids':c_template_ids, 'templates':c_templates}



cluster_dict = {'header':header, 'good_units':good_units, 'mua_units':mua_units, 'noise_units':noise_units, 'chan_dict':chan_dict}

pickle.dump(cluster_dict, open(os.path.join(home_dir, 'clusterbank.pkl'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)