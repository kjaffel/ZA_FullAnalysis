import os
import math
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

import matplotlib.pyplot as plt

from getmasspoints import YMLparser


def mass_to_str(m, _p2f=False):
    if _p2f: m = "%.2f"%m
    return str(m).replace('.','p')


def OverlapCheck(hist1, hist2):
    std1 = hist1.GetStdDev()
    std2 = hist2.GetStdDev()

    mean1 = hist1.GetMean()
    mean2 = hist2.GetMean()

    if not math.abs(mean2 - mean1) <= std1 +std2:
        # to get points in between asuming the reso is similair for both histo
        overlap_estimate = math.abs(std2 - std1 )/2.
        std_estimate  = math.abs(mean2 - mean1 )/2.
        steps = overlap_estimate /std_estimate
        

def get_Resolutions(inDir, thdm, flav, region, process, heavy, m_heavy, light, m_light, year):
    
    prefix = 'GluGluTo' if process == 'gg_fusion' else ''
    tb = '1p50' if process == 'gg_fusion' else '20p0'
    taggerWP= 'DeepFlavourM' if region=='resolved' else 'DeepCSVM'

    m0 = mass_to_str(m_heavy, _p2f=True)
    m1 = mass_to_str(m_light, _p2f=True)
    fNm = os.path.join(inDir, f"{prefix}{thdm}To2L2B_M{heavy}_{m0}_M{light}_{m1}_tb_{tb}_TuneCP5_13TeV_madgraph_pythia8_{year}.root")
    
    h_mbb   = f'{flav}_{region}_METCut_bJetER_bTagWgt_mbb_{taggerWP}_{process}'
    h_mllbb = f'{flav}_{region}_METCut_bJetER_bTagWgt_mllbb_{taggerWP}_{process}'
    
    dict_ = {}
    f = ROOT.TFile.Open(fNm, 'read')
    for m, hNm in {'mllbb': h_mllbb, 'mbb': h_mbb}.items():
        if not hNm in f.GetListOfKeys():
            raise RuntimeError(f"{hNm} Histogram doesnt exist in file : {fNm}!")
    
        hist = f.Get(hNm)
        if hist.GetSum() <= 0 :
            raise RuntimeError(f"{hNm} histogram is empty!")
        dict_[m] = { 'mean': hist.GetMean(), 'std': hist.GetStdDev()}
    return dict_


if __name__ == "__main__":

    path   = 'bjet_energy_regression_yes2/' 
    year   = 'UL17'
    inDir  = os.path.join(path, 'results' )
    thdm   = 'HToZA'
    region = 'resolved'
    heavy  = thdm[0]
    light  = thdm[-1]
    flav   = 'MuMu'
    
    for process, masses in YMLparser.get_masspoints(path, thdm).items(): 
        fig= plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111)
        for i, (m_heavy, m_light) in enumerate(masses):
            del masses[i]
            nearest = min(masses, key=lambda c: math.hypot(c[0]-m_heavy, c[1]-m_light))
            
            dict_ = get_Resolutions(inDir, thdm, flav, region, process, heavy, m_heavy, light, m_light, year)
            
            print( (m_heavy, m_light), nearest, dict_ )

            label1 = r'simulated. $H\rightarrow ZA$' if i ==0 else ''
            label2 = r'reconstructed. $ \mu \pm std. H\rightarrow ZA$' if i ==0 else ''
            
            plt.plot([m_light], [m_heavy], 'o', color='darkblue', label=label1)
            plt.errorbar([dict_['mbb']['mean']], [dict_['mllbb']['mean']], xerr=[dict_['mbb']['std']], yerr=[dict_['mllbb']['std']], capsize=3,  ecolor="k", fmt='.k', color='orange', label=label2)
    
        plt.xlim(0., 1000.)
        plt.ylim(0., 1050.)
        
        plt.xlabel(r'$M_{A} [GeV]$', fontsize=12)
        plt.ylabel(r'$M_{H} [GeV]$', fontsize=12)
        
        plt.title(r"2HDM typeII, run2 ULegacy pavement map for p-value scan")
        plt.legend(loc='best')
    
        plt.grid(zorder = 0, alpha = 0.3)
        
        plt.tight_layout()
        plt.savefig(f'ZAmap_forpvalue-scan_{process}.png')
        plt.gcf().clear()
