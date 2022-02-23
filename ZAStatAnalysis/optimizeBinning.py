#!/usr/bin/env python
import argparse
import json, yaml
import glob
import os
import random
import itertools
import math
import shutil
import subprocess

from json import JSONEncoder
from collections import defaultdict
from hepstats.modeling.bayesian_blocks import bayesian_blocks, Prior
from astropy import visualization
from astropy import stats
from faker import Factory
fake = Factory.create()
from matplotlib import pyplot as plt
import root_numpy
import numpy as np
#from rootpy.plotting import Hist
import ROOT as R
R.gROOT.SetBatch(True)
import Harvester as H
import HistogramTools as HT
import Constants as Constants
import optimizer as optimizer
logger = Constants.ZAlogger(__name__)
from numpy_hist import NumpyHist
import Rebinning as Rb
import opt as opt

class MarkedList:
    _list = None
    def __init__(self, l):
        self._list = l

class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, MarkedList):
            return "##<{}>##".format(o._list)

def BayesianBlocksHybrid(oldHist=None, name=None, output=None, label=None, newEdges=None, include_overflow=False, doThreshold2=False, logy=False):
    
    oldEdges = {}
    np_w_oldhist = {}
    np_w_newhist = {}
   
    np_oldhist = {}
    np_newhist = {}
    newHist    = {}

    for k, v in oldHist.items():
        
        np_oldhist[k]   = NumpyHist.getFromRoot(v)
        np_w_oldhist[k] = np_oldhist[k].w
        oldEdges[k]     = np_oldhist[k].e
        
        newHist[k]      = np_oldhist[k].rebin(np.array(newEdges[k])).fillHistogram(v.GetName()+'_rebin_'+k)
        np_newhist[k]   = NumpyHist.getFromRoot(newHist[k])
        np_w_newhist[k] = np_newhist[k].w
        
        newHist['%s_hybride'%k]      = np_oldhist[k].rebin(np.array(newEdges['hybride'])).fillHistogram(v.GetName()+'_hybride')
        np_newhist['%s_hybride'%k]   = NumpyHist.getFromRoot(newHist['%s_hybride'%k])
        np_w_newhist['%s_hybride'%k] = np_newhist['%s_hybride'%k].w

    if doThreshold2:
        # list of ROOT TH1 for each of your processes (background and signals, or using a summed histogram)
        my_histograms = [ newHist['B_hybride']] 
        
        # fallback for main backgrounds, see net message, non main background we use 0, for signals we use np.inf
        stats = np.zeros(4)
        newHist['B_hybride'].GetStats(stats)
        fallbacks = [stats[1]/stats[0]]
        hybride_bins = optimizer.get_finalbins(oldHist['B'], newEdges['hybride'])
    
        if len( hybride_bins[:-1]) < 4:
            bins = [1, 3, 10, 18, 29, 37, 44, 45, 51]
        else:
            bins = hybride_bins[:-1]
    
        rebinObj = Rb.Threshold2(my_histograms, bins, fallbacks) # Initialize the rebinning object, the TH1 in  my_histograms have not changed
        rebinned_histograms = [rebinObj(hist)  for hist in my_histograms]
    
        newhist_with_thres_cut  = NumpyHist.getFromRoot(rebinned_histograms[0])
        newEdges_with_thres_cut = newhist_with_thres_cut.e
        newBins_with_thres_cut  = optimizer.get_finalbins(oldHist['B'], newEdges_with_thres_cut)
        print( 'new edges after threshold cut :: ', newEdges_with_thres_cut)
        print( 'new bin content after thresold cut ::', newhist_with_thres_cut.w) 
    

    fig = plt.figure(figsize=(12, 4), dpi=300)
    fig.subplots_adjust(left=0.1, right=0.95, bottom=0.15)
    
    for k, subplot in zip(['B', 'S'], [121, 122]):
        color = 'red' if k=='S' else 'blue'
        p0  = 0.1 if isSignal else 0.02
        ax = fig.add_subplot(subplot)

        ax.hist(oldEdges[k][:-1], bins=oldEdges[k], color=color, histtype='stepfilled', weights=np_w_oldhist[k],
                alpha=0.2, density=True, label=label)
        ax.hist(newEdges[k][:-1], bins=newEdges[k], color='black', weights=np_w_newhist[k],
                histtype='step', density=True, label=f"Bayesian blocks: prior = {'%.2f' % (float(p0))}")
        if logy:
            ax.set_yscale('log') 
        ax.legend(prop=dict(size=12), loc='best')
        ax.set_xlabel('DNN_output ZA')
        ax.set_ylabel('Probability density function')
    
    nm = name.replace('hybride_bininngS+B_bayesian_toys', 'data_obs_plus_signal')
    if logy:
        nm += '_logy'
    fig.savefig(os.path.join(output, nm+'.png')) 
    fig.savefig(os.path.join(output, nm+'.pdf'))
    plt.close(fig)
    plt.gcf().clear()


    fig = plt.figure(figsize=(12, 4), dpi=300)
    fig.subplots_adjust(left=0.1, right=0.95, bottom=0.15)
    for i, subplot in enumerate([121, 122]):
    
        ax = fig.add_subplot(subplot)
        if i ==0:
            ax.hist( oldEdges["B"][:-1], 
                    bins    = oldEdges["B"],  # they were the same (50 bins) for both 
                    color   = 'blue', 
                    weights = np_w_oldhist["B"], 
                    alpha=0.2, histtype= 'stepfilled', stacked=True, density=True, label='50 uniform bins: B-Only')
            ax.hist( oldEdges["S"][:-1], 
                    bins    = oldEdges["S"],  # they were the same (50 bins) for both 
                    color   = 'red', 
                    weights = np_w_oldhist["S"], 
                    alpha=0.2, histtype= 'stepfilled', stacked=True, density=True, label='50 uniform bins: S-Only')
            ax.hist(newEdges["B"][:-1], 
                    bins    = newEdges["B"], 
                    color   ='blue', 
                    weights = np_w_newhist["B"], 
                    histtype='step', stacked=True, density=True, fill=False, label=f"Bayesian blocks: B-Only")
            ax.hist(newEdges["S"][:-1], 
                    bins    = newEdges["S"], 
                    color   = 'red', 
                    weights = np_w_newhist["S"], 
                    histtype='step', stacked=True, density=True, fill=False, label=f"Bayesian blocks: S-Only")
            ax.hist(newEdges["hybride"][:-1], 
                    bins    = newEdges["hybride"], 
                    color   ='black', 
                    weights = np.sum([np_w_newhist["S_hybride"], np_w_newhist["B_hybride"]], axis=0), 
                    histtype='step', stacked=True, density=True, fill=False, label=f"Bayesian blocks: hybrid")
        else:
            ax.hist(newEdges["hybride"][:-1], 
                    bins    = newEdges["hybride"], 
                    color   ='blue',
                    weights = np_w_newhist["B_hybride"], 
                    alpha=0.2, histtype='stepfilled', stacked=True, density=True,label="BB-hybrid: Bkg")
            ax.hist(newEdges["hybride"][:-1], 
                    bins    = newEdges["hybride"], 
                    color   = 'red', 
                    weights = np_w_newhist["S_hybride"], 
                    alpha=0.2, histtype='stepfilled', stacked=True, density=True,label="BB-hybrid: Signal")
        #ax.hist(newEdges["B_safe_stat"], 
        #        bins    = newEdges["B_safe_stat"]+[1.], 
        #        color   = 'purple', 
        #        weights = np_arr_hybride["B_safe_stat"], 
        #        histtype='step', stacked=True, density=False, fill=False, label=f"Bayesian blocks: hybride +safe stat.")
        if logy:
            ax.set_yscale('log') 
        ax.legend(prop=dict(size=10), loc='best')
        ax.set_xlabel('DNN_output ZA')
        ax.set_ylabel('Probability density function')
    
    if logy:
        name += '_logy'
    fig.savefig(os.path.join(output, name+'.png')) 
    fig.savefig(os.path.join(output, name+'.pdf'))
    plt.close(fig)
    plt.gcf().clear()

    if doThreshold2:
        return newEdges_with_thres_cut.astype(float).round(2).tolist(), newBins_with_thres_cut
    else:
        return [], []

