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


def pogEraFormat(era):
    return "_UL"+ era.replace('20', '')


def addHistos(histos_Nms, xAxis, path, era, lumi, channel, ttbar_from_data=False, singletop=False):
    
    ttbar_hists = {}

    data = ['DoubleMuon', 'DoubleEG', 'MuonEG', 'SingleMuon', 'SingleElectron', 'EGamma']
    if singletop:
        mc = ['ST_'] 
    else:
        mc = ['TTTo2L2Nu', 'TTToSemiLeptonic', 'TTToHadronic'] 
    
    rf = {
        #"bb_M"     :ROOT.TH1F("bb_M"     , "", 50, 10, 1000),
        "llbb_M"   :ROOT.TH1F("llbb_M"   , "", 50, 100, 1500),
        #"DNN"       :ROOT.TH1F("DNN"   , "", 50, 0, 1),
        #"mbb"      :ROOT.TH1F("bb_M"     , "", 60, 0, 1200),
        #"mllbb"    :ROOT.TH1F("llbb_M"   , "", 60, 120, 1400),
        "ll_M"     :ROOT.TH1F("ll_M"     , "", 50, 70., 120.),
        #"bjet1_pt" :ROOT.TH1F("bjet1_pt" , "", 50, 20, 650),
        #"bjet2_pt" :ROOT.TH1F("bjet2_pt" , "", 50, 20, 650),
        #"bb_DR"    :ROOT.TH1F("bb_DR"    , "", 50, 0, 6),
        #"lep1_pt"  :ROOT.TH1F("lep1_pt"  , "", 50, 0, 650),
        #"lep2_pt"  :ROOT.TH1F("lep2_pt"  , "", 50, 0, 650),
        #"bb_pt"    :ROOT.TH1F("bb_pt"    , "", 50, 0, 650),
        }
    
    if not ttbar_from_data:
        Newhistos_Nms = {}
        for var, nm in histos_Nms.items():
            Newhistos_Nms[var] = nm.replace('MuEl_',f'{channel}_')
    else: 
        Newhistos_Nms = histos_Nms

    for filename in glob.glob(os.path.join(path, '*.root')):
        
        split_filename = filename.split('/')
        if not pogEraFormat(era) in str(split_filename[-1]):
            continue
        
        if ttbar_from_data:
            if not any(x in str(split_filename[-1]) for x in data):
                continue
        elif not ttbar_from_data:
            if not any(str(split_filename[-1]).startswith(x) for x in mc):
                continue
        
        f = ROOT.TFile(filename)
        print (filename)
        
        for var, histNm in Newhistos_Nms.items():
            ttbar_hists[var] = f.Get(histNm)
            ttbar_hists[var].SetDirectory(0)
            #if not ttbar_from_data:
            #    ttbar_hists[var].Scale(lumi)
            rf[var].Add(ttbar_hists[var])
            rf[var].GetXaxis().SetTitle(f"{xAxis[var]}")
            rf[var].GetYaxis().SetTitle("Events")

    return list( rf.values())


