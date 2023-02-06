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


def getHistTemplate(rf, gr, prefix, reg):
    
    f     = ROOT.TFile.Open(rf)
    hist  = f.Get(f"MuMu_{reg}_0Btag_{prefix}")
    
    #histo = ROOT.TH1F(prefix +f"_{gr}","", hist.GetNbinsX(), hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    histo  = hist.Clone()
    
    histo.Reset()
    histo.Sumw2()
    histo.SetName(prefix +f"_{gr}") 
    histo.SetDirectory(0)
    
    f.Close()
    return histo


def subtractMinorBackgrounds(h_data, h_mc):
    
    h_data.Add(h_mc, -1)
    h_data.SetDirectory(0)
    return h_data


def getHisto(year, path, Cfg, flavour, reg, prefix, isData=False, forDataSubstr=False):
    histo = None
    gr    = "data" if isData else ("mc")
    
    requested_flav = ['MuMu', 'ElEl'] if flavour=='LL' else [flavour]
    DLdataset = {"ElEl":"DoubleEG", "MuMu": "DoubleMuon" }
    SLdataset = {"ElEl":"SingleElectron", "MuMu": "SingleMuon" }
    
    if year == "2018":
        DLdataset["ElEl"] ="EGamma"
    
    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        split_filename = filename.split('/')
        smp = str(split_filename[-1])
    
        # ignore skeleton
        if smp.startswith('__skeleton__'):
            continue
        # ignore signal 
        if 'HToZATo2L2B_' in smp:
            continue
        if 'AToZHTo2L2B_' in smp:
            continue
        if 'type' in Cfg['files'][smp].keys() and Cfg['files'][smp]['type'] =='signal':
            continue

        # ignore same root file for different year if happend the given path is the same !
        if not EraPOGFormat(year) in smp:
            continue
        
        if not isData:
            if forDataSubstr: # found all processes that need to be substracted from data! that isn't DY too
                if Cfg['files'][smp]['group'] in ['data', 'DY']: 
                    continue
            else:
                if not smp.startswith("DYJetsToLL"):
                    continue
        else:
            if not Cfg['files'][smp]['group']=='data':
                continue
        
        
        era     = Cfg["files"][smp]['era']
        lumi    = Cfg["configuration"]["luminosity"][era]
        if "cross-section" in Cfg['files'][smp].keys():
            xsc    = Cfg['files'][smp]["cross-section"]
            genevt = Cfg['files'][smp]["generated-events"]
            sf = lumi * xsc / (genevt)
        
        f = ROOT.TFile.Open(filename)
        print ( 'Adding sample :', smp)
        
        if not isData:
            print ( '\t - lumi, xsc, genevt :',  lumi, xsc, genevt)
        
        for cat in requested_flav:
            varToPlots_histo = f.Get(f"{cat}_{reg}_0Btag_{prefix}")
            varToPlots_histo.SetDirectory(0)
            print( '\t - histogram :', f"{cat}_{reg}_0Btag_{prefix}")
            
            if not isData:
                varToPlots_histo.Scale(sf)
            if histo is None:
                histo = varToPlots_histo.Clone()
                histo.SetName(prefix +f"_{gr}")
            else:
                histo.Add(varToPlots_histo, 1)
            histo.SetDirectory(0)
        f.Close()
            
    print( 'all done..........................' )
    return histo


def formatted_bin(_tup):
    return '{}_to_{}'.format(int(_tup[0]),int(_tup[1]))


def getSF_dict(year, BinEdges):
    scale_factor = collections.defaultdict(list)
    scale_factor[year] = {}
    for i, reg in enumerate(['boosted', 'resolved']):

        scale_factor[year][reg] = {}
        for mass in ['mjj']:#, 'mlljj']:
            
            scale_factor[year][reg][mass] = {}
            fit_range_tup = BinEdges[reg][mass]

            if reg == 'resolved':
                scale_factor[year][reg][mass].update({
                        f'highmass_{formatted_bin(fit_range_tup[1])}': {} })
            scale_factor[year][reg][mass].update({
                        f'lowmass_{formatted_bin(fit_range_tup[0])}': {},
                        f'binWgt_above_{int(fit_range_tup[i][1])}': {} })
    return scale_factor


