import glob
import os
import sys
import logging
import json
import re
import collections
import copy
import array

import numpy as np
import pandas as pd

from root_numpy import tree2array, rec2array
from ROOT import TChain, TFile, TTree

import parameters


def Tree2Pandas(input_file, variables, era=None, weight=None, cut=None, xsec=None, event_weight_sum=None, luminosity=None, paramFun=None, tree_name=None, t=None, start=None, stop=None, additional_columns={}):
    """
    Convert a ROOT TTree to a pandas DF
    """
    smpNm = os.path.basename(input_file)
    
    # Otherwise will add the weight and have a duplicate branch
    variables = copy.copy([var for var in variables if not var.startswith("$")]) 
    
    # Check for repetitions in variables -> makes root_numpy crash #
    repeated_var = [item for item, count in collections.Counter(variables).items() if count > 1]
    if len(repeated_var) != 0:
        logging.critical('There are repeated variables')
        for var in repeated_var:
            logging.critical('... %s'%var)
        raise RuntimeError("Repeated arguments for importing data")

    # Get root tree, check if exists first #
    if not os.path.exists(input_file):
        logging.warning("File %s does not exist"%input_file)
        print ("File %s does not exist"%input_file)
        return None
    
    file_handle = TFile.Open(input_file)
    if not file_handle.GetListOfKeys().Contains(t):
        logging.debug(f"\t\tCould not find TTree {t} key for sample: {smpNm}")
        return None
    
    ttree = file_handle.Get(t)
    if not ttree:
        logging.debug(f"\t\tCould not find {tree_name} branch in TTree {t} for sample: {smpNm} ")
        return None
    else:
        tree = ttree.GetBranch(tree_name)
        N    = ttree.GetEntries()
        logging.debug('\t\tNumber of events from %s cat: %d'%(t, N))

    # Read the tree and convert it to a numpy structured array
    if weight is not None:
        variables += [weight]
    try:
        data = tree2array(ttree, branches=variables, selection=cut, start=start, stop=stop)
    except ValueError as e:
        logging.error("Issue with file {}".format(input_file))
        raise e

    # Convert to pandas dataframe #
    df = pd.DataFrame(data)
    
    # Reweighting #
    relative_weight = 1
    if weight is not None and xsec is not None and event_weight_sum is not None:
        if luminosity is None:
            luminosity = 1
        if era =="2016":
            if "preVFP" in input_file:
                luminosity = 19667.812849099
            elif "postVFP" in input_file:
                luminosity = 16977.701784453
            else:
                luminosity = 36645.514633552
        relative_weight = xsec * luminosity / event_weight_sum
        
        logging.debug('\t\tReweighting requested:')
        logging.debug('\t\t\t- Cross section    : %0.5f'%xsec)
        logging.debug('\t\t\t- Event weight sum : %0.2f'%event_weight_sum)
        logging.debug('\t\t\t- Luminosity       : %0.2f'%luminosity)
        logging.debug('\t\t\t- Relative weight  : %0.3e'%relative_weight)
        logging.debug('\t\t-----------------------------------------------------')
        
        df['cross_section']    = np.ones(df.shape[0])*xsec
        df['luminosity']       = np.ones(df.shape[0])*luminosity
        df['event_weight_sum'] = np.ones(df.shape[0])*event_weight_sum
    else:
        df['cross_section']    = np.ones(df.shape[0])
        df['luminosity']       = np.ones(df.shape[0])
        df['event_weight_sum'] = np.ones(df.shape[0])
        if df.shape[0] != 0:
            relative_weight /= df.shape[0]
   
    if weight is not None:
        df['event_weight'] = df[weight]*relative_weight
    else:
        df['event_weight'] = np.ones(df.shape[0])

    if paramFun is not None:
        assert callable(paramFun)
        param = paramFun(os.path.basename(input_file))
        if param is None:
            param = 0
        df['param'] = np.ones(df.shape[0]) * param
    
    # Register additional columns #
    if len(additional_columns.keys()) != 0:
        for key,val in additional_columns.items():
            df[key] = pd.Series([val]*df.shape[0])
    
    # Slice printout #
    if start is not None or stop is not None:
        ni = start if start is not None else 0
        nf = stop if stop is not None else N
        logging.debug(f"Reading from {ni} to {nf} in input tree (over {N} entries)")
    
    file_handle.Close()
    return df


