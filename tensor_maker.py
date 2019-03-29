import numpy as np
import pickle
import os
import psutil
import pandas

available_cpu_count = len(psutil.Process().cpu_affinity())
os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)

home_dir = '/home/camp/warnert/working/Recordings/190325/2019-03-25_16-57-37'

# Length of the experimental trials
trial_length = 5
fs = 30000 # Sampling rate

# Window for the rolling sum
window = 30000

# Clusterbank to get the good units and times
clusterbank = pickle.Unpickler(open(oe.path.join(home_dir, 'clusterbank.pkl'), 'rb')).load()

clusters = clusterbank['good_units']
trial_channel = oe.loadContinuous2(home_dir, '100_CH1.continuous')


bin_response = np.zeros([len(clusters), len(trial_channel['data'])])

for index, c in enumerate(clusters):
	cluster = clusters[c]
	times = cluster['times']
	bin_response[index][time] = 1

rolling_resp = pandas.DataFrame(bin_response)
rolling_resp = rolling_resp.T 
rolling_resp.colums = [c for c in clusters]

spike_resps = rolling_resp.rolling(window = window).sum()
spike_resp_array = np.array(spike_resps)
trial_starts = np.fromfile(os.path.join(home_dir, 'trial_starts.npy'), dtype=np.int)


trial_window_size = 3*trial_length*fs

trial_times = [j for i in trial_starts for j in  range(i-5*fs, i+2*trial_length*fs)]
trial_resp_array = spike_resp_array.T[:, trial_times]
tensor = np.zeros(len(clusters), trial_window_size, len(trial_starts))

for i in range(len(trial_starts)):
	tensor[:, :, i] = trial_resp_array[:, i*trial_window_size:(i+1)*trial_window_size]

pickle.dump(tensor, open(os.path.join(home_dir, 'good_unit_tensor.pkl'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)