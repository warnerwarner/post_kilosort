from clusterbank_maker import *
from cluster_spike_plotter import *
import os
import sys 
import numpy as np
import pickle
import time  

# def find_amps_dat():

# def find_amps_continuous():

available_cpu_count = len(psutil.Process().cpu_affinity())
os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)


home_dir = '/home/camp/warnert/working/Recordings/190410/2019-04-10_15-04-49'
output_dir = os.path.join(home_dir, 'cluster_amplitudes')
cluster_num = list(sys.argv)[1]
cluster_num = int(cluster_num)
if os.path.isfile(os.path.join(output_dir, 'cluster_%d.pkl' % cluster_num)):
	sys.exit()
clusterbank_loc = os.path.join(home_dir, 'clusterbank_basic.pkl')
if os.path.isfile(clusterbank_loc):
	clusterbank = pickle.Unpickler(open(clusterbank_loc, 'rb')).load()
else:
	clusterbank = make_clusterbank_basic(home_dir, kilosort2=True)

cluster = clusterbank['good_units'][cluster_num]

spike_times = cluster['times']
#dat_loc = os.path.join(home_dir, '100_CHs.dat')
amps, max_cluster_chan = find_amplitudes(home_dir, 64, spike_times)

amp_and_chan = {'amps':amps, 'max_cluster_chan':max_cluster_chan}

if not os.path.isdir(output_dir):
	os.mkdir(output_dir)
pickle.dump(amp_and_chan, open(os.path.join(output_dir, 'cluster_%d.pkl' % cluster_num), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)