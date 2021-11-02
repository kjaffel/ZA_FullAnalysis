import os
import logging
import pickle
import glob
import enlighten
import numpy as np
import pandas as pd

from sklearn import preprocessing
from ROOT import TFile, TTree
from import_tree import Tree2Pandas
from root_numpy import tree2array, rec2array

import parameters

def MakeScaler(data=None, list_inputs=[], TTree=[], generator=False, batch=5000, list_samples=None, additional_columns={}):
    
    # Generate scaler #
    logging.info('Starting computation for the scaler')
    scaler      = preprocessing.StandardScaler()
    
    if not os.path.exists(parameters.scaler_path):
        # Not generator #
        if data is not None:
            scaler.fit(data[list_inputs])
        # For generator #
        if generator:
            if list_samples is None:
                raise RuntimeError("Generator mask asked, you need to provide a sample list")
            
            logging.info("Computing mean and std")
            mean = np.zeros(len(list_inputs))
            std  = np.zeros(len(list_inputs))
            Ntot = 0
            pbar_mean = enlighten.Counter(total=len(list_samples), desc='Mean', unit='File')
            pbar_std  = enlighten.Counter(total=len(list_samples), desc='Std', unit='File')
            for f in list_samples:
                pbar_mean.update()
                pbar_std.update()
                if not os.path.exists(f):
                    continue
                file_handle = TFile.Open(f)
                for key in TTree:
                    ttree = file_handle.Get(key)
                    if not ttree:
                        logging.debug(f"Could not find {key} TTree in sample: {f}")
                        continue
                    tree = ttree.Get(parameters.tree_name)
                    N = tree.GetEntries()
                    Ntot += N
                    file_handle.Close()
                    logging.debug("Opening file %s (%d entries)"%(f,N))
                    # Loop over batches #
                    for i in range(0, N, batch):
                        array = Tree2Pandas(ttree, variables=list_inputs, era=None, weight=None, cut=None, xsec=None, event_weight_sum=None, luminosity=None, paramFun=None, tree_name=parameters.tree_name, t=key, start=i, stop=i+batch, additional_columns=additional_columns)[[inp.replace('$','') for inp in list_inputs]].astype(np.float32).values
                        mean += np.sum(array,axis=0)
                        std += np.sum(np.square(array-mean),axis=0)
            mean /= Ntot
            std = np.sqrt(std/Ntot)
            
            # Set manually #
            scaler.mean_ = mean
            scaler.scale_ = std

        # Disable preprocess on onehot variables #
        scaler.mean_[parameters.mask_op]  = 0.
        scaler.scale_[parameters.mask_op] = 1.

        # Safe checks #
        scaler.mean_[np.isnan(scaler.mean_)]   = 0.
        scaler.scale_[np.isnan(scaler.scale_)] = 1.
        scaler.scale_[scaler.scale_ == 0.]     = 1.
        scaler.var_ =  scaler.scale_**2

        # Save #
        with open(parameters.scaler_path, 'wb') as handle:
            pickle.dump(scaler, handle)
        logging.info(f'{parameters.scaler_path} has been created')
    # If exists, will be imported #
    else:
        with open(parameters.scaler_path, 'rb') as handle:
            scaler = pickle.load(handle)
        logging.info(f'{parameters.scaler_path} has been imported')
    # Test the scaler #
    if data is not None:
        try:
            y = scaler.transform(data[list_inputs])
            # Compute mean and var for inputs not in onehot encoding #
            mean_scale = np.mean(y[:,[not m for m in parameters.mask_op]])
            var_scale  = np.var(y[:,[not m for m in parameters.mask_op]])
            if abs(mean_scale)>0.01 or abs((var_scale-1)/var_scale)>0.1: # Check that scaling is correct to 1%
                logging.warning(f"Something is wrong with : {parameters.scaler_path} (mean = %0.6f, var = %0.6f), maybe you loaded an incorrect scaler"%(mean_scale,var_scale))
        except ValueError:
            logging.warning(f"Problem with : {parameters.scaler_path} you imported, has the data changed since it was generated !")
