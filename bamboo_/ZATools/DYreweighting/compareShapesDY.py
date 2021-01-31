#! /bin/env python
import sys, os, json
import copy
import datetime
import subprocess
import numpy as np
import glob
import ROOT
import argparse


def getHistos(path, reg, cat, btagger, wp, data, DYReweighting_Nobtag, getDY_NLO, getDY_LO):
    _files = set()
    nlofiles = set()
    lofiles = set()
    histos = []
    
    mjj_histo = ROOT.TH1F("mjj", "mjj", 60, 0., 650.)
    mlljj_histo = ROOT.TH1F("mlljj", "mlljj", 60, 150., 1200.)
    Njets_histo = ROOT.TH1F("Njets", "Njets", 7, 0., 7.)
    mjj_madgraphMLMpythia8_histo =ROOT.TH1F("mjj_lo", 'mjj: MADGRAPGH + PYTHIA8', 60, 0., 650.)
    mlljj_madgraphMLMpythia8_histo =ROOT.TH1F("mlljj_lo", 'mlljj: MADGRAPGH + PYTHIA8', 60, 150., 1200.)
    mjj_amcatnloFXFXpythia8_histo = ROOT.TH1F("mjj_nlo", "mjj: MADGRAPGH_aMC@NLO + PYTHIA8", 60, 0., 650.)
    mlljj_amcatnloFXFXpythia8_histo = ROOT.TH1F("mlljj_nlo", "mlljj: MADGRAPGH_aMC@NLO + PYTHIA8", 60, 150., 1200.)

    mjj_histo.Reset()
    mlljj_histo.Reset()
    Njets_histo.Reset()
    mjj_madgraphMLMpythia8_histo.Reset()
    mlljj_madgraphMLMpythia8_histo.Reset()
    mjj_amcatnloFXFXpythia8_histo.Reset()
    mlljj_amcatnloFXFXpythia8_histo.Reset()


    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        split_filename = filename.split('/')
        
        if data:
            if cat == 'MuMu':
                if not str(split_filename[-1]).startswith("DoubleMuon"):
                    continue
            elif cat == 'ElEl':
                if not str(split_filename[-1]).startswith("DoubleEGamma"):
                    continue

        else:
            if not str(split_filename[-1]).startswith("DY"):
                continue
        
        if getDY_NLO:
            if str(split_filename[-1]).replace(".root","") in ["DYJetsToLL_0J", "DYJetsToLL_1J","DYJetsToLL_2J"]:
                NLO_files = ROOT.TFile.Open(filename)
                nlofiles.add(NLO_files)

                mjj_nlo = NLO_files.Get("{0}_{1}_mjj".format(cat, reg))
                mlljj_nlo = NLO_files.Get("{0}_{1}_mlljj".format(cat, reg))
            
                mjj_amcatnloFXFXpythia8_histo.Add(mjj_nlo, 1)
                mjj_amcatnloFXFXpythia8_histo.SetDirectory(0)
                
                mlljj_amcatnloFXFXpythia8_histo.Add(mlljj_nlo, 1)
                mlljj_amcatnloFXFXpythia8_histo.SetDirectory(0)
        elif getDY_LO: 
            if str(split_filename[-1]).replace(".root","") =="DYJetsToLL_M-10to50":
                LO_files = ROOT.TFile.Open(filename)
                lofiles.add(LO_files)
            
                mjj_lo = LO_files.Get("{0}_{1}_mjj".format(cat, reg))
                mlljj_lo = LO_files.Get("{0}_{1}_mlljj".format(cat, reg))
                    
                mjj_madgraphMLMpythia8_histo.Add(mjj_lo, 1)
                mjj_madgraphMLMpythia8_histo.SetDirectory(0)
                
                mlljj_madgraphMLMpythia8_histo.Add(mlljj_lo, 1)
                mlljj_madgraphMLMpythia8_histo.SetDirectory(0)
        
        elif DYReweighting_Nobtag:
            f = ROOT.TFile.Open(filename)
            _files.add(f)
            
            # FIXME add the b-tagged plots 
            mjj = f.Get("{0}_{1}_mjj".format(cat, reg))
            mlljj = f.Get("{0}_{1}_mlljj".format(cat, reg))
            Njets = f.Get("{0}__NoCutOnJetsLen_{1}_Jet_mulmtiplicity".format(cat, reg))
            
                #else:
                #mjj = f.Get("jj_M_{0}_hZA_{1}_lljj_{2}_btag{3}_mll_and_met_cut".format(cat, reg, btagger, wp))
                #mlljj = f.Get("lljj_M_{0}_hZA_{1}_lljj_{2}_btag{3}_mll_and_met_cut".format(cat, reg, btagger, wp))
        
            mjj_histo.Add(mjj, 1)
            mjj_histo.SetDirectory(0)
            
            mlljj_histo.Add(mlljj, 1)
            mlljj_histo.SetDirectory(0)
    
            Njets_histo.Add(Njets, 1)
            Njets_histo.SetDirectory(0)
        
    if DYReweighting_Nobtag:
        if not data:
            mjj_histo.Scale(lumi)
            mjj_histo.SetDirectory(0)
            mlljj_histo.Scale(lumi)
            mlljj_histo.SetDirectory(0)
            Njets_histo.Scale(lumi)
            Njets_histo.SetDirectory(0)
    elif getDY_NLO:
        mjj_amcatnloFXFXpythia8_histo.Scale(lumi)
        mjj_amcatnloFXFXpythia8_histo.SetDirectory(0)
        mlljj_amcatnloFXFXpythia8_histo.Scale(lumi)
        mlljj_amcatnloFXFXpythia8_histo.SetDirectory(0)
    elif getDY_LO:
        mjj_madgraphMLMpythia8_histo.Scale(lumi)
        mjj_madgraphMLMpythia8_histo.SetDirectory(0)
        mlljj_madgraphMLMpythia8_histo.Scale(lumi)
        mlljj_madgraphMLMpythia8_histo.SetDirectory(0)
    
    if DYReweighting_Nobtag:
        histos.append(mjj_histo)
        histos.append(mlljj_histo)
        histos.append(Njets_histo)
    elif getDY_NLO:
        histos.append(mjj_amcatnloFXFXpythia8_histo)
        histos.append(mlljj_amcatnloFXFXpythia8_histo)
    elif getDY_LO:
        histos.append(mjj_madgraphMLMpythia8_histo)
        histos.append(mlljj_madgraphMLMpythia8_histo)
    return histos


