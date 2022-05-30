import os, os.path, sys
import math 
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

import numpy as np
import tools as tools


def get_Histograms(inDir, thdm, heavy, m_heavy, light, m_light, year):
    m0 = tools.mass_to_str(m_heavy, _p2f=True) # these are nasty format, sorry I will them in the new production 
    m1 = tools.mass_to_str(m_light, _p2f=True)
    
    fNm = os.path.join(inDir, f"GluGluTo{thdm}To2L2B_M{heavy}_{m0}_M{light}_{m1}_tb_1p50_TuneCP5_13TeV_madgraph_pythia8_{year}.root")
    hNm = f'DNNOutput_ZAnode_{flavor}_{reg}_{taggerWP}_METCut_{prod}_M{heavy}_{tools.mass_to_str(m_heavy)}_M{light}_{tools.mass_to_str(m_light)}'
    
    f = ROOT.TFile.Open(fNm, 'read')
    if not hNm in f.GetListOfKeys():
        raise RuntimeError(f"{hNm} Histogram doesnt exist in file : {fNm}!")
    
    hist = f.Get(hNm)
    if hist.GetSum() <= 0 :
        raise RuntimeError(f"{hNm} histogram is empty!")

    histo = ROOT.TH1F(hist.GetName(),"", hist.GetNbinsX(), hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    histo.Sumw2()
    histo.SetDirectory(0)

    #print(f'opening {fNm} , looking for {hNm}')
    print( 'working on :: ', hist.GetSum(), m_heavy, m_light , histo)
    f.Close()
    return histo


def runInterpolation(par_interlist, doTriangle=False, do2Param=False):

    for par_inter in par_interlist:
        if doTriangle:
            # Find three points in triangle #
            print ('\tLooking for triangle')
            name = f'finder/test_{par_inter[0]}_{par_inter[1]}.png'
        
            finder  = PointFinder(list(HToZA),verbose=False)
            triplet = finder.find_triangle(par_inter)
            finder.draw(name)
            print ('... done')
        
            par0 = tuple(triplet[0])
            par1 = tuple(triplet[1])
            par2 = tuple(triplet[2])
            print ('\tTriangle edge points are :')
        else:
            m_heavy = par_inter[0]
            m_light = par_inter[1]
            params  = [] 
            
            # okay let's get 3 closet points
            for i in np.arange(3):
                nearest = min(all_masses, key=lambda c: math.hypot(c[0]-m_heavy, c[1]-m_light))
                params.append(nearest)
                all_masses.remove(nearest) # rm and start over
            par0, par1, par2 = [p for p in params]
            print ('\tClosest points are :')

        print (f' ... params 0 : {par0}')
        print (f' ... params 1 : {par1}')
        print (f' ... params 2 : {par2}')
        print (f' ... params to get : {par_inter}')
        
        #================= Get your histograms from the root file ===========================
        histos = {}
        for i, (m_heavy, m_light) in enumerate([ par0, par1, par2]):#, par_inter]):
            histos[i] = get_Histograms(inDir, thdm, heavy, m_heavy, light, m_light, year) 
        
        #================= and now interpolate =================================
        print ('\tInterpolating')
        
        if do2Param:
            from twoparameter.interpolate import Interpolation
            getNew_histo = Interpolation(par0, par1, par2, par_inter)
            histos[3]    = getNew_histo(histos[0], histos[1], histos[2], "h3")
        else:
            from oneparameter.interpolate import Interpolation
            idx = tools.get_idx_topave(do_fix, thdm) 
            getNew_histo = Interpolation(par0[idx], par1[idx], par_inter[idx])
            histos[3]    = getNew_histo(histos[0], histos[1], "h3")
        
        print ('... done')
        
        #================= Plotting  =================================
        colors = [ ROOT.kRed+1, ROOT.kBlue+1, ROOT.kGreen+1, ROOT.kMagenta+1, ROOT.kOrange+1]
        
        pdfName = f'test_interp_DNN_{par_inter[0]}_{par_inter[1]}.pdf'
        C = ROOT.TCanvas('C','C',800,800)
        C.Print (pdfName+"[")
        C.SetLogy()
        
        C.Clear()
        
        hmax = max([h.GetMaximum() for h in histos.values()])
        for i, h in histos.items():
            
            if h.Integral() !=0.:
                h.Scale(1./h.Integral()) # scale to 1.
                h.Sumw2()
                h.SetDirectory(0)
            
            h.SetLineColor(colors[i])
            h.SetLineWidth(2)
            if i == '3':
                h.SetLineStyle(2)
            print(f'\th{i} integral is: {h.Integral()}')
        
        leg = ROOT.TLegend(0.2,0.89,0.6,0.62)
        leg.SetTextSize(0.025)
        leg.SetBorderSize(0)
        
        histos[0].Draw('hist')
        histos[0].GetYaxis().SetRangeUser(1,hmax)
        histos[0].SetStats(False)
        
        for i, (h, params) in enumerate(zip(histos.values(), [ par0, par1, par2, par_inter])):
            if i >= 1: h.Draw('hist same')
            nbr = 'original' if i == 2 else ('interpolated' if i == 3  else (i))
            leg.SetTextAlign(12)
            leg.AddEntry(h, f"h_{nbr} {params} GeV")
        leg.Draw()
        
        C.Print (pdfName)
        C.Print (pdfName+"]")
    

    
if __name__ == "__main__":
    """
    do2Param : use mH and mA in the interpolation if you leave it out 'do_fix' assigned above will remain the same and the other mass will change
    doTriangle : will try to get 3 tuples params that form a triangle, if you leave this one out, it will just get 3 closest points
    """

    thdm    = 'HToZA'                # or AToZH
    prod    = 'gg_fusion'            # or bb_associatedProduction
    taggerWP= 'DeepFlavourM'         # or DeepCSVM 
    reg     = 'resolved'             # or boosted
    flavor  = 'MuMu'                 # or ElEl , OSSF
    year    = 'UL17'                 # or UL17, UL18
    do_fix  = 'mH'
    #path   = 'ul2017__ver1'
    #path   = 'ul_run2__ver8'
    path    = 'ul_run2__ver12'
    inDir   = os.path.join(path, 'results' )
    
    heavy = thdm[0]
    light = thdm[-1]
    
    all_masses    = tools.YMLparser.get_masspoints(path, thdm)[prod]
    print( all_masses )
    
    # Put what you want to interpolate in format --> (mH, mA) or (mA, mH) in case  thdm='AToZH' 
    #par_interlist=[(250,100), (300,50),(300,200),(500,200),(510,130),(650,50),(800,50),(800,100),(800,200)]
    par_interlist =[(300.0, 100.0) ]
    
    runInterpolation(par_interlist, doTriangle=False, do2Param=True)
