import os, os.path, sys
import argparse
import json
import CMSStyle
import ROOT
ROOT.gROOT.SetBatch(True)
from ROOT import kLake, kDeepSea

import numpy as np
import Constants as Constants

parser = argparse.ArgumentParser(description='Draw 2D mass scan')
parser.add_argument('-p', '--jsonpath', action='store', type=str, required=True, 
        help='JSON file containing the limits for all the points (Combined channel)')
parser.add_argument('--unblind', action='store_true', default=False, help='If set, draw also observed upper limits')
parser.add_argument('--era', type=str, default=False, required=True, help='data taking of the given limits')

options = parser.parse_args()
output_dir = options.jsonpath
plot_dir   = os.path.join(output_dir, 'paper_2D_mH_mA')
if not os.path.isdir(plot_dir):
    os.makedirs(plot_dir)

plots = [
    #'theory',
    'expected',
    #'expected_over_theory'
    ]
catagories ={
    'ggH_resolved' : ['MuMu_ElEl'],  
    'bbH_resolved' : ['OSSF'],  
    'ggH_boosted'  : ['OSSF'],
    'bbH_boosted'  : ['OSSF'],
    }

interplolate = True
color  = ROOT.kLake
#color = ROOT.kRainBow
#color = ROOT.kAurora

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(color)
ROOT.TColor.InvertPalette()

theory = {}
with open('data/sigmaBR_HZA_type-2_tb-1p5_cba-0p01_fromAlessia.json') as f:
#with open('data/sigmaBR_HZA_type-2_tb-1p5_cba-0p01_mirroring.json') as f:
    theory = json.load(f)