def main():

    global lumi
    lumi = 41529.152060112
    era = '2017'
    #path ='/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.15.05/results/'     
    path ='/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.7/results/'     
    
    categories = ['MuMu', 'ElEl']
    # I don't care about [ 'MuEl', 'ElMu', 'comb'] bkg mainly ttbar 
    regions = ['resolved']#, 'boosted']

    ROOT.gStyle.SetOptStat(0)
    DYReweighting_Nobtag = True
    split_mc =True 
    for cat in categories:
        for reg in regions :

            if reg =='resolved':
                taggers = [None, 'DeepCSV' , 'DeepFlavour']
            elif reg =='boosted':
                taggers = [None, 'DeepCSV', 'DeepDoubleBvL']
            
            for btagger in taggers :

                WorkingPoints = [None]
                if DYReweighting_Nobtag:
                    if btagger !=None:
                        continue
                else: 
                    if reg =='resolved':
                        WorkingPoints = ['L', 'M', 'T']
                    elif reg == 'boosted' and btagger =='DeepCSV':
                        WorkingPoints = ['L', 'M']
                    elif reg == 'boosted' and btagger =='DeepDoubleBvL':
                        WorkingPoints = ['L', 'M1', 'M2', 'T1', 'T2']
            
                for wp in WorkingPoints:

                    suffix = ('Nobtag' if DYReweighting_Nobtag else (btagger+wp))
                    latexOpts = ('e^{+}e^{-}' if cat=='ElEl' 
                                                else( '#mu^{+}#mu^{-}' if cat =='MuMu' 
                                                    else( 'e^{+}#mu^{-}' if cat =='ElMu' 
                                                        else ('e^{+}#mu^{-}' if cat == 'MuEl' 
                                                            else( 'e^{#pm}#mu^{#pm}')))))
    
                    histos_data = []
                    histos_MC = []
                    histos_NLOMC = []
                    histos_LOMC = []
                    
                    histos_data = getHistos(path, reg, cat, btagger, wp, data=True, DYReweighting_Nobtag=True, getDY_NLO=False, getDY_LO=False)
                    histos_MC   = getHistos(path,  reg, cat, btagger, wp, data=False, DYReweighting_Nobtag=True, getDY_NLO=False, getDY_LO=False)
                    histos_NLOMC = getHistos(path, reg, cat, btagger, wp, data=False, DYReweighting_Nobtag=False, getDY_NLO=True, getDY_LO=False)
                    histos_LOMC = getHistos(path,  reg, cat, btagger, wp, data=False, DYReweighting_Nobtag=False, getDY_NLO=False, getDY_LO=True)

        
                    legend = []
                    c1 = []
                    pad1 = []
                    pad2 = []

                    for i, var in zip(range(0, len(histos_data)), ['mjj', 'mlljj']):
                        print ( i, len(histos_NLOMC), len(histos_data), len(histos_MC))
                        print ("Inetgrals %s ***  "%var, cat, " channel:", ", region:", reg ,', tagger:',  btagger, ', workingPoint:',  wp)
                        print ("histos_data[%s].Integral() : "%var, histos_data[i].Integral())
                        print ("histos_MC[%s].Integral()   : "%var, histos_MC[i].Integral())
                        print ("histos_NLOMC[%s].Integral(): "%var, histos_NLOMC[i].Integral())
                        print ("histos_LOMC[%s].Integral() : "%var, histos_LOMC[i].Integral())
                        print ("=============================================================================")
                        #Normalize both data and MC to 1
                        c1.append(ROOT.TCanvas("c1", "c1", 600, 600))
                        pad1.append(ROOT.TPad("pad1", "pad1", 0, 0.0, 1, 1.0))
                        #pad1[i].SetBottomMargin(0.15)
                        pad1[i].SetBottomMargin(0.32)
                        pad1[i].SetLeftMargin(0.15)
                        pad1[i].SetRightMargin(0.1)
                        
                        #pad1.append(ROOT.TPad("pad1","pad1",0,0.3,1,0.9))
                        #pad1[i].SetBottomMargin(0)
                        pad1[i].Draw()
                        pad1[i].cd()

                        histos_data[i].SetMarkerColor(ROOT.kRed)
                        histos_data[i].SetMarkerStyle(20)
                        histos_data[i].GetXaxis().SetTitle( '%s [GeV]'% var)
                        histos_data[i].GetYaxis().SetTitle( 'Events')
                        
                        histos_MC[i].SetMarkerColor(ROOT.kBlue)
                        histos_MC[i].SetMarkerStyle(22)
                        histos_MC[i].GetXaxis().SetTitle( '%s [GeV]'% var)
                        histos_MC[i].GetYaxis().SetTitle( 'Events')
                        
                        # split DY samples 
                        histos_NLOMC[i].SetMarkerColor(ROOT.kCyan)
                        histos_NLOMC[i].SetMarkerStyle(21)
                        histos_NLOMC[i].GetXaxis().SetTitle( '%s [GeV]'% var)
                        histos_NLOMC[i].GetYaxis().SetTitle( 'Events')

                        histos_LOMC[i].SetMarkerColor(ROOT.kViolet)
                        histos_LOMC[i].SetMarkerStyle(22)
                        histos_LOMC[i].GetXaxis().SetTitle( '%s [GeV]'% var)
                        histos_LOMC[i].GetYaxis().SetTitle( 'Events')


                        histos_data[i].Scale(1./histos_data[i].Integral())
                        histos_MC[i].Scale(1./histos_MC[i].Integral())
                        histos_NLOMC[i].Scale(1./histos_NLOMC[i].Integral())
                        #histos_LOMC[i].Scale(1./histos_LOMC[i].Integral())
                        histos_data[i].Draw("")
                        histos_NLOMC[i].Draw("same")
                        histos_MC[i].Draw("same")
                        histos_LOMC[i].Draw("same")
                        
                        legend.append(ROOT.TLegend(0.5,0.8,0.89,0.89))
                        legend[i].SetTextSize(0.015)
                        legend[i].SetHeader(" Z+Jets: {0} channel ".format(latexOpts))
                        legend[i].AddEntry(histos_data[i], "Data", "p")
                        legend[i].AddEntry(histos_MC[i], "DY MC", "p")
                        legend[i].AddEntry(histos_NLOMC[i], "NLO: MADGRAPGH_aMC@NLO + PYTHIA8", "p")
                        legend[i].AddEntry(histos_LOMC[i], "LO: MADGRAPGH + PYTHIA8", "p")
                        legend[i].Draw("same")
                        
                        c1[i].cd()
