#! /bin/env python
import os, sys, argparse
import json
import re
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

# to prevent pyroot to hijack argparse we need to go around
tmpargv  = sys.argv[:] 
sys.argv = []
sys.argv = tmpargv

import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True

import CMSStyle as CMSStyle
import CombineHarvester.CombineTools.ch as ch
sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis')
import Constants as Constants
logger = Constants.ZAlogger(__name__)

def format_float(value):
    if value * 100 < 0.1:
        return '$<$ 0.1'
    else:
        return '%.1f' % (value * 100)


def format_value(value):
    if type(value) is float:
        fmt = r'{}\%'
        return fmt.format(format_float(value))
    else:
        fmt = r'{}\% -- {}\%'

        value_1 = format_float(value[0])
        value_2 = format_float(value[1])

        if value_1 != value_2:
            fmt = r'{}\% -- {}\%'
            return fmt.format(value_1, value_2)
        else:
            fmt = r'{}\%'
            return fmt.format(value_1)


def format_latex_table_line_2(name, value):
    fmt = r'''{}   & \multicolumn{{2}}{{c}}{{{}}} \\
    '''
    return fmt.format(name, format_value(value))


def format_latex_table_line_3(name, v, w):
    fmt = r'''{}   & {}  & {} \\
    '''
    return fmt.format(name, format_value(v), format_value(w))


def beautify(s):
    # names
    if s == 'ttbar':
        return r'ttbar'
    if s == 'DY':
        return 'Drell-Yan'
    if s == 'SingleTop':
        return 'Single top'
    if s == 'VV':
        return 'VV'
    if s == 'SMHiggs':
        return 'SM Higgs'
    if s == 'others':
        return 'other backgrounds'
    if s == 'HToZATo2L2B':
        return r'$H \rightarrow ZA$ signal'
    if s == 'AToZHTo2L2B':
        return r'$A \rightarrow ZH$ signal'
    
    # systs
    # b-tagging
    if s.startswith('CMS_btagSF_'):
        era = s.split('_')[-1]

    if s.startswith('CMS_btagSF_deepJet_fixWP_heavy'):
        return 'Heavy flavour jet b-tagging (DeepJetM)'
    if s.startswith('CMS_btagSF_deepJet_fixWP_light'):
        return 'Light flavour jet b-tagging (DeepJetM)'
    
    if s.startswith('CMS_btagSF_deepCSV_subjet_fixWP_heavy'):
        return 'Heavy flavour subjet b-tagging (DeepCSVM)'
    if s.startswith('CMS_btagSF_deepCSV_subjet_fixWP_light'):
        return 'Light flavour subjet b-tagging (DeepCSVM)'

    # correlated 
    if s.startswith("CMS_UnclusteredEn"):
        return "Unclustered energy" 
    if s.startswith("CMS_HEM"):
        return "CMS event veto for 2018 HEM15/16 failure"
    if s.startswith("CMS_HLTZvtx"):
        return "EGamma HLT Z region inefficiency"
    if s.startswith("CMS_elel_trigSF"):
        return "DoubleEG triggers scale factor"
    if s.startswith("CMS_mumu_trigSF"):
        return "DoubleMuon trigger scale factor"
    if s.startswith("CMS_muel_trigSF"):
        return "MuonEG trigger scale factor"
    if s.startswith("CMS_mu_trigger"):
        return "SingleMuon trigger scale factor"
    if s.startswith("CMS_pileup"):
        return "Pileup"
    if s.startswith("CMS_L1PreFiring"):
        return "Level 1 ECAL and Muon prefiring"
    if s.startswith("CMS_eff_elid"):
        return "Electron identification"
    if s.startswith("CMS_eff_elreco_lowpt"):
        return "Electron reconstruction at low pT ( < 20 \GeV)"
    if s.startswith("CMS_eff_elreco_highpt"):
        return "Electron reconstruction at high pT ( > 20 \GeV)"
    if s.startswith("CMS_eff_muid"):
        return "Muon identification"
    if s.startswith("CMS_eff_muiso"):
        return "Muon isolation"

    #theory
    if s.startswith('QCDscale_'):
        return "QCD scale uncertainty"
    if s.startswith('QCDMuR_'):
        return "QCD renormalisation scale ($\mu_{R}$) uncertainty"
    if s.startswith('QCDMuF_'):
        return "QCD factorization scale ($\mu_{F}$) uncertainty"
    if s.startswith('ISR_'):
        return "Parton shower initial state (ISR) uncertainty"
    if s.startswith('FSR_'):
        return "Parton shower final state (FSR) uncertainty"
    if s.startswith('pdf_'):
        return "Parton distribution functions (PDFs) uncertainty"

    
    if s.startswith('DYweight_'):
        region  = s.split('_')[1]
        channel = s.split('_')[2]
        channel = '$e^{\pm}e^{\mp}$' if channel =='elel' else '$\mu^{\pm}\mu^{\pm}$'
        return "Drell-Yan+jets reweighting %s, (%s)"%( region, channel)

    if s.startswith("CMS_scale_j_"):
        corr = s.split("_")[-1]
        return "Jet energy scale %s uncertainty"%corr
    if s.startswith("CMS_res_j_"):
        corr = s.split("_")[-1]
        return "Jet energy resolution %s uncertainty"%corr

    if s.startswith("CMS_scale_fatjet_"):
        corr = s.split("_")[-1]
        return "Fatjet energy scale %s uncertainty"%corr
    if s.startswith("CMS_res_fatjet_"):
        corr = s.split("_")[-1]
        return "Fatjet energy resolution %s uncertainty"%corr

    if s.startswith('lumi_correlated_13TeV_2016_2017_2018'):
        return 'Correlated luminosity 2016,2017,2018'
    if s.startswith('lumi_correlated_13TeV_2017_2018'):
        return 'Correlated luminosity 2017,2018'
    if s.startswith('lumi_uncorrelated'):
        era = s.split('_')[-1]
        return 'Uncorrelated luminosity %s'%era
    
    if s.startswith('MC_stat'):
        return 'MC statistics'
    
    if 'xsc' in s:
        p = s.split('_')[0]
        return "%s cross-section uncertainty"%p

    return s.replace('_', '\_')


