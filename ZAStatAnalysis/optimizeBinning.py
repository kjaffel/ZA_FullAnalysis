#!/usr/bin/env python
import argparse
import json
import glob
import os
import random
import itertools
import math
import shutil
import subprocess
import collections

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
logger = Constants.ZAlogger(__name__)

def hybride_binning(BOnly=None, SOnly=None):
    """Use min() to find the nearest value in a list to a given one 
    """
    print( 'S-Only:', SOnly[0], 'B-Only:', BOnly[0] )
    # low bin edges from signal template are not accurate: 
    # do not accept values below 0.6 
    signal_edges = [item for item in SOnly[0] if item > 0.65]
    given_value  = signal_edges[0]
    index2 = SOnly[0].index(given_value)

    absolute_difference_function = lambda list_value : abs(list_value - given_value)
    closest_value = min(BOnly[0], key=absolute_difference_function)
    print( f'given_value:  {given_value}, closest_value: {closest_value} ')
    index = BOnly[0].index(closest_value)
    newEdges  = BOnly[0][0:index] + signal_edges
    FinalBins = BOnly[1][0:index] + SOnly[1][index2:]
    print( f'hybride binning: {newEdges} , len: {len(newEdges)}')
    return [newEdges, FinalBins]

def available_points(inputs=None):
    points = []
    for fin in inputs:
        smp = fin.split('/')[-1].replace('.root','')
        if 'MH-' not in smp:
            continue
        p   = smp.split('To2L2B_')[-1].replace('MH-', 'MH_').replace('MA-', 'MA_')
        if not p in points:
            points.append(p)
    return points

def get_histNm_orig(mode=None, smpNm=None, mass=None, info=False):
    if 'gg_fusion' in smpNm: process = 'gg_fusion'
    else: process = 'bb_associatedProduction'
    if 'ElEl' in smpNm: flavor='ElEl'
    else: flavor='MuMu'
    if 'resolved' in smpNm: region='resolved'
    else: region='boosted'
    if 'DeepCSVM' in smpNm: taggerWP= 'DeepCSVM'
    else: taggerWP='DeepFlavourM'
    
    histNm  = f'{mode}_{flavor}_{region}_{taggerWP}_METCut_{process}_{mass}'
    details = {'process':process,
               'flavor' :flavor,
               'region' :region,
               'taggerWP':taggerWP,
               'mass'    :mass
               }
    return histNm, details if info else histNm

def get_new_histogramWgt(hist, newEdges, oldEdges, oldNbins):
    binContent= np.array([])
    FinalBins = []
    for x in newEdges:
        b = hist.FindBin(x)
        #if not b in FinalBins:
        FinalBins.append(b)

    nBins = len(oldEdges) - 1 
    #print( f"FinalBins : {FinalBins}" )
    for i, newBinX in enumerate(FinalBins):
        if i ==len(FinalBins) -1:
            continue
        content = 0
        print("==="*20)
        print(f" merging bins {newBinX} -> {FinalBins[i+1]}") 
        maxOldBinX = FinalBins[i+1] if newBinX <= nBins else oldNbins + 2
        for oldBinX in range(newBinX, maxOldBinX):
            content += hist.GetBinContent(oldBinX)
            print(f"\tGetting from bin {oldBinX }, content = {content}") 
        binContent = np.append(binContent, content)
    #print( len( binContent), len(FinalBins), len(newEdges))
    return binContent, FinalBins


