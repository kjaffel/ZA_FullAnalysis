#! /bin/env python
import sys, os, os.path
import argparse
import glob
import yaml
import ROOT
from ROOT import TCanvas, TPad, TLine
ROOT.gROOT.SetBatch(True)

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/')
import Constants as Constants

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/')
import HistogramTools as HT
import utils as utils
logger = utils.ZAlogger(__name__)


def cloneTH1(hist):
    if (hist == None):
        return None
    cloneHist = ROOT.TH1F(str(hist.GetName()) + "_clone", hist.GetTitle(), hist.GetNbinsX(), hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    return cloneHist


def cloneTH2(hist):
    if (hist == None):
        return None
    cloneHist = ROOT.TH2F(str(hist.GetName()) + "_clone", hist.GetTitle(), hist.GetNbinsX(), hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax(), hist.GetNbinsY(), hist.GetYaxis().GetXmin(), hist.GetYaxis().GetXmax()) 
    return cloneHist


def getHistos(Cfg, path, prefix, lumi, isMC=False):
    old_histos = {}
    new_histos = []
    smpScale   = {} 

    isSignal = True if "type" in Cfg.keys() and Cfg["type"]=="signal" else (False) 
    data_ = ['DoubleMuon', 'DoubleEG', 'MuonEG', 'SingleMuon', 'SingleElectron', 'EGamma']
    
    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        split_filename = filename.split('/')
        smp = str(split_filename[-1])
        # ignore skeleton
        if smp.startswith('__skeleton__'):
            continue
        # ignore created root files for this study
        if 'minus_SingleTop_inHighMET' in smp:
            continue
        
        # ignore signal 
        if isSignal:
            continue
        
        if isMC:
            if prefix == 'all_mc_nonttbar':
                if smp.startswith('TT') or any(x in smp for x in data_):
                    continue
            else:
                if not smp.startswith(prefix):
                    continue
        else: # take all data group 
            if not any(x in smp for x in data_):
                continue

        print(' adding ' , smp )
        
        year   = Cfg['files'][smp]["era"]
        lumi   = Cfg["configuration"]["luminosity"][year]
        if isMC:
            xsc    = Cfg['files'][smp]["cross-section"]
            genevt = Cfg['files'][smp]["generated-events"]
            print( lumi , xsc, genevt )
            sf =  lumi* xsc / (genevt) 
            smpScale[smp] = sf

        f = ROOT.TFile.Open(filename)
        histos_fromSameFile = []
        for j, key in enumerate(f.GetListOfKeys()):
            cl = ROOT.gROOT.GetClass(key.GetClassName())
            if not cl.InheritsFrom("TH1"):
                continue
            
            histoNm = key.ReadObj().GetName()
            histo   = key.ReadObj()
            histo.SetDirectory(0)
            if isMC:
                histo.Scale(sf)
            histos_fromSameFile.append(histo)
            
        old_histos[smp]= histos_fromSameFile

        #print ("Number of histograms processed for %s: " %prefix, len(old_histos[smp]))
    #print ("Number of files processed for %s: " %prefix, len(old_histos))
    print (smpScale )

    samples = list(old_histos.keys())
    for j in range(0, len(old_histos[samples[0]])):
        
        if "_vs_" in str(old_histos[samples[0]][j].GetName()):
            new_histo = cloneTH2(old_histos[samples[0]][j])
        else:
            new_histo = cloneTH1(old_histos[samples[0]][j])

        for i, (smp, histos) in enumerate(old_histos.items()):
            #if "corrmet_pt" in histos[j].GetName() and "MuEl" in histos[j].GetName() and "HighMET" in histos[j].GetName():
            #    print (" histo name: ", histos[j].GetName(), "   # entries: ", histos[j].GetEntries())
            new_histo.Add(histos[j], 1)
            new_histo.SetDirectory(0)
        
        new_histos.append(new_histo)

    return new_histos


def get_kFactors(plotConfig, path, lumi, year, rf):
    
    histos_data      = getHistos(plotConfig, path, f"MuonEG_UL{year}", lumi, isMC=False)
    histos_others    = getHistos(plotConfig, path, "all_mc_nonttbar", lumi, isMC=True)
    
    k_factors = {'ElEl': {}, 'MuMu': {}}
    print( rf )
    inFile    = HT.openFileAndGet(rf)
    for i in range(0, len(histos_data)):
        for flavor in ['ElEl', 'MuMu']:
            hist_dNm = histos_data[i].GetName().replace("_clone", "")
            hist_oNm = histos_others[i].GetName().replace("_clone", "")
            if not flavor in hist_dNm:
                continue
            if not "HighMET" in hist_dNm:
                continue
            if not 'corrmet_pt_' in hist_dNm:
                continue
            
            process = hist_dNm.split('HighMET_')[-1] 
            region  = 'resolved' if 'resolved' in hist_dNm else 'boosted'
            k_factors[flavor].update({process :{} })
            
            if hist_dNm == hist_oNm:
                #histos_data[i].Reset()
                histos_data[i].Add(histos_others[i], -1)
                histos_data[i].Scale(1./lumi)
                histos_data[i].SetDirectory(0)
            
            for  k in inFile.GetListOfKeys():
                histNm = k.GetName()
                if not histNm == hist_dNm: 
                    continue

                hist = inFile.Get(histNm)
                print( ' working on ::', histNm , histos_data[i].Integral(), hist.Integral() )
                print( ' k_factor   ::', histos_data[i].Integral()/hist.Integral())
                k_factors[flavor][process].update({region : histos_data[i].Integral()/ hist.Integral()})
    return k_factors 


def get_HighMETttbarFromData(plotConfig, path, year, era, substractST):
    
    lumi  = Constants.getLuminosity(year)
    #lumi = Constants.getLuminosityForEraForRun(year, era)
    
    histos_data      = getHistos(plotConfig, path, f"MuonEG_UL{year}", lumi, isMC=False)
    histos_SingleTop = getHistos(plotConfig, path, "ST_", lumi, isMC=True)

    if len(histos_data) != len(histos_SingleTop):
        print ("Something went wrong: different number of histograms in data and MC!")
    

    print( f"Before SingleTop substraction : ")    
    for h_data, h_ST in zip(histos_data, histos_SingleTop):
        if not "HighMET" in str(h_data.GetName()):
            continue
        print( f"working on : {h_data.GetName()}")    
        print( f"- Integral from MuonEG data  :  {h_data.Integral()}")
        print( f"- Integral from SingleTop mc :  {h_ST.Integral()}")
        print( '----------------------------------------------------------' )
 
    if substractST: 
        for i in range(0, len(histos_data)):
            if "MuEl" in str(histos_data[i].GetName()) and "HighMET" in str(histos_data[i].GetName()):
                #histos_data[i].Reset()
                histos_data[i].Add(histos_SingleTop[i], -1)
                histos_data[i].SetDirectory(0)


    for i in range(0, len(histos_data)):
        for flavor in ['ElEl', 'MuMu']:
            if flavor in str(histos_data[i].GetName()) and "HighMET" in str(histos_data[i].GetName()):
                for j in range(0, len(histos_data)):
                    if str(histos_data[i].GetName()).replace(flavor, "MuEl") == str(histos_data[j].GetName()):
                        histos_data[i].Reset()
                        histos_data[i].Add(histos_data[j], 1)
                        histos_data[i].SetDirectory(0)
    
    # Now histos_data has the same plots as normal data except for high met MuEl, which has the SingleTop subtracted
    # In PlotIt, these histograms will be normalized with the lumi. Since this is file will replace ttbar mc,
    # we don't want any normalization by lumi. To avoid this, we "normalize" all the plots
    # by 1/lumi here.
    for h in histos_data:
        name = h.GetName()
        h.SetName(name.replace("_clone", ""))
        h.Scale(1./lumi)
        h.SetDirectory(0)

    print( f"After SingleTop substraction :")    
    for h in histos_data:
        if not ("HighMET" in str(h.GetName()) and "corrmet" in str(h.GetName()) ):
            continue
        print( f"working on : {h.GetName()}")    
        print( f"- Integral from MuonEG data  - SingleTop mc  = {h.Integral()}")
    print( "======="*10)
    
    # Save the file that contains the regions at high met defined as dataElMu - SingleTop
    rf_nm  = f"{path}/MuonEG_UL{year}{era}_minus_SingleTop_inHighMET.root"
    r_file = ROOT.TFile.Open(rf_nm, "recreate")
    for hist in histos_data:
        hist.Write()
    r_file.Close()


def get_ttbarFromData(plotConfig, path, year, era):
    
    rf_nm  = f"{path}/MuonEG_UL{year}{era}_minus_SingleTop_inHighMET.root"
    lumi   = Constants.getLuminosity(year) 
    #lumi  = Constants.getLuminosityForEraForRun(year, era)
    
    k_factor_BTAG   = get_kFactors(plotConfig, path, lumi, year, rf_nm)
    k_factor_NOBTAG = {'mumu': 1., 'elel': 1.}
    
    tagger = "DeepFlavour"
    wp = "M"

    histos_data      = getHistos(plotConfig, path, f"MuonEG_UL{year}", lumi, isMC=False)
    histos_SingleTop = getHistos(plotConfig, path, "ST", lumi, isMC=True)
    histos_others    = getHistos(plotConfig, path, "all_mc_nonttbar", lumi, isMC=True)

    if len(histos_data) != len(histos_SingleTop):
        print ("Something went wrong: different number of histograms in data and MC!")
    
    print( f"Before SingleTop substraction : ")    
    for h_data, h_ST in zip(histos_data, histos_SingleTop):
        if not "HighMET" in str(h_data.GetName()):
            continue
        print( f"working on : {h_data.GetName()}")    
        print( f"- Integral from MuonEG data  :  {h_data.Integral()}")
        print( f"- Integral from SingleTop mc :  {h_ST.Integral()}")
        print( '----------------------------------------------------------' )

    for i in range(0, len(histos_data)):
        if "MuEl" in str(histos_data[i].GetName()):
            histos_data[i].Add(histos_SingleTop[i], -1)
            histos_data[i].SetDirectory(0)


    for i in range(0, len(histos_data)):
        histNm = histos_data[i].GetName()
        for flavor in ['ElEl', 'MuMu', 'MuEl']:
            if flavor in ['ElEl', 'MuMu']:
                if flavor in histNm and f"{tagger}{wp}" in histNm and 'resolved' in histNm:
                    for j in range(0, len(histos_data)):
                        if histNm.replace(flavor, "MuEl") == str(histos_data[j].GetName()):
                            name    = histNm.replace("_clone", "")
                            region  = 'resolved' if 'resolved' in name else 'boosted'
                            process = 'gg_fusion' if 'gg_fusion' in name else 'bb_associatedProduction'
                            histos_data[i].Reset()
                            histos_data[j].Scale(k_factor_BTAG[flavor][process][region])
                            histos_data[i].Add(histos_data[j], 1)
                            histos_data[i].SetDirectory(0)
    # In PlotIt, these histograms will be normalized with the lumi. Since this is mc,
    # we don't want any normalization by lumi. To avoid this, we "normalize" all the plots
    # by 1/lumi here.
    for h in histos_data:
        name = h.GetName()
        h.SetName(name.replace("_clone", ""))
        h.Scale(1/lumi)
        h.SetDirectory(0)
    
    print( f"After SingleTop substraction :")    
    for h in histos_data:
        if not ("HighMET" in str(h.GetName()) and "corrmet" in str(h.GetName()) ):
            continue
        print( f"working on : {h.GetName()}")    
        print( f"- Integral from MuonEG data  - SingleTop mc  = {h.Integral()}")
    print( "======="*10)

    # Save the file that contains the ttbar estimation
    r_file = ROOT.TFile.Open(f"{path}/TTbar_FromMuonEGData_UL{year}{era}_minus_SingleTop_inHighMET.root", "recreate")
    for hist in histos_data:
        hist.Write()
    r_file.Close()


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', help='To specifiy which year data taking', required=True)
    parser.add_argument('-i', '--inputs', help='To specifiy the path to the histograms ', required=True)
    parser.add_argument('--minusST', help='substract minor backgrounds', action='store_true', default=True)

    args = parser.parse_args()

    with open(os.path.join(args.inputs.replace('/results',''), 'plots.yml')) as _f:
        plotConfig = yaml.load(_f, Loader=yaml.FullLoader)
    
    eras = { '2016': [],
             '2017': ['BCDEF'], #'B','C','D', 'E', 'F'],
             '2018': [] }
    
    for era in eras[args.year] :
        get_HighMETttbarFromData(plotConfig, path= args.inputs, year= args.year, era= era, substractST= args.minusST)
        get_ttbarFromData(plotConfig, path= args.inputs, year= args.year, era=era)
