#! /bin/env python
# https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part2/bin-wise-stats/
# https://cms-analysis.github.io/CombineHarvester/python-interface.html#py-filtering
# https://twiki.cern.ch/twiki/bin/view/LHCPhysics/LHCHXSWGHH#Current_recommendations_for_di_H

import os, os.path, sys
import stat, argparse
import subprocess
import shutil
import json
import yaml
import random
import glob
import ROOT

ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True

from collections import defaultdict

#import numpy as np

import Harvester as H
import Constants as Constants
import CombineHarvester.CombineTools.ch as ch

logger = Constants.ZAlogger(__name__)


signal_grid_foTest = { 
    'gg_fusion': { 
        'resolved': { 
            'HToZA': [(500., 300)],   #(240.0, 130.0), (300.0, 135.0), (700.0, 200.0), (250.0, 125.0), (750.0, 610.0), (500.0, 250.0), (800.0, 140.0), (200.0, 125.0), (510.0, 130.0), (780.0, 680.0), (220.0, 127.0), (670.0, 500.0), (550.0, 300.0)],
            'AToZH': []},             #(240.0, 130.0), (300.0, 135.0), (700.0, 200.0), (250.0, 125.0), (750.0, 610.0), (500.0, 250.0), (800.0, 140.0), (200.0, 125.0), (510.0, 130.0), (780.0, 680.0), (220.0, 127.0), (670.0, 500.0), (550.0, 300.0)] },
        'boosted': {
            'HToZA': [(500., 300.)], #(240.0, 130.0), (300.0, 135.0), (700.0, 200.0), (250.0, 125.0), (750.0, 610.0), (500.0, 250.0), (800.0, 140.0), (200.0, 125.0), (510.0, 130.0), (780.0, 680.0), (220.0, 127.0), (670.0, 500.0), (550.0, 300.0)], 
            'AToZH': []},            #(240.0, 130.0), (300.0, 135.0), (700.0, 200.0), (250.0, 125.0), (750.0, 610.0), (500.0, 250.0), (800.0, 140.0), (200.0, 125.0), (510.0, 130.0), (780.0, 680.0), (220.0, 127.0), (670.0, 500.0), (550.0, 300.0)] }
        },
    'bb_associatedProduction': { 
        'resolved': { 
            'HToZA': [(500., 300.)], #(240.0, 130.0), (300.0, 135.0), (700.0, 200.0), (250.0, 125.0), (750.0, 610.0), (500.0, 250.0), (800.0, 140.0), (200.0, 125.0), (510.0, 130.0), (780.0, 680.0), (220.0, 127.0), (670.0, 500.0), (550.0, 300.0)],
            'AToZH': []},           #(240.0, 130.0), (300.0, 135.0), (700.0, 200.0), (250.0, 125.0), (750.0, 610.0), (500.0, 250.0), (800.0, 140.0), (200.0, 125.0), (510.0, 130.0), (780.0, 680.0), (220.0, 127.0), (670.0, 500.0), (550.0, 300.0)] },
        'boosted': {
            'HToZA': [(500., 300.)], #(240.0, 130.0), (300.0, 135.0), (700.0, 200.0), (250.0, 125.0), (750.0, 610.0), (500.0, 250.0), (800.0, 140.0), (200.0, 125.0), (510.0, 130.0), (780.0, 680.0), (220.0, 127.0), (670.0, 500.0), (550.0, 300.0)],
            'AToZH': []}            #(240.0, 130.0), (300.0, 135.0), (700.0, 200.0), (250.0, 125.0), (750.0, 610.0), (500.0, 250.0), (800.0, 140.0), (200.0, 125.0), (510.0, 130.0), (780.0, 680.0), (220.0, 127.0), (670.0, 500.0), (550.0, 300.0)] }
        }
    }


def mass_to_str(m, _p2f=True):
    if _p2f: m = "%.2f"%m
    return str(m).replace('.','p')


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
            

def return_flavours_to_process(reco, reg, prod, splitLep=False):
    flavors = []
    if reco =='nb3' or reg =='boosted' or prod =='bb_associatedProduction':
        flavors = [['OSSF', 'MuEl'], ['OSSF'], ['MuEl']]
        if H.splitLep:
            flavors += [['MuMu', 'ElEl'], ['MuMu', 'ElEl', 'MuEl'], ['MuMu'], ['ElEl']]
    else:
        flavors = [['MuMu', 'ElEl', 'MuEl'], ['MuMu', 'ElEl'], ['MuMu'], ['ElEl'], ['MuEl'], ['OSSF'], ['OSSF', 'MuEl']]

    if reco =='nb2PLusnb3' and H.splitLep:
        flavors += [['split_OSSF'], ['split_OSSF', 'MuEl']]
    return flavors


def check_call_DataCard(method, cmd, thdm, mode, output_dir, expectSignal, dataset, opts, era, verbose, unblind=False, what='', run_validation=False, multi_signal=False):
    k      = opts['flavor']
    reco   = opts['nb'] + '_'+ opts['region']
    prod   = opts['process']
    newCmd = ['combineCards.py']
    
    for i, x in enumerate(cmd):
        if "=" in x :
            Tot_nm   = x.split('=')[1]
            channel  = x.split('=')[0]
            split_ch = channel.split('_')
            new_ch   = 'ch%s_%s'%(i+1, '_'.join(split_ch[1:]))
            newCmd  +=[new_ch+'='+Tot_nm]
        else:
            newCmd  +=[x]
            
    out_nm = cmd[0]
    if '=' in out_nm:
        out_nm  = out_nm.split('=')[1]

    suffix        = out_nm.split(mode)[-1].replace('.dat', '')
    output_prefix = '%sTo2L2B_%s_%s_%s_%s%s'%( thdm, prod, reco, k, mode, suffix)
    datacard      = os.path.join(output_dir, output_prefix +'.dat')
    
    logger.info('merging %s %s cmd::: %s'%(k, what, newCmd))
    with open( datacard, 'w') as f:
        subprocess.check_call(newCmd, cwd=output_dir, stdout=f)
    
    workspace_file = os.path.basename(os.path.join(output_dir, output_prefix + '_combine_workspace.root'))
    if method =='asymptotic':
        if multi_signal: 
            for poi in ['r_ggH', 'r_bbH']:
                MultiSignalModel(workspace_file, datacard, output_prefix, output_dir, 125, 'asymptotic', expectSignal, poi, run_validation, unblind, verbose)
        else:
            _AsymptoticLimits(workspace_file, datacard, output_prefix, output_dir, 125, 'asymptotic', expectSignal, dataset, run_validation, unblind, verbose)
    
    elif method =='impacts':
        _PullsImpacts(workspace_file, output_prefix, output_dir, datacard, 125, k, 'impacts', prod, reco, dataset, expectSignal, run_validation, unblind, verbose)
    
    elif method =='likelihood_fit':
        if multi_signal:
            Likelihood_FitsScans(workspace_file, datacard, output_prefix, output_dir, 125, 'likelihood_fit', run_validation, unblind, verbose)
   
    elif method =='goodness_of_fit':
        Goodness_of_fit_tests(workspace_file, datacard, output_prefix, output_dir, 125, method, mode, opts, era, run_validation, unblind, verbose)
    return 


def CustomCardCombination(thdm, mode, cats, proc_combination, expectSignal, dataset, method, prod, era, verbose, reg=None, skip=None, unblind=False, _2POIs_r=False, run_validation=False, multi_signal=False, todo=''):
    
    if method in ['fit', 'generatetoys']:
        return 
    
    keys = ['OSSF', 'OSSF_MuEl', 'split_OSSF', 'split_OSSF_MuEl']
     
    for cat in cats:
        
        output_dir = cat[0]
        output_sig = cat[1]
        if Constants.cat_to_tuplemass(output_sig) in skip:
            continue
        
        for k in keys:
            if not H.splitLep and k in ['split_OSSF', 'split_OSSF_MuEl']:
                continue

            if todo == 'nb2_nb3':
                if not ( cat in proc_combination['nb2_%s'%reg].keys() or cat in proc_combination['nb3_%s'%reg].keys()):
                    continue
                
                kp = k
                if not 'split' in k and reg =='resolved' and prod =='gg_fusion':
                    kp = 'split_'+k
                
                cmd = proc_combination['nb2_%s'%reg][cat][kp] + proc_combination['nb3_%s'%reg][cat][k]
                if not cmd:
                    continue
                
                opts = {'process': prod, 'nb': 'nb2PLusnb3', 'region': reg, 'flavor': k }
                check_call_DataCard(method, cmd, thdm, mode, output_dir, expectSignal, dataset, 
                                    opts            = opts,
                                    unblind         = unblind, 
                                    what            = 'nb2 & nb3 %s'%reg,
                                    era             = era,
                                    verbose         = verbose, 
                                    run_validation  = run_validation, 
                                    multi_signal    = multi_signal )

            elif todo == 'res_boo':
                if not (cat in proc_combination['nb2_resolved'].keys() or cat in proc_combination['nb2_boosted'].keys()
                        or cat in proc_combination['nb3_resolved'].keys() or cat in proc_combination['nb3_boosted'].keys()
                        ):
                    continue
                cmd = []
                
                for reco in ['nb2_resolved', 'nb2_boosted', 'nb3_resolved', 'nb3_boosted']:
                    
                    kp = k
                    if not 'split' in k and reco =='nb2_resolved' and prod =='gg_fusion':
                        kp = 'split_'+k
                    
                    cmd += proc_combination[reco][cat][kp]
                opts = {'process': prod, 'nb': 'nb2PLusnb3', 'region': 'resolved_boosted', 'flavor': k }
                check_call_DataCard(method, cmd, thdm, mode, output_dir, expectSignal, dataset, 
                                    opts            = opts,
                                    unblind         = unblind, 
                                    what            = 'resolved & boosted ( nb2 + nb3)', 
                                    era             = era,
                                    verbose         = verbose, 
                                    run_validation  = run_validation, 
                                    multi_signal    = multi_signal )
            
           ## deprecated !! 
           # elif todo == 'ggH_bbH':
           #     if not method in ['likelihood_fit', 'asymptotic']:
           #         continue
           #     # this should not happen but in case a signal sample does not exist in both prod mechanisms
           #     # then there is no need to continue here
           #     if any( x== output_sig for x in skip):
           #         continue
           #     
           #     Tot_proc_reg_combine = []
           #     for j, reg in enumerate(['resolved', 'boosted']): 
           #         
           #         cmd = [] 
           #         for reco in ['nb2', 'nb3']: 
           #         
           #             for prod in ['gg_fusion', 'bb_associatedProduction']:
           #                 cmd += proc_combination[prod][reco+'_'+reg][cat][k]
           #             
           #             newCmd = ['combineCards.py']
           #             for i, x in enumerate(cmd):
           #                 if "=" in x :
           #                     Tot_nm   = x.split('=')[1]
           #                     channel  = x.split('=')[0]
           #                     split_ch = channel.split('_')
           #                     new_ch   = 'ch%s_%s'%(i+1, '_'.join(split_ch[1:]))
           #                     newCmd  +=[new_ch+'='+Tot_nm]
           #                     Tot_proc_reg_combine +=[new_ch+'='+Tot_nm]
           #             
           #         out_nm = newCmd[1]
           #         if "=" in out_nm:
           #             out_nm = out_nm.split('=')[1]

           #         suffix        = out_nm.split(mode)[-1].replace('.dat', '')
           #         output_prefix = '%sTo2L2B_gg_fusion_bb_associatedProduction_nb2PLusnb3_%s_%s_%s%s'%( thdm, reg, k, mode, suffix)
           #         datacard      = os.path.join(output_dir, output_prefix +'.dat')
           #         
           #         logger.info('merging %s nb2 + nb3 %s ggH & bbH cmd::: %s'%(k, reg, newCmd) )
           #         with open( datacard, 'w') as f:
           #             subprocess.check_call(newCmd, cwd=output_dir, stdout=f)
           #         
           #         for poi in ['r_ggH', 'r_bbH']:
           #             workspace_file = os.path.basename(os.path.join(output_dir, output_prefix + '_combine_workspace.root'))
           #             MultiSignalModel(workspace_file, datacard, output_prefix, output_dir, 125, 'asymptotic', expectSignal, poi, run_validation, unblind, verbose)
           #     
           #     # A full combination of the signal cats, regions, and lepton flavour
           #     FinalCmd = ['combineCards.py']
           #     for i, x in enumerate(list( set(Tot_proc_reg_combine))):
           #         if "=" in x :
           #             Tot_nm    = x.split('=')[1]
           #             channel   = x.split('=')[0]
           #             split_ch  = channel.split('_')
           #             new_ch    = 'ch%s_%s'%(i+1, '_'.join(split_ch[1:]))
           #             FinalCmd +=[new_ch+'='+Tot_nm]
           #     
           #     logger.info('merging %s nb2 + nb3 + resolved + boosted ggH & bbH cmd::: %s'%(k, FinalCmd) )
           #     suffix        = FinalCmd[1].split(mode)[-1].replace('.dat', '')
           #     output_prefix = '%sTo2L2B_gg_fusion_bb_associatedProduction_nb2PLusnb3_resolved_boosted_%s_%s%s'%( thdm, k, mode, suffix)
           #     datacard      = os.path.join(output_dir, output_prefix +'.dat')
           #     with open( datacard, 'w') as f:
           #         subprocess.check_call(FinalCmd, cwd=output_dir, stdout=f)
           #     
           #     workspace_file = os.path.basename(os.path.join(output_dir, output_prefix + '_combine_workspace.root'))
           #     if method =='asymptotic':
           #         for poi in ['r_ggH', 'r_bbH']:
           #             MultiSignalModel(workspace_file, datacard, output_prefix, output_dir, 125, 'asymptotic', expectSignal, poi, run_validation, unblind, verbose)
           #     elif method =='likelihood_fit':
           #         Likelihood_FitsScans(workspace_file, datacard, output_prefix, output_dir, 125, 'likelihood_fit', verbose)

    return 