def TTbarEstim_FormMuonEG(path, subtractSingleTop, era, channel):
    reg    = 'resolved'   # 'boosted'  
    tagger = 'DeepFlavour'# 'DeepCSVM'    
    wp     = 'M'
    process= 'gg_fusion'  #'bb_associatedProduction' 
    
    
    do_ratio = True
    lumi = Constants.getLuminosity(era)
    
    varToPlots = ['llbb_M', 'll_M']#, 'DNN', 'mbb', 'mllbb']#'bb_M', 'llbb_M', 'll_M', 'bjet1_pt', 'bjet2_pt', 'bb_DR', 'lep1_pt', 'lep2_pt', 'bb_pt']
    
    xAxis      = {#'bb_M'    : 'm_{bb} (GeV)', 
                  'llbb_M'  : 'm_{llbb} (GeV)',
                  #'DNN'      : 'DNNoutput ZA',
                  #'mllbb'   : 'm_{llbb} (GeV)',
                  #'mbb'     : 'm_{bb} (GeV)',
                  'll_M'    : 'm_{ll} (GeV)',
                  #'bjet1_pt': 'leading bjet p_{T} (GeV)',
                  #'bjet2_pt': 'subleading bjet p_{T} (GeV)',
                  #'bb_DR'   : '\DeltaR(bjet1, bjet2)',
                  #'lep1_pt' : 'leading lepton p_{T} (GeV)',
                  #'lep2_pt' : 'subleading lepton p_{T} (GeV)',
                  #'bb_pt'   : 'di-bjets p_{T} (GeV)',
                  }

    histos_Nms = {}
    for var in varToPlots:
        #histos_Nms[var] = f"MuEl_{var}_{reg}_{tagger}{wp}_{met}_{process}"
        #histos_Nms[var] = f"MuEl_{reg}_METCut_NobJetER_bTagWgt_{var}_{tagger}{wp}_{process}"
        #histos_Nms[var] = f"DNNOutput_ZAnode_MuEl_{reg}_{tagger}{wp}_METCut_{process}_MH_500_MA_300"
        #histos_Nms[var]  = f"DNNOutput_ZAnode_MuEl_{reg}_{tagger}{wp}_METCut_{process}_MH_516p94_MA_78p52"
        histos_Nms[var]  = f"MuEl_{var}_{reg}_{tagger}{wp}_METCut_{process}"
    
    list_histos_data      = addHistos(histos_Nms, xAxis, path, era, lumi, channel, ttbar_from_data=True)
    list_histos_ttbarMC   = addHistos(histos_Nms, xAxis, path, era, lumi, channel, ttbar_from_data=False) 
    list_histos_singleTop = addHistos(histos_Nms, xAxis, path, era, lumi, channel, ttbar_from_data=False, singletop=True)

    c1 = []
    c2 = []
    pad1 = []
    pad2 = []
    legend = []
    cms_txt = []
    lumi_txt = []
    
    for i, var in zip(range(0, len(list_histos_data)), varToPlots):
        
        norm_data      = list_histos_data[i].Integral()
        norm_ttbar     = list_histos_ttbarMC[i].Integral()
        norm_singletop = list_histos_singleTop[i].Integral()

        print (" norm data      =", norm_data)
        print (" norm ttbar     =", norm_ttbar)
        print (" norm singletop =", norm_singletop)

        c1.append(TCanvas("c1", "c1", 800, 800))
        c1[i].SetTitle(f"; Events; {var}")
        c1[i].SetTopMargin(0.1)
        c1[i].SetBottomMargin(0.1)
        c1[i].SetLeftMargin(0.15)
        c1[i].SetRightMargin(0.15)
        #c1[i].SetTitleOffset(1.2)
        #c1[i].SetTitleSize(0.045)

        pad1.append(TPad("pad1", "pad1", 0, 0.0, 1.0, 1.0))
        if do_ratio: 
            pad1[i].SetBottomMargin(0.2)
            pad1[i].SetLeftMargin(0.15)
        pad1[i].Draw()
        pad1[i].cd()

        list_histos_data[i].SetStats(0)
        list_histos_data[i].SetMarkerColor(ROOT.kBlack)
        list_histos_data[i].SetMarkerStyle(20)
        list_histos_ttbarMC[i].SetLineColor(ROOT.kOrange+1)
        list_histos_ttbarMC[i].SetLineStyle(0)
        list_histos_ttbarMC[i].SetLineWidth(2)
        
        # Subtract the SingleTop background
        if subtractSingleTop:
            list_histos_data[i].Add(list_histos_singleTop[i], -1)
            list_histos_data[i].SetDirectory(0) 

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
        lepflav = '$\mu\mu$' if channel == 'MuMu' else ( 'ee' if channel == 'ElEl' else ('$\mu e$'))
        legend[i].AddEntry(list_histos_data[i], "data ($\mu e$ channel)")
        legend[i].AddEntry(list_histos_ttbarMC[i], f"ttbar ( {lepflav} channel)")
        legend[i].Draw("*L")

        t = c1[i].GetTopMargin()
        r = c1[i].GetRightMargin()
        l = c1[i].GetLeftMargin()
        lumiTextOffset   = 0.2

        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextAngle(0)
        latex.SetTextColor(ROOT.kBlack)

        lumiText = "%s fb-1 (13 TeV)" %format(lumi/1000.,'.2f')
        lumi_txt.append(latex.DrawLatex(0.65,1-t+lumiTextOffset*t,lumiText))
        lumi_txt[i].SetNDC()
        lumi_txt[i].SetTextFont(40)
        lumi_txt[i].SetTextSize(0.03)
        lumi_txt[i].Draw("same")

        cms_txt.append(latex.DrawLatex(0.15, 1-t+lumiTextOffset*t, "CMS Preliminary"))
        cms_txt[i].SetNDC()
        cms_txt[i].SetTextFont(40)
        cms_txt[i].SetTextSize(0.03)
        cms_txt[i].Draw("same")

        # Redraw axis to avoid clipping 0
        #list_histos_data[i].GetXaxis().SetLabelSize(0.)
        #list_histos_data[i].GetXaxis().SetTitle('')
        
        #c1[i].cd()
        if do_ratio:
            ratio = list_histos_data[i].Clone("Ratio")
            ratio.Sumw2()
            ratio.Divide(list_histos_ttbarMC[i])
            
            pad2.append(ROOT.TPad("pad2", "pad2", 0.0, 0.0, 1., 0.2))
           #pad2.append(ROOT.TPad("pad2", "pad2",0, 0.05, 1, 0.3))
            pad2[i].SetTopMargin(0)
            pad2[i].SetBottomMargin(0.3) 
            pad2[i].SetLeftMargin(0.15)
            pad2[i].SetRightMargin(0.1)
            pad2[i].SetGridx()
            pad2[i].SetGridy()
            pad2[i].Draw()
            pad2[i].cd()
    
            ratio.SetLineColor(ROOT.kBlack)
            ratio.SetMarkerStyle(21)
            ratio.SetFillColor(4)
            ratio.SetFillStyle(3001)
            ratio.SetMinimum(0.6)
            ratio.SetMaximum(1.4)
            ratio.SetStats(0)
            
    
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
            
            ratio.Draw("ep")
            
            line = TLine(ratio.GetXaxis().GetXmin(), 1, ratio.GetXaxis().GetXmax(), 1)
            line.SetLineColor(ROOT.kBlack)
            line.Draw("")

        #c1[i].cd()

        output_dir = os.path.join(os.getcwd(), f"plots_ul{era}")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        noST_output_dir = os.path.join(output_dir, "no_SingleTop")
        if not os.path.exists(noST_output_dir):
            os.makedirs(noST_output_dir)
        if not subtractSingleTop:
            c1[i].SaveAs(f"plots_ul{era}/{channel}_{var}_{reg}_{tagger}{wp}_{process}.png")
            c1[i].SaveAs(f"plots_ul{era}/{channel}_{var}_{reg}_{tagger}{wp}_{process}.pdf")
        elif subtractSingleTop:
            c1[i].SaveAs(f"plots_ul{era}/no_SingleTop/noST_{channel}_{var}_{reg}_{tagger}{wp}_{process}.png")
            c1[i].SaveAs(f"plots_ul{era}/no_SingleTop/noST_{channel}_{var}_{reg}_{tagger}{wp}_{process}.pdf")
            
        c2.append(TCanvas("c2","c2",800,800))
        c2[i].cd()
        list_histos_singleTop[i].Draw("")
        c2[i].SaveAs(f"plots_ul{era}/no_SingleTop/noST_{channel}_{var}_{reg}_{tagger}{wp}_{process}.png")
        c2[i].SaveAs(f"plots_ul{era}/no_SingleTop/noST_{channel}_{var}_{reg}_{tagger}{wp}_{process}.pdf")
        print( "========="*10)
        
        c1[i].Clear()
        c2[i].Clear()


if __name__ == "__main__":
    
    #path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/ver20_03_07/forttbarEstimation/'
    #path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2017Results/version20_04_17/results'
    #path = '../../../run2Ulegay_results/ul_run2__ver17/results/'

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run', help='To specifiy which run ', required=True)
    parser.add_argument('-i', '--inputs', help='To specifiy the path to the histograms ', required=True)
    parser.add_argument('--minusST', help='substract single top ', action='store_true', default=False)
    
    args = parser.parse_args()
    
    for channel in [ 'ElEl', 'MuMu', 'MuEl']:
        TTbarEstim_FormMuonEG(path= args.inputs, subtractSingleTop= args.minusST, era= args.run, channel= channel)