def FindPrior():
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


def BayesianBlocks(old_hist=None, mass=None, name=None, output=None, prior=None, cat='', datatype=None, label=None, logy=False, isSignal=False, doplot=False, dofind_bestPrior=False, include_overflow=False):
    """
    Bayesian Blocks is a dynamic histogramming method which optimizes one of
    several possible fitness functions to determine an optimal binning for
    data, where the bins are not necessarily uniform width.  
    The code below uses a fitness function suitable for event data with possible
    repeats.  More fitness functions are available: see :mod:`density_estimation`
    
    https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
    https://root.cern.ch/doc/master/classTH1.html#ae0895b66e993b9e9ec728d828b9336fe 
    np_arr_edges_oldhist = root_numpy.hist2array(old_hist, include_overflow=include_overflow, copy=True, return_edges=True)
    np_arr_oldhist = np_arr_edges_oldhist[0]
    oldEdges       = np_arr_edges_oldhist[1][0]
    
    """
    nph = NumpyHist.getFromRoot(old_hist)
    np_arr_oldhist = nph.w
    oldEdges       = nph.e
    
    oldNbins = old_hist.GetNbinsX() 
    
    print( "oldBinContents : ",  np_arr_oldhist, len(np_arr_oldhist))
    print( "oldEdges       : ",  oldEdges ,      len(oldEdges))


    priorDir = os.path.join(output, "prior")
    if not os.path.isdir(priorDir):
        os.makedirs(priorDir)

    if doplot:
        forthesis= False 
        color = 'red' if isSignal else 'blue' 
        p0  = 0.1 if isSignal else 0.02 
        pNm = datatype + '_' + name + '_bayesian_blocks'+ "_%.2f" %p0
        if forthesis: 
            fig = plt.figure(figsize=(8, 6))
            ax  = fig.add_subplot(111)
        else: 
            fig = plt.figure(figsize=(10, 4), dpi=300)
            fig.subplots_adjust(left=0.1, right=0.95, bottom=0.15)
        
        for i, (p0, subplot) in enumerate(zip([p0, p0+0.01], [121, 122])):
            
            print ( 'working on :', old_hist, pNm , p0)
            if forthesis:
                if i ==1: continue
            else: ax = fig.add_subplot(subplot)
            
            # this will protect me from exiting the bayesian blocks algo when bin content is 0. 
            #newEdges = stats.bayesian_blocks(oldEdges, np_arr_oldhist, fitness='measures', p0=p0, ncp_prior=None) 
            safe_arr = np.array([])
            for el in np_arr_oldhist:
                safe_arr = np.append(safe_arr, [el+1e-7])
            newEdges  = bayesian_blocks(oldEdges[:-1], safe_arr, p0=p0)
            newEdges  = optimizer.no_extra_binedges(newEdges, oldEdges)
            newEdges  = [float(format(e,'.2f')) for e in newEdges]
           
            if len( newEdges) <4:
                newEdges = [0.0, 0.1, 0.28, 0.68, 0.82, 0.9, 1.0] # [1, 6, 15, 35, 45, 51]
            else:
                newEdges  = newEdges[:-3] # merge last 3 bins: keep me safe from having bins with 0 to few bkg events also this will localize signal in 1 bin

            newHist = nph.rebin(np.array(newEdges+[1.0])).fillHistogram(old_hist.GetName()+name+"_%.2f"%p0)
            
            np_newhist     = NumpyHist.getFromRoot(newHist)
            np_arr_newhist = np_newhist.w
            newEdges       = np_newhist.e
            FinalBins      = optimizer.get_finalbins(old_hist, newEdges)
            
            if np_arr_newhist.sum() != 0. and abs(np_arr_newhist.sum()-np_arr_oldhist.sum())/np_arr_newhist.sum() > 1e-4:
                logger.warning("sum of binContents between 2 histogram does not match\n"
                                f"new = {np_arr_newhist.sum():.5e}, old = {np_arr_oldhist.sum():.5e}")
            
            ax.hist(oldEdges[:-1], bins=oldEdges, color=color, histtype='stepfilled', weights=np_arr_oldhist,
                    alpha=0.2, density=True, label=label)
            ax.hist(newEdges[:-1], bins=newEdges, color='black', weights=np_arr_newhist,
                    histtype='step', density=True, label=f"Bayesian blocks: prior = {'%.2f' % (float(p0))}")
            
            ax.legend(prop=dict(size=12))
            ax.set_xlabel('DNN_output ZA')
            ax.set_ylabel('Probability density function')
            if logy:
                ax.set_yscale('log') 
        
        if logy:
            pNm += '_logy'
        fig.savefig(os.path.join(priorDir, pNm+'.png')) 
        fig.savefig(os.path.join(priorDir, pNm+'.pdf'))
        plt.close(fig)
        plt.gcf().clear()
        print(f" plots saved in : {output}" )
    print( newEdges, FinalBins ) 
    return newHist, newEdges, FinalBins

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

