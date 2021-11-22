#! /bin/env python
# https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part2/bin-wise-stats/
import os, os.path, sys, stat, argparse, getpass, json
import subprocess
import json
import glob
import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True

from math import sqrt
from datetime import datetime

import numpy as np
import Harvester as H
import Constants as Constants
import CombineHarvester.CombineTools.ch as ch
logger = Constants.ZAlogger(__name__)

def get_Nm_for_runmode(mode): 
    Nm_formode = {'ellipse':'rho_steps',
                  'dnn'    :'dnn_scores',
                  'mjj'    :'mjj_bins',
                  'mlljj'  :'mlljj_bins',
                  'mjj_vs_mlljj' : 'mjj_vs_mlljj_map',
                  'mjj_and_mlljj': 'mjj_and_mlljj_combined_bins', }
    return Nm_formode[mode]

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

def get_signal_parameters(f):
    # HToZATo2L2B_MH-200_MA-50.root
    split_filename = f.replace('.root','').replace('HToZATo2L2B_','')
    split_filename = split_filename.split('_')
    MH = split_filename[0].split('-')[1]
    MA = split_filename[1].split('-')[1]
    return int(MH), int(MA)


signal_grid = [
        #part0 : 21 signal samples 
        ( 200, 50), ( 200, 100), ( 300, 100),
        ( 250, 50), ( 250, 100),
        #( 300, 50), ( 300, 200),
        #( 500, 50), ( 500, 200), ( 500, 400),
        #( 650, 50),
        #( 800, 50), ( 800, 200), ( 800, 400), ( 800, 700),
        #(1000, 50), (1000, 200), (1000, 500), 
        #(2000, 1000),
        #(3000, 2000) 
        ]
extra_signals = [
        ]
    
def prepare_DataCards(grid_data= None, dataset= None, expectSignal= None, era= None, parameters= None, mode= None, input= None, ellipses_mumu_file= None, output= None, method= None, node= None, unblind= False, signal_strength= False, stat_only= False, verbose= False, split_by_categories= False, scale= False):
    
    luminosity = Constants.getLuminosity(era)
    
    signal_grid = list(set(grid_data))
    parameters = []
    for f in glob.glob(os.path.join(options.input, '*.root')):
        split_filename = f.split('/')[-1]
        if not split_filename.startswith('HToZATo2L2B_'):
            continue
        mH, mA = get_signal_parameters(split_filename)
        if (mH, mA) in signal_grid:
            parameters.append( (mH, mA) )
    
    if signal_strength:
        parameters = [( 500, 300)]
    if len(parameters) == 1 and parameters[0] == 'all':
        parameters = parameters[:]
    for p in parameters:
        if not p in parameters:
            logger.warning("Invalid parameter '%s'. Valid values are %s" % (str(p), str(parameters)))
            return

    logger.info("Era and the corresponding luminosity      : %s, %s" %(era, Constants.getLuminosity(era)))
    logger.info("Input path                                : %s" %input )
    logger.info("Generating set of cards for parameter(s)  : %s" % (', '.join([str(x) for x in parameters])))
    logger.info("Chosen analysis mode                      : %s" % mode)

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
    
    prepareShapes(input                 = input, 
                 dataset                = dataset, 
                 expectSignal           = expectSignal, 
                 era                    = era, 
                 method                 = method, 
                 parameters             = parameters, 
                 productions            = ['gg_fusion', 'bb_associatedProduction'], 
                 regions                = ['resolved', 'boosted'], 
                 flavors                = ['MuMu', 'ElEl'], 
                 ellipses               = ellipses, 
                 mode                   = mode,  
                 output                 = output, 
                 luminosity             = luminosity, 
                 split_by_categories    = split_by_categories, 
                 scale                  = scale, 
                 unblind                  = unblind, 
                 signal_strength        = signal_strength, 
                 stat_only              = stat_only, 
                 verbose                = verbose)

    # Create helper script to run limits
    output = os.path.join(output, mode)
    print( '\tThe generated script to run limits can be found in : %s/' %output)
    script = """#! /bin/bash
scripts=`find {output} -name "*_run_{method}.sh"`
for script in $scripts; do
    dir=$(dirname $script)
    script=$(basename $script)
    echo "\tComputing with ${{script}}"
    pushd $dir &> /dev/null
    . $script
    popd &> /dev/null
done
""".format(output=output, method=method)
    
    script_name = "run_combined_%s_%s.sh" % (mode, method)
    with open(script_name, 'w') as f:
        f.write(script)

    st = os.stat(script_name)
    os.chmod(script_name, st.st_mode | stat.S_IEXEC)

    if method=="hybridnew":
        logger.info("All done. You can run everything by executing %r" % ('./' + script_name[:-3]+"_onSlurm.sh"))
    else:
        logger.info("All done. You can run everything by executing %r" % ('./' + script_name))


