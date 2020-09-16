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

import parameters
from root_numpy import tree2array, rec2array
from ROOT import TChain, TFile, TTree


###############################################################################
# Tree2Pandas#
###############################################################################

def Tree2Pandas(input_file, variables, weight=None, cut=None, xsec=None, event_weight_sum=None, luminosity=None, n=None, tree_name='Events',start=None):
    """
    Convert a ROOT TTree to a numpy array.
    """
    variables = [var for var in variables if not var.startswith("$")]
    variables = copy.copy(variables) # Otherwise will add the weight and have a duplicate branch

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
        return None
    file_handle = TFile.Open(input_file)
    if not file_handle.GetListOfKeys().Contains(tree_name):
        logging.warning("Could not find tree %s in %s"%(tree_name,input_file))
        return None
    tree = file_handle.Get(tree_name)
    N = tree.GetEntries()
    logging.debug('... Number of events : '+str(N))

    relative_weight = 1 
    if xsec is not None and event_weight_sum is not None:
        if luminosity is None:
            luminosity = 1
        relative_weight = xsec * luminosity / event_weight_sum
        logging.debug('\t\tReweighting requested')
        logging.debug('\t\t\tCross section : %0.5f'%xsec)
        logging.debug('\t\t\tEvent weight sum : %0.2f'%event_weight_sum)
        logging.debug('\t\t\tLuminosity : %0.2f'%luminosity)
        logging.debug('\t\tRelative weight %0.3e'%relative_weight)

    # Read the tree and convert it to a numpy structured array
    if weight is not None:
        variables += [weight]
    data = tree2array(tree, branches=variables, selection=cut, start=start, stop=n)
    
    # Convert to pandas dataframe #
    df = pd.DataFrame(data)
    if weight is not None:
        df['event_weight'] = df[weight]*relative_weight


    # Only part of tree #
    if n:
        if n == -1:
            n = N # Get all entries
        if start:
            if n < start:
                logging.critical('Importing tree with start higher than end, will output empty tree')
            logging.info("Reading from {} to {} in input tree".format(start,n))
        else:
            logging.info("Reading only {} from input tree".format(n))
        

    return df

###############################################################################
# LoopOverTrees #
###############################################################################

def LoopOverTrees(input_dir, variables, weight=None, additional_columns={}, cut=None, xsec_json=None, event_weight_sum_json=None, luminosity=None, list_sample=None, start=None, n=None):
    """
    Loop over ROOT trees inside input_dir and process them using Tree2Pandas.
    """
    # Check if directory #
    if not os.path.isdir(input_dir):
        logging.critical("%s not a directory"%sinput_dir)
        raise RuntimeError

    logging.debug("Accessing directory : "+input_dir)

    # Xsec #
    xsec = None
    if xsec_json is not None:
        with open(xsec_json,'r') as handle:
            dict_xsec = json.load(handle)
    # Event weight sum #
    event_weight_sum = None
    if event_weight_sum_json is not None:
        with open(event_weight_sum_json,'r') as handle:
            dict_event_weight_sum = json.load(handle)

    # Wether to use a given sample list or loop over files inside a dir #
    if list_sample is None:
        list_sample = glob.glob(os.path.join(input_dir,"*.root"))
    else:
        list_sample = [os.path.join(input_dir,s) for s in list_sample]

    # Loop over the files #
    first_file = True
    all_df = pd.DataFrame() 
    for sample in list_sample:
        sample_name = os.path.basename(sample)
        logging.debug("\tAccessing file : %s"%sample_name)

        if xsec_json is not None:
            for name,xs in dict_xsec.items():
                if name in sample_name:
                    xsec = xs
        if event_weight_sum_json is not None:
            for name,ews in dict_event_weight_sum.items():
                if name in sample_name:
                    event_weight_sum = ews
       
        # Get the data as pandas df #
        df = Tree2Pandas(input_file                 = sample,
                         variables                  = variables,
                         weight                     = weight,
                         cut                        = cut,
                         xsec                       = xsec,
                         event_weight_sum           = event_weight_sum,
                         luminosity                 = luminosity,
                         n                          = n,
                         tree_name                  = 'Events',
                         start                      = start) 

        if df is None:
            continue

        # Find mH, mA #
        if sample_name.find('HToZA')!=-1: # Signal -> Search for mH and mA
            mH = [int(re.findall(r'\d+', sample_name)[2])]*df.shape[0]    
            mA = [int(re.findall(r'\d+', sample_name)[3])]*df.shape[0]    
        else: # Background, set them at 0
            mH = [0]*df.shape[0]
            mA = [0]*df.shape[0]

        # Register in DF #
        df['mH'] = pd.Series(mH)
        df['mA'] = pd.Series(mA)

        # Register sample name #
        df['sample'] = pd.Series([sample_name.replace('.root','')]*df.shape[0])
        
        # Register additional columns #
        if len(additional_columns.keys()) != 0:
            for key,val in additional_columns.items():
                df[key] = pd.Series([val]*df.shape[0])

        # Concatenate into full df #
        if first_file:
            all_df = df
            first_file = False
        else:
            all_df = pd.concat([all_df,df])
        all_df = all_df.reset_index(drop=True) # Otherwise there will be an index repetition for each file
    return all_df