def _PullsImpacts(workspace_file, output_prefix, output_dir, datacard, mass, flavor, method, prod, reco, dataset, expectSignal, run_validation, unblind, verbose):
    data   = 'real' if unblind else dataset
    fNm    = '{}_realdataset'.format(output_prefix) if unblind else '{}_expectSignal{}_{}dataset'.format(output_prefix, expectSignal, dataset)
    script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi
# Run combined
combineTool.py {method} -d {workspace_root} -m 125 -n {name} {dataset} {expectSignal} --doInitialFit --robustFit 1 --verbose {verbose} &> {name}_doInitialFit.log
combineTool.py {method} -d {workspace_root} -m 125 -n {name} {dataset} {expectSignal} --robustFit 1 --doFits --parallel 60 --verbose {verbose} &> {name}_robustFit.log
combineTool.py {method} -d {workspace_root} -m 125 -n {name} {dataset} {expectSignal} -o impacts__{fNm}.json --verbose {verbose} &> {name}_impacts.log
plotImpacts.py -i impacts__{fNm}.json -o impacts__{fNm} --blind

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi 

popd
""".format( workspace_root = workspace_file, 
            name           = output_prefix,
            fNm            = fNm, 
            datacard       = os.path.basename(datacard), 
            mass           = mass,
            method         = H.get_combine_method(method), 
            dir            = os.path.dirname(os.path.abspath(datacard)), 
            verbose        = verbose, 
            run_validation = str(run_validation).lower(),
            dataset        = '' if unblind else ('-t -1' if dataset=='asimov' else ('-t 8 -s -1')),
            expectSignal   = '' if unblind else '--expectSignal {}'.format(expectSignal) ) 
    
    script_file = os.path.join(output_dir, output_prefix + ('_run_%s.sh' %(method)))
    print( method, script_file)
    with open(script_file, 'w') as f:
        f.write(script)

    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)
            

def _AsymptoticLimits(workspace_file, datacard, output_prefix, output_dir, mass, method, expectSignal, dataset, run_validation, unblind, verbose):
    script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi
# Run combined
combine {method} -m {mass} -n {name} {workspace_root} {dataset} {rule} {blind} --verbose {verbose} &> {name}.log

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi 

popd
""".format( workspace_root = workspace_file, 
            datacard       = os.path.basename(datacard), 
            name           = output_prefix, 
            mass           = mass, 
            rule           = '--rule CLsplusb' if expectSignal==0 else '',
            method         = H.get_combine_method(method), 
            dir            = os.path.dirname(os.path.abspath(datacard)), 
            #dataset       = '--bypassFrequentistFit' , 
            dataset        = '--noFitAsimov',
            verbose        = verbose, 
            run_validation = str(run_validation).lower(),
            blind          = ('' if unblind else '--run blind') )

    script_file = os.path.join(output_dir, output_prefix + ('_run_%s.sh' %(method)))
    print( method, script_file)
    with open(script_file, 'w') as f:
        f.write(script)

    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)
    


def FastScanNLLshape(workspace_file, datacard, output_prefix, output_dir, mass, method):
    script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi

combine -M GenerateOnly {workspace_root} -t -1 --saveToys --setParameters r=1 -m {mass} -n {name}
combineTool.py -M FastScan -w {workspace_root}:w -d higgsCombine{name}.GenerateOnly.mH{mass}.123456.root:toys/toy_asimov

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi 

popd
""".format( workspace_root = workspace_file, 
            datacard       = os.path.basename(datacard), 
            mass           = mass, 
            name           = output_prefix, 
            run_validation = str(run_validation).lower(),
            dir            = os.path.dirname(os.path.abspath(datacard))
            )
    return script



def Likelihood_FitsScans(workspace_file, datacard, output_prefix, output_dir, mass, method, verbose):
    script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:floatingXSHiggs --PO --verbose {verbose} --PO 'map=.*/ggH:r_ggH[1,0,20]' --PO 'map=.*/bbH:r_bbH[1,0,20]' {datacard} -m {mass} -o {workspace_root}
fi
combine {workspace_root} -M MultiDimFit --robustFit=1 --algo=grid --points 2000 --setParameterRanges r_bbH=0,4:r_ggH=0,4 -m {mass} --fastScan -n {name}
$CMSSW_BASE/../utils/NLLscan2D.py -f higgsCombine{name}.MultiDimFit.mH{mass}.root --name {name} --y-axis-max 4 --y-axis-min 0 --x-axis-max 4 --x-axis-min 0

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi 

popd
""".format( workspace_root = workspace_file, 
            datacard       = os.path.basename(datacard), 
            mass           = mass,
            name           = output_prefix,
            run_validation = str(run_validation).lower(),
            verbose        = verbose, 
            dir            = os.path.dirname(os.path.abspath(datacard))
            )
        
    script_file = os.path.join(output_dir, output_prefix + ('_run_%s.sh' %(method)))
    print( method, script_file)
    with open(script_file, 'w') as f:
        f.write(script)

    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)
    return script             


def ChannelCompatibility(workspace_file, datacard, output_prefix, output_dir, mass, method, run_validation, unblind, verbose):
    script = """#! /bin/bash

pushd {dir}
combine -M ChannelCompatibilityCheck {datacard} -m {mass} -n {name} --verbose {verbose} --saveFitResult &> {name}.log
$CMSSW_BASE/../utils/plotCCC.py 

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi 

popd
""".format( workspace_root = workspace_file, 
            datacard       = os.path.basename(datacard), 
            mass           = mass, 
            name           = output_prefix,
            verbose        = verbose, 
            run_validation = str(run_validation).lower(),
            dir            = os.path.dirname(os.path.abspath(datacard))
            )
    script_file = os.path.join(output_dir, output_prefix + ('_run_%s.sh' %(method)))
    print( method, script_file)
    with open(script_file, 'w') as f:
        f.write(script)

    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)
    return script     