def DYEstimation(plotCfg, files_path, flavour, year, nlowmass, n, compareshape):
    
    lumi = Constants.getLuminosity(year)
    
    outDir = os.path.join(os.getcwd(), f"results/ul{year}/{flavour}")
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    
    sf = {}
    for reg in ['resolved', 'boosted']:
        
        func = f'{nlowmass}-{n}' if reg == 'resolved' else str(n)
        sf[reg] = {}
        for idx, varToPlot in enumerate(['mjj']):#, 'mlljj']):
            
            sf[reg][varToPlot] = {}
                
            histo_dy_mc     = getHisto(year, files_path, plotCfg, flavour, reg, varToPlot, isData=False, forDataSubstr=False)
            histo_other_mc  = getHisto(year, files_path, plotCfg, flavour, reg, varToPlot, isData=False, forDataSubstr=True)
            histo_all_data  = getHisto(year, files_path, plotCfg, flavour, reg, varToPlot, isData=True, forDataSubstr=False)
        
            #histo_data  = histo_all_data 
            histo_data = subtractMinorBackgrounds( histo_all_data, histo_other_mc)
            
            print ( " Integrals ** ", ", region:", reg, ", distribution: ", varToPlot)
            print ( " Data     :", histo_data.Integral())
            print ( " MC       :", histo_dy_mc.Integral())
            print ( " other mc :", histo_other_mc.Integral())
            print ( " Data/MC  :", histo_data.Integral()/histo_other_mc.Integral())
            print ( " Data - other_mc/Drell-Yan mc  :", (histo_data.Integral() - histo_other_mc.Integral() )/histo_other_mc.Integral())
            print ( "====================================================================================")
            
            f_nm = f"{outDir}/DYJetsToLL_weightcomb_polfit{func}_{reg}_{varToPlot}.root" 
            w_file = ROOT.TFile.Open(f_nm, "recreate")
            histo_dy_mc.SetDirectory(0)
            histo_data.SetDirectory(0)
            
            histo_dy_mc.Write()
            histo_data.Write()
            w_file.Close()
    
            ratio_file  = ROOT.TFile.Open(f_nm)
            histo_dy_mc = ratio_file.Get("%s_mc"%varToPlot)
            histo_data  = ratio_file.Get("%s_data"%varToPlot)
            
            #histo_data.Sumw2()
            #histo_dy_mc.Sumw2()
            
            #histo_data.Scale(1./histo_data.Integral())
            #histo_dy_mc.Scale(1./histo_dy_mc.Integral())
            
            #histo_data.ResetStats()
            #histo_dy_mc.ResetStats()
            
            if compareshape:
                c1 = ROOT.TCanvas("c1", "c1", 800, 800)
                
                histo_dy_mc.SetStats(0)
                histo_dy_mc.SetLineWidth(2)
                histo_dy_mc.SetLineColor(kRed)
                histo_dy_mc.GetXaxis().SetTitle("%s (GeV)"%varToPlot)
                histo_dy_mc.GetYaxis().SetTitle("Events ")

                histo_data.SetStats(0)
                histo_data.SetLineWidth(2)
                histo_data.SetLineColor(kBlue)
                histo_data.GetXaxis().SetTitle("%s (GeV)"%varToPlot)
                histo_data.GetYaxis().SetTitle("Events ")
            
                histo_dy_mc.Draw()
                histo_data.Draw("same")
                
                c1.SaveAs(f"{outDir}/DYJetsToLL_weightcomb_polfit{func}_{reg}_{varToPlot}.pdf", "pdf")
                c1.SaveAs(f"{outDir}/DYJetsToLL_weightcomb_polfit{func}_{reg}_{varToPlot}.png", "png")
            
                del c1
            
            #create histo of ratio data/MC
            ratio = histo_data.Clone()
            ratio.SetTitle("")
            ratio.Sumw2()
            ratio.SetStats(0)
            ratio.Divide(histo_dy_mc)
            
            c2 = ROOT.TCanvas("c2", "c2", 800, 800)
            c2.DrawFrame(-12,-12,12,12)
            
            ROOT.gStyle.SetOptTitle(0)
            ROOT.gStyle.SetOptStat(0)
            ROOT.gStyle.SetOptFit(1111)
            ROOT.gStyle.SetStatBorderSize(0)
            ROOT.gStyle.SetStatX(.89)
            ROOT.gStyle.SetStatY(.89)
            
            ratio.SetMarkerColor(ROOT.kBlack)
            ratio.SetMarkerStyle(20)
            ratio.SetMarkerSize(1.5)
            ratio.SetMinimum(0.6)
            ratio.SetMaximum(1.4)
            
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

            fit_range_tup   = BinEdges[reg][varToPlot]
            pol_highmass_params = []
            pol_lowmass_params  = []
            if reg == 'resolved':
            
                fit_func1 = ROOT.TF1(f"pol{nlowmass}", f"pol{nlowmass}", BinEdges[reg][varToPlot][0][0], BinEdges[reg][varToPlot][0][1])
                fit_func2 = ROOT.TF1(f"pol{n}", f"pol{n}", BinEdges[reg][varToPlot][1][0], BinEdges[reg][varToPlot][1][1])
            
                #fit_func1.SetParameter(1, 0.0000005)
                #fit_func2.SetParameter(1, 0.0000005)
                
                fit_func1.SetLineColor(ROOT.kBlue)
                fit_func2.SetLineColor(ROOT.kRed)
                
                ratio.Fit(fit_func1, "R")
                ratio.Fit(fit_func2, "R+")
                
                fit_func1.Print()
                fit_func2.Print()
                
                last_bin_of_fit = BinEdges[reg][varToPlot][1][1]
                
                for i in range(0, nlowmass+1):
                    p = fit_func1.GetParameter(i)
                    pol_lowmass_params.append(p)

                for i in range(0, n+1):
                    p = fit_func2.GetParameter(i)
                    pol_highmass_params.append(p)
                
                print("========"*10)
                print(f'Parms for:  {reg} {varToPlot}')
                print(f'low mass ({BinEdges[reg][varToPlot][0][0]}, {BinEdges[reg][varToPlot][0][1]}) GeV pol fit degree {nlowmass} parameters:', pol_lowmass_params)
                print(f'high mass ({BinEdges[reg][varToPlot][1][0]}, {BinEdges[reg][varToPlot][1][1]}) GeV pol fit degree {n} parameters:', pol_highmass_params)
            else:
                fit_func1 = ROOT.TF1(f"pol{n}", f"pol{n}", BinEdges[reg][varToPlot][0][0], BinEdges[reg][varToPlot][0][1])
                fit_func1.SetLineColor(ROOT.kBlue)
                
                ratio.Fit(fit_func1, "R")
                fit_func1.Print()
                
                last_bin_of_fit = BinEdges[reg][varToPlot][0][1]
                
                for i in range(0, n+1):
                    p = fit_func1.GetParameter(i)
                    pol_lowmass_params.append(p)
                
                print("========"*10)
                print(f'Parms for:  {reg} {varToPlot}')
                print(f'low mass ({BinEdges[reg][varToPlot][0][0]}, {BinEdges[reg][varToPlot][0][1]}) GeV pol fit degree {n} parameters:', pol_lowmass_params)
                
            if histo_dy_mc.Integral(histo_dy_mc.FindBin(last_bin_of_fit), histo_dy_mc.FindBin(1200)) != 0 :
                #print( ratio.GetNbinsX(), ratio.GetXaxis().GetBinLowEdge(2), ratio.FindBin(20))
                binWgt = histo_data.Integral(histo_data.FindBin(last_bin_of_fit), histo_data.FindBin(1200))/histo_dy_mc.Integral(histo_dy_mc.FindBin(last_bin_of_fit), histo_dy_mc.FindBin(1200))
            
            print(f'scale factor ({last_bin_of_fit}, 1200) GeV :', binWgt)
            print("========"*10)
            
            
            sf[reg][varToPlot] = {f'lowmass_{formatted_bin(fit_range_tup[0])}' : pol_lowmass_params, 
                                  f'binWgt_above_{int(last_bin_of_fit)}'        : binWgt }
            if reg == 'resolved':
                sf[reg][varToPlot].update({f'highmass_{formatted_bin(fit_range_tup[1])}': pol_highmass_params})


            ratio.Draw()
            
            t = c2.GetTopMargin()
            r = c2.GetRightMargin()
            l = c2.GetLeftMargin()
            lumiTextOffset   = 0.2

            latex = ROOT.TLatex()
            latex.SetNDC()
            latex.SetTextAngle(0)
            latex.SetTextColor(ROOT.kBlack)

            lumiText = "%s #fb^{-1} (13 TeV)" %format(Constants.getLuminosity(year)/1000.,'.2f')
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

            line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1, ratio.GetXaxis().GetXmax(), 1)
            line.SetLineWidth(5)
            line.SetLineColor(ROOT.kBlack)
            line.Draw("PE")
            
            add_ratio = ROOT.TFile.Open(f"{outDir}/DYJetsToLL_weightcomb_polfit{func}_{reg}_{varToPlot}_DataMC_ratio.root", "recreate")
            ratio.SetDirectory(0)
            ratio.Write()
            add_ratio.Close()

            c2.SaveAs(f"{outDir}/DYJetsToLL_weightcomb_polfit{func}_{reg}_{varToPlot}_DataMC_ratio.pdf", "pdf")
            c2.SaveAs(f"{outDir}/DYJetsToLL_weightcomb_polfit{func}_{reg}_{varToPlot}_DataMC_ratio.png", "png")
    
            ratio_file.Close()
            del c2
    return sf

