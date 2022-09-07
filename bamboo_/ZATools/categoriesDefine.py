#! /bin/env python
import sys, os
import math
import glob
import yaml
import numpy as np

import ROOT
ROOT.gROOT.SetBatch(True)
from ROOT import TCanvas, TPad, TLine, TH1F

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/')
import Constants as Constants

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/')
import HistogramTools as HT


def mass_to_str(m, _p2f=False):
    if _p2f: m = "%.2f"%m
    return str(m).replace('.','p')


def getNormalizedSummedHisto(era, Cfg, path, look_for, isBkg):

    histos    = {}
    print( look_for ) 
    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        split_filename = filename.split('/')
        smp = split_filename[-1]
        
        if smp.startswith('__skeleton__'):
            continue

        if not 'UL'+str(era).replace('20', '') in smp:
            continue

        if isBkg: # I need only bkg 
            if any(x in smp for x in [ "DoubleMuon", "DoubleEG", "MuonEG", "HToZA", "GluGluToHToZA", "AToZH", "GluGluToAToZH"]) :
                continue
            smpScale = 1
            k = 'sum_bkg'
        else: # I need only signal
            if not smp.startswith(look_for):
                continue
            br = Cfg['files'][smp]["Branching-ratio"]
            smpScale = br
            k = smp.replace('.root', '')
        
        if not smp in Cfg['files'].keys():
            continue
        
        year   = Cfg['files'][smp]["era"]
        lumi   = Cfg["configuration"]["luminosity"][year]
        xsc    = Cfg['files'][smp]["cross-section"]
        genevt = Cfg['files'][smp]["generated-events"]
        
        smpScale *= ( lumi* xsc )/ genevt
        
        print( 'opening :', smp, k)
        
        f = ROOT.TFile.Open(filename)
        histos[k] = {}
        for j, key in enumerate(f.GetListOfKeys()):
            histo    = key.ReadObj()
            histo_nm = key.ReadObj().GetName() 
            
            if '__' in histo_nm: # ignore sys
                continue
            if not 'DNNOutput_ZAnode_' in histo_nm:
                continue
            if not histo_nm in histos[k].keys():
                histo_dnn = TH1F("histo_dnn", "histo_dnn", 50, 0., 1.)
                histos[k][histo_nm] = histo_dnn
            
            histo.Scale(smpScale)
            histos[k][histo_nm].Add(histo, 1)
            histos[k][histo_nm].SetDirectory(0)
            #print( 'adding', histo_nm, histo.Integral(), smpScale)
    print("-----------"*10)
    return histos


def get_Listrootfiles(path, era, process):
    look_for = "GluGluToHToZATo2L2B" if process == "gg_fusion" else "HToZATo2L2B"
    list_rf  = []
    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        split_filename = filename.split('/')
        if not 'UL'+ str(era).replace('20', '') in split_filename[-1]:
            continue
        if str(split_filename[-1]).startswith(look_for):
            fnm = split_filename[-1].replace('preVFP.root','').replace('postVFP.root', '')
            if not fnm in list_rf:
                list_rf.append(fnm)
    return list_rf


