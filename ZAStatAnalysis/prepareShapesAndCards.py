#! /bin/env python
import os, os.path, sys, stat, argparse, getpass, json
import subprocess
import json
import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
import logging
logger = logging.getLogger(__name__)

from math import sqrt
from datetime import datetime

import numpy as np
import Harvester as H
import Constants as Constants
import CombineHarvester.CombineTools.ch as ch

def format_parameters(p):
    mH = "%.2f" % p[0]
    mA = "%.2f" % p[1]
    return ("MH_"+str(mH) + "_" + "MA_"+str(mA)).replace(".", "p")

def format_ellipse(p, ellipses):
    mH = "%.2f" % p[0]
    mA = "%.2f" % p[1]
    for ie, e in enumerate(ellipses['MuMu'], 0): #put here the enumerate index!!! 
        # it does not matter which flavor we pick as we are checking only the ellipse index
        mA_file = "%.2f" % e[-2]
        mH_file = "%.2f" % e[-1]
        if mA == mA_file and mH == mH_file: # check sim masses
            return '{:d}'.format(ie)        # return ellipse index

def parameter_type(s):
    try:
        if s == 'all':
            return 'all'
        x, y = map(float, s.replace("m", "-").split(','))
        if x.is_integer():
            x = int(x)
        if y.is_integer():
            y = int(y)
        return x, y
    except:
        raise argparse.ArgumentTypeError("Parameter must be x,y")

def get_hist_regex(r):
    return '^%s(__.*(up|down))?$' % r

signal_grid = [
        #part0 : 21 signal samples 
        ( 200, 50), ( 200, 100),
       # ( 250, 50), ( 250, 100),
       # ( 300, 50), ( 300, 100), ( 300, 200),
       # ( 500, 50), ( 500, 200), ( 500, 300), ( 500, 400),
       # ( 650, 50),
       # ( 800, 50), ( 800, 200), ( 800, 400), ( 800, 700),
       # (1000, 50), (1000, 200), (1000, 500), 
       # (2000, 1000),
       # (3000, 2000) 
        ]
