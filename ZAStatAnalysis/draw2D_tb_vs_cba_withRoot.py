import os, os.path , sys
import argparse
import json
import ROOT
import math
import numpy as np

import Constants as Constants

ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description='Draw 2D mass scan')
parser.add_argument('-p', '--jsonpath', action='store', type=str, required=True,
                help='JSON file containing the limits for all the points (Combined channel)')
parser.add_argument('--unblind', action='store_true', dest='unblind', help='If set, draw also observed upper limits')
parser.add_argument('--era', type=str, required=True, help='data taking of the given limits')
parser.add_argument('--prod', type=str, default='ggH', choices=['ggH', 'bbH'], help='data taking of the given limits')
parser.add_argument('--mH', type=float, default=500., help='heavy higgs mass for decay mode H ->ZA')
parser.add_argument('--mA', type=float, default=300., help='light pseudo-scalar mass for decay mode H->ZA')

options = parser.parse_args()

output_dir = options.jsonpath
plot_dir   = os.path.join(output_dir, 'paper_2D_tb_cba')
if not os.path.isdir(plot_dir):
        os.makedirs(plot_dir)

mH = options.mH
mA = options.mA

plots = [
    'theory',
    'expected_over_theory',
    #'expected', 
    ]

catagories ={
    #'ggH_resolved'         : ['MuMu_ElEl'],
    #'ggH_boosted'          : ['OSSF'],
    #'ggH_resolved_boosted'  : ['OSSF'],
    'bbH_resolved'          : ['OSSF'],
    #'bbH_boosted'           : ['OSSF'],
    #'bbH_resolved_boosted' : ['OSSF'],
    }

color = ROOT.kLake
Interpolate = False

#th_jsF = 'sigmaBR_HZA_type-2_MH-379p0_MA-172p00.json'
#th_jsF = 'data/sigmaBR_HZA_type-2_MH-500p0_MA-300p00_everytan_a.json'
th_jsF  = 'data/sigmaBR_{}_HZA_type-2_MH-{}_MA-{}_tb_cba.json'.format(options.prod, options.mH, options.mA)
#th_jsF  = 'data/sigmaBR_HZA_type-2_MH-500p0_MA-300p00.json'

theory = {}
with open(th_jsF) as f:
    theory = json.load(f)