if __name__ == "__main__":
    
    ROOT.gROOT.SetBatch(True)
    
    pp = pprint.PrettyPrinter(indent=2)
    
    nlowmass = { '2016-preVFP' : 6,  # test for resolved that it works well, let's try to get best fit for high mass
                 '2016-postVFP': 6, 
                 '2016': 6, 
                 '2017': 7, 
                 '2018': 6 
                }
    
    BinEdges  = {'resolved': {
                         'mjj'   : [(10., 150.), (150., 600.)], 
                         #'mlljj': [(120., 650.) # not in use 
                         },
                     'boosted' : {
                         'mjj'   : [(10., 150.)], 
                         #'mlljj': [(200., 650.)] 
                         } 
                     }
    
    for flavour in ['LL', 'ElEl', 'MuMu']:
        
        for year, files_path in {
                                 #'2016': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_run2__ver10/results',
                                 #'2017': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_run2__ver10/results',
                                 #'2018': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_run2__ver10/results',
                                 
                                 #'2016-preVFP' : '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver35/results',
                                 #'2016-postVFP': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver35/results',
                                 #'2016': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver35/results',
                                 
                                 #'2017': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2017__ver29/results',
                                 #'2018': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2018__ver19/results',
                                 
                                 #'2016-preVFP' : '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver38/results',
                                 #'2016-postVFP': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver38/results',
                                 #'2016': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2016__ver38/results',
                                 
                                 #'2017': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2017__ver33/results',
                                 
                                 #'2018': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_2018__ver21/results',
                                 
                                 #'2016-preVFP' : '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__1/2016-preVFP/results',
                                 #'2016-postVFP': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__1/2016-postVFP/results',
                                 #'2016': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__1/2016/results',
                                 #'2017': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__1/2017/results',
                                 #'2018': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__1/2018/results',
                                 
                                 #'2016-preVFP' : '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__3/2016-preVFP/results',
                                 #'2016-postVFP': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__3/2016-postVFP/results',
                                 #'2016': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__3/2016/results',
                                 #'2018': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__3/2017/results',
                                 
                                 #'2018': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__3/2017/results',
                                 '2017': '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__7/2017/results',
                                 }.items():
   
            
            if not files_path:
                continue
            
            era = year.replace('20', '').replace('-','')
            jsf_nm = f"DYJetsTo{flavour}_TuneCP5_13TeV-amcatnloFXFX-pythia8_polyfitWeights_RunIISummer20UL{era}_NanoAODv9.json"
            
            scale_factor = getSF_dict(year, BinEdges)        
            
            with open(os.path.join(files_path.replace('/results',''), 'plots.yml')) as _f:
                plotConfig = yaml.load(_f, Loader=yaml.FullLoader)
            
            for deg in [2, 3, 4, 5, 6, 7, 8]:
                _sf = DYEstimation(plotConfig, files_path, flavour, year, nlowmass[year], deg, compareshape=False)
                
                for reg, wgt_per_mass in _sf.items():
                    for m, wgt_per_fit in wgt_per_mass.items():
                            for f_rng, f_param in wgt_per_fit.items():
                                
                                if reg == 'resolved' and f_rng =='low_mass':
                                    deg = nlowmass[year]
                                if 'binWgt' in f_rng: k = 'binWgt'
                                else: k = f'polyfit{deg}'
                                
                                scale_factor[year][reg][m][f_rng].update({f"{k}": f_param})
            
            #pp.pprint(scale_factor)
            with open(jsf_nm, 'w') as _f:
                b = json.dumps(scale_factor, indent=2, separators=(',', ':'), cls=CustomJSONEncoder)
                b = b.replace('"##<', "").replace('>##"', "")
                _f.write(b)
                print('Drell-Yan reweighting is saved in : ', jsf_nm)
