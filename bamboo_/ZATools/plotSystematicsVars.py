#! /bin/env python
import os, sys, argparse
import yaml, json
import subprocess
import glob
import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True

# to prevent pyroot to hijack argparse we need to go around
tmpargv  = sys.argv[:] 
sys.argv = []
sys.argv = tmpargv

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/')
import HistogramTools as HT
import utils as utils
logger = utils.ZAlogger(__name__)

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/')
import Harvester as H
import Constants as Constants

# For systematics computed with alternate samples, draw statistical uncertainties on ratios
alternateSamples = ['isr', 'fsr', 'tune', 'hdamp']

def halfRound(r):
    """Round up to closest half-decimal:
        0.04  -> 0.05
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

def beautify(s, era):
    if s == f'summed_normalized_{era}DY_samples':
        return 'Drell-Yan'
    if s == f'summed_normalized_{era}ttbar_samples':
        return r't#bar{t}'
    if s == f'summed_normalized_{era}SingleTop_samples':
        return 'Single-Top'
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


def get_mergedBKG_processes(inputs=None, Cfg=None, inDir=None, outDir=None, era =None, normalize=True):
    files= {'mc':{'DY':[], 
                  'ttbar':[],
                  'SingleTop':[]}
            }
    s = 'normalized_' if normalize else ''

    for rf in inputs:
        smp   = rf.split('/')[-1]
        smpNm = smp.replace('.root','')
        if smpNm.startswith('__skeleton__'):
            continue
        if any(x in smpNm for x in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon']):
            continue
        if any(x in smpNm for x in ['AToZH', 'HToZA', 'GluGlu']):
            continue

        year   = Cfg['files'][smp]["era"]
        lumi   = Cfg["configuration"]["luminosity"][year]
        xsc    = Cfg['files'][smp]["cross-section"]
        genevt = Cfg['files'][smp]["generated-events"]
       
        rf = os.path.join(outDir, f'summed_{s}processes', rf)

        if any( x in smpNm for x in ['DYJetsToLL']):
            files['mc']['DY'].append(rf)
        elif any( x in smpNm for x in ['TTTo2L2Nu', 'ttbar']):
            files['mc']['ttbar'].append(rf)
        elif any( x in smpNm for x in ['ST']):
            files['mc']['SingleTop'].append(rf)
        
        smpScale = (lumi * xsc )/ genevt

        if normalize:
            resultsFile    = HT.openFileAndGet(os.path.join(inDir, smp), mode="READ")
            normalizedFile = HT.openFileAndGet(os.path.join(outDir, f'summed_{s}processes', smp), "recreate")
            for hk in resultsFile.GetListOfKeys():
                hist  = hk.ReadObj()
                if not hist.InheritsFrom("TH1"):
                    continue
                hist.Scale(smpScale)
                hist.Write()
            normalizedFile.Write()
            resultsFile.Close()
    
    print( files )
    for k, val in files['mc'].items():
        haddCmd = ["hadd", "-f", os.path.join(outDir, f'summed_{s}processes', f"summed_{s}{era}{k}_samples.root")]+val
        try:
            logger.info("running {}".format(" ".join(haddCmd)))
            subprocess.check_call(haddCmd)#, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            logger.error("Failed to run {0}".format(" ".join(haddCmd)))


def get_listofsystematics(directory):
    systematics = []
    files = glob.glob(os.path.join(directory,"*.root"))
    for i, f in enumerate(files):
        F = ROOT.TFile(f)
        for key in F.GetListOfKeys():
            if not 'TH1' in key.GetClassName():
                continue
            if not '__' in key.GetName():
                continue
            if not 'down' in key.GetName() :#or not 'up' in key.GetName():
                continue
            syst = key.GetName().replace('__METCut_NobJetER', '_METCut_NobJetER')
            syst = syst.split('__')[1].replace('up','').replace('down','')
            syst = syst.replace('pile_', 'pileup_')
            if syst not in systematics:
                systematics.append(syst)
        F.Close()
    return systematics

def drawSystematic(nominal, up, down, title, era, syst, proc, plotOpts, output):

    c = ROOT.TCanvas("c", "c", 800, 800)

    hi_pad = ROOT.TPad("pad_hi", "",  0., 0.33333, 1, 1)
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
    up.SetLineColor(ROOT.TColor.GetColor('#ce7e00'))
    up.GetYaxis().SetLabelSize(0.02 / 0.666)
    up.GetYaxis().SetTitleSize(0.03 / 0.666)
    up.GetYaxis().SetTitleOffset(1.7 * 0.666)
    up.GetYaxis().SetTitle("Events")
    up.GetXaxis().SetLabelSize(0)
    up.Draw("hist")

    nominal.SetLineWidth(2)
    nominal.SetLineStyle(2)
    nominal.SetFillColor(ROOT.TColor.GetColor('#d0e0e3'))
    nominal.Draw("hist same")

    up.Draw("hist same")

    down.SetLineWidth(2)
    down.SetLineColor(ROOT.TColor.GetColor('#351c75'))
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

    ratio_style = "ep"
    # if s.name().lower() in alternateSamples:
    #     ratio_style += "E"
    # else:
    #     ratio_style += "hist"

    up_ratio.GetXaxis().SetLabelSize(0.02 / 0.333)
    up_ratio.GetXaxis().SetTitleSize(0.08)
    up_ratio.GetXaxis().SetLabelOffset(0.05)
    up_ratio.GetXaxis().SetTitleOffset(1.5)
    up_ratio.GetXaxis().SetTitle(title)
    up_ratio.GetYaxis().SetLabelSize(0.02 / 0.333)
    up_ratio.GetYaxis().SetTitleSize(0.03 / 0.333)
    up_ratio.GetYaxis().SetTitleOffset(1.7 * 0.333)
    up_ratio.GetYaxis().SetTitle("")
    up_ratio.GetYaxis().SetNdivisions(502, True)
    up_ratio.GetYaxis().SetRangeUser(0.5, 1.5)

    up_ratio.SetLineColor(ROOT.TColor.GetColor('#ce7e00'))
    up_ratio.SetMarkerColor(ROOT.TColor.GetColor('#ce7e00'))
    up_ratio.SetMarkerStyle(21)
    #up_ratio.SetMarkerSize(0.6)
    up_ratio.Draw(ratio_style)

    line = ROOT.TLine(up_ratio.GetXaxis().GetBinLowEdge(1), 1, up_ratio.GetXaxis().GetBinUpEdge(up_ratio.GetXaxis().GetLast()), 1)
    line.Draw("same")

    up_ratio.Draw(ratio_style + "same")

    down_ratio = down.Clone()
    down_ratio.Divide(nominal)
    down_ratio.SetLineColor(ROOT.TColor.GetColor('#351c75'))
    down_ratio.SetMarkerColor(ROOT.TColor.GetColor('#351c75'))
    down_ratio.SetMarkerStyle(21)
    #down_ratio.SetMarkerSize(0.6)
    down_ratio.Draw(ratio_style + "same")

    
    # !!! 
    #nominal_ratio = down.Clone()
    #down_ratio.Divide(nominal)
    #nominal_ratio.SetFillColor(ROOT.TColor.GetColor('#d0e0e3'))
    #nominal_ratio.SetMarkerColor(ROOT.TColor.GetColor('#d0e0e3'))
    #nominal_ratio.SetMarkerStyle(21)
    #nominal_ratio.Draw(ratio_style + "same")
    
    # Look for min and max of ratio and zoom accordingly
    ratio_max = -100
    ratio_min = 100
    for i in range(1, up_ratio.GetNbinsX() + 1):
        if up_ratio.GetBinContent(i) == 0 or down_ratio.GetBinContent(i) == 0:
            continue
        ratio_max = max(ratio_max, up_ratio.GetBinContent(i), down_ratio.GetBinContent(i))
        ratio_min = min(ratio_min, up_ratio.GetBinContent(i), down_ratio.GetBinContent(i))

    # Symetrize
    # ratio_range = halfRound(max(abs(ratio_max - 1), abs(1 - ratio_min)))
    # print(f"min: {ratio_min}, rounded: {halfRound(1-ratio_min)}")
    # print(f"max: {ratio_max}, rounded: {halfRound(ratio_max - 1)}")
    # up_ratio.GetYaxis().SetRangeUser(max(0, 1 - ratio_range), 1 + ratio_range)
    # up_ratio.GetYaxis().SetRangeUser(1 - halfRound(1 - ratio_min), 1 + halfRound(ratio_max - 1))
    
    up_ratio.GetYaxis().SetRangeUser(.95 * ratio_min, 1.05 * ratio_max)
    #up_ratio.GetYaxis().SetNdivisions(210)
    up_ratio.GetYaxis().SetTitle('Ratio')

    c.cd()
    #l = ROOT.TLegend(0.20, 0.79, 0.50, 0.92)
    #l = ROOT.TLegend(0.4,0.6,0.89,0.89)
    l = ROOT.TLegend(0.62, 0.79, 0.89, 0.92)
    l.SetTextSize(0.02)
    #l.SetTextFont(40)
    l.SetFillColor(ROOT.kWhite)
    l.SetFillStyle(0)
    l.SetBorderSize(0)

    l.SetHeader("%s, %s"%(syst, beautify(proc, era)))
    l.AddEntry(nominal, "Nominal")
    l.AddEntry(up, "up variation")
    l.AddEntry(down, "down variation")
    l.Draw("same")

    syst_text = ROOT.TLatex(0.16, 0.96, "CMS Preliminary")
    syst_text.SetNDC(True)
    syst_text.SetTextFont(40)
    syst_text.SetTextSize(0.03)
    syst_text.Draw("same")
   
    lumi = ROOT.TLatex(0.7, 0.96, "%s fb^{-1} (13 TeV)" %format(Constants.getLuminosity(era)/1000.,'.2f'))
    lumi.SetNDC(True)
    syst_text.SetTextFont(40)
    lumi.SetTextSize(0.03)
    lumi.Draw("same")

    name = "%s_%s.pdf" % (title, syst)
    name = "%s_%s.png" % (title, syst)
    
    proc_output = os.path.join(options.output, proc)
    if not os.path.isdir(proc_output):
        os.makedirs(proc_output)
    c.SaveAs(os.path.join(proc_output, name))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Draw systematics')
    parser.add_argument('-i', '--input' , type=str , help='Input to bamboo directory'  , required=True)
    parser.add_argument('-o', '--output', type=str , help='Output directory', default ='sysvars')
    parser.add_argument('-e', '--era'   , type=str , help='', required=True)
    parser.add_argument('-m', '--merge' , action='store_true', default=False , help='merge bkg processes instead of going through them seperatly')
    parser.add_argument('-n', '--normalize', action='store_true', default=True, help='normalize mc samples')
    parser.add_argument('-p', '--plots' , nargs='*', help='Restrict to those plots - use all by default')
    parser.add_argument('-f', '--files' , nargs='*', help='Restrict to those files - use all by default')
    parser.add_argument('-s', '--syst'  , nargs='*', help='Restrict to those systematics - use all by default')
    
    options = parser.parse_args()

    s = 'normalized_' if options.normalize else ''
    
    if not os.path.isdir(options.output):
        os.makedirs(options.output)
    
    with open(os.path.join(options.input, 'plots.yml')) as _f:
        plotConfig = yaml.load(_f, Loader=yaml.FullLoader)
    
    systematics = plotConfig["systematics"]
    with open(os.path.join(options.output, "systematics.json"), 'w') as _f:
        json.dump(systematics, _f, indent=4)
    logger.info( f'found systematics saved in : {options.output}/systematics.json' )
    # use the sys we get from the histogram 
    found_systematics = get_listofsystematics(os.path.join(options.input, 'results/'))
    print( found_systematics )
    
    ignore_systematics = []#['jer2', 'unclustEn', 'jer4', 'jer3', 'L1PreFiring', 'jer0', 'jer5', 'jer1', 'jmr', 'jms', 'HLTZvtx_2016postVFP', 'HLTZvtx_2016', 'HLTZvtx_2016preVFP']

    files = [ f for f in plotConfig["files"] if plotConfig["files"][f]["type"] == "mc" ]
    if options.merge:

        if not os.path.isdir(os.path.join(options.output, f'summed_{s}processes')):
            os.makedirs(os.path.join(options.output, f'summed_{s}processes'))

            files = get_mergedBKG_processes(inputs=files, Cfg=plotConfig, inDir= os.path.join(options.input, 'results/'), outDir=options.output, era =options.era, normalize=options.normalize)
        else:
            logger.info(f'{options.output}/summed_{s}processes/ already exist and not empty!\n'
            '\tScale and hadd steps will be skipped \n'
            '\tif you have an updated version of files OR you want to rerun the steps above :\n'
           f'\tplease remove {options.output}/summed_{s}processes/ and start over!\n' )
        
        files = glob.glob(os.path.join(options.output, f'summed_{s}processes', f'summed_{s}{options.era}*'))
    
    plots = plotConfig["plots"]
    
    HT.setTDRStyle()
    
    for proc in files:
        if options.files:
            if proc not in options.files:
                continue
        
        if options.merge: 
            _tf = ROOT.TFile.Open(proc)
        else:
            _tf = ROOT.TFile.Open(os.path.join(os.path.dirname(options.input), plotConfig["configuration"]["root"], proc))
        
        logger.info(f'working on {_tf}')
        for plot in plots:
            if options.plots:
                if plot not in options.plots:
                    continue
            if not plot.startswith('DNNOutput_ZAnode_'):
                continue
            if not 'resolved' in plot:
                continue
            if 'ElMu' in plot:
                continue
            if not 'gg_fusion' in plot:
                continue
            
            nominal = _tf.Get(plot)
            for syst in found_systematics:
                if options.syst:
                    if syst not in options.syst:
                        continue
                if syst in ignore_systematics:
                    continue
                
                up = _tf.Get(plot + "__" + syst + "up")
                if not (up and up.InheritsFrom("TH1")):
                    logger.error(f"\tCould not find up variation for systematic {syst}, using nominal")
                    continue
                down = _tf.Get(plot + "__" + syst + "down")
                if not (down and down.InheritsFrom("TH1")):
                    logger.error(f"\tCould not find down variation for systematic {syst}, using nominal")
                    continue
                
                cms_syst = H.CMSNamingConvention(syst, '2016')
                drawSystematic(nominal, up, down, plot, options.era, cms_syst, proc.split('/')[-1].split(".root")[0], plots[plot], options.output)
        _tf.Close()