def Goodness_of_fit_tests(workspace_file, datacard, output_prefix, output_dir, mass, method, mode, opts, era, run_validation, unblind, verbose):
    
    Lepts  = { 'MuMu': '\mu\mu',
               'ElEl': 'ee',
               'MuEl': '\mu e',
               'MuMu_MuEl': '\mu\mu+\mu e',
               'ElEl_MuEl': 'ee+\mu e',
               'MuMu_ElEl': '\mu\mu+ee',
               'MuMu_ElEl_MuEl': '\mu\mu+ee+\mu e',
               'OSSF': '\mu\mu+ee',
               'OSSF_MuEl': '\mu\mu+ee+\mu e',
               'split_OSSF': '\mu\mu+ee',
               'split_OSSF_MuEl': '\mu\mu+ee+\mu e'}
    
    p           = 'ggH' if opts['process']=='gg_fusion' else 'bbH'
    nb          = 'nb2+nb3' if opts['nb']=='nb2PLusnb3' else opts['nb'] 
    params      = output_prefix.split(mode)[-1]
    fNm         = opts['process']+ '_'+ opts['nb']+'_' +opts['region']+'_' + opts['flavor'] + params
    
    label_left  = '{}, {}, {}, ({})'.format(p, nb, opts['region'].replace('_','+'), Lepts[opts['flavor']])
    label_right = '%s fb^{-1}(13TeV)'%(round(Constants.getLuminosity(H.PlotItEraFormat(era))/1000., 2))
    pad_style   = '--pad-style TopMargin=0.04' if (opts['region']=='resolved_boosted' or nb == 'nb2+nb3') else ''
    
    script      = """#!/bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root} &> {name}.log
fi

# http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/commonstatsmethods/#goodness-of-fit-tests
algos=("saturated") # "KS" "AD")  
fNm="{fNm}"
addflag=""
run_validation={run_validation}

for algo in ${{algos[*]}}; do
    
    if [ $algo = "saturated" ]; then
        addflag+=" --toysFrequentist"
    fi
    
    echo "working on :: " $algo $addflag
   
    if [ ! -d ${{algo}} ]; then
        mkdir ${{algo}};
    fi

    combine -M GoodnessOfFit {workspace_root} -m {mass} --algo=${{algo}} --verbose {verbose} -n _Obs_${{algo}}_${{fNm}}
    for seed in {{1..5}}; do
        combine -M GoodnessOfFit {workspace_root} -m {mass} --algo=${{algo}} -t 100 -s ${{seed}} -n _Toys_${{algo}}_${{fNm}} ${{addflag}} --verbose {verbose}
    done
    
    if [ -f higgsCombine_Toys_${{algo}}_${{fNm}}.GoodnessOfFit.mH{mass}.12345.root ]; then
        rm higgsCombine_Toys_${{algo}}_${{fNm}}.GoodnessOfFit.mH{mass}.12345.root
        echo "higgsCombine_Toys_${{algo}}_${{fNm}}.GoodnessOfFit.mH{mass}.12345.root is removed, to be recreated again !"
    fi

    hadd higgsCombine_Toys_${{algo}}_${{fNm}}.GoodnessOfFit.mH{mass}.12345.root higgsCombine_Toys_${{algo}}_${{fNm}}.GoodnessOfFit.mH{mass}.1.root higgsCombine_Toys_${{algo}}_${{fNm}}.GoodnessOfFit.mH{mass}.2.root higgsCombine_Toys_${{algo}}_${{fNm}}.GoodnessOfFit.mH{mass}.3.root higgsCombine_Toys_${{algo}}_${{fNm}}.GoodnessOfFit.mH{mass}.4.root higgsCombine_Toys_${{algo}}_${{fNm}}.GoodnessOfFit.mH{mass}.5.root
    
    combineTool.py -M CollectGoodnessOfFit --input higgsCombine_Obs_${{algo}}_${{fNm}}.GoodnessOfFit.mH{mass}.root higgsCombine_Toys_${{algo}}_${{fNm}}.GoodnessOfFit.mH{mass}.12345.root -m {mass} -o ${{algo}}/gof__${{algo}}_${{fNm}}.json 
    
    pushd ${{algo}}
    plotGof.py gof__${{algo}}_${{fNm}}.json --statistic ${{algo}} --mass {mgof} -o gof__${{algo}}_${{fNm}} --title-right="{label_right}" --title-left="{label_left}" {pad_style}
    popd

done

if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi 

popd
""".format( workspace_root = workspace_file,
            datacard       = os.path.basename(datacard), 
            fNm            = fNm,
            #seed          = random.randrange(100, 1000, 3),
            label_left     = label_left,
            label_right    = label_right,
            pad_style      = pad_style, 
            mass           = mass,
            mgof           = float(mass),
            name           = output_prefix,
            verbose        = verbose, 
            run_validation = str(run_validation).lower(),
            dir            = os.path.dirname(os.path.abspath(datacard)) )

    script_file = os.path.join(output_dir, output_prefix + ('_run_%s.sh' %(method)))
    print( method, script_file)
    with open(script_file, 'w') as f:
        f.write(script)

    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)
    return script     


def MultiSignalModel(workspace_file, datacard, output_prefix, output_dir, mass, method, expectSignal, poi, run_validation, unblind, verbose):
    script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel  --PO --verbose {verbose} --PO 'map=.*/ggH:r_ggH[1,0,20]' --PO 'map=.*/bbH:r_bbH[1,0,20]' {datacard} -m {mass} -o {workspace_root}
fi
# Run combined
# set limit on {r} while let {poi} to float freely in the fit 
combine {method} -m {mass} -n {name}_profiled_{poi} {workspace_root} --redefineSignalPOIs {profile} {dataset} {rule} {blind} &> {name}_profiled_{poi}.log

# set limit on {r} while freeze {poi}
combine {method} -m {mass} -n {name}_freezed_{poi} {workspace_root} --redefineSignalPOIs {freeze} {dataset} {rule} {blind} &> {name}_freezed_{poi}.log

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi 

popd
""".format( workspace_root = workspace_file, 
            datacard       = os.path.basename(datacard), 
            name           = output_prefix, 
            mass           = mass, 
            poi            = poi, 
            rule           = '--rule CLsplusb' if expectSignal==0 else '',
            r              = 'r_ggH' if poi=='r_bbH' else 'r_bbH',
            profile        = 'r_ggH --floatParameters r_bbH' if poi=='r_bbH' else 'r_bbH --floatParameters r_ggH',
            freeze         = 'r_ggH --freezeParameters r_bbH --setParameters r_bbH=0.0' if poi=='r_bbH' else 'r_bbH --freezeParameters r_ggH --setParameters r_ggH=0.0',
            method         = H.get_combine_method(method), 
            dir            = os.path.dirname(os.path.abspath(datacard)), 
            #dataset       = '--bypassFrequentistFit', 
            dataset        = '--noFitAsimov',
            verbose        = verbose, 
            run_validation = str(run_validation).lower(),
            blind          = ('' if unblind else '--run blind') )
        
    script_file = os.path.join(output_dir, output_prefix + ('_%s_run_%s.sh' %(poi, method)))
    print( method, script_file)
    with open(script_file, 'w') as f:
        f.write(script)

    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)
    return script            


def get_ellipses_parameters(ellipses_mumu_file):
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
    return ellipses


def get_signal_parameters(f):
    if '_tb_' in f:  # new version format
        split_filename = f.replace('.root','').split('To2L2B_')[-1]
        m_heavy = split_filename.split('_')[1].replace('p', '.')
        m_light = split_filename.split('_')[3].replace('p', '.')
    else:
        split_filename = f.replace('.root','').replace('HToZATo2L2B_','')
        split_filename = split_filename.split('_')
        MH = split_filename[0].split('-')[1]
        MA = split_filename[1].split('-')[1]
    return float(m_heavy), float(m_light) 


def CreateScriptToRunCombine(output, method, mode, tanbeta, era, _2POIs_r, expectSignal, sbatch_time, sbatch_memPerCPU, submit_to_slurm):
    
    poi_dir, tb_dir, CL_dir = Constants.locate_outputs(method, _2POIs_r, tanbeta, expectSignal)
    
    output        = os.path.join(output, H.get_method_group(method), mode, CL_dir, poi_dir, tb_dir)
    symbolic_path = os.path.abspath(os.path.dirname(output.split('/')[0]))+'/'+output.split('/')[0]
    script = """#! /bin/bash

WorkEra='{WorkEra}'
combine_method='{combine_method}'
scripts=`find {output} -name "*_{suffix}.sh"`
base="$(cd "$(dirname "$1")"; pwd -P)/$(basename "$1")"
echo $base

for script in $scripts; do
    dir=$(dirname $script)
    script=$(basename $script)
    echo "\tComputing with ${{script}}"
    echo "\tworking dir ${{dir}}"
    
    pushd $dir &> /dev/null
    if [ "$WorkEra" = "work__ULfullrun2" ]; then
        if [ ! -d {symbol} ]; then
            ln -s -d {symbolic_path} .
        fi
    fi
    {c1}. $script
    popd &> /dev/null

done

sbatch_time={sbatch_time}
sbatch_memPerCPU={sbatch_memPerCPU}

# for slurm submission instead!
{c2}python Combine4Slurm.py -c {output} -o {slurm_dir}/${{WorkEra}} --method ${{combine_method}} --time ${{sbatch_time}} --mem-per-cpu ${{sbatch_memPerCPU}}

