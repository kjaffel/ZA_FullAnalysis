#! /bin/env python
import sys, os, os.path
import collections
import yaml
import glob
import ROOT
import json
import pprint

from json import JSONEncoder
from ROOT import TCanvas, TPad, TLine
from ROOT import kBlack, kBlue, kRed

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/')
import Constants as Constants


class MarkedList:
    _list = None
    def __init__(self, l):
        self._list = l


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, MarkedList):
            return "##<{}>##".format(o._list)


def cloneTH1(hist):
    if (hist == None):
        return None
    cloneHist = ROOT.TH1F(str(hist.GetName()) + "_clone", hist.GetTitle(), hist.GetNbinsX(), hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    return cloneHist


def EraPOGFormat(year):
    return 'UL'+ str(year).replace('20', '').replace('-','')


def getHistTemplate(path, gr, prefix, reg):
    
    filename = glob.glob(os.path.join(path, '*.root'))[0]
    f = ROOT.TFile.Open(filename)
    hist   = f.Get(f"MuMu_noBtag_{reg}_{prefix}")
    #hist  = f.Get(f"MuMu_{reg}_0Btag_{prefix}")
    
    histo = ROOT.TH1F(prefix +f"_{gr}","", hist.GetNbinsX(), hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    #histo.Reset()
    histo.Sumw2()
    histo.SetDirectory(0)
    
    f.Close()
    return histo


def subtractMinorBackgrounds(h_data, h_mc):
    
    h_data.Add(h_mc, -1)
    h_data.SetDirectory(0)
    return h_data


def getHisto(year, path, Cfg, flavour, reg, prefix, isData=False, forDataSubstr=False):
    gr = "data" if isData else ("mc")
    
    requested_flav = ['MuMu', 'ElEl'] if flavour=='LL' else [flavour]
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
        # well better play safe, the histogram will be empty anyway if no events pass 
        #if smp.startswith('MuonEG'):
        #    continue
        
        # ignore signal 
        if 'type' in Cfg['files'][smp].keys() and Cfg['files'][smp]['type'] =='signal':
            continue

        # ignore same root file for different year if happend the given path is the same !
        if not EraPOGFormat(year) in smp:
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
        
        lumi    = Cfg["configuration"]["luminosity"][year]
        if "cross-section" in Cfg['files'][smp].keys():
            xsc    = Cfg['files'][smp]["cross-section"]
            genevt = Cfg['files'][smp]["generated-events"]
            print( lumi, xsc, genevt )
            sf = lumi * xsc / (genevt)
        
        if year == "2018":
            DLdataset["ElEl"] ="EGamma"

        f = ROOT.TFile.Open(filename)
        print ( 'looking into :', smp)
        for cat in requested_flav:
            
            varToPlots_histo = f.Get(f"{cat}_noBtag_{reg}_{prefix}") #old version 
            print( 'adding ::', f"{cat}_noBtag_{reg}_{prefix}")
            #varToPlots_histo = f.Get(f"{cat}_{reg}_0Btag_{prefix}")
            #print( 'adding ::', f"{cat}_{reg}_0Btag_{prefix}")
            if not isData:
                varToPlots_histo.Scale(sf)
            histo.Add(varToPlots_histo, 1)
            histo.SetDirectory(0)
        f.Close()
            
    print( 'all done..........................' )
    return histo



def DYEstimation(plotCfg, files_path, flavour, year, n0, n , splitDYweight, compareshape):
    
    lumi = Constants.getLuminosity(year)

    if splitDYweight :
        BinEdges = {'resolved': {'mjj': [0., 50, 100., 200, 450., 650.], 'mlljj': [100., 200., 450., 650., 1200.] },
                    'boosted' : {'mjj': [], 'mlljj': [] } }
    else:
        BinEdges = {'resolved': {'mjj' : [0., 650.], 'mlljj': [120., 650.] },
                    'boosted' : {'mjj' : [0., 150.], 'mlljj': [200., 650.] } }
        
    
    outDir = os.path.join(os.getcwd(), f"results/ul{year}/{flavour}")
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    
    sf = {}
    for reg in ['resolved', 'boosted']:
        
        func = f'{n0}-{n}' if reg == 'resolved' else str(n)
        sf[reg] = {}
        for idx, varToPlot in enumerate(['mjj']):#, 'mlljj']):
            
            sf[reg][varToPlot] = {}
            for bin in range(0,len(BinEdges[reg][varToPlot])-1):
        
                if splitDYweight: w = bin  
                else: w = 'comb'
                
                #Drell-Yan +jets mc 
                histo_mc        = getHisto(year, files_path, plotCfg, flavour, reg, varToPlot, isData=False, forDataSubstr=False)
                histo_other_mc  = getHisto(year, files_path, plotCfg, flavour, reg, varToPlot, isData=False, forDataSubstr=True)
                histo_all_data  = getHisto(year, files_path, plotCfg, flavour, reg, varToPlot, isData=True, forDataSubstr=False)
            
                #histo_data  = histo_all_data 
                histo_data = subtractMinorBackgrounds( histo_all_data, histo_other_mc)
                
                print ( " Get Drell-Yan weight from polynomial fit order ", n, "from bin ",BinEdges[reg][varToPlot][bin], "to",BinEdges[reg][varToPlot][bin+1], "GeV") 
                print ( " Integrals ** ", ", region:", reg, ", distribution: ", varToPlot)
                print ( " Data     :", histo_data.Integral())
                print ( " MC       :", histo_mc.Integral())
                print ( " other mc :", histo_other_mc.Integral())
                print ( " Data/MC  :", histo_data.Integral()/histo_other_mc.Integral())
                print ( " Data - other_mc/Drell-Yan mc  :", (histo_data.Integral() - histo_other_mc.Integral() )/histo_other_mc.Integral())
                print ( "====================================================================================")
                
                
                w_file = ROOT.TFile.Open(f"{outDir}/DYJetsToLL_weight{w}_polfit{func}_{reg}_{varToPlot}.root", "recreate")
                histo_mc.SetDirectory(0)
                histo_data.SetDirectory(0)
                
                histo_mc.Write()
                histo_data.Write()
                w_file.Close()
        
                ratio_file = ROOT.TFile.Open(f"{outDir}/DYJetsToLL_weight{w}_polfit{func}_{reg}_{varToPlot}.root")
                c1 = ROOT.TCanvas("c1", "c1", 800, 800)
        
                histo_mc   = ratio_file.Get("%s_mc"%varToPlot)
                histo_data = ratio_file.Get("%s_data"%varToPlot)
        
                #histo_data.Sumw2()
                #histo_mc.Sumw2()
                
                #histo_data.Scale(1./histo_data.Integral())
                #histo_mc.Scale(1./histo_mc.Integral())
                
                #histo_data.ResetStats()
                #histo_mc.ResetStats()
                
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
                    
                    c1.SaveAs(f"{outDir}/DYJetsToLL_weight{w}_polfit{func}_{reg}_{varToPlot}.pdf", "pdf")
                    c1.SaveAs(f"{outDir}/DYJetsToLL_weight{w}_polfit{func}_{reg}_{varToPlot}.png", "png")
               
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
                    fit_func1 = ROOT.TF1(f"pol{n0}", f"pol{n0}", 10., b1)
                    fit_func2 = ROOT.TF1(f"pol{n}", f"pol{n}", b1, b2)
                
                    #fit_func1.SetParameter(1, 0.0000005)
                    #fit_func2.SetParameter(1, 0.0000005)
                
                    ratio.Fit(fit_func1, "R")
                    ratio.Fit(fit_func2, "R+")
                
                    for i in range(0, n0+1):
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
                #print( 'gaus fit degree 3:', gaus_pars)
                print(f'Parms for:  {reg} {varToPlot}')
                print(f'low mass pol fit degree {n0} parameters:', pol_lowmass_params)
                print(f'high mass pol fit degree {n} parameters:', pol_highmass_params)
                print(f'scale factor [{b2}-1200] GeV :', binWgt)
                print("========"*10)
                
                sf[reg][varToPlot][bin]= {'low_mass': pol_lowmass_params, 'high_mass': pol_highmass_params, 'binWgt': binWgt }

                line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1, ratio.GetXaxis().GetXmax(), 1)
                line.SetLineColor(ROOT.kBlack)
                line.Draw("")
                
                add_ratio = ROOT.TFile.Open(f"{outDir}/DYJetsToLL_weight{w}_polfit{func}_{reg}_{varToPlot}_DataMC_ratio.root", "recreate")
                ratio.SetDirectory(0)
                ratio.Write()
                add_ratio.Close()

                ratio.Draw()
                c2.SaveAs(f"{outDir}/DYJetsToLL_weight{w}_polfit{func}_{reg}_{varToPlot}_DataMC_ratio.pdf", "pdf")
                c2.SaveAs(f"{outDir}/DYJetsToLL_weight{w}_polfit{func}_{reg}_{varToPlot}_DataMC_ratio.png", "png")
        
                ratio_file.Close()
    return sf

if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)
    
    pp = pprint.PrettyPrinter(indent=2)
    
    #files_path  = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.15.05/results'
    #files_path  = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.7/results'
    #files_path  = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/forexo/controlPlots2017v.9/results'
    #files_path  = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2017Results/controlPlots2017v.8/ver20.05.28/results'
    #files_path  = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2017__ver19/results' 
    #files_path  = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver27/results' 
    #files_path  = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2018__ver10/results' 
    
    n0 = { '2016-preVFP' : 6, 
           '2016-postVFP': 6, 
            '2017': 7, 
            '2018': 6 
            }
    
    for flavour in ['LL', 'ElEl', 'MuMu']:
        
        for year, files_path in {#2016: '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_run2__ver10/results',
                                 #2017: '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_run2__ver10/results',
                                 #2018: '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_run2__ver10/results',
                                 '2016-preVFP' : '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver28/results',
                                 '2016-postVFP': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver28/results',
                                 '2017': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2017__ver27/results',
                                 '2018': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2018__ver11/results',
                                }.items():
   
            
            
            era = year.replace('20', '').replace('-','')
            jsf_nm = f"DYJetsTo{flavour}_TuneCP5_13TeV-amcatnloFXFX-pythia8_polyfitWeights_RunIISummer20UL{era}_NanoAODv9.json"
        
            scale_factor = collections.defaultdict(list)
            scale_factor[year] = {'resolved': { 
                                        'mjj'  : {},
                                        'mlljj': {} },   
                                'boosted': {
                                        'mjj'  : {},
                                        'mlljj': {} }
                                }
            if not files_path:
                continue
    
            with open(os.path.join(files_path.replace('/results',''), 'plots.yml')) as _f:
                plotConfig = yaml.load(_f, Loader=yaml.FullLoader)
            
                
                for deg in [4, 5, 6, 7, 8]:
                    sf = DYEstimation(plotConfig, files_path, flavour, year, n0[year], deg, splitDYweight=False, compareshape=False)
                    
                    for reg, wgt_mass in sf.items():
                        for m, wgt_per_bin in wgt_mass.items():
                            for bin, wgt_massplane in wgt_per_bin.items(): # it is just one bin FIXME later
                                if reg == 'resolved':
                                    scale_factor[year][reg][m].update({f"polyfit{n0[year]}":sf[reg][m][bin]['low_mass']})
                                scale_factor[year][reg][m].update({f"polyfit{deg}":sf[reg][m][bin]['high_mass']})
                                scale_factor[year][reg][m].update({f"binWgt":sf[reg][m][bin]['binWgt']})
            
            #pp.pprint(scale_factor)
            with open(jsf_nm, 'w') as _f:
                b = json.dumps(scale_factor, indent=2, separators=(',', ':'), cls=CustomJSONEncoder)
                b = b.replace('"##<', "").replace('>##"', "")
                _f.write(b)
                print('Drell-Yan reweighting is saved in : ', jsf_nm)
