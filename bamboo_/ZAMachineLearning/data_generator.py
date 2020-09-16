import sys
import glob
import os
import math
import logging
import pickle
import copy

import numpy as np
import keras

import ROOT

from root_numpy import root2array, rec2array

class WeightsGenerator():
    def __init__(self,path_hist):
        root_file = ROOT.TFile(path_hist,"READ")
        self.hist = copy.deepcopy(root_file.Get("weights"))
        root_file.Close()
        self.tot_time = 0
#        self.hist_time = ROOT.TH1F("weight_time","weight_time",1000,0,5)

    def fromHistToDict(self):
        self.weightDict = {}

    def getWeights(self,arr):
        weights = np.zeros(arr.shape[0])
        import timeit
        start_time = timeit.default_timer()
        for i in range(0,arr.shape[0]):
            hist_bin = self.hist.FindBin(arr[i])
            if hist_bin < self.hist.GetNbinsX() and hist_bin >= 0:
                weights[i] = self.hist.GetBinContent(hist_bin)
            else: # If we are in the under/overflow bin
                weights[i] = 1
        # Normalize weights (learning becomes unstable otherwise #
        weights /= np.sum(weights)
        #elapsed = timeit.default_timer() - start_time
        #self.tot_time += elapsed
        #print("Weights evaluated on ",elapsed,"Total time for weight generation ",self.tot_time)
        return weights
        


class DataGenerator(keras.utils.Sequence):
    def __init__(self,path,inputs,outputs,batch_size=32,state_set='',weights_generator=''):
        self.path       = path                          # Path to root file 
        self.inputs     = inputs                        # List of strings of the variables as inputs
        self.outputs    = outputs                       # List of strings of the variables as outputs
        self.batch_size = batch_size                    # Batch size
        if os.path.isdir(path):
            self.list_files = glob.glob(path+'/*.root') # List of files obtained from path
        elif os.path.isfile(path):
            self.list_files = [path]                    # Only one file for generation
        else:
            logging.error("path '%s' is not a dir nor a file "%path)
            sys.exit(1)
        self.state_set = state_set # 'training', 'validation', 'test', 'output'
        self.weights_generator = weights_generator


        if (len(self.list_files)>self.batch_size):
            logging.warning("Fewer files than requested batch size, might be errors")
        logging.info("Starting importation for %s set"%self.state_set)
        if self.weights_generator != '':
            logging.info("Will produce weights from %s"%weights_generator)
            self.weightsGen = WeightsGenerator(self.weights_generator)

        self.get_fractions()
        self.n          = 0
        self.max        = self.__len__() # Must be after get_fractions because that's where self.n_batches is defined

    def get_fractions(self):
        entries = dict() # fraction inside each dataset compared to total
        self.batch_sample = dict() # number of events in each dataset that will enter the batch
        self.pointer = dict()  # Keep memory of how far we have extracted the chunk
        # Compute entries #
        self.n_tot = 0
        for f in self.list_files:
            rootFile = ROOT.TFile(f)
            tree = rootFile.Get('tree')
            n = tree.GetEntries()
            logging.info("Number of entries of file %s : %d"%(f,n))
            entries[f] = n
            self.n_tot += n

        if self.n_tot<self.batch_size:
            logging.error("Fewer events than required batch size for generator")
            sys.exit(1)

        # Fill batch contributions #
        total_in_batch = 0
        for i,(filename,n_entries) in enumerate(entries.items()):
            size_in_batch = math.ceil((n_entries/self.n_tot)*self.batch_size)# keep same ratios in batch as in total sample
            self.batch_sample[filename] = size_in_batch 
            total_in_batch += size_in_batch
        # IF all contributions are too much
        if total_in_batch > self.batch_size: # taken too much, remove from most present sample
            key, value = max(self.batch_sample.items(), key = lambda p: p[1])
            self.batch_sample[key] -= (total_in_batch - self.batch_size)
        # Get maximum number of batches #
        self.n_batches = np.inf
        for filename,n_entries in entries.items():
            size = self.batch_sample[filename]
            if n_entries//size < self.n_batches : 
                self.n_batches = n_entries//size

        logging.info("Total number of events : %d"%(self.n_tot))
        logging.info("Will use %d batches of %d events"%(self.n_batches,self.batch_size))
        logging.info("="*80)

    def __getitem__(self,index): # gets the batch for the supplied index
        # return a tuple (numpy array of image, numpy array of labels) or None at epoch end
        logging.debug("-"*80)
        logging.debug("New batch importation")
        X = np.zeros((self.batch_size,len(self.inputs)))
        Y = np.zeros((self.batch_size,len(self.outputs)))
        pointer = 0

        for f,size in self.batch_sample.items():
            size = int(size) # For python2
            X[pointer:pointer+size,:]= rec2array(root2array(f,treename='tree',branches=self.inputs,start=index*size,stop=(index+1)*size))
            Y[pointer:pointer+size,:] = rec2array(root2array(f,treename='tree',branches=self.outputs,start=index*size,stop=(index+1)*size))
            pointer += size
            logging.debug("%s    - Added %d entries from file %s"%(self.state_set,size,os.path.basename(f)))

        if self.weights_generator == '':
            return X,Y
        else:
            W = self.weightsGen.getWeights(Y)
            return X,Y,W

    def __len__(self): # gets the number of batches
        # return the number of batches in this epoch (do not change in the middle of an epoch)
        return self.n_batches
    def on_epoch_end(self): # performs auto shuffle if enabled
        # Do what we need to do between epochs
        pass

    def __next__(self):
        if self.n >= self.max:
           self.n = 0
        result = self.__getitem__(self.n)
        self.n += 1
        return result
