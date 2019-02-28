import numpy as np 
import tensortools as tt
import os 
import psutil
import sys
import pickle

available_cpu_count = len(psutil.Process().cpu_affinity())
os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)


rank = int(list(sys.argv)[2])
job_id = int(list(sys.argv)[1])

home_dir = '/home/camp/warnert/working/Recordings/190222/2019-02-22_14-15-45'

tensor = np.load(os.path.join(home_dir, 'good_cluster_tensor.npy'))
print(tensor.shape)

als = tt.cp_als(tensor, rank=rank, verbose=True)
exit_path = os.path.join(home_dir, job_id)
if not os.path.exits(exit_path):
	os.makedirs(exit_path)
pickle.dump(als, open(os.path.join(exit_path, 'tca_output_rank_%d' % rank), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
