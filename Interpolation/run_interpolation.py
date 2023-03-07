import os, os.path, sys
import math
import json
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

import numpy as np
import tools as tools


def get_Histograms(inDir, thdm, heavy, light, m_heavy, m_light, flavor, reg, taggerWP, year):
    
    dict_ = {}
    scheme= '_bbH4F' if tb =='20p00' else ''
    fNm = os.path.join(inDir, f"{prefix}{thdm}To2L2B_M{heavy}_{tools.mass_to_str(m_heavy)}_M{light}_{tools.mass_to_str(m_light)}_tb_{tb}_TuneCP5{scheme}_13TeV_madgraph_pythia8_{year}.root")
    hNm = f'DNNOutput_{node}node_{flavor}_{reg}_{taggerWP}_METCut_{prod}_M{heavy}_{tools.mass_to_str(m_heavy)}_M{light}_{tools.mass_to_str(m_light)}'
    
    print(f'opening {fNm} ')
    f = ROOT.TFile.Open(fNm, 'read')
    
    for key in f.GetListOfKeys():
        if key.GetName().startswith(hNm): 
            hist = f.Get(key.GetName())
            
            if hist.GetSum() <= 0 :
                raise RuntimeError(f"{hNm} histogram is empty!")

            histo = ROOT.TH1F(hist.GetName()+'_clone',"", hist.GetNbinsX(), hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
            histo = hist
            histo.SetDirectory(0)
            dict_[hist.GetName()] = histo
    f.Close()
    return dict_


def runInterpolation(par_interlist, doTriangle=False, do2Param=False):

    for par_inter in par_interlist:

        m_heavy_inter = par_inter[0]
        m_light_inter = par_inter[1]
        idx = tools.get_idx_topave(do_fix, thdm) 
        
        #all_masses   = tools.YMLparser.get_masspoints(path, thdm)[prod]
        all_masses    = tools.no_plotsYML(inDir, thdm, year)[prod] # work around when I can't find the plots.yml
        
        if par_inter in all_masses:
            print( f'This mass you already have {par_inter}')
            continue

        pdfFile   = f'test_interp_DNN_{prod}_M{heavy}_{m_heavy_inter}_M{light}_{m_light_inter}_tb_{tb}_{year}.pdf'
        
        C = ROOT.TCanvas('C','C',800,800)
        C.Print(pdfFile+"[")

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
            nearest_params  = [] 
            # okay let's get 3 closet points
            # https://docs.python.org/3.8/library/math.html#math.hypot 
            for i in range(len(all_masses)):
                nearest = min(all_masses, key=lambda c: math.hypot(c[0]-m_heavy_inter, c[1]-m_light_inter))
                nearest_params.append(nearest)
                all_masses.remove(nearest) # rm and start over
            
            ## let's avoid running into extrapolation 
            params_less = []
            params_greater = []
            for p in nearest_params:
                if par_inter[idx] > p[idx]:
                    params_less.append(p)
                elif p[idx] > par_inter[idx]:
                    params_greater.append(p)
            
            if do2Param:
                par0, par1, par2 = nearest_params[0:3]
            else:
                if not params_less or len(params_greater) < 2:
                    print( 'no good points are found to allow interpolation for {par_inter}')
                    continue
                par0 = params_less[0]
                par1, par2 = params_greater[0:2]
        
        print ('\tClosest points are :')
        print (f' ... params 0 : {par0}')
        print (f' ... params 1 : {par1}')
        print (f' ... params 2 : {par2}')
        print (f' ... params to get : {par_inter}')
        #====================================================================== 
        all_histos_3 = {} 
        
        for reg, taggerWP in {'resolved': 'DeepFlavourM', 
                              'boosted' : 'DeepCSVM'}.items():

            if reg == 'boosted' or prod =='bb_associatedProduction': 
                flavors = ['OSSF'] 
            else: 
                flavors = ['ElEl', 'MuMu', 'OSSF']
            
            for flavor in flavors: 
                #================= Get your histograms from the root file ===========================
                histos = {}
                for i, (m_heavy, m_light) in enumerate([ par0, par1, par2]):
                    histos[i] = get_Histograms(inDir, thdm, heavy, light, m_heavy, m_light, flavor, reg, taggerWP, year) 
                
                sorted_histos = {}
                for i in np.arange(3):
                    for hist_nm, hist in histos[i].items():
                        if '__' in hist_nm:
                            syst = '__'+hist_nm.split('__')[-1]
                        else:
                            syst =''
                        if not syst in sorted_histos.keys():
                            sorted_histos[syst] = {}
                        sorted_histos[syst][i]=hist
                
                #================= and now interpolate =================================
                print (f'\tInterpolating : {prod}, {reg}, {flavor} for {year}')
                histName  = f'DNNOutput_ZAnode_{flavor}_{reg}_{taggerWP}_METCut_{prod}_M{heavy}_{tools.mass_to_str(m_heavy_inter)}_M{light}_{tools.mass_to_str(m_light_inter)}'
                histos[3] = {}

                for i , (syst, _histos) in enumerate(sorted_histos.items()):
                    if do2Param:
                        from twoparameter.interpolate import Interpolation
                        getNew_histo = Interpolation(par0, par1, par2, par_inter)
                        histos[3][f'{histName}{syst}']= getNew_histo(_histos[0], _histos[1], _histos[2], f'{histName}{syst}')
                    else:
                        from oneparameter.interpolate import Interpolation
                        if i == 0:
                            print( 'This class take first 2 histogram inputs')
                            print(f' ... params 2 : {par2} will be skipped !!')
                        getNew_histo = Interpolation(par0[idx], par1[idx], par_inter[idx])
                        histos[3][f'{histName}{syst}']= getNew_histo(_histos[0], _histos[1], f'{histName}{syst}') 
                
                all_histos_3.update(histos[3])
                print ('... done')
                #================= Plotting  =================================
                colors = [ ROOT.kRed+1, ROOT.kBlue+1, ROOT.kGreen+1, ROOT.kMagenta+1, ROOT.kOrange+1]
                 
                histosToPlot = {}
                for i in np.arange(3):
                    histosToPlot[i] = sorted_histos[''][i] # '' meaning nominal 
                histosToPlot[3] =  histos[3][f'{histName}']

                hmax = max([h.GetMaximum() for h in histosToPlot.values()])
                for i, h in histosToPlot.items():
                    
                    #if h.Integral() !=0.:
                    #    h.Scale(1./h.Integral()) # scale to 1.
                    #    h.Sumw2()
                    #    h.SetDirectory(0)
                    
                    h.SetLineColor(colors[i])
                    h.SetLineWidth(2)
                    if i == '3':
                        h.SetLineStyle(2)
                    print(f'\th{i} integral is: {h.Integral()}')
                
                leg = ROOT.TLegend(0.2,0.89,0.6,0.62)
                leg.SetTextSize(0.025)
                leg.SetBorderSize(0)
                
                histosToPlot[0].SetTitle(f'Cat. {prod}, {reg}, {flavor}')
                histosToPlot[0].Draw('hist')
                histosToPlot[0].GetYaxis().SetRangeUser(1,hmax)
                histosToPlot[0].SetStats(False)
                histosToPlot[0].GetYaxis().SetTitle("Events")
                histosToPlot[0].GetXaxis().SetTitle(f"DNN_Output {node}")
                histosToPlot[0].GetXaxis().SetTitleOffset(1.5)
                histosToPlot[0].GetYaxis().SetTitleOffset(1.5)

                t = C.GetTopMargin()
                r = C.GetRightMargin()
                l = C.GetLeftMargin()
                lumiTextOffset   = 0.2

                latex = ROOT.TLatex()
                latex.SetNDC()
                latex.SetTextAngle(0)
                latex.SetTextColor(ROOT.kBlack)

                lumiText = "%s fb-1 (13 TeV)" %format(tools.get_lumi(year)/1000.,'.2f')
                lumi_txt = latex.DrawLatex(0.65,1-t+lumiTextOffset*t,lumiText)
                lumi_txt.SetNDC()
                lumi_txt.SetTextFont(40)
                lumi_txt.SetTextSize(0.03)
                lumi_txt.Draw("same")

                cms_txt = latex.DrawLatex(0.1, 1-t+lumiTextOffset*t, "CMS Preliminary")
                cms_txt.SetNDC()
                cms_txt.SetTextFont(40)
                cms_txt.SetTextSize(0.03)
                cms_txt.Draw("same")

                for i, (h, params) in enumerate(zip(histosToPlot.values(), [ par0, par1, par2, par_inter])):
                   
                    if i >= 1: 
                        h.Draw('hist same')

                    if any( p == par_inter for p in [ par0, par1, par2] ):
                        nbr = 'original' 
                    
                    if i == 3: nbr = 'interpolated' 
                    else: nbr = i
                    
                    leg.SetTextAlign(12)
                    leg.AddEntry(h, 'h_{%s} (m_{%s}, m_{%s})= %s GeV'%(nbr, heavy, light, params))
                leg.Draw()
                C.SetLogy()
                C.Print (pdfFile)
        C.Print (pdfFile+"]")
        C.Clear()
        
        rootInter = os.path.join(outDir, f"{prefix}{thdm}To2L2B_M{heavy}_{m_heavy_inter}_M{light}_{m_light_inter}_tb_{tb}_TuneCP5_13TeV_madgraph_pythia8_{year}.root")
        outFile   = ROOT.TFile(rootInter,"RECREATE")
        for hist_Nm, hist in all_histos_3.items():
            hist.GetYaxis().SetTitle("Events")
            hist.GetXaxis().SetTitle(f"DNN_Output {node}")
            hist.SetName(hist_Nm)
            hist.Write()
        outFile.Close() 

    
if __name__ == "__main__":
    """
    do2Param : if set to 'True' will use mH and mA in the interpolation 
               if set to 'False' 'do_fix' assigned below will remain the same and the other mass will change
    doTriangle : if set to 'True' will try to get 3 tuples params that form a triangle, 
                 if you leave this one out ( .i.e. 'False' flag) the code will just get 3 closest points without enforcing the geometric shape of the triangle
    """

    thdm    = 'HToZA'                # or AToZH
    year    = 'UL18'                 # or UL17, UL18, UL16-preVFP, UL16-postVFP
    do_fix  = 'mH'                   # or mA
    #path   = 'ul2017__ver1'
    #path   = 'ul_run2__ver8'
    #path   = 'ul_run2__ver12'
    #path   = 'ul_run2__ver15'
    path    = 'ul_run2__ver19'
    inDir   = os.path.join(path, 'results' )
    outDir  = os.path.join(inDir, 'interpolated2')
    
    if not os.path.isdir(outDir):
        os.makedirs(outDir)
    
    heavy = thdm[0]
    light = thdm[-1]
    node  = f'Z{light}'
    
    # Opening JSON file
    f = open('pavement_for_pvalue_0p2_0p2.json')
    par_interlist = json.load(f)
    
    # Put what you want to interpolate in format --> (mH, mA) or (mA, mH) in case  thdm='AToZH' 
    #par_interlist=[(250,100), (300,50),(300,200),(500,200),(510,130),(650,50),(800,50),(800,100),(800,200)]
    par_interlist=[(609.21, 50.), (609.21, 450.), (500., 150.), (500., 350.)]
    
    for prefix, prod in {'GluGluTo': 'gg_fusion', 
                         '': 'bb_associatedProduction'
                         }.items():
        
        if prod =='gg_fusion': tb = '1p50' 
        else: tb = '20p00'
        
        runInterpolation(par_interlist, doTriangle=False, do2Param=False)
