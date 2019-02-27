import numpy as np 
import tensortools as tt
import os 
import psutil
import sys
import pickle

rank = int(list(sys.argv)[1])

home_dir = '/home/camp/warnert/working/Recordings/190222/2019-02-22_14-15-45'

tensor = np.fromfile(os.path.join(home_dir, 'good_cluster_tensor.npy'))

als = tt.cp_als(tensor, rank=rank, verbose=True)

pickle.dump(als, open(os.path.join(home_dir, 'tca_output_rank_%d' % rank), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
