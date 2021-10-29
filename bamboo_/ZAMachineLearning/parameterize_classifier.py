import os
import sys
import re
import logging
import random
import copy

import pandas as pd
import numpy as np

import parameters

def ParametrizeClassifier(data,name):
    logging.info('Starting the parameterization of the classifier')
    # Add new column : parametric weight HToZA #
    new_col = pd.DataFrame(np.zeros(data.shape[0]),index=data.index,columns=[name])
    data = pd.concat([data,new_col],axis=1)

    # Split in signal and background samples #
    idx_sig   = data['tag']=='HToZA'
    idx_back  = np.invert(idx_sig)
    data_sig  = data[idx_sig]
    data_back = data[idx_back]
   
    # Get the masses #
    list_signal = [s for s in parameters.inputs if s.find('HToZA')!=-1] # Only take the HtoZA weights (not background)
    masses = np.asarray([(float(re.findall(r'\d+',s)[1]),float(re.findall(r'\d+',s)[2])) for s in list_signal]) # mAmH

    # Signal case #
    logging.info('\tParameterizing the signal')
    dict_of_regions = {k: v for k, v in data_sig.groupby(['mH_gen','mA_gen'])} # One region = one specific couple mH_gen,mA_gen
    new_sig_data = []
    for key,val in dict_of_regions.items(): # key = (mH_gen,mA_gen), val = DF
        mH_gen = key[0]
        mA_gen = key[1]
        w = val[(name.replace('HToZA','HToZA_mH_%d_mA_%d'))%(mH_gen,mA_gen)]
        val[name] = w
        new_sig_data.append(val)
    new_sig_data = pd.concat(new_sig_data, axis=0) 

    # Background case #
    new_back_data = []
    logging.info('\tParameterizing the background')
        # repetition at each mass point
    for i in range(masses.shape[0]):
        df = copy.deepcopy(data_back)
        df['mH_gen'] = masses[i,0]
        df['mA_gen'] = masses[i,1]
        df[name] = df[(name.replace('HToZA','HToZA_mH_%d_mA_%d'))%(masses[i,0],masses[i,1])]
        new_back_data.append(df)
    new_back_data = pd.concat(new_back_data, axis=0)
    new_back_data['learning_weight'] /= masses.shape[0] # Not unbalance training in favour of background

    # Concatenate #
    data = pd.concat((new_sig_data,new_back_data),axis=0).reset_index(drop=True)

    return data