for plot in plots:
    print('# Doing plot %s' % plot)
    print('==='*15) 
    if plot == 'theory':
        
        x = theory['cba']
        y = theory['tb']
        z = [theory['sigma'][i] * 1000. * theory['TotBR'][i] for i,z in enumerate(theory['sigma'])]
        
        len_x = len(x)
        len_y = len(y)

        print( 'theory values are loaded from :: ', th_jsF)
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
        
        theory_hist = ROOT.TH2D("theory","theory",1600,-1,1,10000,0,50)
        for bin_x in np.arange(-1,1.1,0.00125):
            for bin_y in np.arange(0,50.1,0.005):
                theory_hist.SetBinContent(theory_hist.FindBin(bin_x,bin_y), theory_graph.Interpolate(bin_x,bin_y))
        
        theory_hist.SetMinimum(0.001)
        theory_hist.SetMaximum(400)
        theory_hist.Draw("COLZ")
        theory_hist.SaveAs('{}/{}_{}_mH_{}_mA_{}_finerbinning.root'.format(plot_dir, plot, options.prod, mH, mA), 'recreate')
        c.SaveAs('{}/{}_{}_mH_{}_mA_{}_root.png'.format(plot_dir, plot, options.prod, mH, mA))
        del c

    else:
        for cat, flavors in catagories.items():
            
            if not options.prod in cat:
                continue

            for flav in flavors:
                jsF = os.path.join(options.jsonpath, 'combinedlimits_{}_{}_UL{}.json'.format(cat, flav, options.era))
                jsFname = jsF.split('/')[-1].replace('.json', '') 
                
                process = "gg-fusion" if "ggH" in jsFname else "b-associated production"
                tb      = '1.5' if 'ggH' in jsFname else '20.'
                
                if not os.path.isfile(jsF):
                    continue
                
                print('# Doing cat %s' % cat)

                all_limits = []
                with open(jsF) as f:
                    all_limits = json.load(f)

                cc  = ROOT.TCanvas("cc", "cc", 800, 800)
                ROOT.gStyle.SetOptStat(0)
                #ROOT.gStyle.SetPalette(71)
                ROOT.gStyle.SetPalette(color)
                ROOT.TColor.InvertPalette()
                
                #get expected and observed histograms
                exp_hist  = ROOT.TH2D("exp","",1600,-1,1,10000,0,50)
                if options.unblind:
                    obs_hist  = ROOT.TH2D("obs","",1600,-1,1,10000,0,50)
                
                #Open theory histo already created in theory step
                f_th = ROOT.TFile('{}/theory_{}_mH_{}_mA_{}_finerbinning.root'.format(plot_dir, options.prod, mH, mA))
                f_th.Print()
                
                theory_hist = f_th.Get("theory")
                print (theory_hist.GetEntries())
                print (theory_hist.GetNbinsX())
                print (theory_hist.GetNbinsY())

                exp_hist.GetXaxis().SetTitle("cos(#beta-#alpha)")
                exp_hist.GetYaxis().SetTitle("tan#beta")
                exp_hist.GetZaxis().SetTitle("#sigma_{95%}/#sigma_{th}")
                exp_hist.GetYaxis().SetRangeUser(0.1, 50.)
                exp_hist.GetZaxis().SetRangeUser(10e-3, 10e3)
                exp_hist.GetXaxis().SetTitleOffset(1.1)
                exp_hist.GetYaxis().SetTitleOffset(1.1)
                exp_hist.GetZaxis().SetTitleOffset(1.3)

                x = []
                y = []
                z = []
                z_obs = []
                for l in all_limits:
                    if l['parameters'] != [str(options.mH), str(options.mA)]:
                        continue
                    
                    br = 0.568484205* 0.570528705* 0.067316
                    limit_exp = l['limits']['expected']*1000
                    print ( 'expected limit 95% CL sigma x BR: ', limit_exp, l['parameters'], '(fb)')
                    if options.unblind:
                        limit_obs = l['limits']['observed']*1000
                        print ( 'observed limit 95% CL sigma x BR: ', limit_obs, '(fb)')
                
                x = theory['cba']
                y = theory['tb']
                for xval in range(len(x)):
                    z.append(limit_exp)
                    if options.unblind:
                        z_obs.append(limit_obs)
                    
                x = np.asarray(x)
                y = np.asarray(y)
                z = np.asarray(z)
                z_obs = np.asarray(z_obs)

                for bin_x in np.arange(-1,1.1,0.00125):
                    for bin_y in np.arange(0,50.1,0.005):
                        
                        if Interpolate: r_exp = exp_hist.Interpolate(bin_x,bin_y)
                        else: r_exp = limit_exp
                        exp_hist.SetBinContent(exp_hist.FindBin(bin_x,bin_y), r_exp) 
                        
                        if options.unblind:
                            if Interpolate: r_obs = obs_hist.Interpolate(bin_x,bin_y)
                            else: r_obs = limit_obs
                            obs_hist.SetBinContent(obs_hist.FindBin(bin_x,bin_y), r_obs)

                
                c = ROOT.TCanvas("c", "c", 800, 800)
                exp_hist.Draw("colz")
                if options.unblind:
                    obs_hist.Draw("colz")
                del c

                exp_hist.SaveAs('{}/expected_{}_mH_{}_mA_{}.root'.format(plot_dir, jsFname, options.mH, options.mA), 'recreate')
                if options.unblind:
                    obs_hist.SaveAs('{}/observed_{}_mH_{}_mA_{}.root'.format(plot_dir, jsFname, options.mH, options.mA), 'recreate')

                if  plot == 'expected_over_theory':
                    exp_hist.Divide(theory_hist)
                    if options.unblind:
                        obs_hist.Divide(theory_hist)
                
                #exp_hist.SetMinimum(0.01)
                #exp_hist.SetMaximum(1e3)
                if options.unblind:
                    obs_hist.SetMinimum(0.001)
                    obs_hist.SetMaximum(1e3)

                contours = []
                contours.append(1.)
                contours = np.asarray(contours)

                #grid = ROOT.TPad("grid","",0,0,1,1) 
                #grid.Draw("same")
                #grid.cd()
                #grid.SetGrid()
                #grid.SetFillStyle(4000)
                
                #cc.DrawFrame(-10,-10,10,10)
                cc.SetLogy()
                cc.SetLogz()
                
                exp_hist.SetContour(20)
                exp_hist.Smooth()
                exp_hist.DrawCopy("colz")
                exp_hist.SetContour(1,contours)
                
                if options.unblind:
                    obs_hist.DrawCopy("colz same")
                    obs_hist.SetContour(1,contours)
                    
                #exp_hist.GetXaxis().SetNdivisions(4)
                #exp_hist.GetYaxis().SetNdivisions(20)
                #exp_hist.GetYaxis().SetLabelOffset(999.) 
                #exp_hist.GetXaxis().SetLabelOffset(999.)
                
                exp_hist.Draw("cont3 same")
                exp_hist.SetLineColor(ROOT.kRed)
                exp_hist.SetLineStyle(3)  #dash-dot
                
                if options.unblind:
                    obs_hist.Draw("cont3 same")
                    obs_hist.SetLineColor(ROOT.kRed)
                    obs_hist.SetLineStyle(1)  #solid
                
                leg = ROOT.TLegend(0.75,0.89,0.6,0.62)
                leg.SetTextSize(0.025)
                leg.SetBorderSize(0)
                leg.SetFillStyle(0)
                leg.SetHeader("#splitline{#it{2HDM-II, %s}}{#splitline{#it{H #rightarrow ZA #rightarrow llbb}}{(m_{H}, m_{A})= (%s, %s) GeV}}"
                        %(process, options.mH, options.mA),"C")
                leg.AddEntry(exp_hist,"Exp. excluded","lp")

                if options.unblind:
                    leg.AddEntry(obs_hist,"Obs. excluded","l")
                
                leg.Draw("same")
                if (ROOT.gPad):
                    ROOT.gPad.SetLeftMargin(0.15)
                    ROOT.gPad.SetRightMargin(0.15)
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

                cc.SaveAs('{}/{}_{}_mH_{}_mA_{}_tb_cba.png'.format(plot_dir, plot, jsFname, mH, mA))
                cc.SaveAs('{}/{}_{}_mH_{}_mA_{}_tb_cba.pdf'.format(plot_dir, plot, jsFname, mH, mA))
                print('==='*15) 
                del cc
