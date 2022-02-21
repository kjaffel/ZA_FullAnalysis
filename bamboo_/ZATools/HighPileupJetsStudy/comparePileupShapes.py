import sys, os, json
import copy
import datetime
import subprocess
import numpy as np
import glob
import ROOT
from ROOT import TCanvas, TPad, TLine
import sys
import argparse

def addHistos(path, lumi, idx, cat, jID, jlen, PuIDWP, getData):
    
    lumi = 41529.152060112
    run= '2017'
    
    list_histos = []
    vtx= ROOT.TH1F( "vtx", "vtx", 60, 0., 80.)
    if PuIDWP==None:
        histos_vtxNames= "OsLepplus_Only2_aka4Jets_vtx"
        #histos_vtxNames= ("OsLepplus_%s_aka4Jets_vtx"%(jlen) #FIXME  
    else:
        histos_vtxNames= "OsLepplus_%s_jId%s_puId%s_CentrPT30_Eta2p4_%s_vtx"%(jlen, jID, PuIDWP, cat)
    
    if not getData:
        for filename in glob.glob(os.path.join(path, '*.root')):
            split_filename = filename.split('/')
            if not str(split_filename[-1]).startswith('DYJetsToLL_%s'%idx):
                continue
            print (filename)
            print( 'histos_vtxNames=', histos_vtxNames)
            f = ROOT.TFile(filename)
            DYplusJets_vtx = f.Get(histos_vtxNames)
            DYplusJets_vtx.SetDirectory(0)
            vtx.Add(DYplusJets_vtx)
    
        vtx.Scale(lumi)
        list_histos.append(vtx)

    if getData:
        for filename in glob.glob(os.path.join(path, '*.root')):
            split_filename = filename.split('/')
            if not str(split_filename[-1]).startswith('DoubleEGamma_') and not str(split_filename[-1]).startswith('DoubleMuon_') and not str(split_filename[-1]).startswith('MuonEG_'):
                continue

            f = ROOT.TFile(filename)
            data_vtx = f.Get(histos_vtxNames)
            data_vtx.SetDirectory(0)
            vtx.Add(data_vtx)
    
        vtx.Scale(lumi)
        list_histos.append(vtx)

    return list_histos