def splitSignal_INcategories(era, process, Cfg, path):

    category = ["OSSF"]#, "ElEl", "MuMu", "OSSF"]
    wp = "M"

    look_for = "GluGluToHToZATo2L2B" if process == "gg_fusion" else "HToZATo2L2B"
    proc     = 'ggH' if process == "gg_fusion" else 'bbH'
    nbr      = '2' if proc == 'ggH' else '3'

    histos_sig = getNormalizedSummedHisto(era, Cfg, path, look_for=look_for, isBkg=False)
    histos_bkg = getNormalizedSummedHisto(era, Cfg, path, look_for='', isBkg=True)
        
    for reg, tagger in { #'resolved': 'DeepFlavour', 
                         'boosted' : 'DeepCSV'
                        }.items():
        c = []
        for k, cat in enumerate(category):

            if cat == "ElEl":
                label = "e^{+}e^{-}"
            elif cat == "MuMu":
                label = "#mu^{+}#mu^{-}"
            elif cat == "OSSF":
                label = "e^{+}e^{-} + #mu^{+}#mu^{-}"

            graph  = ROOT.TGraph2D(len(histos_sig.keys()))
            
            title = graph.GetTitle()
            c.append(TCanvas(f"c{k}",title,800,800))
            c[k].SetLogz()
            c[k].DrawFrame(-12,-12,12,12)
            
            ROOT.gStyle.SetOptStat(0)
            ROOT.gStyle.SetPalette(71)
            #ROOT.gStyle.SetPalette(kBird)
            
            graph.GetXaxis().SetTitle("m_{A} (GeV)")
            graph.GetYaxis().SetTitle("m_{H} (GeV)")
            graph.GetZaxis().SetTitle("Significance #sqrt{2((S+B)ln(1+S/B)-S)}")

            #style = HT.setTDRStyle()
            #style.SetPadRightMargin(0.15)
            #style.SetPadTopMargin(0.15)
            #style.SetLabelSize(0.03, "XYZ")
            #style.SetPaintTextFormat(".3f")
            
            for i, pref in enumerate(histos_sig.keys()):
                split_prefix = pref.split("_")
                    
                mH = float(split_prefix[2].replace('p', '.'))
                mA = float(split_prefix[4].replace('p', '.'))
                
                print( "working on ::", era, pref, reg, tagger, wp, cat, process)
                histNm = f'DNNOutput_ZAnode_{cat}_{reg}_{tagger}{wp}_METCut_{process}_MH_{mass_to_str(mH)}_MA_{mass_to_str(mA)}'
                
                histo_dnn_bkg = histos_bkg['sum_bkg'][histNm]
                histo_dnn_sig = histos_sig[pref][histNm]
                #histo_dnn_sig.GetXaxis().SetRangeUser(11, i)
                #histo_dnn_sig.GetYaxis().SetRangeUser(0, 1.0)
                #histo_dnn_sig.SetDirectory(0)
                
                S  = histo_dnn_sig.Integral()
                B  = histo_dnn_bkg.Integral()
                eq = 2*( (S+B)*math.log(1+S/B) -S ) 
                
                #signif = 2*(math.sqrt(S+B)-math.sqrt(B))
                signif = math.sqrt(2*( (S+B)*math.log(1+S/B) -S ))
                #signif  = S/math.sqrt(B)
                print ('(MH, MA)= (%s, %s) GeV'%(mH, mA), "Integral (S, B) = ", (S, B), "significance =", signif)
                
                significance_array = np.array(float(signif), dtype='double')
                xAxis_array = np.array(float(mH), dtype='double')
                yAxis_array = np.array(float(mA), dtype='double')

                graph.SetPoint(i, float(mA), float(mH), float(signif))
                graph.GetXaxis().SetTitleOffset(1.7)
                graph.GetYaxis().SetTitleOffset(1.7)
                graph.GetZaxis().SetTitleOffset(1.7)
                graph.GetXaxis().SetTitleSize(0.04)
                graph.GetYaxis().SetTitleSize(0.04)
                graph.GetZaxis().SetTitleSize(0.04)
                graph.SetTitle("%s #rightarrow ZA #rightarrow, nb=%s -%s, %s ; m_{A} (GeV); m_{H} (GeV); Significance #sqrt{2((S+B)ln(1+S/B)-S)}"%(proc, nbr, reg, label))
                graph.SetName(pref)
                #graph.SetNpx(50)
                #graph.SetNpy(50)
                print( "===="*20)
            
            #pad = ROOT.TPad(f"pad[k]", "", 0, 0, 1, 1)
            #pad.Draw()
            #pad.cd()
            graph.Draw("colz0")
            graph.Draw("CONT4Z")

    
            if (ROOT.gPad):
                ROOT.gPad.SetLeftMargin(0.15)
                ROOT.gPad.SetRightMargin(0.15)
                ROOT.gPad.SetTopMargin(0.12)
                ROOT.gPad.SetBottomMargin(0.12)

            t = c[k].GetTopMargin()
            r = c[k].GetRightMargin()
            l = c[k].GetLeftMargin()
            lumiTextOffset   = 0.2

            latex = ROOT.TLatex()
            latex.SetNDC()
            latex.SetTextAngle(0)
            latex.SetTextColor(ROOT.kBlack)
            
            lumiText = "%s fb^{-1} (13 TeV)" %format(Constants.getLuminosity(era)/1000.,'.2f')
            lumi = latex.DrawLatex(0.65,1-t+lumiTextOffset*t,lumiText)
            lumi.SetNDC()
            lumi.SetTextFont(40)
            lumi.SetTextSize(0.03)
            lumi.Draw("same")
            
            cms_text = latex.DrawLatex(0.12, 1-t+lumiTextOffset*t, "CMS Preliminary")
            cms_text.SetNDC()
            cms_text.SetTextFont(40)
            cms_text.SetTextSize(0.03)
            cms_text.Draw("same")
            
            #c[k].cd() 
            c[k].Print("cats/ul{}/cat_define_{}_{}_{}_{}{}.png".format(era, process, reg, cat, tagger, wp))
            c[k].Print("cats/ul{}/cat_define_{}_{}_{}_{}{}.pdf".format(era, process, reg, cat, tagger, wp))
            del c[k]

if __name__ == "__main__":
    path_Cfg = '/home/users/k/j/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/'
    path  = '/home/users/k/j/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_run2__ver15/' 
    
    for era in [2017]: #2016, 2017, 2018]:
        for proc in ['gg_fusion']: # ['gg_fusion', 'bb_associatedProduction']:
            with open(os.path.join(path, 'plots_bbH.yml')) as _f:
                Cfg = yaml.load(_f, Loader=yaml.FullLoader)
        
            splitSignal_INcategories(era, proc, Cfg, os.path.join(path, 'results/'))
