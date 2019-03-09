import openephys as oe
import numpy as np
import os
import sys

cluster = list(sys.argv)[1]

home_dir = ''

clusterbank  = os.path.join(home_dir, clusterbank)

good_units = clusterbank['good_units']

spikes= []

unit = good_units[cluster]

max_chan = i['max_chan']
times = i['times']
chan = oe.loadContinuous2(os.path.join(home_dir, '100_CH%d.continuous' % max_chan))
data = chan['data']
spike_times = [time for spike_time in spike_times for time in range(spike_time-30, spike_time+30)]

spikes = [[data[time] for time in range(spike_time-30, spike_time+30)] for spike_time in spike_times]

x = np.arange(-1, 1, 1/30)

avg_spike = np.mean(spikes, axis=0)
for i in spikes:
	plt.plot(x, i, color='gray')
plt.plot(x, avg_spike)
plt.ylabel('Voltage ($\mu V$)')
plt.xlabel('Time (ms)')