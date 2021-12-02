#!/usr/bin/env python
import argparse
import json
import glob
import os
import random
import itertools
import math
import subprocess
import numpy as np
import ROOT as R
R.gROOT.SetBatch(True)
from faker import Factory
fake = Factory.create()
import Harvester as H
import HistogramTools as HT
import Constants as Constants
logger = Constants.ZAlogger(__name__)

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
        print( '='*30)
        print( f'bin {upEdge} :  BinError= {hist.GetBinError(upEdge)}, BinContent= {hist.GetBinContent(upEdge)}')#, {hist.GetSumw2(upEdge)}')
        # This is my threshold:"having at least a yield (i.e. sum of weights in the bin) of 1 for the background 
        #                       and 1 for the signal, 
        #                       plus having statistical uncertainty in both of at least maxUncertainty*100 % "
        while uncertainty < maxUncertainty or content < maxEvents:
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


def rebinCustom(hist, binning, name):
    """ Rebin 1D hist using bin numbers and edges as returned by optimizeBinning() """

    edges = binning[0]
    nBins = len(edges) -1
    oldNbins = hist.GetNbinsX()
    print( f'name: {name}, Title: {hist.GetTitle()}, nbinsx: {nBins}, xlow, xup : {np.array(edges)}' )
    newHist  = R.TH1D(name, hist.GetTitle(), nBins, np.array(edges))
    newHist.Sumw2()
    oldSumw2 = list(hist.GetSumw2())

    for newBinX in range(1, nBins + 2):
        content = 0
        sumw2   = 0
        maxOldBinX = binning[1][newBinX] if newBinX <= nBins else oldNbins + 2
        for oldBinX in range(binning[1][newBinX - 1], maxOldBinX):
            content += hist.GetBinContent(oldBinX)
            sumw2   += oldSumw2[hist.GetBin(oldBinX)]
        print( f'merging bins {binning[1][newBinX-1]} -> {maxOldBinX} : BinContent = {content}')
        newHist.SetBinContent(newBinX, content)
        newHist.GetSumw2()[newHist.GetBin(newBinX)] = sumw2

    return newHist

