import os , os.path, sys
import argparse
import json
import ROOT
import glob
import numpy as np

import CMSStyle as CMSStyle
import Constants as Constants 

ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True


def createGraphAndHisto(input_dir, era):

    for jsF in glob.glob( os.path.join(input_dir, '*.json')):
        
        jsFname= jsF.split('/')[-1].replace('.json', '')
        if not jsFname.startswith('pvalue_significance_'):
            continue
        
        process = 'gg-fusion' if 'ggH' in jsFname else 'b-associated production'
        tb      = '1.5' if 'ggH' in jsFname else '20.'
        
        with open(jsF) as f:
            results = json.load(f)

        masses       = []
        pvalue       = []
        significance = []
        for dict_ in results:
            m = dict_['parameters']
            if not m in masses:
                masses.append(m)
            if 'expected_significance' in dict_.keys():
                significance.append(dict_['expected_significance'])
            else:
                pvalue.append(dict_['expected_p-value'])

        cc = ROOT.TCanvas("cc", "cc", 800,800)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetPalette(71)
        #ROOT.gStyle.SetPalette(ROOT.kViridis)
        #ROOT.TColor.InvertPalette()

        #get expected and observed histograms
        pvalue_graph = ROOT.TGraph2D()
        pvalue_hist = ROOT.TH2D("pvalue","",1000,0,1000,1000,0,1000)

        pvalue_hist.SetTitleSize(0.2, "t")
        pvalue_hist.GetXaxis().SetTitle("m_{A} (GeV)")
        pvalue_hist.GetYaxis().SetTitle("m_{H} (GeV)")
        pvalue_hist.GetXaxis().SetRangeUser(20., 1000.)
        pvalue_hist.GetYaxis().SetRangeUser(90., 1000.)
        pvalue_hist.GetZaxis().SetTitle("p-value")
        pvalue_hist.GetXaxis().SetTitleOffset(1.1)
        pvalue_hist.GetYaxis().SetTitleOffset(1.7)
        pvalue_hist.GetZaxis().SetTitleOffset(1.1)

        x = []
        y = []
        z = []
        print( 'working on :: %s'%jsFname)
        for i,(m, p)in enumerate(zip(masses, pvalue)):
            #if i%2==0:
            print ("(mH, mA)= ({}, {}) , pvalue= {}".format(m[0], m[1], p))
            x.append(m[1])
            y.append(m[0])
            z.append(p)

        x = np.asarray(x)
        y = np.asarray(y)
        z = np.asarray(z)

        for i in range(0,len(x)):
            pvalue_graph.SetPoint(i, float(x[i]), float(y[i]), float(z[i]))
        print ("graph filled" )

        for bin_x in range(1,1001):
            for bin_y in range(1,1001):
                pvalue_hist.SetBinContent(pvalue_hist.FindBin(bin_x,bin_y), pvalue_graph.Interpolate(bin_x,bin_y))

        #f_th = ROOT.TFile(input_dir+'pvalue_hist.root')
        #theory_hist = f_th.Get("pvalue")
        pvalue_hist.SetMaximum(1) 
        pvalue_hist.SetMinimum(0.0000001) 

        cc.SetLogz()
        cc.DrawFrame(-10,-10,10,10)
        pvalue_hist.Draw("colz");
        pvalue_hist.SetTitleSize(0.2, "t")
        #pvalue_graph.Draw("colz");
        if (ROOT.gPad):
            ROOT.gPad.SetLeftMargin(0.12)
            ROOT.gPad.SetRightMargin(0.135)
    
        leg = ROOT.TLegend(0.7,0.89,0.6,0.8)
        leg.SetTextSize(0.025)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0)
        leg.SetHeader("#splitline{#it{2HDM-II, tan#beta= %s, cos(#beta-#alpha) = 0.01}}{%s, #it{H #rightarrow ZA #rightarrow llbb}}"%(tb, process),"C")
        leg.Draw("same")

        t = cc.GetTopMargin()
        r = cc.GetRightMargin()
        l = cc.GetLeftMargin()
        lumiTextOffset   = 0.2
        
        syst_text = ROOT.TLatex(0.15, 1-t+lumiTextOffset*t, "CMS Simulation")
        syst_text.SetNDC(True)
        syst_text.SetTextFont(40)
        syst_text.SetTextSize(0.03)
        syst_text.Draw("same")

        lumi = ROOT.TLatex(0.62, 1-t+lumiTextOffset*t, "%s fb^{-1} (13 TeV)" %format(Constants.getLuminosity(era)/1000.,'.2f'))
        lumi.SetNDC(True)
        lumi.SetTextSize(0.03)
        lumi.Draw("same")
        

        cc.SaveAs(input_dir+'{}.png'.format(jsFname))
        del cc

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='2D Pvalue scan', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-i", "--input", default=None, required=True, help="bamboo stageout dir")
    parser.add_argument("--era", type=str, required=True, help="")

    options = parser.parse_args()
    
    createGraphAndHisto(input_dir=options.input, era=options.era)
