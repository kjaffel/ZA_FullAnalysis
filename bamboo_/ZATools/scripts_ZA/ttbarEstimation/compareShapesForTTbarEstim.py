import sys, os, json
import copy
import datetime
import subprocess
import argparse
import glob
import ROOT
ROOT.gROOT.SetBatch(True)
from ROOT import TCanvas, TPad, TLine

import numpy as np

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/')
import Constants as Constants


def getSingleTop(histos_Nms, path, lumi):
    
    rf = {
        "bb_M"     :ROOT.TH1F("bb_M"     , "", 40, 10, 1000),
        "llbb_M"   :ROOT.TH1F("llbb_M"   , "", 50, 100, 1500),
        "ll_M"     :ROOT.TH1F("ll_M"     , "", 60, 70., 120.),
        "bjet1_pt" :ROOT.TH1F("bjet1_pt" , "", 50, 20, 650),
        "bjet2_pt" :ROOT.TH1F("bjet2_pt" , "", 50, 20, 650),
        "bb_DR"    :ROOT.TH1F("bb_DR"    , "", 50, 0, 6),
        "lep1_pt"  :ROOT.TH1F("lep1_pt"  , "", 50, 20, 650),
        "lep2_pt"  :ROOT.TH1F("lep2_pt"  , "", 50, 0, 650),
        "bb_pt"    :ROOT.TH1F("bb_pt"    , "", 50, 0, 650),
        }

    list_histos = []
    singletop_hists = {}
    
    for filename in glob.glob(os.path.join(path, '*.root')):
        split_filename = filename.split('/')
        if not str(split_filename[-1]).startswith('ST_'):
            continue

        f = ROOT.TFile(filename)
        print (filename)
        for var, histNm in histos_Nms.items():
            singletop_hists[var] = f.Get(histNm)
            singletop_hists[var].SetDirectory(0)
            rf[var].Add(singletop_hists[var])
   
    for hist in rf.values():
        hist.Scale(lumi)
        list_histos.append(hist)
    
    return list_histos


def addHistos(histos_Nms, path, lumi, ttbar_from_data):
    
    rf = {
        "bb_M"     :ROOT.TH1F("bb_M"     , "", 40, 10, 1000),
        "llbb_M"   :ROOT.TH1F("llbb_M"   , "", 50, 100, 1500),
        "ll_M"     :ROOT.TH1F("ll_M"     , "", 60, 70., 120.),
        "bjet1_pt" :ROOT.TH1F("bjet1_pt" , "", 50, 20, 650),
        "bjet2_pt" :ROOT.TH1F("bjet2_pt" , "", 50, 20, 650),
        "bb_DR"    :ROOT.TH1F("bb_DR"    , "", 50, 0, 6),
        "lep1_pt"  :ROOT.TH1F("lep1_pt"  , "", 50, 20, 650),
        "lep2_pt"  :ROOT.TH1F("lep2_pt"  , "", 50, 0, 650),
        "bb_pt"    :ROOT.TH1F("bb_pt"    , "", 50, 0, 650),
        }
    
    list_histos = []
    ttbar_hists = {}
    
    if not ttbar_from_data:
        Newhistos_Nms = {}
        for var, nm in histos_Nms.items():
            Newhistos_Nms[var] = nm.replace('MuEl_','MuMu_')
    else: 
        Newhistos_Nms = histos_Nms

    for filename in glob.glob(os.path.join(path, '*.root')):
        
        split_filename = filename.split('/')
        if ttbar_from_data:
            if not str(split_filename[-1]).startswith('MuonEG'):
                continue
        elif not ttbar_from_data:
            if not str(split_filename[-1]).startswith('TT'):
                continue
        
        f = ROOT.TFile(filename)
        print (filename)
        
        for var, histNm in Newhistos_Nms.items():
            ttbar_hists[var] = f.Get(histNm)
            ttbar_hists[var].SetDirectory(0)
            rf[var].Add(ttbar_hists[var])
   
    for hist in rf.values():
        if not ttbar_from_data:
            hist.Scale(lumi)
        list_histos.append(hist)
        
    return list_histos