#def PLotHybrideHistos(rf=None, old_hist_S=None, histNm=None, name=None, output=None, newEdges=None, include_overflow=False, logy=False
def PLotHybrideHistos(oldHist=None, name=None, output=None, newEdges=None, include_overflow=False, logy=False):
    fig = plt.figure(figsize=(10, 7))
    ax  = fig.add_subplot(111)

    #inFile  = HT.openFileAndGet(rf)
    #old_hist_B = inFile.Get(histNm)
    
    #oldHist = {'B':old_hist_B, 'S': old_hist_S}

    oldEdges = {}
    np_arr_oldhist = {}
    np_arr_newhist = {}
    np_arr_hybride = {}
    for k, v in oldHist.items():
        np_arr_edges_oldhist= root_numpy.hist2array(v, include_overflow=include_overflow, copy=True, return_edges=True)
        np_arr_oldhist[k] = np_arr_edges_oldhist[0]
        oldEdges[k]       = np_arr_edges_oldhist[1][0]
        if include_overflow: oldEdges[k]   = np.append(oldEdges[k], 1.02 )
        else: np_arr_oldhist[k] = np.append(np_arr_oldhist[k], 0. )

        oldNbins = v.GetNbinsX() 
        np_arr_newhist[k] = get_new_histogramWgt(v, newEdges[k], oldEdges[k], oldNbins)[0]
        np_arr_newhist[k] = np.append(np_arr_newhist[k], np_arr_oldhist[k][-1])    

        np_arr_hybride[k] = get_new_histogramWgt(oldHist[k], newEdges['hybride'], oldEdges[k], oldNbins)[0]
        np_arr_hybride[k] = np.append(np_arr_hybride[k], np_arr_hybride[k][-1])

    np_arr_hybride['hybride']= np.add(np_arr_hybride['B'],np_arr_hybride['S'])
    #print( 'BACKGROUND:', oldEdges["B"] , np_arr_oldhist["B"], len( oldEdges["B"]), len(np_arr_oldhist["B"]))
    #print( 'SIGNAL    :', oldEdges["S"] , np_arr_oldhist["S"], len(oldEdges["S"]), len(np_arr_oldhist["S"]) )
    #print( 'HYBRIDE   :', newEdges['hybride'], np_arr_newhist["B"], np_arr_newhist["S"], len(newEdges['hybride']), len(np_arr_newhist["B"]), len(np_arr_newhist["S"]))
    
    ax.hist( [oldEdges["S"], oldEdges["B"]], bins   =oldEdges["B"],  # they were the same (50 bins) for both 
                                             color  =['red', 'blue'], 
                                             weights=[np_arr_oldhist["S"],np_arr_oldhist["B"]], 
                                             alpha=0.2, histtype='stepfilled', stacked=True, density=False, label=['50bins: S-Only', '50bins: B-Only'])
    
    ax.hist(newEdges["S"], bins=newEdges["S"], color='red', weights=np_arr_newhist["S"], 
                                            histtype='step', stacked=True, density=False, fill=False, label=f"Bayesian blocks: S-Only")
    ax.hist(newEdges["B"], bins=newEdges["B"], color='blue', weights=np_arr_newhist["B"], 
                                            histtype='step', stacked=True, density=False, fill=False, label=f"Bayesian blocks: B-Only")
    ax.hist(newEdges["hybride"], bins=newEdges["hybride"], color='black', weights=np_arr_hybride["hybride"], 
                                            histtype='step', stacked=True, density=False, fill=False, label=f"Bayesian blocks: S+B")
            
    ax.legend(prop=dict(size=12), loc='best')
    ax.set_xlabel('DNN_output ZA')
    ax.set_ylabel('Events')
    
    if logy:
        ax.set_yscale('log') 
        name += '_logy'
    fig.savefig(os.path.join(output, name+'.png')) 
    fig.savefig(os.path.join(output, name+'.pdf'))
    
    inFile.Close()
    plt.gcf().clear()

