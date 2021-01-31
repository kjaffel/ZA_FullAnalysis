#! /bin/env python

import os, sys, argparse
import yaml

# to prevent pyroot to hijack argparse we need to go around
tmpargv = sys.argv[:] 
sys.argv = []

# ROOT imports
import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
sys.argv = tmpargv

from HistogramTools import setTDRStyle

# For systematics computed with alternate samples, draw statistical uncertainties on ratios
alternateSamples = ['isr', 'fsr', 'tune', 'hdamp']

def beautify(s):
    if s == 'ttbar':
        return r't#bar{t}'
    if s == 'dy':
        return 'Drell-Yan'
    if s == 'SingleTop':
        return 'Single top'
    if s == 'others':
        return 'other backgrounds'
    if s == 'ttV':
        return 't#bar{t}V'
    if s == 'wjets':
        return 'W + jets'
    if s == 'VV':
        return 'VV'
    if s == 'SMHiggs':
        return 'SM Higgs'
    if s == 'ggHH':
        return 'SM HH'

    if s == 'CMS_eff_b':
        return 'Jet b-tagging'
    if s == 'CMS_eff_trigger':
        return 'Trigger efficiency'
    if s == 'CMS_scale_j':
        return 'Jet energy scale'
    if s == 'CMS_res_j':
        return 'Jet energy resolution'
    if s == 'CMS_eff_e':
        return 'Electron ID \\& ISO'
    if s == 'CMS_eff_mu':
        return 'Muon ID'
    if s == 'CMS_iso_mu':
        return 'Muon ISO'
    if s == 'CMS_pu':
        return 'Pileup'
    if s == 'pdf':
        return 'Parton distributions'
    if s == 'lumi_13TeV_2015':
        return 'Luminosity'

    if s == 'ttbar_modeling':
        return r'$\ttbar$ modeling'
    if s == 'ttbar_xsec':
        return r'$\ttbar$ cross-section'
    if s == 'dy_modeling':
        return r'Drell-Yan modeling'
    if s == 'dy_xsec':
        return r'Drell-Yan cross-section'
    if s == 'SingleTop_modeling':
        return r'Single top modeling'
    if s == 'SingleTop_xsec':
        return r'Single top cross-section'

    if s == 'MC_stat':
        return 'MC stat.'

    if 'QCDscale' in s:
        return 'QCD scale'

    return s + '**'

