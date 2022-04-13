#! /bin/env python
import sys, os, os.path
import argparse
import glob
import yaml
import ROOT
ROOT.gROOT.SetBatch(True)
from ROOT import TCanvas, TPad, TLine

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


def getHistos(Cfg=None, path=None, prefix=None, lumi=None):
    _files = set()
    old_histos = {}
    new_histos = []
    smpScale   = {} 

    for i, filename in enumerate(glob.glob(os.path.join(path, '*.root'))):
        split_filename = filename.split('/')
        smp = str(split_filename[-1])
        if not smp.startswith(prefix):
            continue
        if 'minus_SingleTop_inHighMET' in smp:
            continue
        print(' adding ' , smp )
        if not prefix.startswith('MuonEG'):
            year   = Cfg['files'][smp]["era"]
            lumi   = Cfg["configuration"]["luminosity"][year]
            xsc    = Cfg['files'][smp]["cross-section"]
            genevt = Cfg['files'][smp]["generated-events"]
            print( lumi , xsc, genevt )
            sf =  lumi* xsc / (genevt) 
            smpScale[smp] = sf

        f = ROOT.TFile.Open(filename)
        _files.add(f)
        histos_fromSameFile = []
        for j, key in enumerate(f.GetListOfKeys()):
            cl = ROOT.gROOT.GetClass(key.GetClassName())
            if not cl.InheritsFrom("TH1"):
                continue
            histNm = key.ReadObj().GetName()
            key.ReadObj().SetDirectory(0)
            histos_fromSameFile.append(key.ReadObj())
            #histos_fromSameFile[j].SetDirectory(0)
            
        old_histos[smp]= histos_fromSameFile

        print ("Number of histograms processed for %s: " %prefix, len(old_histos[smp]))
    print ("Number of files processed for %s: " %prefix, len(old_histos))
    
    samples = list(old_histos.keys())
    for j in range(0, len(old_histos[samples[0]])):
        if "_vs_" in str(old_histos[samples[0]][j].GetName()):
            new_histo = cloneTH2(old_histos[samples[0]][j])
        else:
            new_histo = cloneTH1(old_histos[samples[0]][j])

        for i, (smp, histos) in enumerate(old_histos.items()):
            if "corrmet_pt" in histos[j].GetName() and "MuEl" in histos[j].GetName() and "HighMET" in histos[j].GetName():
                print (" histo name: ", histos[j].GetName(), "   # entries: ", histos[j].GetEntries())
            new_histo.Add(histos[j], 1)
            if not prefix.startswith('MuonEG'):
                new_histo.Scale(smpScale[smp])
            #else:
            #    new_histo.Scale(lumi)
            new_histo.SetDirectory(0)
        new_histos.append(new_histo)

    #for j in range(0, len(histos[0])):
    #    if "_vs_" in str(histos[0][j].GetName()):
    #        new_histo = cloneTH2(histos[0][j])
    #    else:
    #        new_histo = cloneTH1(histos[0][j])
    #    for i in range(0, len(histos)):
    #        if "corrmet_pt" in histos[i][j].GetName() and "MuEl" in histos[i][j].GetName() and "HighMET" in histos[i][j].GetName():
    #            print (" histo name: ", histos[i][j].GetName(), "   # entries: ", histos[i][j].GetEntries())
    #        new_histo.Add(histos[i][j], 1)
    #        if not prefix.startswith('MuonEG'):
    #            new_histo.Scale(smpScale[i])
    #        new_histo.SetDirectory(0)
    #    new_histos.append(new_histo)

    #for h in new_histos:
    #    if prefix.startswith('MuonEG'):
    #        h.Scale(lumi)
    #    else:
    #       h.Scale(smpScale[i])
    return new_histos



def get_HighMETttbarFromData(plotConfig, path, year, era, substract_ST):
    
    lumi = Constants.getLuminosity(year)
    #lumi = Constants.getLuminosityForEraForRun(year, era)
    
    histos_data      = getHistos(plotConfig, path, f"MuonEG_UL{year}", lumi)
    histos_SingleTop = getHistos(plotConfig, path, "ST_", lumi)

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
 
    if substract_ST: 
        for i in range(0, len(histos_data)):
            if "MuEl" in str(histos_data[i].GetName()) and "HighMET" in str(histos_data[i].GetName()):
                histos_data[i].Add(histos_SingleTop[i], -1)
                histos_data[i].SetDirectory(0)

    # Now histos_data has the same plots as normal data except for high met MuEl, which has the SingleTop subtracted
    # In PlotIt, these histograms will be normalized with the lumi. Since this is data,
    # we don't want any normalization by lumi. To avoid this, we "normalize" all the plots
    # by 1/lumi here.

    for i in range(0, len(histos_data)):
        for flavor in ['ElEl', 'MuMu']:
            if flavor in str(histos_data[i].GetName()) and "HighMET" in str(histos_data[i].GetName()):
                for j in range(0, len(histos_data)):
                    if str(histos_data[i].GetName()).replace(flavor, "MuEl") == str(histos_data[j].GetName()):
                        histos_data[i].Reset()
                        histos_data[i].Add(histos_data[j], 1)
                        histos_data[i].SetDirectory(0)
    
    for h in histos_data:
        h.Scale(1/lumi)
        name = h.GetName()
        h.SetName(name.replace("_clone", ""))
        h.SetDirectory(0)

    print( f"After SingleTop substraction :")    
    for h in histos_data:
        if not ("HighMET" in str(h.GetName()) and "corr" in str(h.GetName()) ):
            continue
        print( f"working on : {h.GetName()}")    
        print( f"- Integral from MuonEG data  - SingleTop mc  = {h.Integral()}")
    print( "======="*10)
    # Save the file that contains the regions at high met defined as dataElMu - SingleTop
    r_file = ROOT.TFile.Open(f"MuonEG_UL{year}{era}_minus_SingleTop_inHighMET.root", "recreate")
    for hist in histos_data:
        hist.Write()
    r_file.Close()


