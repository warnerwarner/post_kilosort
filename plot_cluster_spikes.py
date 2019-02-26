import numpy as np
import openephys as oe
import pickle
import os 
import matplotlib.pyplot as plt
import psutil
import sys



available_cpu_count = len(psutil.Process().cpu_affinity())
os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)

home_dir = '/home/camp/warnert/working/Recordings/190222/2019-02-22_14-15-45'

clusterbank = pickle.Unpickler(open(os.path.join(home_dir, 'clusterbank.pkl'), 'rb')).load()
chan_dict = clusterbank['chan_dict']
clusters = clusterbank['units']

x = np.arange(-1, 2, 1/30)

cluster_num = list(sys.argv)[1]
cluster_num = int(cluster_num)

cluster = clusters[cluster_num]
max_chan = cluster['max_chan']
chan = oe.loadContinuous2(os.path.join(home_dir, '100_CH%d.continuous'% max_chan))
data =  chan['data']
times = cluster['times']
spikes = []
for index, time in enumerate(times):
	spikes.append(data[int(time-30):int(time+60)] - np.median(data[int(time-30):int(time+60)]))
	if index % 5000 == 0:
		print(index)

print(cluster_num, max_chan)

for spike in spikes:
	plt.plot(x, spike, color='gray')
avg_spike = np.mean(spikes, axis=0)
plt.plot(x, avg_spike)
plt.xlabel('Time (ms)')
plt.ylabel('Voltage ($\mu V$)')
plt.title('Cluster avg spike %d, chan: %d' % (cluster_num, max_chan))
plt.savefig(os.path.join(home_dir, 'unit_plots/cluster_%d.png' % cluster_num))
plt.clf()