import tensortools
import numpy as np
import pickle

tensors = []

max_rank = 50
rep_length = 5

for j in range(1, max_rank+1):
	rep_tensors = []
	for i in os.listdir(home_dir):
		if os.path.isdir(os.path.join(home_dir, i)) and '_50' in i:
			job_dir = os.path.join(home_dir, i)
			rep_tensors.append(pickle.Unpickler(open(os.path.join(job_dir, 'tca_output_rank_%d' % j), 'rb')).load())
	tensors.append(rep_tensors)


corrs = []
for rank in tensors:
	rank_corrs = np.zeros((rep_length, rep_length))
	for index1, tensor1 in enumerate(rank):
		for index2, tensor2 in enumerate(rank):
			rank_corrs[index1, index2] = tt.kruskal_align(tensor1.factors, tensor2.factors, permute_V=True)
	corrs.append(rank_corrs)

corrs = np.array(corrs)

