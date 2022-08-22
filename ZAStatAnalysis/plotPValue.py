import argparse
import json
import ROOT
import CMSStyle as CMSStyle
import numpy as np


def createGraphAndHisto():
    input_dir = "ul__combinedlimits/preapproval/work__v10-ext2/work__2/bayesian_rebin_on_S/pvalue-significance/dnn/jsons/"

    with open(input_dir+'pvalue_significance_ggH_resolved_ElEl_MuMu.json') as f:
        results = json.load(f)

    masses       = []
    pvalue       = []
    significance = []
    for dict_ in results:
        print( dict_ )
        m = dict_['parameters']
        if not m in masses:
            masses.append(m)
        if 'expected_significance' in dict_.keys():
            significance.append(dict_['expected_significance'])
        else:
            pvalue.append(dict_['expected_p-value'])

    cc = ROOT.TCanvas("cc", "cc", 800,800)
    print ("canvas defined" )
    ROOT.gStyle.SetOptStat(0)
    print ("set opt stat")
    ROOT.gStyle.SetPalette(71)
    print ("palette set")

    #get expected and observed histograms
    pvalue_graph = ROOT.TGraph2D()
    pvalue_hist = ROOT.TH2D("pvalue","p-value",1000,0,1000,1000,0,1000)

    print ("graph defined")

    pvalue_hist.SetTitleSize(0.2, "t")
    pvalue_hist.GetXaxis().SetTitle("m_{A} (GeV)")
    pvalue_hist.GetYaxis().SetTitle("m_{H} (GeV)")
    pvalue_hist.GetXaxis().SetRangeUser(20., 1000.)
    pvalue_hist.GetYaxis().SetRangeUser(90., 1000.)
    pvalue_hist.GetZaxis().SetTitle("p-value")
    pvalue_hist.GetXaxis().SetTitleOffset(1.1)
    pvalue_hist.GetYaxis().SetTitleOffset(1.7)
    pvalue_hist.GetZaxis().SetTitleOffset(1.1)
    print ("graph params set")

    x = []
    y = []
    z = []
    for i,m in enumerate(masses):
        if i%2==0:
            print ("mA, mH: ", m[1], m[0])
        x.append(m[1])
        y.append(m[0])

    for i,p in enumerate(pvalue): 
        if i%2==0:
            print ("pvalue: ", p)
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
    
    cc.SaveAs(input_dir+'pvalue2D_207SimMasses.png')
    del cc

if __name__ == "__main__":
    createGraphAndHisto()