extra_signals = [
        #(173.52,  72.01), (209.90,  30.00), (209.90,  37.34), (261.40, 102.99), (261.40, 124.53),
        #(296.10, 145.93), (296.10,  36.79), (379.00, 205.76), (442.63, 113.53), (442.63,  54.67),
        #(442.63,  80.03), (609.21, 298.01), (717.96,  30.00), (717.96, 341.02), (846.11, 186.51),
        #(846.11, 475.64), (846.11,  74.80), (997.14, 160.17), (997.14, 217.19), (997.14, 254.82), (997.14, 64.24)
        ##part2
        #(132.00,  30.00), (132.00,  37.34), (173.52,  57.85), (190.85,  71.28), (209.90, 46.48), (261.40,  56.73),
        #(335.40,  36.79), (379.00, 246.30), (442.63, 135.44), (516.94, 423.96), (516.94, 78.52), (609.21, 135.66),
        #(609.21, 253.68), (609.21,  54.71), (717.96, 249.34), (717.96,  63.58), (717.96, 99.78), (846.11, 294.51),
        #(846.11, 405.40), (846.11,  47.37), (846.11, 654.75), (997.14,  55.16)
        ##part3
        #(143.44,  46.48), (173.52,  46.48), (209.90, 104.53), (261.40,  69.66), (296.10, 45.12), (335.40, 120.39),
        #(335.40, 209.73), (442.63, 161.81), (442.63, 193.26), (442.63,  44.76), (442.63, 95.27), (516.94, 212.14),
        #(516.94,  30.00), (609.21, 158.41), (609.21,  34.86), (609.21, 417.76), (609.21, 85.86), (997.14, 298.97),
        #(997.14,  30.00), (997.14,  34.93), (997.14, 482.85), (997.14, 566.51)
        ##part4
        #(143.44, 30.00), (143.44,  37.34), (173.52,  30.00), (173.52,  37.34), (190.85, 86.78), (230.77, 102.72), (261.40,  37.10),
        #(261.40, 85.10), (296.10, 120.82), (335.40, 174.55), (335.40,  45.12), (335.40, 67.54), (335.40,  82.14), (379.00, 171.71),
        #(379.00, 80.99), (516.94, 151.69), (516.94, 179.35), (516.94, 352.61), (516.94, 44.34), (609.21, 116.29), (609.21, 216.52),
        #(717.96, 40.51), (846.11, 160.17), (997.14, 186.51), (997.14,  87.10)
        ##part5
        #(230.77,  37.10), (230.77,  45.88), (230.77, 69.78), (261.40,  45.88), (296.10, 176.02),
        #(296.10,  82.40), (442.63, 327.94), (442.63, 66.49), (516.94, 128.58), (516.94,  36.47),
        #(717.96, 400.03), (717.96, 475.80), (717.96, 47.08), (717.96,  85.86), (846.11, 137.54),
        #(846.11, 217.19), (846.11, 345.53), (846.11, 34.93), (846.11,  40.68), (846.11,  55.16), (997.14, 411.54)
        ##part6
        #(190.85,  57.85), (230.77,  30.00), (230.77,  85.09), (261.40, 150.50), (296.10,  67.65),
        #(335.40, 145.06), (379.00,  66.57), (379.00,  98.26), (442.63, 274.57), (516.94,  53.90),
        #(516.94,  65.52), (516.94,  93.12), (609.21, 185.18), (609.21,  40.51), (717.96, 157.56),
        #(717.96, 213.73), (717.96,  34.86), (846.11, 101.43), (846.11, 252.91), (846.11, 558.06),
        #(846.11,  64.24), (997.14, 118.11), (997.14, 350.77), (997.14,  47.37), (997.14,  74.80)
        ##part7
        #(157.77,  46.48), (157.77,  57.85), (190.85,  30.00), (190.85,  37.34), (209.90,  57.71),
        #(230.77, 123.89), (230.77,  56.73), (296.10,  99.90), (335.40,  30.00), (335.40,  55.33),
        #(379.00, 118.81), (379.00, 143.08), (379.00,  54.59), (442.63, 230.49), (442.63,  36.64),
        #(516.94, 296.65), (609.21,  30.00), (609.21, 351.22), (609.21,  47.08), (609.21, 505.93),
        #(717.96,  73.89), (846.11, 118.11), (846.11,  87.10), (997.14,  40.68), (997.14, 664.66),
        #(997.14, 779.83)
        ##part8
        #(157.77,  30.00), (157.77,  37.34), (190.85,  46.48), (209.90,  71.15), (209.90, 86.79),
        #(296.10,  30.00), (296.10,  55.33), (335.40,  99.61), (379.00,  30.00), (379.00, 36.63),
        #(379.00,  44.72), (442.63,  30.00), (516.94, 109.30), (516.94, 250.63), (609.21, 63.58),
        #(609.21,  99.78), (717.96, 116.19), (717.96, 183.48), (717.96, 291.34), (717.96, 54.71),
        #(717.96, 577.65), (846.11,  30.00), (997.14, 101.43), (997.14, 137.54)
        ]
    