def optimizeBinning(hist, maxEvents, maxUncertainty, acceptLargerOverFlowUncert=True):
    """ Optimize binning, return result in the form of:
        (list of edges, list of bin numbers of original histo)
        args:
            - acceptLargerOFlowUncert: if false, will always merge overflow with previous bin
                                        to ensure the overflow uncertainty is below the threshold
    bin = 0; underflow bin
    bin = 1; first bin with low-edge xlow INCLUDED
    bin = nbins; last bin with upper-edge xup EXCLUDED
    bin = nbins+1; overflow bin
    GetSum
    GetSumOfWeights
    GetSumw2
    GetSumw2N
    """
    # Find first bin with non-zero content
    startBin = 0
    NBins = hist.GetNbinsX()
    for i in range(0, NBins + 1):
        if hist.GetBinContent(i) == 0:
            startBin += 1
        else:
            break
    print(f"New start bin: {startBin}, BinContent: {hist.GetBinContent(startBin)}")

    binContents = list(hist)
    binSumW2    = list(hist.GetSumw2()) # Total Sum of squares of weights
    finalBins   = [startBin] # array [i j k ...] -> bin 1 in new histo = bins i ... j-1 in old one, etc.

    upEdge = startBin
    mergeLastBin = False
    newEdges = []
    uncertainties =[]
    while upEdge <= NBins + 1:
        content     = 0 
        sumw2       = 0
        uncertainty = 0
        yields      = 0.5
        print( '='*30)
        #print( f'BinError= {hist.GetBinError(upEdge)}, BinContent= {hist.GetBinContent(upEdge)}, {hist.GetSumw2(upEdge)}')
        # This is my threshold:"having at least a yield (i.e. sum of weights in the bin) of 1 for the background 
        #                       and 1 for the signal, 
        #                       plus having statistical uncertainty in both of at least maxUncertainty*100 % "
        if hist.Integral(upEdge, upEdge+1) !=0:
            population = binContents[upEdge]/hist.Integral(upEdge, upEdge+1)
        # bins does not satisfiy my thresholdes, start merging , until they do :p 
        print( f'bin {upEdge} :  stat.uncer =  {np.sqrt(binSumW2[upEdge]) / binContents[upEdge]}, yield = {population}')
        while uncertainty < maxUncertainty:# or population < yields: # content < maxEvents:
            if upEdge == NBins + 2:
                # we've now included the overflow bin without going below the required uncertainty
                # -> stop and make sure we merge last bin with next-to-last one
                mergeLastBin = True
                break
            content += binContents[upEdge]
            sumw2   += binSumW2[upEdge]
            if content != 0:
                uncertainty = np.sqrt(sumw2) / content
            lowedge = hist.GetXaxis().GetBinLowEdge(upEdge)
            print( f'\tbin:{upEdge} lowedge:%.2f ==> unc= {uncertainty}, cont= {content}, sumw2= {sumw2}'%lowedge)
            upEdge += 1
        # We now have the new binning. Find the lower edges it corresponds to.
        newEdges.append(hist.GetXaxis().GetBinLowEdge(upEdge))
        uncertainties.append( uncertainty)
        finalBins.append(upEdge)
    
    # The last bin will correspond to the overflow bin so we don't include it explicitly in the edges
    #del newEdges[-1]
    #if mergeLastBin and acceptLargerOverFlowUncert:
    #    del finalBins[-2]
    print(f"New binning == >  newEdges = {newEdges} ,  finalBins = {finalBins}")
    return newEdges, finalBins, uncertainties