def main():
    
    #parser = argparse.ArgumentParser()
    #parser.add_argument('-r', '--run', help='To specifiy which run ', required=True)
    #parser.add_argument('-i', '--inputs', help='To specifiy the path to the histograms ', required=True)

    #args = parser.parse_args()
    #path= args.inputs

    path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.3/results/'
    lumi = 41529.152060112
    run= '2017'
    print( " path to histograms : " , path, " for run ", run)
    
    #jf args.run =='2016':
    #    lumi = 35921.875594646
    #elif args.run=='2017':
    #    lumi = 41529.152060112
    #else:
    #    lumi = 59740.565201546
    
    
    list_histos_data_nopileup   = []
    list_histos_data_LoOsepuID  = []
    list_histos_data_MediumpuID = []
    list_histos_data_TightpuID  = []
    
    list_histos_DYPlusJets_nopileup = []
    list_histos_DYPlusJets_LoOsepuID = []
    list_histos_DYPlusJets_MediumpuID = []
    list_histos_DYPlusJets_TightpuID = []


    cat = 'ElEl'
    jID = 'TLepVeto'
    jlen = 'only2Jets'
    nbrj = 0
    print(lumi, nbrj, jlen, jID, cat)
                                            # path, lumi, nbrj, cat, jID,  jlen, PuIDWP, getData
    list_histos_DYPlusJets_nopileup  = addHistos(path, lumi, nbrj, cat, jID, jlen, None, False)
    list_histos_DYPlusJets_LoOsepuID = addHistos(path, lumi, nbrj, cat, jID, jlen, 'L',  False)
    list_histos_DYPlusJets_MediumpuID= addHistos(path, lumi, nbrj, cat, jID, jlen, 'M',  False) 
    list_histos_DYPlusJets_TightpuID = addHistos(path, lumi, nbrj, cat, jID, jlen, 'T',  False)
            
    list_histos_data_nopileup   = addHistos(path, lumi, None, cat, jID,  jlen, None,   True)
    list_histos_data_LoOsepuID  = addHistos(path, lumi, None, cat, jID,  jlen, 'L',    True)
    list_histos_data_MediumpuID = addHistos(path, lumi, None, cat, jID,  jlen, 'M',    True)
    list_histos_data_TightpuID  = addHistos(path, lumi, None, cat, jID,  jlen, 'T',    True)
            
        
    legend = []
    c1 = []
    c2 = []
    pad1 = []
    pad2 = []
                    
    for i, sfx in zip(range(0, len(list_histos_data_nopileup)), ['vtx']): # keep it in a loop maybe want to add other histos later on 

        norm_data_nopileup = list_histos_data_nopileup[i].Integral()
        norm_data_L = list_histos_data_LoOsepuID[i].Integral()
        norm_data_M = list_histos_data_MediumpuID[i].Integral()
        norm_data_T = list_histos_data_TightpuID[i].Integral()

        print ( "\n********************************************************",
                "\n Data Integral no pu :", norm_data_nopileup,
                "\n Data Integral L :", norm_data_L, 
                "\n Data Integral M :", norm_data_M, 
                "\n Data Integral T :", norm_data_T, 
                "\n********************************************************") 

        norm_DYJets_nopileup = list_histos_DYPlusJets_nopileup[i].Integral()
        norm_DYJets_L = list_histos_DYPlusJets_LoOsepuID[i].Integral()
        norm_DYJets_M = list_histos_DYPlusJets_MediumpuID[i].Integral()
        norm_DYJets_T = list_histos_DYPlusJets_TightpuID[i].Integral()
    

        print ( "\n*******************************************************",
                "\n Z + %sJets Integral no pu :"%nbrj, norm_DYJets_nopileup,
                "\n Z + %sJets Integral L :"%nbrj, norm_DYJets_L, 
                "\n Z + %sJets Integral M :"%nbrj, norm_DYJets_M, 
                "\n Z + %sJets Integral T :"%nbrj, norm_DYJets_T,
                "\n********************************************************") 

        c1.append(TCanvas("c1","c1",600, 600))
        pad1.append(TPad("pad1","pad1",0,0.3,1,0.9))
        pad1[i].SetBottomMargin(0)
        pad1[i].Draw()
        pad1[i].cd()
                
        print ( '************************************************', list_histos_data_nopileup)
                        
        #legend.append(ROOT.TLegend(0.5, 0.7, 0.8, 0.8))
        legend.append(ROOT.TLegend(0.7, 0.6, 0.91, 0.91))
        #for list_histos_data, list_histos_DYJetsMC, norm_data, norm_DYJets, color in zip([ list_histos_data_nopileup, list_histos_data_LoOsepuID, list_histos_data_MediumpuID, list_histos_data_TightpuID],
        #                            [list_histos_DYPlusJets_nopileup, list_histos_DYPlusJets_LoOsepuID, list_histos_DYPlusJets_MediumpuID, list_histos_DYPlusJets_TightpuID],
        #                            [norm_data_nopileup, norm_data_L, norm_data_M, norm_data_T],
        #                            [norm_DYJets_nopileup, norm_DYJets_L, norm_DYJets_M, norm_DYJets_T],
        #                            [ROOT.kRed, ROOT.kMagenta, ROOT.kGreen, ROOT.kBlue]):
            
        list_histos_data = list_histos_data_nopileup
        list_histos_DYJetsMC = list_histos_DYPlusJets_nopileup
        norm_data = norm_data_nopileup
        norm_DYJets = norm_DYJets_nopileup
        color = ROOT.kRed
            
        list_histos_data[i].SetStats(0)
        list_histos_data[i].SetMarkerColor(color)
        list_histos_data[i].SetMarkerStyle(20)
            
        list_histos_data[i].Scale(1/norm_data)
        list_histos_data[i].Draw("")
                    
        legend[i].AddEntry(list_histos_data[i], "data (%s channel)"%cat, "p")
        legend[i].Draw("same")
                    
        list_histos_DYJetsMC[i].SetMarkerColor(color)
        list_histos_DYJetsMC[i].SetMarkerStyle(22)
        list_histos_DYJetsMC[i].SetLineStyle(1)
    
        list_histos_DYJetsMC[i].Scale(1/norm_DYJets)
        list_histos_DYJetsMC[i].Draw("same")
            
        legend[i].AddEntry(list_histos_DYJetsMC[i], " Z+ %sjets  (%s channel)"%(nbrj, cat), "p")
        legend[i].Draw("same")
                            
    
                        
        c1[i].cd()
        pad2.append(TPad("pad2","pad2",0, 0.05, 1, 0.3))
        pad2[i].SetTopMargin(0)
        pad2[i].SetBottomMargin(0.3)
        pad2[i].Draw()
        pad2[i].cd()


        ratio = list_histos_data[i].Clone("Ratio")

                
        ratio.SetTitle("")
        ratio.Sumw2()
        ratio.SetMarkerColor(ROOT.kBlack)
        ratio.SetMarkerSize(0.8)
        ratio.SetStats(0)
        ratio.GetYaxis().SetRangeUser(0,2)
        ratio.Draw("same")
        line = TLine(ratio.GetXaxis().GetXmin(), 1, ratio.GetXaxis().GetXmax(), 1)
        line.SetLineColor(ROOT.kBlack)
        line.Draw("")
        
        c1[i].cd()

        output_dir = os.path.join(os.getcwd(), "comparePileupShapes")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print ( run, nbrj, jID, jlen, cat, sfx , output_dir)
        c1[i].SaveAs("comparePileupShapes/plot_DYPlus_%s_%s_%s_%s_%s.png"%(nbrj, jID, jlen, cat, sfx))
        c1[i].SaveAs("comparePileupShapes/plot_DYPlus_%s_%s_%s_%s_%s.pdf"%(nbrj, jID, jlen, cat, sfx))
                    
        c2.append(TCanvas("c2","c2", 600, 600))
        c2[i].cd()
        list_histos_DYJetsMC[i].Draw("")
            
        c2[i].SaveAs("comparePileupShapes/plot_Data_%s_%s_%s_%s_%s.png"%(nbrj, jID, jlen, cat, sfx))
        c2[i].SaveAs("comparePileupShapes/plot_Data_%s_%s_%s_%s_%s.pdf"%(nbrj, jID, jlen, cat, sfx))


#main
if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)
    main()