#                        pad2.append(ROOT.TPad("pad2", "pad2", 0, 0.0, 1, 0.3))
#                        pad2[i].SetTopMargin(0)
#                        pad2[i].SetBottomMargin(0.4)
#                        pad2[i].SetLeftMargin(0.15)
#                        pad1[i].SetRightMargin(0.1)
#
#                        pad2.append(ROOT.TPad("pad2","pad2",0, 0.05, 1, 0.3))
#                        pad2[i].SetTopMargin(0)
#                        pad2[i].SetBottomMargin(0.3)
#                        pad2[i].Draw()
#                        pad2[i].cd()
#
#                        if split_mc:
#                            ratio = histos_NLOMC[i].Clone()
#                            ratio.GetYaxis().SetTitle("aMC@NLO/Madgraph+Pythia8")
#                          
#                        else:
#                            ratio = histos_data[i].Clone()
#                            ratio.GetYaxis().SetTitle("Data/MC")
#                         
#                        ratio.GetYaxis().SetTitle("%s [GeV]"% var)
#                        histos_NLOMC[i].GetXaxis().SetLabelSize(0.)
#                        histos_NLOMC[i].GetXaxis().SetTitle('')
#                        
#                        ratio.SetTitle("")
#                        ratio.Sumw2()
#                        if split_mc:
#                            ratio.Divide(histos_LOMC[i])
#                        else:
#                            ratio.Divide(histos_MC[i])
#                        ratio.SetMarkerColor(ROOT.kBlack)
#                        ratio.SetMarkerSize(0.8)
#                        ratio.SetStats(0)
#                        ratio.GetYaxis().SetRangeUser(0.4,1.6)
#                        ratio.GetXaxis().SetLabelFont(43)
#                        ratio.GetXaxis().SetLabelSize(15)
#                        ratio.GetYaxis().SetLabelFont(43)
#                        ratio.GetYaxis().SetLabelSize(15)
#                         
#                        ratio.Draw("ep")
#                        ratio.Draw("same")
#                        
#                        line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1, ratio.GetXaxis().GetXmax(), 1)
#                        line.SetLineColor(ROOT.kBlack)
#                        line.Draw("")
#                        
                        c1[i].cd()
                        c1[i].SaveAs("compareDYShapes__{0}/{1}_{2}_{3}_{4}.pdf".format(era, reg, cat, suffix, var))
                        c1[i].SaveAs("compareDYShapes__{0}/{1}_{2}_{3}_{4}.png".format(era, reg, cat, suffix, var))
#        
#                    
if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)
    main()

