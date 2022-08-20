# To optimize the cut on MET, we need the met_pt distribution for:
# 1) One signal sample (then it has to be extended to the 21)
# 2) All the backgrounds

#Things to do: add all the backgrounds together in order to have two superimposed histograms, one for the background and one for the signal.
# Then vary the met cut bin by bin and get the integral of the backrounds histo and of the signal histo and compute S/sqrt(B)

#! /bin/env python
import sys, os
import math
import glob
import ROOT
import yaml
import numpy as np

ROOT.gROOT.SetBatch(True)
from ROOT import TCanvas, TPad, TLine, TH1F
from faker import Factory
fake = Factory.create()

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/')
import Constants as Constants

wheel  = [ROOT.kTeal,ROOT.kBlue, ROOT.kAzure, ROOT.kViolet, ROOT.kTeal, ROOT.kYellow, ROOT.kOrange, ROOT.kGreen, ROOT.kMagenta, ROOT.kCyan, ROOT.kYellow]
colors = []
for i in range(1, 10):
    for c in wheel:
        colors.append(c+i)

def getHisto(era, Cfg, path, isBkg, prefix, reg, tagger, wp, cat, process):

    _files = set()
    histo_met = TH1F("histo_met", "histo_met", 60, 0, 600)

    integral=0
    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        split_filename = filename.split('/')
        smp = split_filename[-1]
        if smp.startswith('__skeleton__'):
            continue

        if isBkg:
            if smp.startswith("DoubleMuon") or smp.startswith("DoubleEG") or smp.startswith("MuonEG") or smp.startswith("HToZA") or smp.startswith("GluGluToHToZA"):
                continue
            smpScale = 1.
        else:
            if not smp.startswith(prefix):
                continue
            br = Cfg['files'][smp]["branching-ratio"]
            smpScale = br
       
        if not smp in Cfg['files'].keys():
            continue
        year   = Cfg['files'][smp]["era"]
        lumi   = Cfg["configuration"]["luminosity"][year]
        xsc    = Cfg['files'][smp]["cross-section"]
        genevt = Cfg['files'][smp]["generated-events"]
        
        smpScale *= ( lumi* xsc )/ genevt

        f = ROOT.TFile.Open(filename)
        _files.add(f)
        for j, key in enumerate(f.GetListOfKeys()):
            cl = ROOT.gROOT.GetClass(key.GetClassName())
            if key.ReadObj().GetName() == "xycorrmet_pt_{}_{}_hZA_lljj_{}{}_{}".format(reg, cat, tagger, wp, process):
                key.ReadObj().SetDirectory(0)
                integral = integral + key.ReadObj().Integral()
                histo_met.Add(key.ReadObj(), 1)
        histo_met.SetDirectory(0)
        histo_met.Scale(smpScale)
    return histo_met


def gethistNm(path, process):
    look_for = "GluGluToHToZATo2L2B" if process == "gg_fusion" else "HToZATo2L2B"
    prefix = []
    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        split_filename = filename.split('/')
        if str(split_filename[-1]).startswith(look_for):
            fnm = split_filename[-1].replace('preVFP.root','').replace('postVFP.root', '')
            if not fnm in prefix:
                prefix.append(fnm)
    return prefix

