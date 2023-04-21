#!/usr/bin/env python
import argparse
import glob
import os
import yaml
import random
import itertools
import math
import shutil
import subprocess
import root_numpy

from collections import defaultdict
from faker import Factory
fake = Factory.create()
from matplotlib import pyplot as plt

import numpy as np
import ROOT as R
R.gROOT.SetBatch(True)

from numpy_hist import NumpyHist

import Harvester as H
import HistogramTools as HT
import Constants as Constants
logger = Constants.ZAlogger(__name__)


# splitting same way in combine
sorted_files = { 
        # signal 
        'signal'   : ['AToZH', 'HToZA', 'GluGluToHToZA', 'GluGluToAToZH'],
        # data 
        'data'     : ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleElectron', 'SingleMuon'],
        # main Background
        'ttbar'    : ['TTToSemiLeptonic', 'TTTo2L2Nu', 'TTToHadronic'],
        'SingleTop': ['ST_'],
        'DY'       : ['DYJetsToLL_0J', 'DYJetsToLL_1J', 'DYJetsToLL_2J', 'DYJetsToLL_M-10to50'],
        # Others Backgrounds
        'WJets'    : ['WJetsToLNu'],
        'ttV'      : ['TTWTo', 'TTZTo'],
        'VV'       : ['ZZTo', 'WWTo', 'WZTo'],
        'VVV'      : ['ZZZ_', 'WWW_', 'WZZ_', 'WWZ_'],
        'SMHiggs'  : ['ggZH_HToBB_ZToLL_M-125', 'HZJ_HToWW_M-125', 'ZH_HToBB_ZToLL_M-125', 'ggZH_HToBB_ZToNuNu_M-125', 
                    'GluGluHToZZTo2L2Q_M125', 'ttHTobb_M125_', 'ttHToNonbb_M125_']
}

plotIt_mc_groups = {  # group, legend
        'DY'        : ['DY', 'DY+jets'],
        'ttbar'     : ['ttbar', 'ttbar'],
        'SingleTop' : ['ST', 'ST'],
        'SMHiggs'   : ['SM', 'ggh, tth, Zh'],
        'VV'        : ['VV', 'VV'],
        'WJets'     : ['others', 'VVV,ttV'],
        'VVV'       : ['others', 'VVV,ttV'],
        'ttV'       : ['others', 'VVV,ttV'],
}


def EraFromPOG(era):
    return '_UL'+era.replace('20','')


def mass_to_str(m):
    m = str(m).replace('p','.')
    m = "%.2f"%float(m)
    return str(m).replace('.','p')


def LATEX(uname=None):
    uname=uname.lower()
    if "elmu" in uname:
        label = "e^{+}#mu^{-}"
    elif "muel" in uname:
        label = "#mu^{+}e^{-}"
    elif "elel" in uname:
        label = "e^{+}e^{-}"
    elif "mumu" in uname:
        label = "#mu^{+}#mu^{-}"
    if "gg_fusion" in uname:
        label = "ggH"
    elif "bb_associatedProduction":
        label = "bbH"
    return label


def get_legend(smpNm):
    mode     = 'AToZH' if 'AToZH' in smpNm else 'HToZA'
    heavy    = mode[0]
    light    = mode[-1]
    comp     = 'nlo' if 'amcatnlo' in smpNm else 'lo'
    process  = f'gg{heavy}' if smpNm.startswith('GluGluTo') else(f'bb{heavy}')
    tb       = 1.5 if  smpNm.startswith('GluGluTo') else 20.0
    m_heavy  = smpNm.split('_')[2].split('-')[-1].replace('p', '.')
    m_light  = smpNm.split('_')[4].split('-')[-1].replace('p', '.')
    m_heavy  = ('%.2f'%float(m_heavy)).replace('.00', '')
    m_light  = ('%.2f'%float(m_light)).replace('.00', '')
    return "#splitline{%s: (m_{%s}, m_{%s})}{= (%s, %s) GeV}"%(process, heavy, light, m_heavy, m_light)


