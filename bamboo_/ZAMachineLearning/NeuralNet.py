import os
import re
import sys
import json
import shutil
import pickle
import string
import logging
import random
import csv
import time
import itertools
import plotille # For plots in terminal
import array

import numpy as np
import matplotlib.pyplot as plt

import talos
from talos import Scan, Reporting, Predict, Evaluate, Deploy, Restore, Autom8
from talos.utils.best_model import *
from talos.model.layers import *
from tensorflow.keras.optimizers import Adam
from talos.model.normalizers import lr_normalizer

from sklearn.model_selection import train_test_split

# Personal files #
import parameters
import Operations
import Model
from split_training import DictSplit
from plot_scans import PlotScans
from preprocessing import PreprocessLayer
from data_generator import DataGenerator
from generate_mask import GenerateSliceIndices, GenerateSliceMask

class HyperModel:
    def __init__(self, name, list_inputs=None, list_outputs=None):
        self.name = name
        #self.custom_objects = {'PreprocessLayer': PreprocessLayer} # Needs to be specified when saving and restoring
        self.custom_objects = {name:getattr(Operations,name) for name in dir(Operations) if name.startswith('op')}
        self.list_inputs    = list_inputs
        self.list_outputs   = list_outputs
        # Printing #
        if self.list_inputs is not None:
            logging.info('Number of features : %d'%len(self.list_inputs))
            for name,op in zip(self.list_inputs,parameters.operations):
                if op is not None:
                    op_inst = getattr(Operations,op)()
                    logging.info('..... %s (onehot encoding : %d bits)'%(name,op_inst.onehot_dim))
                else:
                    logging.info('..... %s'%name)
        if self.list_outputs is not None:
            logging.info('Number of outputs : %d'%len(self.list_outputs))
            for name in self.list_outputs:
                logging.info('..... %s'%name)

    #############################################################################################
    # HyperScan #
    #############################################################################################
    def HyperScan(self,data,task,model_idx=None,generator=False,resume=False):
        """
        Performs the scan for hyperparameters
        If task is specified, will load a pickle dict splitted from the whole set of parameters
        Data is a pandas dataframe containing all the event informations (inputs, outputs and unused variables)
        The column to be selected are given in list_inputs, list_outputs as lists of strings
        Reference : /home/ucl/cp3/fbury/.local/lib/python3.6/site-packages/talos/scan/Scan.py
        """
        logging.info(' Starting scan '.center(80,'-'))
            
        # Records #
        if not generator:
            x = data[[param.replace('$','') for param in parameters.inputs]].values
            y = data[self.list_outputs+['learning_weight']].values
            # Data splitting #
            if model_idx is None:
                size = parameters.training_ratio/(parameters.training_ratio+parameters.evaluation_ratio)
                self.x_train, self.x_val, self.y_train, self.y_val = train_test_split(x,y,train_size=size)

            else: # Cross validation : take the training and evaluation set based on the mask
                # model_idx == index of mask on which model will be applied (aka, not trained nor evaluated)
                _, eval_idx, train_idx = GenerateSliceIndices(model_idx) #, GenerateSliceMask
                eval_mask  = GenerateSliceMask(eval_idx,data['mask'])
                train_mask = GenerateSliceMask(train_idx,data['mask'])
                self.x_val   = x[eval_mask]
                self.y_val   = y[eval_mask]
                self.x_train = x[train_mask]
                self.y_train = y[train_mask]
            logging.info("Training set   : %d"%self.x_train.shape[0])
            logging.info("Evaluation set : %d"%self.x_val.shape[0])
        else:
            # Needs to use dummy inputs to launch talos scan but in Model the generator will be used
            dummyX = np.ones((1,len(parameters.inputs)))
            dummyY = np.ones((1,len(self.list_outputs))) 
            
            self.x_train = dummyX
            self.y_train = dummyY
            self.x_val   = dummyX
            self.y_val   = dummyY

        # Talos hyperscan parameters #
        self.task = task
        if self.task !='': # if task is specified load it otherwise get it from parameters.py
            with open(os.path.join(parameters.path_out,'split',self.name,self.task), 'rb') as f:
                self.p = pickle.load(f)
        else: # We need the full dict
            self.p = parameters.p

        # If resume, puts it as argument ot be passed to function #
        # Also, needs to change the dictionary parameters for the one in the imported model #
        if resume:
            logging.info("Will resume training of model %s"%parameters.resume_model)
            # Get model and extract epoch range #
            a = Restore(parameters.resume_model,custom_objects=self.custom_objects)
            initial_epoch = a.params['epochs'][0]
            supp_epochs = self.p['epochs'][0] # Will update the param dict, so must keep that in memory
            batch_size_save = self.p['batch_size'] # Might want to change batch_size in retraining
            # Update params dict with the one from the trained model #
            self.p = a.params
            self.p['resume'] = [parameters.resume_model]
            self.p['initial_epoch'] = [initial_epoch]  # Save initial epoch to be passed to Model
            self.p['epochs'][0] = initial_epoch+supp_epochs # Initial = last epoch of already trained model (is a list)
            self.p['batch_size'] = batch_size_save
            logging.warning("Since you asked to resume training of model %s, the parameters dictionary has been set to the one used to train the model"%parameters.resume_model)
            logging.info("Will train the model from epoch %d to %d"%(self.p['initial_epoch'][0],self.p['epochs'][0]))

        # add model_idx if cross validation #
        if parameters.crossvalidation:
            self.p['model_idx'] = [model_idx]

        # Check if no already exists then change it -> avoids rewriting  #
        # This is only valid in worker mode, not driver #
        no = 1
        if self.task == '': # If done on frontend
            name = self.name
            if model_idx is not None:
                name += '_crossval%d'%model_idx
            while os.path.exists(os.path.join(parameters.path_out,self.name+'_'+str(no)+'.csv')):
                no +=1
            self.name_model = name+'_'+str(no)
        else:               # If job on cluster
            name = self.name
            if model_idx is not None:
                name += '_crossval%d'%model_idx
            self.name_model = name+'_'+self.task.replace('.pkl','')
        
        print (self.x_train)
        print (self.x_train.shape)
        print (self.y_train)
        print (self.y_train.shape)

        print( 'helooooooooooooooooooooooooooooooooooooo111111111111111111111111111111111111111111111111111')
        # Define scan object #
        self.h = Scan(x=self.x_train,                       # Training inputs 
                      y=self.y_train,                       # Training targets
                      params=self.p,                        # Parameters dict
                      dataset_name=self.name,               # Name of experiment
                      experiment_no=str(no),                # Number of experiment
                      model= getattr(Model,'NeuralNetGeneratorModel') if generator else getattr(Model,parameters.model),
                      val_split=0.1,                        # How much data is to be used for val_loss
                      reduction_metric='val_loss',          # How to select best model
                      #grid_downsample=0.1,                 # When used in serial mode
                      #random_method='lhs',                     ---
                      #reduction_method='spear',                ---
                      #reduction_window=1000,                   ---
                      #reduction_interval=100,                  ---
                      #last_epoch_value=True,                   ---
                      print_params=True,                    # To print param at each job
                      repetition=parameters.repetition,     # Wether a set of parameters is to be trained several times
                      path_model = parameters.path_model,   # Where to save the model
                      custom_objects=self.custom_objects,   # Custom object : custom layer
                )
        print( self.h)
        print( 'helooooooooooooooooooooooooooooooooo22222222222222222222222222222222222222222222222222222' )
        if not generator:
            # Use the save information in DF #
            self.h_with_eval = Autom8(scan_object = self.h,     # the scan object
                                      x_val = np.hsplit(self.x_val,self.x_val.shape[1]),       # Evaluation inputs
                                      y_val = self.y_val[:,:-1],# Evaluatio targets (last column is weight)
                                      n = -1,                   # How many model to evaluate (n=-1 means all)
                                      metric = 'val_loss',      # On what metric to sort
                                      folds = 5,                # Cross-validation splits for nominal and errors
                                      shuffle = True,           # Shuffle bfore evaluation
                                      average = 'micro',        # Only needed for multi class !!!
                                      asc = True)               # Ascending because loss function
            self.h_with_eval.data.to_csv(self.name_model+'.csv') # save to csv including error
            self.autom8 = True
        else:
            # Needs to use the generator evaluation #
            error_arr = np.zeros(self.h.data.shape[0])
            for i in range(self.h.data.shape[0]):
                logging.info("Evaluating model %d"%i)
                # Load model #
                model_eval = model_from_json(self.h.saved_models[i],custom_objects=self.custom_objects)   
                model_eval.set_weights(self.h.saved_weights[i])
                model_eval.compile(optimizer=Adam(),loss={'OUT':parameters.p['loss_function'][0]},metrics=['accuracy'])
                
                # Evaluate model #
                evaluation_generator = DataGenerator(path       = parameters.sampleList_full,
                                                     TTree      = parameters.TTree, 
                                                     inputs     = parameters.inputs,
                                                     outputs    = parameters.outputs,
                                                     cut        = parameters.cut,
                                                     weight     = parameters.weight, 
                                                     batch_size = parameters.p['batch_size'][0],
                                                     state_set  = 'evaluation',
                                                     model_idx  = model_idx if parameters.crossvalidation else None)
                eval_metric = model_eval.evaluate_generator(generator             = evaluation_generator,
                                                            workers               = parameters.workers,
                                                            use_multiprocessing   = True)
                # Save errors #
                error_arr[i] = eval_metric[0]
                logging.info('Error is %f'%error_arr[i])

            # Save evaluation error to csv #
            self.h.data['eval_mean'] = error_arr
            self.h.data.to_csv(self.name_model+'.csv') # save to csv including error
            self.autom8 = True
            
        # returns the experiment configuration details
        logging.info('='*80)
        logging.debug('Details')
        logging.debug(self.h.details)

    #############################################################################################
    # HyperDeploy #
    #############################################################################################
    def HyperDeploy(self,best='eval_error'):
        """
        Deploy the model according to the evaluation error (default) or val_loss if not found
        Reference :
            /home/ucl/cp3/fbury/.local/lib/python3.6/site-packages/talos/commands/deploy.py
        """
        logging.info(' Starting deployment '.center(80,'-'))

        # Check arguments #
        if best != 'val_loss' and best != 'eval_error' : 
            logging.critical('Model not saved as .zip due to incorrect best model parameter')
        if self.task == '':     # On frontend
            path_model = parameters.path_model
        else:                   # On cluster
            path_model = ''

        # Save models #
        if best == 'eval_error' and not self.autom8:
            logging.warning('You asked for the evaluation error but it was not computed, will switch to val_loss') 
            best = 'val_loss'
        if best == 'eval_error':
            Deploy(self.h,model_name=self.name_model,metric='eval_mean',asc=False,path_model=path_model)
        elif best == 'val_loss':
            Deploy(self.h,model_name=self.name_model,metric='val_loss',asc=False,path_model=path_model)
            logging.warning('Best model saved according to val_loss')
        else: 
            logging.error('Argument of HyperDeploy not understood')
            sys.exit(1)

    #############################################################################################
    # HyperReport #
    #############################################################################################
    def HyperReport(self,eval_criterion='val_loss'):
        """
        Reports the model from csv file of previous scan
        Plot several quantities and comparisons in dir /$name/
        Selects the best models according to the eval_criterion (val_loss or eval_error)
        Reference :
        """
        logging.info(' Starting reporting '.center(80,'-'))

        # Get reporting #
        report_file = os.path.join('model',self.name+'.csv')
        if os.path.exists(report_file):
            r = Reporting(report_file)
        else:
            logging.critical('Could not find %s'%(report_file))
            sys.exit(1)

        # returns the results dataframe
        logging.info('='*80)
        logging.info('Complete data after n_round = %d'%(r.rounds()))
        logging.debug(r.data)

        # Lowest eval_error #
        logging.info('-'*80)
        if eval_criterion == 'eval_error':
            logging.info('Lowest eval_error = %0.5f obtained after %0.f rounds'%(r.low('eval_mean'),r.rounds2high('eval_mean')))
        elif eval_criterion == 'val_loss':
            logging.info('Lowest val_loss = %0.5f obtained after %0.f rounds'%(r.low('val_loss'),r.rounds2high('val_loss')))
        else:
            logging.critical('Could not find evaluation criterion "%s" in the results'%eval_criterion)
            sys.exit(1)

        # Best params #
        logging.info('='*80)
        logging.info('Best parameters sets')
        if eval_criterion == 'eval_error':
            sorted_data = r.data.sort_values('eval_mean',ascending=False)
        elif eval_criterion == 'val_loss':
            sorted_data = r.data.sort_values('val_loss',ascending=False)

        for i in range(0,10):
            logging.info('-'*80)
            logging.info('Best params no %d'%(i+1))
            try:
                logging.info(sorted_data.iloc[i])
            except:
                logging.warning('\tNo more parameters')
                break
        # Hist in terminal #
        eval_mean_arr = r.data['eval_mean'].values
        val_loss_arr  = r.data['val_loss'].values
        fig1 = plotille.Figure()
        fig1.width = 150
        fig1.height = 50
        fig1.set_x_limits(min_=np.amin(eval_mean_arr),max_=np.amax(eval_mean_arr))
        fig1.color_mode = 'byte'
        fig1.histogram(eval_mean_arr, bins=200, lc=25)
        print ('  Evaluation error  '.center(80,'-'))
        print ('Best model : ',sorted_data.iloc[0][['eval_mean']])
        print(fig1.show(legend=True))

        fig2 = plotille.Figure()
        fig2.width = 150
        fig2.height = 50
        fig2.set_x_limits(min_=np.amin(val_loss_arr),max_=np.amax(val_loss_arr))
        fig2.color_mode = 'byte'
        fig2.histogram(val_loss_arr, bins=200, lc=100)
        print ('  Val loss  '.center(80,'-'))
        print ('Best model : ',sorted_data.iloc[0][['val_loss']])
        print(fig2.show(legend=True))

        logging.info('='*80)

        # Generate dir #
        path_plot = os.path.join(parameters.path_out,'model',self.name)
        if not os.path.isdir(path_plot):
            os.makedirs(path_plot)
        
        logging.info('Starting plots')
        # Make plots #
        PlotScans(data=r.data,path=path_plot,tag='')

    #############################################################################################
    # HyperRestore #
    #############################################################################################
    def HyperRestore(self,inputs,verbose=0,generator=False):
        """
        Retrieve a zip containing the best model, parameters, x and y data, ... and restores it
        Produces an output from the input numpy array
        Reference :
            /home/ucl/cp3/fbury/.local/lib/python3.6/site-packages/talos/commands/restore.py
        """
        logging.info(('Using model %s.zip '%(self.name).center(80,'-')))
        # Restore model #
        loaded = False
        while not loaded:
            try:
                a = Restore(os.path.join(parameters.path_model, self.name+'.zip'),custom_objects=self.custom_objects)
                loaded = True
            except Exception as e:
                logging.warning('Could not load model due to "%s", will try again in 3s'%e)
                time.sleep(3)
       
        if not generator:
            outputs = a.model.predict(inputs,batch_size=parameters.output_batch_size,verbose=verbose)
        else:
            inputsLL = inputs[[param.replace('$','') for param in parameters.inputs]].astype(np.float32).values
            outputs  = a.model.predict(np.hsplit(inputsLL,inputsLL.shape[1]),batch_size=parameters.output_batch_size,verbose=verbose)
#       outputs  = a.model.predict_generator(output_generator,
#                                            workers=parameters.workers,
#                                            max_queue_size=2*parameters.workers,
#                                            use_multiprocessing=True,
#                                            verbose=1)
        return outputs