for plot in plots:
    if plot == 'theory':
        print ('working on %s plot :: this may take some time' % plot)
        x = theory['mA']
        y = theory['mH']
        z = [theory['sigma'][i] * 1000. * theory['BR'][i] for i,z in enumerate(theory['sigma'])]

        x = np.asarray(x)
        y = np.asarray(y)
        z = np.asarray(z)
        xmin = ymin = 90
        xmax = ymax = 1000
        
        theory_graph = ROOT.TGraph2D()
        
        for i in range(0,len(x)):
            theory_graph.SetPoint(i, float(x[i]), float(y[i]), float(z[i]))

        theory_hist = ROOT.TH2D("theory","theory",1000,0,1000,1000,0,1000)

        for bin_x in range(1,len(x)+1):
            for bin_y in range(1,len(y)+1):
                theory_hist.SetBinContent(theory_hist.FindBin(bin_x,bin_y), theory_graph.Interpolate(bin_x,bin_y))

        #theory_hist.SetMinimum(0.001)
        #theory_hist.SetMaximum(700)
        ROOT.gStyle.SetOptStat("")
        ROOT.TColor.InvertPalette()
        ROOT.gStyle.SetPalette(color)

        c = ROOT.TCanvas("c", "c", 800, 600)
        theory_hist.Draw("COLZ")
        
        c.SaveAs('paper_2D_mH_mA/' + plot + '_limits.png')
        c.SaveAs('paper_2D_mH_mA/' + plot + '_limits.pdf')
        del c
        theory_hist.SaveAs('paper_2D_mH_mA/' + plot + '_limits.root')
    
    else:
        for cat, flavors in catagories.items():
            process = "gg-fusion" if "ggH" in cat else "b-associated production"
            for flav in flavors:
                json_f = os.path.join(options.jsonpath, 'combinedlimits_{}_{}_UL{}.json'.format(cat, flav, options.era))
                if not os.path.isfile(json_f):
                    continue
                with open(json_f) as f:
                    all_limits = json.load(f)
    
                print ('working on %s plot :: this may take some time' % plot)
                cc  = ROOT.TCanvas("cc", "cc", 800,800)
                leg = ROOT.TLegend(0.63,0.76,0.85,0.88)
                

                #Open theory histo already created in theory step
                if plot == 'expected_over_theory':
                    f_th = ROOT.TFile('{}/theory_limits.root'.format(plot_dir))
                    #f_th.Print()
                    theory_hist = f_th.Get("theory")
                    print (theory_hist.GetEntries())

                #get expected and observed histograms
                exp_graph = ROOT.TGraph2D()
                title     = "2HDM-II tan#beta=1.5, cos(#beta-#alpha)=0.01"
                exp_hist  = ROOT.TH2D("exp",title,1000,0,1000,1000,0,1000)
                
                if options.unblind: 
                    obs_graph = ROOT.TGraph2D()
                    obs_hist  = ROOT.TH2D("obs","obs",1000,0,1000,1000,0,1000)

                exp_hist.SetTitleSize(0.2, "t")
                exp_hist.GetXaxis().SetTitle("m_{A} (GeV)")
                exp_hist.GetYaxis().SetTitle("m_{H} (GeV)")
                exp_hist.GetXaxis().SetRangeUser(29., 1000.)
                exp_hist.GetYaxis().SetRangeUser(29., 1000.)
                exp_hist.GetXaxis().SetTitleOffset(1.1)
                exp_hist.GetYaxis().SetTitleOffset(1.7)
                exp_hist.GetZaxis().SetTitleOffset(1.1)
                
                if plot == 'expected_over_theory':
                    exp_hist.GetZaxis().SetTitle("#sigma_{95%}/#sigma_{th}")
                else:
                    exp_hist.GetZaxis().SetTitle('95% C.L. limit on #sigma(pp #rightarrow H)')

                x = []
                y = []
                z = []
                z_obs = []
                for l in all_limits:
                    x.append(l['parameters'][1])
                    y.append(l['parameters'][0])
                    z.append(l['limits']['expected'] *1000) # from pb to fb
                    if options.unblind:
                        z_obs.append(l['limits']['observed']*1000) # from pb to fb
                    
                    #Mirror the plane:
                    #x.append(l['parameters'][0])
                    #y.append(l['parameters'][1])
                    #z.append(l['limits']['expected']*1000)
                    #if options.unblind:
                    #    z_obs.append(l['limits']['observed']*1000)
                
                x = np.asarray(x)
                y = np.asarray(y)
                z = np.asarray(z)
                if options.unblind:
                    z_obs = np.asarray(z_obs)

                for i in range(0,len(x)):
                    exp_graph.SetPoint(i, float(x[i]), float(y[i]), float(z[i]))
                    if options.unblind:
                        obs_graph.SetPoint(i, float(x[i]), float(y[i]), float(z_obs[i]))
                
                if interplolate:
                    for bin_x in range(1,1001):
                        for bin_y in range(1,1001):
                            exp_hist.SetBinContent(exp_hist.FindBin(bin_x,bin_y), exp_graph.Interpolate(bin_x,bin_y))
                            if options.unblind:
                                obs_hist.SetBinContent(obs_hist.FindBin(bin_x,bin_y), obs_graph.Interpolate(bin_x,bin_y))

                #exp_hist.SetMinimum(0.001)
                #exp_hist.SetMaximum(3500)
                #obs_hist.SetMinimum(0.001)
                #obs_hist.SetMaximum(3500)
                
                #c = ROOT.TCanvas("c", "c", 800, 800)
                #exp_hist.Draw("COLZ")
                #obs_hist.Draw("COLZ")
                #del c
                
                #exp_hist.SaveAs('paper_2D_mH_mA/expected.root', 'update')
                #obs_hist.SaveAs('paper_2D_mH_mA/observed.root', 'update')
                #exp_graph.SaveAs('paper_2D_mH_mA/expected.root')
                #obs_graph.SaveAs('paper_2D_mH_mA/observed.root')

                #print (theory_hist.GetBinContent(382,140) )
                #print (exp_hist.GetBinContent(382,140) )
                #print (obs_hist.GetBinContent(382,140) )
                #print ("ratio exp: ", exp_hist.GetBinContent(172,379)/theory_hist.GetBinContent(172,379))
                #print ("ratio obs: ", obs_hist.GetBinContent(172,379)/theory_hist.GetBinContent(172,379))
       
                if plot == 'expected_over_theory': 
                    exp_hist.Divide(theory_hist)
                    if options.unblind:
                        obs_hist.Divide(theory_hist)

                exp_hist.SetMaximum(30) 
                exp_hist.SetMinimum(0)
                if options.unblind:
                    obs_hist.SetMaximum(30) 
                    obs_hist.SetMinimum(0) 

                #for binx in range(1,1001):
                    #for biny in range(1,1001):
                        #if binx>biny-90. and binx<biny+90.:
                        #    exp_hist.SetBinContent(exp_hist.FindBin(binx,biny), 0.)
                        #    obs_hist.SetBinContent(obs_hist.FindBin(binx,biny), 0.)

                contours = []
                contours.append(1.)
                contours = np.asarray(contours)

                #c = ROOT.TCanvas("c", "c", 800, 600)
                #exp_hist.Draw("COLZ")
                #c.SetRightMargin(2)
                #c.SetLeftMargin(2)
                #c.SaveAs('paper_2D_mH_mA/ratio_exp_root.png')
                #del c

                #cc = ROOT.TCanvas("cc", "cc", 800,800)
                cc.SetLogz()
                cc.DrawFrame(-10,-10,10,10);
                #cc.SetRightMargin(1.5)
                #cc.SetLeftMargin(1.5)
                
                exp_hist.DrawCopy("colz");
                exp_hist.SetContour(1,contours);
                
                if options.unblind:
                    obs_hist.DrawCopy("colz same");
                    obs_hist.SetContour(1,contours);
                
                exp_hist.Draw("cont3 same");
                exp_hist.SetLineColor(ROOT.kBlack)
                exp_hist.SetLineStyle(1)  # 3 dash-dot
                exp_hist.SetLineWidth(3)

                if options.unblind:
                    obs_hist.Draw("cont3 same");
                    obs_hist.SetLineColor(ROOT.kRed)
                    obs_hist.SetLineStyle(1)  # 1 solid
       
                leg.SetLineWidth(1) 
                leg.SetLineColor(2)
                leg.SetFillColor(ROOT.kWhite)
                leg.SetFillStyle(0)
                leg.SetBorderSize(0)
                leg.AddEntry(exp_hist,"95% Expected upper limit" +"\n"+"{}".format(process),"lp")
                if options.unblind:
                    leg.AddEntry(obs_hist,"Obs. excluded","l")
                leg.Draw("same")
                if (ROOT.gPad):
                    ROOT.gPad.SetLeftMargin(0.12)
                    ROOT.gPad.SetRightMargin(0.135)
                    #ROOT.gPad.SetBottomMargin(0.15)

                #syst_text = ROOT.TLatex(0.13, 0.96, "CMS Preliminary")
                #syst_text.SetNDC(True)
                #syst_text.SetTextFont(40)
                #syst_text.SetTextSize(0.03)
                #syst_text.Draw("same")

                #lumi = ROOT.TLatex(0.6, 0.96, "%s fb^{-1} (13 TeV)" %format(Constants.getLuminosity(options.era)/1000.,'.2f'))
                #lumi.SetNDC(True)
                #syst_text.SetTextFont(40)
                #lumi.SetTextSize(0.03)
                #lumi.Draw("same")

                #cc.Update();
                #palette = exp_hist.GetListOfFunctions().FindObject("palette")
                #palette.SetX1NDC(0.9)
                #palette.SetX2NDC(0.95)
                #palette.SetY1NDC(0.2)
                #palette.SetY2NDC(0.8)
                #cc.Modified()
                #cc.Update()

                if options.unblind:
                    plot +='_observed'
                cc.SaveAs('{}/{}_limits_2d_mH_mA_{}_{}_{}.png'.format(plot_dir, plot, cat, flav, options.era))
                cc.SaveAs('{}/{}_limits_2d_mH_mA_{}_{}_{}.pdf'.format(plot_dir, plot, cat, flav, options.era))
                
                #    obs_hist.SaveAs('{}/{}_limits_{}_{}_{}.png'.format(plot_dir, plot, cat, flav, options.era))
                del cc
