'''
Plots all those nice cluster spike plots to compare and the spikes that are
isolated using kilosort
'''

import os
import psutil
import numpy as np
import matplotlib.pyplot as plt
import pickle
import math
import openephys as oe
from tqdm import tqdm


def bin_spikes(spike_times, experiment_length, *, bin_size=0.05,
               array_of_arrays=True):
    '''
    Counts number of spikes in each bin in a time series

    Arguments:
    spike_times:
    The times of the spikes in relation to stimulus onset
    experiment_length:
    Length of the experiment in seconds

    Optional arguments:
    bin_size:
    Size of the bins in seconds
    array_of_arrays:
    If True will combine all values in array of arrays into one single array
    else will just count the single array.

    Returns:
    count:
    The binned counted spikes
    '''

    # Create the time series to bin the spikes to
    time = np.arange(-experiment_length, 2 * experiment_length+bin_size,
                     bin_size)

    # If the spike times are an array of array combine them together to a
    # single array
    if array_of_arrays:
        all_spike_times = [i for j in spike_times for i in j]
    else:
        all_spike_times = spike_times

    # Count up the spikes
    count = np.bincount(np.digitize(all_spike_times, time, right=1))/bin_size

    # If is array of array divide by the number of repeats that have gone into
    # the count
    if array_of_arrays:
        count = count / len(array_of_arrays)

    # Needed because if no spikes after a bin, bincount will ignore and will
    # have a count of the wrong length
    while len(count) < len(time):
        count = np.append(count, 0)
    return count


def find_cluster_spikes(data, spike_times, *, pre_spike_length=30,
                        post_spike_length=60):
    '''
    Finds all the spikes for a cluster and returns them as a Nxt array where N
    is number of spikes and t is the number of time points

    Arguments:
    data:
    The recorded channel
    spike_times:
    Times at which the cluster is believed to have spiked
    '''
    cluster_spikes = []
    for i in tqdm(spike_times):
        spike = data[int(i-pre_spike_length):int(i+post_spike_length)]
    cluster_spikes.append(spike - np.median(spike))
    x = np.arange(-int(pre_spike_length/30), int(post_spike_length/30), 1/30)
    cluster_spikes = np.array(cluster_spikes)

    return x, cluster_spikes


def find_trial_spike_times(trial_starts, spike_times, *, trial_length=5,
                           fs=30000, pre_trial_length=1, post_trial_length=1):
    '''
    Finds spikes that are present in, or in a window around a trial and returns
    then as an k x t array

    Arguments:
    trial_starts:
    Times the trials start
    spike_times:
    Times that spikes are found

    Optional arguments:
    trial_length:
    Length of the trials
    fs:
    Sampling frequency
    pre_trial_length:
    The length, as a function of the trial_length that is be included pre
    stimuli
    post_trial_length:
    The length, as a function of the trial_length that is to be included post
    stimuli
    '''
    trial_spike_times = []
    for i in tqdm(trial_starts):
        init = i - trial_length*fs*pre_trial_length
    end = i + trial_length*fs + trial_length*fs*post_trial_length

    reset_spike_times = spike_times[(spike_times > init) & (spike_times < end)] - float(i)
    trial_spike_times.append(reset_spike_times/fs)
    return trial_spike_times


def spike_plot(x, cluster_spikes, cluster_num, channel_num, output_loc):
    '''
    Plots all spikes from a channel associated with a cluster and then plots
    the average spike on top

    Arguments:
    x:
    The x axis, should be time
    cluster_spikes:
    The snipped spikes from a cluster
    cluster_num:
    The number of the cluster, for the title of the plot
    channel_num:
    The data channel passed to the function, for the title of the plot
    output_loc:
    The output location for the plot
    '''
    plt.plot(x, cluster_spikes.T, color='gray')
    plt.plot(x, np.mean(cluster_spikes, axis=0))
    plt.xlabel('Time (ms)')
    plt.ylabel('Voltage ($\mu$V)')
    plt.title('Cluster %d channel %d' % (cluster_num, channel_num))
    plt.savefig(output_loc, dpi=300)


def raster_plot(trial_spike_times, output_loc):
    '''
    Plots a raster plot for a cluster

    Arguments:
    trial_spike_times:
    The times at which the cluster spikes during trials, has been rescaled for
    lower sampling rate
    output_loc:
    The location for the plot to be saved
    '''
    plt.eventplot(trial_spike_times)
    plt.ylabel('Trial')
    plt.xlabel('Time (s)')
    plt.axvline(0, color='r')
    plt.axvline(trial_length, color='r')
    plt.savefig(output_loc, dpi=300)


