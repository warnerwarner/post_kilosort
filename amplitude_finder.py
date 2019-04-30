'''
Finds amplitudes from a single unit/cluster passed to it
'''
from clusterbank_maker import *
from cluster_spike_plotter import *
import os
import sys 
import numpy as np
import pickle
import time  

# Magic code - but doesnt seem to do much this time
available_cpu_count = len(psutil.Process().cpu_affinity())
os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)

# Home dir et al
home_dir = '/home/camp/warnert/working/Recordings/190410/2019-04-10_15-04-49'
output_dir = os.path.join(home_dir, 'cluster_amplitudes')
cluster_num = list(sys.argv)[1]
cluster_num = int(cluster_num)

# Stop if this cluster has already been run
# if os.path.isfile(os.path.join(output_dir, 'cluster_%d.pkl' % cluster_num)):
# 	sys.exit()

# Check if the clusterbank_basic already exits and if not, then make one
clusterbank_loc = os.path.join(home_dir, 'clusterbank_basic.pkl')
if os.path.isfile(clusterbank_loc):
	clusterbank = pickle.Unpickler(open(clusterbank_loc, 'rb')).load()
else:
	clusterbank = make_clusterbank_basic(home_dir, kilosort2=True)

# Load in this cluster
cluster = clusterbank['good_units'][cluster_num]

spike_times = cluster['times']

# Find the amplitudes from the home directory - all the clusters reading from a single 
# dat file is too slow
amps, max_cluster_chan = find_amplitudes(home_dir, 64, spike_times)

# Turn the outputs into a dict and, if the output locations doesn't exist then make it
amp_and_chan = {'amps':amps, 'max_cluster_chan':max_cluster_chan}
if not os.path.isdir(output_dir):
	os.mkdir(output_dir)
pickle.dump(amp_and_chan, open(os.path.join(output_dir, 'cluster_%d.pkl' % cluster_num), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)