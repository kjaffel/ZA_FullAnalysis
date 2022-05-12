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

def getHistTemplate(path, gr, prefix, reg):
    
    filename = glob.glob(os.path.join(path, '*.root'))[0]
    f = ROOT.TFile.Open(filename)
    hist  = f.Get(f"MuMu_noBtag_{reg}_{prefix}")
    
    histo = ROOT.TH1F(prefix +f"_{gr}","", hist.GetNbinsX(), hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    histo.Reset()
    histo.Sumw2()
    histo.SetDirectory(0)
    
    f.Close()
    return histo

def subtractMinorBackgrounds(h_data, h_mc, lumi):
    h_data.Add(h_mc, -1)
    h_data.SetDirectory(0)
    return h_data

def getHisto(path, Cfg, reg, prefix, isData=False, forDataSubstr=False):
    _files = set()
    gr = "data" if isData else ("mc")
    
    DLdataset = {"ElEl":"DoubleEG", "MuMu": "DoubleMuon" }
    SLdataset = {"ElEl":"SingleElectron", "MuMu": "SingleMuon" }


    histo = getHistTemplate(path, gr, prefix, reg)

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
        sf     = lumi
        if "cross-section" in Cfg['files'][smp].keys():
            xsc    = Cfg['files'][smp]["cross-section"]
            genevt = Cfg['files'][smp]["generated-events"]
            print( lumi, xsc, genevt )
            sf *= xsc / (genevt)
        if year == "2018":
            DLdataset["ElEl"] ="EGamma"

        f = ROOT.TFile.Open(filename)
        _files.add(f)
        for cat in ['MuMu', 'ElEl']: 
            if isData:
                if not ((smp.startswith(DLdataset[cat]) or smp.startswith(SLdataset[cat]))): 
                    continue
            #print( 'working on :', cat , smp)
            varToPlots_histo = f.Get(f"{cat}_noBtag_{reg}_{prefix}")
            histo.Add(varToPlots_histo, 1)
            histo.SetDirectory(0)
            
            if forDataSubstr and not isData:
                #histo.Sumw2()
                histo.Scale(sf)

        f.Close()
    print( 'all done..........................' )
    return histo



def DYEstimation(plotCfg, files_path, year, n , splitDYweight, compareshape):
    lumi = Constants.getLuminosity(year)

    if splitDYweight :
        BinEdges = {'resolved': {'mjj': [0., 50, 100., 200, 450., 650.], 'mlljj': [100., 200., 450., 650., 1200.] },
                    'boosted' : {'mjj': [], 'mlljj': [] } }
    else:
        BinEdges = {'resolved': {'mjj' : [0., 650.], 'mlljj': [120., 650.] },
                    'boosted' : {'mjj' : [0., 150.], 'mlljj': [200., 650.] } }
        
        n0 = { 2016: 6,
               2017: 7,
               2018: 6 }

    outDir = os.path.join(os.getcwd(), f"results/ul{year}")
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    
    for reg in ['boosted']:#, 'boosted']:
        for idx, varToPlot in enumerate(['mjj']):#, 'mlljj']):
            for bin in range(0,len(BinEdges[reg][varToPlot])-1):
        
                if splitDYweight: w = bin  
                else: w = 'comb'
                
                #Drell-Yan +jets mc 
                histo_mc        = getHisto(files_path, plotCfg, reg, varToPlot, isData=False, forDataSubstr=False)
                histo_other_mc  = getHisto(files_path, plotCfg, reg, varToPlot, isData=False, forDataSubstr=True)
                histo_all_data  = getHisto(files_path, plotCfg, reg, varToPlot, isData=True, forDataSubstr=False)
            
                #histo_data  = histo_all_data 
                histo_data = subtractMinorBackgrounds( histo_all_data, histo_other_mc, lumi)
                
                print ("Getting Drell-Yan weight from polynomial fit order ", n, "from bin ",BinEdges[reg][varToPlot][bin], "to",BinEdges[reg][varToPlot][bin+1], "GeV") 
                print ( "Integrals ** ", ", region:", reg, ", distribution: ", varToPlot)
                print ( "- Data     :", histo_data.Integral())
                print ( "- MC       :", histo_mc.Integral())
                print ( "- other mc :", histo_other_mc.Integral())
                print ( "====================================================================================")
                
                
                w_file = ROOT.TFile.Open(f"{outDir}/DYJetsToLL_weight{w}_polfit{n}_{reg}_{varToPlot}.root", "recreate")
                histo_mc.SetDirectory(0)
                histo_data.SetDirectory(0)
                
                histo_mc.Write()
                histo_data.Write()
                w_file.Close()
        
                ratio_file = ROOT.TFile.Open(f"{outDir}/DYJetsToLL_weight{w}_polfit{n}_{reg}_{varToPlot}.root")
                c1 = ROOT.TCanvas("c1", "c1", 800, 800)
        
                histo_mc   = ratio_file.Get("%s_mc"%varToPlot)
                histo_data = ratio_file.Get("%s_data"%varToPlot)
        
                histo_data.Sumw2()
                histo_mc.Sumw2()
                
                histo_data.Scale(1./histo_data.Integral())
                histo_mc.Scale(1./histo_mc.Integral())
                
                histo_data.ResetStats()
                histo_mc.ResetStats()
                

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
                    
                    c1.SaveAs(f"{outDir}/DYJetsToLL_weight{w}_polfit{n}_{reg}_{varToPlot}.pdf", "pdf")
                    c1.SaveAs(f"{outDir}/DYJetsToLL_weight{w}_polfit{n}_{reg}_{varToPlot}.png", "png")
               
                    del c1
                #create histo of ratio data/MC
                c2 = ROOT.TCanvas("c2", "c2", 800, 800)
                ratio = histo_data.Clone()
                ratio.SetTitle("")
                ratio.Sumw2()
                ratio.SetStats(0)
                ratio.Divide(histo_mc)
                
                ratio.SetMarkerColor(ROOT.kBlack)
                ratio.SetMarkerStyle(20)
                ratio.SetMarkerSize(1.5)
                ratio.SetMinimum(0.6)
                ratio.SetMaximum(1.4)
                
                ratio.SetTitle("")
                ratio.GetYaxis().SetTitle("Data/Mc")
                ratio.GetYaxis().SetNdivisions(505)
                ratio.GetYaxis().SetTitleSize(20)
                ratio.GetYaxis().SetTitleFont(43)
                ratio.GetYaxis().SetTitleOffset(1.8)
                ratio.GetYaxis().SetLabelFont(43)
                ratio.GetYaxis().SetLabelSize(15)

                ratio.GetXaxis().SetTitle(f"{varToPlot} (GeV)")
                ratio.GetXaxis().SetNdivisions(510)
                ratio.GetXaxis().SetTitleSize(20)
                ratio.GetXaxis().SetTitleFont(43)
                ratio.GetXaxis().SetTitleOffset(1.8)
                ratio.GetXaxis().SetLabelFont(43)
                ratio.GetXaxis().SetLabelSize(15)

                b0 = BinEdges[reg][varToPlot][bin]
                b1 = 150.
                b2 = BinEdges[reg][varToPlot][bin+1]
                

                gaus_pars  = []
                pol_highmass_params = []
                pol_lowmass_params  = []
                if reg == 'resolved':
                
                    #fit_func1 = ROOT.TF1("gaus", "gaus", 0., b1)
                    fit_func1 = ROOT.TF1(f"pol{n0[year]}", f"pol{n0[year]}", 30., b1)
                    fit_func2 = ROOT.TF1(f"pol{n}", f"pol{n}", b1, b2)
                
                    #fit_func1.SetParameter(1, 0.0000005)
                    #fit_func2.SetParameter(1, 0.0000005)
                
                    ratio.Fit(fit_func1, "R")
                    ratio.Fit(fit_func2, "R+")
                
                    for i in range(0, n0[year]+1):
                        p = fit_func1.GetParameter(i)
                        pol_lowmass_params.append(p)
                else:
                    fit_func2 = ROOT.TF1(f"pol{n}", f"pol{n}", 10., 200.)
                    ratio.Fit(fit_func2, "R")
                
                if histo_mc.Integral(histo_mc.FindBin(b2), histo_mc.FindBin(1200)) != 0 :
                    #print( ratio.GetNbinsX(), ratio.GetXaxis().GetBinLowEdge(2), ratio.FindBin(20))
                    binWgt = histo_data.Integral(histo_data.FindBin(b2), histo_data.FindBin(1200))/histo_mc.Integral(histo_mc.FindBin(b2), histo_mc.FindBin(1200))
                
                for i in range(0, n+1):
                    p = fit_func2.GetParameter(i)
                    pol_highmass_params.append(p)
                
                print("========"*10)
                print(f'Parms for:  {reg} {varToPlot}')
                print( 'gaus fit degree 3:', gaus_pars)
                print(f'low mass pol fit degree {n0[year]} parameters:', pol_lowmass_params)
                print(f'high mass pol fit degree {n} parameters:', pol_highmass_params)
                print(f'scale factor [{b2}-1200] GeV :', binWgt)
                print("========"*10)

                line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1, ratio.GetXaxis().GetXmax(), 1)
                line.SetLineColor(ROOT.kBlack)
                line.Draw("")
                
                add_ratio = ROOT.TFile.Open(f"{outDir}/DYJetsToLL_weight{w}_polfit{n}_{reg}_{varToPlot}_DataMC_ratio.root", "recreate")
                ratio.SetDirectory(0)
                ratio.Write()
                add_ratio.Close()

                ratio.Draw()
                c2.SaveAs(f"{outDir}/DYJetsToLL_weight{w}_polfit{n}_{reg}_{varToPlot}_DataMC_ratio.pdf", "pdf")
                c2.SaveAs(f"{outDir}/DYJetsToLL_weight{w}_polfit{n}_{reg}_{varToPlot}_DataMC_ratio.png", "png")
        
                ratio_file.Close()

if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)
    
    #files_path  = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.15.05/results'
    #files_path  = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.7/results'
    #files_path  = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.9/results'
    #files_path  = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2017Results/controlPlots2017v.8/ver20.05.28/results'
    #files_path  = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2017__ver19/results' 
    #files_path  = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver27/results' 
    #files_path  = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2018__ver10/results' 
    
    files_path = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver28/results'
    #files_path = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2017__ver27/results'
    #files_path = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2018__ver11/results'
    
    year = 2016
   
    with open(os.path.join(files_path.replace('/results',''), 'plots.yml')) as _f:
        plotConfig = yaml.load(_f, Loader=yaml.FullLoader)
    
    for polfit in [4, 5, 6, 7, 8]:
        DYEstimation(plotConfig, files_path, year, polfit, splitDYweight=False, compareshape=False)