def prepare_DataCards(grid_data = None, era= None, parameters= None, mode= None, input= None, ellipses_mumu_file= None, output= None, method= None, node= None, unblind= False, signal_strength= False, stat_only= False, verbose= False, split_by_categories=False):
    
    luminosity= Constants.getLuminosity(era)
    
    signal_grid = list(set(grid_data))
    parameters  = signal_grid 

    if signal_strength:
        parameters = [( 500, 300)]

    if len(parameters) == 1 and parameters[0] == 'all':
        parameters = parameters[:]

    for p in parameters:
        if not p in parameters:
            print("Invalid parameter '%s'. Valid values are %s" % (str(p), str(parameters)))
            return

    print("\tEra and the corresponding luminosity      : %s, %s" %(era, Constants.getLuminosity(era)))
    print("\tInput path                                : %s" %input )
    print("\tGenerating set of cards for parameter(s)  : %s" % (', '.join([str(x) for x in parameters])))
    print("\tChosen analysis mode                      : %s" % mode)

    ellipses = {}
    ellipses['MuMu'] = []
    ellipses['ElEl'] = []
    ellipses['MuEl'] = []
    with open(ellipses_mumu_file.replace('ElEl', 'MuMu')) as inf: 
        content = json.load(inf)
        ellipses['MuMu'] = content
        ellipses['MuEl'] = content
    with open(ellipses_mumu_file.replace('MuMu', 'ElEl')) as inf:
        content = json.load(inf)
        ellipses['ElEl'] = content
    
    prepareShapes(input, era, method, parameters, ['ggH', 'bbH'], ['boosted', 'resolved'], ['MuMu', 'ElEl', 'MuEl'], ellipses, mode, output, luminosity, split_by_categories, unblind, signal_strength, stat_only, verbose)

    # Create helper script to run limits
    output = os.path.join(output, mode)
    print( '\tThe generated script to run limits can be found in : %s' %output)
    script = """#! /bin/bash
scripts=`find {output} -name "*_run_{method}.sh"`
for script in $scripts; do
    dir=$(dirname $script)
    script=$(basename $script)
    echo "Computing with ${{script}}"
    pushd $dir &> /dev/null
    . $script
    popd &> /dev/null
done
""".format(output=output, method=method)
    
    script_name = "%s_%s_run_all_%s.sh" % (os.path.basename(output), mode, method)
    with open(script_name, 'w') as f:
        f.write(script)

    st = os.stat(script_name)
    os.chmod(script_name, st.st_mode | stat.S_IEXEC)

    if method=="hybridnew":
        print("All done. You can run everything by executing %r" % ('./' + script_name[:-3]+"_onSlurm.sh"))
    else:
        print("All done. You can run everything by executing %r" % ('./' + script_name))


