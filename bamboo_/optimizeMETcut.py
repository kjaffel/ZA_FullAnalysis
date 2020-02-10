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


def getHisto(path, isBkg, prefix, cat):

    _files = set()
    histo_met = TH1F("histo_met", "histo_met", 50, 0, 400)


    integral=0
    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        split_filename = filename.split('/')
        if isBkg:
            if str(split_filename[-1]).startswith("DoubleMuon") or str(split_filename[-1]).startswith("DoubleEG") or str(split_filename[-1]).startswith("MuonEG") or str(split_filename[-1]).startswith("HToZA"):
                continue
        else:
            if not str(split_filename[-1]) == prefix:
                continue
        #print split_filename[-1]
        f = ROOT.TFile.Open(filename)
        _files.add(f)
        for j, key in enumerate(f.GetListOfKeys()):
            tagger= "DeepJetM"   # TODO is to loop over all of them !
            cl = ROOT.gROOT.GetClass(key.GetClassName())
            #if key.ReadObj().GetName() == "met_pt_{0}_hZA_lljj_btag_{1}".format(cat, tagger):
            if key.ReadObj().GetName() == "xycorrmet_pt_{0}_hZA_lljj_btag_{1}".format(cat, tagger):
                key.ReadObj().SetDirectory(0)
                integral = integral + key.ReadObj().Integral()
                histo_met.Add(key.ReadObj(), 1)
        histo_met.SetDirectory(0)  

    #print "INTEGRAL: ", integral*lumi
    # Scale by the luminosity if MC histograms
    if not isBkg:
        histo_met.Scale(50*1000)
    
    return histo_met


def main():

    global lumi
    lumi = 35921.875594646
    path = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/2016LegacyResults_signalsamples/version0/results'
    category = ["MuMu", "ElEl"]
    prefix = []
    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        print("filename:", filename)
        split_filename = filename.split('/')
        if str(split_filename[-1]).startswith("HToZATo2L2B"):
            prefix.append(split_filename[-1])
    
    print("prefix", prefix)
    c = []
    legend = []
    for k, cat in enumerate(category):

        legend.append(ROOT.TLegend(0.85,0.55,0.95,0.95))
        legend[k].SetHeader("{0} category".format(cat))
        histo_met_bkg = getHisto(path, isBkg=True, prefix="", cat=cat)

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
                #Check why for different i, the integral is the same
                histo_met_bkg.SetDirectory(0)
                histo_met_sig = getHisto(path, isBkg=False, prefix=pref, cat=cat)
                histo_met_sig.GetXaxis().SetRangeUser(11, i)
                histo_met_sig.SetDirectory(0)
                #significance = 2*(SQRT(S+B)-SQRT(B))
                #signif = 2*(math.sqrt(histo_met_sig.Integral() + histo_met_bkg.Integral()) - math.sqrt(histo_met_bkg.Integral()))
                S = histo_met_sig.Integral()
                print ("signal Integral", S)
                B = histo_met_bkg.Integral()
                signif = math.sqrt(2*( (S+B)*math.log(1+S/B) -S ))
                print ("prefix: ", pref, "   i: ", i, "   significance: ", signif)
                significance.append(float(signif))
                xAxis.append(float(i))

            significance_array = np.array(significance)
            xAxis_array = np.array(xAxis)
            graph = ROOT.TGraph(int(40), xAxis_array, significance_array)
            graph.SetName(split_prefix[1]+"_"+split_prefix[2])
            graphs.append(graph)

        print (len(graphs))
        c.append(TCanvas("c{0}".format(k),"c{0}".format(k),800,600))
        #c[k].DrawFrame(40,0.0012,160,0.02).SetTitle("Significance vs MET cut; MET cut (GeV); 2(#sqrt{S+B} - #sqrt{B})")
        #c[k].DrawFrame(0,0.0012,160,0.02).SetTitle("Significance vs MET cut; MET cut (GeV); #sqrt{2((S+B)ln(1+S/B)-S)}")
        c[k].DrawFrame(0,0,210,3.5).SetTitle("Significance vs MET cut; MET cut (GeV); #sqrt{2((S+B)ln(1+S/B)-S)}")
        for i, gr in enumerate(graphs):
            legend[k].AddEntry(gr, gr.GetName(), "l")
            gr.Draw("*L")
            if i==0:
                color = ROOT.kRed
            elif i==1:
                color = ROOT.kTeal-5
            elif i==2:
                color = ROOT.kYellow
            elif i==3:
                color = ROOT.kRed-7
            elif i==4:
                color = ROOT.kOrange
            elif i==5:
                color = ROOT.kOrange-3
            elif i==6:
                color = ROOT.kOrange+2
            elif i==7:
                color= ROOT.kGreen-4
            elif i==8:
                color= ROOT.kMagenta-2 
            elif i==9:
                color= ROOT.kMagenta-6 
            elif i==10:
                color= ROOT.kMagenta-9 
            elif i==11:
                color= ROOT.kGreen 
            elif i==12:
                color= ROOT.kGreen+3 
            elif i==13:
                color= ROOT.kGreen-2 
            elif i==14:
                color= ROOT.kGreen-5
            elif i==15:
                color= ROOT.kCyan+1
            elif i==16:
                color= ROOT.kCyan+3
            elif i==17:
                color= ROOT.kBlue
            elif i==18:
                color= ROOT.kBlue+2
            elif i==19:
                color= ROOT.kBlue-9
            elif i==20:
                color= ROOT.kYellow+3
            gr.SetMarkerColor(color)
            gr.SetLineColor(color)
            #ROOT.kMagenta = ROOT.kMagenta+2
            #gr.SetMarkerColor(i*5+2-i)
            #gr.SetLineColor(i*5+2-i)
        legend[k].Draw()
        c[k].cd() 

        c[k].SaveAs("optimizeMETcut_{0}.root".format(cat))
        #del c1


#main
if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)
    main()

