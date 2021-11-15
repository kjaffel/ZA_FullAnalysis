#!/usr/bin/env python
import logging
import re
import math
import glob
import csv
import os
import sys
import pprint
import copy
import pickle
import argparse
#import psutil
import operator
import itertools

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
if plt.rcParams['backend'] == 'TkAgg':
    raise ImportError("Change matplotlib backend to 'Agg' in ~/.config/matplotlib/matplotlibrc")
# Avoid tensorflow print on standard error
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from functools import reduce
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

import gc
gc.collect()

def get_options():
    """
    Parse and return the arguments provided by the user.
    """
    parser = argparse.ArgumentParser(description='ZA Machine learning for full run2 Ulegacy data')
    
    parser.add_argument('-o', '--outputs', action='store', required=True, type=str,
        help='ZA machine learning outputs dir ')

    #=========================================================================
    # Local For Test : Scan, deploy and restore arguments #
    #=========================================================================
    a = parser.add_argument_group('Scan, deploy and restore arguments')
    a.add_argument('-s','--scan', action='store', required=False, type=str, default='',
        help='Name of the scan to be used (modify scan parameters in NeuralNet.py)')
    a.add_argument('-task','--task', action='store', required=False, type=str, default='',
        help='Name of dict to be used for scan (Used by function itself when submitting jobs or DEBUG)')
    a.add_argument('--generator', action='store_true', required=False, default=False, 
        help='Wether to use a generator for the neural network')
    a.add_argument('--resume', action='store_true', required=False, default=False,
        help='Wether to resume the training of a given model (path in parameters.py)')
    #=========================================================================
    # Slurm Submissions : Splitting and submitting jobs arguments #
    #=========================================================================
    b = parser.add_argument_group('Splitting and submitting jobs arguments')
    b.add_argument('-split','--split', action='store', required=False, type=int, default=0,
        help='Number of parameter sets per jobs to be used for splitted training for slurm submission (if -1, will create a single subdict)')
    b.add_argument('-submit','--submit', action='store', required=False, default='', type=str,
        help='Wether to submit on slurm and name for the save (must have specified --split)')
    b.add_argument('-resubmit','--resubmit', action='store', required=False, default='', type=str,
        help='Wether to resubmit failed jobs given a specific path containing the jobs that succeded')
    b.add_argument('-debug','--debug', action='store_true', required=False, default=False,
        help='Debug mode of the slurm submission, does everything except submit the jobs')
    #=========================================================================
    # Repot and Produce Outputs: This do csv concatenation and get the best model : workdir/model/*.csv
    #                            Further used for : Analyzing or producing outputs of the given model 
    #=========================================================================
    c = parser.add_argument_group('Analyzing or producing outputs for given model (csv or zip file)')
    c.add_argument('-r','--report', action='store_true', required=False, default=False,
        help='report 10 best models (according to the eval_criterion) and plot on the console several histograms and *.png files')
    c.add_argument('-m','--model', action='store', required=False, type=str, default='',
        help='Loads the provided model name (without .zip and type, it will find them)') 
    c.add_argument('-k','--key', action='store', required=False, nargs='+', type=str, default=[], 
        help='Applies the provided model (do not forget -k) on the list of keys from parameters.TTree') 
    #=========================================================================
    # Physics arguments #
    #=========================================================================
    e = parser.add_argument_group('Physics arguments')
    e.add_argument('-p','--process', action='store', required=False, nargs='+', default=[],
        help='Which process you want to submit for training ')
    e.add_argument('--resolved', action='store_true', required=False, default=False,
       help='Resolved topology')
    e.add_argument('--boosted', action='store_true', required=False, default=False,
       help='Boosted topology')
    #=========================================================================
    # Additional arguments #
    #=========================================================================
    f = parser.add_argument_group('Additional arguments')
    f.add_argument('-v','--verbose', action='store_true', required=False, default=False,
        help='Show DEGUG logging')
    f.add_argument('--GPU', action='store_true', required=False, default=False,
        help='GPU requires to execute some commandes before')
    f.add_argument('--cache', action='store_true', required=False, default=False,
        help='Will use the cache')
    f.add_argument('--interactive', action='store_true', required=False, default=False,
        help='Interactive mode to check the dataframe')
    
    opt = parser.parse_args()

    if opt.split!=0 or opt.submit!='':
        if opt.scan!='' or opt.report:
            logging.critical('These parameters cannot be used together: ')  
            logging.critical('\t--scan --debug --verbose : to debug and check that all okay locally')  
            logging.critical('\t--submit --split 1       : to submit jobs to slurm if the previous okay')  
            logging.critical('\t--report                 : should be the last step in order to get the best model, plots, etc...')
            sys.exit(1)
    
    if opt.submit!='': # Need --output or --split arguments
        if opt.split==0 and len(opt.key)==0:
            logging.warning('In case of learning you forgot to specify --split')
            sys.exit(1)
    
    if opt.split!=0 and (opt.report or opt.key!='' or opt.scan!=''):
        logging.warning('Since you have specified a split, all the other arguments will be skipped')
    
    if opt.report and (opt.key!='' or opt.scan!=''):
        logging.warning('Since you have specified a scan report, all the other arguments will be skipped')
    
    if len(opt.key)!=0 and opt.key == '': 
        logging.critical(f'--key is missing choices: {parameters.TTree}')
        sys.exit(1)
    
    if opt.generator:
        logging.info("Will use the generator")
    
    if opt.resume:
        logging.info("Will resume the training of the model")

    return opt