def fill_table(bkg_, sig_, table):
    # Remove statistical systematic uncertainty shapes
    bkg = [x.cp() for x in bkg_]
    sig = [x.cp() for x in sig_]

    for x in bkg:
        x.FilterSysts(lambda s: 'bin_' in s.name())
    for x in sig:
        x.FilterSysts(lambda s: 'bin_' in s.name())

    common_systematics = []

    flavor_bkg_systematics = {}
    flavor_sig_systematics = {}
    for i in range(len(bkg)):
        processes = bkg[i].process_set()

        # First, keep only shape systematics
        only_shape_systematics = bkg[i].cp()
        systematics = only_shape_systematics.syst_name_set()

        for s in systematics:
            # Keep only the desired systematic uncertainty
            c = only_shape_systematics.cp().syst_name([s])

            # Get list of processes affected by this systematic uncertainty
            p = set()
            c.ForEachSyst(lambda s: p.add(s.process()))

            if 'data' in p:
                p.remove('data')

            # Keep only systematics affecting all the backgrounds
            if set(processes) != set(p):
                #print("Systematics %r does not affect all the backgrounds, skipping." % s)
                continue

            std_syst = s

            flavor_bkg_systematics.setdefault(std_syst, []).append(c.GetUncertainty() / c.GetRate())
            c = sig[i].cp().syst_name([s])
            flavor_sig_systematics.setdefault(std_syst, []).append(c.GetUncertainty() / c.GetRate())
            common_systematics.append(s)

    systematics = list(set(flavor_bkg_systematics.keys() + flavor_sig_systematics.keys()))
    # Sort systematics by value, biggest impact top
    systematics = sorted(systematics, key= lambda k: max(flavor_bkg_systematics[k]), reverse=True)

    bkg_systematics = []
    sig_systematics = []

    for s in systematics:
        bkg_systematics.append((min(flavor_bkg_systematics[s]), max(flavor_bkg_systematics[s])))
        sig_systematics.append((min(flavor_sig_systematics[s]), max(flavor_sig_systematics[s])))
    
    max_syst_ToPrint = len(bkg_systematics)
    if len(bkg_systematics) > 10:
        max_syst_ToPrint = 10

    for i in range(max_syst_ToPrint):
        table = table + format_latex_table_line_3(beautify(systematics[i]), bkg_systematics[i], sig_systematics[i])

    table = table + r'''\midrule
    '''
    return table, common_systematics