""".format(output           = output.replace('work_'+ H.EraFromPOG(era), '$WorkEra'),
           WorkEra          = 'work_' + H.EraFromPOG(era),
           slurm_dir        = output.split('work__UL')[0],
           combine_method   = H.get_method_group(method),
           suffix           = 'run_%s'%method,
           sbatch_time      = sbatch_time,
           sbatch_memPerCPU = sbatch_memPerCPU,
           c1               = '#' if submit_to_slurm  else '',
           c2               = ''  if submit_to_slurm  else '#',
           symbol           = symbolic_path.split('/')[-1],
           symbolic_path    = symbolic_path
           )
   
    print( '\tThe generated script to run limits can be found in : %s/' %output)
    if   method == 'fit': suffix= 'prepost'
    elif method == 'impacts': suffix= 'pulls'
    elif method in ['asymptotic', 'hybridnew']: suffix= 'limits'
    else: suffix= ''

    script_name = "run_combine_%s_%s%s.sh" % (mode, method, suffix)
    with open(script_name, 'w') as f:
        f.write(script)

    st = os.stat(script_name)
    os.chmod(script_name, st.st_mode | stat.S_IEXEC)

    logger.info("All done. You can run everything by executing %r" % ('./' + script_name))


def prepare_DataCards(grid_data, thdm, dataset, expectSignal, era, mode, input, ellipses_mumu_file, output, method, node, scalefactors, tanbeta, verbose, sbatch_time, sbatch_memPerCPU, unblind= False, stat_only= False, merge_cards= False, _2POIs_r=False, multi_signal=False, scale= False, normalize= False, run_validation=False, submit_to_slurm= False):
   
    luminosity  = Constants.getLuminosity(H.PlotItEraFormat(era))
    
    ellipses = {}
    if mode == "ellipse":
        get_ellipses_parameters(ellipses_mumu_file)

    # this is cross-check that the extracted signal mass points from the plots.yml
    # have their equivalent root file in the results/ dir  
    all_parameters = {}
    for prefix, prod in {'GluGluTo': 'gg_fusion', 
                         '': 'bb_associatedProduction',
                         'full': 'gg_fusion_bb_associatedProduction'}.items():
        
        p =''
        if method != 'generatetoys':  p = prod
        
        all_parameters[prod] = { 'resolved': [] , 'boosted': [] }
        for f in glob.glob(os.path.join(input, p, '*.root')):
            
            split_filename = f.split('/')[-1]
            
            if not thdm in split_filename:
                continue

            if prefix =='full':
                if not '_tb_' in split_filename:
                    continue
            else:
                if not split_filename.startswith('{}{}To2L2B_'.format(prefix, thdm)): 
                    continue
            
            if era != "fullrun2":
                if not H.EraFromPOG(era) in split_filename:
                    continue
            
            for reg in ['resolved', 'boosted']:
                m_heavy, m_light = get_signal_parameters(split_filename)

                if prefix =='full':
                    if not (m_heavy, m_light) in grid_data['gg_fusion'][reg][thdm] and not (m_heavy, m_light) in grid_data['bb_associatedProduction'][reg][thdm]:
                        continue
                else:
                    if not (m_heavy, m_light) in grid_data[prod][reg][thdm]:
                        continue
                
                if not (m_heavy, m_light) in all_parameters[prod][reg]:
                    all_parameters[prod][reg].append( (m_heavy, m_light) )
    
    print( all_parameters )
    NotIn2Prod = []    
    for tup in all_parameters['gg_fusion']['resolved']:
        if not tup in all_parameters['bb_associatedProduction']['resolved']:
            NotIn2Prod.append('%s_M%s_%s_M%s_%s'%(mode, thdm[0], tup[0], thdm[-1], tup[1]))

    logger.info("Era and the corresponding luminosity      : %s, %s" %(era, Constants.getLuminosity(H.PlotItEraFormat(era))))
    logger.info("Input path                                : %s" % input )
    logger.info("Chosen analysis mode                      : %s" % mode)

    if not os.path.exists(input):
        logger.warning(" This 'path' %s does not exist ...!"%input)
        exit()

    if _2POIs_r:
        if multi_signal:
            productions = ['gg_fusion_bb_associatedProduction']
        else:
            productions = ['gg_fusion', 'bb_associatedProduction']
    else:
        productions = ['gg_fusion_bb_associatedProduction']

    proc_combination = {}
    cats = []
    for prod in productions:
        p = ''
        if method != 'generatetoys': p = prod
        proc_combination[prod] = {}
        if _2POIs_r:
            if multi_signal:
                sig_process = ['gg'+thdm[0], 'bb'+thdm[0]]
            else:
                sig_process = [prod.split('_')[0]+thdm[0]]
        else:
            sig_process = ['gg'+thdm[0], 'bb'+thdm[0]]

        for reg in ['resolved', 'boosted']:
            ToFIX = []
            for reco in ['nb2', 'nb3']:
                flavors = []
                if method=="generatetoys":
                    flavors = ['MuMu', 'ElEl', 'MuEl', 'OSSF']
                else:
                    if reco =='nb3' or reg =='boosted' or prod in ['bb_associatedProduction', 'gg_fusion_bb_associatedProduction']:
                        flavors = ['OSSF', 'MuEl']
                        if H.splitLep:
                            flavors += ['MuMu', 'ElEl']
                    else:
                        flavors = ['MuMu', 'ElEl', 'MuEl']
                
                logger.info("Working on %s && %s cat.     :"%(prod, reg) )
                logger.info("Generating set of cards for parameter(s)  : %s" % (', '.join([str(x) for x in all_parameters[prod][reg]])))
                
                
                Totflav_cards_allparams, buggy = prepareShapes( input           = os.path.join(input, p), 
                                                                dataset         = dataset, 
                                                                thdm            = thdm, 
                                                                sig_process     = sig_process, 
                                                                expectSignal    = expectSignal, 
                                                                era             = era, 
                                                                method          = method, 
                                                                parameters      = all_parameters[prod][reg], 
                                                                prod            = prod,
                                                                reco            = reco, 
                                                                reg             = reg, 
                                                                flavors         = flavors, 
                                                                ellipses        = ellipses, 
                                                                mode            = mode,  
                                                                output          = output, 
                                                                luminosity      = luminosity, 
                                                                scalefactors    = scalefactors,
                                                                tanbeta         = tanbeta, 
                                                                verbose         = verbose,
                                                                scale           = scale, 
                                                                merge_cards     = merge_cards, 
                                                                _2POIs_r        = _2POIs_r, 
                                                                multi_signal    = multi_signal,
                                                                unblind         = unblind, 
                                                                stat_only       = stat_only, 
                                                                normalize       = normalize,
                                                                run_validation  = run_validation,
                                                                submit_to_slurm = submit_to_slurm)
                
                ToFIX += buggy
                proc_combination[prod][reco+'_'+reg] = Totflav_cards_allparams 
                for x in Totflav_cards_allparams.keys():
                    if x not in cats and Constants.cat_to_tuplemass(x[1]) not in ToFIX: cats.append(x) 
            
            # remove duplicate 
            ToFIX = list(dict.fromkeys(ToFIX))
            
            CustomCardCombination(thdm, mode, cats, proc_combination[prod], expectSignal, dataset, method, 
                                  prod          = prod, 
                                  era           = era, 
                                  verbose       = verbose, 
                                  reg           = reg, 
                                  skip          = ToFIX, 
                                  unblind       = unblind, 
                                  _2POIs_r      = _2POIs_r, 
                                  run_validation= run_validation, 
                                  multi_signal  = multi_signal, 
                                  todo          = 'nb2_nb3')
        
        CustomCardCombination(thdm, mode, cats, proc_combination[prod], expectSignal, dataset, method, 
                              prod              = prod, 
                              era               = era,
                              verbose           = verbose, 
                              reg               = None, 
                              skip              = ToFIX, 
                              unblind           = unblind, 
                              _2POIs_r          = _2POIs_r, 
                              run_validation    = run_validation, 
                              multi_signal      = multi_signal, 
                              todo              = 'res_boo')
    #if _2POIs_r:
    #    CustomCardCombination(thdm, mode, cats, proc_combination, expectSignal, dataset, method, prod=None, verbose=verbose, reg=None, skip=NotIn2Prod, unblind=unblind, _2POIs_r=_2POIs_r, run_validation=run_validation, multi_signal=multi_signal, todo='ggH_bbH')
        
    # Add mc stat. 
    #cb.AddDatacardLineAtEnd("* autoMCStats 0 0 1")
    #for datacard in glob.glob(os.path.join(output, H.get_method_group(method), mode,'*/', '*.dat')):
    #    Constants.add_autoMCStats(datacard, threshold=0, include_signal=0, hist_mode=1)

    # Create helper script to run combine
    CreateScriptToRunCombine(output, method, mode, tanbeta, era, _2POIs_r, expectSignal, sbatch_time, sbatch_memPerCPU, submit_to_slurm)



def prepareShapes(input, dataset, thdm, sig_process, expectSignal, era, method, parameters, prod, reco, reg, flavors, ellipses, mode, output, luminosity, scalefactors, tanbeta, verbose, scale=False, merge_cards=False, _2POIs_r=False, multi_signal=False, unblind=False, stat_only=False, normalize=False, run_validation=False, submit_to_slurm=False):
    
    if mode == "mjj_and_mlljj":
        categories = [
                (1, 'mlljj'),
                (2, 'mjj')
                ]
    elif mode == "mjj_vs_mlljj":
        categories = [
                (1, 'mjj_vs_mlljj')
                ]
    elif mode == "mbb":
        categories = [
                (1, 'mbb')
                ]
    elif mode == "mllbb":
        categories = [
                (1, 'mllbb')
                ]
    elif mode == "ellipse":
        categories = [
                # % (flavour, ellipse_index)
                (1, 'ellipse_{}_{}')
                ]
    elif mode == "dnn":
        categories = [
                # % ( H, A, mass_H, mass_A) if thdm 'HToZA'
                (1, 'dnn_M{}_{}_M{}_{}')
                ]
    
    heavy = thdm[0]
    light = thdm[-1]
    
    _s = '*'
    if prod == 'gg_fusion': 
        look_for = 'GluGluTo'
    else : 
        look_for = ''

    histfactory_to_combine_categories = {}
    histfactory_to_combine_processes  = {
            # main Background
            'ttbar'    : ['^TTToSemiLeptonic*', '^TTTo2L2Nu*', '^TTToHadronic*'],  
            'SingleTop': ['^ST_*'],
            'DY'       : ['^DYJetsToLL_0J*', '^DYJetsToLL_1J*', '^DYJetsToLL_2J*', '^DYJetsToLL_M-10to50*'],
            # Others Backgrounds
            'WJets'    : ['^WJetsToLNu*'],
            'ttV'      : ['^TT(W|Z)To*'],
            'VV'       : ['^(ZZ|WW|WZ)To*'],
            'VVV'      : ['^ZZZ_*', '^WWW_*', '^WZZ_*', '^WWZ_*'],
            'SMHiggs'  : ['^ggZH_HToBB_ZToLL_M-125*', '^HZJ_HToWW_M-125*', '^ZH_HToBB_ZToLL_M-125*', '^ggZH_HToBB_ZToNuNu_M-125*', '^GluGluHToZZTo2L2Q_M125*', '^ttHTobb_M125_*', '^ttHToNonbb_M125_*']
            }

    if H.splitTTbar:
        del histfactory_to_combine_processes['ttbar']
        histfactory_to_combine_processes.update({'ttB': ['^TTToSemiLeptonic_ttB_*', '^TTTo2L2Nu_ttB_*', '^TTToHadronic_ttB_*'],
                                                 'tt' : ['^TTToSemiLeptonic_tt_*', '^TTTo2L2Nu_tt_*', '^TTToHadronic_tt_*'] })
    if H.splitDrellYan:
        del histfactory_to_combine_processes['DY']
        histfactory_to_combine_processes.update({'DY0jets' : ['^DYJetsToLL_0J*'],
                                                 'DY1jets' : ['^DYJetsToLL_1J*'],
                                                 'DY2jets' : ['^DYJetsToLL_2J*'] })

    
    bkg_processes = histfactory_to_combine_processes.keys()

    # Shape depending on the signal hypothesis
    for p in parameters:
        m_heavy = p[0]
        m_light = p[1]

        formatted_p = format_parameters(p)
        
        if _2POIs_r: # if so, you should not merge the signals 
            if multi_signal:
                histfactory_to_combine_processes['gg{}_M{}-{}_M{}-{}'.format(thdm[0], heavy, m_heavy, light, m_light), p] = [
                                                 '^GluGluTo{}To2L2B_M{}_{}_M{}_{}*'.format(thdm, heavy, mass_to_str(m_heavy), light, mass_to_str(m_light)),
                                                ]
                histfactory_to_combine_processes['bb{}_M{}-{}_M{}-{}'.format(thdm[0], heavy, m_heavy, light, m_light), p] = [
                                                 '^{}To2L2B_M{}_{}_M{}_{}{}'.format(thdm, heavy, mass_to_str(m_heavy), light, mass_to_str(m_light), _s),
                                                ]
            else:
                histfactory_to_combine_processes['{}_M{}-{}_M{}-{}'.format(sig_process[0], heavy, m_heavy, light, m_light), p] = [
                                                '^{}{}To2L2B_M{}_{}_M{}_{}{}'.format(look_for, thdm, heavy, mass_to_str(m_heavy), light, mass_to_str(m_light), _s) 
                                                ]
        else:
            histfactory_to_combine_processes['{}_M{}-{}_M{}-{}'.format(sig_process[0], heavy, m_heavy, light, m_light), p] = [
                                             '^GluGluTo{}To2L2B_M{}_{}_M{}_{}*'.format(thdm, heavy, mass_to_str(m_heavy), light, mass_to_str(m_light)),
                                             '^{}To2L2B_M{}_{}_M{}_{}{}'.format(thdm, heavy, mass_to_str(m_heavy), light, mass_to_str(m_light), _s) 
                                            ]

        if mode == "dnn":
            if H.FixbuggyFormat: 
                histfactory_to_combine_categories[('dnn_M{}_{}_M{}_{}'.format(heavy, m_heavy, light, m_light), p)] = get_hist_regex(
                   'DNNOutput_Z%snode_{flavor}_{reg}_{taggerWP}_METCut_{fix_reco_format}_M%s_%s_M%s_%s'%( light, heavy, mass_to_str(m_heavy), light, mass_to_str(m_light)) )
            else:     
                histfactory_to_combine_categories[('dnn_M{}_{}_M{}_{}'.format(heavy, m_heavy, light, m_light), p)] = get_hist_regex(
                    'DNNOutput_Z%snode_{flavor}_{reco}_{reg}_{taggerWP}_METCut_M%s_%s_M%s_%s'%( light, heavy, mass_to_str(m_heavy), light, mass_to_str(m_light)) )
        
        elif mode == "mllbb":
            histfactory_to_combine_categories[('mllbb', p)] = get_hist_regex('{flavor}_{reg}_METCut_NobJetER_bTagWgt_mllbb_{taggerWP}_{fix_reco_format}')
        elif mode == "mbb":
            histfactory_to_combine_categories[('mbb', p)]   = get_hist_regex('{flavor}_{reg}_METCut_NobJetER_bTagWgt_mbb_{taggerWP}_{fix_reco_format}')
        
        #  !! deprecated 
        #formatted_e = format_ellipse(p, ellipses)
        #elif mode == "mjj_and_mlljj":
        #    histfactory_to_combine_categories[('mjj', p)]   = get_hist_regex('jj_M_resolved_{flavor}_hZA_lljj_DeepCSVM_mll_and_met_cut')
        #    histfactory_to_combine_categories[('mlljj', p)] = get_hist_regex('lljj_M_resolved_{flavor}_hZA_lljj_DeepCSVM_mll_and_met_cut')
        #elif mode == "mjj_vs_mlljj": 
        #    histfactory_to_combine_categories[('mjj_vs_mlljj', p)] = get_hist_regex('Mjj_vs_Mlljj_resolved_{flavor}_hZA_lljj_DeepCSVM_mll_and_met_cut')
        #elif mode == "ellipse":
        #    histfactory_to_combine_categories[('ellipse_{}_{}'.format(formatted_p, formatted_e), p)] = get_hist_regex('rho_steps_{flavor}_{reg}_DeepCSVM__METCut_NobJetER_{prod}_MH_%sp0_MA_%sp0'%(mH, mA))
    
    if unblind:
        histfactory_to_combine_processes['data_obs'] = ['^DoubleMuon*', '^DoubleEG*', '^MuonEG*', '^SingleMuon*', '^SingleElectron*', '^EGamma*']
    
    logger.info('Hist factory to combine categories        : %s '%histfactory_to_combine_categories )
    logger.info('hist factory to combine processes         : %s '%histfactory_to_combine_processes  )

    if not histfactory_to_combine_categories:
        logger.warning('.. nothing to be processed, will exit !')
        exit()

    analysis_categories = []
    for flavor in flavors:
        cat = '{}_{}_{}_{}'.format(prod, reco, reg, flavor)
        analysis_categories.append(cat)

    file, systematics, ToFIX = H.prepareFile(processes_map       = histfactory_to_combine_processes, 
                                             categories_map      = histfactory_to_combine_categories, 
                                             input               = input, 
                                             output_filename     = os.path.join(output, 'shapes_{}_{}_{}.root'.format('_'.join(sig_process), reco, reg)), 
                                             signal_process      = sig_process,
                                             method              = method, 
                                             luminosity          = luminosity, 
                                             mode                = mode,
                                             thdm                = thdm,
                                             analysis_categories = analysis_categories,
                                             era                 = era, 
                                             scalefactors        = scalefactors,
                                             tanbeta             = tanbeta, 
                                             _2POIs_r            = _2POIs_r,
                                             multi_signal        = multi_signal,
                                             unblind             = unblind,
                                             normalize           = normalize)
    
    #print ( "\tsystematics : %s       :" %systematics )
    print( 'params to avoid ::', ToFIX)

    processes  = sig_process + bkg_processes
    logger.info( "Processes       : %s" %processes)
        
    # Dummy mass value used for all combine input when a mass is needed
    mass = "125"
    
    poi_dir, tb_dir, CL_dir = Constants.locate_outputs(method, _2POIs_r, tanbeta, expectSignal)
    
    output_prefix  = '{}To2L2B'.format(thdm)
    
    Totflav_cards_allparams = {}
    for i, p in enumerate(parameters):
        if p in ToFIX:
            continue
        m_heavy = p[0]
        m_light = p[1]
        
        output_dir = os.path.join(output, H.get_method_group(method), mode, CL_dir, poi_dir, tb_dir, 'M%s-%s_M%s-%s'%(heavy, m_heavy, light, m_light))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
        cb = ch.CombineHarvester()
        cb.SetVerbosity(verbose)
        cb.SetFlag("zero-negative-bins-on-import", True)
        cb.SetFlag("check-negative-bins-on-import",True)

        formatted_p  = format_parameters(p)
        #formatted_e = format_ellipse(p, ellipses)

        categories_with_parameters = categories[:]
        for i, k in enumerate(categories_with_parameters):
            if mode  == 'dnn':
                categories_with_parameters[i] = (k[0], k[1].format(heavy, m_heavy, light, m_light))
            elif mode in ['mbb', 'mllbb']:
                categories_with_parameters[i] = (k[0], k[1])
            else:
                logger.info( 'Deprecated mode !' )
        
        logger.info( 'looking for categories_with_parameters      :  %s '%categories_with_parameters) 
        
        analysis = sig_process
        if multi_signal: # use nb2 shaphes for ggH and nb3 shaphes for bbH 
            if reco =='nb3':
                analysis = ['bb%s'% thdm[0]]
            elif reco =='nb2':
                analysis = ['gg%s'% thdm[0]]
        
        #cb.AddObservations( mass, analysis, era, channel, bin)
        cb.AddObservations(['*'], analysis, ['13TeV_%s'%era], analysis_categories, categories_with_parameters)
        
        #cb.AddProcesses( mass, analysis, era, channel, process, bin, signal( bool))
        cb.AddProcesses(['*'], analysis, ['13TeV_%s'%era], analysis_categories, bkg_processes, categories_with_parameters, signal=False)
        cb.AddProcesses([mass], analysis, ['13TeV_%s'%era], analysis_categories, sig_process, categories_with_parameters, signal=True)
        
        cb.AddDatacardLineAtEnd("* autoMCStats 0 0 1")
        
        if not stat_only:
            processes_without_weighted_data = cb.cp()
            processes_without_weighted_data.FilterProcs(lambda p: 'data' in p.process())
            
            lumi_correlations = Constants.getLuminosityUncertainty()
            newEra = '2016' if 'VFP' in era else era
            processes_without_weighted_data.AddSyst(cb, 'lumi_uncorrelated_$ERA', 'lnN', ch.SystMap('era')(['13TeV_%s'%era], lumi_correlations['uncorrelated'][newEra]))
            processes_without_weighted_data.AddSyst(cb, 'lumi_correlated_13TeV_2016_2017_2018', 'lnN', ch.SystMap('era')(['13TeV_%s'%era], lumi_correlations['correlated_16_17_18'][newEra]))
            if era in ['2017', '2018']:
                processes_without_weighted_data.AddSyst(cb, 'lumi_correlated_13TeV_2017_2018', 'lnN', ch.SystMap('era')(['13TeV_%s'%era], lumi_correlations['correlated_17_18'][era]))

            #cb.cp().AddSyst(cb, 'ttbar_xsec', 'lnN', ch.SystMap('process')(['ttbar'], 1.001525372691124) )
            #cb.cp().AddSyst(cb, 'SingleTop_xsec', 'lnN', ch.SystMap('process')(['SingleTop'], 1.19/1.22) )
            #cb.cp().AddSyst(cb, 'DY_xsec', 'lnN', ch.SystMap('process')(['DY'], 1.007841991384859) )
            #
            #print( sig_process )
            #for sig in sig_process:
            #    xsc, xsc_err, totBR = Constants.get_SignalStatisticsUncer(m_heavy, m_light, sig, thdm)
            #    signal_uncer        = 1+xsc_err/xsc
    
            #    cb.cp().AddSyst(cb, '$PROCESS_xsec', 'lnN', ch.SystMap('process')([sig], signal_uncer) )

            for _, category_with_parameters in categories_with_parameters:
                for cat in analysis_categories:
                    for process in processes:
                        _type = 'mc'
                        if process in ['ggH', 'bbH', 'ggA', 'bbA']:
                            _type = 'signal'
                        if not process in cb.cp().channel([cat]).process_set():
                            print("[{}, {}] Process '{}' not found, skipping systematics".format(category_with_parameters, cat, process))
                        for s in systematics[cat][category_with_parameters][process]:
                            s = str(s)
                            if H.ignoreSystematic(smp=None, cat=cat, process=process, s=s, _type=_type):
                                print("[{}, {}, {}] Ignoring systematic '{}'".format(category_with_parameters, cat, process, s))
                                continue
                            cb.cp().channel([cat]).process([process]).AddSyst(cb, s, 'shape', ch.SystMap()(1.00))
        
        if scale:
            cb.cp().process(sig_process).ForEachProc(lambda x : x.set_rate(x.rate()*1000))
            cb.cp().process(sig_process).PrintProcs()
        
        bin_id  = categories_with_parameters[0][1]
        
        # Import shapes from ROOT file
        for cat in analysis_categories:
        
            cb.cp().bin([bin_id]).channel([cat]).backgrounds().ExtractShapes(file, '$BIN/$PROCESS_%s' %cat, '$BIN/$PROCESS_%s__$SYSTEMATIC' %cat)
            cb.cp().bin([bin_id]).channel([cat]).signals().ExtractShapes(file, '$BIN/$PROCESS_M%s-%s_M%s-%s_%s'% (heavy, m_heavy, light, m_light, cat), 
                                                    '$BIN/$PROCESS_%s_%s__$SYSTEMATIC'% ('M%s-%s_M%s-%s'%(heavy, m_heavy, light, m_light), cat))
           
        cb.FilterProcs(lambda x: H.drop_zero_procs(cb,x)) 
        cb.FilterSysts(lambda x: H.drop_zero_systs(x))
        cb.cp().bin([bin_id]).ForEachSyst(lambda x: H.symmetrise_smooth_syst(cb,x) if (x.name().startswith("CMS_scale_j") or x.name().startswith("CMS_res_j") or x.name().startswith("QCD")) else None)
        #cb.FilterSysts(lambda x: H.drop_onesided_systs(x))
        
        # Bin by bin uncertainties
        #if not stat_only:
        #    bkgs = cb.cp().backgrounds()
        #    bkgs.FilterProcs(lambda p: 'data' in p.process())
        #    bbb = ch.BinByBinFactory()
        #    bbb.SetAddThreshold(0.05).SetMergeThreshold(0.5).SetFixNorm(False)
        #    bbb.MergeBinErrors(bkgs)
        #    bbb.AddBinByBin(bkgs, cb)

        # Write small script to compute the limit
        def createRunCombineScript(bin_id, mass, output_dir, output_prefix, cat, opts, create=False, skip=False):
            datacard       = os.path.join(output_dir, output_prefix + '.dat')
            workspace_file = os.path.basename(os.path.join(output_dir, output_prefix + '_combine_workspace.root'))

            if method == 'goodness_of_fit': 
                #and any( x in cat for x in['MuMu_ElEl', 'MuMu_ElEl_MuEl', 'OSSF', 'OSSF_MuEl']):
                create      = False
                Goodness_of_fit_tests(workspace_file, datacard, output_prefix, output_dir, mass, method, mode, opts, era, run_validation, unblind, verbose)
            
            if method == 'pvalue' and any( x in cat for x in ['MuMu_ElEl', 'MuMu_ElEl_MuEl', 'OSSF', 'OSSF_MuEl']):
                create = True
                script ="""#!/bin/bash -l

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}.root
fi

