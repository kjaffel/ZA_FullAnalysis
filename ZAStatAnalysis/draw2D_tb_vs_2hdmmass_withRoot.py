import os, os.path , sys
import argparse
import math
import yaml
import json
import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
from collections import OrderedDict
import numpy as np

import Constants as Constants

logger = Constants.ZAlogger(__name__)



def get_branchingratio_crosssection(dict_, m_heavy, m_light, mode, process, tb):
    br_Ztoll = 0.067264
    heavy    = mode[0]
    light    = mode[-1]
    key      = 'M{}_{}_M{}_{}_tb_{}'.format(heavy, float(m_heavy), light, float(m_light), tb)
    
    if not key in dict_[mode] or not dict_[mode][key]:
        return None, None, None
    
    br_HeavytoZlight = dict_[mode][key]['branching-ratio']['{}ToZ{}'.format(heavy, light)]
    br_lighttobb     = dict_[mode][key]['branching-ratio']['{}Tobb'.format(light)]
    
    if process == 'gg{}'.format(heavy):
        xsc      = dict_[mode][key]['cross-section'][process].split()[0]
        xsc_err  = dict_[mode][key]['cross-section'][process].split()[2]
    else:
        xsc      = dict_[mode][key]['cross-section'][process]['NLO'].split()[0]
        xsc_err  = dict_[mode][key]['cross-section'][process]['NLO'].split()[2]
    
    if br_HeavytoZlight is None or br_lighttobb is None: br = None
    else: br = float(br_HeavytoZlight) * br_Ztoll* float(br_lighttobb)
    
    return float(xsc), float(xsc_err), br


def get_generated_masses(jsf, m):
    m_to_pave =[]
    with open(jsf) as f_:
        limits = yaml.safe_load(f_)
    
    for l in limits:
        for i in range(2):
            j = 1 if i ==0 else 0
            if l['parameters'][i] == str(m):
                m_to_pave.append(float(l['parameters'][j]))
    return m_to_pave



parser = argparse.ArgumentParser(description='Draw 2D tb vs mass')
parser.add_argument('-p', '--jsonpath', action='store', type=str, required=True,
                help='JSON file containing the limits for all the points (Combined channel)')
parser.add_argument('--unblind', action='store_true', dest='unblind', help='If set, draw also observed upper limits')
parser.add_argument('--era', type=str, required=True, help='data taking of the given limits')
parser.add_argument('--interpolate', action='store_true', default=True, help='')
parser.add_argument('--mirror', action='store_true', default=True, help='')
parser.add_argument('--_2POIs_r', action='store_true', dest='_2POIs_r', required=False, default=True,
            help='This will merge both signal in 1 histogeram and normalise accoridngly, tanbeta will be required')
parser.add_argument('--tanbeta', action='store', type=float, default=None, required=False, help='')
parser.add_argument('--expectSignal', action='store', required=False, type=int, default=1, choices=[0, 1],
            help=' Is this S+B or B-Only fit? ')
parser.add_argument('-r', '--rescale-to-za-br', action='store_true', dest='rescale_to_za_br',
            help='If flagged True, limits in HToZA mode will be x to BR( Z -> ll) x BR(A -> bb ) x (H -> ZA)')
parser.add_argument('--fix', type=str, choices=['mH', 'mA'], required=True, help='2hdm mass to fix ')
parser.add_argument('--mass', type=float, required=True, help='to which value the above mass need to be fixed ?')


options = parser.parse_args()

if options.fix == 'mH': 
    pave        = 'mA'
    idx_mtofix  = 0
    idx_mtopave = 1
else: 
    pave        = 'mH'
    idx_mtofix  = 1
    idx_mtopave = 0 


mirror = False      # options.mirror
Interpolate = True  # options.interpolate

opt = ''
if mirror:
    opt += 'mirror'
if Interpolate:
    opt += '_interpolate'

poi_dir, tb_dir, cl = Constants.locate_outputs("asymptotic", options._2POIs_r, options.tanbeta, options.expectSignal)

