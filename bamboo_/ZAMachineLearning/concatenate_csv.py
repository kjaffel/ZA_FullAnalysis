import os
import re
import sys
import logging
import glob
import csv
import pprint
import shutil
import pandas as pd
from pandas import read_csv, DataFrame

import parameters 

class ConcatenateCSV:
    def __init__(self,path): 
        self.path = path
        self.Concatenate()
        self.WriteToFile()
    
    def Concatenate(self):
        self.dict_tot = {} 
        self.counter  = 0
        self.full_df  = None
        self.name     = None
        for f in glob.glob(os.path.join(self.path,'slurm', 'output', '*.csv')):
            # name should be the same we need to get it first for other use later !
            self.name = f.split('/')[-1].split('_dict')[0]
            logging.debug('File : %s'%(f))

            # Use pandas to get the dict inside the csv file #
            panda_data = read_csv(f)
            panda_data['zip'] = os.path.basename(f.replace('.csv','.zip'))
            
            # Initialize dict at first elements #
            if self.counter == 0:
                self.full_df = panda_data
            else:
                self.full_df = pd.concat([self.full_df,panda_data],axis=0)
            self.counter += panda_data.shape[0]
            logging.debug('\tCurrent number of hyperparameter sets : %d'%(self.counter)) 

        if parameters.eval_criterion == 'eval_error':
            self.full_df = self.full_df.sort_values(by=['eval_mean'], ascending=False)
        elif parameters.eval_criterion == 'val_loss':
            self.full_df = self.full_df.sort_values(by=['val_loss'])
        elif parameters.eval_criterion == 'val_acc':
            self.full_df = self.full_df.sort_values(by=['val_acc'],ascending=False)
        else:
            raise RuntimeError('Evaluation criterion is not valid')
        logging.info('Total number of hyperparameter sets : %d'%(self.full_df.shape[0])) 

    def WriteToFile(self):
        # Define name for output file #
        self.path_out = os.path.join(parameters.path_out,'model',self.name+'.csv')
        self.full_df.to_csv(self.path_out)
        logging.info('The best model saved in :  %s'%(self.path_out))
    
    def save_bestmodel(self):
        with open(self.path_out, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for line_count, row in enumerate(csv_reader):
                if line_count == 0:
                    print(f'Column names are ::: {", ".join(row)}')
                if line_count == 1:
                    self.zipNm = row["zip"].replace('.zip', '_isbest_model')
                    best_model_path = os.path.join(parameters.path_out,'model',row["zip"].replace('.zip', '_isbest_model.zip'))
                    shutil.copyfile(os.path.join(parameters.path_out,'slurm', 'output',row["zip"]), best_model_path)
                    logging.info(f'\tA copy of the best model will be kept in : {best_model_path}')
                    continue
    
    def modelNm(self):
        return self.name
    def modelzipNm(self):
        return self.zipNm
    
    @staticmethod
    def _correct(obj):
        # Corrects the <function relu at 0x{12}> -> relu
        # Corrects the <class 'keras.optimizers.Adam'> -> Adam
        if obj.startswith('<function'):
            return obj.split(' ')[1]
        elif obj.startswith('<class'):
            return obj.split(' ')[1].split('.')[2].replace("'>","")
        else:
            return obj
