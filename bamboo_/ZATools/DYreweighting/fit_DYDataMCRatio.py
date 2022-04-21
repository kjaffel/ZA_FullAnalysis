#! /bin/env python
import sys, os, os.path
import yaml
import glob
import ROOT
from ROOT import TCanvas, TPad, TLine
from ROOT import kBlack, kBlue, kRed

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/')
import Constants as Constants


def cloneTH1(hist):
    if (hist == None):
        return None
    cloneHist = ROOT.TH1F(str(hist.GetName()) + "_clone", hist.GetTitle(), hist.GetNbinsX(), hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    return cloneHist


def subtractMinorBackgrounds(h_data, h_mc):
    h_data.Add(h_mc, -1)
    h_data.SetDirectory(0)
    return h_data


def getHisto(path, Cfg, reg, prefix, list_BinEdges, bin, w, isData=False, splitDY=False, forDataSubstr=False):
    _files = set()
    gr = "data" if isData else ("mc")
    DLdataset = {"ElEl":"DoubleEGamma", "MuMu": "DoubleMuon" }
    SLdataset = {"ElEl":"SingleElectron", "MuMu": "SingleMuon" }

    if not splitDY:
        histo = ROOT.TH1F(prefix +f"_{gr}","", 60, 0., 650.)
    else:
        histo = ROOT.TH1F(prefix +f"_{gr}","", 60, list_BinEdges[bin], list_BinEdges[bin+1])
    
    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        split_filename = filename.split('/')
        smp = str(split_filename[-1])
    
        # ignore skeleton
        if smp.startswith('__skeleton__'):
            continue
        # ignore dataset that does not describe DY
        if smp.startswith('MuonEG'):
            continue
        # ignore signal 
        if 'type' in Cfg['files'][smp].keys() and Cfg['files'][smp]['type'] =='signal':
            continue

        if not isData:
            if forDataSubstr: 
                if Cfg['files'][smp]['group'] in ['data', 'DY']: 
                    continue
            else:
                if not smp.startswith("DYJetsToLL"):
                    continue
        else:
            if not Cfg['files'][smp]['group']=='data':
                continue
        
        year   = Cfg['files'][smp]["era"]
        lumi   = Cfg["configuration"]["luminosity"][year]
        sf     = 1. #lumi
        if "cross-section" in Cfg['files'][smp].keys():
            xsc    = Cfg['files'][smp]["cross-section"]
            genevt = Cfg['files'][smp]["generated-events"]
            #print( lumi , xsc, genevt )
            #sf *= xsc / (genevt)

        f = ROOT.TFile.Open(filename)
        _files.add(f)
        for cat in ['ElEl', 'MuMu']: 
            if isData:
                if not ((smp.startswith(DLdataset[cat]) or smp.startswith(SLdataset[cat]))): 
                    #print( smp, smp.startswith(DLdataset[cat]), smp.startswith(SLdataset[cat]), smp.startswith(DLdataset[cat]) or smp.startswith(SLdataset[cat]) )
                    continue
            print( 'working on :', cat , smp)
            if splitDY: varToPlots_histo = f.Get(f"{cat}_{reg}_DYweight{w}_{prefix}")
            else: varToPlots_histo = f.Get(f"{cat}_{reg}_{prefix}")
            
            histo.Add(varToPlots_histo, 1)
            histo.SetDirectory(0)
            histo.Scale(sf)

        f.Close()
    print( 'all done..........................' )
    return histo



def DYEstimation(plotCfg, files_path, year, splitDY):
    compareshape = False
    lumi = Constants.getLuminosity(year)

    if splitDY :
        BinEdges = {'mjj'  : [0., 50, 100., 200, 450., 650.],
                    'mlljj': [100., 200., 450.,650., 1200.] } 
    else:
        BinEdges = {'mjj'  : [0., 650.],
                    'mlljj': [100., 1200.] } 
    
    outDir = os.path.join(os.getcwd(), f"results/ul{year}")
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    
    for reg in ['resolved', 'boosted']:
        for idx, varToPlot in enumerate(['mjj']):#, 'mlljj']):
            for bin in range(0,len(BinEdges[varToPlot])-1):
        
                if splitDY: w = ( bin+2 if varToPlot =='mlljj' else ( bin+1))  
                else: w = 'comb'
                
                #Drell-Yan +jets mc 
                histo_mc        = getHisto(files_path, plotCfg, reg, varToPlot, BinEdges[varToPlot], bin , w, isData=False, splitDY=False, forDataSubstr=False)
                histo_other_mc  = getHisto(files_path, plotCfg, reg, varToPlot, BinEdges[varToPlot], bin , w, isData=False, splitDY=False, forDataSubstr=True)
                histo_all_data  = getHisto(files_path, plotCfg, reg, varToPlot, BinEdges[varToPlot], bin , w, isData=True, splitDY=False, forDataSubstr=False)
            
                histo_data = histo_all_data 
                #histo_data = subtractMinorBackgrounds( histo_all_data, histo_other_mc)
                
                print ("Getting Drell-Yan weight from :", BinEdges[varToPlot][bin], "to",BinEdges[varToPlot][bin+1], "GeV") 
                print ( "- Integrals ** ", ", region:", reg, ", varToPlot: ", varToPlot)
                print ( "- Data:", histo_data.Integral())
                print ( "- MC  :", histo_mc.Integral())
                print ( "====================================================================================")
                
                w_file = ROOT.TFile.Open(f"{outDir}/DYJetsToLL_weight{w}_{reg}_{varToPlot}.root", "recreate")
                histo_mc.SetDirectory(0)
                histo_data.SetDirectory(0)
                
                histo_mc.Write()
                histo_data.Write()
                w_file.Close()
        
                ratio_file = ROOT.TFile.Open(f"{outDir}/DYJetsToLL_weight{w}_{reg}_{varToPlot}.root")
                c1 = ROOT.TCanvas("c1", "c1", 800, 800)
        
                histo_mc   = ratio_file.Get("%s_mc"%varToPlot)
                histo_data = ratio_file.Get("%s_data"%varToPlot)
        
                histo_data.Scale(1./histo_data.Integral())
                histo_mc.Scale(1./histo_mc.Integral())
                
                if compareshape:
                    histo_mc.SetStats(0)
                    histo_mc.SetLineWidth(2)
                    histo_mc.SetLineColor(kRed)
                    histo_mc.GetXaxis().SetTitle("%s (GeV)"%varToPlot)
                    histo_mc.GetYaxis().SetTitle("Events ")
    
                    histo_data.SetStats(0)
                    histo_data.SetLineWidth(2)
                    histo_data.SetLineColor(kBlue)
                    histo_data.GetXaxis().SetTitle("%s (GeV)"%varToPlot)
                    histo_data.GetYaxis().SetTitle("Events ")
                
                    histo_mc.Draw()
                    histo_data.Draw("same")
                    
                    c1.SaveAs(f"{outDir}/DYJetsToLL_weight{w}_{reg}_{varToPlot}.pdf", "pdf")
                    c1.SaveAs(f"{outDir}/DYJetsToLL_weight{w}_{reg}_{varToPlot}.png", "png")
               
                    del c1
                #create histo of ratio data/MC
                c2 = ROOT.TCanvas("c2", "c2", 800, 800)
                ratio = histo_data.Clone()
                ratio.SetTitle("")
                ratio.Sumw2()
                ratio.Divide(histo_mc)
                
                ratio.SetMarkerColor(ROOT.kBlack)
                ratio.SetMarkerSize(1.5)
                ratio.SetStats(0)
                ratio.SetMinimum(0.4)
                ratio.SetMaximum(1.6)
                
                ratio.SetTitle("")
                ratio.GetYaxis().SetTitle("Data/Mc")
                ratio.GetYaxis().SetNdivisions(505)
                ratio.GetYaxis().SetTitleSize(20)
                ratio.GetYaxis().SetTitleFont(43)
                ratio.GetYaxis().SetTitleOffset(1.8)
                ratio.GetYaxis().SetLabelFont(43)
                ratio.GetYaxis().SetLabelSize(15)

                ratio.GetXaxis().SetTitle(f"{varToPlot} (GeV)" )
                ratio.GetXaxis().SetNdivisions(510)
                ratio.GetXaxis().SetTitleSize(20)
                ratio.GetXaxis().SetTitleFont(43)
                ratio.GetXaxis().SetTitleOffset(4.)
                ratio.GetXaxis().SetLabelFont(43)
                ratio.GetXaxis().SetLabelSize(15)

                fit_func = ROOT.TF1("pol6", "pol6")
                fit_func.SetParameter(1, 0.0000005)
                ratio.Fit(fit_func)

                line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1, ratio.GetXaxis().GetXmax(), 1)
                line.SetLineColor(ROOT.kBlack)
                line.Draw("")
                
                add_ratio = ROOT.TFile.Open(f"{outDir}/DYJetsToLL_weight{w}_{reg}_{varToPlot}_DataMc_ratio.root", "recreate")
                ratio.SetDirectory(0)
                ratio.Write()
                add_ratio.Close()

                ratio.Draw()
                c2.SaveAs(f"{outDir}/DYJetsToLL_weight{w}_{reg}_{varToPlot}_DataMC_ratio.pdf", "pdf")
                c2.SaveAs(f"{outDir}/DYJetsToLL_weight{w}_{reg}_{varToPlot}_DataMC_ratio.png", "png")
        
                ratio_file.Close()

if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)
    
    #files_path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.15.05/results'
    #files_path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.7/results'
    #files_path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.9/results'
    #files_path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2017Results/controlPlots2017v.8/ver20.05.28/results'
    
    #files_path  = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2017__ver19/results' 
    #files_path  = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver27/results' 
    files_path  = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2018__ver10/results' 

    year = 2018
   
    with open(os.path.join(files_path.replace('/results',''), 'plots.yml')) as _f:
        plotConfig = yaml.load(_f, Loader=yaml.FullLoader)

    DYEstimation(plotConfig, files_path, year, splitDY=False)
