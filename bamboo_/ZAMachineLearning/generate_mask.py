import numpy as np
import os
import logging

import parameters                                                                                                                                                                                      
from ZAMachineLearning import get_options

opt = get_options()
def GenerateMask(N,name):
    path_mask = os.path.join(parameters.path_out, opt.submit,'mask_'+name)
    if not os.path.exists(path_mask+'.npy'):                     
        mask = np.full((N,), False, dtype=bool)     
        size = parameters.training_ratio+parameters.evaluation_ratio
        mask[:int(size*N)] = True                         
        np.random.shuffle(mask)                                     
        np.save(path_mask,mask)                                 
        # False => Evaluation set, True => Training set           
        logging.info('Mask not found at '+path_mask+' -> Has been generated')
    else:                                                        
        mask = np.load(path_mask+'.npy')     
        logging.info('Mask found at '+path_mask+'.npy')

    return mask
