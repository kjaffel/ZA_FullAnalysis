#! /usr/bin/env python
import CombineHarvester.CombineTools.plotting as plot 
import argparse
import math
import os, sys
import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Likelihood Fits and Scans')
    parser.add_argument('-f', '--file', action='store', type=str, dest='file', help='Path to the ROOT file created by combine harvester', required=True)
    parser.add_argument('-n', '--name', action='store', type=str, dest='name', help='name of the signal cats.', required=True)
    parser.add_argument('--y-axis-max', default=None, help="""y-axis max""")
    parser.add_argument('--y-axis-min', default=None, help="""y-axis min""")
    parser.add_argument('--x-axis-max', default=None, help="""x-axis max""")
    parser.add_argument('--x-axis-min', default=None, help="""x-axis min""")
    parser.add_argument('--sm-exp', action='store_true', default=False, help='', required=False)
    parser.add_argument('--bg-exp', action='store_true', default=False, help='', required=False)
    parser.add_argument('--mass', default='', help="""Mass label on the plot""")
    parser.add_argument('--cms-sub', default='Internal', help="""Text below the CMS logo""")
    parser.add_argument('--title-right', default='', help="""Right header text above the frame""")
    parser.add_argument('--title-left', default='', help="""Left header text above the frame""")

    args  = parser.parse_args()
    
    #Create canvas and TH2D for each component
    plot.ModTDRStyle(width=600, l=0.12)
    ROOT.gStyle.SetNdivisions(510, 'XYZ')
    plot.SetBirdPalette()
    canv = ROOT.TCanvas(args.name, args.name)
    pads = plot.OnePad()

    #limit = plot.MakeTChain([args.file], 'limit')    
    F = ROOT.TFile.Open(args.file)
    limit = F.Get('limit')
    graph = plot.TGraph2DFromTree(
                limit, 'r_ggH', 'r_bbH', '2*deltaNLL', 'quantileExpected > -0.5 && deltaNLL > 0 && deltaNLL < 1000')
    best = plot.TGraphFromTree(
                limit, 'r_ggH', 'r_bbH', 'deltaNLL == 0')

    plot.RemoveGraphXDuplicates(best)
    hists = plot.TH2FromTGraph2D(graph, method='BinCenterAligned')
    plot.fillTH2(hists, graph)
    
    if args.bg_exp:
        limit_bg = plot.MakeTChain(args.bg_exp, 'limit')
        best_bg  = plot.TGraphFromTree( limit_bg, args.x_var, args.y_var, 'deltaNLL == 0')
        plot.RemoveGraphXDuplicates(best_bg)
    if args.sm_exp:
        limit_sm = plot.MakeTChain(args.sm_exp, 'limit')
        best_sm  = plot.TGraphFromTree(limit_sm, args.x_var, args.y_var, 'deltaNLL == 0')
        plot.RemoveGraphXDuplicates(best_sm)

    hists.SetMaximum(6)
    hists.SetMinimum(0)
    hists.SetContour(255)
    
    #Set x and y axis maxima:
    if args.y_axis_max is not None:
        y_axis_max = float(args.y_axis_max)
    else:
        y_axis_max = float(hists.GetYaxis().GetXmax())

    if args.y_axis_min is not None:
        y_axis_min = float(args.y_axis_min)
    else:
        y_axis_min = float(hists.GetYaxis().GetXmin())

    
    if args.x_axis_max is not None:
        x_axis_max = float(args.x_axis_max)
    else:
        x_axis_max = float(hists.GetXaxis().GetXmax())

    if args.x_axis_min is not None:
        x_axis_min = float(args.x_axis_min)
    else:
        x_axis_min = float(hists.GetXaxis().GetXmin())

    axis = ROOT.TH2D(hists.GetName(),hists.GetName(),hists.GetXaxis().GetNbins(),x_axis_min,x_axis_max,hists.GetYaxis().GetNbins(),y_axis_min,y_axis_max)
    axis.Reset()
    axis.GetXaxis().SetTitle('r_ggH')
    axis.GetXaxis().SetLabelSize(0.025)
    axis.GetYaxis().SetLabelSize(0.025)
    axis.GetYaxis().SetTitle('r_bbH')

    cont_0p05   = plot.contourFromTH2(hists, ROOT.Math.chisquared_quantile_c(1 - 0.05, 2),   20, frameValue=20)
    cont_0p1    = plot.contourFromTH2(hists, ROOT.Math.chisquared_quantile_c(1 - 0.10, 2),   20, frameValue=20)
    cont_1sigma = plot.contourFromTH2(hists, ROOT.Math.chisquared_quantile_c(1 - 0.6827, 2), 20, frameValue=20)
    cont_2sigma = plot.contourFromTH2(hists, ROOT.Math.chisquared_quantile_c(1 - 0.9545, 2), 20, frameValue=20)
    
    
    c2=ROOT.TCanvas()
    hists.Draw("COLZ")
    c2.SaveAs("{}.png".format(args.name))
    
    if args.sm_exp or args.bg_exp:
        legend = plot.PositionedLegend(0.5, 0.25, 3, 0.015)
    else:
         legend = plot.PositionedLegend(0.3, 0.2, 3, 0.015)
    
    legend.SetFillStyle(0)
    
    pads[0].cd()
    axis.Draw()
    for i, p in enumerate(cont_2sigma):
          p.SetLineStyle(1)
          p.SetLineWidth(2)
          p.SetLineColor(ROOT.kBlack)
          p.SetFillColor(ROOT.kBlue-8)
          p.SetFillStyle(1001)
          p.Draw("F SAME")
          p.Draw("L SAME")
          legend.AddEntry(cont_2sigma[0], "95% CL", "F")
    
    for i, p in enumerate(cont_1sigma):
          p.SetLineStyle(1)
          p.SetLineWidth(2)
          p.SetLineColor(ROOT.kBlack)
          p.SetFillColor(ROOT.kBlue-10)
          p.SetFillStyle(1001)
          p.Draw("F SAME")
          p.Draw("L SAME")
          legend.AddEntry(cont_1sigma[0], "68% CL", "F")
    
    #for i, p in enumerate(cont_0p1):
    #      p.SetLineStyle(1)
    #      p.SetLineWidth(2)
    #      p.SetLineColor(ROOT.kBlack)
    #      p.SetFillColor(ROOT.kGreen+2)
    #      p.SetFillStyle(1001)
    #      p.Draw("F SAME")
    #      p.Draw("L SAME")
    #      legend.AddEntry(cont_0p1[0], "10% CL", "F")
    #
    #for i, p in enumerate(cont_0p05):
    #      p.SetLineStyle(1)
    #      p.SetLineWidth(2)
    #      p.SetLineColor(ROOT.kBlack)
    #      p.SetFillColor(ROOT.kGreen)
    #      p.SetFillStyle(1001)
    #      p.Draw("F SAME")
    #      p.Draw("L SAME")
    #      legend.AddEntry(cont_0p05[0], "5% CL", "F")
    
    best.SetMarkerStyle(34)
    best.SetMarkerSize(3)
    best.Draw("P SAME")
    legend.AddEntry(best, "Best fit", "P")
    if args.sm_exp:
        best_sm.SetMarkerStyle(33)
        best_sm.SetMarkerColor(1)
        best_sm.SetMarkerSize(3.0)
        best_sm.Draw("P SAME")
        legend.AddEntry(best_sm, "Expected for 125 GeV SM Higgs", "P")
    if args.bg_exp:
        best_bg.SetMarkerStyle(33)
        best_bg.SetMarkerColor(46)
        best_bg.SetMarkerSize(3)
        best_bg.Draw("P SAME")
        legend.AddEntry(best_bg, "Expected for background only", "P")
    
    
    if args.mass:
        legend.SetHeader("m_{#phi} = "+args.mass+" GeV")
    legend.Draw("SAME")
    if args.sm_exp:
        overlayLegend,overlayGraphs = plot.getOverlayMarkerAndLegend(legend, {legend.GetNRows()-1 : best_sm}, {legend.GetNRows()-1 : {"MarkerColor" : 2}}, markerStyle="P")
    
    plot.DrawCMSLogo(pads[0], 'CMS', args.cms_sub, 11, 0.045, 0.035, 1.2, '', 1.0)
    plot.DrawTitle(pads[0], args.title_right, 3)
    plot.DrawTitle(pads[0], args.title_left, 1)
    plot.FixOverlay()
    if args.sm_exp:
        best_sm.Draw("P SAME")
        for overlayGraph in overlayGraphs:
            overlayGraph.Draw("P SAME")
        overlayLegend.Draw("SAME")
    canv.Print('.pdf')
    canv.Print('.png')
    canv.Close()
    
    #if debug is not None:
    #    debug.Close()
    
    #if args.likelihood_database:
    #    output_file = open(args.output+".out","w")
    #    for i in range(0,limit.GetEntries()):
    #        limit.GetEntry(i)
    #        ggH = limit.r_ggH
    #        bbH = limit.r_bbH
    #        deltanll = limit.deltaNLL
    #        output_file.write("%(ggH)f %(bbH)f %(deltanll)f \n"%vars())
    #    output_file.close()
    #
    #
    #ROOT.gStyle.SetOptFit(1111)
    #C = ROOT.TCanvas(args.name,args.name,500,400) 
    #F = ROOT.TFile.Open(args.file)
    #tree = F.Get('limit')
    #tree.Draw("2*deltaNLL:r_ggH:r_bbH>>h(44,0,10,44,0,4)","2*deltaNLL<10","prof colz")
    #tree.Draw("r_ggH:r_bbH","quantileExpected == -1","P same")
    #h = ROOT.gROOT.FindObject("h")
    #if not h:
    #    print('Error {} - in file : {}'.format(args.name, args.file))
    #else:
    #    best_fit = deepcopy(h)
    #F.Close()
    #
    ##best_fit.SetMarkerSize(3)
    ##best_fit.SetMarkerStyle(34)
    ##best_fit.Draw("p same")
    #C.cd()
    #best_fit.Draw("H same")
    #C.Print("{}.png".format(args.name))
    #C.Clear()
