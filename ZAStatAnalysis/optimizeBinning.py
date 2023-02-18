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
import root_numpy

import numpy_hist as numpy_hist

#from rootpy.plotting import Hist
from numpy_hist import NumpyHist
from json import JSONEncoder
from collections import defaultdict
from hepstats.modeling.bayesian_blocks import bayesian_blocks, Prior
from astropy import visualization
from astropy import stats
from faker import Factory
fake = Factory.create()
from matplotlib import pyplot as plt

import numpy as np
import ROOT as R
R.gROOT.SetBatch(True)

import Harvester as H
import HistogramTools as HT
import optimizer as optimizer
import Constants as Constants
logger = Constants.ZAlogger(__name__)
import utils.CMSStyle as CMSStyle
import Rebinning as Rb


class MarkedList:
    _list = None
    def __init__(self, l):
        self._list = l


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, MarkedList):
            return "##<{}>##".format(o._list)


def BayesianBlocksHybrid(oldHist, name, output, label, newEdges, include_overflow=False, doThreshold2=False, logy=False):
    
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
    
        #if len( hybride_bins[:-1]) < 4:
        #    bins = [1, 3, 10, 18, 29, 37, 44, 45, 51]
        #else:
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
        p0    = 0.1 if isSignal else 0.02
        
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
    #fig.savefig(os.path.join(output, nm+'.pdf'))
    plt.close(fig)
    plt.gcf().clear()

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
        # not in use!
        #ax.hist(newEdges["B_safe_stat"], 
        #        bins    = newEdges["B_safe_stat"]+[1.], 
        #        color   = 'purple', 
        #        weights = np_arr_hybride["B_safe_stat"], 
        #        histtype='step', stacked=True, density=False, fill=False, label=f"Bayesian blocks: hybride +safe stat.")
        if logy:
            ax.set_yscale('log')
            #ax.set_ylim([10e-4, 10e3])
        ax.legend(prop=dict(size=10), loc='best')
        ax.set_xlabel('DNN_output ZA')
        ax.set_ylabel('Probability density function')
    
    if logy:
        name += '_logy'
    
    fig.savefig(os.path.join(output, name+'.png')) 
    #fig.savefig(os.path.join(output, name+'.pdf'))
    plt.close(fig)
    plt.gcf().clear()

    if doThreshold2:
        return newEdges_with_thres_cut.astype(float).round(2).tolist(), newBins_with_thres_cut
    else:
        return [], []