#=============================================
# Computing Significances with toys
#=============================================
combine -M HybridNew {datacard} --LHCmode LHC-significance --saveToys --fullBToys --saveHybridResult -T 500 -i 10 -s 1 -m {mass} --verbose {verbose} &> {name}__toys1.log
combine -M HybridNew {datacard} --LHCmode LHC-significance --saveToys --fullBToys --saveHybridResult -T 500 -i 10 -s 2 -m {mass} --verbose {verbose} &> {name}__toys2.log
combine -M HybridNew {datacard} --LHCmode LHC-significance --saveToys --fullBToys --saveHybridResult -T 500 -i 10 -s 3 -m {mass} --verbose {verbose} &> {name}__toys3.log
combine -M HybridNew {datacard} --LHCmode LHC-significance --saveToys --fullBToys --saveHybridResult -T 500 -i 10 -s 4 -m {mass} --verbose {verbose} &> {name}__toys4.log
combine -M HybridNew {datacard} --LHCmode LHC-significance --saveToys --fullBToys --saveHybridResult -T 500 -i 10 -s 5 -m {mass} --verbose {verbose} &> {name}__toys5.log

if [ -f merged.root ]; then
    rm merged.root
    echo "merged.root is removed, to be created again !"
fi

hadd merged.root higgsCombineTest.HybridNew.mH125.1.root higgsCombineTest.HybridNew.mH125.2.root higgsCombineTest.HybridNew.mH125.3.root higgsCombineTest.HybridNew.mH125.4.root higgsCombineTest.HybridNew.mH125.5.root 

