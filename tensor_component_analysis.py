import numpy as np 
import tensortools as tt
import os 
import psutil
import sys
import pickle

available_cpu_count = len(psutil.Process().cpu_affinity())
os.environ["MKL_NUM_THREADS"] = str(available_cpu_count)

max_rank = int(list(sys.argv[3]))
rank = int(list(sys.argv)[2])
job_id = int(list(sys.argv)[1])

home_dir = '/home/camp/warnert/working/Recordings/190211/2019-02-11_16-35-46'

tensor = np.load(os.path.join(home_dir, 'good_cluster_tensor.npy'))
print(tensor.shape)

exit_folder_name = str(job_id) + '_'+str(max_rank)

als = tt.cp_als(tensor, rank=rank, verbose=True)
exit_path = os.path.join(home_dir, exit_folder_name)
if not os.path.exists(exit_path):
	os.makedirs(exit_path)
pickle.dump(als, open(os.path.join(exit_path, 'tca_output_rank_%d' % rank), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)