def prepareShapes(input=None, era=None, method=None, parameters=None, productions=None, regions=None, flavors=None, ellipses=None, mode=None, output=None, luminosity=None, split_by_categories=False, unblind=False, signal_strength=False, stat_only=False, verbose=False):
    if mode == "mjj_and_mlljj":
        categories = [
                (1, 'mlljj'),
                (2, 'mjj')
                ]
    elif mode == "mjj_vs_mlljj":
        categories = [
                (1, 'mjj_vs_mlljj')
                ]
    elif mode == "mjj":
        categories = [
                (1, 'mjj')
                ]
    elif mode == "mlljj":
        categories = [
                (1, 'mlljj')
                ]
    elif mode == "ellipse":
        categories = [
                # % (flavour, ellipse_index)
                (1, 'ellipse_{}_{}')
                ]
    elif mode == "postfit":
        split_by_categories = True
        categories = [
                # % (flavour, ellipse_index)
                (1, 'ellipse_{}_{}')
                (2, 'mlljj'),
                (3, 'mjj'),
                (4, 'mjj_vs_mlljj')
                # % (process, cat, flavour, MH, MA, node )
                (5, 'dnn_ggH_resolved_{}_{}_{}_{}')
                ]
    elif mode == "dnn":
        categories = [
                # % (process, cat, flavour, MH, MA, node )
                (1, 'dnn_ggH_resolved_{}_{}_{}_{}')
                ]

    histfactory_to_combine_categories = {}
    if mode == "postfit":
        for p in parameters:
            formatted_p = format_parameters(p)
            formatted_e = format_ellipse(p, ellipses)
            histfactory_to_combine_categories = {
                    'ellipse_{}_{}'.format(formatted_p, formatted_e):    get_hist_regex('rho_steps_histo_{flavor}_hZA_lljj_deepCSV_btagM_mll_and_met_cut_%s' % format_ellipse(p, ellipses)),
                    'mlljj':   get_hist_regex('lljj_M_resolved_{flavor}_hZA_lljj_DeepCSVM_mll_and_met_cut'),
                    'mjj':     get_hist_regex('jj_M_resolved_{flavor}_hZA_lljj_DeepCSVM_mll_and_met_cut'),
                    'mjj_vs_mlljj': get_hist_regex('jj_M_vs_lljj_M_resolved_{flavor}_hZA_lljj_DeepCSVM_mll_and_met_cut'),
                    # FIXME add the dnn histos
                    }

    histfactory_to_combine_processes = {
            # main Background
            'ttbar'    : ['^TT*'],  
            'SingleTop': ['^ST_*'],
            'DY'       : ['^DYJetsToLL_0J*', '^DYJetsToLL_1J*', '^DYJetsToLL_2J*', '^DYToLL_*'],
            # Others Backgrounds
            'WPlusJets': ['^WJetsToLNu*'],
            'ttV'      : ['^TT(WJets|Z)To*'],
            'VV'       : ['^(ZZ|WW|WZ)To*'],
            'VVV'      : ['^(ZZZ|WWW|WZZ|WWZ)*'],
            #'Wgamma'  : ['^WGToLNuG_TuneCUETP8M1'], TODO add this sample 
            'SMHiggs'  : ['^ggZH_HToBB_ZToNuNu*', '^HZJ_HToWW*', '^ZH_HToBB_ZToLL*', '^ggZH_HToBB_ZToLL*', '^ttHJet*']
            }

    # Shape depending on the signal hypothesis
    for p in parameters:

        formatted_p = format_parameters(p)
        formatted_e = format_ellipse(p, ellipses)

        # Signal process
        suffix = 'MH_%s_MA_%s'%(p[0].replace('.', p), p[1].replace('.', p))
        histfactory_to_combine_processes['HToZATo2L2B_MH-%s_MA-%s'%(p[0],p[1]), p] = ['^HToZATo2L2B_MH-%s_MA-%s*'%(p[0],p[1])]
        
        # FIXME ZA postfit category, one per mass hypothesis
        if mode == "postfit":
            histfactory_to_combine_categories[('_', p)]     = get_hist_regex('DNNOutput_{flavor}channel_resolved_{node}scan_%s'%suffix)
        elif mode == "mjj_and_mlljj":
            histfactory_to_combine_categories[('mjj', p)]   = get_hist_regex('jj_M_resolved_{flavor}_hZA_lljj_DeepCSVM_mll_and_met_cut')
            histfactory_to_combine_categories[('mlljj', p)] = get_hist_regex('lljj_M_resolved_{flavor}_hZA_lljj_DeepCSVM_mll_and_met_cut')
        elif mode == "mjj_vs_mlljj": 
            histfactory_to_combine_categories[('mjj_vs_mlljj', p)] = get_hist_regex('Mjj_vs_Mlljj_resolved_{flavor}_hZA_lljj_DeepCSVM_mll_and_met_cut')
        elif mode == "mlljj":
            histfactory_to_combine_categories[('mlljj', p)] = get_hist_regex('{flavor}_resolved_METCut__mllbb_DeepCSVM')
        elif mode == "mjj":
            histfactory_to_combine_categories[('mjj', p)]   = get_hist_regex('jj_M_resolved_{flavor}_hZA_lljj_DeepCSVM_mll_and_met_cut')
        elif mode == "ellipse":
            histfactory_to_combine_categories[('ellipse_{}_{}'.format('MH-%s_MA-%s'%(p[0],p[1]), formatted_e), p)] = get_hist_regex('rho_steps_resolved_histo_{flavor}_hZA_lljj_DeepCSV_btagM__METCut__MH_%sp0_MA_%sp0'%(p[0],p[1]))
        elif mode == "dnn":
            histfactory_to_combine_categories[('dnn_ggH_resolved_{}_{}_{}_{}'.format(flavor, p[0], p[1], node ), p)] = get_hist_regex('DNNOutput_{flavor}_resolved_{node}scan_MA_%s_MH_%s'%(node, p[1], p[0]))

    if not unblind:
        histfactory_to_combine_processes['data_obs'] = ['^DoubleMuon*', '^DoubleEG*', '^MuonEG*', '^SingleMuon*', '^EGamma*']

    H.splitJECBySources = False
    if signal_strength:
        H.scaleZAToSMCrossSection = True
    H.splitTTbarUncertBinByBin = False

    output_filename = os.path.join(output, 'shapes_HToZATo2L2B.root')
    file, systematics = H.prepareFile(histfactory_to_combine_processes, histfactory_to_combine_categories, input, output_filename, 'HToZATo2L2B', method, luminosity, unblind=unblind, flavors=flavors)

    print ( "\tsystematics : %s       :" %systematics )
    for p in parameters:
        cb = ch.CombineHarvester()
        if verbose:
            cb.SetVerbosity(3)
        cb.SetFlag("zero-negative-bins-on-import", True)

        # Dummy mass value used for all combine input when a mass is needed
        mass = "125"

        formatted_p = format_parameters(p)
        formatted_e = format_ellipse(p, ellipses)

        analysis_name = 'HToZATo2L2B_%s'%(formatted_p)
        categories_with_parameters = categories[:]
        for i, k in enumerate(categories_with_parameters):
            if mode=='dnn':
                categories_with_parameters[i] = ('_')
            else:
                categories_with_parameters[i] = (k[0], k[1].format('MH-%s_MA-%s'%(p[0],p[1]), formatted_e))

        cb.AddObservations(['*'], [analysis_name], ['13TeV_%s'%era], flavors, categories_with_parameters)
        bkg_processes = [
                'ttbar',
                'SingleTop',
                'DY',
                'WPlusJets',
                'ttV',
                'VV',
                'VVV',
                #'Wgamma',
                'SMHiggs'
                ]

        processes = []
        for flavor in flavors:
            cb.AddProcesses(['*'], [analysis_name], ['13TeV_%s'%era], [flavor], bkg_processes, categories_with_parameters, False)
            processes += bkg_processes

        sig_process = 'HToZATo2L2B'
        cb.AddProcesses([mass], [analysis_name], ['13TeV_%s'%era], flavors, [sig_process], categories_with_parameters, True)
        processes += [sig_process]
        print ( "processes       : %s" %processes)
        
        if not stat_only:
            processes_without_weighted_data = cb.cp()
            processes_without_weighted_data.FilterProcs(lambda p: 'data' in p.process())
            processes_without_weighted_data.AddSyst(cb, 'lumi_$ERA', 'lnN', ch.SystMap('era')(['13TeV_%s'%era], Constants.getLuminosityUncertainty(era)))

            # Cross-section uncertainties with PDF uncertainties, without scale uncertainties:
            #  - Single top: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SingleTopRefXsec
            #      - t channel: 0.029588519
            #      - tW channel: 0.056872038
            #      - s channel: 0.033615785
            #      - Combined uncertainty: 0.072387362
            #  - TT: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO
            #      - 0.053
            #  - DY: https://twiki.cern.ch/twiki/bin/view/CMS/SummaryTable1G25ns#DY_Z
            #      - M(ll) > 50: 0.037343159
            #      - M(ll) > 20: 0.051940354

            if not H.splitTTbarUncertBinByBin:
                #- ttxsc: {type: const, value: 1.0007626608267177 , on: 'TT'}   # uncer=0.5572
                #- TTTo2L2Nuxsc: {type: const, value: 1.0007627118644067 , on: 'TTTo2L2Nu'}  # uncer= 0.0585
                cb.cp().AddSyst(cb, 'ttbar_xsec', 'lnN', ch.SystMap('process')
                        (['ttbar'], 1.001525372691124) )
                
                #- ST_s-channel_4fxsc: {type: const, value: 1.0013622585438335, on: 'ST_schannel_4f'} # uncer= 0.004584
                #- ST_tW_top_5fxsc: {type: const, value: 1.0008007351010764, on: 'ST_tW_top_5f'}  # uncer= 0.0305
                #- ST_tW_antitop_5fxsc: {type: const, value: 1.00080204778157, on: 'ST_tW_antitop_5f'} # uncer= 0.03055
                cb.cp().AddSyst(cb, 'SingleTop_xsec', 'lnN', ch.SystMap('process')
                    (['SingleTop'], 1.0029650414264797) )
            
            #- DYJetsToLLxsc: {type: const, value: 1.0032721956406168, on: 'DYJetsToLL'}    # uncer= 61.55
            #- DYToLL_0Jxsc: {type: const, value: 1.0013216312802187, on: 'DYToLL_0J'} # uncer= 6.287
            #- DYToLL_2Jxsc: {type: const, value: 1.0032481644640234, on: 'DYToLL_2J'}   # uncer= 1.106
            cb.cp().AddSyst(cb, '$PROCESS_xsec', 'lnN', ch.SystMap('process') # shouldn't this be on dy process only 
                    (['DY'], 1.007841991384859) )

            if signal_strength:
                # FIXME ZA: this is completely random at this point
                #  - SM HH production: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/LHCHXSWGHH#Current_recommendations_for_di_H
                #      - m_h = 125.0 GeV
                cb.cp().AddSyst(cb, '$PROCESS_xsec', 'lnN', ch.SystMap('process')
                        ([sig_process], 1.0729) )

            for _, category_with_parameters in categories_with_parameters:
                for flavor in flavors:
                    for process in processes:
                        process = str(process)
                        if sig_process in process:
                            process = sig_process
                        if not process in cb.cp().channel([flavor]).process_set():
                                print("[{}, {}] Process '{}' not found, skipping systematics".format(category_with_parameters, flavor, process))
                        for s in systematics[flavor][category_with_parameters][process]:
                            s = str(s)
                            if H.ignoreSystematic(flavor, process, s):
                                print("[{}, {}, {}] Ignoring systematic '{}'".format(category_with_parameters, flavor, process, s))
                                continue

                            s = H.renameSystematic(flavor, process, s)
                            cb.cp().channel([flavor]).process([process]).AddSyst(cb, s, 'shape', ch.SystMap()(1.00))

        # Import shapes from ROOT file
        for flavor in flavors:
            cb.cp().channel([flavor]).backgrounds().ExtractShapes(file, '$BIN/$PROCESS_%s' % flavor, '$BIN/$PROCESS_%s__$SYSTEMATIC' % flavor)
            cb.cp().channel([flavor]).signals().ExtractShapes(file, '$BIN/$PROCESS_MH-%s_MA-%s_%s' % (p[0],p[1], flavor), '$BIN/$PROCESS_%s_%s__$SYSTEMATIC' % ('MH-%s_MA-%s'%(p[0],p[1]), flavor))

        # if you want to scale the signal rate by 1000
        #if scale:
        #    cb.cp().process(['HToZATo2L2B']).ForEachProc(lambda x : x.set_rate(x.rate()*1000))
        #    cb.cp().process(['HToZATo2L2B']).PrintProcs()

        # Bin by bin uncertainties
        if not stat_only:
            bkgs = cb.cp().backgrounds()
            bkgs.FilterProcs(lambda p: 'data' in p.process())
            bbb = ch.BinByBinFactory()
            bbb.SetAddThreshold(0.05).SetMergeThreshold(0.5).SetFixNorm(False)
            bbb.MergeBinErrors(bkgs)
            bbb.AddBinByBin(bkgs, cb)

        output_prefix = 'HToZATo2L2B_MH-%s_MA-%s' % (p[0],p[1])
        output_prefix_run = 'HToZATo2L2B_%s' % (formatted_e)

        output_dir = os.path.join(output, mode, H.get_method_group(method), 'MH-%s_MA-%s'%(p[0],p[1]))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        def createRunCombineScript(mass, output_dir, output_prefix):
            # Write small script to compute the limit
            datacard = os.path.join(output_dir, output_prefix + '.dat')
            workspace_file = os.path.basename(os.path.join(output_dir, output_prefix + '_combine_workspace.root'))

            if method == 'hybridnew':
                script = """#! /bin/bash
                    pushd {dir}
                    # If workspace does not exist, create it once
                    if [ ! -f {workspace_root} ]; then
                    text2workspace.py {datacard} -m {mass} -o {workspace_root}
                    fi
        
                    # Run limit
                    combine {method} --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}.log
                    combine {method} --expectedFromGrid=0.5 --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}_exp.log
                    combine {method} --expectedFromGrid=0.84 --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}_P1sigma.log
                    combine {method} --expectedFromGrid=0.16 --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}_M1sigma.log
                    combine {method} --expectedFromGrid=0.975 --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}_P2sigma.log
                    combine {method} --expectedFromGrid=0.025 --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}_M2sigma.log
                    popd
                """.format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, mass=mass, systematics=(0 if stat_only else 1), method=H.get_combine_method(method), dir=os.path.dirname(os.path.abspath(datacard))) 
            else:
                script = """#! /bin/bash
                    pushd {dir}
                    # If workspace does not exist, create it once
                    if [ ! -f {workspace_root} ]; then
                    text2workspace.py {datacard} -m {mass} -o {workspace_root}
                    fi
    
                    # Run limit
                    combine {method} --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}.log
                    popd
                """.format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, mass=mass, systematics=(0 if stat_only else 1), method=H.get_combine_method(method), dir=os.path.dirname(os.path.abspath(datacard)))
            
            script_file = os.path.join(output_dir, output_prefix + ('_run_%s.sh' % method))
            print( method, script_file)
            with open(script_file, 'w') as f:
                f.write(script)

            st = os.stat(script_file)
            os.chmod(script_file, st.st_mode | stat.S_IEXEC)

        # Write card
        def writeCard(c, mass, output_dir, output_prefix, script=True):
            datacard = os.path.join(output_dir, output_prefix + '.dat')
            c.cp().mass([mass, "*"]).WriteDatacard(datacard, os.path.join(output_dir, output_prefix + '_shapes.root'))
            if script:
                createRunCombineScript(mass, output_dir, output_prefix)

        print ("Writing datacards!")
        print (categories_with_parameters )
        mergeable_flavors = ['MuMu', 'ElEl', 'MuEl']
        if split_by_categories:
            for flavor in flavors:
                for i, cat in enumerate(categories_with_parameters):
                    cat_output_prefix = output_prefix + '_%s_cat_%s' % (flavor, cat[1])
                    writeCard(cb.cp().bin([cat[1]]).channel([flavor]), mass, output_dir, cat_output_prefix, i + 1 == len(categories_with_parameters))

            for i, cat in enumerate(categories_with_parameters):
                if all(x in flavors for x in mergeable_flavors):
                    print("Merging flavors datacards into a single one for {}".format(cat[1]))
                    # Merge all flavors into a single datacards
                    datacards = ["{flavor}={prefix}_{flavor}_cat_{category}.dat".format(prefix=output_prefix, flavor=x, category=cat[1]) for x in mergeable_flavors]
                    args = ['combineCards.py'] + datacards

                    merged_datacard_name = output_prefix + '_' + '_'.join(mergeable_flavors) + '_cat_' + cat[1]
                    merged_datacard = os.path.join(output_dir, merged_datacard_name + '.dat')
                    with open(merged_datacard, 'w') as f:
                        subprocess.check_call(args, cwd=output_dir, stdout=f)

                    createRunCombineScript(mass, output_dir, merged_datacard_name)
            
            for flavor in flavors:
                if mode == "postfit":
                    script = """#! /bin/bash
                        pushd {dir}
    
                        # Fit the rho distribution
                        ./{prefix}_cat_{categories}_run_fit.sh
        
                        # Create post-fit shapes for all the categories
                        for CAT in {categories}; do
                        text2workspace.py {prefix}_cat_${{CAT}}.dat -m {mass} -o {prefix}_cat_${{CAT}}_combine_workspace.root
                        PostFitShapesFromWorkspace -w {prefix}_cat_${{CAT}}_combine_workspace.root -d {prefix}_cat_${{CAT}}.dat -o postfit_shapes_${{CAT}}.root -f fitDiagnostics{prefix}_cat_${{CAT}}.root:fit_b -m {mass} --postfit --sampling --samples 1000 --print
        
                        $CMSSW_BASE/src/ZAStatAnalysis/utils/convertPostfitShapesForPlotIt.py -i postfit_shapes_${{CAT}}.root -o plotIt_{flavor} --signal-process HToZATo2L2B -n rho_steps

                        done
                        popd
                    """.format(prefix=output_prefix + '_' + flavor, flavor=flavor, mass=125, parameter='MH-%s_MA-%s'%(p[0],p[1]), categories=' '.join([x[1] for x in categories_with_parameters]), dir=os.path.abspath(output_dir))
                    script_file = os.path.join(output_dir, output_prefix + '_' + flavor + ('_do_postfit.sh'))
                    with open(script_file, 'w') as f:
                        f.write(script)

                    st = os.stat(script_file)
                    os.chmod(script_file, st.st_mode | stat.S_IEXEC)
        else:
            print ( flavor, flavors, cb.cp().channel([flavor]), mass, output_dir, output_prefix + "_" + flavor ) 
            
            for flavor in flavors:
                writeCard(cb.cp().channel([flavor]), mass, output_dir, output_prefix + "_" + flavor)
            if all(x in flavors for x in mergeable_flavors):
                print("Merging flavors datacards into a single one")
                # Merge all flavors into a single datacards
                datacards = ["{flavor}={prefix}_{flavor}.dat".format(prefix=output_prefix, flavor=x) for x in mergeable_flavors]
                args = ['combineCards.py'] + datacards

                merged_datacard = os.path.join(output_dir, output_prefix + '_' + '_'.join(mergeable_flavors) + '.dat')
                with open(merged_datacard, 'w') as f:
                    subprocess.check_call(args, cwd=output_dir, stdout=f)

                createRunCombineScript(mass, output_dir, output_prefix + '_' + '_'.join(mergeable_flavors))

