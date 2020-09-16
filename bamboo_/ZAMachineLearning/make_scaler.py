import os
import logging
import pickle
import glob
#import enlighten
import numpy as np
import pandas as pd
from sklearn import preprocessing
from ROOT import TFile, TTree
from root_numpy import tree2array, rec2array

import parameters
from ZAMachineLearning import get_options

opt = get_options()

def MakeScaler(data=None,list_inputs=[],generator=False,batch=100000):
    # Generate scaler #
    scaler_name = 'scaler_'+parameters.suffix+'.pkl'
    scaler_path = os.path.join(parameters.path_out,opt.submit,scaler_name)
    scaler = preprocessing.StandardScaler()
    print ( "scaler_path:", scaler_path )
    if not os.path.exists(scaler_path):
        # Not generator #
        
        print ( 'list_inputs:', list_inputs ) 
        print ( ' data:', data )
        print ( data[list_inputs] ) 
        if data is not None:
            scaler.fit(data[list_inputs])
        # For generator #
        if generator:
            logging.info("-"*80)
            logging.info("Computing mean")
            # Mean Loop #
            mean = np.zeros(len(list_inputs))
            Ntot = 0
            for f in glob.glob(parameters.path_gen_training+'/*root'):
                file_handle = TFile.Open(f)
                tree = file_handle.Get('tree')
                N = tree.GetEntries()
                Ntot += N
                logging.info("Opening file %s (%d entries)"%(f,N))
                # Loop over batches #
                #pbar = enlighten.Counter(total=N//batch+1, desc='Mean', unit='Batch')
                for i in range(0, N, batch):
                    array = rec2array(tree2array(tree,branches=list_inputs,start=i,stop=i+batch))
                    mean += np.sum(array,axis=0)
                    #pbar.update()
            mean /= Ntot
            
            # Var Loop #
            logging.info("-"*80)
            logging.info("Computing std")
            std = np.zeros(len(list_inputs))
            for f in glob.glob(parameters.path_gen_training+'/*root'):
                file_handle = TFile.Open(f)
                tree = file_handle.Get('tree')
                N = tree.GetEntries()
                logging.info("Opening file %s (%d entries)"%(f,N))
                # Loop over batches #
                #pbar = enlighten.Counter(total=N//batch+1, desc='Std', unit='Batch')
                for i in range(0, N, batch):
                    array = rec2array(tree2array(tree,branches=list_inputs,start=i,stop=i+batch))
                    std += np.sum(np.square(array-mean),axis=0)
                    #pbar.update()
            std = np.sqrt(std/Ntot)
            # Set manually #
            scaler.mean_ = mean
            scaler.scale_ = std

        # Save #
        with open(scaler_path, 'wb') as handle:
            pickle.dump(scaler, handle)
        logging.info('Scaler %s has been created'%scaler_name)
    # If exists, will import it #
    else:
        with open(scaler_path, 'rb') as handle:
            scaler = pickle.load(handle)
        logging.info('Scaler %s has been imported'%scaler_name)
     # Test the scaler #
    if data is not None:
        try:
            mean_scale = np.mean(scaler.transform(data[list_inputs]))
            var_scale = np.var(scaler.transform(data[list_inputs]))
        except ValueError:
            logging.critical("Problem with the scaler '%s' you imported, has the data changed since it was generated ?"%scaler_name)
            raise ValueError
        if abs(mean_scale)>0.01 or abs((var_scale-1)/var_scale)>0.01: # Check that scaling is correct to 1%
            logging.critical("Something is wrong with scaler '%s' (mean = %0.6f, var = %0.6f), maybe you loaded an incorrect scaler"%(scaler_name,mean_scale,var_scale))
            raise RuntimeError