def rebinmethods(): #deprecated
    method   = {}
    normal   = [['scott', 'freedman'], ['Scotts rule', 'Freedman-Diaconis rule']]
    bayesian = [['knuth', 'blocks'], ["Knuth's rule", 'Bayesian blocks']]
    
    for i, m in enumerate([ normal, bayesian]):
        pNm = name + f'_{i}'
        for bins, title, subplot in zip(m[0],m[1],[121, 122]):
            ax = fig.add_subplot(subplot)
            
            # plot a standard histogram in the background, with alpha transparency
            visualization.hist(data, bins=oldEdges, histtype='stepfilled',
                alpha=0.2, density=False, label='standard histogram')
            
            # plot an adaptive-width histogram on top
            visualization.hist(data, bins=bins, ax=ax, color='black',
                histtype='step', density=False, label=title)
            
            np_arr_edges_newhist = stats.histogram(np_arr_oldhist, bins=bins, range=None, weights=None)
            print( f'{title} new hist  : {np_arr_edges_newhist[0]}' )
            print( f'{title} new edges : {np_arr_edges_newhist[1]}' )
            
            rebin = len(newEdges[0]) +1
            root_newhist = R.TH1D(name, "", rebin, 0., 1.)
            
            newHist    = root_numpy.array2hist(np.flipud(np_arr_newhist), root_newhist)
            mergedBins = np.flipud(newEdges).tolist()
            
            for b in range(1, len(mergedBins) +2):
                newEdges.append(newHist.GetXaxis().GetBinLowEdge(b))
            method[bins] = [newHist, [newEdges, upEdges]]


def FindPrior():  # deprectaed !!
    random_seed = {'toy1': 500.}#, 'toy2':458., 'toy3': 42.}
    for t, rd in random_seed.items():
        toydata = np.array([])
        for el in np_arr_oldhist:
            toydata = np.append(toydata, [el*rd])
    
        for p_star in np.arange(0.95, 1., 0.01):
            p0 = p_star
            _fitness = stats.FitnessFunc(p0=p_star, gamma=None, ncp_prior=None)
            ncp      = _fitness.compute_ncp_prior(N=old_hist.GetNbinsX()) # or prior.calc(N=old_hist.GetNbinsX())
            newEdges = bayesian_blocks(oldEdges, weights=toydata, p0=p_star, gamma=None)
            logger.info( f'{t}, ncp= {ncp}, prior= {p0}, newBlocks= {len(newEdges)}, newEdges= {newEdges}') 
            
            p0 = p_star*(1/len(newEdges))
            new_toydata = optimizer.get_new_histogramWgt(old_hist, newEdges, oldEdges, verbose=False) [0]
            new_toydata = np.append(new_toydata, toydata[-1])
            rev_fitness = stats.FitnessFunc(p0=p0, gamma=None, ncp_prior=None)
            rev_ncp = _fitness.compute_ncp_prior(N=len(newEdges))
            new_newEdges  = bayesian_blocks(newEdges, weights=new_toydata, p0=p0, gamma=None)
            logger.info( f'{t}, reversed ncp= {rev_ncp}, prior= {p0}, newBlocks= {len(new_newEdges)}, newEdges= {new_newEdges}') 
            logger.info('======'*20) 


def get_yields(Observation, v=False):
    newdic = defaultdict(dict)
    channels = []
    for k,v in Observation.items():
        for k1, v1 in v.items():
            if not k1 in channels:
                channels.append(k1)
    for ch in channels:
        newdic[ch] = {}
        obs = 0 
        for k,v in Observation.items():
            if not v: continue
            newdic[ch][k] = Observation[k][ch][0]
            obs += Observation[k][ch][0]
            if v:
                print(f'Observation from {k} channel: {obs}')
        if v:
            print(f'===> Total Observation for {ch} channel: {obs}')
            print('==='*20)
    return newdic


def get_sortedfiles(binnings=None, inputs=None, era=None, toys=False, asimov=False):
    for rf in inputs:
        smpNm = rf.split('/')[-1].replace('.root','')
        if smpNm.startswith('__skeleton__'):
            continue
        if asimov:
            binnings['root'] = rf.split('/')[-2]
            
            if 'summed_data' in smpNm or 'summed_scaled_data' in smpNm: 
                binnings['files']['asimov']['tot_obs_data'].append(rf)
            elif 'summed_mc' in smpNm or 'summed_scaled_mc' in smpNm: 
                binnings['files']['asimov']['tot_b'].append(rf)
            elif 'summed_signal' in smpNm or 'summed_scaled_signal' in smpNm: 
                binnings['files']['asimov']['tot_s'].append(rf)
            
            for group , poss_f in sorted_files.items():
                if any(x in smpNm for x in poss_f):
                    if not group in ['data', 'signal']:
                        binnings['files']['asimov']['mc'][group].append(smpNm)
                    else:
                        binnings['files']['asimov'][group].append(smpNm)
        if toys:
            binnings['files']['toys'].append(rf)
    return binnings