def plotRebinnedHistograms(inDir, files, to_plot, folder, norm=True):
    plotsDIR = os.path.join(folder, "plots")
    if not os.path.isdir(plotsDIR):
        os.makedirs(plotsDIR)
    
    smpConfig  = H.getnormalisationScale(inDir, method=None, seperate=True)
    lumiconfig = smpConfig['configuration']
    """
    smpConfig = {"Configurations": {}
                 smp_signal : [era, lumi, xsc , generated-events, br],
                 smp_mc     : [era, lumi, xsc , generated-events, None], 
                 smp_data   : [era, None, None, None,           , None] }
    """
    with open(f"data/rebinned_template.yml", 'r') as inf:
        with open(f"{folder}/plots.yml", 'w+') as outf:
            for line in inf:
                if "  root: myroot_path" in line:
                    outf.write(f"  root: {folder}/standalone_rebin/\n")
                elif "files:" in line:
                    outf.write("files:\n")
                    for kf, vf in files.items():
                        if not vf:
                            continue
                        if kf == 'data':
                            continue # bug need to be solved first 
                        _type = kf if kf in ['data', 'signal'] else 'mc'
                        color = fake.hex_color()
                        for root_f in vf:
                            smp    = root_f.split('/')[-1]
                            era    = smpConfig[smp][0]
                            lumi   = smpConfig[smp][1]
                            xsc    = smpConfig[smp][2]
                            genevt = smpConfig[smp][3]
                            br     = smpConfig[smp][4]
                            
                            outf.write(f"  {smp}:\n")
                            outf.write(f"    type: {_type}\n")
                            outf.write(f"    group: {kf}\n")
                            outf.write(f"    era: {era}\n")
                            
                            if _type == 'signal':
                                outf.write(f"    legend: {smp.split('.root')[0]}\n")
                                outf.write(f"    line-color: '{color}'\n")
                                outf.write("    line-type: 1\n")
                                if norm:
                                    outf.write(f"    Branching-ratio: {br}\n")
                                    outf.write(f"    generated-events: {genevt}\n")
                                    outf.write(f"    cross-section: {xsc} # pb\n")
                            elif _type == 'mc' and norm:
                                    outf.write(f"    generated-events: {genevt}\n")
                                    outf.write(f"    cross-section: {xsc} # pb\n")
                elif "  - myera" in line:
                    for era in lumiconfig.keys():
                        outf.write(f"  - {era}\n")
                elif "    myera: mylumi" in line:
                    for era, lumi in lumiconfig.items():
                        outf.write(f"    {era}: {lumi}\n")
                elif "plots:" in line:
                    outf.write("plots:\n")
                    for plotNm in to_plot:
                        infos  = plotNm.split('_')
                        flavor = infos[2].lower()
                        region = infos[3]
                        signal_smp = f'MH-{infos[9]}_MA-{infos[10]}'
                        outf.write(f"  {plotNm}:\n")
                        outf.write("    blinded-range: [0.6, 1.0]\n")
                        outf.write("    labels:\n")
                        outf.write("    - position: [0.22, 0.895]\n")
                        outf.write("      size: 24\n")
                        outf.write(f"      text: {flavor}\n")
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file', required=True)
    parser.add_argument('-o', '--output', help='json output file name for new binning', required=True)
    parser.add_argument('-u', '--uncertainty', type=float, default=0.008, help='max stat. uncertainty')
    parser.add_argument('-e', '--events', type=float, default=10e2, help='max entries in bins')
    parser.add_argument('-r', '--rebin', action='store', choices= ['custom', 'standalone'], required=True, 
                            help='compute new binning by setting some treshold on the uncer and number of events\n'
                                 'or just re-arrange the oldbins to merge few bins into one, starting from the left to the right\n')
    args = parser.parse_args()
    era = '2016' 
    keep_bins = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 52] 
    suffix  = "custom_rebin" if args.rebin =="custom" else "standalone_rebin"
    
    if not os.path.isdir(os.path.join(args.output, suffix)):
        os.makedirs(os.path.join(args.output, suffix))
    list_inputs = glob.glob(os.path.join(args.input, 'results', '*.root'))
  
    path_to_hadded_f = os.path.join(args.output, "inputs")
    if not os.path.isdir(path_to_hadded_f):
        os.makedirs(path_to_hadded_f)
    
    if not os.listdir(path_to_hadded_f):
        sorted_inputs= {'data'  :[], 
                        'mc'    :[], 
                        'signal':[] }
        
        for rf in list_inputs:
            smpNm = rf.split('/')[-1].replace('.root','')
            if smpNm.startswith('__skeleton__'):
                continue
            if any(x in smpNm for x in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon']):
                sorted_inputs['data'].append(rf)
            elif any(x in smpNm for x in ['AToZH', 'HToZA', 'GluGlu']):
                sorted_inputs['signal'].append(rf)
            else:
                sorted_inputs['mc'].append(rf)

        for k, val in sorted_inputs.items():
            haddCmd = ["hadd", "-f", os.path.join(args.output, 'inputs', f"summed_{era}{k}_samples.root")]+val
            try:
                logger.info("running {}".format(" ".join(haddCmd)))
                subprocess.check_call(haddCmd)#, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                logger.error("Failed to run {0}".format(" ".join(haddCmd)))
    else:
        logger.info(f'directory {path_to_hadded_f}/ exist and not empty, skipping hadd step, if you have an updated files version rm dir and run again!' )
    
    if args.rebin == 'custom':
        inputs = glob.glob(os.path.join(args.output, 'inputs', '*.root')) 
    else:
        inputs = list_inputs

    binnings = {}
    files    = {'signal': [],
                'data'  : [],
                'DY'    : [],
                'ttbar' : [],
                'ST'    : [] }
    
    for rf in inputs:
        smpNm = rf.split('/')[-1].replace('.root','')
        if 'data' in smpNm:
            continue
        if 'signal' in smpNm:
            continue
        if smpNm.startswith('__skeleton__'):
            continue

        if any(x in smpNm for x in ['AToZH', 'HToZA', 'GluGlu']):
            files['signal'].append(rf)
        elif any(x in smpNm for x in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon']):
            files['data'].append(rf)
            #continue # just for now sth wrong with the ranges in rebinCustom step 
        elif any( x in smpNm for x in ['DYJetsToLL']):
            files['DY'].append(rf)
        elif any( x in smpNm for x in ['TTTo2L2Nu', 'ttbar']):
            files['ttbar'].append(rf)
        elif any( x in smpNm for x in ['ST']):
            files['ST'].append(rf)

        print( ' working on :', rf ) 
        rf_out  = os.path.join(args.output, suffix, f"{smpNm}.root")
        inFile  = HT.openFileAndGet(rf)
        outFile = HT.openFileAndGet(rf_out, "recreate")

        nameTemplate = 'DNNOutput_ZAnode_ElEl_resolved_DeepCSVM_METCut_gg_fusion_MH_650_MA_50'
        binnings[nameTemplate] = []
        to_plot = []
        for key in inFile.GetListOfKeys():
            if not key.GetName().startswith(nameTemplate):
                continue
            if '__' in key.GetName(): # ignore systematics histograms let's look only to the nominal
                continue
            
            oldHist = inFile.Get(key.GetName())
            to_plot.append(key.GetName() + '_rebin')
            
            name = f'{nameTemplate}' +'__rebin'
            if args.rebin == 'custom':
                binning = optimizeBinning(oldHist, args.events, args.uncertainty)
                binnings[nameTemplate].append(binning[0])
                newHist = rebinCustom(oldHist, binning, oldHist.GetName() + "_rebin")
                name   += '_custome'
            else:
                # FIXME different for each catgories
                equiv_edges = []
                for i in keep_bins:
                    equiv_edges.append(oldHist.GetXaxis().GetBinLowEdge(i))
                binning  = [equiv_edges, keep_bins]
                newHist  =  rebinCustom(oldHist, binning, oldHist.GetName() + "_rebin")
                name    += '_standalone'
            
            print(np.sqrt(sum(list(newHist.GetSumw2())))/newHist.Integral())
            outFile.cd()
            newHist.Write()
        inFile.Close()
        outFile.Close()
        print(' rebinned histogram saved in: {} '.format(os.path.join(args.output, "rebinned_histograms", f"{smpNm}.root")))
    
    plotRebinnedHistograms(os.path.join(args.input, 'results'), files, to_plot, args.output, norm=True)
    
    with open(os.path.join(args.output, f"rebinned_edges.json"), 'w') as _f:
        json.dump(binnings, _f, indent=4)
    print(' rebinned template saved in : {} '.format(os.path.join(args.output, "rebinned_edges.json")))