def BayesianBlocks(old_hist=None, name=None, output=None, prior=None, cat='', histNm=None, label=None, logy=False, isSignal=False, include_overflow=False):
    """
    Bayesian Blocks is a dynamic histogramming method which optimizes one of
    several possible fitness functions to determine an optimal binning for
    data, where the bins are not necessarily uniform width.  
    The code below uses a fitness function suitable for event data with possible
    repeats.  More fitness functions are available: see :mod:`density_estimation`
    
    https://numpy.org/doc/stable/reference/generated/numpy.histogram.html
    https://root.cern.ch/doc/master/classTH1.html#ae0895b66e993b9e9ec728d828b9336fe 
    
    bin_content = []
    binnxs = [hist.GetXaxis().GetBinLowEdge(1)]
    for i in range(1,hist.GetNbinsX()+1):
        bin_content.append(hist.GetBinContent(i))
        binnxs.append(hist.GetXaxis().GetBinUpEdge(i))
    print( bin_content, binnxs )
    
    #assert_equal(old_hist.GetDimension(), np_arr_edges_oldhist.ndim)
    #for iaxis, axis in enumerate('XYZ'[:np_arr_edges_oldhist.ndim]):
    #    if include_overflow:
    #        assert_equal(array.shape[iaxis], getattr(old_hist, 'GetNbins{0}'.format(axis))() + 2)
    #    else:
    #        assert_equal(array.shape[iaxis], getattr(old_hist, 'GetNbins{0}'.format(axis))())
    """

    np_arr_edges_oldhist = root_numpy.hist2array(old_hist, include_overflow=include_overflow, copy=True, return_edges=True)
    np_arr_oldhist = np_arr_edges_oldhist[0]
    oldEdges       = np_arr_edges_oldhist[1][0]
    
    if include_overflow:
        oldEdges   = np.append(oldEdges, 1.02 )
    else:
        np_arr_oldhist = np.append(np_arr_oldhist, 0. )
    
    oldNbins = old_hist.GetNbinsX() 
    oldBins  = []
    for i in oldEdges:
        oldBins.append(old_hist.FindBin(i))
    
    print( "oldBins :", oldBins, "NBins :", oldNbins)
    print( oldEdges.shape , np_arr_oldhist.shape )
    print( np_arr_edges_oldhist, len(np_arr_oldhist), len(oldEdges))
   
    fig = plt.figure(figsize=(10, 4))
    fig.subplots_adjust(left=0.1, right=0.95, bottom=0.15)
    doplot = True
    find_best_prior = False

    if find_best_prior:
        for p0 in np.arange(0., 1., 0.001):
                
            prior    = Prior(p0=p0, gamma=None)
            _fitness = stats.FitnessFunc(p0=p0, gamma=None, ncp_prior=None)
            ncp      = _fitness.compute_ncp_prior(N=old_hist.GetNbinsX()) # or prior.calc(N=old_hist.GetNbinsX())
        
            newEdges  = bayesian_blocks(oldEdges, weights=np_arr_oldhist, p0=p0, gamma=None)
            #newEdges = stats.bayesian_blocks(oldEdges, np_arr_oldhist, fitness='measures')   
            logger.info( f'ncp = {ncp}, prior = {p0}, newBlocks = {len(newEdges)} ') 
        
    if doplot:
        color = 'red' if isSignal else 'blue' 
        p0  = 0.1 if isSignal else 0.05 
        pNm = histNm + name + '_' + cat + "_%.2fp0" %p0
        for p0, subplot in zip([p0, p0+0.01], [121, 122]):
            
            print("prior p0:", p0 )
            ax = fig.add_subplot(subplot)
            
            newEdges = bayesian_blocks(oldEdges,np_arr_oldhist, p0=p0)
            #newEdges = stats.bayesian_blocks(oldEdges, np_arr_oldhist, fitness='measures', p0=p0, ncp_prior=None) 
            newEdges = [float(format(e,'.2f')) for e in newEdges]
            
            np_arr_newhist, FinalBins= get_new_histogramWgt(old_hist, newEdges, oldEdges, oldNbins)
            np_arr_newhist = np.append(np_arr_newhist, np_arr_oldhist[-1])

            if np.sum(np_arr_newhist) != np.sum(np_arr_oldhist):
                logger.warning("sum of binContents between 2 histogram does not match\n"
                                f"new = {np.sum(np_arr_newhist)}   old = {np.sum(np_arr_oldhist)}")
            print( "oldBinContents : ",  np_arr_oldhist, len(np_arr_oldhist))
            print( "newBinContents : ",  np_arr_newhist, len(np_arr_newhist))
            print( "oldEdges       : ",  oldEdges ,      len(oldEdges))
            print( "newEdges       : ",  newEdges ,      len(newEdges))
            
            root_newhist = R.TH1D(name, "", len(newEdges), 0., 1.)
            newHist      = root_numpy.array2hist(np_arr_newhist, root_newhist)
        
            ax.hist(oldEdges, bins=oldEdges, color=color, histtype='stepfilled', weights=np_arr_oldhist,
                    alpha=0.2, density=False, label=label)
            ax.hist(newEdges, bins=newEdges, color='black', weights=np_arr_newhist,
                    histtype='step', density=False, label=f"Bayesian blocks: {'%.2f' % (float(p0))}")
            
            ax.legend(prop=dict(size=12))
            ax.set_xlabel('DNN_output ZA')
            ax.set_ylabel('Events')
            if logy:
                ax.set_yscale('log') 
        
        if logy:
            pNm += '_logy'
        fig.savefig(os.path.join(output, pNm+'.png')) 
        fig.savefig(os.path.join(output, pNm+'.pdf'))
        #plt.show()
        plt.gcf().clear()
    print(f" plots saved in : {output}" )

    """  works better for unweighted histogram !! 
    method   = {}
    normal   = [['scott', 'freedman'], ['Scott’s rule', 'Freedman-Diaconis rule']]
    bayesian = [['knuth', 'blocks'], ["Knuth's rule", 'Bayesian blocks']]
    
    for i, m in enumerate([ normal, bayesian]):
        pNm = name + f'_{i}'
        for bins, title, subplot in zip(m[0],m[1],[121, 122]):
            ax = fig.add_subplot(subplot)
            #ax.set_xlim([0., 1.])
            
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
    """     
    return newHist, newEdges, FinalBins

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
    #GetSum
    #GetSumOfWeights
    #GetSumw2
    #GetSumw2N

    binContents = list(hist)
    binSumW2    = list(hist.GetSumw2()) # Total Sum of squares of weights
    finalBins   = [startBin] # array [i j k ...] -> bin 1 in new histo = bins i ... j-1 in old one, etc.

    upEdge = startBin
    mergeLastBin = False
    newEdges = []
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
        while uncertainty < maxUncertainty or population < yields: # content < maxEvents:
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
        finalBins.append(upEdge)
    
    # The last bin will correspond to the overflow bin so we don't include it explicitly in the edges
    #del newEdges[-1]
    #if mergeLastBin and acceptLargerOverFlowUncert:
    #    del finalBins[-2]

    print(f"New binning == >  newEdges = {newEdges} ,  finalBins = {finalBins}")
    return newEdges, finalBins