def hybride_binning(BOnly=None, SOnly=None):
    """Use min() to find the nearest value in a list to a given one 
        low bin edges from signal template are not accurate: 
        do not accept values below 0.6 
    """
    print( 'S-Only:', SOnly[0], 'B-Only:', BOnly[0] )

    signal_edges = [item for item in SOnly[0] if item > 0.65]
    given_value  = signal_edges[0]
    idx2 = SOnly[0].index(given_value)

    absolute_difference_function = lambda list_value : abs(list_value - given_value)
    closest_value = min(BOnly[0], key=absolute_difference_function)
    print( f'given_value:  {given_value}, closest_value: {closest_value} starting from {idx2}')
    
    idx = BOnly[0].index(closest_value) 
    newEdges  = BOnly[0][0:idx] + signal_edges
    FinalBins = BOnly[1][0:idx] + SOnly[1][idx2:]
    
    print( f'hybride binning: {newEdges} , len: {len(newEdges)}')
    return [newEdges, FinalBins]


def available_points(inputs):
    points = []
    for fin in inputs:
        smp = fin.split('/')[-1].replace('.root','')
        if not 'To2L2B' in smp:
            continue
        if '_tb_' in smp:
            p = smp.split('To2L2B_')[-1].split('_tb')[0].replace('p00','')
        else:
            p = smp.split('To2L2B_')[-1].replace('MH-', 'MH_').replace('MA-', 'MA_')
        if not p in points:
            points.append(p)
    return points


def get_histNm_orig(mode, hist_nm, mass=None, info=False, fix_reco_format=False):
    if not mode == 'dnn': prefix= mode
    else:
        if 'HToZA' in hist_nm: 
            prefix = 'DNNOutput_ZAnode'
            thdm = 'HToZA'
        else: 
            prefix= 'DNNOutput_ZHnode' 
            thdm = 'AToZH'
    
    heavy = thdm[0]
    light = thdm[-1]

    def returnIfExist(x, smp):
        if x in smp:
            return x
        else:
            return None

    dict_ = { 'flavor'  : [ 'ElEl','MuMu', 'MuEl', 'ElMu', 'OSSF'],
              'process' : ['gg_fusion', 'bb_associatedProduction'],
              'region'  : ['resolved', 'boosted'],
              'reco'    : ['nb2', 'nb3'],
              }
                
    opts = {}
    opts['mode'] = thdm
    for k, v in dict_.items():
        for opt in v:
            value = returnIfExist(opt, hist_nm) 
            if value is not None:
                opts[k] =  value
                continue
    
    if fix_reco_format:
        if 'nb2' in hist_nm:
            opts['process'] = 'gg_fusion'
        elif 'nb3' in hist_nm:
            opts['process'] = 'bb_associatedProduction'
   
    if mass is None:
        if fix_reco_format:
            mass = hist_nm.split('__')[0].split(opts['process']+'_')[-1]
        else:
            mass = hist_nm.split('__')[0].split('METCut_')[-1]

    m_heavy  = mass.split('_')[1]
    m_light  = mass.split('_')[3]

    prod     = opts['process'].split('_')[0] + heavy
    taggerWP = 'DeepFlavourM' if opts['region'] == 'resolved' else 'DeepCSVM'
    
    opts.update({'mass': mass, 'taggerWP': taggerWP, 'prod': prod, 'signal': '$%s: (m_{%s}, m_{%s})=(%s, %s) GeV$'%(prod, heavy, light, m_heavy, m_light)})
    
    if fix_reco_format:
        histNm  = f"{prefix}_{opts['flavor']}_{opts['region']}_{opts['taggerWP']}_METCut_{opts['process']}_M{heavy}_{mass_to_str(m_heavy)}_M{light}_{mass_to_str(m_light)}"
    else:
        histNm  = f"{prefix}_{opts['flavor']}_{opts['reco']}_{opts['region']}_{opts['taggerWP']}_METCut_M{heavy}_{mass_to_str(m_heavy)}_M{light}_{mass_to_str(m_light)}"

    if info:
        return histNm, opts
    else:
        return histNm