def drawSystematic(nominal, up, down, title, syst, proc, plotOpts, output):

    c = ROOT.TCanvas("c", "c")

    hi_pad = ROOT.TPad("pad_hi", "", 0., 0.33333, 1, 1)
    hi_pad.Draw()
    hi_pad.SetTopMargin(0.05 / .6666)
    hi_pad.SetLeftMargin(0.16)
    hi_pad.SetBottomMargin(0.015)
    hi_pad.SetRightMargin(0.02)

    lo_pad = ROOT.TPad("pad_lo", "", 0., 0., 1, 0.33333)
    lo_pad.Draw()
    lo_pad.SetTopMargin(1)
    lo_pad.SetLeftMargin(0.16)
    lo_pad.SetBottomMargin(0.13 / 0.33333)
    lo_pad.SetRightMargin(0.02)
    lo_pad.SetTickx(1)

    hi_pad.cd()

    up.SetLineWidth(2)
    up.SetLineColor(ROOT.TColor.GetColor('#468966'))
    up.GetYaxis().SetLabelSize(0.02 / 0.666)
    up.GetYaxis().SetTitleSize(0.03 / 0.666)
    up.GetYaxis().SetTitleOffset(1.7 * 0.666)
    up.GetYaxis().SetTitle("Events")
    up.GetXaxis().SetLabelSize(0)
    up.Draw("hist")

    nominal.SetLineWidth(2)
    nominal.SetLineStyle(2)
    nominal.SetLineColor(ROOT.TColor.GetColor('#FFB03B'))
    nominal.Draw("hist same")

    up.Draw("hist same")

    down.SetLineWidth(2)
    down.SetLineColor(ROOT.TColor.GetColor('#8E2800'))
    down.Draw("hist same")

    hist_max = -100
    hist_min = 9999999
    for i in range(1, up.GetNbinsX() + 1):
        hist_max = max(hist_max, up.GetBinContent(i), down.GetBinContent(i), nominal.GetBinContent(i))
        hist_min = min(hist_min, up.GetBinContent(i), down.GetBinContent(i), nominal.GetBinContent(i))
    # up.GetYaxis().SetRangeUser(hist_min * 0.9, hist_max * 1.4)    
    up.GetYaxis().SetRangeUser(0, hist_max * 1.4)    
    
    lo_pad.cd()
    lo_pad.SetGrid()

    up_ratio = up.Clone()
    up_ratio.Divide(nominal)

    ratio_style = "P"
    # if s.name().lower() in alternateSamples:
    #     ratio_style += "E"
    # else:
    #     ratio_style += "hist"

    up_ratio.GetXaxis().SetLabelSize(0.02 / 0.333)
    up_ratio.GetXaxis().SetTitleSize(0.03 / 0.333)
    up_ratio.GetXaxis().SetLabelOffset(0.05)
    up_ratio.GetXaxis().SetTitleOffset(1.5)
    up_ratio.GetXaxis().SetTitle(title)
    up_ratio.GetYaxis().SetLabelSize(0.02 / 0.333)
    up_ratio.GetYaxis().SetTitleSize(0.03 / 0.333)
    up_ratio.GetYaxis().SetTitleOffset(1.7 * 0.333)
    up_ratio.GetYaxis().SetTitle("")
    up_ratio.GetYaxis().SetNdivisions(502, True)
    up_ratio.GetYaxis().SetRangeUser(0.5, 1.5)

    up_ratio.SetLineColor(ROOT.TColor.GetColor('#468966'))
    up_ratio.SetMarkerColor(ROOT.TColor.GetColor('#468966'))
    up_ratio.SetMarkerStyle(20)
    up_ratio.SetMarkerSize(0.6)
    up_ratio.Draw(ratio_style)

    line = ROOT.TLine(up_ratio.GetXaxis().GetBinLowEdge(1), 1, up_ratio.GetXaxis().GetBinUpEdge(up_ratio.GetXaxis().GetLast()), 1)
    line.Draw("same")

    up_ratio.Draw(ratio_style + "same")

    down_ratio = down.Clone()
    down_ratio.Divide(nominal)

    down_ratio.SetLineColor(ROOT.TColor.GetColor('#8E2800'))
    down_ratio.SetMarkerColor(ROOT.TColor.GetColor('#8E2800'))
    down_ratio.SetMarkerStyle(20)
    down_ratio.SetMarkerSize(0.6)
    down_ratio.Draw(ratio_style + "same")

    # Look for min and max of ratio and zoom accordingly
    ratio_max = -100
    ratio_min = 100
    for i in range(1, up_ratio.GetNbinsX() + 1):
        if up_ratio.GetBinContent(i) == 0 or down_ratio.GetBinContent(i) == 0:
            continue
        ratio_max = max(ratio_max, up_ratio.GetBinContent(i), down_ratio.GetBinContent(i))
        ratio_min = min(ratio_min, up_ratio.GetBinContent(i), down_ratio.GetBinContent(i))

    def halfRound(r):
        """Round up to closest half-decimal:
            0.04 -> 0.05
            0.009 -> 0.01
        """
        power = 0
        while r < 1:
            r *= 10
            power -= 1
        if r >= 5:
            return pow(10., power+1)
        else:
            return 5. * pow(10., power)


    # Symetrize
    # ratio_range = halfRound(max(abs(ratio_max - 1), abs(1 - ratio_min)))
    # print(f"min: {ratio_min}, rounded: {halfRound(1-ratio_min)}")
    # print(f"max: {ratio_max}, rounded: {halfRound(ratio_max - 1)}")
    # up_ratio.GetYaxis().SetRangeUser(max(0, 1 - ratio_range), 1 + ratio_range)
    # up_ratio.GetYaxis().SetRangeUser(1 - halfRound(1 - ratio_min), 1 + halfRound(ratio_max - 1))
    up_ratio.GetYaxis().SetRangeUser(.95 * ratio_min, 1.05 * ratio_max)
    up_ratio.GetYaxis().SetNdivisions(210)
    up_ratio.GetYaxis().SetTitle('Ratio')

    c.cd()
    l = ROOT.TLegend(0.20, 0.79, 0.50, 0.92)
    l.SetTextFont(42)
    l.SetFillColor(ROOT.kWhite)
    l.SetFillStyle(0)
    l.SetBorderSize(0)

    l.AddEntry(nominal, "Nominal")
    l.AddEntry(up, "+1 std. deviation")
    l.AddEntry(down, "-1 std. deviation")
    l.Draw("same")

    text = f"systematic: {syst}, {proc}"
    syst_text = ROOT.TLatex(0.16, 0.96, text)
    syst_text.SetNDC(True)
    syst_text.SetTextFont(40)
    syst_text.SetTextSize(0.03)
    syst_text.Draw("same")


    name = "%s_%s_%s.pdf" % (title, proc, syst)
    name = "%s_%s_%s.png" % (title, proc, syst)
    c.SaveAs(os.path.join(output, name))

# Options

parser = argparse.ArgumentParser(description='Draw systematics')
parser.add_argument('-i', '--input', type=str, help='Input YML file')
parser.add_argument('-o', '--output', type=str, default ='sysvars', help='Output directory')
parser.add_argument('-p', '--plots', nargs='*', help='Restrict to those plots - use all by default')
parser.add_argument('-f', '--files', nargs='*', help='Restrict to those files - use all by default')
parser.add_argument('-s', '--syst', nargs='*', help='Restrict to those systematics - use all by default')

options = parser.parse_args()

if not os.path.isdir(options.output):
    os.makedirs(options.output)

with open(options.input) as _f:
    plotConfig = yaml.load(_f, Loader=yaml.FullLoader)

systematics = plotConfig["systematics"]
print ( systematics )
files = [ f for f in plotConfig["files"] if plotConfig["files"][f]["type"] == "mc" ]
plots = plotConfig["plots"]

setTDRStyle()

for proc in files:
    if options.files:
        if proc not in options.files:
            continue

    _tf = ROOT.TFile.Open(os.path.join(os.path.dirname(options.input), plotConfig["configuration"]["root"], proc))
    print (_tf)
    for plot in plots:
        if options.plots:
            if plot not in options.plots:
                continue
        #if "DYweight" in plot or "DY_weight" in plot or "dxy" in plot or "dz" in plot or "miniPFRelIso_all" in plot or "sip3d" in plot or "Yield" in plot: # for now I don't have any sys for DY-rewighting 
         #   continue
        nominal = _tf.Get(plot)

        for syst in systematics:
            if options.syst:
                if syst not in options.syst:
                    continue

            up = _tf.Get(plot + "__" + syst + "up")
            print( plot + "__" + syst + "up")
            if not (up and up.InheritsFrom("TH1")):
                print(f"Could not find up variation for systematic {syst}, using nominal")
                up = nominal
            down = _tf.Get(plot + "__" + syst + "down")
            if not (down and down.InheritsFrom("TH1")):
                print(f"Could not find down variation for systematic {syst}, using nominal")
                down = nominal

            drawSystematic(nominal, up, down, plot, syst, proc.split(".root")[0], plots[plot], options.output)

    _tf.Close()