def LoopOverTrees(input_dir, variables, list_sample=None, weight=None, cut=None, era=None, luminosity=None, xsec_dict=None, event_weight_sum_dict=None, additional_columns={}, tree_name=None, TTree=None, paramFun=None, start=None, stop=None):
    """
    Loop over ROOT trees inside input_dir and process them using Tree2Pandas.
    """
    # Check if directory #
    if not os.path.exists(input_dir):
        raise RuntimeError("%s does not exist"%input_dir)
    
    # Xsec #
    if xsec_dict is not None and not isinstance(xsec_dict,dict):
        raise NotImplementedError('Cannot handle xsec not being a dict')
    
    # Event weight sum #
    if event_weight_sum_dict is not None and not isinstance(event_weight_sum_dict,dict):
        raise NotImplementedError('Cannot handle event weight sum not being a dict')
    if era is None and (xsec_dict is None or event_weight_sum_dict is None):
        raise RuntimeError('If you plan to use xsec and even weight sum you need to provide the era (either one value or a list with one element per sample)')
    
    # Wether to use a given sample list or loop over files inside a dir #
    if list_sample is None:
        list_sample = glob.glob(os.path.join(input_dir,"*.root"))
    else:
        list_sample = [os.path.join(input_dir,s) for s in list_sample]
    
    # Start and stop #
    if isinstance(start,list) and isinstance(stop,list):
        if len(start) != len(list_sample):
            raise RuntimeError("Start events list does not match the list samples")
        if len(stop) != len(list_sample):
            raise RuntimeError("Stop events list does not match the list samples")

    # Loop over the files #
    first_file = True
    all_df = pd.DataFrame() 
    for i,sample in enumerate(list_sample):
        logging.debug('===================================================')
        logging.debug("\tAccessing file : %s"%sample)
        sample_name = os.path.basename(sample)

        # Eras
        if isinstance(era,list):
            era = eras
        
        # Cross section #
        xsec = None
        if xsec_dict is not None and sample_name in xsec_dict[era].keys():
            xsec = xsec_dict[era][sample_name]
        
        # Event weight sum #
        event_weight_sum = None
        if event_weight_sum_dict is not None and sample_name in event_weight_sum_dict[era].keys():
            event_weight_sum = event_weight_sum_dict[era][sample_name]
        
        # Start #
        ni = None
        if start is not None:
            if isinstance(start,list):
                ni = start[i]
            else:
                ni = start
        
        # Stop #
        nf = None
        if stop is not None:
            if isinstance(stop,list):
                nf = stop[i]
            else:
                nf = stop
        for key_ in TTree:
            # Get the data as pandas df #
            df = Tree2Pandas(input_file                 = sample,
                             variables                  = variables,
                             era                        = era,
                             weight                     = weight,
                             cut                        = cut,
                             xsec                       = xsec,
                             event_weight_sum           = event_weight_sum,
                             luminosity                 = luminosity,
                             tree_name                  = tree_name,
                             t                          = key_,
                             paramFun                   = paramFun,
                             start                      = ni,
                             stop                       = nf)
            if df is None:
                continue
            
            # Find mH, mA #
            if sample_name.find('HToZATo2L2B')!=-1: # Signal -> Search for mH and mA
                if 'tb_20p00' in sample_name or 'tb_1p50' in sample_name:
                    # new bbH signal sample
                    # HToZATo2L2B_MH_800p00_MA_700p00_tb_20p00_TuneCP5_bbH4F_13TeV_amcatnlo_pythia8_UL16preVFP.root
                    # new ggH signal sample
                    # GluGluToHToZATo2L2B_MH_1000p00_MA_50p00_tb_1p50_TuneCP5_13TeV_madgraph_pythia8_UL16preVFP.root
                    split_smpNm = sample_name.split('_')
                    mH = [float(split_smpNm[2].replace('p','.'))]*df.shape[0]
                    mA = [float(split_smpNm[4].replace('p','.'))]*df.shape[0]
                    logging.debug( f"\t\tmH = {float(split_smpNm[2].replace('p','.'))}, mA = {float(split_smpNm[4].replace('p','.'))}")
                else:
                    # old signal samples: 
                    # HToZATo2L2B_MH-3000_MA-2000
                    mH = [int(re.findall(r'\d+', sample_name)[2])]*df.shape[0]
                    mA = [int(re.findall(r'\d+', sample_name)[3])]*df.shape[0]
                    logging.debug( "\t\tmH = {} , mA = {}".format(int(re.findall(r'\d+', sample_name)[2]), int(re.findall(r'\d+', sample_name)[3])))
            elif sample_name.find('AToZHTo2L2B')!=-1:
                if 'tb_20p00' in sample_name or 'tb_1p50' in sample_name:
                    split_smpNm = sample_name.split('_')
                    mA = [float(split_smpNm[2].replace('p','.'))]*df.shape[0]
                    mH = [float(split_smpNm[4].replace('p','.'))]*df.shape[0]
                    logging.debug( f"\t\tmA = {float(split_smpNm[2].replace('p','.'))}, mH = {float(split_smpNm[4].replace('p','.'))}")
            else: # Background, set them at 0
                mH = [0]*df.shape[0]
                mA = [0]*df.shape[0]

            # Register in DF #
            df['mH'] = pd.Series(mH)
            df['mA'] = pd.Series(mA)
            
            # Register sample name #
            df['sample'] = pd.Series([sample_name.replace('.root',f'_{key_}')]*df.shape[0])

            # Register additional columns #
            if len(additional_columns.keys()) != 0:
                for key,val in additional_columns.items():
                    if isinstance(val,list):
                        if len(val) != len(list_sample):
                            raise RuntimeError('Value list %s you want to add has len %d while there are %d samples'%(key,len(val),len(list_sample)))
                        df[key] = pd.Series([val[i]]*df.shape[0])
                    else:
                        df[key] = pd.Series([val]*df.shape[0])
            
            # Concatenate into full df #
            if first_file:
                all_df = df
                first_file = False
            else:
                all_df = pd.concat([all_df,df])
    
    all_df = all_df.reset_index(drop=True) # Otherwise there will be an index repetition for each file

    # Zero pad possible nan #
    #all_df = all_df[~all_df.isnull().any(axis=1)]
    all_df = all_df.fillna(0.)

    return all_df