def no_extra_binedges(newEdges, oldEdges):
    cleanEdges = [] 
    newEdges   = newEdges.astype(float).round(2).tolist()
    oldEdges   = oldEdges.astype(float).round(2).tolist()
    for i, x in enumerate(newEdges):
        if not x in oldEdges:
            closest_value = min(oldEdges, key=lambda val:abs(val-x))
            #logger.warning(f'replacing {x} with the closest value : {closest_value} in oldEdges')
            x = closest_value
        if not x in cleanEdges:
            if i == 0: 
                cleanEdges.append(x)
            else:
                if x - cleanEdges[-1] != 0.02:
                    cleanEdges.append(x)
                else:
                    print(x, 'is a very narrow bin width will be removed ' )
    return cleanEdges


def no_zero_binContents(nph, newEdges, crossNm):
    FinalEdges  = newEdges
    edges       = np.array(newEdges)
    newHist     = nph.rebin(edges).fillHistogram(crossNm)
    np_newhist  = NumpyHist.getFromRoot(newHist)
    result      = np.array(np.where(np_newhist.w == 0.))[0]
    FinalEdges  = np.array(np.delete(edges, result))
    # keep bin boundaries should
    if not FinalEdges[0] == 0: FinalEdges = np.append([0], FinalEdges)
    if not FinalEdges[-1]== 1: FinalEdges = np.append(FinalEdges, [1])
    return  FinalEdges


def no_low_binContents(nph, newEdges, crossNm, thresh=6.):
    FinalEdges = newEdges
    edges      = np.array(newEdges)
    newHist    = nph.rebin(edges).fillHistogram(crossNm)
    np_newhist = NumpyHist.getFromRoot(newHist)
    still_below_thresh = any( x < thresh for x in np_newhist.w)
    
    i = 0
    while still_below_thresh:
        if any( x < thresh for x in np_newhist.w):
            result      = np.array(np.where(np_newhist.w < thresh))[0]
            result      = np.where(result == 0, 1, result)
            if len(result) >= 2:
                result  = np.where(result == len(result)+1, result[-2], result)
            FinalEdges  = np.delete(edges, result)
            
            logger.warning( f'full bin contents                : {np_newhist.w.tolist()}' )
            logger.warning( f'low bin contents below threshold : {result.tolist()}' )
            logger.warning( f'old edges                        : {newEdges.tolist()}, new edges: {FinalEdges.tolist()}' )
            
            edges      = np.array(FinalEdges)
            newHist    = nph.rebin(edges).fillHistogram(crossNm+f'_iter{i}')
            np_newhist = NumpyHist.getFromRoot(newHist)
            still_below_thresh = any( x < thresh for x in np_newhist.w)
            i +=1
    else: 
        return  np.array(FinalEdges)


def no_bins_empty_background_across_year(rf, histNm, newEdges, channel, crossNm):
    correctedEdges = newEdges
    logger.info(f'ULfullrun2 binning: {crossNm}, {correctedEdges}')
    if correctedEdges.tolist()== [0.,1.]:
        return correctedEdges
    for era in ['UL16', 'UL17', 'UL18', 'UL16preVFP', 'UL16postVFP']:
        rf_per_era = rf.replace('ULfullrun2', era)
        if not os.path.exists(rf_per_era):
            continue
        inFile   = HT.openFileAndGet(rf_per_era)
        hist     = inFile.Get(channel).Get(histNm)
        nph      = NumpyHist.getFromRoot(hist)
        correctedEdges = no_zero_binContents(nph, correctedEdges, crossNm)
        logger.info(f'{era} binning: {crossNm}, {correctedEdges}')
    return correctedEdges


def get_finalbins(hist, edges):
    FinalBins = []
    for x in edges:
        b = hist.FindBin(x)
        FinalBins.append(b)
    return FinalBins #list(set(FinalBins))


def get_bin_Content_and_Edges(hist):
    Nbins = hist.GetNbinsX()
    edges = [hist.GetXaxis().GetBinLowEdge(1)]
    bin_content = []
    errors = []
    for i in range(1,hist.GetNbinsX()+1):
        bin_content.append(hist.GetBinContent(i))
        edges.append(hist.GetXaxis().GetBinUpEdge(i))
        errors.append(hist.GetBinError(i))
    return bin_content, errors, edges, Nbins