if __name__ == '__main__':
    """
    Parse and return arguments provided by the user
    """
    parser = argparse.ArgumentParser(description='Create shape datacards ready for combine')
    parser.add_argument('-i', '--input',        action='store', dest='input', type=str, default='ul__combinedlimits/ul2016_cards__ver1', 
                                                help='histFactory input path: those are the histograms for signal/data/backgrounds that pass through all the following steps: final selection(2l+bjets pass btagging discr cut ) -> make skim -> train the DNN using these skimmed trees -> pass to BAMBOO to produce your dnn output ( prefit-plot) need here for Combined .')
    parser.add_argument('-e', '--era',          action='store', dest='era',       type=str, default= '2016',   
                                                help='you need to pass your era')
    parser.add_argument('-p', '--parameters',   nargs='+', metavar='MH,MA', dest='parameters', type=parameter_type, default=['all'],               
                                                help='Parameters list. Use `all` as an alias for all parameters')
    parser.add_argument('-o', '--output',       action='store', dest='output', type=str, default='ul__combinedlimits/ul2016_cards__ver1',        
                                                help='Output directory')
    parser.add_argument('-s', '--stat',         action='store_true', dest='stat_only',                                                            
                                                help='Do not consider systematic uncertainties')
    parser.add_argument('-a', '--mode',         action='store', dest='mode', type=str, default='dnn', choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'postfit', 'mjj', 'mlljj', 'ellipse', 'dnn'],
                                                help='Analysis mode')
    parser.add_argument('-n', '--node',         action='store', dest='node', type=str, default='ZA', choices=['DY', 'TT', 'ZA'],
                                                help='DNN nodes')
    parser.add_argument('--method',             action='store', dest='method', type=str, default='asymptotic', choices=['asymptotic', 'hybridnew', 'fit'],        
                                                help='Analysis method')
    parser.add_argument('--unblind',            action='store_true', dest='unblind',
                                                help='Use fake data instead of real data')
    parser.add_argument('--signal-strength',    action='store_true', dest="signal_strength",                                                   
                                                help='Put limit on the signal strength instead of the cross-section')
    parser.add_argument('--ellipses-mumu-file', action='store', dest='ellipses_mumu_file', default='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZATools/scripts_ZA/ellipsesScripts/vers20.06.03Inputs/fullEllipseParamWindow_MuMu.json',
                                                help='file containing the ellipses parameters for MuMu (ElEl is assumed to be in the same directory)')
    parser.add_argument('-v', '--verbose',      action='store_true', required=False,
                                                help='For debugging purposes , you may consider this argument !')

    options = parser.parse_args()
    options.mode = options.mode.lower()

    prepare_DataCards(grid_data= signal_grid + extra_signals, era=options.era, parameters=options.parameters, mode=options.mode, input=options.input, ellipses_mumu_file=options.ellipses_mumu_file, output=options.output, method=options.method, node=options.node, unblind=options.unblind, signal_strength=options.signal_strength, stat_only=options.stat_only, verbose=options.verbose, split_by_categories=True)