def spike_correlation(times, *, window_size=100, bin_size=1, fs_millisecond=30):
    '''
    Creates a set of bins which contains the number of spikes detected after
    another spike. For use with correlogram

    Arguments:
    times:
    Times of the spikes in samples

    Optional arguments:
    window_size:
    Size of the window around spikes that will be considered in milliseconds
    default = 100

    bin_size:
    Size of the bins for the spikes in milliseconds default = 1

    fs_millisecond:
    The sampling rate in milliseconds default = 30
    '''

    # Find the number of bins in one direction
    num_of_bins = int(window_size/bin_size)
    # Initilise empty bins
    bins = np.zeros(2*num_of_bins)

    for index, time in enumerate(times):
        relative_times = np.array(times - time)

    # Find times in a window around the chosen spike time - ignoring 0
    window_relative_times = relative_times[(-window_size*fs_millisecond<relative_times)
                                            & (relative_times < window_size*fs_millisecond)
                                            & (relative_times != 0)]

    # Translating the relative window times to bin values
    window_relative_times = [math.floor(i/bin_size/fs_millisecond) + num_of_bins for i in window_relative_times]

    # Assigning them to the bins
    for i in window_relative_times:
        bins[i] += 1
    return bins


def correlelogram(bins, output_loc, *, window_size=100, bin_size=1):
    '''
    Plot an auto-correlelogram of all the spike times

    Arguments:
    bin:
    The binned count of the spikes
    output_loc:
    Location to save the figure

    Optional arguments;
    window_size:
    Size of the around the spike that is being counted in milliseconds
    bin_size:
    Size of the bins in milliseconds
    '''
    x = list(np.arange(-window_size, 0, bin_size)) + list(np.arange(bin_size, bin_size+window_size, bin_size))

    plt.bar(x, np.arange(-window_size, window_size, bin_size))
    plt.xlabel('Time (ms)')
    plt.ylabel('Spike counts')
    plt.savefig(output_loc, dpi=300)


def amplitude_plot(amps, times, output_loc, *, fs=30000):
    flip_amps = [-i for i in amps]
    plt.scatter(times/fs, flip_amps, s=0.5, alpha=0.5)
    plt.ylabel('Peak amplitude ($\mu$V)')
    plt.xlabel('Time (s)')
    plt.savefig(output_loc, dpi=300)


def together_plot(spike_x, cluster_spikes, bins, window_size, bin_size,
                  trial_spike_times, trial_length, cluster_num, cluster,
                  recording_length, output_loc, *, fs=30000):
    '''
    Plots a 4 part figure with average spike, trial response, amplitude,
    and autocorrelelogram

    Arguments:
    spike_x:
    Time series for the spike plot
    cluster_spikes:
    Array of arrays of channel recordings from around the spikes detected and
    assigned to this cluster
    bins:
    The binned spikes for the autocorreleogram in milliseconds
    window_size:
    Size of the window of the autocorrelelogram in milliseconds
    bin_size:
    Size of the bins in the autocorrelelogram in milliseconds
    trial_spike_times:
    Times the unit spiked during a trial for use in the raster
    trial_length:
    Length of the trials for use in the raster
    cluster_num:
    The number of the cluster (for use in the plot title)
    cluster:
    The cluster from the clusterbank
    recording_length:
    Length of the recording in samples not seconds
    output_loc:
    Location to save the plot

    Optional arguments:
    fs:
    Sampling frequency, default = 30000
    '''

    # Set up the figure
    fig, ax = plt.subplots(2, 2, figsize=(10, 10))

    # First plot, the average cluster spike
    ax[0, 0].plot(spike_x, cluster_spikes.T, color='lightgray')
    ax[0, 0].plot(spike_x, np.mean(cluster_spikes, axis=0))
    ax[0, 0].set_ylabel('Time (ms)')
    ax[0, 0].set_xlabel('Time (ms)')
    ax[0, 0].set_xlim(-1, 2)

    # Second plot, the correlelogram
    corr_x = list(np.arange(-window_size, 0, bin_size)) + list(np.arange(bin_size, bin_size+window_size, bin_size))
    ax[0, 1].bar(corr_x, bins, width=bin_size)
    ax[0, 1].set_ylabel('Spike count')
    ax[0, 1].set_xlabel('Time (ms)')
    ax[0, 1].set_xlim(-window_size, window_size)

    # Third plot, the raster plot
    ax[1, 0].eventplot(trial_spike_times, color='k')
    ax[1, 0].axvline(0, color='r')
    ax[1, 0].axvline(trial_length, color='r')
    ax[1, 0].set_ylabel('Trial')
    ax[1, 0].set_xlabel('Time (s)')
    ax[1, 0].set_ylim(-0.5, len(trial_spike_times)-0.5)
    ax[1, 0].set_xlim(-trial_length, 2*trial_length)

    #Fourth plot, the amplitudes
    flip_amps = [-i for i in cluster['amps']] # Flip the amplitudes to be positive
    ax[1, 1].scatter(cluster['times']/fs, flip_amps, s=0.5, alpha=0.5)
    ax[1, 1].set_ylabel('Amplitude ($\mu$V)')
    ax[1, 1].set_xlabel('Time (s)')
    ax[1, 1].set_xlim(0, recording_length/fs)
    ax[1, 1].set_ylim(0)

    # Extra subplot to hold the title etc
    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)
    plt.title('Cluster %d' % cluster_num)
    plt.tight_layout()
    plt.savefig(output_loc, dpi=300)


