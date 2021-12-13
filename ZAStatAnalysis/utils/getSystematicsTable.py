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
        return 'signal'
    if s == 'CMS_eff_b_heavy':
        return 'Jet b-tagging (heavy)'
    if s == 'CMS_eff_b_light':
        return 'Jet b-tagging (light)'
    if 'CMS_eff_trigger' in s:
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
    if 'lumi_13TeV' in s:
        return 'Luminosity'
    if s == 'ttbar_modeling':
        return r'ttbar modeling'
    if s == 'ttbar_xsec':
        return r'ttbar cross-section'
    if s == 'dy_mc_modeling':
        return r'Drell-Yan modeling'
    if s == 'dy_mc_xsec':
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

            p = [x for x in p if not 'nobtag_to_btagM' in x]
            if 'data' in p:
                p.remove('data')

            # Keep only systematics affecting all the backgrounds
            if set(processes) != set(p):
                #print("Systematics %r does not affect all the backgrounds, skipping." % s)
                continue

            std_syst = s
            if 'CMS_eff_trigger' in s:
                std_syst = 'CMS_eff_trigger'

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
    for i in range(len(bkg_systematics)):
        table = table + format_latex_table_line_3(beautify(systematics[i]), bkg_systematics[i], sig_systematics[i])

    table = table + r'''\midrule
    '''
    return table, common_systematics

def fill_affecting_only_table(name=None, bkgs=None, already_included_systs=None, table=None, processes=None, title="Affecting only {} ({} of the total bkg.)"):
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

    title = title.format(beautify(name), format_value((min(proportions), max(proportions))))
    table = table + r'''\multicolumn{{3}}{{c}}{{{}}} \\
    '''.format(title)

    for i in range(len(systematics_values)):
        table = table + format_latex_table_line_2(beautify(systematics[i]), systematics_values[i])

    return table

def fill_affecting_only_signal_table(sigs, already_included_systs, table, title="Affecting only {} ({} of the total bkg.)"):
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

    flavor_systematics_values = extract_values('HToZATo2L2B')
    systematics = flavor_systematics_values.keys()
    # Sort systematics by value, biggest impact on SM on top
    systematics = sorted(systematics, key= lambda k: max(flavor_systematics_values[k]), reverse=True)

    systematics_values = []
    for s in systematics:
        systematics_values.append((min(flavor_systematics_values[s]), max(flavor_systematics_values[s])))

    #table = table + r'''Affecting only signal & SM signal & $\text{m}_\text{X} = 400\,\text{GeV}$ \\
    table = table + r'''\multicolumn{3}{c}{Affecting only signal} \\
    '''
    for i in range(len(systematics_values)):
        table = table + format_latex_table_line_2(beautify(systematics[i]), systematics_values[i])

    return table

def get_table(bkg=None, sig=None):
    table = r'''
\begin{tabular}{@{}lcc@{}} \torule
Source & Background yield variation & %s \\
\midrule
''' % signal_title

    table, systematics = fill_table(bkg, sig, table)

    table = fill_affecting_only_table('DY', bkg, systematics, table, title=r"Affecting only {} ({} of the total bkg.)")
    table = table + r'''\midrule
    '''
    table = fill_affecting_only_table('ttbar', bkg, systematics, table)
    table = table + r'''\midrule
    '''
    table = fill_affecting_only_table('SingleTop', bkg, systematics, table)
    table = table + r'''\midrule
    '''
    #table = fill_affecting_only_table('ZZ', bkg, systematics, table)
    #table = table + r'''\midrule
    #'''
    #table = fill_affecting_only_table('SM', bkg, systematics, table)
    #table = table + r'''\midrule
    #'''
    #table = fill_affecting_only_table('others', bkg, systematics, table)
    #table = table + r'''\midrule
    #'''
    
    # if 'ggHH' in sig.process_set():
    #table = table + r'''\midrule
    #'''
    table = fill_affecting_only_signal_table(sig, systematics, table)
    # if 'ggX0HH' in sig.process_set():
        # table = table + r'''\midrule
        # '''
        # table = fill_affecting_only_table('ggX0HH', sig, systematics, table)
    table = table + r'''\bottomrule
\end{tabular}
'''
    return table

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create LaTeX table of systematics impact on background')
    parser.add_argument('-i', '--inputs', action='store', required=True, help='path to data cards')
    parser.add_argument('--mode', action='store', required=True, choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'mjj', 'mlljj', 'ellipse', 'dnn'], help='Analysis mode')
    options = parser.parse_args()
    
    # Extract mass from name. We can't let CH do it for us
    signal_title = "Signal yield variation"

    
    inputs_list = glob.glob(os.path.join(options.inputs, 'fit',options.mode, '*', '*.dat'))
    for f in inputs_list:
        cbs = []
        signals = []
        backgrounds = []
        for prod in ['gg_fusion', 'bb_associatedProduction']:
            process = 'ggH' if prod =='gg_fusion' else 'bbH'
            for reg in ['resolved', 'boosted']:
                for flavor in ['ElEl_MuMu', 'ElEl', 'MuMu']:

                    outputDir = os.path.join(options.inputs, 'systematics-tabs', options.mode, f.split('/')[-2])
                    if not os.path.isdir(outputDir):
                        os.makedirs(outputDir)
                
                    mass = f.split('/')[-2].replace('-','_')
                    cat  = "HToZATo2L2B_{}_{}_{}_{}_{}.tex".format(prod, reg, flavor, options.mode, mass)

                    cb = ch.CombineHarvester()
                    cb.ParseDatacard(f, mass="125")
        
                    backgrounds.append(cb.cp().backgrounds())
                    signals.append(cb.cp().signals())
                
                    cbs.append(cb)
                    
                    latex_table = get_table(backgrounds, signals)
                    print(latex_table)
                    with open(os.path.join(outputDir, cat), 'w') as f_:
                        f_.write(latex_table)
        print( "All Latex tables saved in : %s" %os.path.join(options.inputs, 'systematics-tabs', options.mode))