# Observed significance with toys
combine -M HybridNew {datacard} --LHCmode LHC-significance --readHybridResult --toysFile=merged.root --grid=higgsCombineTest.significance_obs.mH{mass}.root --pvalue -m {mass} --verbose {verbose} &> {name}__significance_obs.log

# Expected significance, assuming some signal
combine -M HybridNew {datacard} --LHCmode LHC-significance --readHybridResult --toysFile=merged.root --grid=higgsCombineTest.significance_exp_plus_s.mH{mass}.root --pvalue --expectedFromGrid=0.84 -m {mass} --verbose {verbose} &> {name}__significance_exp_plus_s.log
#=============================================

{c}echo "Observed significance"
{c}combine {method} {workspace_root}.root -m {mass} &> observed__significance_expectSignal{expectSignal}_{cat}.log

echo "Expected significance"
combine {method} {workspace_root}.root {dataset} --expectSignal {expectSignal} -m {mass} --toysFreq &> expected__significance_expectSignal{expectSignal}_{cat}.log

{c}echo "Observed p-value" 
{c}combine {method} {workspace_root}.root --pvalue -m {mass} &> observed__pvalue_expectSignal{expectSignal}_{cat}.log

echo "Expected p-value" 
combine {method} {workspace_root}.root {dataset} --expectSignal {expectSignal} --pvalue -m {mass} --toysFreq &> expected__pvalue_expectSignal{expectSignal}_{cat}.log

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi

popd
""".format( workspace_root = workspace_file.replace('.root', ''), 
            datacard       = os.path.basename(datacard), 
            cat            = cat, 
            mass           = mass,
            name           = 'sig__toysFreq__{}'.format(output_prefix),
            seed           = random.randrange(100, 1000, 3),
            method         = H.get_combine_method(method), 
            dataset        = '' if unblind else ('-t -1' if dataset=='asimov' else ('-t 8 -s -1')),
            verbose        = verbose,
            dir            = os.path.dirname(os.path.abspath(datacard)),
            expectSignal   = expectSignal, 
            run_validation = str(run_validation).lower(),
            c              = '' if unblind else '#',
            )
            
            if method == 'hybridnew':
                create = True
                script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi
# Run limit
combine {method} --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} --verbose {verbose} &> {name}.log
combine {method} --expectedFromGrid=0.5   --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} --verbose {verbose} &> {name}_exp.log
combine {method} --expectedFromGrid=0.84  --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} --verbose {verbose} &> {name}_P1sigma.log
combine {method} --expectedFromGrid=0.16  --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} --verbose {verbose} &> {name}_M1sigma.log
combine {method} --expectedFromGrid=0.975 --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} --verbose {verbose} &> {name}_P2sigma.log
combine {method} --expectedFromGrid=0.025 --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} --verbose {verbose} &> {name}_M2sigma.log

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi

popd
""".format( workspace_root = workspace_file, 
            datacard       = os.path.basename(datacard), 
            name           = output_prefix, 
            mass           = mass,
            verbose        = verbose, 
            run_validation = str(run_validation).lower(),
            systematics    = (0 if stat_only else 1), 
            method         = H.get_combine_method(method), 
            dir            = os.path.dirname(os.path.abspath(datacard)) )
            
            elif method == 'likelihood_fit':
                if multi_signal:
                    create     = False
                    Likelihood_FitsScans(workspace_file, datacard, output_prefix, output_dir, 125, 'likelihood_fit', verbose)

            elif method == 'asymptotic':
                if multi_signal:
                    create     = False
                    for poi in ['r_ggH', 'r_bbH']:
                        MultiSignalModel(workspace_file, datacard, output_prefix, output_dir, 125, 'asymptotic', expectSignal, poi, run_validation, unblind, verbose)
                else:
                    create = True
                    script = """#!/bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi
# Run combined
combine {method} -m {mass} -n {name} {workspace_root} {dataset} {rule} {blind} --verbose {verbose} &> {name}.log

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi 

popd
""".format( workspace_root = workspace_file, 
            datacard       = os.path.basename(datacard), 
            name           = output_prefix, 
            mass           = mass, 
            rule           = '--rule CLsplusb' if expectSignal==0 else '',
            method         = H.get_combine_method(method), 
            dir            = os.path.dirname(os.path.abspath(datacard)), 
            #dataset       = '--bypassFrequentistFit' , 
            dataset        = '--noFitAsimov',
            verbose        = verbose, 
            run_validation = str(run_validation).lower(), 
            blind          = ('' if unblind else '--run blind'),
            )
            
            elif method =='impacts':
                #and ( 'MuMu' in cat or 'ElEl' in cat or 'OSSF' in cat):
                create = True
                data   = 'real' if unblind else dataset
                fNm    = '{}_realdataset'.format(output_prefix) if unblind else '{}_expectSignal{}_{}dataset'.format(output_prefix, expectSignal, dataset)
                script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi
# Run combined
combineTool.py {method} -d {workspace_root} -m 125 -n {name} {dataset} {expectSignal} --doInitialFit --robustFit 1 --verbose {verbose} &> {name}_doInitialFit.log
combineTool.py {method} -d {workspace_root} -m 125 -n {name} {dataset} {expectSignal} --robustFit 1 --doFits --parallel 60 --verbose {verbose} &> {name}_robustFit.log
combineTool.py {method} -d {workspace_root} -m 125 -n {name} {dataset} {expectSignal} -o impacts__{fNm}.json --verbose {verbose} &> {name}_impacts.log
plotImpacts.py -i impacts__{fNm}.json -o impacts__{fNm} --blind

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi

popd
""".format( workspace_root = workspace_file, 
            name           = output_prefix,
            fNm            = fNm, 
            datacard       = os.path.basename(datacard), 
            mass           = mass,
            method         = H.get_combine_method(method), 
            dir            = os.path.dirname(os.path.abspath(datacard)), 
            verbose        = verbose, 
            run_validation = str(run_validation).lower(),
            dataset        = '' if unblind else ('-t -1' if dataset=='asimov' else ('-t 8 -s -1')),
            expectSignal   = '' if unblind else '--expectSignal {}'.format(expectSignal) ) 
            
            
            elif method =='generatetoys':
                create = True
                t      = '--toysNoSystematics' if stat_only else '--toysFrequentist'
                script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi
combine -M GenerateOnly {workspace_root} {dataset} --toysFile --saveToys -m 125 {expectSignal} {systematics} -n {fNm} --verbose {verbose} &> {name}.log

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi

popd
""".format( dir            = os.path.dirname(os.path.abspath(datacard)),
            workspace_root = workspace_file,
            datacard       = os.path.basename(datacard), 
            mass           = mass,
            dataset        = ('-t -1' if dataset=='asimov' else '-t 1 -s -1'),
            expectSignal   = '--expectSignal {}'.format(expectSignal),
            systematics    = t, 
            name           = output_prefix,
            verbose        = verbose, 
            run_validation = str(run_validation).lower(),
            fNm            = '_{}_expectSignal{}_{}'.format(t.replace('--',''), expectSignal, output_prefix))

            
            elif method == 'signal_strength':
                create = True
                script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi

combine {method} {workspace_root} -n .{cat}.snapshot -t -1 -m 125 --algo grid --points 30 --saveWorkspace --verbose {verbose}
combine -M MultiDimFit  higgsCombine.{cat}.snapshot.MultiDimFit.mH125.root -n .{cat}.freezeAll -m 125 --algo grid --points 30 --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit --verbose {verbose}

python $CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/plot1DScan.py higgsCombine.{cat}.snapshot.MultiDimFit.mH125.root --others 'higgsCombine.{cat}.freezeAll.MultiDimFit.mH125.root:FreezeAll:2' -o {plotNm} --breakdown Syst,Stat &> {name}.log

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi

popd
""".format( dir            = os.path.dirname(os.path.abspath(datacard)),
            method         = H.get_combine_method(method), 
            workspace_root = workspace_file,
            datacard       = os.path.basename(datacard), 
            mass           = mass,
            verbose        = verbose, 
            run_validation = str(run_validation).lower(),
            cat            = cat,
            plotNm         = 'signal_strength_'+cat, 
            name           = output_prefix )
            
            elif method =='nll_shape':
                create = True
                script = FastScanNLLshape(workspace_file, datacard, output_prefix, output_dir, mass, method)
            
            elif method =='fit':
                # for PAG closure checks : https://twiki.cern.ch/twiki/bin/view/CMS/HiggsWG/HiggsPAGPreapprovalChecks
                create = True
                script = """#! /bin/bash

# http://cms-analysis.github.io/CombineHarvester/post-fit-shapes-ws.html
pushd {dir}

# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi

