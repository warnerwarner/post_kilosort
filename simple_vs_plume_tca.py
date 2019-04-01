'''
Computes TCA for subsections of recordings, and also the full recording to determine if a subsection has less factors than the whole
'''

import pickle
import numpy as np
import tensortools as tt
import os 
import psutil
import sys



rank = list(sys.argv)[1]
rank = int(rank)
job_id = list(sys.argv)[2]

home_dir = '/home/camp/warnert/working/Recordings/190325/2019-03-25_16-57-37'

tensor = pickle.Unpickler(open(os.path.join(home_dir, 'ds_tensor.pkl'), 'rb')).load()
tensor = tensor['tensor']
trialbank = pickle.Unpickler(open('/home/camp/warnert/working/Recordings/190325/simple_and_plumes_190325.trialbank', 'rb')).load()

plumes = []
for index, i, in enumerate(trialbank):
	for j in i[1]:
		if j['type'] == 'Plume':
			plumes.append(index)
			break

simps = [i for i in range(len(trialbank)) if i not in plumes]
full_simps = [j+i*len(trialbank) for i in range(14) for j in simps]
full_simps = full_simps[:-1] # Cuase we lost the last trial
full_plumes = [j+i*len(trialbank) for i in range(14) for j in plumes]

simp_tensor = tensor[:, :, full_simps]
plume_tensor = tensor[:, :, full_plumes]

print('full tensor')
full_tca = tt.cp_als(tensor, rank)
print('simple tensor')
simp_tca = tt.cp_als(simp_tensor, rank)
print('plume tensor')
plume_tca = tt.cp_als(plume_tensor, rank)

tcas = {'full':full_tca, 'simps':simp_tca, 'plume':plume_tca}

output_dir = os.path.join(home_dir, job_id)
if not os.path.isdir(output_dir):
	os.mkdir(output_dir)

pickle.dump(tcas, open(os.path.join(output_dir, 'tca_rank_%d_' % rank +job_id+'.pkl'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)