def rebinCustom(hist, binning, name, verbose=False):
    """ Rebin 1D hist using bin numbers and edges as returned by optimizeBinning() """
    
    edges = binning[0]
    nBins = len(edges) - 1
    oldNbins = hist.GetNbinsX()
    print( f'processing ::: name: {name}, Title: {hist.GetTitle()}, nbinsx: {nBins}, xlow, xup : {np.array(edges)}, FinalBins: {binning[1]}' )
    
    newHist  = R.TH1D(name, hist.GetTitle(), nBins, np.array(edges))
    newHist.Sumw2()
    oldSumw2 = list(hist.GetSumw2())
    sumOfWeightsGenerated = 0
    
    for newBinX in range(1, nBins+2):
        content = 0
        sumw2   = 0
        maxOldBinX = binning[1][newBinX] if newBinX <= nBins else oldNbins + 2
        for oldBinX in range(binning[1][newBinX - 1], maxOldBinX):
            content += hist.GetBinContent(oldBinX)
            sumw2   += oldSumw2[hist.GetBin(oldBinX)]
        if verbose:
            print( f'merging bins {binning[1][newBinX-1]} ({hist.GetXaxis().GetBinLowEdge(binning[1][newBinX-1])})\n'
                   f'-> {maxOldBinX} ({hist.GetXaxis().GetBinLowEdge(maxOldBinX)}) : BinContent = {content}\n')
        newHist.SetBinContent(newBinX, content)
        newHist.GetSumw2()[newHist.GetBin(newBinX)] = sumw2
        sumOfWeightsGenerated += content
    
    if abs(newHist.Integral() -hist.Integral()) > 0.001:
        logger.error( f'Yields new: {newHist.Integral()}, old: {hist.Integral()}' )
    return newHist, sumOfWeightsGenerated

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Collection of functions to get the best binning')
    parser.add_argument('-i', '--input', help='input file, either toys data or bamboo output files', required=True)
    parser.add_argument('-o', '--output', help='output dir', required=True)
    parser.add_argument('--era', help='era', required=True)
    parser.add_argument('--uncertainty', type=float, default=0.3, help='max stat. uncertainty')
    parser.add_argument('--events', type=float, default=10e2, help='max entries in bins')
    parser.add_argument('-p0', '--prior', type=float, default=0.05, 
                            help='false positive probability: the relative\n'
                                 'frequency with which the algorithm falsely reports detection of a\n'
                                 'change-point in data with no signal present.\n')
    parser.add_argument('--scale', action='store_true', default=False, help=' scale histograms before start rebining')
    parser.add_argument('--toys', action='store_true', default=False, help=' use toys data')
    parser.add_argument('--plotit', action='store_true', default=False, help=' do plots after rebining')
    parser.add_argument('--onlypost', action='store_true', default=False, 
                            help=' useful to set to True when the changes is only at the plotting stage')
    parser.add_argument('--logy', action='store_true', default=False, help=' produce plots in log scale')
    parser.add_argument('--sys', action='store_true', default=False, help=' produce rebinned systematic histograms')
    parser.add_argument('--mode', action='store', required=True, choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'mjj', 'mlljj', 'rho', 'dnn'], help='Analysis mode')
    parser.add_argument('--submit', action='store', default='test', choices=['all', 'test'],
                            help='submit all or just pass test, useful when small modification is need for plotting\n'
                                 'without a need to touch the histogram again\n')
    parser.add_argument('--normalized', action='store_true', default=False, 
                            help= 'rebinned plotit-plots can be normalized to 1pb')
    parser.add_argument('--rebin', action='store', choices= ['custom', 'standalone', 'bayesian'], required=True, 
                            help='compute new binning by setting some treshold on the uncer and number of events\n'
                                 'or just re-arrange the oldbins to merge few bins into one, starting from the left to the right\n')
    parser.add_argument('--scenario', action='store', choices= ['hybride', 'S', 'B', 'BB_hybride_good_stat'], required=False, 
                            help='')
    
    args = parser.parse_args()
    try:
        shutil.copyfile(os.path.join(args.input, 'plots.yml'), os.path.join(args.output, 'plots.yml'))
    except shutil.SameFileError: 
        pass
    
    keep_bins = [1, 3, 9, 21, 39, 51, 52] # accept overflow  
    sumPath   = "summed_scaled_histogramms" if args.scale else "summed_histogramms"
    mode_     = 'DNNOutput_ZAnode' if args.mode =='dnn' else args.mode
    suffix    = f"{args.rebin}_rebin_on_{args.scenario}/results"
    suff      = f'_all_on_{args.scenario}' if args.submit=='all' else '_template'

    inDir  = os.path.join(args.input, 'results/')
    list_inputs = glob.glob(os.path.join(inDir, '*.root'))
    
    if not inDir:
        logger.warning(f'No Bamboo inputs found in : {inDir}')
    
    
    plotsDIR = os.path.join(args.output, "plots")
    if not os.path.isdir(plotsDIR):
        os.makedirs(plotsDIR)
    
    # normalize and sum samples
    outDir = os.path.join(args.output, 'inputs/')
    if not args.toys: # no need to merge files
        if not os.path.isdir(outDir):
            os.makedirs(outDir)
            if not os.path.isdir(os.path.join(outDir, sumPath)):
                os.makedirs(os.path.join(outDir, sumPath))
                optimizer.normalizeAndSumSamples(inDir, outDir, sumPath, list_inputs, args.era, args.scale)
        else:
            logger.info(f'{outDir}/ already exist and not empty!\n'
                        '\tScale and hadd steps will be skipped \n'
                        '\tif you have an updated version of files OR you want to rerun the steps above :\n'
                       f'\tplease remove {outDir}/ and start over!\n' )
        
    if args.onlypost:
        inputs = [] # don not process anything , just go to the plotter
    else:
        if args.submit=='all':
            # bkg , data and signal as it is given/found in the args.inputs
            if args.scale:
                inputs = glob.glob(os.path.join(outDir, '*.root'))
            else:
                inputs= list_inputs
            try:
                f = open(os.path.join(args.output, f"rebinned_edges_{args.rebin}_template.json"))
                data = json.load(f)
            except Exception as ex:
                raise RuntimeError(f' -- {ex} occure when reading rebinned_edges_{args.rebin}_template.json')
        else:
            if args.toys:
                # take toys data 
                inDir  = os.path.join(args.input, f'generatetoys-/{args.mode}/*')
                inputs = glob.glob(os.path.join(inDir, '*_shapes.root'))
            else:
                # take pseudo-data: sum of all bkg 
                inputs = glob.glob(os.path.join(outDir, sumPath, '*.root'))
                for x in ['AToZH', 'HToZA', 'GluGlu']:
                    inputs += glob.glob(os.path.join(inDir, x, '*.root'))

    binnings = {
            'files': {
                    'tot_b'       : [],
                    'tot_s'       : [],
                    'tot_obs_data': [],
                    'toys'     : [],
                    'signal'   : [],
                    'data'     : [],
                    'mc': {
                        'DY': [],
                        'ttbar'    : [],
                        'SingleTop': [],
                        'ZZ'       : [],
                        'SM'       : [],
                        'others'   : []}
                    },
            'histograms':{}
            }
    binnings = optimizer.get_sortedfiles(binnings, inputs, args.era)
    
    
    if args.toys:
        for rf in inputs:
            smpNm = rf.split('/')[-1].split('_shapes')[0]
            if 'boosted' in smpNm:
                if not '_ElEl_MuMu_' in smpNm: continue # for boosted cat, accept only merged flavor , because of the lack of stat
            
            out_  = os.path.join(args.output, f'{args.rebin}_rebin_on_toysdata/{smpNm}')
            if not os.path.isdir(out_):
                os.makedirs(out_)
            
            binnings['files']['toys'].append(out_)
            channels = set()
            inFile  = HT.openFileAndGet(rf)
            for k in inFile.GetListOfKeys():
                cat = k.GetName()
                if not cat.startswith(args.mode):
                    continue
                channels.add(cat)
            channels = list(channels)
            print ("Detected channels: ", channels )
            
            for channel in channels:
                oldHist   = {}
                newHist   = {} 
                newEdges  = {}
                oldEdges  = {}
                oldNbins  = {}
                FinalBins = {}
                newBinErrors  = {}
                oldBinErrors  = {}
                oldBinContent = {}

                mass = channel.replace(f'{args.mode}_', '')
                histNm = optimizer.get_histNm_orig(mode_, smpNm, mass, info=False)
                binnings['histograms'][histNm] = {}
                
                for key in inFile.Get(channel).GetListOfKeys():
                    
                    isSignal  = False
                    isData    = False
                    if key.GetName().startswith('HToZATo2L2B'): isSignal=True
                    if 'data' in key.GetName(): isData=True 

                    k = 'S' if isSignal else ('B' if isData else(key.GetName()))
                    if not (isData or isSignal):
                        continue
                    oldHist[k] = inFile.Get(channel).Get(key.GetName())
                    
                    if not oldHist[k]:
                        logger.error('could not find object: inFile.Get({channel}).Get({key.GetName()}) -- return null pointer!')
                    print( f' working on : {key.GetName()}' ) 
                    
                    label  = mass if isSignal else 'B-Only toy data'
                    datatype = 'signal' if isSignal else key.GetName()
                   
                    np_hist = NumpyHist.getFromRoot(oldHist[k])
                    oldBinContent[k] = np_hist.w
                    oldBinErrors[k]  = np_hist.s
                    oldEdges[k]      = np_hist.e

                    newHist[k], newEdges[k], FinalBins[k] = BayesianBlocks( old_hist          = oldHist[k], 
                                                                            mass              = mass, 
                                                                            name              = histNm,
                                                                            output            = plotsDIR, 
                                                                            prior             = args.prior, 
                                                                            datatype          = datatype, 
                                                                            label             = label,
                                                                            logy              = args.logy, 
                                                                            isSignal          = isSignal, 
                                                                            doplot            = True,
                                                                            dofind_bestPrior  = False,
                                                                            include_overflow  = False)
                
                newEdges['B'] = newEdges['B'].astype(float).round(2).tolist()
                newEdges['S'] = newEdges['S'].astype(float).round(2).tolist()
                binning  = optimizer.hybride_binning( BOnly = [newEdges['B'], FinalBins['B']], 
                                            SOnly = [newEdges['S'], FinalBins['S']] )

                
                hybridebinning_dict = {'B': newEdges['B'],
                                       'S': newEdges['S'],
                                       'hybride': binning[0]}
                newEdges_with_thres_cut, newBins_with_thres_cut = BayesianBlocksHybrid(
                                oldHist, 
                                name                  = 'hybride_bininngS+B_bayesian_toys' + '_' + smpNm, 
                                output                = plotsDIR, 
                                label                 = label,
                                newEdges              = hybridebinning_dict, 
                                include_overflow      = False, 
                                logy                  = args.logy)

                binnings['histograms'][optimizer.get_histNm_orig(mode_, smpNm, mass, info=False)].update(
                           {'B': [MarkedList(newEdges['B']), MarkedList(FinalBins['B']) ],
                            'S': [MarkedList(newEdges['S']), MarkedList(FinalBins['S']) ],
                            'hybride': [MarkedList(binning[0]), MarkedList(binning[1])],
                            'BB_hybride_good_stat': [MarkedList(newEdges_with_thres_cut), MarkedList(newBins_with_thres_cut)],
                        })

            inFile.Close()
    else:
    
        if not os.path.isdir(os.path.join(args.output, suffix)):
            os.makedirs(os.path.join(args.output, suffix))
        
        if args.submit=='all':
            mc = []
            for group, bkg in binnings['files']['mc'].items():
                if not bkg: continue
                mc += bkg
            files = binnings['files']['signal']+ mc + binnings['files']['data']
        else:
            files= binnings['files']['signal']+ binnings['files']['tot_b']

        Observation = {}
        for rf in files:
            smpNm = rf.split('/')[-1].replace('.root','')
            Observation[smpNm] = {}

            print( f'==='*40) 
            print( f' working on : {rf}' ) 
            rf_out  = os.path.join(args.output, suffix, f"{smpNm}.root")
            inFile  = HT.openFileAndGet(rf)
            outFile = HT.openFileAndGet(rf_out, "recreate")

            for key in inFile.GetListOfKeys():
                isSys = False
                if not key.GetName().startswith(mode_):
                    continue
                               
                if '__' in key.GetName(): isSys=True
                if not args.sys and isSys: 
                    continue
                
                if 'gg_fusion' in key.GetName(): process = 'gg_fusion'
                else: process = 'bb_associatedProduction' 
               
                mass = key.GetName().split(process+'_')[-1].split('__')[0]
                sig = mass.replace('MH_', 'MH-').replace('MA_', 'MA-')
                params = optimizer.get_histNm_orig(mode_, key.GetName(), mass, info=True)[1]
               
                # do not focus on these for now
                if mass == 'MH_609p21_MA_253p68':
                    continue
                if params['process'] == 'bb_associatedProduction':
                    continue
                if params['taggerWP'] == 'DeepFlavourM':
                    continue
                if params['region'] == 'boosted':
                    continue
                if params['flavor'] == 'MuEl':
                    continue
                
                if not mass in optimizer.available_points(inputs):
                    continue
                
                hist = inFile.Get(key.GetName())
                if not (hist and hist.InheritsFrom("TH1")):
                    continue
                
                oldHist = inFile.Get(key.GetName())
                
                if not isSys:
                    channel = f"{args.mode}_{mass}_{params['process']}_{params['region']}_{params['flavor']}_{params['taggerWP']}"
                    Observation[smpNm][channel] = []
                    binnings['histograms'][key.GetName()] = []
                    if not key.GetName() in binnings['histograms']:
                        binnings['histograms'].append(key.GetName())
                
                print( f' working on : {key.GetName()}' ) 
                name = key.GetName() +'_rebin'
                if args.rebin == 'custom':
                    binning = optimizeBinning(oldHist, args.events, args.uncertainty)
                    newEdges= binning[0]
                    newHist, sumOfWeightsGenerated = rebinCustom(oldHist, binning, oldHist.GetName())
                    name   += '_custome'

                elif args.rebin == 'standalone':
                    newEdges = []
                    for i in keep_bins:
                        newEdges.append(oldHist.GetXaxis().GetBinLowEdge(i))
                    binning  = [newEdges, keep_bins]
                    newHist, sumOfWeightsGenerated  =  rebinCustom(oldHist, binning, oldHist.GetName())
                    name    += '_standalone'
                
                elif args.rebin == 'bayesian':
                    # sys hist should have the same bins as nominal && the same for the flavors 
                    # otherwise you won't be able to combine the datacards
                    #!! binning  = data['histograms'][key.GetName().split('__')[0].replace(params['flavor'],'MuMu')]['args.scenario']
                    
                    if params['flavor'] == 'MuEl': # this channel  will help to control ttbar
                        binning  = data['histograms'][key.GetName().split('__')[0]]['B']
                    else:
                        binning  = data['histograms'][key.GetName().split('__')[0]][args.scenario]
                    
                    nph_old = NumpyHist.getFromRoot(oldHist)
                    newHist = nph_old.rebin(np.array(binning[0])).fillHistogram(oldHist.GetName()) 
                    nph_new = NumpyHist.getFromRoot(newHist)
                    if nph_new.w.sum() != 0. and abs(nph_new.w.sum()-nph_old.w.sum())/nph_new.w.sum() > 1e-4:
                        logger.warning("sum of binContents between 2 histogram does not match\n"
                                      f"new = {nph_new.w.sum():.5e}, old = {nph_old.w.sum():.5e}")
                   
                    Observation[smpNm][channel].append(newHist.Integral())
                
                if not isSys:
                    binnings['histograms'][key.GetName()].append([MarkedList(binning[0]), MarkedList(binning[1])])
                
                #print(np.sqrt(sum(list(newHist.GetSumw2())))/newHist.Integral())
                outFile.cd()
                newHist.Write()
            inFile.Close()
            outFile.Close()
            print(' rebinned histogram saved in: {} '.format(os.path.join(args.output, suffix, f"{smpNm}.root")))
    
        optimizer.get_yields(Observation)
    
    if not args.onlypost: 
        with open(os.path.join(args.output, f"rebinned_edges_{args.rebin}{suff}.json"), 'w') as _f:
            b = json.dumps(binnings, indent=2, separators=(',', ':'), cls=CustomJSONEncoder)
            b = b.replace('"##<', "").replace('>##"', "")
            _f.write(b)
        print(' rebinned template saved in : {} '.format(os.path.join(args.output, f"rebinned_edges_{args.rebin}{suff}.json")))
        
    if args.plotit:
        if args.onlypost:
            f = open(os.path.join(args.output, f"rebinned_edges_{args.rebin}{suff}.json"))
            binnings = json.load(f)
        optimizer.plotRebinnedHistograms(binnings, inDir, args.output, mode_, suffix, args.era, args.toys, normalized=args.normalized)
