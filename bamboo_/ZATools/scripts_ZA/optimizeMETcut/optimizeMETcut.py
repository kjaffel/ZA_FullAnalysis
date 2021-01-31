# To optimize the cut on MET, we need the met_pt distribution for:
# 1) One signal sample (then it has to be extended to the 21)
# 2) All the backgrounds

#Things to do: add all the backgrounds together in order to have two superimposed histograms, one for the background and one for the signal.
# Then vary the met cut bin by bin and get the integral of the backrounds histo and of the signal histo and compute S/sqrt(B)

#! /bin/env python
import sys, os, json
import copy
import datetime
import subprocess
import numpy as np
import math
import glob
import ROOT
from ROOT import TCanvas, TPad, TLine, TH1F

import argparse
from random import randint


def getHisto(path, isBkg, prefix, reg, tagger, cat):

    _files = set()
    histo_met = TH1F("histo_met", "histo_met", 60, 0, 600)

    integral=0
    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        split_filename = filename.split('/')
        if str(split_filename[-1]).startswith('__skeleton__'):
            continue
        if isBkg:
            if str(split_filename[-1]).startswith("DoubleMuon") or str(split_filename[-1]).startswith("DoubleEG") or str(split_filename[-1]).startswith("MuonEG") or str(split_filename[-1]).startswith("HToZA"):
                continue
        else:
            if not str(split_filename[-1]) == prefix:
                continue
        f = ROOT.TFile.Open(filename)
        _files.add(f)
        for j, key in enumerate(f.GetListOfKeys()):
            cl = ROOT.gROOT.GetClass(key.GetClassName())
            if key.ReadObj().GetName() == "xycorrmet_pt_{0}_{1}_hZA_lljj_{2}M".format(reg, cat, tagger):
                key.ReadObj().SetDirectory(0)
                integral = integral + key.ReadObj().Integral()
                histo_met.Add(key.ReadObj(), 1)
        histo_met.SetDirectory(0)  
    return histo_met


def main():

    global lumi
    lumi = 35921.875594646
    #path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/version20_02_19/ellipses_metcut_bjets_/results'
    #path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/version20_04_01/plots_toOptimizeMETCut/'
    path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/ver.20_04_01/plots_toOptimizeMETCut/'
    category = ["MuMu", "ElEl", "MuEl"]
    prefix = []
    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        #print("filename:", filename)
        split_filename = filename.split('/')
        if str(split_filename[-1]).startswith("HToZATo2L2B"):
            prefix.append(split_filename[-1])
    
    c = []
    legend = []
    taggers=["DeepCSV"]
    
    for reg in ['resolved']:#, 'boosted']:
        if reg=='resovled':
            taggers.append("DeepFlavour")
        for tagger in taggers:
            for k, cat in enumerate(category):
    
                legend.append(ROOT.TLegend(0.85,0.55,0.95,0.95))
                legend[k].SetHeader("{0} category".format(cat))
                histo_met_bkg = getHisto(path, isBkg=True, prefix="", reg=reg, tagger=tagger, cat=cat)

                i=0
                graphs = []
                for pref in prefix:
                    split_prefix = pref.split("_")
                    if "2000" in pref or "3000" in pref:
                        continue
                    significance = []
                    xAxis = []
                    for i in range(0, 201, 5):
                        histo_met_bkg.GetXaxis().SetRangeUser(11, i)
                        histo_met_bkg.GetYaxis().SetRangeUser(0, 1.0)
                        #Check why for different i, the integral is the same
                        histo_met_bkg.SetDirectory(0)
                        histo_met_sig = getHisto(path, isBkg=False, prefix=pref, reg=reg, tagger=tagger, cat=cat)
                        histo_met_sig.GetXaxis().SetRangeUser(11, i)
                        histo_met_sig.GetYaxis().SetRangeUser(0, 1.0)
                        histo_met_sig.SetDirectory(0)
                        #significance = 2*(SQRT(S+B)-SQRT(B))
                        #signif = 2*(math.sqrt(histo_met_sig.Integral() + histo_met_bkg.Integral()) - math.sqrt(histo_met_bkg.Integral()))
                        S = histo_met_sig.Integral()
                        B = histo_met_bkg.Integral()
                        #print ("signal Integral", S, "Background Integral:" , B)
                        signif = math.sqrt(2*( (S+B)*math.log(1+S/B) -S ))
                        #print ("signal: ", pref, "   MET_pT: ", i, "   significance: ", signif)
                        significance.append(float(signif))
                        xAxis.append(float(i))
    
                    significance_array = np.array(significance)
                    xAxis_array = np.array(xAxis)
                    graph = ROOT.TGraph(int(40), xAxis_array, significance_array)
                    graph.SetName(split_prefix[1]+"_"+split_prefix[2])
                    graphs.append(graph)
        
                c.append(TCanvas("c{0}".format(k),"c{0}".format(k),800,600))
                #c[k].DrawFrame(40,0.0012,160,0.02).SetTitle("Significance vs MET cut; MET cut (GeV); 2(#sqrt{S+B} - #sqrt{B})")
                #c[k].DrawFrame(0,0.0012,160,0.02).SetTitle("Significance vs MET cut; MET cut (GeV); #sqrt{2((S+B)ln(1+S/B)-S)}")
                c[k].DrawFrame(0,0,210,3.5).SetTitle("Significance vs MET cut; MET cut (GeV); #sqrt{2((S+B)ln(1+S/B)-S)}")
        
                colors= [ROOT.kRed, ROOT.kTeal-5, ROOT.kYellow, ROOT.kRed-7, ROOT.kOrange, ROOT.kOrange-3, ROOT.kOrange+2, ROOT.kGreen-4, ROOT.kMagenta-2, ROOT.kMagenta-6, ROOT.kMagenta-9, ROOT.kGreen, ROOT.kGreen+3, ROOT.kGreen-2, ROOT.kGreen-5, ROOT.kCyan+1, ROOT.kCyan+3, ROOT.kBlue, ROOT.kBlue+2, ROOT.kBlue-9, ROOT.kYellow+3 ]
                for gr, color in zip(graphs, colors):
                    legend[k].AddEntry(gr, gr.GetName(), "l")
                    gr.Draw("*L")
                    gr.SetMarkerColor(color)
                    gr.SetLineColor(color)
                legend[k].Draw()
                c[k].cd() 
    
                c[k].SaveAs("optimizeMETcut_{0}_{1}_{2}M.png".format(reg, cat.lower(), tagger.lower()))
                #del c1
if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)
    main()