def TTbarEstim_FormMuonEG(path, subtractSingleTop, era):
    suffix = 'resolved'
    tagger = 'DeepFlavour'
    wp     = 'M'
    met    = 'METCut'
    process= 'gg_fusion'
    
    do_ratio= False
    lumi = Constants.getLuminosity(era)
    
    varToPlots = ['bb_M', 'llbb_M', 'll_M', 'bjet1_pt', 'bjet2_pt', 'bb_DR', 'lep1_pt', 'lep2_pt', 'bb_pt']
    histos_Nms = {}
    for var in varToPlots:
        histos_Nms[var] = f"MuEl_{var}_{suffix}_{tagger}{wp}_{met}_{process}"
    
    list_histos_data      = addHistos(histos_Nms, path, lumi, ttbar_from_data=True)
    list_histos_ttbarMC   = addHistos(histos_Nms, path, lumi, ttbar_from_data=False) 
    list_histos_singleTop = getSingleTop(histos_Nms, path, lumi)

    c1 = []
    c2 = []
    pad1 = []
    pad2 = []
    legend = []
    cms_txt = []
    lumi_txt = []
    for i, sfx in zip(range(0, len(list_histos_data)), varToPlots):

        norm_data      = list_histos_data[i].Integral()
        norm_ttbar     = list_histos_ttbarMC[i].Integral()
        norm_singletop = list_histos_singleTop[i].Integral()

        print (" norm data      =", norm_data)
        print (" norm ttbar     =",  norm_ttbar)
        print (" norm singletop =", norm_singletop)

        c1.append(TCanvas("c1", "c1", 800, 800))
        c1[i].SetTitle(f"; Events; {var}")
        #c1[i].SetTitleOffset(1.2)
        #c1[i].SetTitleSize(0.045)

        pad1.append(TPad("pad1", "pad1", 0, 0.3, 1, 0.9))
        pad1[i].SetTopMargin(0.1)
        pad1[i].SetBottomMargin(0.15)
        pad1[i].SetLeftMargin(0.15)
        pad1[i].SetRightMargin(0.1)
        
        list_histos_data[i].SetStats(0)
        list_histos_data[i].SetMarkerColor(ROOT.kBlack)
        list_histos_data[i].SetMarkerStyle(20)
        list_histos_ttbarMC[i].SetLineColor(ROOT.kOrange+1)
        list_histos_ttbarMC[i].SetLineStyle(0)
        list_histos_ttbarMC[i].SetLineWidth(2)
        
        # Subtract the SingleTop background
        if subtractSingleTop:
            list_histos_data[i].Add(list_histos_singleTop[i], -1)
            norm_data = list_histos_data[i].Integral()
        list_histos_data[i].Scale(1/norm_data)
        list_histos_data[i].Draw()
        list_histos_ttbarMC[i].Scale(1/norm_ttbar)
        list_histos_ttbarMC[i].GetXaxis().SetTitle(f"{var}")
        list_histos_ttbarMC[i].GetYaxis().SetTitle("Events")
        list_histos_ttbarMC[i].GetXaxis().SetTitleOffset(1.2)
        list_histos_ttbarMC[i].GetYaxis().SetTitleOffset(1.2)
        list_histos_ttbarMC[i].GetXaxis().SetTitleSize(0.045)
        list_histos_ttbarMC[i].GetYaxis().SetTitleSize(0.045)
        list_histos_ttbarMC[i].Draw("L same")


        legend.append(ROOT.TLegend(0.75,0.89,0.6,0.62))
        legend[i].SetTextSize(0.025)
        legend[i].SetBorderSize(0)
        legend[i].Draw()
        legend[i].AddEntry(list_histos_data[i], "data ($\mu e$ channel)")
        legend[i].AddEntry(list_histos_ttbarMC[i], "ttbar ($\mu\mu$ channel)")
        legend[i].Draw("*L")

        t = c1[i].GetTopMargin()
        r = c1[i].GetRightMargin()
        l = c1[i].GetLeftMargin()
        lumiTextOffset   = 0.2

        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextAngle(0)
        latex.SetTextColor(ROOT.kBlack)

        lumiText = "%s fb^{-1} (13 TeV)" %format(lumi/1000.,'.2f')
        lumi_txt.append(latex.DrawLatex(0.6,1-t+lumiTextOffset*t,lumiText))
        lumi_txt[i].SetNDC()
        lumi_txt[i].SetTextFont(40)
        lumi_txt[i].SetTextSize(0.03)
        lumi_txt[i].Draw("same")

        cms_txt.append(latex.DrawLatex(0.12, 1-t+lumiTextOffset*t, "CMS Preliminary"))
        cms_txt[i].SetNDC()
        cms_txt[i].SetTextFont(40)
        cms_txt[i].SetTextSize(0.03)
        cms_txt[i].Draw("same")

        c1[i].cd()
        if do_ratio:
            pad2.append(ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3))
            pad2[i].SetTopMargin(0)
            pad2[i].SetBottomMargin(0.3)
            pad2[i].SetLeftMargin(0.15)
            pad2[i].SetRightMargin(0.1)
            pad2[i].SetGridx()
            pad2[i].SetGridy()
            pad2[i].Draw()
            pad2[i].cd()
    
            ratio = list_histos_data[i].Clone("Ratio")
            ratio.SetLineColor(ROOT.kBlack)
            ratio.SetMarkerStyle(21)
            ratio.SetFillColor(4)
            ratio.SetFillStyle(3001)
            ratio.SetMinimum(0.6)
            ratio.SetMaximum(1.4)
            ratio.SetStats(0)
            
            ratio.Draw("ep")
    
            ratio.SetTitle("")
            ratio.GetYaxis().SetTitle("Data/MC")
            ratio.GetYaxis().SetNdivisions(505)
            ratio.GetYaxis().SetTitleSize(20)
            ratio.GetYaxis().SetTitleFont(43)
            ratio.GetYaxis().SetTitleOffset(1.8)
            ratio.GetYaxis().SetLabelFont(43)
            ratio.GetYaxis().SetLabelSize(15)
                
            ratio.GetXaxis().SetNdivisions(510)
            ratio.GetXaxis().SetTitleSize(20)
            ratio.GetXaxis().SetTitleFont(43)
            ratio.GetXaxis().SetTitleOffset(4.)
            ratio.GetXaxis().SetLabelFont(43)
            ratio.GetXaxis().SetLabelSize(15)
            
            line = TLine(ratio.GetXaxis().GetXmin(), 1, ratio.GetXaxis().GetXmax(), 1)
            line.SetLineColor(ROOT.kBlack)
            line.Draw("")

        c1[i].cd()

        output_dir = os.path.join(os.getcwd(), f"plots_ul{era}")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if not subtractSingleTop:
            c1[i].SaveAs(f"plots_ul{era}/{sfx}.png")
            c1[i].SaveAs(f"plots_ul{era}/{sfx}.pdf")
        elif subtractSingleTop:
            c1[i].SaveAs(f"plots_ul{era}/noST_{sfx}.png")
            c1[i].SaveAs(f"plots_ul{era}/noST_{sfx}.pdf")
            
        c2.append(TCanvas("c2","c2",800,800))
        c2[i].cd()
        list_histos_singleTop[i].Draw("")
        c2[i].SaveAs(f"plots_ul{era}/noST_{sfx}.png")
        c2[i].SaveAs(f"plots_ul{era}/noST_{sfx}.pdf")
        print( "========="*10)


if __name__ == "__main__":
    #path = '/nfs/scratch/fynu/asaggio/CMSSW_8_0_30/src/cp3_llbb/ZATools/factories_ZA/ttbarSplitting/slurm/output/' 
    #path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/ver20_03_07/forttbarEstimation/'
    #path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2017Results/version20_04_17/results'
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run', help='To specifiy which run ', required=True)
    parser.add_argument('-i', '--inputs', help='To specifiy the path to the histograms ', required=True)
    parser.add_argument('--minusST', help='substract single top ', action='store_true', default=False)

    args = parser.parse_args()
    
    TTbarEstim_FormMuonEG(path= args.inputs, subtractSingleTop= args.minusST, era= args.run)
