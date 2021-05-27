import os
import sys
import ROOT
import glob
import argparse
from copy import deepcopy
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

import logging
LOG_LEVEL = logging.DEBUG
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
logger = logging.getLogger("ZA resolutions")
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream)
try:
    import colorlog
    from colorlog import ColoredFormatter
    formatter = ColoredFormatter(
                "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
                datefmt=None,
                reset=True,
                log_colors={
                        'DEBUG':    'cyan',
                        'INFO':     'green',
                        'WARNING':  'blue',
                        'ERROR':    'red',
                        'CRITICAL': 'red',
                        },
                secondary_log_colors={},
                style='%'
                )
    stream.setFormatter(formatter)
except ImportError:
    # https://pypi.org/project/colorlog/
    pass

def float_to_mass(m):
    r = '{:.2f}'.format(m)
    return float(r)
def string_to_mass(s):
    m = float(s.replace('p', '.'))
    return m

def getParameters(filename=None):
    split_filename = filename.split('/')
    split_filename = split_filename[-1]
    split_filename = split_filename.split('_')
    mode = 'AToZH' if 'AToZHTo2L2B'in split_filename else('HToZA')
    if mode == 'HToZA':
        mH = split_filename[1]
        mA = split_filename[2]
    else:
        mA = split_filename[1]
        mH = split_filename[2]
    tb = split_filename[3].replace('.root','')
    proc = ("ggH" if tb == "1p50" else ("bbH"))
    return mH, mA, tb, proc

def ResolutionsVSWidth(path=None):
    for mode in ['AToZH', 'HToZA']:
        for cat in ['elel', 'mumu', 'oslep']:
            for var_ToPlot in  ['mllbb', 'mbb']:
                reco_w = {}
                natural_w = {}
                C = ROOT.TCanvas("c1","c1",500,400)
                pad2 = ROOT.TPad("pad2", "pad2", 0, 0.0, 1, 0.3)
                pad2.SetTopMargin(0)
                pad2.SetBottomMargin(0.4)
                pad2.SetLeftMargin(0.15)
                pad2.SetRightMargin(0.1)
                pad2.SetGridx()
                pad2.SetGridy()
                #C.SetLogy()
                #C.SetLogx()
                C.Clear()
                for rootf in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), path, "results", "*.root")):
                    file = ROOT.TFile(rootf)
                    smp = rootf.split('/')[-1]
                    mH, mA, tb, proc = getParameters(filename=rootf)
                    if "__skeleton__" in smp:
                        continue
                    if not smp.startswith("{}To2L2B_240p00_130p00_{}_{}".format(mode, tb, proc)) and not smp.startswith("{}To2L2B_500p00_250p00_{}_{}".format(mode, tb, proc)) and not smp.startswith("{}To2L2B_800p00_140p00_{}_{}".format(mode, tb, proc)):
                        continue
                    mA = mA.replace('p', '.').replace('.00', '')
                    mH = mH.replace('p', '.').replace('.00', '')
                    tb = tb.replace('p', '.').replace('.00', '').replace('.50', '.5')
                    if mode =='AToZH':
                        smpName = r"m_{A}=%s , m_{H}= %s, tan\beta= %s"%(mA,mH, tb)
                        h_fromGenPart = ('h2' if var_ToPlot =='mbb' else('h3'))
                        mass = (string_to_mass(mH) if var_ToPlot =='mbb' else(string_to_mass(mA)))
                    else:
                        smpName = r"m_{H}= %s, m_{A}=%s, tan\beta= %s"%(mH, mA, tb)
                        h_fromGenPart = ('h3' if var_ToPlot =='mbb' else('h2'))
                        mass = (string_to_mass(mA) if var_ToPlot =='mbb' else(string_to_mass(mH)))
                        
                    hist_naturalwidth = '{}_fromGenPart_Mass'.format(h_fromGenPart)
                    hist_reconstructedwidth = '{}_resolved_at_least_2bjets_gen{}'.format(cat, var_ToPlot)
                    if file.Get(hist_naturalwidth).Integral() ==0. or file.Get(hist_reconstructedwidth).Integral() ==0. :
                        continue
                    logger.info( f'{mode} , {smpName}, {var_ToPlot}, {cat}')
                    logger.info( f'resolution = {file.Get(hist_reconstructedwidth).GetStdDev()}')
                    logger.info( f'resolution /Mass (%) = {(file.Get(hist_reconstructedwidth).GetStdDev()/mass) *100}\n' )
                    logger.info( f'natural width = {file.Get(hist_naturalwidth).Integral()}')
                    logger.info( f'Width / Mass (%) = {file.Get(hist_naturalwidth).Integral()/mass *100}\n')
                    natural_w[smpName] = deepcopy(file.Get(hist_naturalwidth))
                    natural_w[smpName].SetDirectory(0)            
                    reco_w[smpName] = deepcopy(file.Get(hist_reconstructedwidth))
                    reco_w[smpName].SetDirectory(0)
                    file.Close()
        
                
                colors = [ROOT.kViolet, ROOT.kRed, ROOT.kCyan, ROOT.kBlack, ROOT.kGreen, ROOT.kBlue, ROOT.kCyan, ROOT.kRed+2, ROOT.kSpring, ROOT.kTeal, ROOT.kYellow, ROOT.kMagenta, ROOT.kCyan, ROOT.kOrange]
        
                legend = ROOT.TLegend(0.6, 0.6, 0.9, 0.9)
                legend.SetFillStyle(4000)
                legend.SetBorderSize(0)
                header = r" CMS Simulation: H\rightarrow ZA \rightarrow llbb" if mode =="HToZA" else r" CMS Simulation : A\rightarrow ZH \rightarrow ll bb"
                for d_idx, dict_ in enumerate([reco_w, natural_w]):
                    for i,(name, h) in enumerate(sorted(dict_.items())):
                        if h.Integral() ==0. :
                            logger.warning( f"0Entries for sample {name} , skipp")
                            continue
                        h.Scale(1./h.Integral())  # normalized to 1.
                        h.SetLineStyle(d_idx +1)
                        h.SetLineColor(colors[i])
                        h.SetLineWidth(2)
                        h.GetXaxis().SetTitle(f"{var_ToPlot} [GeV]")
                        h.GetYaxis().SetTitle("Events")
                        h.SetMaximum(1.2 )#h.GetMaximum())
                        h.SetMinimum(0.)
                        if d_idx == 0:
                            legend.AddEntry(h,name + " reconstructed")
                        else:
                            legend.AddEntry(h,name + " natural width")
                        h.Draw("H same")
                    
                legend.SetHeader("{}".format(header))
                legend.Draw()

                C.Print(f"resolution_vs_naturalwidth_{mode}/{cat}_{var_ToPlot}_bbH.png")
                C.Print(f"resolution_vs_naturalwidth_{mode}/{cat}_{var_ToPlot}_bbH.pdf")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--path', required=True, help='Bamboo directory')
    options = parser.parse_args()
    ResolutionsVSWidth(path=options.path)