def fill_affecting_only_bkg_table(name=None, bkgs=None, already_included_systs=None, table=None, processes=None, title="Affecting only %s (%s of the total bkg.)"):
    if not processes:
        processes = [name]

    bkgs = [x.cp() for x in bkgs]
    proportions = []

    flavor_systematics_values = {}

    for cb_ in bkgs:
        cb = cb_.cp()
        cb.FilterSysts(lambda s: 'bin_' in s.name())

        systematics = cb.syst_name_set()
        # Affecting only 'name' background
        c = cb.cp().process(processes)

        if len(c.process_set()) == 0:
            continue
        proportions.append(c.GetRate() / cb.GetRate())
        # Keep only systematics affecting only one background
        c.FilterSysts(lambda s: s.name() in already_included_systs)

        for s in c.syst_name_set():
            c_s = c.cp().syst_name([s])
            systematics_values = flavor_systematics_values.setdefault(s, [])
            systematics_values.append(c_s.GetUncertainty() / c_s.GetRate())

        # Get MC stats systematics
        systematics_values = flavor_systematics_values.setdefault('MC_stat', [])
        only_mc_stat = cb_.cp().process(processes)
        only_mc_stat.FilterSysts(lambda s: 'bin_' not in s.name())
        systematics_values.append(only_mc_stat.GetUncertainty() / only_mc_stat.GetRate())

    systematics = flavor_systematics_values.keys()
    # Sort systematics by value, biggest impact top
    systematics = sorted(systematics, key= lambda k: max(flavor_systematics_values[k]), reverse=True)

    systematics_values = []
    for s in systematics:
        systematics_values.append((min(flavor_systematics_values[s]), max(flavor_systematics_values[s])))

    title = title%(beautify(name), format_value((min(proportions), max(proportions))))
    table = table + r'''\multicolumn{{3}}{{c}}{{{}}} \\
    '''.format(title)

    for i in range(len(systematics_values)):
        table = table + format_latex_table_line_2(beautify(systematics[i]), systematics_values[i])

    return table

def fill_affecting_only_signal_table(sigs, signal_process, already_included_systs, table, title="Affecting only %s (%s of the total bkg.)"):
    sigs = [x.cp() for x in sigs]

    def extract_values(process):
        flavor_systematics_values = {}
        for cb_ in sigs:
            cb = cb_.cp()
            cb.FilterSysts(lambda s: 'bin_' in s.name())

            systematics = cb.syst_name_set()

            # Affecting only 'name' background
            c = cb.cp().process([process])
            if len(c.process_set()) == 0:
                continue
            # Keep only systematics affecting only one background
            c.FilterSysts(lambda s: s.name() in already_included_systs)

            for s in c.syst_name_set():
                c_s = c.cp().syst_name([s])
                if 'QCDscale' in s:
                    s = 'QCDscale'

                systematics_values = flavor_systematics_values.setdefault(s, [])
                systematics_values.append(c_s.GetUncertainty() / c_s.GetRate())

            # Get MC stats systematics
            systematics_values = flavor_systematics_values.setdefault('MC_stat', [])
            only_mc_stat = cb_.cp().process([process])
            only_mc_stat.FilterSysts(lambda s: 'bin_' not in s.name())
            systematics_values.append(only_mc_stat.GetUncertainty() / only_mc_stat.GetRate())

        return flavor_systematics_values
    flavor_systematics_values = extract_values(signal_process)
    systematics = flavor_systematics_values.keys()
    # Sort systematics by value, biggest impact on SM on top
    systematics = sorted(systematics, key= lambda k: max(flavor_systematics_values[k]), reverse=True)

    systematics_values = []
    for s in systematics:
        systematics_values.append((min(flavor_systematics_values[s]), max(flavor_systematics_values[s])))

    table = table + r'''\multicolumn{3}{c}{Affecting only %s signal} \\
    '''%signal_process
    for i in range(len(systematics_values)):
        table = table + format_latex_table_line_2(beautify(systematics[i]), systematics_values[i])

    return table


