#!/usr/bin/env python
import argparse
import json
import glob
import os
import random
import itertools
import math

import numpy as np
import ROOT as R
R.gROOT.SetBatch(True)

import HistogramTools as HT

def optimizeBinning(hist, maxUncertainty, acceptLargerOverFlowUncert=True):
    """ Optimize binning, return result in the form of:
        (list of edges, list of bin numbers of original histo)
        args:
            - acceptLargerOFlowUncert: if false, will always merge overflow with previous bin
                                        to ensure the overflow uncertainty is below the threshold
    """
    #bin = 0; underflow bin
    #bin = 1; first bin with low-edge xlow INCLUDED
    #bin = nbins; last bin with upper-edge xup EXCLUDED
    #bin = nbins+1; overflow bin

    # Find first bin with non-zero content
    startBin = 0
    NBins = hist.GetNbinsX()
    for i in range(0, NBins + 1):
        if hist.GetBinContent(i) == 0.:
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
        content     = 0 #binContents[upEdge] 
        sumw2       = 0 #binSumW2[upEdge]  
        uncertainty = 0 #np.sqrt(sumw2) / content 
        print( f'bin {upEdge} :  {uncertainty}, {content}, {sumw2}')
        print( '='*30)
        while uncertainty < maxUncertainty:
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
            print( f'\tbin:{upEdge} lowedge:%.2f ==>  {uncertainty}, {content}, {sumw2}'%lowedge)
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

def plotSlices(hist, name, folder, norm=True):

    style = HT.setTDRStyle()
    style.SetMarkerStyle(0)

    c = R.TCanvas("c", "c")

    colors = itertools.cycle([
        "#7044f1",
        "#45ad95",
        "#c07f00",
        "#da7fb7",
        "#ff2719",
        "#251c00"]
    )

    nBins = hist.GetNbinsX()
    projs = []
    legEntries = []
    # get all projections in the reco axis including the gen overflow bin
    for xBin in range(1, nBins + 2):
        projs.append(hist.ProjectionY(name + str(xBin), xBin, xBin))
        upEdge = hist.GetXaxis().GetBinLowEdge(xBin+1) if xBin <= nBins else -1
        legEntries.append(f"Gen {name} from {hist.GetXaxis().GetBinLowEdge(xBin):.2f} to {upEdge:.2f}")

    projs[0].SetLineWidth(2)
    projs[0].SetLineStyle(2)
    projs[0].SetLineColor(R.TColor.GetColor(next(colors)))
    projs[0].GetYaxis().SetLabelSize(0.03)
    projs[0].GetYaxis().SetTitleSize(0.03)
    projs[0].GetYaxis().SetTitleOffset(1.7)
    # projs[0].GetYaxis().SetTitle("Events")
    projs[0].GetXaxis().SetTitle("Reco " + name)
    projs[0].GetXaxis().SetLabelSize(0.03)
    projs[0].GetXaxis().SetTitleSize(0.03)
    # projs[0].GetXaxis().SetLabelOffset(0.05)
    projs[0].GetXaxis().SetTitleOffset(1.5)
    if norm:
        # include the overflow in the integrals
        projs[0].Scale(1./projs[0].Integral(1, nBins + 1))
    projs[0].Draw("Lhist")
    projs[0].Draw("E0same")

    for i, proj in enumerate(projs[1:]):
        proj.SetLineWidth(2)
        proj.SetLineColor(R.TColor.GetColor(next(colors)))
        proj.SetLineStyle(2)
        if norm:
            proj.Scale(1./proj.Integral(1, nBins + 1))
        proj.Draw("Lhistsame")
        proj.Draw("E0same")
        # make sure we also draw the overflow bin
        proj.GetXaxis().SetRange(1, nBins + 1)
    
    histMax = -100
    histMin = 9999999
    for i in range(1, projs[0].GetNbinsX() + 2):
        histMax = max(histMax, *[h.GetBinContent(i) for h in projs])
        histMin = min(histMin, *[h.GetBinContent(i) for h in projs])
    projs[0].GetYaxis().SetRangeUser(0, histMax * 1.6)
    projs[0].GetXaxis().SetRange(1, nBins + 1)

    l = R.TLegend(0.53, 0.65, 0.98, 0.92)
    l.SetTextFont(42)
    l.SetFillColor(R.kWhite)
    l.SetFillStyle(0)
    l.SetBorderSize(0)

    for i in range(len(projs)):
        l.AddEntry(projs[i], legEntries[i])
    l.Draw("same")

    c.SaveAs(os.path.join(folder, name + ".pdf"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file', required=True)
    parser.add_argument('-o', '--output', help='json output file name for new binning', required=True)
    parser.add_argument('-u', '--uncertainty', type=float, default=0.3, help='max stat. uncertainty')
    parser.add_argument('-c', '--compute', action='store_true', help='compute new binning and rebin 2D histograms before plotting them')
    args = parser.parse_args()
    
    
    if not os.path.isdir(os.path.join(args.output, "rebinned_histograms")):
        os.makedirs(os.path.join(args.output, "rebinned_histograms"))
    list_inputs = glob.glob(os.path.join(args.input, 'results', '*.root'))
    for rf in list_inputs:
        smp = rf.split('/')[-1].replace('.root','')
        if smp.startswith('__skeleton__'):
            continue
        if not smp.startswith('DYJetsToLL_0J_postVFP'): # just for test 
            continue
        print( ' working on :', rf ) 
        inFile  = HT.openFileAndGet(rf)
        outFile = HT.openFileAndGet(os.path.join(args.output, "rebinned_histograms", f"{smp}.root"), "recreate")

        nameTemplate = 'DNNOutput_ZAnode_ElEl_resolved_DeepFlavourM_METCut_bb_associatedProduction_MH_650_MA_50'
        
        binnings = {}
        for key in inFile.GetListOfKeys():
            if not key.GetName().startswith(nameTemplate):
                continue
            if '__' in key.GetName(): # let's look only to the nominal
                continue
            oldHist = inFile.Get(key.GetName())
            if args.compute:
                binning = optimizeBinning(oldHist, args.uncertainty)
                binnings[nameTemplate] = binning[0]
                newHist = rebinCustom(oldHist, binning, oldHist.GetName() + "_rebin")
            else:
                newHist = oldHist
            outFile.cd()
            #print(np.sqrt(sum(list(newHist.GetSumw2())))/newHist.Integral())
            newHist.Write()
            #plotSlices(newHist, smp, args.output, "rebinned_histograms")
        print(' rebinned histogram saved in: {} '.format(os.path.join(args.output, "rebinned_histograms", f"{smp}.root")))
        if args.compute:
            with open(f"{smp}_rebinned.json", 'w') as _f:
                json.dump(binnings, _f)
        inFile.Close()
        outFile.Close()
