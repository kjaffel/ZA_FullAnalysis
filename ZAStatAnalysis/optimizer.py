#!/usr/bin/env python
# You may not need all of this, these are some my functions/craps to get things working in optimizeBinning.py
# using the bayesian blocks 
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

import Harvester as H
import HistogramTools as HT
import Constants as Constants
logger = Constants.ZAlogger(__name__)


def rebinmethods():
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


def get_sortedfiles(binnings, inputs, era):
    for rf in inputs:
        smpNm = rf.split('/')[-1].replace('.root','')
        if smpNm.startswith('__skeleton__'):
            continue
    
        if   'summed_data' in smpNm or 'summed_scaled_data' in smpNm: 
            binnings['files']['tot_obs_data'].append(rf)
        elif   'summed_mc' in smpNm or 'summed_scaled_mc' in smpNm: 
            binnings['files']['tot_b'].append(rf)
        elif   'summed_signal' in smpNm or 'summed_scaled_signal' in smpNm: 
            binnings['files']['tot_s'].append(rf)
        elif any(x in smpNm for x in ['AToZH', 'HToZA', 'GluGluTo']):
            binnings['files']['signal'].append(rf)
        elif any(x in smpNm for x in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleElectron', 'SingleMuon']):
            binnings['files']['data'].append(rf)
        elif any( x in smpNm for x in ['DYJetsToLL']):
            binnings['files']['mc']['DY'].append(rf)
        elif any( x in smpNm for x in ['TTTo2L2Nu', 'ttbar','TTToSemiLept']):
            binnings['files']['mc']['ttbar'].append(rf)
        elif any( x in smpNm for x in ['ST_']):
            binnings['files']['mc']['SingleTop'].append(rf)
        elif any( x in smpNm for x in ['ZZTo2L2Nu', 'ZZTo4L', 'ZZTo2L2Q']):
            binnings['files']['mc']['ZZ'].append(rf)
        elif any( x in smpNm for x in ['HZJ_HToWW_M125', 'ZH_HToBB_ZToLL_M125', 'ggZH_HToBB_ZToNuNu_M125', 'ggZH_HToBB_ZToLL_M125', 'ttHTobb', 'ttHToNonbb']):
            binnings['files']['mc']['ZZ'].append(rf)
        else:
            binnings['files']['mc']['others'].append(rf)
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


def get_histNm_orig(mode, smpNm, mass, info=False):
    if not mode == 'dnn': prefix= mode
    else:
        if 'HToZA' in smpNm: 
            prefix = 'DNNOutput_ZAnode'
            thdm = 'HToZA'
        else: 
            prefix= 'DNNOutput_ZAnode' # to fix later in the new production
            thdm = 'AToZH'

    heavy = thdm[0]
    light = thdm[-1]
    m_heavy = str(mass.split('_')[1]).replace('.', 'p')
    m_light = str(mass.split('_')[3]).replace('.', 'p')
    
    def returnIfExist(x, smp):
        if x in smp:
            return x
        else:
            return None

    dict_ = { 'flavor'  : [ 'ElEl','MuMu', 'MuEl', 'ElMu', 'OSSF'],
              'process' : ['gg_fusion', 'bb_associatedProduction'],
              'region'  : ['resolved', 'boosted'],
              #'taggerWP': ['DeepFlavourM', 'DeepCSVM'], 
              }
                
    opts = {}
    for k, v in dict_.items():
        for opt in v:
            value = returnIfExist(opt, smpNm) 
            if value is not None:
                opts[k] =  value
                continue

    taggerWP = 'DeepFlavourM' if opts['region'] == 'resolved' else 'DeepCSVM'
    opts.update({'mass': mass, 'taggerWP': taggerWP})
    
    histNm  = f"{prefix}_{opts['flavor']}_{opts['region']}_{opts['taggerWP']}_METCut_{opts['process']}_M{heavy}_{m_heavy}_M{light}_{m_light}"
    
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
                if x - cleanEdges[-1] != 0.01:
                    cleanEdges.append(x)
                else:
                    print(x, 'is a very narrow bin width will be removed ' )
    return cleanEdges


def get_finalbins(hist, edges):
    FinalBins = []
    for x in edges:
        b = hist.FindBin(x)
        FinalBins.append(b)
    return FinalBins


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
   
    oldNbins = hist.GetNbinsX() 
    
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


def EraFromPOG(era):
    return '_UL'+era.replace('20','')


def normalizeAndSumSamples(inDir, outDir, inputs, era, scale=False, doNeedData=False):
    s   = 'scaled_' if scale else ''
    in_ = inDir.replace('results', '')
    
    with open(os.path.join(in_, 'plots.yml')) as _f:
        Cfg = yaml.load(_f, Loader=yaml.FullLoader)

    sorted_inputs= {'data'  :[], 
                    'mc'    :[], 
                    }
    for rf in inputs:
        isData = False
        smp    = rf.split('/')[-1]
        smpNm  = smp.replace('.root','')
        
        if smpNm.startswith('__skeleton__'):
            continue
        
        if not era == 'fullrun2':
            if not EraFromPOG(era) in smpNm:
                continue

        year   = Cfg['files'][smp]["era"]
        lumi   = Cfg["configuration"]["luminosity"][year]

        if scale: path = os.path.join(outDir, smp)
        else: path = rf 
        
        if any(x in smpNm for x in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon']):
            if doNeedData:
                if scale:
                    shutil.copyfile( os.path.join(inDir, smp), os.path.join(outDir, smp))
                sorted_inputs['data'].append(path)
            isData = True
        else:
            xsc    = Cfg['files'][smp]["cross-section"]
            genevt = Cfg['files'][smp]["generated-events"]
            
            if any(x in smpNm for x in ['AToZHTo', 'HToZATo', 'GluGluTo']):
                
                br = Cfg['files'][smp]["generated-events"]
                
                smpScale = (lumi * xsc * br)/ genevt
                signal = smpNm.split('_UL')[0]
                
                if not signal in sorted_inputs.keys():
                    sorted_inputs[signal] = []
                sorted_inputs[signal].append(path)
            else:
                smpScale = (lumi * xsc )/ genevt
                sorted_inputs['mc'].append(path)
        
        if scale and not isData:
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
    
    for k, val in sorted_inputs.items():
        haddCmd = []
        if not val : continue
        if k in ['mc', 'data']:
            sum_f = f"summed_{s}{k}_samples_UL{era}.root"
            haddCmd = ["hadd", "-f", os.path.join(outDir, sum_f)]+val
        else: 
            # the rest are signal we dont want to hadd them all 
            # only the ones those belong to the same group like 2016 pre-/post-VFP signals
            if era == '2016':
                sum_f = val[0].replace('preVFP', '')
                haddCmd = ["hadd", "-f", os.path.join(outDir, sum_f)]+val
        
        if haddCmd:
            try:
                logger.info("running {}".format(" ".join(haddCmd)))
                subprocess.check_call(haddCmd)#, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                logger.error("Failed to run {0}".format(" ".join(haddCmd)))
    

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


def writeymlPlotter(files, kf, year, Cfg, outf, normalized):
    for root_f in files:

        color  = fake.hex_color()
        smp    = root_f.split('/')[-1]
        if normalized:
            year   = Cfg['files'][smp]["era"]
            lumi   = Cfg["configuration"]["luminosity"][year]
            xsc    = Cfg['files'][smp]["cross-section"]
            genevt = Cfg['files'][smp]["generated-events"]
            
        outf.write(f"  {smp}:\n")
        outf.write(f"    type: {kf}\n")
        if not kf=='signal': 
            outf.write(f"    group: {kf}\n")
        outf.write(f"    era: {year}\n")
                            
        if kf == 'signal':
            br = Cfg['files'][smp]["Branching-ratio"]
            
            outf.write(f"    legend: {smp.split('.root')[0]}\n")
            outf.write(f"    line-color: '{color}'\n")
            outf.write("    line-type: 1\n")
            if normalized:
                outf.write(f"    Branching-ratio: {br}\n")
                outf.write(f"    generated-events: {genevt}\n")
                outf.write(f"    cross-section: {xsc} # pb\n")
        elif kf == 'mc' and normalized:
            outf.write(f"    generated-events: {genevt}\n")
            outf.write(f"    cross-section: {xsc} # pb\n")


def plotRebinnedHistograms(binnings, inDir, folder, mode_, suffix, year, toysdata=False, normalized=False):
    
    with open(os.path.join(inDir, 'plots.yml')) as _f:
        Cfg = yaml.load(_f, Loader=yaml.FullLoader)
    lumiconfig = Cfg['configuration']
    print(lumiconfig) 
    
    if toysdata:
        plotsDIR = os.path.join(folder, 'bayesian_rebinned_on_toysdata')
        for pr in binnings['files']['toys']:
            smpNm = pr.split('/')[-1]
            mass  = 'MH_' + smpNm.split('_MH_')[-1] 
            pNm, infos = get_histNm_orig(mode_, smpNm, mass, info=True) 
            with open(f"data/bayesianblocks_rebin_withtoys_template.yml", 'r') as inf:
                with open(f"{pr}/plots.yml", 'w+') as outf:
                    for line in inf:
                        if '  root: myroot_path' in line:
                            outf.write(f"  root: {pr}\n")
                        elif '  myplot_Name:' in line:
                            outf.write(f"  {pNm}:\n")
                        elif '    legend: mysignal' in line:
                            outf.write(f"    legend: '{infos['mass']}'\n")
                        elif '      text: mychannel' in line:
                            outf.write(f"      text: {infos['region']}, {LATEX(infos['flavor'])}\n")
                        else:
                            outf.write(line)
            plotitCmd = ["/home/ucl/cp3/kjaffel/bamboodev/plotIt/plotIt", "-o", plotsDIR, "--", f"{pr}/plots.yml"]
            try:
                logger.info("running {}".format(" ".join(plotitCmd)))
                subprocess.check_call(plotitCmd)#, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                logger.error("Failed to run {0}".format(" ".join(plotitCmd)))
        print( f'\tplots saved in : {plotsDIR}')
    else:
        plotsDIR   = os.path.join(folder, "plotit")
        if not os.path.isdir(plotsDIR):
            os.makedirs(plotsDIR)
        
        with open(f"data/rebinned_template.yml", 'r') as inf:
            with open(f"{folder}/{suffix}/plots.yml", 'w+') as outf:
                for line in inf:
                    
                    if "  root: myroot_path" in line:
                        outf.write(f"  root: {folder}/{suffix}/\n")
                    elif "files:" in line:
                        outf.write("files:\n")
                        
                        for kf, vf in binnings['files'].items():
                            if not vf: continue
                            if kf == 'mc' :
                                for mc_k, mc_f in vf.items():
                                    writeymlPlotter(mc_f, mc_k, year, Cfg, outf, normalized)
                            else:
                                writeymlPlotter(vf, kf, year, Cfg, outf, normalized)
                    
                    elif "  - myera" in line:
                        for era, lumi in lumiconfig.items():
                            outf.write(f"  - {era}\n")
                    elif "    myera: mylumi" in line:
                        for era, lumi in lumiconfig.items():
                            outf.write(f"    {era}: {lumi}\n")
                    elif "  extra-label: myextralabel" in line:
                        if year =='2016': label = 'pre/-postVFP' 
                        else: label =  year
                        outf.write(f"  extra-label: {label} ULegacy Preliminary\n")

                    elif "plots:" in line:
                        outf.write("plots:\n")
                        for plotNm in binnings['histograms']:
                            infos  = plotNm.split('_')
                            flavor = infos[2].lower()
                            region = infos[3]
                            outf.write(f"  {plotNm}:\n")
                            outf.write("    blinded-range: [0.6, 1.0]\n")
                            outf.write("    labels:\n")
                            outf.write("    - position: [0.22, 0.895]\n")
                            outf.write("      size: 24\n")
                            outf.write(f"      text: {region}, {flavor}\n")
                            outf.write("    legend-columns: 2\n")
                            outf.write("    log-y: both\n")
                            outf.write("    ratio-y-axis-range: [0.6, 1.4]\n")
                            outf.write("    save-extensions: [pdf, png]\n")
                            outf.write("    show-ratio: true\n")
                            outf.write("    sort-by-yields: false\n")
                            outf.write("    x-axis: DNN_Output ZA node\n")
                            outf.write("    x-axis-range:\n")
                            outf.write("    - 0.0\n")
                            outf.write("    - 1.0\n")
                            outf.write("    y-axis: Events\n")
                            outf.write("    y-axis-show-zero: true\n")
                    else:
                        outf.write(line)
            plotitCmd = ["/home/ucl/cp3/kjaffel/bamboodev/plotIt/plotIt", "-o", plotsDIR, "--", f"{folder}/{suffix}/plots.yml"]
            try:
                logger.info("running {}".format(" ".join(plotitCmd)))
                subprocess.check_call(plotitCmd)#, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                logger.error("Failed to run {0}".format(" ".join(plotitCmd)))
    print( f'\tplots saved in : {plotsDIR}')
