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

home_dir = '/home/camp/warnert/working/Recordings/190410/2019-04-10_15-04-49'

tensor = pickle.Unpickler(open(os.path.join(home_dir, 'ds_tensor.pkl'), 'rb')).load()
tensor = tensor['tensor']
trialbank = pickle.Unpickler(open('/home/camp/warnert/working/Recordings/190325/simple_and_plumes_190325.trialbank', 'rb')).load()

simps_plumes = pickle.Unpickler(open(os.path.join(home_dir, 'plume_and_simple_trials.pkl'), 'rb')).load()
full_plumes = simps_plumes['plume']
full_simps = simps_plumes['simple']


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

