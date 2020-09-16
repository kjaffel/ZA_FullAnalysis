import glob
import os
import re
import math
import sys
import json
import shutil
import pickle
import pprint
import logging

import numpy as np
import pandas as pd
import itertools

from talos.parameters.ParamGrid import ParamGrid
from talos import Scan

# Personal files #
import parameters 

# TODO : add possiblity to use more than one folder for resubmit

#################################################################################################
# SplitTraining #
#################################################################################################

class SplitTraining:

    def __init__(self,p,params_per_job,dir_name):
        self.params = p
        self.grid_downsample = None
        self.params_per_job = params_per_job
        self.dir_name = dir_name
        self.repetition = parameters.repetition
    
        self.paramgrid_object = ParamGrid(self)

        # Generate grid #
        self.param_log, self.param_grid = self._generate_grid()
        logging.info("Number of hyperparameters : "+str(self.param_grid.shape[0]))
        if self.param_grid.shape[0] < self.params_per_job: # If more params_per_job than actual parameters, equal them
            self.params_per_job = self.param_grid.shape[0] 
            logging.warning('You specified a number of parameters per job higher than the actual number of parameters, will use the latter')
        if self.params_per_job == -1: # params_per_job = number of params in set  
            self.params_per_job = self.param_grid.shape[0]
            logging.info('Single dict of %d parameters has been created'%(self.params_per_job))
        if self.params_per_job>1:
            logging.warning("Be careful with the combinations of parameters, they scale as N_prams! ... might be redundencies")



        # Split the list into dict #
        self.list_dict = self._split_dict()

        # Save as pickle file #
        self._save_as_pickle()

    def _generate_grid(self):

        _param_log = self.paramgrid_object.param_log
        _param_grid = self.paramgrid_object.param_grid  
        
        return _param_log,_param_grid 
        

    def _split_dict(self):
        _list_dict = []
        i = 0
        count = 0
        for param in self.param_grid:
            if i==0:
                # Initialize dict #
                one_dict = {}
                for key in self.params.keys():
                    one_dict[key] = []

            # Append each case #
            for p,k in zip(param,self.params.keys()):
                one_dict[k].append(p)

            i += 1
            count += 1
            if i == self.params_per_job:
                i=0
                _list_dict.append(one_dict)
            logging.debug("Creating the list - current status : %d/%d"%(count,self.param_grid.shape[0]))
        return _list_dict

    def _save_as_pickle(self):
        # Remove content of dir if already exists #
        path_dict = os.path.join(parameters.main_path,'split',self.dir_name)
        logging.debug('Directory containing the dict : %s'%(path_dict))
        if os.path.exists(path_dict):
            logging.debug('Removing older files')
            for file_pkl in glob.glob(os.path.join(path_dict,'*.pkl')):
                logging.debug('Removed file %s'%(file_pkl)) 
                os.remove(file_pkl)
        else:
            os.makedirs(path_dict)

        # Dump each dict into separate pkl file #
        for i,d in enumerate(self.list_dict):
            logging.debug("Writing the dict - current status : %d/%d"%(i,len(self.list_dict)))
            with open(path_dict+'/dict_'+str(i)+'.pkl', 'wb') as f: 
                pickle.dump(d, f)  
        logging.info('Generated %d dict of parameters at \t%s'%(len(self.list_dict),path_dict))

#################################################################################################
# CheckResubmit #
#################################################################################################
class ResubmitSplitting(SplitTraining):
    def __init__(self,p,params_per_job,path_success,dir_name):
        SplitTraining.__init__(self,p=p,params_per_job=params_per_job,dir_name=dir_name)
        self.path_success = path_success
        self.repetition = parameters.repetition
        self.GetSuccessingJobs()
        
    def GetSuccessingJobs(self):
        # get success list of csv #
        csv_files = glob.glob(self.path_success+'/*.csv')
        if len(csv_files) == 0:
            logging.warning('No successed jobs were found')
        # Get the pandas dataframe of all the trials #
        full_list = []
        for csv_file in csv_files:
            full_list.append(pd.read_csv(csv_file))
        df = pd.concat(full_list)

        # Get the parameters names from dict #
        names = list(self.params.keys())
        names_from_df = list(df.columns.values)
        if 'lr.1' in names_from_df:
            logging.debug('Learning rate normalization has been used, will correct for that')
            idx = names.index('lr')
            names[idx] = 'lr.1'

        # Select corresponding df columns #
        success_trials = df[df.columns.intersection(names)].values
        all_trials = self.param_grid[:,:-1]
        if success_trials.shape[0] == 0:
            logging.warning('All the jobs have been completed, no need to resubmit')
            sys.exit()

        # Look for matches #
        count = 0
        match_arr = np.array([],dtype=bool)
        for i in range(all_trials.shape[0]):
            #print (all_trials[i,:])
            match = self.FindMatch(success_trials,all_trials[i,:])
            match_arr = np.append(match_arr,match)
            if match :
                count += 1
        if count != success_trials.shape[0]:
            logging.critical('Matches between successful trials and full config is inconsistent, will exit to avoid mistakes')
            logging.debug('Found %d successful trials in full trials compared to %d that should have been found'%(count,success_trials.shape[0]))
            sys.exit()
        self.param_grid = self.param_grid[match_arr==False]
        
        # Split the list into dict #
        logging.info('New set of dict has been generated for the resubmit')
        logging.debug('Remaining parameters :')
        for i in range(0,self.param_grid.shape[0]):
            logging.debug(self.param_grid[i,:])
        self.dir_name += '_resubmit'
        self.list_dict = self._split_dict()

        # Save as pickle file #
        self._save_as_pickle()

    def FindMatch(self,list_params,the_param):
        for row in range(list_params.shape[0]):
            for col in range(list_params.shape[1]):
                param1 = list_params[row,col] # param1 = from the list, param2 from the searched one
                param2 = the_param[col]
                if isinstance(param1,float) or isinstance(param1,int):
                    match = bool(param1 == param2)
                if isinstance(param1,str):
                    match = bool(param1.find(param2.__name__) != -1)
                    
                if not match: # At first different element, get next config
                    break
            if match: # Found a match, return and end
                return True

        if not match: # At the end, if not match return it
            return False
                
        
        
#################################################################################################
# DictSplit #
#################################################################################################
    
def DictSplit(params_per_job,name,resubmit=''):
        
    # Retrieve Hyperparameter dict #    
    p = parameters.p

       # Split into sub dict #
    if resubmit == '':
        SplitTraining(p,params_per_job=params_per_job,dir_name=name)
    else:
        ResubmitSplitting(p,params_per_job=params_per_job,path_success=resubmit,dir_name=name)

