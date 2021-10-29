import os
import logging
import ROOT
import numpy as np

import parameters

def GenerateMask(N,name):
    if not name.endswith(".npy"):
        name += ".npy"
    path_mask = os.path.join(parameters.path_out,'mask_'+name)
    if not os.path.exists(path_mask):                     
        mask = np.full((N,), False, dtype=bool)     
        size = parameters.training_ratio+parameters.evaluation_ratio
        mask[:int(size*N)] = True                         
        # False => Output set, True => Training set           
        np.random.shuffle(mask)                                     
        # Save #
        np.save(path_mask,mask)                                 
        logging.info('Mask not found at %s -> Has been generated'%path_mask)
    else:                                                        
        mask = np.load(path_mask)     
        logging.info('Mask found at %s'%path_mask)
    return mask

def GenerateSampleMasks(list_samples,name):
    if not name.endswith(".npz"):
        name += ".npz"
    path_mask = os.path.join(parameters.path_out,'mask_'+name)
    if not os.path.exists(path_mask):
        mask_dict = {}
        for i,sample in enumerate(list_samples):
            if not os.path.exists(sample):
                raise RuntimeError(f'Sample path {sample} not found !')
            rootFile = ROOT.TFile(sample)
            for key in parameters.TTree:
                tree = rootFile.Get(key)
                if not tree.GetListOfKeys().Contains(parameters.tree_name): 
                    logging.debug(f'Could not find {parameters.tree_name} in {key} TTree  in file path : {sample} ')
                    continue
                N = tree.Get(parameters.tree_name).GetEntries(parameters.cut)
                rootFile.Close()
                Nt = int(parameters.training_ratio*N)
                Ne = int(parameters.evaluation_ratio*N)
                No = N-Nt-Ne
                mask = np.concatenate((np.zeros(Nt),np.ones(Ne),np.ones(No)*2),axis=0)
                # 0 -> training, 1-> evaluation, 2-> output
                np.random.shuffle(mask)                                     
                mask_dict[sample] = mask
                logging.debug('[%3.2f%%] : Produced mask for %s for selection %s'%(i*100/len(list_samples),sample, key))
        np.savez(path_mask,**mask_dict)
        logging.info('Mask not found at %s -> Has been generated'%path_mask)
    else:
        logging.info('Mask found at %s'%path_mask)
        mask_dict = np.load(path_mask)
    return mask_dict

def GenerateSliceIndices(model_idx):
    Nm = parameters.N_models
    assert model_idx < Nm
    Nt = parameters.N_train
    Ne = parameters.N_eval
    Na = parameters.N_apply
    Ns = parameters.N_slices
    model_idx *= Ns/Nm
    apply_idx  = [int(model_idx+i) for i in range(0,Na)]
    eval_idx   = [int ((apply_idx[-1]+1+i)%Ns) for i in range(0,Ne)]
    train_idx  = [i for i in range(0,Ns) if i not in apply_idx and not i in eval_idx]
    return apply_idx,eval_idx,train_idx

def GenerateSliceMask(slices,mask):
    selector = np.full((mask.shape[0]), False, dtype=bool)
    for s in slices:
        selector = selector | (mask == s)
    return selector