def rebinCustom(hist, binning, name, verbose=False):
    """ Rebin 1D hist using bin numbers and edges as returned by optimizeBinning() """

    edges = binning[0]
    nBins = len(edges) - 1
    oldNbins = hist.GetNbinsX()
    print( f'processing ::: name: {name}, Title: {hist.GetTitle()}, nbinsx: {nBins}, xlow, xup : {np.array(edges)}, FinalBins: {binning[1]}' )
    newHist  = R.TH1D(name, hist.GetTitle(), nBins, np.array(edges))
    newHist.Sumw2()
    oldSumw2 = list(hist.GetSumw2())
    for newBinX in range(1, nBins+2):
        content = 0
        sumw2   = 0
        maxOldBinX = binning[1][newBinX] if newBinX <= nBins else oldNbins + 2
        for oldBinX in range(binning[1][newBinX - 1], maxOldBinX):
            content += hist.GetBinContent(oldBinX)
            sumw2   += oldSumw2[hist.GetBin(oldBinX)]
        if verbose:
            print( f'merging bins {binning[1][newBinX-1]} ({hist.GetXaxis().GetBinLowEdge(binning[1][newBinX-1])}) -> {maxOldBinX} ({hist.GetXaxis().GetBinLowEdge(maxOldBinX)}) : BinContent = {content}')
        newHist.SetBinContent(newBinX, content)
        newHist.GetSumw2()[newHist.GetBin(newBinX)] = sumw2

    return newHist

