#!/usr/bin/env python
import os, os.path, sys
import CombineHarvester.CombineTools.ch as ch
import argparse
# import CombineHarvester.CombineTools.pdgRounding as pdgRounding
import ROOT

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)

ROOT.gSystem.Load('libHiggsAnalysisCombinedLimit')

parser = argparse.ArgumentParser()
parser.add_argument('--workspace',  '-w', help='Input workspace')
parser.add_argument('--fit_file',   '-f', help='Input file')
parser.add_argument('--fit',              help='b-only fit or s+b fit ??', choices=['fit_s', 'fit_b'])
parser.add_argument('--bin',        '-b', help='bin name')
parser.add_argument('--signal',     '-s', help='signal name')


args = parser.parse_args()

fin = ROOT.TFile(args.workspace)
wsp = fin.Get('w')

cmb = ch.CombineHarvester()
cmb.SetFlag("workspaces-use-clone", True)
ch.ParseCombineWorkspace(cmb, wsp, 'ModelConfig', 'data_obs', False)


mlf = ROOT.TFile(args.fit_file)
rfr = mlf.Get(args.fit)
fbin= args.bin
signal_process = args.signal

def getColumnName(workspace):
    # this works assuming no combination of lepton flavour or regions
    # which is true for  'fit' 
    mode   = workspace.split('To2L2B_')[0]
    heavy  = mode[0]
    light  = mode[-1]
    prod   = 'gg%s'%heavy if 'gg_fusion' in workspace else 'bb%s'%heavy
    nb     = workspace.split('_')[3]
    region = workspace.split('_')[4] 
    channel= workspace.split('_')[5]
    flavDict = {
            'ElEl': '$e^{\pm}e^{\mp}$', 
            'MuMu': '$\mu^{\pm}\mu^{\mp}$',
            'MuEl': '$\mu^{\pm}e^{\mp}$',
            'OSSF': '$\mu^{\pm}\mu^{\mp}$ + $e^{\pm}e^{\mp}$'}
    return '%s -%s, (%s)'%(nb, region, flavDict[channel])  


def PrintTables(cmb, fbin, signal_process, column, uargs):
    c_dnn = cmb.cp().bin([fbin])
    
    LatexTab = r"""
\begin{tabular}{|l|r@{$ \,\,\pm\,\, $}l|}
\hline
Process & \multicolumn{2}{c}{%s} \\
\hline
\hline
"""%column
    # main bkg
    LatexTab += r'''TTbar                                                     & $%.2f$ & $%.2f$ \\
            ''' % (c_dnn.cp().process(['ttbar']).GetRate(), c_dnn.cp().process(['ttbar']).GetUncertainty(*uargs))
    LatexTab += r'''Single Top                                                & $%.2f$ & $%.2f$  \\
            ''' % (c_dnn.cp().process(['SingleTop']).GetRate(), c_dnn.cp().process(['SingleTop']).GetUncertainty(*uargs))
    LatexTab += r'''Drell-Yan +jets                                           & $%.2f$ & $%.2f$ \\
            ''' % (c_dnn.cp().process(['DY']).GetRate(), c_dnn.cp().process(['DY']).GetUncertainty(*uargs))
    # others
    #LatexTab += r'''W +jets                                                   & $%.2f$ & $%.2f$ \\
    #        ''' % (c_dnn.cp().process(['WJets']).GetRate(), c_dnn.cp().process(['WJets']).GetUncertainty(*uargs))
    LatexTab += r'''ttV                                                       & $%.2f$ & $%.2f$ \\
            ''' % (c_dnn.cp().process(['ttV']).GetRate(), c_dnn.cp().process(['ttV']).GetUncertainty(*uargs))
    LatexTab += r'''VV                                                        & $%.2f$ & $%.2f$ \\
            ''' % (c_dnn.cp().process(['VV']).GetRate(), c_dnn.cp().process(['VV']).GetUncertainty(*uargs))
    LatexTab += r'''VVV                                                       & $%.2f$ & $%.2f$ \\
            ''' % (c_dnn.cp().process(['VVV']).GetRate(), c_dnn.cp().process(['VVV']).GetUncertainty(*uargs))
    LatexTab += r'''SM Higgs                                                  & $%.2f$ & $%.2f$ \\
            ''' % (c_dnn.cp().process(['SMHiggs']).GetRate(), c_dnn.cp().process(['SMHiggs']).GetUncertainty(*uargs))
    
    # tot bkg.
    LatexTab += r'''\hline'''
    LatexTab += r'''
                Total expected background                             & $%.2f$ & $%.2f$ \\ 
            ''' % (c_dnn.cp().backgrounds().GetRate(), c_dnn.cp().backgrounds().GetUncertainty(*uargs))
    # signal 
    LatexTab += r'''%s                                                & $%.2f$ & $%.2f$  \\ 
            ''' % (signal_process, c_dnn.cp().signals().GetRate(), c_dnn.cp().signals().GetUncertainty(*uargs))
    # data
    LatexTab += r'''\hline'''
    LatexTab += r'''
                Observed data                                         & \multicolumn{2}{c}{$%g$} \\
            ''' % (c_dnn.cp().GetObservedRate())
    LatexTab += r"""\hline
\end{tabular}"""
    print LatexTab
    return LatexTab


column = getColumnName(args.workspace)

print 'Pre-fit tables:\n\n'
preFit_LatexTab = PrintTables(cmb, fbin, signal_process, column, tuple())

saveFile1 = os.path.join('YieldTables', args.workspace.split('_combine_workspace.root')[0]+'_%s_preFit.tex'%args.fit)
with open(os.path.join(saveFile1), 'w+') as f_:
    f_.write(preFit_LatexTab)

cmb.UpdateParameters(rfr)

print 'Post-fit tables:\n\n'
postFit_LatexTab = PrintTables(cmb, fbin, signal_process, column, (rfr, 500))

saveFile2 = os.path.join('YieldTables', args.workspace.split('_combine_workspace.root')[0]+'_%s_postFit.tex'%args.fit)
with open(os.path.join(saveFile2), 'w+') as f_:
    f_.write(postFit_LatexTab)