jsonpath   = os.path.join(options.jsonpath, poi_dir, tb_dir)
plot_dir   = os.path.join(jsonpath, '2D_tb.vs.2hdm_masses')
if not os.path.isdir(plot_dir):
        os.makedirs(plot_dir)

color = ROOT.kLake
plots = [
    'theory',
    'expected_over_theory',
    #'expected', 
    ]

catagories = OrderedDict({
   # 'ggH_nb2_resolved'        : [['MuMu_ElEl_MuEl'],    'ggH', '$nb2$-',        'resolved'],
   # 'ggH_nb2_boosted'         : [['OSSF_MuEl'],         'ggH', '$nb2$-',        'boosted' ],
   # 'ggH_nb3_resolved'        : [['MuMu_ElEl_MuEl'],    'ggH', '$nb3$-',        'resolved'],
   # 'ggH_nb3_boosted'         : [['OSSF_MuEl'],         'ggH', '$nb3$-',        'boosted' ],
   # 'ggH_nb2PLusnb3_resolved'  : [['OSSF', 'OSSF_MuEl'], 'ggH', 'nb2+nb3, ',     'resolved'],
   # 'ggH_nb2PLusnb3_boosted'   : [['OSSF', 'OSSF_MuEl'], 'ggH', 'nb2+nb3, ',     'boosted' ],             
    
   # 'bbH_nb2_resolved'        : [['OSSF_MuEl'],         'bbH', '$nb2$-',        'resolved'],
   # 'bbH_nb2_boosted'         : [['OSSF_MuEl'],         'bbH', '$nb2$-',        'boosted' ],
   # 'bbH_nb3_resolved'        : [['OSSF_MuEl'],         'bbH', '$nb3$-',        'resolved'],
   # 'bbH_nb3_boosted'         : [['OSSF_MuEl'],         'bbH', '$nb3$-',        'boosted' ],
   # 'bbH_nb2PLusnb3_resolved'  : [['OSSF', 'OSSF_MuEl'], 'bbH', 'nb2+nb3, ',     'resolved'],             
   # 'bbH_nb2PLusnb3_boosted'   : [['OSSF', 'OSSF_MuEl'], 'bbH', 'nb2+nb3, ',     'boosted' ],   
    
    # combination 1 reso +boo  
    'ggH_nb2PLusnb3_resolved_boosted': [['OSSF', 'OSSF_MuEl'], 'ggH', 'nb2+nb3, ', 'resolved + boosted'],
    #'bbH_nb2PLusnb3_resolved_boosted': [['OSSF', 'OSSF_MuEl'], 'bbH', 'nb2+nb3, ', 'resolved + boosted'],
    })


th_ymlF   = 'data/2hdmc1.8.0-br_cba-0.01_mAorH-{}_2hdm-type2.yml'.format(options.mass)
if not os.path.isfile(th_ymlF):
    logger.error('{} not found cannot proceed ... make sure to run sushi and 2hdmc first '.format(th_ymlF))
    exit()
logger.info('Opening theory file : {}'.format(th_ymlF))
with open(th_ymlF) as f:
    theory = yaml.load(f)


