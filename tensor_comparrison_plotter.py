import tensortools
import numpy as np
import pickle

tensors = []

max_rank = 50

for j in range(1, max_rank+1):
	rep_tensors = []
	for i in os.listdir(home_dir):
		if os.path.isdir(os.path.join(home_dir, i)) and '_50' in i:
			job_dir = os.path.join(home_dir, i)
			rep_tensors.append(pickle.Unpickler(open(os.path.join(job_dir, 'tca_output_rank_%d' % j), 'rb')).load())
	tensors.append(rep_tensors)