# print yield tables
if [ ! -d YieldTables ]; then
    mkdir YieldTables;
fi

# Run combined
# Fit the {name} distribution

if [ ! -d plotIt_{cat} ]; then
    mkdir plotIt_{cat};
fi

pushd plotIt_{cat}
    combine {method} -m {mass} {dataset} --saveWithUncertainties --ignoreCovWarning -n {name} ../{workspace_root} --plots --verbose {verbose} &> {name}.log
popd 


# Create pre/post-fit shapes 
#fit_b   RooFitResult object containing the outcome of the fit of the data with signal strength set to zero
#fit_s   RooFitResult object containing the outcome of the fit of the data with floating signal strength

CAT={CAT}
fits=("fit_s" "fit_b")  

for fit_what in ${{fits[*]}}; do
    
    if [ ! -d plotIt_{cat}/${{fit_what}} ]; then
        mkdir plotIt_{cat}/${{fit_what}};
    fi
    
    pushd plotIt_{cat}/${{fit_what}} 
    
    PostFitShapesFromWorkspace -w ../../{workspace_root} -d ../../{datacard} -o ../fit_shapes_${{CAT}}_${{fit_what}}.root -f ../fitDiagnostics{prefix}.root:${{fit_what}} -m {mass} --postfit --sampling --covariance --total-shapes --print

    {c}$CMSSW_BASE/../utils/convertPrePostfitShapesForPlotIt.py -i ../fit_shapes_${{CAT}}_${{fit_what}}.root -o . --signal-process HToZATo2L2B -n {name2}
    $CMSSW_BASE/../utils/printYieldTables.py -w ../../{workspace_root} -f ../fitDiagnostics{prefix}.root -s {signal} -b {bin} --fit ${{fit_what}} -o ../../YieldTables
    
    # Generate JSON for interactive covariance viewer
    # https://cms-hh.web.cern.ch/tools/inference/scripts.html#generate-json-for-interactive-covariance-viewer
    $CMSSW_BASE/../utils/extract_fitresult_cov.json.py ../fitDiagnostics{prefix}.root
    
    popd

done

run_validation={run_validation}
if $run_validation; then 
    if [ ! -d validation_datacards ]; then
        mkdir validation_datacards;
    fi
    ValidateDatacards.py {datacard} --mass {mass} --printLevel 3 --jsonFile validation_datacards/validation_{name}.json &> validation_datacards/validation_{name}.log
fi

