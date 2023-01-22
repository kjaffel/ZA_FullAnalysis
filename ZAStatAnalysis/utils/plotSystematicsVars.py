#! /bin/env python
import os, sys, argparse
import yaml, json
import subprocess
import glob
import collections
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

H.splitJECs =True
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
    if s == 'lumi_13TeV':
        return 'Luminosity'
    if s == 'ttbar_modeling':
        return r'$\ttbar$ modeling'
    if s == 'ttbar_xsec':
        return r'$\ttbar$ cross-section'
    if s == 'dy_modeling':
        return r'Drell-Yan modeling'
    if s == 'DY_xsec':
        return r'Drell-Yan cross-section'
    if s == 'SingleTop_modeling':
        return r'Single top modeling'
    if s == 'SingleTop_xsec':
        return r'Single top cross-section'
    if s == 'MC_stat':
        return 'MC stat.'
    if 'QCDscale' in s:
        return 'QCD scale'
    return s


def get_mergedBKG_processes(inputs=None, Cfg=None, inDir=None, outDir=None, era =None, normalize=False):
    
    groups = Cfg['groups'].keys()
    
    split_gp = {}
    for gp in groups:
        split_gp[gp]  = []
    #split_gp['total'] = []

    files= {'mc': split_gp,
            'signal': collections.defaultdict(dict),
            }
    
    s = 'normalized_' if normalize else ''
    for rf in inputs:
        smp   = rf.split('/')[-1]
        smpNm = smp.replace('.root','')
        
        if not os.path.exists(os.path.join(inDir, smp)):
            continue

        if smpNm.startswith('__skeleton__'):
            continue
        
        if any(x in smpNm for x in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon', 'SingleElectron']):
            continue
        
        if not era == "fullrun2":
            if not H.EraFromPOG(era).replace('-','') in smp:
                continue
        
        year   = Cfg['files'][smp]["era"]
        lumi   = Cfg["configuration"]["luminosity"][year]
        xsc    = Cfg['files'][smp]["cross-section"]
        genevt = Cfg['files'][smp]["generated-events"]
        
        smpScale = (lumi * xsc )/ genevt
        
        if normalize:
            rf = os.path.join(outDir, f'summed_{s}processes', rf)
        else:
            rf = os.path.join(inDir, rf)

        if Cfg['files'][smp]['type'] == 'mc':
            files['mc'][Cfg['files'][smp]['group']].append(rf)
            #files['mc']['total'].append(rf)
        else:
            if Cfg['files'][smp]['type'] == 'signal':
                
                br = Cfg['files'][smp]["branching-ratio"]
                smpScale *= br 
                
                #signal_smp = smpNm.replace('_preVFP', '').replace('_postVFP', '')
                if not smp in files['signal'].keys():
                    files['signal'][smp] = []
                files['signal'][smp].append(rf)
        
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
    
    for group in ['mc', 'signal']:
        for k, val in files[group].items():
            if not val or len(val) ==1: 
                continue
            r_f = f"summed_{s}{era}{k}_samples.root" if group == 'mc' else k
            haddCmd = ["hadd", "-f", os.path.join(outDir, f'summed_{s}processes', r_f)]+val
            if group == 'signal':
                print( haddCmd )
                exit()
            try:
                logger.info("running {}".format(" ".join(haddCmd)))
                subprocess.check_call(haddCmd)#, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                logger.error("Failed to run {0}".format(" ".join(haddCmd)))


def drawSystematic(nominal, up, down, title, era, syst, proc, output):

    name = "%s_%s.pdf" % (title, syst)
    name = "%s_%s.png" % (title, syst)
    
    c = ROOT.TCanvas("%s_%s"% (title, syst), "%s_%s"% (title, syst), 900, 800)
    #c.SetLogy()

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
    #l = ROOT.TLegend(0.62, 0.79, 0.89, 0.92)
    l = ROOT.TLegend(0.3, 0.79, 0.89, 0.92)
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

    
    proc_output = os.path.join(options.output, proc)
    if not os.path.isdir(proc_output):
        os.makedirs(proc_output)
    c.SaveAs(os.path.join(proc_output, name))
    del c

def getPlotList(fh):
    keys = fh.GetListOfKeys()
    keys = [ k for k in keys if not "__" in k.GetName() ]
    keys = [ k.GetName() for k in keys if "TH" in k.GetClassName() ]
    return keys


def scale(hist, plotConfig, proc):
    procCfg = plotConfig["files"][proc]
    era = procCfg["era"]
    lumi = plotConfig["configuration"]["luminosity"][era]
    sf = lumi * procCfg["cross-section"] / procCfg["generated-events"]
    hist.Scale(sf)


def proj(hist):
    if hist.InheritsFrom("TH2") or hist.InheritsFrom("TH3"):
        return hist.ProjectionX(hist.GetName() + "_proj")
    else:
        return hist


def get_process(f, plotConfig, era, merge=False):
    fNm = f.split('/')[-1]
    if 'prod' in plotConfig["files"][fNm].keys(): # signal 
        return plotConfig["files"][fNm]['prod']
    else:
        if merge: # 'summed_normalized_2017others_samples'
            group = fNm.split(era)[-1].split('_')[0]
            return group
        else:    
            if 'group' in plotConfig["files"][fNm].keys():
                return plotConfig["files"][fNm]["group"]


def getSystList(fh, nom):
    keys = fh.GetListOfKeys()
    nomName = nom.GetName()
    keys = [ k.GetName() for k in keys if k.GetName().startswith(nomName + "__") ]
    keys = [ k.split("__")[1] for k in keys ]
    keys = [ k.split("up")[0] for k in keys ]
    keys = [ k.split("down")[0] for k in keys ]
    return set(keys)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Draw systematics')
    
    parser.add_argument('-i', '--input' , type=str , help='Input to bamboo directory results dir', required=True)
    parser.add_argument('-o', '--output', type=str , help='Output directory', default ='sysvars')
    parser.add_argument('-y', '--yml'   , help='plotit yml files', required=True) 
    parser.add_argument('-e', '--era'   , type=str , help='', choices=['2016-preVFP', '2016-postVFP', '2017', '2018'], required=True)
    parser.add_argument('-p', '--plots' , nargs='*', help='Restrict to those plots - use all by default')
    parser.add_argument('-f', '--files' , nargs='*', help='Restrict to those files - use all by default')
    parser.add_argument('-s', '--syst'  , nargs='*', help='Restrict to those systematics - use all by default')
    parser.add_argument('-m', '--merge'    , action='store_true', default=False, help='merge bkg processes instead of going through them seperatly')
    parser.add_argument('-n', '--normalize', action='store_true', default=True, help='normalize mc samples by  xsc * lumi/ sum_genEvts')
    
    options = parser.parse_args()

    if not os.path.isdir(options.output):
        os.makedirs(options.output)
    
    with open(options.yml) as _f:
        plotConfig = yaml.load(_f, Loader=yaml.FullLoader)
    
    all_files  = [ f for f in plotConfig["files"] if plotConfig["files"][f]["type"] == "mc"]
    if options.era !='fullrun2':
        all_files  = [  f for f in all_files if plotConfig["files"][f]["era"] == options.era]
    elif options.era == '2016':
        all_files  = [  f for f in all_files if plotConfig["files"][f]["era"] in ['2016-preVFP', '2016-postVFP']]

    # I am assuming you will be able to get full list of sys from these 2 
    files_tolistsysts  = [ [ f'{options.input}/{f}' for f in all_files if plotConfig["files"][f]["group"] == "ttbar"][0] , 
                           [ f'{options.input}/{f}' for f in all_files if plotConfig["files"][f]["group"] == "DY" ][0] 
                         ]
    
    _files_tolistsysts = []
    if options.era =='fullrun2':
        for e in ['_UL16postVFP.root', '_UL16preVFP.root', '_UL17.root','_UL18.root']:
            for f in files_tolistsysts:
                pNm = options.input
                fNm = f.split('/')[-1].split('_UL')[0]
                _files_tolistsysts += [ pNm + fNm +e]
    else:
        _files_tolistsysts = files_tolistsysts

    all_files += [ f for f in plotConfig["files"] if plotConfig["files"][f]["type"] == "signal" ]
    if options.era =='fullrun2': files = [ f for f in all_files ]
    elif options.era == '2016': files = [ f for f in all_files if any(x in f for x in ['_UL16preVFP', '_UL16postVFP'])]
    else: files = [ f for f in all_files if H.EraFromPOG(options.era).replace('-','') in f]
    
    print( options.input )
    if options.merge:
        s = 'normalized_' if options.normalize else ''
        if not os.path.isdir(os.path.join(options.output, f'summed_{s}processes')):
            os.makedirs(os.path.join(options.output, f'summed_{s}processes'))
            get_mergedBKG_processes(inputs=files, Cfg=plotConfig, inDir=options.input, outDir=options.output, era =options.era, normalize=options.normalize)
        else:
            logger.info(f'{options.output}/summed_{s}processes/ already exist and not empty!\n'
            '\tScale and hadd steps will be skipped \n'
            '\tif you have an updated version of files OR you want to rerun the steps above :\n'
           f'\tplease remove {options.output}/summed_{s}processes/ and start over!\n' )
        
        files  = glob.glob(os.path.join(options.output, f'summed_{s}processes', f'summed_{s}{options.era}*'))
        files += glob.glob(os.path.join(options.output, f'summed_{s}processes', f'GluGluTo*To2L2B_*_tb_1p50_*{H.EraFromPOG(options.era)}*.root')) 
        files += glob.glob(os.path.join(options.output, f'summed_{s}processes', f'*To2L2B_*_tb_20p00_*{H.EraFromPOG(options.era)}*.root'))

    HT.setTDRStyle()
    found_systematics = {}
    for reg in ['resolved', 'boosted']:
        for flavor in ['ElEl', 'MuMu', 'OSSF', 'MuEl']:
            found_systematics[f'{flavor}_{reg}'] = H.get_listofsystematics(_files_tolistsysts, cat=None, flavor=flavor, reg=reg, multi_signal=False) 
    
    print( 'found syst :: ', found_systematics )
    print( 'requested syst ::', options.syst)
    print( 'files::', files )  

    ignore_systematics = []
    
    for proc in files:
        process = get_process(proc, plotConfig, options.era, merge=options.merge)
        
        if options.files:
            if proc not in options.files:
                continue
        
        if options.merge: 
            _tf = ROOT.TFile.Open(proc)
        else:
            _tf = ROOT.TFile.Open(os.path.join(os.path.dirname(options.input), proc))
        
        logger.info(f'working on {_tf}')

        plots = getPlotList(_tf)
        
        for plot in plots:
            
            if options.plots:
                if plot not in options.plots:
                    continue
            
            if not 'DNNOutput_' in plot:
                continue

            if 'MuEl' in plot: flavor = 'MuEl'
            elif 'ElEl'in plot: flavor = 'ElEl'
            elif 'MuMu' in plot: flavor = 'MuMu'
            
            if 'resolved' in plot: reg = 'resolved'
            elif 'boosted' in plot: reg = 'boosted'
            
            nominal     = _tf.Get(plot)
            systematics = getSystList(_tf, nominal)
            nominal     = proj(nominal)
            if options.normalize and not options.merge:
                scale(nominal, plotConfig, proc)

            for syst in found_systematics[f'{flavor}_{reg}']:
                if options.syst:
                    if syst not in options.syst:
                        continue
                if any(syst.startswith(x) for x in ignore_systematics):
                    continue
                
                cms_syst  = H.CMSNamingConvention(origName=syst, era=options.era, process=process)

                up = _tf.Get(plot + "__" + syst + "up")
                if not (up and up.InheritsFrom("TH1")):
                    logger.error(f"\tCould not find up variation for systematic {syst} == {cms_syst}, using nominal")
                    up = nominal
                
                down = _tf.Get(plot + "__" + syst + "down")
                if not (down and down.InheritsFrom("TH1")):
                    logger.error(f"\tCould not find down variation for systematic {syst} == {cms_syst}, using nominal")
                    down=nominal
                
                if up == down == nominal:
                    print("Neither up nor down found, skipping!")
                    continue
                
                up = proj(up)
                down = proj(down)
                if options.normalize and not options.merge:
                    scale(up, plotConfig, proc)
                    scale(down, plotConfig, proc)

                drawSystematic(nominal, up, down, plot, options.era, cms_syst, proc.split('/')[-1].split(".root")[0], options.output)
        _tf.Close()