def jULIE_16_chan_plotter(data, cluster_times, cluster_num):
    '''
    Plots a 16 channel jULIE plot of average waveforms

    Arguments:
    data:
    Array of all data in format of chan_num x time_points
    cluster_times:
    The times the cluster spiked
    cluster_num:
    The number of the cluster
    '''

    all_spikes = [data[:, int(i-30):int(i+60)] for i in cluster_times]
    all_spikes = np.array(all_spikes)
    mean_spikes = np.mean(all_spikes, axis=0)

    fig, ax = plt.subplots(2, 8, sharey=True)
    spike_time = np.arange(-1, 2, 1/30)
    min_spike = math.inf
    max_spike = 0
    big_chan = 17
    smol_chan = 17

    plot_spikes = []
    for i in range(16):
        spike = (mean_spikes[i] - np.median(mean_spikes[i]))*0.195
        ax[int(i/8), i % 8].plot(spike_time, spike, color='k')
        ax[int(i/8), i % 8].axis('off')
        var = max(spike) - min(spike)
        if var < min_spike:
            min_spike = var
            smol_chan = i
        if var > max_spike:
            max_spike = var
            big_chan = i
        plot_spikes.append(spike)
    ax[int(smol_chan/8), smol_chan%8].plot([-1, -1], [min(plot_spikes[big_chan]), min(plot_spikes[big_chan])+100], color='k')
    ax[int(smol_chan/8), smol_chan%8].plot([-1, 0], [min(plot_spikes[big_chan]), min(plot_spikes[big_chan])], color='k')
    ax[int(smol_chan/8), smol_chan%8].text(-4.5, min(plot_spikes[big_chan])+40, '100 $\mu$V')
    ax[int(smol_chan/8), smol_chan%8].text(-1, min(plot_spikes[big_chan])-30, '1 ms')
    fig.suptitle('Cluster %d' % cluster_num)
    plt.show()

def cluster_comparision(clusters, all_cluster_spikes):
    '''
    Compares all the clusters in a recording
    '''
    cluster_comparision = {}
    spike_number = []

    for cluster_num in clusters:
        cluster = clusters[cluster_num]
        number_of_spikes = len(cluster['times'])
        cluster_spikes = all_cluster_spikes[cluster_num]
    #amps = [np.]


if __name__ == '__main__':
    #magic code
    available_cpu_count = len(psutil.Process().cpu_affinity())
    os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)

    # Location of data
    home_dir = '/home/camp/warnert/working/Recordings/190410/2019-04-10_15-04-49'

    # Location of phy channel map
    chan_map = np.load(os.path.join(home_dir, 'channel_map.npy'))

    # Clusterbank and good clusters
    clusterbank = pickle.Unpickler(open(os.path.join(home_dir, 'clusterbank.pkl'), 'rb')).load()
    good_clusters = clusterbank['good_units']

    print(home_dir)

    for cluster_num in good_clusters:

        # Open the single cluster info
        cluster= good_clusters[cluster_num]
        spike_times = cluster['times']

    # Load the trial starts
        trial_starts = np.fromfile(os.path.join(home_dir, 'trial_starts.npy'), dtype=np.int)

        full_trials = trial_starts[1:113] # Missed first one and mouse died during final iteration kept the first of the final iteration to keep repeats equal

        # Map the channel number using the channel map
        channel_num = cluster['max_chan']
        channel_num = int(chan_map[channel_num])

        # Load all the data
        data = oe.loadContinuous2(os.path.join(home_dir, '100_CH%d.continuous' % (channel_num + 1)))['data']

    # Make the output if it doesn't exit
        output_dir = os.path.join(home_dir, 'unit_plots')
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        # Do all the stuff
        cluster_spikes = together_plot(data, spike_times, full_trials, cluster_num, channel_num+1, os.path.join(output_dir, '%d_cluster.png' % cluster_num))
        print('Done', cluster_num)
