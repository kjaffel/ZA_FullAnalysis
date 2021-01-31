#! /bin/env python

import sys, os, json
import copy
import numpy as np
import glob
import re
import os.path
import ROOT
from ROOT import TCanvas, TPad, TLine
from ROOT import kBlack, kBlue, kRed
import argparse

def getHisto(path, reg, prefix, list_BinEdges, bin_, isData, splitDY_acrossplane):
    
    _files = set()
    if not splitDY_acrossplane:
        histo = ROOT.TH1F(prefix +"_%s"%("data" if isData else ("mc")), prefix, 60, 0., 1200.)
    else:
        if prefix =="Jet_mulmtiplicity":
            histo = ROOT.TH1F(prefix +"_%s"%("data" if isData else ("mc")), "Jet_mulmtiplicity", 7, 0., 7.)
        else:
            histo = ROOT.TH1F(prefix +"_%s"%("data" if isData else ("mc")), prefix, 60, list_BinEdges[bin_], list_BinEdges[bin_+1])

    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        split_filename = filename.split('/')
        if isData:
            if not str(split_filename[-1]).startswith("DoubleEGamma") and not str(split_filename[-1]).startswith("DoubleMuon"):
                continue
        else:
            if not str(split_filename[-1]).startswith("DYJetsToLL_0J") and not str(split_filename[-1]).startswith("DYJetsToLL_1J") and not str(split_filename[-1]).startswith("DYJetsToLL_2J"):
                continue
        #print ("INFO. I am looking only to the NLO DY +Jets samples, DYJetsToLL_M-10to50 yields is 0 ") 
        f = ROOT.TFile.Open(filename)
        _files.add(f)
        print (filename)
       # for j, key in enumerate(f.GetListOfKeys()):
       #     if (key.ReadObj().GetName().endswith(prefix) 
       #         and "MuEl" not in key.ReadObj().GetName() 
       #         and "ElMu" not in key.ReadObj().GetName() 
       #         and reg in key.ReadObj().GetName() 
       #         and "mlljj_vs_mjj" not in key.ReadObj().GetName() 
       #         and "fitpolynomial" not in key.ReadObj().GetName()):                
       #         print ("histo Name: ", key.ReadObj().GetName())
       #         histo.Add(key.ReadObj(), 1)
       # 
        #for j, key in enumerate(f.GetListOfKeys()):
        for cat in ["MuMu", "ElEl"]:
            if splitDY_acrossplane:
                supressWgt0 = ( bin_+2 if prefix =='mlljj' else ( bin_+1))
                varToPlots_histo = f.Get("{0}_{1}_DY_weight{2}_{3}".format(cat, reg, supressWgt0, prefix))
            else: 
                varToPlots_histo = f.Get("{0}_{1}_noDYweight_{2}".format(cat, reg, prefix))
            if prefix == "Jet_mulmtiplicity":
                varToPlots_histo = f.Get("{0}__NoCutOnJetsLen_{1}_Jet_mulmtiplicity".format(cat, reg))
    
            histo.Add(varToPlots_histo, 1)
            histo.SetDirectory(0)

        #f.Close()
    if not isData:
        print ("Scale by the lumi : ", lumi)
        histo.Scale(lumi)

    return histo