def prepareShapes(input=None, dataset=None, expectSignal=None, era=None, method=None, parameters=None, productions=None, regions=None, flavors=None, ellipses=None, mode=None, output=None, luminosity=None, split_by_categories=False, scale=False, unblind=False, signal_strength=False, stat_only=False, verbose=False):
    
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
                # % ( MH, MA)
                (1, 'dnn_MH_{}_MA_{}')
                # % (flavour, ellipse_index)
                #(2, 'ellipse_{}_{}'),
                #(3, 'mlljj'),
                #(4, 'mjj'),
                #(5, 'mjj_vs_mlljj')
                ]
    elif mode == "dnn":
        categories = [
                # % ( prod, reg, MH, MA)
                (1, 'dnn_MH_{}_MA_{}')
                ]

    histfactory_to_combine_categories = {}
    histfactory_to_combine_processes  = {
            # main Background
            'ttbar'    : ['^TT*', '^ttbar_*'],  
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
    if options.mode == "postfit":
        for p in parameters:
            mH = p[0]
            mA = p[1]
            
            formatted_p = format_parameters(p)
            formatted_e = format_ellipse(p, ellipses)
           
            histfactory_to_combine_categories = {
                'dnn_MH_{}_MA_{}'.format(mH, mA) : get_hist_regex('DNNOutput_ZAnode_{flavor}_{reg}_DeepCSVM_METCut_{prod}_MH_%s_MA_%s'%(mH, mA)),
                #'ellipse_{}_{}'.format(formatted_p, formatted_e):    get_hist_regex('rho_steps_histo_{flavor}_hZA_lljj_deepCSV_btagM_mll_and_met_cut_%s' % format_ellipse(p, ellipses)),
                #'mjj':      get_hist_regex('jj_M_{flavor}_hZA_lljj_deepCSV_btagM_'),
                #'mlljj': get_hist_regex('lljj_M_{flavor}_hZA_lljj_deepCSV_btagM_'),
            }
    # Shape depending on the signal hypothesis
    for p in parameters:
        mH = p[0]
        mA = p[1]
        
        formatted_p = format_parameters(p)
        formatted_e = format_ellipse(p, ellipses)
        
        suffix = formatted_p.replace('MH_', 'MH-').replace('MA_','MA-')
        histfactory_to_combine_processes['HToZATo2L2B_MH-%s_MA-%s'%(mH,mA), p] = ['^HToZATo2L2B_MH-%s_MA-%s*'%(mH, mA), '^GluGluToHToZATo2L2B_MH-%s_MA-%s*']
        
        if mode == "postfit":
            histfactory_to_combine_categories[('dnn_MH_{}_MA_{}'.format(mH, mA), p)] = get_hist_regex('DNNOutput_ZAnode_{flavor}_{reg}_DeepCSVM_METCut_{prod}_MH_%s_MA_%s'%(mH, mA))
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
            histfactory_to_combine_categories[('ellipse_{}_{}'.format(formatted_p, formatted_e), p)] = get_hist_regex('rho_steps_resolved_histo_{flavor}_hZA_lljj_DeepCSV_btagM__METCut__%s'%formatted_p)
        elif mode == "dnn": 
            histfactory_to_combine_categories[('dnn_MH_{}_MA_{}'.format(mH, mA), p)] = get_hist_regex('DNNOutput_ZAnode_{flavor}_{reg}_DeepCSVM_METCut_{prod}_MH_%s_MA_%s'%(mH, mA))
    logger.info('Histfactory_to_combine_categories         : %s '%histfactory_to_combine_categories )
    
    if unblind:
        histfactory_to_combine_processes['data_obs'] = ['^DoubleMuon*', '^DoubleEG*', '^MuonEG*', '^SingleMuon*', '^EGamma*']
    
    H.splitJECBySources = False
    if signal_strength:
        H.scaleZAToSMCrossSection = True
    H.splitTTbarUncertBinByBin = False

    file, systematics = H.prepareFile(processes_map       = histfactory_to_combine_processes, 
                                      categories_map      = histfactory_to_combine_categories, 
                                      input               = input, 
                                      output_filename     = os.path.join(output, 'shapes_HToZATo2L2B.root'), 
                                      signal_process      = 'HToZATo2L2B', 
                                      method              = method, 
                                      luminosity          = luminosity, 
                                      flavors             = flavors, 
                                      regions             = regions, 
                                      productions         = productions, 
                                      era                 = era, 
                                      unblind             = unblind)
    flav_categories = []
    for prod in productions:
        for reg in regions:
            for flavor in flavors:
                cat = '{}_{}_{}'.format(prod, reg, flavor)
                flav_categories.append(cat)

    #print ( "\tsystematics : %s       :" %systematics )
    for i, p in enumerate(parameters):
        mH = p[0]
        mA = p[1]
        
        cb = ch.CombineHarvester()
        if verbose:
            cb.SetVerbosity(3)
        cb.SetFlag("zero-negative-bins-on-import", True)

        # Dummy mass value used for all combine input when a mass is needed
        mass = "125"
        formatted_p = format_parameters(p)
        formatted_e = format_ellipse(p, ellipses)

        analysis_name = 'HToZATo2L2B'
        categories_with_parameters = categories[:]
        for i, k in enumerate(categories_with_parameters):
            if mode in ['dnn', 'postfit']:
                categories_with_parameters[i] = (k[0], k[1].format(mH, mA))
            elif mode == 'ellipse':
                categories_with_parameters[i] = (k[0], k[1].format('MH-%s_MA-%s'%(mH, mA), formatted_e))
            else:
                print( 'FIXME' )
        logger.info( 'looking for categories_with_parameters      :  %s '%categories_with_parameters) 
        #cb.AddObservations( mass, analysis, era, channel, bin)
        cb.AddObservations(['*'], [analysis_name], ['13TeV_%s'%era], flav_categories, categories_with_parameters)
        bkg_processes = [
                'ttbar',
                'SingleTop',
                'DY',
                #'WPlusJets',
                #'ttV',
                #'VV',
                #'VVV',
                #'Wgamma',
                #'SMHiggs'
                ]

        # FIXME I am not sure if this intended or a mistake 
        for cat in flav_categories:
            processes = []
            cb.AddProcesses(['*'], [analysis_name], ['13TeV_%s'%era], [cat], bkg_processes, categories_with_parameters, False)
            processes += bkg_processes
        
        sig_process = 'HToZATo2L2B'
        cb.AddProcesses([mass], [analysis_name], ['13TeV_%s'%era], flav_categories, [sig_process], categories_with_parameters, True)
        processes  += [sig_process]
        logger.info( "Processes       : %s" %processes)
        
        if not stat_only:
            processes_without_weighted_data = cb.cp()
            processes_without_weighted_data.FilterProcs(lambda p: 'data' in p.process())
            processes_without_weighted_data.AddSyst(cb, 'lumi_$ERA', 'lnN', ch.SystMap('era')(['13TeV_%s'%era], Constants.getLuminosityUncertainty(era)))

            if not H.splitTTbarUncertBinByBin:
                cb.cp().AddSyst(cb, 'ttbar_xsec', 'lnN', ch.SystMap('process')
                        (['ttbar'], 1.001525372691124) )
            cb.cp().AddSyst(cb, 'SingleTop_xsec', 'lnN', ch.SystMap('process')
                    (['SingleTop'], 1.0029650414264797) )
            cb.cp().AddSyst(cb, 'DY_xsec', 'lnN', ch.SystMap('process') 
                    (['DY'], 1.007841991384859) )
            if signal_strength:
                # https://twiki.cern.ch/twiki/bin/view/LHCPhysics/LHCHXSWGHH#Current_recommendations_for_di_H
                cb.cp().AddSyst(cb, '$PROCESS_xsec', 'lnN', ch.SystMap('process')
                    ([sig_process], 1.0729) )

            for _, category_with_parameters in categories_with_parameters:
                for cat in flav_categories:
                    for process in processes:
                        process = str(process)
                        if sig_process in process:
                            process = sig_process
                        if not process in cb.cp().channel([cat]).process_set():
                            print("[{}, {}] Process '{}' not found, skipping systematics".format(category_with_parameters, cat, process))
                        for s in systematics[cat][category_with_parameters][process]:
                            s = str(s)
                            if H.ignoreSystematic(cat, process, s):
                                print("[{}, {}, {}] Ignoring systematic '{}'".format(category_with_parameters, cat, process, s))
                                continue
                            cb.cp().channel([cat]).process([process]).AddSyst(cb, s, 'shape', ch.SystMap()(1.00))

        # Import shapes from ROOT file
        for cat in flav_categories:
            cb.cp().channel([cat]).backgrounds().ExtractShapes(file, '$BIN/$PROCESS_%s' %cat, '$BIN/$PROCESS_%s__$SYSTEMATIC' %cat)
            cb.cp().channel([cat]).signals().ExtractShapes(file, '$BIN/$PROCESS_MH-%s_MA-%s_%s' % (p[0],p[1], cat), '$BIN/$PROCESS_%s_%s__$SYSTEMATIC' % ('MH-%s_MA-%s'%(p[0],p[1]), cat))

        if scale:
            cb.cp().process(['HToZATo2L2B']).ForEachProc(lambda x : x.set_rate(x.rate()*1000))
            cb.cp().process(['HToZATo2L2B']).PrintProcs()

        # Bin by bin uncertainties
        if not stat_only:
            bkgs = cb.cp().backgrounds()
            bkgs.FilterProcs(lambda p: 'data' in p.process())
            bbb = ch.BinByBinFactory()
            bbb.SetAddThreshold(0.05).SetMergeThreshold(0.5).SetFixNorm(False)
            bbb.MergeBinErrors(bkgs)
            bbb.AddBinByBin(bkgs, cb)

        output_prefix      = 'HToZATo2L2B'
        #output_prefix_run = 'HToZATo2L2B_%s' % (formatted_e)
        
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
# Run combined
#combine {method} --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} {dataset} --expectSignal {expectSignal} {blind} &> {name}.log
combine {method} -m {mass} -n {name} {workspace_root} {dataset} --expectSignal {expectSignal} {blind} &> {name}.log
popd
""".format(workspace_root=workspace_file, datacard=os.path.basename(datacard), name=output_prefix, mass=mass, systematics=(0 if stat_only else 1), method=H.get_combine_method(method), dir=os.path.dirname(os.path.abspath(datacard)), dataset=('-t -1' if dataset=='asimov' else '-t 8 -s -1'), blind=('' if unblind else '--run blind'), expectSignal=expectSignal)
            
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

        logger.info("Writing datacards!")
        print (categories_with_parameters )

        if split_by_categories:
            for flavor in flav_categories:
                for i, cat in enumerate(categories_with_parameters):
                    cat_output_prefix = output_prefix + '_%s_%s' % (flavor, cat[1])
                    writeCard(cb.cp().bin([cat[1]]).channel([flavor]), mass, output_dir, cat_output_prefix, i + 1 == len(categories_with_parameters))
            
            mergeable_regions = ['resolved', 'boosted']
            mergeable_flavors = ['ElEl', 'MuMu']
            for prod in productions:
                for i, cat in enumerate(categories_with_parameters):
                    if all(x in flavors for x in mergeable_flavors) and all(x in regions for x in mergeable_regions):
                        print("Merging {} datacards into a single one for {}".format(flavors, cat[1]))
                        # Merge all flavors into a single datacards
                        datacards = ["{flavor}={prefix}_{prod}_{reg}_{flavor}_{category}.dat".format(prefix=output_prefix, prod=prod, reg=y, flavor=x, category=cat[1]) for x in mergeable_flavors for y in mergeable_regions]
                        args      = ['combineCards.py'] + datacards
                        
                        merged_datacard_name = output_prefix + '_'+ prod +'_'+ '_'.join(mergeable_regions) + '_'+ '_'.join(mergeable_flavors) + '_' + cat[1]
                        merged_datacard      = os.path.join(output_dir, merged_datacard_name + '.dat')
                        with open(merged_datacard, 'w') as f:
                            subprocess.check_call(args, cwd=output_dir, stdout=f)

                        createRunCombineScript(mass, output_dir, merged_datacard_name)
            
            for cat in flav_categories:
                if mode == "postfit":
                    name = get_Nm_for_runmode('dnn')
                    script = """#! /bin/bash
pushd {dir}
# Fit the {name} distribution
./{prefix}_{categories}_run_fit.sh

# Create post-fit shapes for all the categories
for CAT in {categories}; do
    text2workspace.py {prefix}_${{CAT}}.dat -m {mass} -o {prefix}_${{CAT}}_combine_workspace.root
    PostFitShapesFromWorkspace -w {prefix}_${{CAT}}_combine_workspace.root -d {prefix}_${{CAT}}.dat -o postfit_shapes_${{CAT}}.root -f fitDiagnostics{prefix}_${{CAT}}.root:fit_b -m {mass} --postfit --sampling --samples 1000 --print
    $CMSSW_BASE/src/ZAStatAnalysis/utils/convertPostfitShapesForPlotIt.py -i postfit_shapes_${{CAT}}.root -o plotIt_{flavor} --signal-process HToZATo2L2B -n {name}
done
popd
""".format(prefix=output_prefix + '_' + cat, flavor=cat, mass=125, parameter='MH-%s_MA-%s'%(mH,mA), categories=' '.join([x[1] for x in categories_with_parameters]), dir=os.path.abspath(output_dir), name=name)
                    script_file = os.path.join(output_dir, output_prefix + '_' + cat + ('_do_postfit.sh'))
                    with open(script_file, 'w') as f:
                        f.write(script)

                    st = os.stat(script_file)
                    os.chmod(script_file, st.st_mode | stat.S_IEXEC)
        else:
            mergeable_regions = ['resolved', 'boosted']
            mergeable_flavors = ['ElEl', 'MuMu']
            for cat in flav_categories:
                writeCard(cb.cp().channel([cat]), mass, output_dir, output_prefix + "_" + cat)
            if all(x in flavors for x in mergeable_flavors) and all(x in regions for x in mergeable_regions):
                print("Merging flavors datacards into a single one")
                # Merge all flavors into a single datacards
                datacards = ["{flavor}={prefix}_{prod}_{reg}_{flavor}_{category}.dat".format(prefix=output_prefix, prod=prod, reg=y, flavor=x, category=cat[1]) for x in mergeable_flavors for y in mergeable_regions]
                args      = ['combineCards.py'] + datacards

                merged_datacard_name = output_prefix + '_'+ prod +'_'+ '_'.join(mergeable_regions) + '_'+ '_'.join(mergeable_flavors) + '_' + cat[1]
                with open(merged_datacard, 'w') as f:
                    subprocess.check_call(args, cwd=output_dir, stdout=f)
                
                createRunCombineScript(mass, output_dir, output_prefix + '_' + '_'.join(mergeable_flavors))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create shape datacards ready for combine')
    parser.add_argument('-i', '--input',        action='store', dest='input', type=str, required=True, default=None, 
                                                help='HistFactory input path: those are the histograms for signal/data/backgrounds that pass through all the following \n'
                                                     'steps: 1/- final selection ( 2l+bjets pass btagging discr cut + met + corrections + etc... ) \n'
                                                     '       2/- do skim  \n'
                                                     '       3/- DNN trained using these skimmed trees \n'
                                                     '       4/- run bamboo to produce your dnn outputs(prefit plots) with all systematics variations using the model you get from training.\n')
    parser.add_argument('-o', '--output',       action='store', dest='output', required=True, default=None,        
                                                help='Output directory')
    parser.add_argument('-s', '--stat',         action='store_true', dest='stat_only', required=False, default=False,                                                           
                                                help='Do not consider systematic uncertainties')
    parser.add_argument('-v', '--verbose',      action='store_true', required=False, default=False, 
                                                help='For debugging purposes , you may consider this argument !')
    parser.add_argument('--era',                action='store', dest='era', required=True, default=None, choices=['2016', '2017', '2018'],
                                                help='You need to pass your era')
    parser.add_argument('--parameters',         nargs='+', metavar='MH,MA', dest='parameters', type=parameter_type, default=['all'],               
                                                help='Parameters list. Use `all` as an alias for all parameters')
    parser.add_argument('--expectSignal',       action='store', required=True, type=int, choices=[0, 1],
                                                help=' Is this S+B fit B-Only  ? ')
    parser.add_argument('--mode',               action='store', dest='mode', default='dnn', choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'postfit', 'mjj', 'mlljj', 'ellipse', 'dnn'],
                                                help='Analysis mode')
    parser.add_argument('--node',               action='store', dest='node', default='ZA', choices=['DY', 'TT', 'ZA'],
                                                help='DNN nodes')
    parser.add_argument('--method',             action='store', dest='method', required=True, default=None, choices=['asymptotic', 'hybridnew', 'fit'],        
                                                help='Analysis method')
    parser.add_argument('--unblind',            action='store_true', dest='unblind', required=False,
                                                help='Use fake data instead of real data')
    parser.add_argument('--signal-strength',    action='store_true', dest="signal_strength", required=False, default=False,                                                  
                                                help='Put limit on the signal strength instead of the cross-section')
    parser.add_argument('--ellipses-mumu-file', action='store', dest='ellipses_mumu_file', required=False, default='./data/fullEllipseParamWindow_MuMu.json',
                                                help='file containing the ellipses parameters for MuMu (ElEl is assumed to be in the same directory)')
    parser.add_argument('--scale',              action='store_true', dest='scale', required=False, default=False,                                                  
                                                help='scale signal rate')
    parser.add_argument('--dataset',            action='store', dest='dataset', choices=['toys', 'asimov'], required=True, default=None,                             
                                                help='if asimov:\n'
                                                        '-t -1 will produce an Asimov dataset in which statistical fluctuations are suppressed. \n'
                                                     'if toys: \n'
                                                        '-t N with N > 0. Combine will generate N toy datasets from the model and re-run the method once per toy. \n'
                                                        'The seed for the toy generation can be modified with the option -s (use -s -1 for a random seed). \n'
                                                        'The output file will contain one entry in the tree for each of these toys.\n')
    options = parser.parse_args()
    options.mode = options.mode.lower()

    prepare_DataCards(grid_data= signal_grid + extra_signals, dataset= options.dataset, expectSignal=options.expectSignal, era=options.era, parameters=options.parameters, mode=options.mode, input=options.input, ellipses_mumu_file=options.ellipses_mumu_file, output=options.output, method=options.method, node=options.node, unblind=options.unblind, signal_strength=options.signal_strength, stat_only=options.stat_only, verbose=options.verbose, split_by_categories=True, scale=options.scale)