def BayesianBlocks(root_file, old_hist, mass, name, channel, output, prior, datatype, label, logy=False, isSignal=False, doplot=False, dofind_bestPrior=False, include_overflow=False):
    """
    Bayesian Blocks is a dynamic histogramming method which optimizes one of
    several possible fitness functions to determine an optimal binning for
    data, where the bins are not necessarily uniform width.  
    The code below uses a fitness function suitable for event data with possible
    repeats.  More fitness functions are available: see :mod:`density_estimation`
    
    useful ref :
        - https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
        - https://root.cern.ch/doc/master/classTH1.html#ae0895b66e993b9e9ec728d828b9336fe 
    
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
        color = 'red' if isSignal else 'blue' 
        p0    = 0.1 # the larger the number of bins, the small the P0 should be to prevent the creation of spurious, jagged bins.
        
        fig   = plt.figure(figsize=(10, 4), dpi=300)
        fig.subplots_adjust(left=0.1, right=0.95, bottom=0.15)
        
        for i, (p0, subplot) in enumerate(zip([p0, p0+0.02], [121, 122])):
            
            pNm   = datatype + '_' + name + '_bayesian_blocks'+ "_%.2f" %p0
            print ( 'working on :', old_hist, pNm , p0)
            
            ax    = fig.add_subplot(subplot)
            CMSStyle.applyStyle(fig, ax, Constants.getLuminosity(args.era), figures=1)
            
            # this will protect me from exiting the bayesian blocks algo when bin content is 0. 
            safe_arr = np.array([])
            for elem in np_arr_oldhist:
                safe_arr = np.append(safe_arr, [elem+1e-7])
            # reduce importance of stats. 
            if not isSignal and 'nb2' in name and 'resolved' in name:
                safe_arr = np.divide(safe_arr, 100.)
                print( 'reduce stat by /100.:', safe_arr )
            
            #newEdges = stats.bayesian_blocks(oldEdges, np_arr_oldhist, fitness='measures', p0=p0, ncp_prior=None) 
            newEdges  = bayesian_blocks(oldEdges[:-1], safe_arr, p0=p0)
            newEdges  = optimizer.no_extra_binedges(newEdges, oldEdges)
            newEdges  = [float(format(e,'.2f')) for e in newEdges]
            
            #if 'signal' in datatype and len( newEdges) <= 2:
            #    newEdges = [0.0, 0.74, 0.94, 0.96, 1.0]
            #if 'data' in datatype and 'boosted' in pNm:
            #    newEdges = newEdges[0:1]+newEdges[3:] 
            # merge last 2 bins: keep me safe from having bins with 0 to few bkg events also this will localize signal in 1 bin
            #newEdges   = newEdges[:-2] 
            
            if 0.98 in newEdges: newEdges.remove(0.98)
            if not 1.0 in newEdges: FinalEdges = newEdges+[1.0]
            else: FinalEdges = newEdges
            
            crossNm     = old_hist.GetName()+name+"_crossCheck_%.2f"%p0
            FinalEdges  = optimizer.no_zero_binContents(nph, FinalEdges, crossNm) 
            if not isSignal:
                FinalEdges  = optimizer.no_bins_empty_background_across_year(root_file, old_hist.GetName(), FinalEdges, channel, crossNm)
            
            _newHist        = nph.rebin(FinalEdges).fillHistogram(old_hist.GetName()+name+"_%.2f"%p0)
            np_newhist      = NumpyHist.getFromRoot(_newHist)
            np_arr_newhist  = np_newhist.w
            _newEdges       = np_newhist.e
            _newBins        = optimizer.get_finalbins(old_hist, FinalEdges)
            
            if np_arr_newhist.sum() != 0. and abs(np_arr_newhist.sum()-np_arr_oldhist.sum())/np_arr_newhist.sum() > 1e-4:
                logger.warning("sum of binContents between 2 histogram does not match\n"
                                f"new = {np_arr_newhist.sum():.5e}, old = {np_arr_oldhist.sum():.5e}")
            
            ax.hist(oldEdges[:-1], bins=oldEdges, color=color, histtype='stepfilled', weights=np_arr_oldhist,
                    alpha=0.2, density=True, label=label)
            ax.hist(_newEdges[:-1], bins=_newEdges, color='black', weights=np_arr_newhist,
                    histtype='step', density=True, label=f"Bayesian blocks: prior = {'%.2f' % (float(p0))}")
            
            ax.legend(prop=dict(size=10), loc='best')
            ax.set_xlabel('DNN_output ZA')
            ax.set_ylabel('Probability density function')
            #ax.set_ylim([10e-4, 10e3])
            if logy:
                ax.set_yscale('log') 
        
        if logy:
            pNm += '_logy'
        
        fig.savefig(os.path.join(priorDir, pNm+'.png')) 
        #fig.savefig(os.path.join(priorDir, pNm+'.pdf'))
        plt.close(fig)
        plt.gcf().clear()
        print(f" plots saved in : {output}" )
    
    print( "newBinContents : ",  np_arr_newhist, len(np_arr_newhist))
    print( "newEdges       : ",  _newEdges , len(_newEdges))
    print( "newBins        : ",  _newBins, len(_newBins))
    print( "==================="*6)
    return _newHist, _newEdges, _newBins


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
    
    newHist  = R.TH1D(name, hist.GetTitle(), nBins, np.array(edges))
    newHist.Sumw2()
    oldSumw2 = list(hist.GetSumw2())
    sumOfWeightsGenerated = 0
    
    print( f'processing ::: nbinsx: {nBins} \n' 
                           f'xlow, xup : {np.array(edges)}\n' 
                           f'oldSumw2  : {oldSumw2} \n'
                           f'FinalBins : {binning[1]}\n' )
    
    for newBinX in range(1, nBins+1):
        content = 0
        sumw2   = 0
        maxOldBinX = binning[1][newBinX] if newBinX <= nBins else oldNbins + 2
        for oldBinX in range(binning[1][newBinX - 1], maxOldBinX):
            content += hist.GetBinContent(oldBinX)
            if oldSumw2:
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
    parser.add_argument('--era', help='era', choices=['2016', '2017', '2018', 'fullrun2'], required=True)
    parser.add_argument('--uncertainty', type=float, default=0.3, help='max stat. uncertainty')
    parser.add_argument('--events', type=float, default=10e2, help='max entries in bins')
    parser.add_argument('-p0', '--prior', type=float, default=0.05, 
                            help='false positive probability: the relative\n'
                                 'frequency with which the algorithm falsely reports detection of a\n'
                                 'change-point in data with no signal present.\n')
    parser.add_argument('--yields',  action='store_true', default=False, help='')
    parser.add_argument('--scale', action='store_true', default=False, help=' scale histograms before start rebining')
    parser.add_argument('--toys', action='store_true', default=False, help=' use toys data')
    parser.add_argument('--asimov', action='store_true', default=False, help=' use pseudo-data , sum of all bkg+ sum of signal')
    parser.add_argument('--plotit', action='store_true', default=False, help=' do plots after rebining')
    parser.add_argument('--onlypost', action='store_true', default=False, 
                            help=' useful to set to True when the changes is only at the plotting stage')
    parser.add_argument('--logy', action='store_true', default=False, help=' produce plots in log scale')
    parser.add_argument('--sys', action='store_true', default=False, help=' produce rebinned systematic histograms')
    parser.add_argument('--mode', action='store', required=True, choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'mjj', 'mlljj', 'rho', 'dnn'], 
                            help='Analysis mode')
    parser.add_argument('--submit', action='store', default='test', choices=['all', 'test'],
                            help='submit all or just pass test, useful when small modification is need for plotting\n'
                                 'without a need to touch the histogram again\n')
    parser.add_argument('--job', action='store', default='local', choices=['local', 'slurm'],
                            help= '')
    parser.add_argument('--normalized', action='store_true', default=False, 
                            help= 'rebinned plotit-plots can be normalized to 1pb')
    parser.add_argument('--rebin', action='store', choices= ['custom', 'standalone', 'bayesian'], required=True, 
                            help='compute new binning by setting some treshold on the uncer and number of events\n'
                                 'or just re-arrange the oldbins to merge few bins into one, starting from the left to the right\n')
    parser.add_argument('--scenario', action='store', choices= ['hybride', 'S', 'B'], required=False, 
                            help='')
    parser.add_argument('--unblind', action='store_true', default=True, help="If set to True will produced histogram for data too")

    args = parser.parse_args()
    
    
    if not os.path.isdir(args.output):
        os.makedirs(args.output)
   
    plotsDIR = os.path.join(args.output, "plots")
    if not os.path.isdir(plotsDIR):
        os.makedirs(plotsDIR)

    sumPath   = "asimov_data-scaled" if args.scale else "asimov"
    s         = f"_on_{args.scenario}" if args.scenario !=None else ""
    suffix    = f"{args.rebin}_rebin{s}/results"
    case      = f'_all_on_{args.scenario}' if args.submit=='all' else '_template'
    
    divideByBinWidth = False
    get_half         = False
    force_muel_onebin= False
    force_samebin    = False   # A -> ZH and H-> ZA have the same binning
    fix_reco_format  = False
    
    numpy_hist.get_half = get_half

    if args.job =='local': list_inputs = glob.glob(os.path.join(args.input, '*.root'))
    else: list_inputs = [args.input] # will give one root file at the time with slurm_job id 
    
    # normalize and sum samples
    outDir = os.path.join(args.output, sumPath)
    if args.asimov: 
        if not os.path.isdir(outDir):
            os.makedirs(outDir)
            logger.info(f'working on hadd backgrounds from bamboo {args.input} to play with as an asimov dataset')
            optimizer.normalizeAndSumSamples(args.input, outDir, list_inputs, args.era, args.scale)
        else:
            logger.info(f'{outDir}/ already exist and not empty!\n'
                        '\tScale/ hadd steps will be skipped \n'
                        '\tIf you have an updated version of files or you want to rerun the steps above :\n'
                       f'\tPlease rm -rf {outDir}/ and start over!\n' )
        
    if args.onlypost:
        inputs = [] # do not process anything , just go to the plotter
    else:
        if args.submit=='all':
            # bkg, data and signal as it is given/found in the args.inputs
            inputs = list_inputs
            if args.rebin == 'bayesian':
                try:
                    f = open(os.path.join(args.output, f"rebinned_edges_{args.rebin}_template.json"))
                    data = json.load(f)
                except Exception as ex:
                    raise RuntimeError(f' -- {ex} occure when reading rebinned_edges_{args.rebin}_template.json')
        
        else: 
            # prepare Bayesian_Blocks/or custon binning template 
            if args.toys:
                # take toys data 
                inDir  = os.path.join(args.input, f'generatetoys-data/{args.mode}/2POIs_r/*')
                inputs = glob.glob(os.path.join(inDir, '*_shapes.root'))
            elif args.asimov:
                k    = 'data' #'mc' if args.scale else 'data'    # avoid normalisation crap of mc 
                s    = 'scaled_' if args.scale else ''
                dir_ = outDir  if args.scale else inDir #  take from the scaled otherwise bamboodir
                # take pseudo-data: A sum of all bkg, signal stay seperate 
                inputs = {'B' : [f"{outDir}/summed_{s}{k}_UL{args.era}.root"],
                          'S' : [] }
                for rf_s in glob.glob(os.path.join(dir_, '*.root')):
                    rf_sNm = rf_s.split('/')[-1]
                    if not optimizer.EraFromPOG(args.era) in rf_sNm: 
                        continue    
                    if any(rf_sNm.startswith(x) for x in ['AToZH', 'HToZA', 'GluGluToAToZH', 'GluGluToHToZA']):
                        inputs['S'].append(rf_s)
    
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
            smpNm    = rf.split('/')[-1].split('_shapes')[0]
            process  = smpNm.split('_')[1] + '_' + smpNm.split('_')[2]
            channels = set()
            inFile   = HT.openFileAndGet(rf)
            for k in inFile.GetListOfKeys():
                cat = k.GetName()
                if not cat.startswith(args.mode):
                    continue
                channels.add(cat)
            channels = list(channels)
            print ("Detected channels: ", channels , smpNm)
             
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

                mass   = channel.replace(f'{args.mode}_', '')
                histNm = optimizer.get_histNm_orig(args.mode, smpNm, mass, info=False, fix_reco_format=fix_reco_format)
                
                if not histNm in binnings['histograms'].keys():
                    binnings['histograms'][histNm] = {}
                if not process in binnings['histograms'][histNm].keys():
                    binnings['histograms'][histNm].update({process: {}})
                
                for key in inFile.Get(channel).GetListOfKeys():
                    
                    isSignal  = False
                    isData    = False

                    if key.GetName().startswith('gg') or key.GetName().startswith('bb'): isSignal=True
                    if 'data' in key.GetName(): isData=True 

                    k = 'S' if isSignal else ('B' if isData else(key.GetName()))
                    if not (isData or isSignal):
                        continue
                    if isSignal and any( x in histNm for x in ['MuEl', 'ElMu'] ):
                        continue
                     
                    oldHist[k] = inFile.Get(channel).Get(key.GetName())
                    
                    if not oldHist[k]:
                        logger.error('could not find object: inFile.Get({channel}).Get({key.GetName()}) -- return null pointer!')
                    print( f'- working on : {key.GetName()}' ) 
                    
                    label    = mass if isSignal else 'B-Only toy data'
                    datatype = "toys_signal" if isSignal else key.GetName()
                   
                    np_hist = NumpyHist.getFromRoot(oldHist[k])
                    oldBinContent[k] = np_hist.w
                    oldBinErrors[k]  = np_hist.s
                    oldEdges[k]      = np_hist.e
                   
                    newHist[k], newEdges[k], FinalBins[k] = BayesianBlocks( root_file         = rf,
                                                                            old_hist          = oldHist[k],
                                                                            mass              = mass, 
                                                                            name              = smpNm,
                                                                            channel           = channel,
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
                
                hybridebinning_dict = {'B': newEdges['B'] }
                
                binnings['histograms'][optimizer.get_histNm_orig(args.mode, smpNm, mass, info=False, fix_reco_format=fix_reco_format)][process].update(
                           {'B': [MarkedList(newEdges['B']), MarkedList(FinalBins['B']) ] } )
                
                if not any ( x in histNm for x in ['MuEl', 'ElMu'] ):
                    newEdges['S'] = newEdges['S'].astype(float).round(2).tolist()
                    binning  = optimizer.hybride_binning( BOnly = [newEdges['B'], FinalBins['B']], 
                                                          SOnly = [newEdges['S'], FinalBins['S']] )

                
                    hybridebinning_dict.update( {'S': newEdges['S'],
                                                 'hybride': binning[0] } )
                   # not in use !! 
                   # newEdges_with_thres_cut, newBins_with_thres_cut = BayesianBlocksHybrid(
                   #                 oldHist, 
                   #                 name                  = 'hybride_bininngS+B_bayesian_toys' + '_' + smpNm, 
                   #                 output                = plotsDIR, 
                   #                 label                 = label,
                   #                 newEdges              = hybridebinning_dict, 
                   #                 include_overflow      = False, 
                   #                 logy                  = args.logy)
                    binnings['histograms'][optimizer.get_histNm_orig(args.mode, smpNm, mass, info=False, fix_reco_format=fix_reco_format)][process].update(
                            {   'S'      : [MarkedList(newEdges['S']), MarkedList(FinalBins['S']) ],
                                'hybride': [MarkedList(binning[0]), MarkedList(binning[1])],
                                # deprecated: 'BB_hybride_good_stat': [MarkedList(newEdges_with_thres_cut), MarkedList(newBins_with_thres_cut)],
                            })

            inFile.Close()
    
    elif args.asimov:
        
        for k, rf_list in inputs.items():
            isSignal = False
            
            if k == 'S':
                datatype = 'asimov_signal' 
                isSignal = True
            else:
                datatype = 'asimov_data'
            
            for rf in rf_list:
                inFile   = HT.openFileAndGet(rf)
                smpNm    = rf.split('/')[-1]
                
                if isSignal:
                    if smpNm.stratswith('GluGluTo'): process = 'gg_fusion'
                    else: process = 'bb_associatedProduction' 
                
                for key in inFile.GetListOfKeys():
                    
                    histNm   = key.GetName()
                    
                    if '__' in histNm: # sys avoid
                        continue
                    if args.mode == 'dnn' and not histNm.startswith('DNN'):
                        continue
                    if isSignal and any (flav in histNm for flav in ['ElMu', 'MuEl']):
                        continue
                    if 'boosted' in histNm or process == 'bb_associatedProduction':
                        if not 'OSSF' in histNm:
                            continue
                    if 'resolved' in histNm and 'OSSF' in histNm:
                        continue

                    binnings['histograms'][histNm] = {}
                    if not process in binnings['histograms'][histNm].keys():
                        binnings['histograms'][histNm].update({process: {}})
                    
                    mass   = histNm.split(process+'_')[-1].split('__')[0]
                    label  = mass if isSignal else 'B-Only Asimov data'
                    newHist, newEdges, FinalBins = BayesianBlocks(  root_file         = rf, 
                                                                    old_hist          = inFile.Get(histNm), 
                                                                    mass              = mass, 
                                                                    name              = histNm,
                                                                    channel           = None, 
                                                                    output            = plotsDIR, 
                                                                    prior             = args.prior, 
                                                                    datatype          = datatype, 
                                                                    label             = label,
                                                                    logy              = args.logy, 
                                                                    isSignal          = isSignal, 
                                                                    doplot            = True,
                                                                    dofind_bestPrior  = False,
                                                                    include_overflow  = False)
                    if k == 'B':
                        binnings['histograms'][histNm][process]['B'] = {'B': [MarkedList(newEdges), MarkedList(FinalBins) ] }
                    if not any ( x in histNm for x in ['MuEl', 'ElMu'] ):
                        binnings['histograms'][histNm][process].update(
                                {   'S' : [MarkedList(newEdges), MarkedList(FinalBins) ],
                                })
                inFile.Close()
    
    else: 
        # this step will do the rebinning on bamboo output using the rebining already saved in the json template
        if not os.path.isdir(os.path.join(args.output, suffix)):
            os.makedirs(os.path.join(args.output, suffix), exist_ok=True)
        
        if args.submit=='all':
            files= list_inputs
        elif args.submit=='test':
            files= binnings['files']['signal']+ binnings['files']['tot_b']
        
        Observation = {}
        for process in ['gg_fusion', 'bb_associatedProduction']:
            
            if not os.path.isdir(os.path.join(args.output, suffix, process)):
                os.makedirs(os.path.join(args.output, suffix, process), exist_ok=True)
            
            for rf in files:
                isSignal = False
                smpNm = rf.split('/')[-1].replace('.root','')
                if smpNm.startswith('__skeleton__'):
                    continue
                
                if args.era != 'fullrun2':
                    if not optimizer.EraFromPOG(args.era) in smpNm:
                        continue
                
                if not args.unblind:
                    if any(x in smpNm for x in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon', 'SingleElectron']):
                        continue

                if any(x in smpNm for x in ['_tb_20p00_','_tb_1p50_']): # my signals
                    isSignal = True
                    if smpNm.startswith('GluGluTo'): p = 'gg_fusion'
                    else: p = 'bb_associatedProduction' 
                
                if isSignal and p !=process:
                    continue
                
                print( f'==='*40) 
                print( f' working on : {rf}' ) 
                print( f' working on : {process} rebinning' )
            
                curr_dir = os.path.dirname(os.path.abspath(__file__))
                rf_out   = os.path.join(curr_dir, args.output, suffix, process, f"{smpNm}.root")
                inFile   = HT.openFileAndGet(rf)
                outFile  = HT.openFileAndGet(rf_out, "recreate")
                
                if not smpNm in Observation.keys():
                    Observation[smpNm] = {}

                for key in inFile.GetListOfKeys():
                    isSys  = False
                    if args.mode == 'dnn':  
                        if not key.GetName().startswith('DNN'):
                            continue
                    
                    if '__' in key.GetName(): isSys=True
                    if not args.sys and isSys: 
                        continue
                   
                    if args.rebin=='bayesian':
                        # after all conditions above , now the binning template 
                        # need to be found for these histogram ( taken from json file)
                        if not any( key.GetName().startswith(x) for x in data['histograms'].keys()): 
                            continue
                    
                    params = optimizer.get_histNm_orig(args.mode, key.GetName(), mass=None, info=True, fix_reco_format=fix_reco_format)[1]
                    hist   = inFile.Get(key.GetName())
                    if not (hist and hist.InheritsFrom("TH1")):
                        continue
                    
                    oldHist = inFile.Get(key.GetName())
                    
                    if not isSys:
                        Observation[smpNm][key.GetName()]= {'sumTotal': None, 'sumPass': None}
                        
                        if not key.GetName() in binnings['histograms'].keys():
                            binnings['histograms'][key.GetName()] = {}
                        if not process in binnings['histograms'][key.GetName()].keys():
                            binnings['histograms'][key.GetName()].update({process: []})

                    print( f' working on : {key.GetName()}' ) 
                    name = key.GetName() +'_rebin'
                    #===================================================== 
                    
                    if args.rebin == 'custom':
                        binning = optimizeBinning(oldHist, args.events, args.uncertainty)
                        newEdges= binning[0]
                        newHist, sumOfWeightsGenerated = rebinCustom(oldHist, binning, oldHist.GetName())
                        name   += '_custome'

                    elif args.rebin == 'standalone':
                        newEdges = []
                        
                        if params['flavor'] == 'MuEl': 
                            keep_bins = [1, 51]
                        else:
                            keep_bins = np.arange(1, 26, 1).tolist() 
                        
                        for bin in keep_bins:
                            newEdges.append(oldHist.GetXaxis().GetBinLowEdge(int(bin)))
                        binning  = [newEdges, keep_bins]
                        newHist, sumOfWeightsGenerated  =  rebinCustom(oldHist, binning, oldHist.GetName())
                        name    += '_standalone'
                    
                    elif args.rebin == 'bayesian':
                        
                        look_for_hist = key.GetName().split('__')[0]
                        
                        if not process in data['histograms'][look_for_hist].keys():
                            continue

                        if force_samebin:
                            hist_ = look_for_hist
                            if 'ZA' in hist_:
                                hist_ = hist_.replace('ZA', 'ZH')
                                op    = hist_.split('METCut_')
                                m1    = op[-1].split('_')[1]
                                m2    = op[-1].split('_')[3]
                                
                                hist_ToForce  = op[0]+ 'METCut_MA_'+ m1 +'_MH_' +m2
                                if hist_ToForce in  data['histograms'].keys():
                                    look_for_hist = hist_ToForce
                                    #print( 'Force using histogram :: ' , hist_ToForce )

                        if params['flavor'] == 'MuEl': # this channel will help to control ttbar
                            if force_muel_onebin :
                                binning  = [[0., 1.], [1, 51]]
                            
                            elif get_half:
                                
                                hit_boundaries = False
                                _all_bins  = data['histograms'][look_for_hist][process]['B'][0]
                                _all_edges = data['histograms'][look_for_hist][process]['B'][1]
                                _half_bins = [x for x in _all_bins if x <= 0.6]
                                _half_edges= _all_edges[0:len(_half_bins)]
                                
                                if len(_half_bins) ==1: hit_boundaries = True
                                
                                if hit_boundaries:
                                    binning  = data['histograms'][look_for_hist][process]['B']
                                else:
                                    binning    = [_half_bins, _half_edges]
                            else:
                                binning  = data['histograms'][look_for_hist][process]['B']
                        else:
                            if get_half:
                                
                                hit_boundaries = False
                                _all_bins  = data['histograms'][look_for_hist][process][args.scenario][0]
                                _all_edges = data['histograms'][look_for_hist][process][args.scenario][1]
                                _half_bins = [x for x in _all_bins if x <= 0.6]
                                _half_edges= _all_edges[0:len(_half_bins)]
                                
                                if len(_half_bins) ==1: hit_boundaries = True
                                
                                if hit_boundaries:
                                    binning  = data['histograms'][look_for_hist][process][args.scenario]
                                else:
                                    binning    = [_half_bins, _half_edges]
                            else:
                                binning  = data['histograms'][look_for_hist][process][args.scenario]

                        nph_old = NumpyHist.getFromRoot(oldHist)
                        
                        """
                            Please do not use this option if you are producing rebinned histogram for Combine
                            I use it only to get better binning for paper plots (just for visual effect improvemets)
                            So I am not sure how the stat error is propagated if you intend to use it when you run the stat test in combine
                        
                        if divideByBinWidth: 
                            newHist_ = nph_old.rebin(np.array(binning[0])).fillHistogram(oldHist.GetName()) 
                            nph_new = NumpyHist.getFromRoot(newHist_)
                            nph_new.divideByBinWidth() 
                            #nph_new.setUnitaryBinWidth()
                            newHist = nph_new.fillHistogram(oldHist.GetName())
                        """ 
                        
                        newHist = nph_old.rebin(np.array(binning[0])).fillHistogram(oldHist.GetName()) 
                        nph_new = NumpyHist.getFromRoot(newHist)
                        
                        if not get_half:
                            if nph_new.w.sum() != 0. and abs(nph_new.w.sum()-nph_old.w.sum())/nph_new.w.sum() > 1e-4:
                                logger.warning("sum of binContents between 2 histogram does not match\n"
                                              f"new = {nph_new.w.sum():.5e}, old = {nph_old.w.sum():.5e}")
                       
                    if not isSys:
                        Observation[smpNm][key.GetName()]['sumPass'] = newHist.GetEntries()
                        binnings['histograms'][key.GetName()][process].append([MarkedList(binning[0]), MarkedList(binning[1])])
                    
                    #print(np.sqrt(sum(list(newHist.GetSumw2())))/newHist.Integral())
                    outFile.cd()
                    newHist.Write()

                # save Runs TTree too also once
                runsTree = inFile.Get('Runs')
                runsTree.Write()
                
                inFile.Close()
                outFile.Close()
                print(' rebinned histogram saved in: {} '.format(os.path.join(args.output, suffix, process, f"{smpNm}.root")))
        
        if args.yields: 
            #optimizer.get_yields(Observation)
            # dump in yaml file instead , could be useful later for plotting eff 
            with open('event_generated_and_passed.yaml', 'w') as file:
                yaml.dump(Observation, file)

    fNm = f"rebinned_edges_{args.rebin}{case}.json"
    if not args.onlypost:
        with open(os.path.join(args.output, fNm), 'w') as _f:
            b = json.dumps(binnings, indent=2, separators=(',', ':'), cls=CustomJSONEncoder)
            b = b.replace('"##<', "").replace('>##"', "")
            _f.write(b)
        print(' rebinned template saved in : {} '.format(os.path.join(args.output, fNm)))
        
    if args.plotit:
        if args.onlypost:
            f = open(os.path.join(args.output, fileNm))
            binnings = json.load(f)
        optimizer.plotRebinnedHistograms(binnings, inDir, args.output, mode, suffix, args.era, args.toys, normalized=args.normalized)