def optimizeMETcut(era, Cfg, path):

    category = ["MuMu", "ElEl"]#, "MuEl"]
    workingPoint = "M"
    yaxis_max = {"gg_fusion":{
                    "resolved":  5.,
                    "boosted" :  5. },
                "bb_associatedProduction":{
                    "resolved" : 5.,
                    "boosted"  : 5. }
                }
    for process in ['bb_associatedProduction']:#, 'gg_fusion']:
        prefix = gethistNm(path, process)
   
        for reg, tagger in {#'resolved':'DeepFlavour', 
                            'boosted' : 'DeepCSV'
                            }.items():
            c = []
            legend = []
            for k, cat in enumerate(category):
    
                legend.append(ROOT.TLegend(0.5,0.89,0.6,0.62))
                legend[k].SetTextSize(0.025)
                legend[k].SetBorderSize(0)
                
                histo_met_bkg = getHisto(era, Cfg, path, isBkg=True, prefix="", reg=reg, tagger=tagger, wp= workingPoint, cat=cat, process=process)

                i=0
                graphs = []
                masspoints = []
                for pref in prefix:
                    split_prefix = pref.split("_")
                    if "2000" in pref or "3000" in pref:
                        continue
                    significance = []
                    xAxis = []
                    toSkip=False
                    print( "working on ::", pref, process, reg, cat)
                    for i in range(0, 201, 5):
                        histo_met_bkg.GetXaxis().SetRangeUser(0, i)
                        #histo_met_bkg.GetYaxis().SetRangeUser(0, 1.0)
                        #Check why for different i, the integral is the same
                        histo_met_bkg.SetDirectory(0)
                        histo_met_sig = getHisto(era, Cfg, path, isBkg=False, prefix=pref, reg=reg, tagger=tagger, wp= workingPoint, cat=cat, process=process)
                        histo_met_sig.GetXaxis().SetRangeUser(0, i)
                        #histo_met_sig.GetYaxis().SetRangeUser(0, 1.0)
                        histo_met_sig.SetDirectory(0)
                        
                        #significance = 2*(SQRT(S+B)-SQRT(B))
                        #signif = 2*(math.sqrt(histo_met_sig.Integral() + histo_met_bkg.Integral()) - math.sqrt(histo_met_bkg.Integral()))
                        
                        S = histo_met_sig.Integral()
                        B = histo_met_bkg.Integral()
                        eq = 2*( (S+B)*math.log(1+S/B) -S ) 
                        
                        signif = math.sqrt(2*( (S+B)*math.log(1+S/B) -S ))
                        if eq < 0. or signif > 5.:
                            toSkip=True
                            continue
                        print ("\t\tMET_pT: ", i, "Integral (S, B) = ", (S, B), "significance =", signif)
                        
                        significance.append(float(signif))
                        xAxis.append(float(i))
    
                    if not toSkip:
                        significance_array = np.array(significance)
                        xAxis_array = np.array(xAxis)
                        graph = ROOT.TGraph(int(40), xAxis_array, significance_array)
                        graph.SetName(pref.replace('.root', ''))
                        graphs.append(graph)
                    
                        mH = split_prefix[2].replace('p00', '')
                        mA = split_prefix[4].replace('p00', '')
                        masspoints.append('(MH, MA)= (%s, %s) GeV'%(mH, mA))
                    print( "===="*20)
        
                c.append(TCanvas("c{0}".format(k),"c{0}".format(k),800,600))
                #c[k].DrawFrame(40,0.0012,160,0.02).SetTitle("Significance vs MET cut; MET cut (GeV); 2(#sqrt{S+B} - #sqrt{B})")
                #c[k].DrawFrame(0,0.0012,160,0.02).SetTitle("Significance vs MET cut; MET cut (GeV); #sqrt{2((S+B)ln(1+S/B)-S)}")
                c[k].DrawFrame(0,0,210,yaxis_max[process][reg]).SetTitle("; MET cut (GeV); Significance #sqrt{2((S+B)ln(1+S/B)-S)}")
        
                for i, (gr, Nm) in enumerate(zip(graphs, masspoints)):
                    legend[k].AddEntry(gr, Nm, "l")
                    gr.Draw("*L")
                    gr.SetMarkerStyle(ROOT.kFullSquare)
                    gr.SetMarkerColor(colors[i])
                    gr.SetLineColor(colors[i])
                
                legend[k].Draw("*L")
                
                t = c[k].GetTopMargin()
                r = c[k].GetRightMargin()
                l = c[k].GetLeftMargin()
                lumiTextOffset   = 0.2

                latex = ROOT.TLatex()
                latex.SetNDC()
                latex.SetTextAngle(0)
                latex.SetTextColor(ROOT.kBlack)
                
                lumiText = "%s fb^{-1} (13 TeV)" %format(Constants.getLuminosity(era)/1000.,'.2f')
                lumi = latex.DrawLatex(0.7,1-t+lumiTextOffset*t,lumiText)
                lumi.SetNDC()
                lumi.SetTextFont(40)
                lumi.SetTextSize(0.03)
                lumi.Draw("same")
                
                cms_text = latex.DrawLatex(0.12, 1-t+lumiTextOffset*t, "CMS Preliminary")
                cms_text.SetNDC()
                cms_text.SetTextFont(40)
                cms_text.SetTextSize(0.03)
                cms_text.Draw("same")
                
                c[k].cd() 
                c[k].SaveAs("ul{}/optimizeMETcut_{}_{}_{}_{}{}.png".format(era, process, reg, cat, tagger, workingPoint))
                c[k].SaveAs("ul{}/optimizeMETcut_{}_{}_{}_{}{}.pdf".format(era, process, reg, cat, tagger, workingPoint))
                #del c

if __name__ == "__main__":
    #path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/version20_02_19/ellipses_metcut_bjets_/results'
    #path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/version20_04_01/plots_toOptimizeMETCut/'
    #path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/ver.20_04_01/plots_toOptimizeMETCut/'
    #path = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2017__ver3/'
    #path = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver16/'
    #path = '/storage/data/cms/store/user/kjaffel/ulBamboo_results/ul_2016__ver16/'
    path  = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/forHIG/ul_2017_ver42/'
    era   = 2017
    
    with open(os.path.join(path, 'plots.yml')) as _f:
        Cfg = yaml.load(_f, Loader=yaml.FullLoader)

    optimizeMETcut(era, Cfg, os.path.join(path, 'results/'))