def get_new_histogramWgt(hist=None, newEdges=None, oldEdges=None, verbose=False):
    oldNbins  = hist.GetNbinsX() 
    binContent= np.array([])
    binError  = np.array([])
    FinalBins = []
    for x in newEdges:
        b = hist.FindBin(x)
        FinalBins.append(b)
    
    nBins = len(newEdges) - 1 
    for newBinX in range(1, nBins+2):
        content = 0
        uncer   = 0 
        error   = 0
        maxOldBinX = FinalBins[newBinX] if newBinX <= nBins else oldNbins + 2
        if verbose:
            print("==="*20)
            print(f" merging bins {FinalBins[newBinX - 1]} -> {maxOldBinX}") 
        for oldBinX in range(FinalBins[newBinX - 1], maxOldBinX):
            content += hist.GetBinContent(oldBinX)
            error   += hist.GetBinError(oldBinX)
            
            if hist.GetBinContent(oldBinX) !=0 :
                uncer = round(hist.GetBinError(oldBinX)*100/hist.GetBinContent(oldBinX), 3)
            if verbose:
                print(f"\tGetting from bin {oldBinX }, content = {content}, error = {error}, uncer = {uncer}%") 
        
        binContent = np.append(binContent, content)
        binError   = np.append(binError, error)
    return binContent, binError, FinalBins


def bbbyields(hist):
    stat  = []
    uncer = []
    NBins = hist.GetNbinsX()
    for i in range(1, NBins + 1):
        content = hist.GetBinContent(i)
        error   = hist.GetBinError(i)
        stat.append(content)
        uncer.append(error)
    return stat, uncer


def optimizeUncertainty_(hist, l, thres, edges): # deprectaed /bugy
    cond = True
    dels = 0 
    num_bins = len(l)
    reversed_list = l[::-1]
    pos  = np.arange(len(l)+1)
    l    =np.array(reversed_list)
    while cond:
        indx = np.where(l < thres)[0]
        if len(indx) == 0:
            cond=False
            break
        cell = indx[0]
        if len(indx) == 1:
            if cell == 0 :
                l[cell-1] = l[cell-1]+ l[1]
            else:
                l[cell-1] = l[cell-1]+ l[cell]
        else:
            if cell == 0: cell = indx[1]
            l[cell-1] = l[cell-1]+ l[cell]
        
        mask = np.ones_like(l, dtype=bool)
        mask[cell] = False
        l = l[mask]
        cell += dels
        dels += 1
        pos[cell] = pos[dels -1 ]
   
    newpos = np.ones_like(pos)*(num_bins) - pos[::-1]
    newEdges_thres = []
    for p in newpos:
        if not edges[p] in newEdges_thres:
            newEdges_thres.append(edges[p])
    
    newBins_thres = get_finalbins(hist, newEdges_thres)
    return l, newEdges_thres, newBins_thres


def arr2root(old_hist=None, newEdges=None, include_overflow=False, verbose=False):
    np_arr_edges_oldhist = root_numpy.hist2array(old_hist, include_overflow=include_overflow, copy=False, return_edges=True)
    
    np_arr_oldhist = np_arr_edges_oldhist[0]
    oldEdges       = np_arr_edges_oldhist[1][0]
    
    np_arr_newhist = get_new_histogramWgt(old_hist, newEdges, oldEdges, verbose=verbose)[0]
    
    nBins = len(newEdges) 
    root_newhist = R.TH1D(old_hist.GetName(), old_hist.GetTitle(), nBins, np.append(newEdges, 1.02))
    newHist      = root_numpy.array2hist(np_arr_newhist, root_newhist)
    
    if abs(newHist.Integral() - hist.Integral()) > 0.001:
        logger.error( f'Yields new: {newHist.Integral()}, old: {hist.Integral()}, diff(new-old): {newHist.Integral()-hist.Integral()}' )
    return newHist