def main():
    #############################################################################################
    # Preparation #
    #############################################################################################
    LOG_LEVEL = logging.DEBUG
    stream = logging.StreamHandler()
    stream.setLevel(LOG_LEVEL)
    logger = logging.getLogger(__name__)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(stream)
    try:
        import colorlog
        from colorlog import ColoredFormatter
        formatter = ColoredFormatter(
                        "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
                        datefmt='%m/%d/%Y %H:%M:%S',
                        reset=True,
                        log_colors={
                                'DEBUG':    'cyan',
                                'INFO':     'green',
                                'WARNING':  'blue',
                                'ERROR':    'red',
                                'CRITICAL': 'red',
                            },
                        secondary_log_colors={},
                        style='%'
                        )
        stream.setFormatter(formatter)
    except ImportError:
        print(" You can add colours to the output of Python logging module via : https://pypi.org/project/colorlog/")
        pass
    # Get options from user #
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s',datefmt='%m/%d/%Y %H:%M:%S')
    
    opt = get_options()
    # Verbose logging #
    if not opt.verbose:
        logging.getLogger().setLevel(logging.INFO)

    # Private modules containing Pyroot #
    from NeuralNet import HyperModel
    from import_tree import LoopOverTrees
    from produce_output import ProduceOutput
    from make_scaler import MakeScaler
    from submit_on_slurm import submit_on_slurm
    from generate_mask import GenerateMask
    from split_training import DictSplit
    from concatenate_csv import ConcatenateCSV
    from threadGPU import utilizationGPU
    import parameters

    logging.info("="*94)
    logging.info("  _____   _    __  __            _     _            _                          _             ")
    logging.info(" |__  /  / \  |  \/  | __ _  ___| |__ (_)_ __   ___| |    ___  __ _ _ __ _ __ (_)_ __   __ _ ")
    logging.info("   / /  / _ \ | |\/| |/ _` |/ __| '_ \| | '_ \ / _ \ |   / _ \/ _` | '__| '_ \| | '_ \ / _` |")
    logging.info("  / /_ / ___ \| |  | | (_| | (__| | | | | | | |  __/ |__|  __/ (_| | |  | | | | | | | | (_| |")
    logging.info(" /____/_/   \_\_|  |_|\__,_|\___|_| |_|_|_| |_|\___|_____\___|\__,_|_|  |_| |_|_|_| |_|\__, |")
    logging.info("                                                                                       |___/ ")
    logging.info("="*94)

    # Make path model #
    if not os.path.exists(parameters.path_model):
        os.mkdir(parameters.path_model)

    # Import variables from parameters.py
    variables = parameters.inputs+parameters.outputs+parameters.other_variables
    variables = [v for i,v in enumerate(variables) if v not in variables[:i]] # avoid repetitons while keeping order

    list_inputs  = [var.replace('$','') for var in parameters.inputs]
    list_outputs = [var.replace('$','') for var in parameters.outputs]
    
    #############################################################################################
    # Splitting into sub-dicts and slurm submission #
    #############################################################################################
    if opt.submit != '':
        if opt.split != 0:
            DictSplit(opt.split, opt.submit, opt.resubmit)
            logging.info('Splitting jobs done')
        
        p =''
        for proc in opt.process:
            p +=f' {proc}'
        # Arguments to send #
        # Do not forget the spaces after each arg!
        args = '' 
        if opt.resolved:            args += ' --resolved'
        if opt.boosted:             args += ' --boosted'
        if opt.generator:           args += ' --generator'
        if opt.GPU:                 args += ' --GPU'
        if opt.resume:              args += ' --resume'
        if opt.model!='':           args += f' --model {opt.model}'
        if len(opt.key)!=0:         args += f' --key {opt.key}'
        if len(opt.process)!=0:     args += f' --process {p} '
        if len(opt.outputs)!=0:     args += f' --output {opt.outputs} '

        if opt.submit!='':
            logging.info('Submitting jobs with args "%s"'%args)
            if opt.resubmit:
                submit_on_slurm(name=opt.submit+'_resubmit', args=args, debug=opt.debug)
            else:
                submit_on_slurm(name=opt.submit, args=args, debug=opt.debug)
        sys.exit()

    #############################################################################################
    # Reporting given model #
    #############################################################################################
    if opt.report:
        logging.info('Concatenating csv files from : %s'%(opt.outputs))
        dict_csv = ConcatenateCSV(opt.outputs)
        dict_csv.Concatenate()
        dict_csv.WriteToFile()
        dict_csv.save_bestmodel()
        
        reportNm   = dict_csv.modelNm()
        modelzipNm = dict_csv.modelzipNm()
        # will solve UnicodeEncodeError: 'ascii' codec 
        # can't encode characters in position 39-188: ordinal not in range(128) in NeuralNet.py", line 298
        os.system('export PYTHONIOENCODING=utf8')
        instance = HyperModel(reportNm)
        instance.HyperReport(workdir=opt.outputs, eval_criterion=parameters.eval_criterion, plotscan=False)

    #############################################################################################
    # Output of given files from given model #
    #############################################################################################
    if opt.model != '' and len(opt.key) != 0:
        path_output = os.path.join(opt.outputs,opt.model)
        if not os.path.exists(path_output):
            os.mkdir(path_output)
        inst_out = ProduceOutput(model=path_output, generator=opt.generator)
        # Loop over output keys #
        for key in opt.key:
            # Create subdir #
            path_output_sub = os.path.join(path_output,key+'_output')
            if not os.path.exists(path_output_sub):
                os.mkdir(path_output_sub)
            try:
                inst_out.OutputNewData(input_dir=parameters.samples_path,list_sample=samples_dict[key],path_output=path_output_sub)
            except Exception as e:
                logging.critical('Could not process key "%s" due to "%s"'%(key,e))
        sys.exit()
    
    #############################################################################################
    # Data Input and preprocessing #
    #############################################################################################
    # Memory Usage #
    #pid = psutil.Process(os.getpid())
    logging.info('Current pid : %d'%os.getpid())

    # Input path #
    logging.info('Starting tree importation')
    if opt.cache:
        logging.info(' --- trying to load from cache')
        if not os.path.exists(parameters.train_cache):
            raise RuntimeError(f'File not found: {parameters.train_cache}')
        try:
            logging.info(f'Will load train data from cache: {parameters.train_cache}')
            train_all = pd.read_pickle(parameters.train_cache)
        except Exception as ex:
            raise RuntimeError(f'{ex} when trying to read_pickle({parameters.train_cache}).')
        if parameters.crossvalidation:
            if not os.path.exists(parameters.test_cache):
                raise RuntimeError(f'File not found: {parameters.test_cache}')
            try:        
                logging.info(f'Will load testing data from cache: {parameters.test_cache}')
                test_all = pd.read_pickle(parameters.test_cache)
            except Exception as ex:
                raise RuntimeError(f'{ex} when trying to read_pickle({parameters.test_cache}).')
    else:
        logging.warning('SKIPPED: No cache will be used !')
        # Import arrays #
        data_dict = {}
        for node in parameters.nodes:
            list_sample = []
            TTree   = parameters.TTree
            if not TTree:
                logging.critical("selections list is empty, useless to continue !")
                sys.exit()

            data_node = None
            for era,samples_dict in {'2016':parameters.samples_dict_run2UL["2016"][f"combined_{node}_nodes"], 
                                     '2017':parameters.samples_dict_run2UL["2017"][f"combined_{node}_nodes"], 
                                     '2018':parameters.samples_dict_run2UL["2018"][f"combined_{node}_nodes"]}.items():
                if len(samples_dict)==0:
                    logging.info(f'Sample dict for era {era} is empty')
                    continue
                #list_sample = [sample for key in TTree for sample in samples_dict[key]]
                # cat :  reso, boosted , ee , mumu , ggH , bbH  for tagger+WP 
                print( samples_dict )
                list_sample = samples_dict
                
                data_node_era = LoopOverTrees(input_dir                 = parameters.samples_path[era],
                                              list_sample               = list_sample,
                                              variables                 = variables,
                                              weight                    = parameters.weights,
                                              cut                       = parameters.cut,
                                              era                       = era,
                                              luminosity                = parameters.lumidict[era],
                                              xsec_dict                 = parameters.xsec_dict,
                                              event_weight_sum_dict     = parameters.event_weight_sum_dict,
                                              additional_columns        = {'tag':node,'era':era},
                                              tree_name                 = parameters.tree_name,
                                              TTree                     = TTree, 
                                              paramFun                  = None,
                                              start                     = None,
                                              stop                      = None)
                # The shape attribute for numpy arrays returns the dimensions of the array. 
                # If Y has n rows and m columns, then Y.shape is (n,m). So Y.shape[0] is n.
                smp_info = '{:5s} class - era {}  : sample size = {:10d}'.format(node, era,data_node_era.shape[0])
                if data_node is None:
                    data_node = data_node_era
                else:
                    data_node = pd.concat([data_node,data_node_era],axis=0)
                
                if parameters.weights is not None:
                    smp_info += ', weight sum = {:.3e} (with normalization = {:.3e})'.format(data_node_era[parameters.weights].sum(),data_node_era['event_weight'].sum())
                logging.info(smp_info)
                
            smp_info2 = '{:5s} class : sample size = {:10d}'.format(node,data_node.shape[0])
            if data_node.shape[0] == 0:
                logging.info(smp_info2)
                continue
            data_dict[node] = data_node
        
        #logging.info('Current memory usage : %0.3f GB'%(pid.memory_info().rss/(1024**3)))
        # Modify MA and MH for background #
        mass_prop_ZA = [(x, len(list(y))) for x, y in itertools.groupby(sorted(data_dict['ZA'][["mH","mA"]].values.tolist()))]
        mass_prop_DY = [(x,math.ceil(y/data_dict['ZA'].shape[0]*data_dict['DY'].shape[0])) for x,y in mass_prop_ZA]
        mass_prop_TT = [(x,math.ceil(y/data_dict['ZA'].shape[0]*data_dict['TT'].shape[0])) for x,y in mass_prop_ZA]
        
        # array of [(mH,mA), proportions]
        mass_DY = np.array(reduce(operator.concat, [[m]*n for (m,n) in mass_prop_DY]))
        mass_TT = np.array(reduce(operator.concat, [[m]*n for (m,n) in mass_prop_TT]))
        
        np.random.shuffle(mass_DY) # Shuffle so that each background event has random masses
        np.random.shuffle(mass_TT) # Shuffle so that each background event has random masses
        
        df_masses_DY = pd.DataFrame(mass_DY,columns=["mH","mA"]) 
        df_masses_TT = pd.DataFrame(mass_TT,columns=["mH","mA"]) 
        df_masses_DY = df_masses_DY[:data_dict['DY'].shape[0] ]# Might have slightly more entries due to numerical instabilities in props
        df_masses_TT = df_masses_TT[:data_dict['TT'].shape[0] ]# Might have slightly more entries due to numerical instabilities in props
        
        data_dict['DY'][["mH","mA"]] = df_masses_DY
        data_dict['TT'][["mH","mA"]] = df_masses_TT

        # Check the proportions #
        logging.debug("Check on the masses proportions")
        tot_DY = 0
        tot_TT = 0
        for masses, prop_in_ZA in mass_prop_ZA:
            prop_in_DY = data_dict['DY'][(data_dict['DY']["mH"]==masses[0]) & (data_dict['DY']["mA"]==masses[1])].shape[0]
            prop_in_TT = data_dict['TT'][(data_dict['TT']["mH"]==masses[0]) & (data_dict['TT']["mA"]==masses[1])].shape[0]
            logging.debug("... Mass point (MH = %d, MA = %d)\t: N signal = %d (%0.2f%%),\tN DY = %d (%0.2f%%)\tN TT = %d (%0.2f%%)"
                         %(masses[0],masses[1],prop_in_ZA,prop_in_ZA/data_dict['ZA'].shape[0]*100,prop_in_DY,prop_in_DY/data_dict['DY'].shape[0]*100,prop_in_TT,prop_in_TT/data_dict['TT'].shape[0]*100))
            tot_DY += prop_in_DY
            tot_TT += prop_in_TT
        assert tot_DY == data_dict['DY'].shape[0]
        assert tot_TT == data_dict['TT'].shape[0]

        # Weight equalization #
        if parameters.weights is not None:
            weight_DY = data_dict['DY']["event_weight"]
            weight_TT = data_dict['TT']["event_weight"]
            # Use mass prop weights so that eahc mass point has same importance #
            weight_ZA = np.zeros(data_dict['ZA'].shape[0])
            for m,p in mass_prop_ZA:    
                idx = list(data_dict['ZA'][(data_dict['ZA']["mH"]==m[0]) & (data_dict['ZA']["mA"]==m[1])].index)
                weight_ZA[idx] = 1./p
            # We need the different types to have the same sumf of weight to equalize training
            # Very small weights produce very low loss function, needs to add multiplicating factor
            weight_DY = weight_DY/np.sum(weight_DY)*1e5
            weight_TT = weight_TT/np.sum(weight_TT)*1e5
            weight_ZA = weight_ZA/np.sum(weight_ZA)*1e5
        else:
            weight_DY = np.ones(data_dict['DY'].shape[0])
            weight_TT = np.ones(data_dict['TT'].shape[0])
            weight_ZA = np.ones(data_dict['ZA'].shape[0])

        # Check sum of weight #
        if np.sum(weight_ZA) != np.sum(weight_TT) or np.sum(weight_ZA) != np.sum(weight_DY) or np.sum(weight_TT) != np.sum(weight_DY):
            logging.warning ('Sum of weights different between the samples')
            logging.warning('\tDY : '+str(np.sum(weight_DY)))
            logging.warning('\tTT : '+str(np.sum(weight_TT)))
            logging.warning('\tZA : '+str(np.sum(weight_ZA)))

        data_dict['DY']['learning_weight'] = pd.Series(weight_DY)
        data_dict['TT']['learning_weight'] = pd.Series(weight_TT)
        data_dict['ZA']['learning_weight'] = pd.Series(weight_ZA)
        #logging.info('Current memory usage : %0.3f GB'%(pid.memory_info().rss/(1024**3)))

        # Data splitting #
        mask_DY = GenerateMask(data_dict['DY'].shape[0],parameters.suffix+'_DY')
        mask_TT = GenerateMask(data_dict['TT'].shape[0],parameters.suffix+'_TT')
        mask_ZA = GenerateMask(data_dict['ZA'].shape[0],parameters.suffix+'_ZA')
           # Needs to keep the same testing set for the evaluation of model that was selected earlier
        try:
            train_DY = data_dict['DY'][mask_DY==True]
            train_TT = data_dict['TT'][mask_TT==True]
            train_ZA = data_dict['ZA'][mask_ZA==True]
            
            test_DY  = data_dict['DY'][mask_DY==False]
            test_TT  = data_dict['TT'][mask_TT==False]
            test_ZA  = data_dict['ZA'][mask_ZA==False]
        except ValueError:
            logging.critical("Problem with the mask you imported, has the data changed since it was generated ?")
            raise ValueError
            
        #logging.info('Current memory usage : %0.3f GB'%(pid.memory_info().rss/(1024**3)))
        del data_dict
        
        train_all = pd.concat([train_DY,train_TT,train_ZA],copy=True).reset_index(drop=True)
        test_all  = pd.concat([test_DY,test_TT,test_ZA],copy=True).reset_index(drop=True)
        
        del train_TT, train_DY, train_ZA, test_TT, test_DY, test_ZA
        #logging.info('Current memory usage : %0.3f GB'%(pid.memory_info().rss/(1024**3)))

        # Randomize order, we don't want only one type per batch #
        random_train = np.arange(0,train_all.shape[0]) # needed to randomize x,y and w in same fashion
        np.random.shuffle(random_train)                # Not needed for testing
        train_all = train_all.iloc[random_train]
          
        # Add target #
        label_encoder  = LabelEncoder()
        onehot_encoder = OneHotEncoder(sparse=False)
        label_encoder.fit(train_all['tag'])
        
        # From strings to labels #
        train_integers = label_encoder.transform(train_all['tag']).reshape(-1, 1)
        test_integers  = label_encoder.transform(test_all['tag']).reshape(-1, 1)
        
        # From labels to strings #
        train_onehot = onehot_encoder.fit_transform(train_integers)
        test_onehot  = onehot_encoder.fit_transform(test_integers)
        
        # From arrays to pd DF #
        train_cat = pd.DataFrame(train_onehot,columns=label_encoder.classes_,index=train_all.index)
        test_cat  = pd.DataFrame(test_onehot,columns=label_encoder.classes_,index=test_all.index)
        
        # Add to full #
        train_all = pd.concat([train_all,train_cat],axis=1)
        test_all  = pd.concat([test_all,test_cat],axis=1)
        train_all[list_inputs+list_outputs] = train_all[list_inputs+list_outputs].astype('float32')
        test_all[list_inputs+list_outputs]  = test_all[list_inputs+list_outputs].astype('float32')
        
        # Preprocessing #
        # The purpose is to create a scaler object and save it
        # The preprocessing will be implemented in the network with a custom layer
        if opt.scan!='': # If we don't scan we don't need to scale the data
            MakeScaler(train_all, list_inputs, TTree, generator=False, batch=100000, list_samples=None, additional_columns={})
            
        train_all.to_pickle(parameters.train_cache)
        if parameters.crossvalidation:
            test_all.to_pickle(parameters.test_cache)
        logging.info('Data saved to cache')
        logging.info('... Training set : %s'%parameters.train_cache)


    logging.info("Sample size seen by network : %d"%train_all.shape[0])
    if parameters.crossvalidation:
        logging.info("Sample size for the output  : %d"%test_all.shape[0])
    #logging.info('Current memory usage : %0.3f GB'%(pid.memory_info().rss/(1024**3)))
    
    if opt.interactive:
        import IPython
        IPython.embed()
    #############################################################################################
    # DNN #
    #############################################################################################
    if opt.GPU:
        # Start the GPU monitoring thread #
        thread = utilizationGPU(print_time = 900, print_current = False, time_step=0.01)
        thread.start()

    if opt.scan != '':
        instance = HyperModel(opt.scan,list_inputs,list_outputs)
        instance.HyperScan(data      = train_all,
                           task      = opt.task,
                           model_idx = None,
                           generator = opt.generator,
                           resume    = opt.resume)
        instance.HyperDeploy(best='eval_error')
        
    if opt.GPU:
        # Closing monitor thread #
        thread.stopLoop()
        thread.join()
    
    if opt.report:
        # Make path #
        path_output = os.path.join(opt.outputs, 'model', modelzipNm)
        if not os.path.exists(path_output):
            os.makedirs(path_output)

        # Instance of output class #
        inst_out = ProduceOutput(model       = [modelzipNm],
                                 generator   = opt.generator,
                                 list_inputs = list_inputs)
        
        # Use it on test samples #
        logging.info('  Processing test output sample  '.center(80,'*'))
        if parameters.crossvalidation: # in cross validation the testing set in inside the training DF
            inst_out.OutputFromTraining(data=test_all,path_output=path_output, crossval_use_training=True)
        else:
            inst_out.OutputFromTraining(data=train_all,path_output=path_output, crossval_use_training=False)
             
if __name__ == "__main__":
    main()