for plot in plots:
    
    if plot == 'theory':
        for p in ["gg_fusion", "bb_associated_production"]:
        
            if p== "gg_fusion":
                Extra  = [ 50., 100., 200., 250., 300., 400., 450., 1000.]
                Extra += [ 55.16, 566.51, 160.17, 87.1, 298.97, 186.51, 118.11, 137.54, 40.68, 47.37, 779.83, 350.77, 664.66, 74.8, 34.93, 254.82, 101.43, 217.19, 482.85, 411.54, 64.24, 30.0]
                masses_to_pave = sorted(Extra + np.arange(10., 1000., 50.).tolist())
            else:
                Extra = [ 200., 50., 400., 300., 100., 1000., 55.16, 566.51, 160.17, 87.1, 298.97, 186.51, 118.11, 137.54, 40.68, 47.37, 779.83, 350.77, 664.66, 74.8, 34.93, 254.82, 101.43, 217.19, 482.85, 411.54, 64.24, 30.0] 
                masses_to_pave = sorted(Extra + np.arange(10., 1000., 100.).tolist())

            print('==='*15) 
            print('# Doing plot %s for %s' %(plot, p))
            print('==='*15) 
            
            x = []
            y = []
            z = []
            for tb in np.arange(0.05, 50.5, 0.5):
                for mTopave in masses_to_pave:
                    mTofix = options.mass
                    if mTopave < mTofix:
                        heavy   = options.fix[-1]
                        light   = pave[-1]
                        m_heavy = mTofix
                        m_light = mTopave
                    else:
                        heavy   = pave[-1]
                        light   = options.fix[-1]
                        m_heavy = mTopave
                        m_light = mTofix

                    prod = p.split('_')[0]+heavy
                    mode = '{}ToZ{}'.format(heavy, light) 
                    xsc, xsc_err, BR = get_branchingratio_crosssection(theory, m_heavy, m_light, mode, prod, tb)
                    if BR is None:
                        continue
                    
                    x.append(mTopave)
                    y.append(tb)
                    #print('th::', xsc*1000)
                    z.append(xsc*1000) # values from sushi are in pb --> move to fb 
        
            len_x = len(x)
            len_y = len(y)

            print( 'theory values are loaded from :: ', th_ymlF)
            print( len_x,len_y)
            print( 'max xsc:', max(z), 'min xsc:', min(z))

            x = np.asarray(x)
            y = np.asarray(y)
            z = np.asarray(z)
            
            ROOT.gStyle.SetOptStat("")
            ROOT.gStyle.SetPalette(color)
            ROOT.TColor.InvertPalette()
            c = ROOT.TCanvas("c", "c", 800, 800)
            
            theory_graph = ROOT.TGraph2D()
            for i in range(0,len(x)):
                theory_graph.SetPoint(i, float(x[i]), float(y[i]), float(z[i]))
            
            theory_hist = ROOT.TH2D("th_%s"%p,"th_%s"%p,1000,0,1000,50,0,50)
            for bin_x in np.arange(0,1000.,0.1):
                for bin_y in np.arange(0.05,50.,0.01):
                    theory_hist.SetBinContent(theory_hist.FindBin(bin_x,bin_y), theory_graph.Interpolate(bin_x,bin_y))
            
            theory_hist.GetYaxis().SetRangeUser(0, 50.)
            theory_hist.GetYaxis().SetRangeUser(0.,1000.)
            #theory_hist.GetZaxis().SetRangeUser(10e-3, 10e3)
            
            theory_hist.GetXaxis().SetTitleOffset(1.1)
            theory_hist.GetYaxis().SetTitleOffset(1.1)
            theory_hist.GetZaxis().SetTitleOffset(1.5)
            theory_hist.SetMinimum(1e-3)
            theory_hist.SetMaximum(1e10)
            c.SetLogz()
            theory_hist.Draw("COLZ")
            theory_hist.SaveAs('{}/theory_tb_vs_{}_{}-{}.root'.format(plot_dir, p, options.fix, options.mass), 'recreate')
            c.SaveAs('{}/theory_tb_vs_{}_{}-{}.png'.format(plot_dir, p, options.fix, options.mass))
            del c

    else:
        
        for cat, Cfg in catagories.items():

            flavors, prod, nb, region = Cfg    
            
            for flav in flavors:
                jsF = os.path.join(jsonpath, 'combinedlimits_{}_{}_{}_UL{}.json'.format(cat, flav, cl, options.era))
                jsFname = jsF.split('/')[-1].replace('.json', '') 
                
                process = "gg-fusion" if "ggH" in jsFname else "b-associated production"
                if not os.path.isfile(jsF):
                    continue
                
                print('==='*15) 
                logger.info('# working on %s :: %s %s %s'% (plot, cat, flav, region))
                print('==='*15) 
                li = get_generated_masses(jsF, options.mass)
                
                all_limits = []
                with open(jsF) as f:
                    all_limits = json.load(f)
                
                if not all_limits:
                    continue
                print( jsF)

                #get expected and observed histograms
                exp_graph = ROOT.TGraph2D()
                exp_hist  = ROOT.TH2D("exp_{}".format(jsFname),"",1000,0,1000,50,0,50)
                exp_hist.SetDirectory(0)
                if options.unblind:
                    obs_graph = ROOT.TGraph2D()
                    obs_hist  = ROOT.TH2D("obs_{}".format(jsFname),"",1000,0,1000,50,0,50)
                
                if  plot == 'expected_over_theory':
                    p = "gg_fusion" if prod == "ggH" else "bb_associated_production"
                    
                    exp_hist.GetZaxis().SetTitle("#sigma_{95%}/#sigma_{th}")
                    #Open theory histo already created in theory step
                    f_th = ROOT.TFile('{}/theory_tb_vs_{}_{}-{}.root'.format(plot_dir, p, options.fix, options.mass))
                    f_th.Print()

                    theory_hist = f_th.Get("th_%s"%p)
                    
                    #print (theory_hist.GetEntries())
                    #print (theory_hist.GetNbinsX())
                    #print (theory_hist.GetNbinsY())
                else:
                    if mirror:
                        exp_hist.GetZaxis().SetTitle('95% C.L. limit on #sigma(pp #rightarrow H/A) (fb)')#x B(Z #rightarrow l^{+}l^{-}) x B(H/A #rightarrow b#bar{b})')
                    else:
                        exp_hist.GetZaxis().SetTitle('95% C.L. limit on #sigma(pp #rightarrow H) (fb)')#x B(Z #rightarrow l^{+}l^{-}) x B(A #rightarrow b#bar{b})')
                
                cc  = ROOT.TCanvas(jsFname, jsFname, 800, 800)
                ROOT.gStyle.SetOptStat(0)
                ROOT.gStyle.SetPalette(color)
                #ROOT.TColor.InvertPalette()
                
                x = []
                y = []
                z = []
                z_obs = []
                
                for l in all_limits:
                    if l['parameters'][idx_mtofix] != str(options.mass):
                        continue
                    
                    mTopave = float(l['parameters'][idx_mtopave])
                    mTofix  = options.mass
                    
                    for tb in np.arange(0.05, 50.5, 0.5):
                        if mTopave < mTofix:
                            heavy   = options.fix[-1]
                            light   = pave[-1]
                            m_heavy = mTofix
                            m_light = mTopave
                        else:
                            heavy   = pave[-1]
                            light   = options.fix[-1]
                            m_heavy = mTopave
                            m_light = mTofix

                        mode = '{}ToZ{}'.format(heavy, light) 
                        xsc, xsc_err, BR   = get_branchingratio_crosssection(theory, m_heavy, m_light, mode, prod, tb)
                        if BR is None:
                            continue
                        
                        y.append(tb)
                        x.append(mTopave) 
                    
                        limit_exp = l['limits']['expected']*1000#/BR
                        z.append(limit_exp)
                        #print( mode, m_heavy, m_light, prod , BR, 'r:', l['limits']['expected']*1000, 'xsc:', limit_exp)
                        #print('Expected limit 95% {} sigma x BR, tb= {} : {} fb // (m{}, m{})= ({}, {}) GeV'.format(cl, tb, limit_exp, heavy, light, m_heavy, m_light))
                        if options.unblind:
                            limit_obs = l['limits']['observed']*1000#/BR
                            z_obs.append(limit_obs)
                            #print('Observed limit 95% {} sigma x BR, tb= {} : {} fb // (m{}, m{})= ({}, {}) GeV'.format(cl, tb, limit_exp, heavy, light, m_heavy, m_light))
                
                if mirror:
                    for l in all_limits:
                        if l['parameters'][idx_mtopave] != str(options.mass):
                            continue
                        
                        mTopave = float(l['parameters'][idx_mtofix])
                        if mTopave == 400.0:
                            continue
                        mTofix  = options.mass
                        
                        for tb in np.arange(0.05, 50.5, 0.5):
                            if mTopave < mTofix:
                                heavy   = pave[-1]
                                light   = options.fix[-1]
                                m_heavy = mTopave
                                m_light = mTofix
                            else:
                                heavy   = options.fix[-1]
                                light   = pave[-1]
                                m_heavy = mTofix
                                m_light = mTopave

                            for tb in np.arange(0.05, 50.5, 0.5):
                                op_mode = '{}ToZ{}'.format(heavy, light) 
                                op_prod = prod.replace(prod[-1], heavy)
                                
                                xsc, xsc_err, BR   = get_branchingratio_crosssection(theory, m_light, m_heavy, op_mode, op_prod, tb)
                                if BR is None:
                                    continue
                                
                                y.append(tb)
                                x.append(mTopave) 
                                limit_exp = l['limits']['expected']*1000/BR
                                z.append(limit_exp)
                            
                            if options.unblind:
                                limit_obs = l['limits']['observed']*1000/BR
                                z_obs.append(limit_obs)

                #print( set(x)) 
                #print( y)
                #print( z)
                #print( z_obs)
                
                xmax = max(set(x))
                xmin = min(set(x))
                
                x = np.asarray(x)
                y = np.asarray(y)
                z = np.asarray(z)
                z_obs = np.asarray(z_obs)
                
                
                for i in range(0,len(x)):
                    exp_graph.SetPoint(i, float(x[i]), float(y[i]), float(z[i]))
                    if options.unblind:
                        obs_graph.SetPoint(i, float(x[i]), float(y[i]), float(z_obs[i]))
                
                #for bin_x in range(0,1001):
                for bin_x in np.arange(0,1000,0.1):
                    for bin_y in np.arange(0,50,0.01):
                        if Interpolate: r_exp = exp_graph.Interpolate(bin_x,bin_y)
                        else: r_exp = z[bin_x]
                        exp_hist.SetBinContent(exp_hist.FindBin(bin_x,bin_y), r_exp) 
                        
                        if options.unblind:
                            if Interpolate: r_obs = obs_graph.Interpolate(bin_x,bin_y)
                            else: r_obs = z_obs[bin_x]
                            obs_hist.SetBinContent(obs_hist.FindBin(bin_x,bin_y), r_obs)
                
                xNm = pave[-1] if not mirror else 'H/A'
                exp_hist.GetXaxis().SetTitle("m_{%s} (GeV)"%xNm)
                exp_hist.GetYaxis().SetTitle("tan#beta")
                exp_hist.GetXaxis().SetRangeUser(xmin, xmax)#(0., 1000.)
                exp_hist.GetYaxis().SetRangeUser(0., 50.)
                #exp_hist.GetZaxis().SetRangeUser(1e2, 1e10)
                exp_hist.GetXaxis().SetTitleOffset(1.1)
                exp_hist.GetYaxis().SetTitleOffset(1.1)
                exp_hist.GetZaxis().SetTitleOffset(1.5)
                
                if plot != 'expected_over_theory':
                    exp_hist.SaveAs('{}/expected_{}_{}_tb_vs_{}_{}-{}.root'.format(plot_dir, opt, jsFname, pave, options.fix, options.mass), 'recreate')
                    if options.unblind:
                        obs_hist.SaveAs('{}/observed_{}_{}_tb_vs_{}_{}-{}.root'.format(plot_dir, opt, jsFname, pave, options.fix, options.mass), 'recreate')

                if  plot == 'expected_over_theory':
                    exp_hist.Divide(theory_hist)
                    if options.unblind:
                        obs_hist.Divide(theory_hist)
                
                    exp_hist.SetMinimum(1e-3)
                    exp_hist.SetMaximum(1e3)
                    if options.unblind:
                        obs_hist.SetMinimum(1e-3)
                        obs_hist.SetMaximum(1e3)
                

                contours = []
                contours.append(1.)
                contours = np.asarray(contours)

                #grid = ROOT.TPad("grid","",0,0,1,1) 
                #grid.Draw("same")
                #grid.cd()
                #grid.SetGrid()
                #grid.SetFillStyle(4000)
                
                #cc.SetLogy()
                cc.SetLogz()
                #cc.DrawFrame(-10,-10,10,10)
                
                exp_graph.Draw("colz")
                if options.unblind:
                    obs_graph.Draw("colz")
                
                exp_hist.SetContour(30)
                exp_hist.Smooth(1) # try  smoothing n times 
                exp_hist.DrawCopy("colz")
                exp_hist.SetContour(1,contours)
                
                if options.unblind:
                    obs_hist.DrawCopy("colz same")
                    obs_hist.SetContour(1,contours)
                    
                #exp_hist.GetXaxis().SetNdivisions(4)
                #exp_hist.GetYaxis().SetNdivisions(20)
                #exp_hist.GetYaxis().SetLabelOffset(999.) 
                #exp_hist.GetXaxis().SetLabelOffset(999.)
                if  plot == 'expected_over_theory':
                    exp_hist.Draw("cont3 same")
                    exp_hist.SetLineColor(ROOT.kRed)
                    exp_hist.SetLineStyle(3)  #dash-dot
                    
                    if options.unblind:
                        obs_hist.Draw("cont3 same")
                        obs_hist.SetLineColor(ROOT.kRed)
                        obs_hist.SetLineStyle(1)  #solid
                
                #leg = ROOT.TLegend(0.75,0.89,0.6,0.62)
                leg = ROOT.TLegend(0.7,0.87,0.55,0.62)
                leg.SetTextSize(0.025)
                leg.SetBorderSize(0)
                leg.SetFillStyle(0)
                
                if not mirror:
                    leg.SetHeader("#splitline{#it{2HDM-II, %s}}{#splitline{#it{H #rightarrow ZA #rightarrow llbb}}{#splitline{m_{%s}= %s GeV, cos(#beta-#alpha) = 0.01}{#it{%s%s}}}}"
                            %(process, options.fix[-1], int(options.mass), nb, region),"C")
                else:
                    leg.SetHeader("#splitline{#it{2HDM-II, %s}}{#splitline{#it{H/A #rightarrow ZA/H #rightarrow l^{+}l^{-} b#bar{b}}}{#splitline{m_{%s}= %s GeV, cos(#beta-#alpha) = 0.01}{#it{%s%s}}}}"
                            %(process, 'H/A', int(options.mass), nb, region),"C")
                
                suffix =' excluded' if  plot == 'expected_over_theory' else ''
                leg.AddEntry(exp_hist,"Exp.%s"%suffix,"lp")

                if options.unblind:
                    leg.AddEntry(obs_hist,"Obs.%s"%suffix,"l")
                
                leg.Draw("same")
                if (ROOT.gPad):
                    ROOT.gPad.SetLeftMargin(0.15)
                    ROOT.gPad.SetRightMargin(0.2)
                    ROOT.gPad.SetTopMargin(0.12)
                    ROOT.gPad.SetBottomMargin(0.12)
                
                t = cc.GetTopMargin()
                r = cc.GetRightMargin()
                l = cc.GetLeftMargin()
                lumiTextOffset   = 0.2
                
                syst_text = ROOT.TLatex(0.15, 1-t+lumiTextOffset*t, "CMS Simulation")
                syst_text.SetNDC(True)
                syst_text.SetTextFont(40)
                syst_text.SetTextSize(0.03)
                syst_text.Draw("same")

                lumi = ROOT.TLatex(0.62, 1-t+lumiTextOffset*t, "%s fb^{-1} (13 TeV)" %format(Constants.getLuminosity(options.era)/1000.,'.2f'))
                lumi.SetNDC(True)
                syst_text.SetTextFont(40)
                lumi.SetTextSize(0.03)
                lumi.Draw("same")

                if plot == 'expected_over_theory':
                    exp_hist.SaveAs('{}/expected_over_theory_{}_{}_tb_vs_{}_{}-{}.root'.format(plot_dir, opt, jsFname, pave, options.fix, options.mass), 'recreate')
                    if options.unblind:
                        obs_hist.SaveAs('{}/observed_over_theory_{}_{}_tb_vs_{}_{}-{}.root'.format(plot_dir, opt, jsFname, pave, options.fix, options.mass), 'recreate')
                
                cc.SaveAs('{}/{}_{}_{}_tb_vs_{}_{}-{}.png'.format(plot_dir, plot, opt, jsFname, pave, options.fix, options.mass))
                cc.SaveAs('{}/{}_{}_{}_tb_vs_{}_{}-{}.pdf'.format(plot_dir, plot, opt, jsFname, pave, options.fix, options.mass))
                del cc