popd
""".format(workspace_root = workspace_file, 
           prefix         = output_prefix, 
           cat            = cat, 
           bin            = bin_id, 
           signal         = sig_process[0],  
           CAT            = cat+'_'+bin_id, 
           dir            = os.path.abspath(output_dir),
           name           = output_prefix, 
           name2          = Constants.get_Nm_for_runmode(mode),
           c              = '#' if skip else '',
           datacard       = os.path.basename(datacard), 
           mass           = mass, 
           verbose        = verbose, 
           run_validation = str(run_validation).lower(),
           method         = H.get_combine_method(method), 
           dataset        = '' if unblind else ('-t -1' if dataset=='asimov' else ('-t 8 -s -1')) )
            
            if create:
                script_file = os.path.join(output_dir, output_prefix + ('_run_%s.sh' % method))
                print( method, script_file)
                with open(script_file, 'w') as f:
                    f.write(script)
        
                st = os.stat(script_file)
                os.chmod(script_file, st.st_mode | stat.S_IEXEC)

        # Write card and save shape root files
        logger.info("Writing datacards!")
        print (categories_with_parameters )
         
        def writeCard(c, mass, output_dir, output_file, cat, opts, script=True):
            datacard  = os.path.join(output_dir, output_file + '.dat')
            # this did not work !
            #shapeFile = ROOT.TFile(os.path.join(output_dir, output_file + '_shapes.root'), 'recreate')
            #c.cp().mass([mass, "*"]).WriteDatacard(datacard, shapeFile)
            #shapeFile.Close()           
            
            # parse again the datacard for smoothing
            # ParseDatacard(filename, analysis, era, channel, bin_id, mass)
            #c.cp().ParseDatacard(datacard, analysis=analysis[0], era='13TeV_%s'%era, channel=cat, mass=mass)#, bin_id) 
            #c.cp().FilterProcs(lambda x: H.drop_zero_procs(c,x)) 
            #c.cp().bin([bin_id]).ForEachSyst(lambda x: H.symmetrise_smooth_syst(c, x) if (x.name().startswith("CMS_scale_j") or x.name().startswith("CMS_res_j") or x.name().startswith("QCD")) else None)
            #c.cp().FilterSysts(lambda x: H.drop_zero_systs(x))
            #c.cp().FilterSysts(lambda x: H.drop_onesided_systs(x))

            c.cp().mass([mass, "*"]).WriteDatacard(datacard, os.path.join(output_dir, output_file + '_shapes.root'))
            
            #shapeFile_smooth = ROOT.TFile(os.path.join(output_dir, output_file + '_smooth_shapes.root'), 'recreate')
            #datacard_smooth  = os.path.join(output_dir, output_file + '.dat')
            #c.cp().WriteDatacard(datacard, os.path.join(output_dir, output_file + '_smooth_shapes.root'))
            #c.cp().AddDatacardLineAtEnd("* autoMCStats 0")
            #shapeFile_smoothed.Close()           
           
            if script:
                createRunCombineScript(bin_id, mass, output_dir, output_file, cat, opts, create=False, skip=False)
        
        #cb.PrintObs()
        #cb.PrintProcs()
        #cb.PrintAll()
        #cb.PrintSysts()
        #cb.PrintParams()
        for cat in analysis_categories:
            opts = {'process': prod, 'nb': reco, 'region': reg, 'flavor': cat.split('_')[-1]}
            output_file = output_prefix + '_%s_%s' % (cat, bin_id)
            
            shallow_cp = cb.cp().bin([bin_id]).channel([cat])
            shallow_cp.PrintProcs()
            shallow_cp.PrintObs()
            print('--------------------------------------------------------------------------------------------------------')
            writeCard(shallow_cp, mass, output_dir, output_file, cat, opts, script=True)
            

        if merge_cards and method not in ['generatetoys']:
            
            list_mergeable_flavors = [['MuMu', 'ElEl'], ['MuMu', 'ElEl', 'MuEl'], ['OSSF', 'MuEl'], ['MuMu', 'MuEl'], ['ElEl', 'MuEl']] 
            
            Totflav_cards_allparams[(output_dir, bin_id)] = {'OSSF': [], 
                                                          'OSSF_MuEl': [],
                                                          'split_OSSF': [],
                                                          'split_OSSF_MuEl':[] }
               
            ToSKIP = [['MuMu', 'MuEl'], ['ElEl', 'MuEl']]
            default_comb = []
            
            if prod in ['bb_associatedProduction', 'gg_fusion_bb_associatedProduction'] or reg =='boosted' or reco =='nb3':
                default_comb = [['OSSF', 'MuEl']]
                Totflav_cards_allparams[(output_dir, bin_id)]['OSSF'].append("ch2_{}_{}_{}_{}_OSSF=".format(mode, '_'.join(sig_process), reco, reg) + 
                    "{prefix}_{prod}_{reco}_{reg}_{flavor}_{bin_id}.dat".format(prefix=output_prefix, prod=prod, reco=reco, reg=reg, flavor="OSSF", bin_id=bin_id))
            else:
                # these flav are by default in split mode and the comb does not exit
                ToSKIP += [['OSSF', 'MuEl']]
            
            for mflav in list_mergeable_flavors:
                if all(x in flavors for x in mflav):
                    print("Merging {} datacards into a single one for bin  {}".format(mflav, bin_id))
                    args = ["ch{i}_{mode}_{sig}_{reco}_{reg}_{flavor}={prefix}_{prod}_{reco}_{reg}_{flavor}_{bin_id}.dat".format(
                                i=i+1, mode=mode, sig='_'.join(sig_process), reco=reco, reg=reg, flavor=x, prefix=output_prefix, prod=prod, bin_id=bin_id) for i, x in enumerate(mflav)]
                    cmd  = ['combineCards.py'] + args
                    
                    merged_flav_datacard = output_prefix + '_'+ prod +'_' + reco+ '_' + reg + '_'+ '_'.join(mflav) + '_' + bin_id
                    
                    with open( os.path.join(output_dir, merged_flav_datacard + '.dat'), 'w+') as f:
                        subprocess.check_call(cmd, cwd=output_dir, stdout=f)
                    
                    opts = {'process': prod, 'nb': reco, 'region': reg, 'flavor': '_'.join(mflav)}
                    createRunCombineScript(bin_id, mass, output_dir, merged_flav_datacard, prod +'_' + reco+ '_' + reg + '_'+ '_'.join(mflav), opts, create=False, skip=True)
                    
                    if not mflav in ToSKIP:
                        if mflav in default_comb:
                            if 'MuEl' in mflav: k = 'OSSF_MuEl'
                            else: k = 'OSSF'
                        else:
                            if H.splitLep:
                                if 'MuEl' in mflav: k = 'split_OSSF_MuEl'
                                else: k = 'split_OSSF'
                        Totflav_cards_allparams[(output_dir, bin_id)][k] += args

    return Totflav_cards_allparams, ToFIX



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Create shape datacards ready for combine')
    
    # must 
    parser.add_argument('-i', '--input',        action='store', dest='input', type=str, required=True, default=None, 
                                                help='HistFactory input path: those are the histograms for signal/data/backgrounds that pass through all the following\n'
                                                     'steps: 1/- final selection ( 2lep+2bjets pass btagging discr cut + met + corrections + etc... )\n'
                                                     '       2/- do skim\n'
                                                     '       3/- DNN trained using these skimmed trees\n'
                                                     '       4/- run bamboo to produce your dnn outputs(prefit plots) with all systematics variations using the model you get from training.\n'
                                                     '       5/- Bayesian Blocks rebinning ( if requestd)\n')
    parser.add_argument('-o', '--output',       action='store', dest='output', required=True, default=None,        
                                                help='Output directory')
    parser.add_argument('--bambooDir',          action='store', dest='bambooDir', required=True, default=None,        
                                                help='Bamboo stage out dir')
    parser.add_argument('--era',                action='store', dest='era', required=True, default=None, choices=['2016preVFP', '2016postVFP', '2016', '2017', '2018', 'fullrun2'],
                                                help='You need to pass your era')
    parser.add_argument('--mode',               action='store', dest='mode', default='dnn', choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'mbb', 'mllbb', 'ellipse', 'dnn'],
                                                help='Analysis mode')
    parser.add_argument('--node',               action='store', dest='node', default='ZA', choices=['DY', 'TT', 'ZA'],
                                                help='DNN nodes')
    parser.add_argument('--method',             action='store', dest='method', required=True, default=None, choices=['validation_datacards', 'nll_shape', 'asymptotic', 'hybridnew', 'fit', 'impacts', 'generatetoys', 'signal_strength', 'pvalue', 'goodness_of_fit', 'likelihood_fit'],        
                                                help='Analysis method')
    parser.add_argument('--expectSignal',       action='store', required=False, type=int, default=1, choices=[0, 1],
                                                help=' Is this S+B or B-Only fit? ')
    # normalisation 
    parser.add_argument('--normalize',          action='store_true', dest='normalize', required=False, default=False,                                                  
                                                help='normalize the inputs histograms : lumi * xsc * (BR if signal) / sum_of_generated_evets_weights')
    parser.add_argument('--scale',              action='store_true', dest='scale', required=False, default=False,                                                  
                                                help='scale signal rate will x1000')
    ## extra 
    parser.add_argument('-s', '--stat',         action='store_true', dest='stat_only', required=False, default=False,                                                           
                                                help='Do not consider systematic uncertainties')
    parser.add_argument('--ellipses-mumu-file', action='store', dest='ellipses_mumu_file', required=False, default='./data/fullEllipseParamWindow_MuMu.json',
                                                help='file containing the ellipses parameters for MuMu (ElEl is assumed to be in the same directory)')
    parser.add_argument('--splitJECs',          action='store_true', dest='splitJECs', required=False, default=False,                                                  
                                                help='split JES and JER by uncertaintues sources')
    parser.add_argument('--splitLep',           action='store_true', dest='splitLep', required=False, default=True,                                                  
                                                help='combine ee+mumu for bbH and boosted cat. ( combination on the level of histograms not the datacards )')
    parser.add_argument('--splitTTbar',         action='store_true', dest='splitTTbar', required=False, default=True,                                                  
                                                help='This will split ttbar between tt+b and tt ')
    parser.add_argument('--splitDrellYan',      action='store_true', dest='splitDrellYan', required=False, default=False,                                                  
                                                help='This will split splitDrellYan into DY+0jets, DY+1jets and DY+2jets')
    parser.add_argument('--splitEraUL2016',     action='store_true', dest='splitEraUL2016', required=False, default=False,                                                  
                                                help='Will work with 2016 split between pre/post VFP')
    parser.add_argument('--FixbuggyFormat',     action='store_true', dest='FixbuggyFormat', required=False, default=False,                                                  
                                                help='Will be removed in the next itertaion of bamboo histograms')
    parser.add_argument('--rm_mix_lo_nlo_bbH_signal',  action='store_true', dest='rm_mix_lo_nlo_bbH_signal', required=False, default=False,                                                  
                                                help='bbH signal @ nlo will not be processed, only the samples produced @ lo')
    parser.add_argument('--validation_datacards',action='store_true', dest='validation_datacards', required=False, default=False,                                                  
                                                help='Will run https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/validation/ and save the results in json files')
    # slurm
    parser.add_argument('--slurm',              action='store_true', dest='submit_to_slurm', required=False, default=False,                                                  
                                                help='slurm submission for long pull and impacts jobs')
    parser.add_argument('--sbatch_time',        action='store', type=str, dest='sbatch_time', required=False, default='02:59:00',                                                  
                                                help='slurm submission time')
    parser.add_argument('--sbatch_memPerCPU',   action='store', type=str, dest='sbatch_memPerCPU', required=False, default='7000',                                                  
                                                help='slurm requested memory per cpu')
    # r 
    parser.add_argument('--_2POIs_r',           action='store_true', dest='_2POIs_r', required=False, default=False,                                                  
                                                help='This will merge both signal in 1 histogeram and normalise accoridngly, tanbeta will be required')
    parser.add_argument('--multi_signal',       action='store_true', dest='multi_signal', required=False, default=False,                                                  
                                                help='The cards will contain both signals but using 1 discriminator ggH -> for nb2 and bbH -> for nb3')
    parser.add_argument('--tanbeta',            action='store', type=float, required=False, default=None, 
                                                help='tanbeta value needed for BR and theory cross-section during the normalisation\n'
                                                     'This is required so both signal are normalised using one value during the card combination\n')
    # data    
    parser.add_argument('--unblind',            action='store_true', dest='unblind', required=False,
                                                help='Unblind analysis :: use real data instead of fake pseudo-data')
    parser.add_argument('--dataset',            action='store', dest='dataset', choices=['toys', 'asimov'], required='--unblind' not in sys.argv, default=None,                             
                                                help='if asimov:\n'
                                                        '-t -1 will produce an Asimov dataset in which statistical fluctuations are suppressed. \n'
                                                     'if toys: \n'
                                                        '-t N with N > 0. Combine will generate N toy datasets from the model and re-run the method once per toy. \n'
                                                        'The seed for the toy generation can be modified with the option -s (use -s -1 for a random seed). \n'
                                                        'The output file will contain one entry in the tree for each of these toys.\n')
    
    parser.add_argument('-v', '--verbose',      action='store', required=False, type=int, default=0, 
                                                help='For debugging purposes , you may consider this argument !')
    
    options = parser.parse_args()
    
    H.splitEraUL2016 = options.splitEraUL2016
    H.splitJECs      = options.splitJECs
    H.splitLep       = options.splitLep
    H.splitTTbar     = options.splitTTbar
    H.splitDrellYan  = options.splitDrellYan 
    H.FixbuggyFormat = options.FixbuggyFormat
    H.rm_mix_lo_nlo_bbH_signal = options.rm_mix_lo_nlo_bbH_signal

    if not os.path.isdir(options.output):
        os.makedirs(options.output)
    
    Years = ['16preVFP', '16postVFP', '17', '18'] if H.splitEraUL2016 else [16, 17, 18]
    
    for thdm in ['HToZA', 'AToZH']:
        
        heavy = thdm[0]
        light = thdm[-1]
        
        poi_dir, tb_dir, CL_dir = Constants.locate_outputs( options.method, options._2POIs_r, options.tanbeta, options.expectSignal)
        
        if options.era == "fullrun2" and options.method != "generatetoys":
            to_combine = defaultdict()
            outDir = os.path.join(options.output, H.get_method_group(options.method), options.mode, CL_dir, poi_dir, tb_dir)
            
            for prod in ['gg_fusion', 'bb_associatedProduction']:
                for reco in ['nb2', 'nb3', 'nb2PLusnb3']:
                    for reg in ['resolved', 'boosted', 'resolved_boosted']:
                        
                        flavors = return_flavours_to_process(reco, reg, prod, splitLep=H.splitLep)

                        for flav in flavors:
                            cat = '{}_{}_{}_{}_{}'.format(prod, reco, reg, '_'.join(flav), options.mode)
                            to_combine[cat] = {}
                            for j, year in enumerate(Years):
                                
                                mPath = os.path.join(outDir.replace('work__ULfullrun2', 'work__UL{}'.format(year)))
                                for p in glob.glob(os.path.join(mPath, 'M%s-*'%heavy)):
                                    
                                    masses = p.split('/')[-1]
                                    cardNm = '{}To2L2B_{}_{}_{}_{}_{}_{}.dat'.format(thdm, prod, reco, reg, '_'.join(flav), options.mode, masses.replace('-','_'))
                                    shNm   = '{}To2L2B_{}_{}_{}_{}_{}_{}_run_{}.sh'.format(thdm, prod, reco, reg, '_'.join(flav), options.mode, masses.replace('-','_'), options.method)
                                    
                                    pOut = p.replace('work__UL{}'.format(year), 'work__ULfullrun2')
                                    if not os.path.isdir(pOut):
                                        os.makedirs(pOut)
                                    
                                    if not os.path.exists(os.path.join(p, shNm)):
                                        continue

                                    if j ==0:
                                        shutil.copy(os.path.join(p, shNm), pOut)
                                        lumi = round(Constants.getLuminosity(H.PlotItEraFormat('20'+year))/1000., 2) 
                                        Constants.overwrite_path(os.path.join(pOut, shNm), 'UL'+year, str(lumi))
                                    
                                    if not masses in to_combine[cat].keys():
                                        to_combine[cat][masses]= ['combineCards.py']
                                    to_combine[cat][masses].append('UL{}={}'.format(year, os.path.join(p, cardNm)))

            for cat, Cmd_per_mass in to_combine.items():        
                for m, cmd in to_combine[cat].items():
                    
                    if len(cmd) !=(len(Years)+1): 
                        logger.warning("The {}-years cards are needed".format(len(Years)))
                        logger.warning("trying to run :: ' {} ' for {}\\".format(" ".join(cmd), m))

                    CardOut = '{}/{}/{}'.format(outDir, m, cmd[1].split('/')[-1])
                    try:
                        with open(CardOut, "w+") as outfile:
                            subprocess.call(cmd, stdout=outfile)
                    except subprocess.CalledProcessError:
                        logger.error("Failed to run {0}".format(" ".join(cmd)))
            
            CreateScriptToRunCombine(options.output, options.method, options.mode, options.tanbeta, options.era, options._2POIs_r, options.expectSignal, options.sbatch_time, options.sbatch_memPerCPU, options.submit_to_slurm)
        
        else:
            # get latest BB histograms from other dir
            if options.method != "generatetoys":
                #bb = os.path.join(os.path.dirname(os.path.abspath(__file__)), options.output.split('work_')[0], 'work__ULfullrun2', '/bayesian_rebin_on_S/results')
                bb = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hig-22-010/unblinding_stage1/followup1__ext23/work__ULfullrun2/bayesian_rebin_on_S/results')
                Constants.SymbolicLinkForBayesianResults(bb, options.output)
            
            scalefactors  = H.get_normalisationScale(options.bambooDir, options.input, options.output, options.method, options.era)
            
            # for test or for specific points : please use signal_grid_foTest,
            # otherwise the full list of samples will be used !
            signal_grid = Constants.get_SignalMassPoints(H.PlotItEraFormat(options.era), returnKeyMode= False, split_sig_reso_boo= False) 
        
            prepare_DataCards(  grid_data           = signal_grid,#_foTest, 
                                thdm                = thdm,
                                dataset             = options.dataset, 
                                expectSignal        = options.expectSignal, 
                                era                 = options.era, 
                                mode                = options.mode.lower(), 
                                input               = options.input, 
                                ellipses_mumu_file  = options.ellipses_mumu_file, 
                                output              = options.output, 
                                method              = options.method, 
                                node                = options.node, 
                                scalefactors        = scalefactors,
                                tanbeta             = options.tanbeta,
                                verbose             = options.verbose, 
                                sbatch_time         = options.sbatch_time,
                                sbatch_memPerCPU    = options.sbatch_memPerCPU,
                                unblind             = options.unblind, 
                                stat_only           = options.stat_only, 
                                merge_cards         = True, # will do all lepton flavour combination of ee+mumu+mue / also resolved+boosted / also nb2+nb3 
                                _2POIs_r            = options._2POIs_r, # r_ggH , r_bbH or just 1 POI r
                                multi_signal        = options.multi_signal,
                                scale               = options.scale, 
                                normalize           = options.normalize,
                                run_validation      = options.validation_datacards,
                                submit_to_slurm     = options.submit_to_slurm)


