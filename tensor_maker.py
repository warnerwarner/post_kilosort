import numpy as np
import pickle
import os
import psutil
import pandas
import openephys as oe

available_cpu_count = len(psutil.Process().cpu_affinity())
os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)

home_dir = '/home/camp/warnert/working/Recordings/190325/2019-03-25_16-57-37'

# Length of the experimental trials
trial_length = 5
fs = 30000 # Sampling rate

# Window for the rolling sum
window = 30000

# Clusterbank to get the good units and times
clusterbank = pickle.Unpickler(open(os.path.join(home_dir, 'clusterbank.pkl'), 'rb')).load()
print('loaded clusterbank')
clusters = clusterbank['good_units']
trial_channel = oe.loadContinuous2(os.path.join(home_dir, '100_CH1.continuous'))

# Make a bin response which are 0 for when theres no spike and 1 for when there is
bin_response = np.zeros([len(clusters), len(trial_channel['data'])])
print('made bin_response')
# Change all the spike times to 1 in bin_response
for index, c in enumerate(clusters):
	cluster = clusters[c]
	times = cluster['times']
	bin_response[index][times] = 1

print('filled bin_response')

rolling_resp = np.zeros(bin_response.shape)

# For each unit make a cumulative sum and take a window at each point to essentially take the sum of the previous window
# way faster than before and doesn't need as much memory
for c in range(len(bin_response)):
	b = bin_response[c].cumsum()
	b[window:] = b[window:] - b[:-window]
	rolling_resp[c] = b

print('changed rolling window into array')
trial_starts = np.fromfile(os.path.join(home_dir, 'trial_starts.npy'), dtype=np.int)
print('loaded trial starts')
# Make the trial_window e.g the length of the trial response 
trial_window_size = 3*trial_length*fs

trial_times = [j for i in trial_starts for j in  range(i-trial_length*fs, i+2*trial_length*fs)]
print('made trial times')
trial_resp_array = rolling_resp[:, trial_times]
print('made trial resp array')


tensor = np.zeros((len(clusters), trial_window_size, len(trial_starts)))
for i in range(len(trial_starts)):
	tensor[:, :, i] = trial_resp_array[:, i*trial_window_size:(i+1)*trial_window_size]
print('assigned to tensor')
pickle.dump(tensor, open(os.path.join(home_dir, 'good_unit_tensor.pkl'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
print('dumped tensor')