def normalizeAndSumSamples(inDir, outDir, sumPath, inputs, era, scale=False):
    s = 'scaled_' if scale else ''
    smpCfg  = H.getnormalisationScale(inDir, method=None, seperate=True)        
    sorted_inputs= {'data'  :[], 
                    'mc'    :[], 
                    'signal':[] }
    for rf in inputs:
        isData = False
        smp    = rf.split('/')[-1]
        smpNm  = smp.replace('.root','')
        if smpNm.startswith('__skeleton__'):
            continue
        lumi   = smpCfg[smp][1]
        xsc    = smpCfg[smp][2]
        genevt = smpCfg[smp][3]
        br     = smpCfg[smp][4]
        
        if any(x in smpNm for x in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon']):
            shutil.copyfile( os.path.join(inDir, smp), os.path.join(outDir, smp))
            sorted_inputs['data'].append(rf)
            isData = True
        else:
            smpScale = lumi / genevt
            if any(x in smpNm for x in ['AToZH', 'HToZA', 'GluGlu']):
                smpScale *= xsc * br
                sorted_inputs['signal'].append(rf)
            else:
                smpScale *= xsc
                sorted_inputs['mc'].append(rf)
        
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
        else:
            shutil.copyfile( os.path.join(inDir, smp), os.path.join(outDir, smp))

    for k, val in sorted_inputs.items():
        haddCmd = ["hadd", "-f", os.path.join(outDir, sumPath, f"summed_{s}{era}{k}_samples.root")]+val
        try:
            logger.info("running {}".format(" ".join(haddCmd)))
            subprocess.check_call(haddCmd)#, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            logger.error("Failed to run {0}".format(" ".join(haddCmd)))

def plotRebinnedHistograms(binnings, folder, mode_, suffix, year, toysdata=False, normalized=False):
   
    if normalized:
        smpConfig  = H.getnormalisationScale(folder, method=None, seperate=True)
        lumiconfig = smpConfig['configuration']
        """
        smpConfig = {"Configurations": {}
                    smp_signal : [era, lumi, xsc , generated-events, br],
                    smp_mc     : [era, lumi, xsc , generated-events, None], 
                    smp_data   : [era, None, None, None,           , None] }
        """
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
                            outf.write(f"      text: {infos['region']}, {infos['flavor'].lower()}\n")
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
        plotsDIR   = os.path.join(folder, "plots", "plotit")
        if not os.path.isdir(plotsDIR):
            os.makedirs(plotsDIR)
        
        with open(f"data/rebinned_template.yml", 'r') as inf:
            with open(f"{folder}/plots.yml", 'w+') as outf:
                for line in inf:
                    if "  root: myroot_path" in line:
                        outf.write(f"  root: {folder}/{suffix}/\n")
                    elif "files:" in line:
                        outf.write("files:\n")
                        for kf, vf in binnings['files'].items():
                            
                            if not vf:
                                continue
                            _type = kf if kf in ['data', 'signal'] else 'mc'
                            
                            for root_f in vf:

                                color  = fake.hex_color()
                                smp    = root_f.split('/')[-1]
                                if normalized:
                                    year   = smpConfig[smp][0]
                                    lumi   = smpConfig[smp][1]
                                    xsc    = smpConfig[smp][2]
                                    genevt = smpConfig[smp][3]
                                    br     = smpConfig[smp][4]
                                
                                outf.write(f"  {smp}:\n")
                                outf.write(f"    type: {_type}\n")
                                if not _type=='signal': 
                                    outf.write(f"    group: {kf}\n")
                                outf.write(f"    era: {year}\n")
                                
                                if _type == 'signal':
                                    outf.write(f"    legend: {smp.split('.root')[0]}\n")
                                    outf.write(f"    line-color: '{color}'\n")
                                    outf.write("    line-type: 1\n")
                                    if normalized:
                                        outf.write(f"    Branching-ratio: {br}\n")
                                        outf.write(f"    generated-events: {genevt}\n")
                                        outf.write(f"    cross-section: {xsc} # pb\n")
                                elif _type == 'mc' and normalized:
                                        outf.write(f"    generated-events: {genevt}\n")
                                        outf.write(f"    cross-section: {xsc} # pb\n")
                    elif "  - myera" in line:
                    #    for era in lumiconfig.keys():
                        outf.write(f"  - {year}\n")
                    elif "    myera: mylumi" in line:
                    #    for era, lumi in lumiconfig.items():
                        lumi = Constants.getLuminosity(era)
                        outf.write(f"    {year}: {lumi}\n")
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
                            outf.write("    ratio-y-axis-range: [0.6, 1.2]\n")
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
        plotitCmd = ["/home/ucl/cp3/kjaffel/bamboodev/plotIt/plotIt", "-o", plotsDIR, "--", f"{folder}/plots.yml"]
        try:
            logger.info("running {}".format(" ".join(plotitCmd)))
            subprocess.check_call(plotitCmd)#, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            logger.error("Failed to run {0}".format(" ".join(plotitCmd)))
        print( f'\tplots saved in : {plotsDIR}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
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
    args = parser.parse_args()
    
    keep_bins = [1, 3, 9, 21, 39, 51, 52] # accept overflow  
    sumPath   = "summed_scaled_histogramms" if args.scale else "summed_histogramms"
    mode_     = 'DNNOutput_ZAnode' if args.mode =='dnn' else args.mode
    suffix    = f"{args.rebin}_rebin" 
    suff      = '_hybride' if args.submit=='all' and args.rebin== 'bayesian' else ''

    if args.toys:
        inDir  = os.path.join(args.input, f'generatetoys-limits/{args.mode}/*')
        list_inputs = glob.glob(os.path.join(inDir, '*_shapes.root'))
    else:
        inDir  = os.path.join(args.input, 'results/')
        list_inputs = glob.glob(os.path.join(inDir, '*.root'))
    outDir = os.path.join(args.output, 'inputs/')
    
    if not os.path.isdir(os.path.join(args.output, suffix)):
        os.makedirs(os.path.join(args.output, suffix))
    
    plotsDIR = os.path.join(args.output, "plots")
    if not os.path.isdir(plotsDIR):
        os.makedirs(plotsDIR)
    
    # normalize and sum samples
    if not args.toys:
        if not os.path.isdir(outDir):
            os.makedirs(outDir)
            if not os.path.isdir(os.path.join(outDir, sumPath)):
                os.makedirs(os.path.join(outDir, sumPath))
                normalizeAndSumSamples(inDir, outDir, sumPath, list_inputs, args.era, args.scale)
        else:
            logger.info(f'{outDir}/ already exist and not empty!\n'
                        '\tScale and hadd steps will be skipped \n'
                        '\tif you have an updated version of files OR you want to rerun the steps above :\n'
                        f'\tplease remove {outDir}/ and start over!\n' )
        shutil.copyfile(os.path.join(args.input, 'plots.yml'), os.path.join(args.output, 'plots.yml'))
    
    if args.submit=='all':
        # bkg , data and signal as it is given/found in the args.inputs
        inputs= list_inputs
    elif args.submit=='test':
        # take hadded files ( 1 tot bkg , 1 tot. data and 1 tot. signal )
        inputs= glob.glob(os.path.join(outDir, sumPath, '*.root'))
        if not args.toys: 
            for rf in glob.glob(os.path.join(outDir, '*.root')): # add also the signals seperatly 
                smpNm = rf.split('/')[-1].replace('.root','')
                if any(x in smpNm for x in ['AToZH', 'HToZA', 'GluGlu']):
                    inputs.append(rf)
    
    if args.onlypost: 
        inputs = [] # do not process any files 
        f = open(os.path.join(args.output, f"rebinned_edges_{args.rebin}{suff}.json"))
        binnings = json.load(f)
    else:
        binnings = {
                'files': {
                        'toys'     : [],
                        'signal'   : [],
                        'data'     : [],
                        'DY'       : [],
                        'ttbar'    : [],
                        'SingleTop': [],
                        'ZZ'       : [],
                        'SM'       : [],
                        'others'   : []},
                'histograms':{}
                }
    
    if args.toys:
        name = '_bayesian_toys'
        for rf in inputs:
            smpNm    = rf.split('/')[-1].split('_shapes')[0]
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
                newHist   = {} 
                oldHist   = {}
                newEdges  = {}
                FinalBins = {}
                isSignal  = False
                isData    = False
                
                sNm = channel.replace(f'{args.mode}_', '')
                binnings['histograms'][get_histNm_orig(mode_, smpNm, sNm)] = {}
                
                for key in inFile.Get(channel).GetListOfKeys():
                    
                    if key.GetName().startswith('HToZATo2L2B'): isSignal=True
                    elif 'data' in key.GetName(): isData=True 
                    

                    k = 'S' if isSignal else 'B'
                    if not (isData or isSignal):
                        continue
                    oldHist[k] = inFile.Get(channel).Get(key.GetName())
                    
                    if not oldHist:
                        logger.error('could not find object: inFile.Get({channel}).Get({key.GetName()}) -- return null pointer!')
                    logger.info( f' working on : {key.GetName()}' ) 
                    
                    label  = sNm if isSignal else 'B-Only toy data'
                    histNm = 'signal' if isSignal else key.GetName()
                    newHist[k], newEdges[k], FinalBins[k] = BayesianBlocks( oldHist[k], 
                                                                            name, 
                                                                            output            = plotsDIR, 
                                                                            prior             = args.prior, 
                                                                            cat               = smpNm, 
                                                                            histNm            = histNm, 
                                                                            label             = label,
                                                                            logy              = args.logy, 
                                                                            isSignal          = isSignal, 
                                                                            include_overflow  = False)
                
                binning  = hybride_binning( BOnly= [newEdges['B'], FinalBins['B']], SOnly= [newEdges['S'], FinalBins['S']] )
                hybridebinning_dict = {'B': newEdges['B'],
                                       'S': newEdges['S'],
                                       'hybride': binning[0]}
                PLotHybrideHistos(oldHist, 
                                  name                  = 'hybride_bininngS+B_bayesian_toys' + '_' + smpNm, 
                                  output                = plotsDIR, 
                                  newEdges              = hybridebinning_dict, 
                                  include_overflow      = False, 
                                  logy                  = args.logy)

                binnings['histograms'][get_histNm_orig(mode_, smpNm, sNm)].update({'B': [newEdges['B'], FinalBins['B']],
                                                                                   'S': [newEdges['S'], FinalBins['S']],
                                                                                   'hybride': binning })
                
                inFile  = HT.openFileAndGet(rf)
                for key in inFile.Get(channel).GetListOfKeys():
                    for histNm, bins in binnings['histograms'].items():
                    
                        oldHist_  = inFile.Get(channel).Get(key.GetName())
                        newHist_  = rebinCustom(oldHist_, bins['hybride'], histNm, verbose=False)
                
                        out_ = os.path.join(args.output, f'{args.rebin}_rebinned_on_toysdata/{smpNm}')
                        binnings['files']['toys'].append(out_)
                        if not os.path.isdir(out_):
                            os.makedirs(out_)
                        
                        rf_out  = os.path.join(out_, f"{key.GetName()}.root")
                        outFile = HT.openFileAndGet(rf_out, "recreate")
                        outFile.cd()
                        newHist_.Write()
                        outFile.Close()
            inFile.Close()
    else:
        for rf in inputs:
            smpNm = rf.split('/')[-1].replace('.root','')
            if smpNm.startswith('__skeleton__'):
                continue
            
            if   f'_{args.era}data' in smpNm: 
                type_='alldata'
            elif f'_{args.era}mc' in smpNm: 
                type_='allmc'
            elif f'_{args.era}signal' in smpNm: # save sometime ignoring hadd signals , no need for these histograms for now !! 
                type_='allsignal'
                continue
            
            isSignal =False
            if any(x in smpNm for x in ['AToZH', 'HToZA', 'GluGlu']):
                binnings['files']['signal'].append(rf)
                type_ = smpNm
                isSignal =True
            elif any(x in smpNm for x in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon']):
                continue # just for now sth wrong with the ranges in rebinCustom step 
                binnings['files']['data'].append(rf)
            elif any( x in smpNm for x in ['DYJetsToLL']):
                binnings['files']['DY'].append(rf)
            elif any( x in smpNm for x in ['TTTo2L2Nu', 'ttbar']):
                binnings['files']['ttbar'].append(rf)
            elif any( x in smpNm for x in ['ST']):
                binnings['files']['ST'].append(rf)

            logger.info( f' working on : {rf}' ) 
            rf_out  = os.path.join(args.output, suffix, f"{smpNm}.root")
            inFile  = HT.openFileAndGet(rf)
            outFile = HT.openFileAndGet(rf_out, "recreate")

            isSys = False
            binnings[smpNm] = collections.defaultdict(dict)
            for key in inFile.GetListOfKeys():
                if not key.GetName().startswith(args.mode):
                    continue
               
                if '__' in key.GetName(): isSys=True
                if not args.sys and isSys: 
                    continue
                
                if args.submit == "test":
                    if not (key.GetName().startswith(f"DNNOutput_ZAnode_MuMu_resolved_DeepCSVM_METCut_gg_fusion") 
                         or key.GetName().startswith(f"DNNOutput_ZAnode_ElEl_resolved_DeepCSVM_METCut_gg_fusion")):
                        continue
                else: # just for now, these catagories are a bit messy 
                    if 'boosted' in key.GetName() or 'DeepFlavourM' in key.GetName() or 'bb_associatedProduction' in key.GetName() or 'MuEl' in key.GetName():
                        continue
                
                if 'gg_fusion' in key.GetName(): process = 'gg_fusion'
                else: process = 'bb_associatedProduction' 
                
                sig = key.GetName().split(process+'_')[-1].replace('MH_', 'MH-').replace('MA_', 'MA-')
                if not key.GetName().split(process+'_')[-1] in available_points(inputs):
                    #logger.info(f'{sig} mass point not found between the .root signal files, will skip this one !')
                    continue
                if isSignal and not key.GetName().endswith(smpNm.split('To2L2B_')[-1].replace('-','_')) and not args.plotit:
                    continue
                
                hist = inFile.Get(key.GetName())
                if not (hist and hist.InheritsFrom("TH1")):
                    continue
                if hist.GetEntries() == 0.:
                    continue
                
                logger.info( f' working on : {key.GetName()}' ) 
                oldHist = inFile.Get(key.GetName())
                
                if not isSys:
                    binnings[smpNm]['histograms'][key.GetName()] = []
                    if not key.GetName() in binnings['histograms']:
                        binnings['histograms'].append(key.GetName())
                
                name = key.GetName() +'_rebin'
                if args.rebin == 'custom':
                    binning = optimizeBinning(oldHist, args.events, args.uncertainty)
                    newEdges= binning[0]
                    newHist = rebinCustom(oldHist, binning, oldHist.GetName())
                    name   += '_custome'

                elif args.rebin == 'standalone':
                    newEdges = []
                    for i in keep_bins:
                        newEdges.append(oldHist.GetXaxis().GetBinLowEdge(i))
                    binning  = [newEdges, keep_bins]
                    newHist  =  rebinCustom(oldHist, binning, oldHist.GetName())
                    name    += '_standalone'
                
                elif args.rebin == 'bayesian':
                    if args.submit =='all':
                        toy  = 'mc'
                        s    = 'scaled_' if args.scale else '' 
                        try:
                            f = open(os.path.join(args.output, f"rebinned_edges_{args.rebin}.json"))
                            data = json.load(f)
                        except Exception as ex:
                            raise RuntimeError(f' -- {ex} occure when reading rebinned_edges_{args.rebin}.json')
                        
                        binning  = hybride_binning( BOnly= data[f'summed_{s}{args.era}{toy}_samples']['histograms'][key.GetName()][0], 
                                                    SOnly= data[f'HToZATo2L2B_{sig}']['histograms'][key.GetName()][0])
                        newHist  = rebinCustom(oldHist,binning, oldHist.GetName())
                        
                        hybridebinning_dict = {'B':data[f'summed_{s}{args.era}{toy}_samples']['histograms'][key.GetName()][0][0],
                                               'S':data[f'HToZATo2L2B_{sig}']['histograms'][key.GetName()][0][0],
                                               'hybride':binning[0]}
                        if isSignal:
                            PLotHybrideHistos( os.path.join(outDir, sumPath, f'summed_{s}{args.era}{toy}_samples.root'), 
                                               oldHist, 
                                               key.GetName(), 
                                               name, 
                                               output               = plotsDIR, 
                                               newEdges             = hybridebinning_dict, 
                                               include_overflow     = False, 
                                               logy                 = args.logy)
                    else: 
                        name   += f'_bayesian'
                        newHist, newEdges, FinalBins = BayesianBlocks(  oldHist, 
                                                                        name, 
                                                                        output           = plotsDIR, 
                                                                        prior            = args.prior, 
                                                                        label            = type_, 
                                                                        logy             = args.logy, 
                                                                        isSignal         = isSignal, 
                                                                        include_overflow = False)
                        binning = [newEdges, FinalBins]
                
                if not isSys:
                    binnings[smpNm]['histograms'][key.GetName()].append(binning)
                
                #print(np.sqrt(sum(list(newHist.GetSumw2())))/newHist.Integral())
                outFile.cd()
                newHist.Write()
            inFile.Close()
            outFile.Close()
            print(' rebinned histogram saved in: {} '.format(os.path.join(args.output, suffix, f"{smpNm}.root")))
       
    if not args.onlypost: 
        with open(os.path.join(args.output, f"rebinned_edges_{args.rebin}{suff}.json"), 'w') as _f:
            json.dump(binnings, _f, indent=2)
        print(' rebinned template saved in : {} '.format(os.path.join(args.output, f"rebinned_edges_{args.rebin}{suff}.json")))
    
    if args.plotit:
        plotRebinnedHistograms(binnings, args.output, mode_, suffix, args.era, args.toys, normalized=args.normalized)