def main():

    global lumi , mjj_BinEdges, mlljj_BinEdges
    lumi = 41529.152060112
    mjj_BinEdges   = [0., 100., 250., 400., 550.,700., 850., 1000., 1200.]
    mlljj_BinEdges = [100., 150., 300., 450.,600., 750., 1000., 1200.]
    #files_path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.15.05/results'
    #files_path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.7/results'
    files_path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.8/ver20.05.28/results'
    #files_path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.9/results'

    splitDY_acrossplane= False

    pathtoRoot = os.path.join(os.getcwd(), "fitPlots_2017new")
    if not os.path.exists(pathtoRoot):
        os.makedirs(pathtoRoot)
    
    print (pathtoRoot)
    for reg in ['resolved']:#, 'boosted']:
    
        for idx, varToPlot in enumerate(['mjj', 'mlljj']):#, "_NoCutOnJetsLen_{0}_Jet_mulmtiplicity".format(reg)]):
           
            list_BinEdges = (mjj_BinEdges if varToPlot== 'mjj' else ( mlljj_BinEdges)) 
            suffix = (varToPlot if idx !=2 else ( varToPlot.replace( "_NoCutOnJetsLen_{0}".format(reg), "")))
            for bin_ in range(0,len(list_BinEdges)-1):
        
                supressWgt0 = ( bin_+2 if varToPlot =='mlljj' else ( bin_+1))  

                histo_mc = getHisto(files_path, reg, varToPlot, list_BinEdges, bin_ , isData=False, splitDY_acrossplane=False)
                histo_data = getHisto(files_path, reg, varToPlot, list_BinEdges, bin_ , isData=True, splitDY_acrossplane=False)
            
                print ("INFO.Getting Drell-Yan weight from :", list_BinEdges[bin_], "to",list_BinEdges[bin_+1], "GeV") 
                print ( "- Integrals ** ", ", region:", reg, ", varToPlot: ", suffix)
                print ( "- Data:", histo_data.Integral())
                print ( "- MC:", histo_mc.Integral())
                print ( "====================================================================================")
                #Saving files
                w_file = ROOT.TFile.Open("fitPlots_2017new/DY_%s_DYweight%s_%s.root"%(reg, supressWgt0, suffix), "recreate")
                histo_mc.SetDirectory(0)
                histo_data.SetDirectory(0)
                
                histo_mc.Write()
                histo_data.Write()
                w_file.Close()
        
                ratio_file = ROOT.TFile.Open("fitPlots_2017new/DY_%s_DYweight%s_%s.root"%(reg, supressWgt0, suffix))
                c1 = ROOT.TCanvas("c1", "c1", 800, 800)
        
                histo_mc = ratio_file.Get("%s_mc"%varToPlot)
                histo_data = ratio_file.Get("%s_data"%varToPlot)
        
                histo_data.Scale(1./histo_data.Integral())
                histo_mc.Scale(1./histo_mc.Integral())
                
                histo_mc.SetLineWidth(2)
                histo_mc.SetLineColor(kRed)
                histo_mc.GetXaxis().SetTitle("%s [GeV]"%varToPlot)
                histo_mc.GetYaxis().SetTitle("Events ")

                histo_data.SetLineWidth(2)
                histo_data.SetLineColor(kBlue)
                histo_data.GetXaxis().SetTitle("%s [GeV]"%varToPlot)
                histo_data.GetYaxis().SetTitle("Events ")
                
                histo_mc.Draw()
                histo_data.Draw("same")
                if splitDY_acrossplane: 
                    c1.SaveAs("fitPlots_2017new/DY_%s_DYweight%s_%s.pdf"%(reg, supressWgt0, suffix), "pdf")
                    c1.SaveAs("fitPlots_2017new/DY_%s_DYweight%s_%s.png"%(reg, supressWgt0, suffix), "png")
                else: 
                    c1.SaveAs("fitPlots_2017new/DY_%s_%s.pdf"%(reg, suffix), "pdf")
                    c1.SaveAs("fitPlots_2017new/DY_%s_%s.png"%(reg, suffix), "png")
                #create histo of ratio data/MC
#                c2 = ROOT.TCanvas("c2", "c2", 800, 800)
#                DY_DataMC_ratio = histo_data.Clone()
#                DY_DataMC_ratio.SetTitle("")
#                DY_DataMC_ratio.Sumw2()
#                DY_DataMC_ratio.Divide(histo_mc)
#                
#                DY_DataMC_ratio.SetMarkerColor(ROOT.kBlack)
#                DY_DataMC_ratio.SetMarkerSize(0.8)
#                
#                DY_DataMC_ratio.SetStats(0)
#                DY_DataMC_ratio.SetMinimum(0.4)
#                DY_DataMC_ratio.SetMaximum(1.6)
#    
#                #fit_func = ROOT.TF1("pol6", "pol6")
#                #fit_func.SetParameter(1, 0.0000005)
#                #DY_DataMC_ratio.Fit(fit_func)
#
#                line = ROOT.TLine(DY_DataMC_ratio.GetXaxis().GetXmin(), 1, DY_DataMC_ratio.GetXaxis().GetXmax(), 1)
#                line.SetLineColor(ROOT.kBlack)
#                line.Draw("")
#                
#                add_ratio = ROOT.TFile.Open("fitPlots_2017new/DY_%s_DYweight%s_%s_Onlyratio.root"%(reg, supressWgt0, suffix), "recreate")
#                DY_DataMC_ratio.SetDirectory(0)
#                DY_DataMC_ratio.Write()
#                add_ratio.Close()
#
#                DY_DataMC_ratio.Draw()
#                c2.SaveAs("fitPlots_2017new/DYweight%s_DataMC_ratio_%s_%s.pdf"%(supressWgt0, reg, suffix), "pdf")
#                c2.SaveAs("fitPlots_2017new/DYweight%s_DataMC_ratio_%s_%s.png"%(supressWgt0, reg, suffix), "png")
#        
#                ratio_file.Close()
#
if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)
    main()
