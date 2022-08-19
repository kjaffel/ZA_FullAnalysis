import os
import json
import math
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

import matplotlib.pyplot as plt

import tools as tools



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

    m0 = tools.mass_to_str(m_heavy, _p2f=True)
    m1 = tools.mass_to_str(m_light, _p2f=True)
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


def Radar(data):
    points = []
    mA_min = 30
    mA = mA_min
    mH = 125
    mZ = 91.1876
    sigmaY = 0.2 # assumed resolution on mllbb
    sigmaX = 0.2 # assumed resolution on mbb 
    step_x = 0.2 
    step_y = 0.2

    while mH < 1000:
        while mA <= (mH-mZ):
            if not (mH,mA) in data:
                points.append((round(mH,2), round(mA,2)))
            mA = mA*(1+sigmaX*step_x) 
        mH = mH*(1+sigmaY*step_y) 
        mA = mA_min 

    # Save points
    str_stepx = str(round(step_x, 2))
    str_stepx = str_stepx.replace('.', 'p')
    str_stepy = str(round(step_y, 2))
    str_stepy = str_stepy.replace('.', 'p')
   
    f2 = open('pavement_for_pvalue_{0}_{1}.json'.format(str_stepx, str_stepy),'w')
    json.dump(points,f2)
    f2.close()
    return points


if __name__ == "__main__":

    #path  = 'bjet_energy_regression_yes2/' 
    path   = 'ul_run2__ver19' 
    year   = 'UL18'
    inDir  = os.path.join(path, 'results' )
    thdm   = 'HToZA'
    region = 'resolved'
    heavy  = thdm[0]
    light  = thdm[-1]
    flav   = 'MuMu'
    
    #all_masses   = tools.YMLparser.get_masspoints(path, thdm)
    all_masses    = tools.no_plotsYML(thdm)
    print( all_masses)
    extra_points = Radar(all_masses)
    exit()

    for process, masses in all_masses.items(): 
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