def normalizeAndSumSamples(inDir, outDir, inputs, era, scale=False):
    sorted_inputs= {'data'  :[],
                    'mc'    :[]}
    
    in_ = inDir.replace('results', '')
    plotter_p = outDir.split('work__UL')[0]

    if scale:
        file_ = os.path.join(in_, 'plots.yml')
        if not os.path.exists(file_):
            file_ = os.path.join(plotter_p, f'config_{era}.yml')
        if not os.path.exists(file_):
            logger.info(f'Sorry neither Bamboo plotIt  << plots.yml >> is found \n'
                        '\t\tneither << config_{year}.yml >> of Harvester.get_normalisationScale class, \n'
                        '\t\tthis is then gonna take sometime!\n')
            H.get_normalisationScale(inDir, method, era)
        
        with open(file_) as _f:
            Cfg = yaml.load(_f, Loader=yaml.FullLoader)
    
    for rf in inputs:
        isData = False
        smp    = rf.split('/')[-1]
        smpNm  = smp.replace('.root','')
        
        if smpNm.startswith('__skeleton__'):
            continue
        
        if not era == 'fullrun2':
            if not EraFromPOG(era) in smpNm:
                continue
        # just use the sum of data, will save you sometime
        if Cfg['files'][smp]["type"] =='mc':
            continue
        
        if scale: path = os.path.join(outDir, smp)
        else: path = rf 
        
        if any(x in smpNm for x in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon']):
            isData = True
            sorted_inputs['data'].append(path)
            #shutil.copyfile( os.path.join(inDir, smp), os.path.join(outDir, smp))
        else:
            if scale:
                year     = Cfg['files'][smp]["era"]
                lumi     = Cfg["configuration"]["luminosity"][year]
                xsc      = Cfg['files'][smp]["cross-section"]
                genevt   = Cfg['files'][smp]["generated-events"]
                smpScale = (lumi * xsc )/ genevt
            
            if any(x in smpNm for x in ['AToZHTo', 'HToZATo', 'GluGluToHToZATo', 'GluGluToAToZHTo']):
                if scale:
                    br = Cfg['files'][smp]["generated-events"]
                    smpScale *=br

                signal   = smpNm.split(f'_UL{EraFromPOG(era)}')[0]
                if not signal in sorted_inputs.keys():
                    sorted_inputs[signal] = []
                sorted_inputs[signal].append(path)
            else:
                sorted_inputs['mc'].append(path)
        
        if scale and not isData:
            print('working on scaling ::', smp)
            resultsFile    = HT.openFileAndGet(os.path.join(inDir, smp), mode="READ")
            normalizedFile = HT.openFileAndGet(os.path.join(outDir, smp), "recreate")
            for hk in resultsFile.GetListOfKeys():
                hist  = hk.ReadObj()
                #hist = resultsFile.Get(hk.GetName())
                if not hist.InheritsFrom("TH1"): 
                    continue
                hist.Scale(smpScale)
                hist.Write()
            normalizedFile.Write()
            resultsFile.Close()
    
    s   = 'scaled_' if scale else ''
    for k, val in sorted_inputs.items():
        if not val : continue
        if len(val) ==1: continue

        if  k in ['data', 'mc']: sum_f = f"summed_{s}{k}_UL{era}.root" 
        else: sum_f = f"{k}_UL{era}.root"

        haddCmd = ["hadd", "-f", os.path.join(outDir, sum_f)]+val
        try:
            logger.info("running {}".format(" ".join(haddCmd)))
            subprocess.check_call(haddCmd)#, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            logger.error("Failed to run {0}".format(" ".join(haddCmd)))
    


def WriteYamlForPlotIt(files, Cfg, era, outf, normalized):
    for root_f in files:
        color  = fake.hex_color()
        smp    = root_f.split('/')[-1]
        smpNm  = smp.split('.root')[0]
        smpEra = "20"+ smpNm.split('_UL')[-1]
        
        if not era == 'fullrun2':
            if not EraFromPOG(era) in smpNm:
                continue
        if 'VFP' in smpEra: smpEra = smpEra.replace('2016', '2016-')
        if 'VFP' in era: era = era.replace('2016', '2016-')
        
        print( smp )
        outf.write(f"  {smp}:\n")
        
        for gp, poss_f in sorted_files.items():
            if any(x in smp for x in poss_f):
                group = gp

        if normalized:
            if group != 'data':
                xsc    = Cfg['files'][smp]["cross-section"]
                genevt = Cfg['files'][smp]["generated-events"]
            outf.write(f"    era: {smpEra}\n")
                            
        if group == 'signal':
            outf.write(f"    type: signal\n")
            outf.write(f"    legend: '{get_legend(smpNm)}'\n")
            outf.write(f"    line-color: '{color}'\n")
            outf.write("    line-type: 1\n")
            if normalized:
                br = Cfg['files'][smp]["branching-ratio"]
                outf.write(f"    branching-ratio: {br}\n")
                outf.write(f"    generated-events: {genevt}\n")
                outf.write(f"    cross-section: {xsc} # pb\n")
        
        elif group =='data':
            outf.write(f"    type: data\n")
            outf.write(f"    group: {group}\n")
        else:
            newgroup = plotIt_mc_groups[group][0]
            legend   = plotIt_mc_groups[group][1]
            outf.write(f"    type: mc\n")
            outf.write(f"    group: {newgroup}\n")
            outf.write(f"    legend: {legend}\n")
            if normalized:
                outf.write(f"    generated-events: {genevt}\n")
                outf.write(f"    cross-section: {xsc} # pb\n")


def plotRebinnedHistograms(binnings, bambooDir, plotsDIR, era, normalized=True):
    lumi     = Constants.getLuminosity(era)
    bamboo_p = bambooDir.replace('results', '')
    with open(os.path.join(bamboo_p, 'plots.yml')) as _f:
        print(f"Will load normalisation  ( xsc, BR, sumgenEvts, lumi, etc ... ) from {os.path.join(bamboo_p, 'plots.yml')}")
        Cfg = yaml.load(_f, Loader=yaml.FullLoader)
    
    for j, process in enumerate(['gg_fusion', 'bb_associatedProduction']):
        
        _root  = os.path.join( binnings['root'], process)
        _files = glob.glob( os.path.join(_root, '*.root'))
        outDir = os.path.join(plotsDIR, 'plotit', process)
        if not os.path.exists(outDir):
            os.makedirs(outDir)
        
        with open(f"data/rebinned_template.yml", 'r') as inf:
            with open(f"{outDir}/plots.yml", 'w+') as outf:
                
                for line in inf:
                    if "  root: myroot_path" in line:
                        outf.write(f"  root: {_root}\n")
                    elif "files:" in line:
                        outf.write("files:\n")
                        WriteYamlForPlotIt(_files, Cfg, era, outf, normalized)
                    
                    elif "  no-lumi-rescaling:" in line:
                        no_lumi_rescaling = "false" if normalized else "true"
                        outf.write(f"  no-lumi-rescaling: {no_lumi_rescaling}\n")

                    elif "  luminosity: mylumi" in line:
                        if normalized:
                            if era =='fullrun2':
                                outf.write("  eras:\n")
                                for e in ['2016-preVFP', '2016-postVFP', '2017', '2018']:
                                    outf.write(f"  - {e}\n")
                                outf.write(f"  luminosity:\n")
                                for e in ['2016-preVFP', '2016-postVFP', '2017', '2018']:
                                    outf.write(f"    {e}: {Constants.getLuminosity(e)}\n")
                            else:
                                outf.write(f"  luminosity: {lumi}\n")
                        else:
                            outf.write(f"  luminosity: {lumi}\n")

                    elif "plots:" in line:
                        outf.write("plots:\n")
                        for plotNm in binnings['histograms'].keys():
                            params = get_histNm_orig('dnn', plotNm, mass=None, info=True, fix_reco_format=False)[1]
                            
                            outf.write(f"  {plotNm}:\n")
                            outf.write("    blinded-range: [0.6, 1.0]\n")
                            outf.write("    labels:\n")
                            outf.write("    - position: [0.22, 0.89]\n")
                            outf.write("      size: 20\n")
                            outf.write(f"      text: {params['region']}, {params['flavor']}\n")
                            outf.write("    legend-columns: 2\n")
                            outf.write("    log-y: both\n")
                            outf.write("    ratio-y-axis-range: [0.6, 1.4]\n")
                            outf.write("    save-extensions: [pdf, png]\n")
                            outf.write("    show-ratio: true\n")
                            outf.write("    sort-by-yields: false\n")
                            outf.write("    x-axis: DNN_Output Z{params['mode'][-1]} node\n")
                            outf.write("    x-axis-range:\n")
                            outf.write("    - 0.0\n")
                            outf.write("    - 1.0\n")
                            outf.write("    y-axis: Events\n")
                            outf.write("    y-axis-show-zero: true\n")
                    else:
                        outf.write(line)
            plotitCmd = ["/home/ucl/cp3/kjaffel/bamboodev/plotIt/plotIt", "-o", outDir, "--", f"{outDir}/plots.yml"]
            try:
                logger.info("running {}".format(" ".join(plotitCmd)))
                subprocess.check_call(plotitCmd)#, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                logger.error("Failed to run {0}".format(" ".join(plotitCmd)))
        print( f'\t{process} plots saved in : {outDir}')