def get_ttbarFromData(plotConfig, path, year, era):
    
    k_factor_BTAG   = {'mumu': 1., 'elel': 1.}
    k_factor_NOBTAG = {'mumu': 1., 'elel': 1.}

    tagger = "DeepFlavour"
    wp = "M"

    lumi = Constants.getLuminosity(year) 
    #lumi = Constants.getLuminosityForEraForRun(year, era)

    histos_data      = getHistos(plotConfig, path, f"MuonEG_UL{year}", lumi)
    histos_SingleTop = getHistos(plotConfig, path, "ST", lumi)
    estimated_ttbar  = []

    if len(histos_data) != len(histos_SingleTop):
        print ("Something went wrong: different number of histograms in data and MC!")
    
    for h_data, h_ST in zip(histos_data, histos_SingleTop):
        print( f"Before SingleTop substraction :  {h_data.GetName()}")    
        print( f"- Integral from MuonEG data   :  {h_data.Integral()}")
        print( f"- Integral from SingleTop mc  :  {h_ST.Integral()}")
        print( '----------------------------------------------------------------------------------' )

    for i in range(0, len(histos_data)):
        if "MuEl" in str(histos_data[i].GetName()):
            histos_data[i].Add(histos_SingleTop[i], -1)
            histos_data[i].SetDirectory(0)


    for i in range(0, len(histos_data)):
        for flavor in ['ElEl', 'MuMu']:
            histNm = str(histos_data[i].GetName())
            if flavor in histNm and f"{tagger}{wp}" in histNm:
                if histos_data[i].Integral() != 0:
                    logger.error("the same-lepton category in data has non-zero entries")
                for j in range(0, len(histos_data)):
                    if str(histos_data[i].GetName()).replace(flavor, "MuEl") == str(histos_data[j].GetName()):
                        name = histos_data[i].GetName()
                        histos_data[i].Reset()
                        histos_data[i].Add(histos_data[j], 1)
                        histos_data[i].Scale(k_factor_BTAG[flavor.lower()])
                        histos_data[i].SetName(name.replace("_clone", ""))
                        histos_data[i].SetDirectory(0)
                        estimated_ttbar.append(histos_data[i])

            elif "MuEl" in histNm:
                name = histos_data[i].GetName()
                if "_vs_" in str(histos_data[i].GetName()):
                    temp = cloneTH2(histos_data[i])
                else:
                    temp = cloneTH1(histos_data[i])
                temp.Add(histos_data[i], 1)
                temp.SetName(name.replace("_clone", ""))
                temp.SetDirectory(0)
                estimated_ttbar.append(temp)
                del temp 
                #histos_data[i].Reset()
                #histos_data[i].Add(histos_data[i], 1)
                #histos_data[i].SetName(name.replace("_clone", ""))
                #histos_data[i].SetDirectory(0)
                #estimated_ttbar.append(histos_data[i]) 

    #print ("Number of new histograms (should coincide with the total number of histograms): ", len(estimated_ttbar))
    # In PlotIt, these histograms will be normalized with the lumi. Since this is data,
    # we don't want any normalization by lumi. To avoid this, we "normalize" all the plots
    # by 1/lumi here.
    for h in estimated_ttbar:
        h.Scale(1/lumi)
        h.SetDirectory(0)

    print( f"After SingleTop substraction :")    
    for h in estimated_ttbar:
        print( f"working on : {h_data.GetName()}")    
        print( f"- Integral from MuonEG data  - SingleTop mc  = {h.Integral()}")
    print( "======="*10)
 
    # Save the file that contains the ttbar estimation
    r_file = ROOT.TFile.Open("ttbar_from_data_final.root", "recreate")
    for hist in estimated_ttbar:
        hist.Write()
    r_file.Close()

if __name__ == "__main__":
    #path = '/nfs/scratch/fynu/asaggio/CMSSW_8_0_30/src/cp3_llbb/ZATools/factories_ZA/ttbarSplitting/slurm/output/'
    #path = '/nfs/scratch/fynu/asaggio/CMSSW_8_0_30/src/cp3_llbb/ZATools/factories_ZA/inverted_met_cut/slurm/output/'
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--year', help='To specifiy which year data taking', required=True)
    parser.add_argument('-i', '--inputs', help='To specifiy the path to the histograms ', required=True)
    parser.add_argument('--minusST', help='substract single top ', action='store_true', default=True)

    args = parser.parse_args()

    with open(os.path.join(args.inputs.replace('/results',''), 'plots.yml')) as _f:
        plotConfig = yaml.load(_f, Loader=yaml.FullLoader)
    
    eras = { '2016': [],
             '2017': ['BCDEF'], #'B','C','D', 'E', 'F'],
             '2018': [] }
    
    for era in eras[args.year] :
        get_HighMETttbarFromData(plotConfig, path= args.inputs, year= args.year, era=era, substract_ST= args.minusST)
        #get_ttbarFromData(plotConfig, path= args.inputs, year= args.year, era=eralurm_ba  kjaffel  R 3-01:27:16      1 mb-ivy211 