def get_table(bkg=None, sig=None, signal_process=None, label=''):
    table = r'''
\begin{table}[!htb]
    \caption{ }
    \label{table:systs_%s}
    \small
    \resizebox{\textwidth}{!}{
    \begin{tabular}{@{}lcc@{}}
        \hline
        \\
        \textbf{Source} & \textbf{Background yield variation} & \textbf{%s} \\
        \\ 
        \hline
        ''' % (label, signal_title)
    
    table, systematics = fill_table(bkg, sig, table)

    table = fill_affecting_only_bkg_table('DY', bkg, systematics, table, title=r"\textbf{Affecting only %s (%s of the total bkg.)}")
    table = table + r'''\\
        \hline
    '''
    table = fill_affecting_only_bkg_table('ttbar', bkg, systematics, table)
    table = table + r'''\\
    \hline
    '''
    table = fill_affecting_only_bkg_table('SingleTop', bkg, systematics, table)
    table = table + r'''\\
    \hline
    '''
    #table = fill_affecting_only_bkg_table('ZZ', bkg, systematics, table)
    #table = table + r'''\midrule
    #\hline
    #'''
    #table = fill_affecting_only_bkg_table('SM', bkg, systematics, table)
    #table = table + r'''\midrule
    #\hline
    #'''
    #table = fill_affecting_only_bkg_table('others', bkg, systematics, table)
    #table = table + r'''\midrule
    #\hline
    #'''
    table = fill_affecting_only_signal_table(sig, signal_process, systematics, table)
    table = table + r'''\\
    \hline
    \end{tabular}
    }
\end{table}
'''
    return table

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create LaTeX table of systematics impact on background')
    parser.add_argument('-i', '--inputs', action='store', required=True, 
            help='path to data cards')
    parser.add_argument('--mode', action='store', required=True, choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'mbb', 'mllbb', 'ellipse', 'dnn'], 
            help='Analysis mode')
    parser.add_argument('--expectSignal', action='store', required=False, type=int, default=1, choices=[0, 1],
            help=' Is this S+B or B-Only fit? ')
    parser.add_argument('--tanbeta', action='store', type=float, default=None, required=False, help='')
    parser.add_argument('--_2POIs_r', action='store_true', dest='_2POIs_r', required=False, default=False,
            help='This will merge both signal in 1 histogeram and normalise accoridngly, tanbeta will be required')
    options = parser.parse_args()
    

    poi_dir, tb_dir, CL_dir = Constants.locate_outputs('fit', options._2POIs_r, options.tanbeta, options.expectSignal)
    
    signal_title = "Signal yield variation"
    inputs_list  = glob.glob(os.path.join(options.inputs, 'fit', options.mode, CL_dir, poi_dir, tb_dir, '*', '*.dat'))
    
    
    for f in inputs_list:
        
        cbs = []
        signals = []
        backgrounds = []
        
        outputDir = os.path.join(options.inputs, 'systematics-tabs', options.mode, f.split('/')[-2])
        if not os.path.isdir(outputDir):
            os.makedirs(outputDir)
            
        if not any( x in f.split('/')[-1] for x in [ 'OSSF', 
                                                     'OSSF_MuEl',
                                                     'MuMu', 
                                                     'ElEl', 
                                                     'MuMu_ElEl', 
                                                     'MuMu_ElEl_MuEl']):
            continue # avoid  MuEl solo cat. 
            
        mass  = f.split('/')[-2].replace('-','_')
        cat   = f.split('/')[-1].replace('.dat', '.tex')
        thdm  = f.split('/')[-1].split('_')[0].split('To2L2B')[0]
        heavy = thdm[0]
        signal_process = 'gg%s'%heavy if 'gg_fusion' in cat else 'bb%s'%heavy
        label = cat.split('_dnn')[0].split('To2L2B_')[-1]

        print( 'working on ::', cat)
        
        # Extract mass from name. We can't let CH do it for us
        cb = ch.CombineHarvester()
        cb.ParseDatacard(f, mass="125")

        backgrounds.append(cb.cp().backgrounds())
        signals.append(cb.cp().signals())
        
        cbs.append(cb)
        
        latex_table = get_table(backgrounds, signals, signal_process, label)
        with open(os.path.join(outputDir, cat), 'w') as f_:
            f_.write(latex_table)
        
        print( latex_table)
    print( "All Latex tables are saved in : %s" %os.path.join(options.inputs, 'systematics-tabs', options.mode))
