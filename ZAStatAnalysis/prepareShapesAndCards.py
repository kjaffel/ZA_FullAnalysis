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

import numpy as np

import Harvester as H
import Constants as Constants
import CombineHarvester.CombineTools.ch as ch

logger = Constants.ZAlogger(__name__)

H.splitTTbarUncertBinByBin = False


signal_grid_foTest = { 
    'gg_fusion': { 
        'resolved': { 
            'HToZA': [(500., 200.)],
            'AToZH': [] },
        'boosted': {
            'HToZA': [(500., 200.)], 
            'AToZH': [] }
        },
    'bb_associatedProduction': { 
        'resolved': { 
            'HToZA': [(500., 200.)],
            'AToZH': [] },
        'boosted': {
            'HToZA': [(500., 200.)],
            'AToZH': [] }
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
            

def check_call_DataCard(cmd, thdm, prod, k, mode, output_dir, expectSignal, dataset, reco, unblind, what=''):
    newCmd= ['combineCards.py']
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
    _AsymptoticLimits(workspace_file, datacard, output_prefix, output_dir, 125, 'asymptotic', expectSignal, dataset, unblind)
    return 


def CustomCardCombination(thdm, mode, cats, proc_combination, expectSignal, dataset, prod, reg=None, skip=None, unblind=False, todo=''):
    for cat in cats:
        
        output_dir = cat[0]
        output_sig = cat[1]

        for k in ['OSSF', 'OSOF']:
            
            if todo == 'nb2_nb3':
                cmd = proc_combination['nb2_%s'%reg][cat][k] + proc_combination['nb3_%s'%reg][cat][k]
                check_call_DataCard(cmd, thdm, prod, k, mode, output_dir, expectSignal, dataset, reco='nb2PLusnb3_%s'%reg, unblind=unblind, what='nb2 & nb3 %s'%reg)

            elif todo == 'res_boo':
                if not (cat in proc_combination['nb2_resolved'].keys() or cat in proc_combination['nb2_boosted'].keys()
                        or cat in proc_combination['nb3_resolved'].keys() or cat in proc_combination['nb3_boosted'].keys()
                        ):
                    continue
                
                cmd = []
                for reco in ['nb2_resolved', 'nb2_boosted', 'nb3_resolved', 'nb3_boosted']:
                    cmd += proc_combination[reco][cat][k]

                check_call_DataCard(cmd, thdm, prod, k, mode, output_dir, expectSignal, dataset, reco='nb2PLusnb3_resolved_boosted', unblind=unblind, what='resolved & boosted ( nb2 + nb3)')
            
            elif todo == 'ggH_bbH':
                # this should not happen but in case a signal sample does not exist in both prod mechanisms
                # no need to continue here
                if any( x== output_sig for x in skip):
                    continue
                
                Tot_proc_reg_combine = []
                for j, reg in enumerate(['resolved', 'boosted']): 
                    
                    cmd = [] 
                    for reco in ['nb2', 'nb3']: 
                    
                        for prod in ['gg_fusion', 'bb_associatedProduction']:
                            cmd += proc_combination[prod][reco+'_'+reg][cat][k]
                        
                        newCmd = ['combineCards.py']
                        for i, x in enumerate(cmd):
                            if "=" in x :
                                Tot_nm   = x.split('=')[1]
                                channel  = x.split('=')[0]
                                split_ch = channel.split('_')
                                new_ch   = 'ch%s_%s'%(i+1, '_'.join(split_ch[1:]))
                                newCmd  +=[new_ch+'='+Tot_nm]
                                Tot_proc_reg_combine +=[new_ch+'='+Tot_nm]
                        
                    out_nm = newCmd[1]
                    if "=" in out_nm:
                        out_nm = out_nm.split('=')[1]

                    suffix        = out_nm.split(mode)[-1].replace('.dat', '')
                    output_prefix = '%sTo2L2B_gg_fusion_bb_associatedProduction_nb2PLusnb3_%s_%s_%s%s'%( thdm, reg, k, mode, suffix)
                    datacard      = os.path.join(output_dir, output_prefix +'.dat')
                    
                    logger.info('merging %s nb2 + nb3 %s ggH & bbH cmd::: %s'%(k, reg, newCmd) )
                    with open( datacard, 'w') as f:
                        subprocess.check_call(newCmd, cwd=output_dir, stdout=f)
                
                    for poi in ['r_ggH', 'r_bbH']:
                        workspace_file = os.path.basename(os.path.join(output_dir, output_prefix + '_combine_workspace.root'))
                        MultiSignalModel(workspace_file, datacard, output_prefix, output_dir, 125, 'asymptotic', expectSignal, poi, unblind)
                               
                FinalCmd = ['combineCards.py']
                for i, x in enumerate(list( set(Tot_proc_reg_combine))):
                    if "=" in x :
                        Tot_nm   = x.split('=')[1]
                        channel  = x.split('=')[0]
                        split_ch = channel.split('_')
                        new_ch   = 'ch%s_%s'%(i+1, '_'.join(split_ch[1:]))
                        FinalCmd+=[new_ch+'='+Tot_nm]
                
                logger.info('merging %s nb2 + nb3 + resolved + boosted ggH & bbH cmd::: %s'%(k, FinalCmd) )
                
                suffix        = FinalCmd[1].split(mode)[-1].replace('.dat', '')
                output_prefix = '%sTo2L2B_gg_fusion_bb_associatedProduction_nb2PLusnb3_resolved_boosted_%s_%s%s'%( thdm, k, mode, suffix)
                datacard      = os.path.join(output_dir, output_prefix +'.dat')
                with open( datacard, 'w') as f:
                    subprocess.check_call(FinalCmd, cwd=output_dir, stdout=f)
                
                for poi in ['r_ggH', 'r_bbH']:
                    workspace_file = os.path.basename(os.path.join(output_dir, output_prefix + '_combine_workspace.root'))
                    MultiSignalModel(workspace_file, datacard, output_prefix, output_dir, 125, 'asymptotic', expectSignal, poi, unblind)



def _AsymptoticLimits(workspace_file, datacard, output_prefix, output_dir, mass, method, expectSignal, dataset, unblind):
    script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi
# Run combined
combine {method} -m {mass} -n {name} {workspace_root} {dataset} {rule} {blind} &> {name}.log
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
            blind          = ('' if unblind else '--run blind') )

    script_file = os.path.join(output_dir, output_prefix + ('_run_%s.sh' %(method)))
    print( method, script_file)
    with open(script_file, 'w') as f:
        f.write(script)

    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)
    


def MultiSignalModel(workspace_file, datacard, output_prefix, output_dir, mass, method, expectSignal, poi, unblind):
    script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel  --PO verbose --PO 'map=.*/ggH:r_ggH[1,0,20]' --PO 'map=.*/bbH:r_bbH[1,0,20]' {datacard} -m {mass} -o {workspace_root}
fi
# Run combined
# set limit on {r} while let {poi} to float freely in the fit 
combine {method} -m {mass} -n {name}_profiled_{poi} {workspace_root} --redefineSignalPOIs {profile} {dataset} {rule} {blind} &> {name}_profiled_{poi}.log

# set limit on {r} while freeze {poi}
combine {method} -m {mass} -n {name}_freezed_{poi} {workspace_root} --redefineSignalPOIs {freeze} {dataset} {rule} {blind} &> {name}_freezed_{poi}.log

popd
""".format( workspace_root = workspace_file, 
            datacard       = os.path.basename(datacard), 
            name           = output_prefix, 
            mass           = mass, 
            poi            = poi, 
            rule           = '--rule CLsplusb' if expectSignal==0 else '',
            r              = 'r_ggH' if poi=='r_bbH' else 'r_bbH',
            profile        = 'r_ggH,r_bbH --setParameters r_bbH=0.0 --floatParameters r_bbH' if poi=='r_bbH' else 'r_bbH,r_ggH --setParameters r_ggH=0.0 --floatParameters r_ggH',
            freeze         = 'r_ggH --setParameters r_bbH=0.0 --freezeParameters r_bbH' if poi=='r_bbH' else 'r_bbH --setParameters r_ggH=0.0 --freezeParameters r_ggH',
            method         = H.get_combine_method(method), 
            dir            = os.path.dirname(os.path.abspath(datacard)), 
            #dataset       = '--bypassFrequentistFit', 
            dataset        = '--noFitAsimov',
            blind          = ('' if unblind else '--run blind') )
        
    script_file = os.path.join(output_dir, output_prefix + ('_%s_run_%s.sh' %(poi, method)))
    print( method, script_file)
    with open(script_file, 'w') as f:
        f.write(script)

    st = os.stat(script_file)
    os.chmod(script_file, st.st_mode | stat.S_IEXEC)
                

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


def CreateScriptToRunCombine(output, method, mode, era):
    output = os.path.join(output, H.get_method_group(method), mode)
    script = """#! /bin/bash
scripts=`find {output} -name "*_{suffix}.sh"`
for script in $scripts; do
    dir=$(dirname $script)
    script=$(basename $script)
    echo "\tComputing with ${{script}}"
    pushd $dir &> /dev/null
    {c}ln -s -d /home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/ul__combinedlimits/ .
    . $script
    popd &> /dev/null
done
""".format(output=output, suffix='run_%s'%method, c='' if era =='fullrun2' else '#')
   
    print( '\tThe generated script to run limits can be found in : %s/' %output)
    
    if   method == 'fit': suffix= 'prepost'
    elif method == 'impacts': suffix= 'pulls'
    elif method in ['asymptotic', 'hybridnew']: suffix= 'limits'
    else: suffix= ''

    script_name = "run_combined_%s_%s%s.sh" % (mode, method, suffix)
    with open(script_name, 'w') as f:
        f.write(script)

    st = os.stat(script_name)
    os.chmod(script_name, st.st_mode | stat.S_IEXEC)

    if method=="hybridnew":
        logger.info("All done. You can run everything by executing %r" % ('./' + script_name[:-3]+"_onSlurm.sh"))
    else:
        logger.info("All done. You can run everything by executing %r" % ('./' + script_name))



def prepare_DataCards(grid_data, thdm, dataset, expectSignal, era, mode, input, ellipses_mumu_file, output, method, node, scalefactors, unblind= False, signal_strength= False, stat_only= False, verbose= False, merge_cards= False, merge_ggH_bbH=False, scale= False, normalize= False, submit_to_slurm= False):
    
    luminosity  = Constants.getLuminosity(era)
    
    ellipses = {}
    if mode == "ellipse":
        get_ellipses_parameters(ellipses_mumu_file)

    # this is cross-check that the extracted signal mass points from the plots.yml
    # have their equivalent root file in the results/ dir  
    all_parameters = {}
    for prefix, prod in {'GluGluTo': 'gg_fusion', '': 'bb_associatedProduction'}.items():
        
        all_parameters[prod] = { 'resolved': [] , 'boosted': [] }
        for f in glob.glob(os.path.join(input, '*.root')):
            
            split_filename = f.split('/')[-1]
            if not split_filename.startswith('{}{}To2L2B_'.format(prefix, thdm)): 
                continue
            
            if era != "fullrun2":
                if not H.EraFromPOG(era) in split_filename:
                    continue
            
            for reg in ['resolved', 'boosted']:
                m_heavy, m_light = get_signal_parameters(split_filename)
                
                #==============================================================================
                # FIXME 
                # here I just need to get some work done, to  be removed later !!
                #fast_list = [125.]+list(np.arange(100., 1050., 100.))
                #if not m_heavy in fast_list:
                #    continue
                #==============================================================================

                if (m_heavy, m_light) in grid_data[prod][reg][thdm] and not (m_heavy, m_light) in all_parameters[prod][reg]:
                    all_parameters[prod][reg].append( (m_heavy, m_light) )
    
    NotIn2Prod = []    
    for tup in all_parameters['gg_fusion']['resolved']:
        if not tup in all_parameters['bb_associatedProduction']['resolved']:
            NotIn2Prod.append('%s_M%s_%s_M%s_%s'%(mode, thdm[0], tup[0], thdm[-1], tup[1]))

    logger.info("Era and the corresponding luminosity      : %s, %s" %(era, Constants.getLuminosity(era)))
    logger.info("Input path                                : %s" % input )
    logger.info("Chosen analysis mode                      : %s" % mode)

    proc_combination = {}
    cats = []
    for prod in ['gg_fusion', 'bb_associatedProduction']:
        
        proc_combination[prod] = {}
        sig_process = prod.split('_')[0]+thdm[0]
        
        for reg in ['resolved', 'boosted']:
            for reco in ['nb2', 'nb3']:
                
                if prod =='bb_associatedProduction' or reg =='boosted':
                    flavors = ['OSSF', 'MuEl']
                else:
                    flavors = ['MuMu', 'ElEl', 'MuEl']

                logger.info("Working on %s && %s cat.     :"%(prod, reg) )
                logger.info("Generating set of cards for parameter(s)  : %s" % (', '.join([str(x) for x in all_parameters[prod][reg]])))
                
                Totflav_cards_allparams = prepareShapes(input                  = input, 
                                                        dataset                = dataset, 
                                                        thdm                   = thdm, 
                                                        sig_process            = sig_process, 
                                                        expectSignal           = expectSignal, 
                                                        era                    = era, 
                                                        method                 = method, 
                                                        parameters             = all_parameters[prod][reg], 
                                                        prod                   = prod,
                                                        reco                   = reco, 
                                                        reg                    = reg, 
                                                        flavors                = flavors, 
                                                        ellipses               = ellipses, 
                                                        mode                   = mode,  
                                                        output                 = output, 
                                                        luminosity             = luminosity, 
                                                        scalefactors           = scalefactors,
                                                        scale                  = scale, 
                                                        merge_cards            = merge_cards, 
                                                        merge_ggH_bbH          = merge_ggH_bbH, 
                                                        unblind                = unblind, 
                                                        signal_strength        = signal_strength, 
                                                        stat_only              = stat_only, 
                                                        normalize              = normalize,
                                                        verbose                = verbose,
                                                        submit_to_slurm        = submit_to_slurm)
                
                proc_combination[prod][reco+'_'+reg] = Totflav_cards_allparams 
                for x in Totflav_cards_allparams.keys():
                    if x not in cats: cats.append(x) 
            
            CustomCardCombination(thdm, mode, cats, proc_combination[prod], expectSignal, dataset, prod=prod, reg=reg, skip=None, unblind=unblind, todo='nb2_nb3')
        
        CustomCardCombination(thdm, mode, cats, proc_combination[prod], expectSignal, dataset, prod=prod, reg=None, skip=None, unblind=unblind, todo='res_boo')

    if method == 'asymptotic':
        CustomCardCombination(thdm, mode, cats, proc_combination, expectSignal, dataset, prod=None, reg=None, skip=NotIn2Prod, unblind=unblind, todo='ggH_bbH')
        
    # Add mc stat. 
    for datacard in glob.glob(os.path.join(output, H.get_method_group(method), mode,'*/', '*.dat')):
        Constants.add_autoMCStats(datacard)

    # Create helper script to run combine
    CreateScriptToRunCombine(output, method, mode, era)



def prepareShapes(input, dataset, thdm, sig_process, expectSignal, era, method, parameters, prod, reco, reg, flavors, ellipses, mode, output, luminosity, scalefactors, scale=False, merge_cards=False, merge_ggH_bbH=False, unblind=False, signal_strength=False, stat_only=False, normalize=False, verbose=False, submit_to_slurm=False):
    
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

    if prod == 'gg_fusion': look_for = 'GluGluTo'
    else : look_for = ''
    
    # FIXME next iteration of plots in Bamboo
    fix_reco_format = 'gg_fusion' if reco =='nb2' else 'bb_associatedProduction'

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
            #'VVV'     : ['^(ZZZ|WWW|WZZ|WWZ)*'],
            'SMHiggs'  : ['^ggZH_HToBB_ZToLL_M-125*', '^HZJ_HToWW_M-125*', '^ZH_HToBB_ZToLL_M-125*', '^ggZH_HToBB_ZToNuNu_M-125*', '^GluGluHToZZTo2L2Q_M125*', '^ttHTobb_M125_*', '^ttHToNonbb_M125_*']
            }
    
    bkg_processes = histfactory_to_combine_processes.keys()

    # Shape depending on the signal hypothesis
    for p in parameters:
        m_heavy = p[0]
        m_light = p[1]

        formatted_p = format_parameters(p)
        
        # if merge_ggH_bbH:
        #      histfactory_to_combine_processes['{}_M{}-{}_M{}-{}'.format(sig_process, heavy, m_heavy, light, m_light), p] = [
        #                                      '^GluGluTo{}To2L2B_M{}_{}_M{}_{}*'.format(thdm, heavy, mass_to_str(m_heavy), light, mass_to_str(m_light)),
        #                                      '^{}To2L2B_M{}_{}_M{}_{}*'.format(thdm, heavy, mass_to_str(m_heavy), light, mass_to_str(m_light)) 
        #                                      ]
        histfactory_to_combine_processes['{}_M{}-{}_M{}-{}'.format(sig_process, heavy, m_heavy, light, m_light), p] = [
                                         '^{}{}To2L2B_M{}_{}_M{}_{}*'.format(look_for, thdm, heavy, mass_to_str(m_heavy), light, mass_to_str(m_light)) 
                                            ]

        if mode == "dnn":
           histfactory_to_combine_categories[('dnn_M{}_{}_M{}_{}'.format(heavy, m_heavy, light, m_light), p)] = get_hist_regex(
                'DNNOutput_ZAnode_{flavor}_{reg}_{taggerWP}_METCut_{fix_reco_format}_M%s_%s_M%s_%s'%( heavy, mass_to_str(m_heavy), light, mass_to_str(m_light)) )
        elif mode == "mllbb":
            histfactory_to_combine_categories[('mllbb', p)] = get_hist_regex('{flavor}_{reg}_METCut_NobJetER_bTagWgt_mllbb_{taggerWP}_{prod}')
        elif mode == "mbb":
            histfactory_to_combine_categories[('mbb', p)]   = get_hist_regex('{flavor}_{reg}_METCut_NobJetER_bTagWgt_mbb_{taggerWP}_{prod}')
        
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
    
    logger.info('Histfactory_to_combine_categories         : %s '%histfactory_to_combine_categories )
    logger.info('histfactory_to_combine_processes          : %s '%histfactory_to_combine_processes  )
    
    
    flav_categories = []
    for flavor in flavors:
        cat = '{}_{}_{}_{}'.format(prod, reco, reg, flavor)
        flav_categories.append(cat)

    file, systematics = H.prepareFile(processes_map       = histfactory_to_combine_processes, 
                                      categories_map      = histfactory_to_combine_categories, 
                                      input               = input, 
                                      output_filename     = os.path.join(output, 'shapes_{}_{}.root'.format(sig_process, reg)), 
                                      signal_process      = sig_process,
                                      method              = method, 
                                      luminosity          = luminosity, 
                                      mode                = mode,
                                      thdm                = thdm,
                                      flav_categories     = flav_categories,
                                      era                 = era, 
                                      scalefactors        = scalefactors,
                                      merge_ggH_bbH       = merge_ggH_bbH,
                                      unblind             = unblind,
                                      normalize           = normalize)
    
    #print ( "\tsystematics : %s       :" %systematics )
    
    processes  = [sig_process] + bkg_processes
    logger.info( "Processes       : %s" %processes)
        
    # Dummy mass value used for all combine input when a mass is needed
    mass = "125"
    
    Totflav_cards_allparams = {}
    for i, p in enumerate(parameters):
        m_heavy = p[0]
        m_light = p[1]
    
        cb = ch.CombineHarvester()
        if verbose:
            cb.SetVerbosity(3)
        cb.SetFlag("zero-negative-bins-on-import", True)
        
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
        
        #cb.AddObservations( mass, analysis, era, channel, bin)
        cb.AddObservations(['*'], [sig_process], ['13TeV_%s'%era], flav_categories, categories_with_parameters)
        
        for cat in flav_categories:
            cb.AddProcesses(['*'], [sig_process], ['13TeV_%s'%era], [cat], bkg_processes, categories_with_parameters, signal=False)
        
        cb.AddProcesses([mass], [sig_process], ['13TeV_%s'%era], flav_categories, [sig_process], categories_with_parameters, signal=True)

        if not stat_only:
            processes_without_weighted_data = cb.cp()
            processes_without_weighted_data.FilterProcs(lambda p: 'data' in p.process())
            processes_without_weighted_data.AddSyst(cb, 'lumi_$ERA', 'lnN', ch.SystMap('era')(['13TeV_%s'%era], Constants.getLuminosityUncertainty(era)))

            if not H.splitTTbarUncertBinByBin:
                cb.cp().AddSyst(cb, 'ttbar_xsec', 'lnN', ch.SystMap('process')
                    (['ttbar'], 1.001525372691124) )
            
            cb.cp().AddSyst(cb, 'SingleTop_xsec', 'lnN', ch.SystMap('process')
                    (['SingleTop'], 1.19/1.22) )
            cb.cp().AddSyst(cb, 'DY_xsec', 'lnN', ch.SystMap('process') 
                    (['DY'], 1.007841991384859) )

            xsc, xsc_err, totBR= Constants.get_SignalStatisticsUncer(m_heavy, m_light, sig_process, thdm)
            signal_uncer = 1+xsc_err/xsc

            cb.cp().AddSyst(cb, '$PROCESS_xsec', 'lnN', ch.SystMap('process')
                    ([sig_process], signal_uncer) )

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
            cb.cp().channel([cat]).signals().ExtractShapes(file, 
                                                    '$BIN/$PROCESS_M%s-%s_M%s-%s_%s'% (heavy, m_heavy, light, m_light, cat), 
                                                    '$BIN/$PROCESS_%s_%s__$SYSTEMATIC' % ('M%s-%s_M%s-%s'%(heavy, m_heavy, light, m_light), cat))
                                                    #'$BIN/$PROCESS_%s'%cat, 
                                                    #'$BIN/$PROCESS_%s__$SYSTEMATIC' %cat)

        if scale:
            cb.cp().process([sig_process]).ForEachProc(lambda x : x.set_rate(x.rate()*1000))
            cb.cp().process([sig_process]).PrintProcs()

        # Bin by bin uncertainties
        #if not stat_only:
        #    bkgs = cb.cp().backgrounds()
        #    bkgs.FilterProcs(lambda p: 'data' in p.process())
        #    bbb = ch.BinByBinFactory()
        #    bbb.SetAddThreshold(0.05).SetMergeThreshold(0.5).SetFixNorm(False)
        #    bbb.MergeBinErrors(bkgs)
        #    bbb.AddBinByBin(bkgs, cb)

        output_prefix  = '{}To2L2B'.format(thdm)
        output_dir     = os.path.join(output, H.get_method_group(method), mode, 'M%s-%s_M%s-%s'%(heavy, m_heavy, light, m_light))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Write small script to compute the limit
        def createRunCombineScript(cat, mass, output_dir, output_prefix, flavor, create=False):
            datacard       = os.path.join(output_dir, output_prefix + '.dat')
            workspace_file = os.path.basename(os.path.join(output_dir, output_prefix + '_combine_workspace.root'))

            if method == 'goodness_of_fit' and ('MuMu_ElEl' in flavor or 'OSSF' in flavor or 'ElEl_MuMu' in flavor):
                create      = True
                region      = 'resolved' if 'resolved' in flavor else 'boosted'
                label_left  = '{}-{} (ee+$\mu\mu$)'.format(sig_process, region)
                label_right = '$ %s fb^{-1} (13TeV)$'%(round(Constants.getLuminosity(era)/1000., 2))
                script      = """#!/bin/bash

#SBATCH --job-name      = Goodnessoffit
#SBATCH --time          = 1:59:00
#SBATCH --mem-per-cpu   = 1500
#SBATCH --partition     = cp3
#SBATCH --qos           = cp3
#SBATCH --ntasks        = 1
#SBATCH --array         = 0-104
#SBATCH -p debug -n 1

echo "My SLURM_ARRAY_TASK_ID: " $SLURM_ARRAY_TASK_ID

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi

{slurm}combine -M GoodnessOfFit {workspace_root} -m {mass} --algo=saturated --toysFreq
{slurm}combine -M GoodnessOfFit {workspace_root} -m {mass} --algo=saturated -t 500 -s {seed} -n Toys --toysFreq
{slurm}combine -M GoodnessOfFit {workspace_root} -m {mass} --algo=saturated -t 500 -s {seed} -n Toys --toysFreq
combineTool.py -M CollectGoodnessOfFit --input higgsCombineTest.GoodnessOfFit.mH125.root higgsCombineToys.GoodnessOfFit.mH125.{seed}.root -m 125.0 -o gof__{fNm}.json 
plotGof.py gof__{fNm}.json --statistic saturated --mass 125.0 -o gof_{fNm} --title-right="{label_right}" --title-left="{label_left}"
popd
""".format( workspace_root = workspace_file,
            datacard       = os.path.basename(datacard), 
            fNm            = flavor,
            seed           = random.randrange(100, 1000, 3),
            label_left     = label_left,
            label_right    = label_right,
            mass           = mass,
            slurm          = 'srun ' if submit_to_slurm else '', 
            dir            = os.path.dirname(os.path.abspath(datacard)) )


            if method == 'pvalue' and ( 'MuMu_ElEl' in flavor or 'OSSF' in flavor):
                create = True
                script ="""#!/bin/bash -l

#SBATCH --job-name=pvalue
#SBATCH --time=1:59:00
#SBATCH --mem-per-cpu=1500
#SBATCH --partition=cp3
#SBATCH --qos=cp3
#SBATCH --ntasks=1
#SBATCH -p debug -n 1
#SBATCH --array=0-104

# Print this sub-job's task ID
echo "My SLURM_ARRAY_TASK_ID: " $SLURM_ARRAY_TASK_ID

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}{SLURM_ARRAY_TASK_ID}.root
fi

#=============================================
# Computing Significances with toys
#=============================================
#{slurm}combine -M HybridNew {datacard} --LHCmode LHC-significance --saveToys --fullBToys --saveHybridResult -T 500 -i 10 -s 1 -m {mass} {verbose} &> {name}__toys1.log
#{slurm}combine -M HybridNew {datacard} --LHCmode LHC-significance --saveToys --fullBToys --saveHybridResult -T 500 -i 10 -s 2 -m {mass} {verbose} &> {name}__toys2.log
#{slurm}combine -M HybridNew {datacard} --LHCmode LHC-significance --saveToys --fullBToys --saveHybridResult -T 500 -i 10 -s 3 -m {mass} {verbose} &> {name}__toys3.log
#{slurm}combine -M HybridNew {datacard} --LHCmode LHC-significance --saveToys --fullBToys --saveHybridResult -T 500 -i 10 -s 4 -m {mass} {verbose} &> {name}__toys4.log
#{slurm}combine -M HybridNew {datacard} --LHCmode LHC-significance --saveToys --fullBToys --saveHybridResult -T 500 -i 10 -s 5 -m {mass} {verbose} &> {name}__toys5.log

if [ -f merged.root ]; then
    rm merged.root
    echo "merged.root is removed, to be created again !"
fi

#hadd merged.root higgsCombineTest.HybridNew.mH125.1.root higgsCombineTest.HybridNew.mH125.2.root higgsCombineTest.HybridNew.mH125.3.root higgsCombineTest.HybridNew.mH125.4.root higgsCombineTest.HybridNew.mH125.5.root 

# Observed significance with toys
#{slurm}combine -M HybridNew {datacard} --LHCmode LHC-significance --readHybridResult --toysFile=merged.root --grid=higgsCombineTest.significance_obs.mH{mass}.root --pvalue -m {mass} {verbose} &> {name}__significance_obs.log

# Expected significance, assuming some signal
#{slurm}combine -M HybridNew {datacard} --LHCmode LHC-significance --readHybridResult --toysFile=merged.root --grid=higgsCombineTest.significance_exp_plus_s.mH{mass}.root --pvalue --expectedFromGrid=0.84 -m {mass} {verbose} &> {name}__significance_exp_plus_s.log
#=============================================

{c}echo "Observed significance"
{c}combine {method} {workspace_root}.root -m {mass} &> observed__significance_expectSignal{expectSignal}_{flavor}.log

echo "Expected significance"
combine {method} {workspace_root}.root {dataset} --expectSignal {expectSignal} -m {mass} --toysFreq &> expected__significance_expectSignal{expectSignal}_{flavor}.log

{c}echo "Observed p-value" 
{c}combine {method} {workspace_root}.root --pvalue -m {mass} &> observed__pvalue_expectSignal{expectSignal}_{flavor}.log

echo "Expected p-value" 
combine {method} {workspace_root}.root {dataset} --expectSignal {expectSignal} --pvalue -m {mass} --toysFreq &> expected__pvalue_expectSignal{expectSignal}_{flavor}.log

popd
""".format( workspace_root = workspace_file.replace('.root', ''), 
            datacard       = os.path.basename(datacard), 
            flavor         = flavor, 
            mass           = mass,
            name           = 'sig__toysFreq__{}'.format(output_prefix),
            slurm          = 'srun ' if submit_to_slurm else '', 
            seed           = random.randrange(100, 1000, 3),
            method         = H.get_combine_method(method), 
            dataset        = '' if unblind else ('-t -1' if dataset=='asimov' else ('-t 8 -s -1')),
            c              = '' if unblind else '#',
            verbose        = '--verbose 2' if verbose else '',
            dir            = os.path.dirname(os.path.abspath(datacard)),
            expectSignal   = expectSignal, 
            SLURM_ARRAY_TASK_ID = '${SLURM_ARRAY_TASK_ID}' if submit_to_slurm else '')
            
            if method == 'hybridnew':
                create = True
                script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi
# Run limit
combine {method} --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}.log
combine {method} --expectedFromGrid=0.5   --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}_exp.log
combine {method} --expectedFromGrid=0.84  --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}_P1sigma.log
combine {method} --expectedFromGrid=0.16  --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}_M1sigma.log
combine {method} --expectedFromGrid=0.975 --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}_P2sigma.log
combine {method} --expectedFromGrid=0.025 --X-rtd MINIMIZER_analytic -m {mass} -n {name} {workspace_root} -S {systematics} &> {name}_M2sigma.log
popd
""".format( workspace_root = workspace_file, 
            datacard       = os.path.basename(datacard), 
            name           = output_prefix, 
            mass           = mass, 
            systematics    = (0 if stat_only else 1), 
            method         = H.get_combine_method(method), 
            dir            = os.path.dirname(os.path.abspath(datacard)) )
            
            elif method == 'asymptotic':
                create = True
                script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi
# Run combined
combine {method} -m {mass} -n {name} {workspace_root} {dataset} {rule} {blind} &> {name}.log
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
            blind          = ('' if unblind else '--run blind') 
            )
            
            elif method =='impacts' and ( 'MuMu' in flavor or 'ElEl' in flavor or 'OSSF' in flavor):
                create = True
                data   = 'real' if unblind else dataset
                fNm    = '{}_realdataset'.format( flavor) if unblind else '{}_expectSignal{}_{}dataset'.format( flavor, expectSignal, dataset)
                script = """#! /bin/bash

#SBATCH --time=1:59:00
#SBATCH --mem-per-cpu=1500
#SBATCH --partition=cp3
#SBATCH --qos=cp3

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi
# Run combined
{slurm}combineTool.py {method} -d {workspace_root} -m 125 {dataset} {expectSignal} --doInitialFit --robustFit 1 &> {name}_doInitialFit.log
{slurm}combineTool.py {method} -d {workspace_root} -m 125 {dataset} {expectSignal} --robustFit 1 --doFits --parallel 30 &> {name}_robustFit.log
{slurm}combineTool.py {method} -d {workspace_root} -m 125 {dataset} {expectSignal} -o impacts__{fNm}.json &> {name}_impacts.log
{slurm}plotImpacts.py -i impacts__{fNm}.json -o impacts__{fNm}
popd
""".format( workspace_root = workspace_file, 
            slurm          = 'srun ' if submit_to_slurm else '',
            name           = output_prefix,
            fNm            = fNm, 
            datacard       = os.path.basename(datacard), 
            mass           = mass,
            method         = H.get_combine_method(method), 
            dir            = os.path.dirname(os.path.abspath(datacard)), 
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
combine -M GenerateOnly {workspace_root} {dataset} --toysFile --saveToys -m 125 {expectSignal} {systematics} -n {fNm} &> {name}.log
popd
""".format( dir            = os.path.dirname(os.path.abspath(datacard)),
            workspace_root = workspace_file,
            datacard       = os.path.basename(datacard), 
            mass           = mass,
            dataset        = ('-t -1' if dataset=='asimov' else '-t 1 -s -1'),
            expectSignal   = '--expectSignal {}'.format(expectSignal),
            systematics    = t, 
            name           = output_prefix,
            fNm            = '_{}_expectSignal{}_{}'.format(t.replace('--',''), expectSignal, output_prefix))


            elif method == 'signal_strength':
                create = True
                script = """#! /bin/bash

pushd {dir}
# If workspace does not exist, create it once
if [ ! -f {workspace_root} ]; then
    text2workspace.py {datacard} -m {mass} -o {workspace_root}
fi
combine {method} {workspace_root} -n .part0.snapshot -t -1 -m 125 --algo grid --points 30 --saveWorkspace
combine -M MultiDimFit  higgsCombine.part0.snapshot.MultiDimFit.mH125.root -n .part0.freezeAll -m 125 --algo grid --points 30 --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit
python $CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/plot1DScan.py higgsCombine.part0.snapshot.MultiDimFit.mH125.root --others 'higgsCombine.part0.freezeAll.MultiDimFit.mH125.root:FreezeAll:2' -o {plotNm} --breakdown Syst,Stat &> {name}.log
""".format( dir            = os.path.dirname(os.path.abspath(datacard)),
            method         = H.get_combine_method(method), 
            workspace_root = workspace_file,
            datacard       = os.path.basename(datacard), 
            mass           = mass,
            plotNm         = 'signal_strength_'+flavor, 
            name           = output_prefix )
            
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

# Run combined
# Fit the {name} distribution
combine {method} -m {mass} {dataset} --saveWithUncertainties --ignoreCovWarning -n {name} {workspace_root} --plots &> {name}.log

CAT={CAT}

#fit_b   RooFitResult object containing the outcome of the fit of the data with signal strength set to zero
#fit_s   RooFitResult object containing the outcome of the fit of the data with floating signal strength

# Create pre/post-fit shapes 
{c}fit_what=fit_s
{c}PostFitShapesFromWorkspace -w {workspace_root} -d {datacard} -o fit_shapes_${{CAT}}_${{fit_what}}.root -f fitDiagnostics{prefix}.root:${{fit_what}} -m {mass} --postfit --sampling --covariance --total-shapes --print
{c}$CMSSW_BASE/../utils/convertPrePostfitShapesForPlotIt.py -i fit_shapes_${{CAT}}_${{fit_what}}.root -o plotIt_{flavor}_${{fit_what}} --signal-process HToZATo2L2B -n {name2}

fit_what=fit_b
PostFitShapesFromWorkspace -w {workspace_root} -d {datacard} -o fit_shapes_${{CAT}}_${{fit_what}}.root -f fitDiagnostics{prefix}.root:${{fit_what}} -m {mass} --postfit --sampling --covariance --total-shapes --print
$CMSSW_BASE/../utils/convertPrePostfitShapesForPlotIt.py -i fit_shapes_${{CAT}}_${{fit_what}}.root -o plotIt_{flavor}_${{fit_what}} --signal-process HToZATo2L2B -n {name2}

popd
""".format(workspace_root = workspace_file, 
           prefix         = output_prefix, 
           flavor         = flavor, 
           CAT            = cat, 
           dir            = os.path.abspath(output_dir),
           name           = output_prefix, 
           name2          = Constants.get_Nm_for_runmode(mode),
           c              = '#' if 'MuEl' in flavor else '',
           datacard       = os.path.basename(datacard), 
           mass           = mass, 
           method         = H.get_combine_method(method), 
           dataset        = '' if unblind else ('-t -1' if dataset=='asimov' else ('-t 8 -s -1')) )

            
            if create:
                script_file = os.path.join(output_dir, output_prefix + ('_run_%s.sh' % method))
                print( method, script_file)
                with open(script_file, 'w') as f:
                    f.write(script)
        
                st = os.stat(script_file)
                os.chmod(script_file, st.st_mode | stat.S_IEXEC)

        # Write card
        logger.info("Writing datacards!")
        print (categories_with_parameters )
        
        def writeCard(c, mass, output_dir, output_prefix, flavor, script=True):
            datacard = os.path.join(output_dir, output_prefix + '.dat')
            cat      = categories_with_parameters[0][1]
            c.cp().mass([mass, "*"]).WriteDatacard(datacard, os.path.join(output_dir, output_prefix + '_shapes.root'))
            if script:
                createRunCombineScript(cat, mass, output_dir, output_prefix, flavor)

        for flavor in flav_categories:
            for i, cat in enumerate(categories_with_parameters):
                cat_output_prefix = output_prefix + '_%s_%s' % (flavor, cat[1])
                cb.PrintObs() 
                print('--------------------------------------------------------------------------------------------------------')
                # cb_shallow_copy = cb.cp()
                writeCard( cb.cp().bin([cat[1]]).channel([flavor]), mass, output_dir, cat_output_prefix, flavor, i + 1 == len(categories_with_parameters))
            
        if merge_cards and method != 'generatetoys':
            list_mergeable_flavors = [['MuMu', 'ElEl'], ['MuMu', 'ElEl', 'MuEl'], ['OSSF', 'MuEl'], ['MuMu', 'MuEl'], ['ElEl', 'MuEl']] 
            
            for i, cat in enumerate(categories_with_parameters):
                
                Totflav_cards_allparams[(output_dir, cat[1])] = {'OSSF': [], 
                                                                 'OSOF': [] }
                
                if prod=='bb_associatedProduction' or reg =='boosted':
                    Totflav_cards_allparams[(output_dir, cat[1])]['OSSF'].append("ch2_{}_{}_{}_{}_OSSF=".format(mode, sig_process, reco, reg) + 
                            "{prefix}_{prod}_{reco}_{reg}_{flavor}_{category}.dat".format(prefix=output_prefix, prod=prod, reco=reco, reg=reg, flavor="OSSF", category=cat[1]))
                
                for mergeable_flavors in list_mergeable_flavors:
                    if all(x in flavors for x in mergeable_flavors):
                        
                        if 'MuEl' in mergeable_flavors: k = 'OSOF'
                        else: k = 'OSSF'

                        print("Merging {} datacards into a single one for {}".format(mergeable_flavors, cat[1]))
                        args = ["ch{i}_{mode}_{sig}_{reco}_{reg}_{flavor}={prefix}_{prod}_{reco}_{reg}_{flavor}_{category}.dat".format(
                                 i=i+1, mode=mode, sig=sig_process, reco=reco, reg=reg, flavor=x, prefix=output_prefix, prod=prod, category=cat[1]) for i, x in enumerate(mergeable_flavors)]
                        cmd  = ['combineCards.py'] + args
                        
                        merged_flav_datacard = output_prefix + '_'+ prod +'_' + reco+ '_' + reg + '_'+ '_'.join(mergeable_flavors) + '_' + cat[1]
                        
                        if not mergeable_flavors in [['MuMu', 'MuEl'], ['ElEl', 'MuEl']]:
                            Totflav_cards_allparams[(output_dir, cat[1])][k] += args 
                        
                        with open( os.path.join(output_dir, merged_flav_datacard + '.dat'), 'w') as f:
                            subprocess.check_call(cmd, cwd=output_dir, stdout=f)
                        
                        createRunCombineScript(cat[1], mass, output_dir, merged_flav_datacard, prod +'_' + reco+ '_' + reg + '_'+ '_'.join(mergeable_flavors))

    return Totflav_cards_allparams



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Create shape datacards ready for combine')
    
    parser.add_argument('-i', '--input',        action='store', dest='input', type=str, required=True, default=None, 
                                                help='HistFactory input path: those are the histograms for signal/data/backgrounds that pass through all the following\n'
                                                     'steps: 1/- final selection ( 2l+bjets pass btagging discr cut + met + corrections + etc... )\n'
                                                     '       2/- do skim\n'
                                                     '       3/- DNN trained using these skimmed trees\n'
                                                     '       4/- run bamboo to produce your dnn outputs(prefit plots) with all systematics variations using the model you get from training.\n')
    parser.add_argument('-o', '--output',       action='store', dest='output', required=True, default=None,        
                                                help='Output directory')
    parser.add_argument('-s', '--stat',         action='store_true', dest='stat_only', required=False, default=False,                                                           
                                                help='Do not consider systematic uncertainties')
    parser.add_argument('-v', '--verbose',      action='store_true', required=False, default=False, 
                                                help='For debugging purposes , you may consider this argument !')
    parser.add_argument('--era',                action='store', dest='era', required=True, default=None, choices=['2016', '2017', '2018', 'fullrun2'],
                                                help='You need to pass your era')
    parser.add_argument('--expectSignal',       action='store', required=False, type=int, default=1, choices=[0, 1],
                                                help=' Is this S+B or B-Only fit? ')
    parser.add_argument('--mode',               action='store', dest='mode', default='dnn', choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'mbb', 'mllbb', 'ellipse', 'dnn'],
                                                help='Analysis mode')
    parser.add_argument('--node',               action='store', dest='node', default='ZA', choices=['DY', 'TT', 'ZA'],
                                                help='DNN nodes')
    parser.add_argument('--method',             action='store', dest='method', required=True, default=None, 
                                                choices=['asymptotic', 'hybridnew', 'fit', 'impacts', 'generatetoys', 'signal_strength', 'pvalue', 'goodness_of_fit'],        
                                                help='Analysis method')
    parser.add_argument('--unblind',            action='store_true', dest='unblind', required=False,
                                                help='Unblind analysis :: use real data instead of fake pseudo-data')
    parser.add_argument('--signal-strength',    action='store_true', dest="signal_strength", required=False, default=False,                                                  
                                                help='Put limit on the signal strength instead of the cross-section')
    parser.add_argument('--ellipses-mumu-file', action='store', dest='ellipses_mumu_file', required=False, default='./data/fullEllipseParamWindow_MuMu.json',
                                                help='file containing the ellipses parameters for MuMu (ElEl is assumed to be in the same directory)')
    parser.add_argument('--scale',              action='store_true', dest='scale', required=False, default=False,                                                  
                                                help='scale signal rate')
    parser.add_argument('--slurm',              action='store_true', dest='submit_to_slurm', required=False, default=False,                                                  
                                                help='slurm submission for long pull and impacts jobs')
    parser.add_argument('--normalize',          action='store_true', dest='normalize', required=False, default=False,                                                  
                                                help='normalize the inputs histograms : lumi * xsc * (BR if signal) / sum_genEvts')
     
    parser.add_argument('--dataset',            action='store', dest='dataset', choices=['toys', 'asimov'], required='--unblind' not in sys.argv, default=None,                             
                                                help='if asimov:\n'
                                                        '-t -1 will produce an Asimov dataset in which statistical fluctuations are suppressed. \n'
                                                     'if toys: \n'
                                                        '-t N with N > 0. Combine will generate N toy datasets from the model and re-run the method once per toy. \n'
                                                        'The seed for the toy generation can be modified with the option -s (use -s -1 for a random seed). \n'
                                                        'The output file will contain one entry in the tree for each of these toys.\n')
    options = parser.parse_args()
    
    if not os.path.isdir(options.output):
        os.makedirs(options.output)
    
    for thdm in ['HToZA']:#, 'AToZH']:
        
        if options.era == "fullrun2" and options.method != "generatetoys":
            to_combine = defaultdict()
            outDir = os.path.join(options.output, H.get_method_group(options.method), options.mode)
            
            for prod in ['gg_fusion', 'bb_associatedProduction']:
                for reg in ['resolved', 'boosted']:
                    
                    if prod =='bb_associatedProduction' or reg =='boosted':
                        flavors = [['OSSF', 'MuEl'], ['OSSF'], ['MuEl']]
                    else:
                        flavors = [['MuMu', 'ElEl', 'MuEl'], ['MuMu', 'ElEl'], ['MuMu'], ['ElEl'], ['MuEl']]
                    
                    for flav in flavors:
                        cat = '{}_{}_{}_{}'.format(prod, reg, '_'.join(flav), options.mode)
                        to_combine[cat] = {}
                        for j, year in enumerate([16, 17, 18]):
                            
                            mPath = os.path.join(outDir.replace('work__ULfullrun2', 'work__UL{}'.format(year)))
                            for p in glob.glob(os.path.join(mPath, 'M*')):
                                
                                masses = p.split('/')[-1]
                                cardNm = '{}To2L2B_{}_{}_{}_{}_{}.dat'.format(thdm, prod, reg, '_'.join(flav), options.mode, masses.replace('-','_'))
                                shNm   = '{}To2L2B_{}_{}_{}_{}_{}_run_{}.sh'.format(thdm, prod, reg, '_'.join(flav), options.mode, masses.replace('-','_'), options.method)
                                
                                pOut = p.replace('work__UL{}'.format(year), 'work__ULfullrun2')
                                if not os.path.isdir(pOut):
                                    os.makedirs(pOut)
                                
                                if not os.path.exists(os.path.join(p, shNm)):
                                    continue

                                if j ==0:
                                    shutil.copy(os.path.join(p, shNm), pOut)
                                    Constants.overwrite_path(os.path.join(pOut, shNm))
                                
                                if not masses in to_combine[cat].keys():
                                    to_combine[cat][masses]= ['combineCards.py']
                                to_combine[cat][masses].append('UL{}={}'.format(year, os.path.join(p, cardNm)))

            for cat, Cmd_per_mass in to_combine.items():        
                for m, cmd in to_combine[cat].items():
                    
                    if len(cmd) !=4: 
                        logger.info("The 3-eras cards are needed, will sum what we got!")
                        logger.info("running :: ' {} ' for {}\\".format(" ".join(cmd), m))
                    
                    CardOut = '{}/{}/{}'.format(outDir, m, cmd[1].split('/')[-1])
                    try:
                        with open(CardOut, "w+") as outfile:
                            subprocess.call(cmd, stdout=outfile)
                    except subprocess.CalledProcessError:
                        logger.error("Failed to run {0}".format(" ".join(cmd)))
            
            CreateScriptToRunCombine(options.output, options.method, options.mode, options.era)

        else:
            scalefactors  = H.get_normalisationScale(options.input, options.method, options.era)
            # for test or for specific points : please use signal_grid_foTest,
            # otherwise the full list of samples will be used !
            signal_grid = Constants.get_SignalMassPoints(options.era, returnKeyMode= False, split_sig_reso_boo= False) 
            
            prepare_DataCards(  grid_data          = signal_grid_foTest, 
                                thdm               = thdm,
                                dataset            = options.dataset, 
                                expectSignal       = options.expectSignal, 
                                era                = options.era, 
                                mode               = options.mode.lower(), 
                                input              = options.input, 
                                ellipses_mumu_file = options.ellipses_mumu_file, 
                                output             = options.output, 
                                method             = options.method, 
                                node               = options.node, 
                                scalefactors       = scalefactors,
                                unblind            = options.unblind, 
                                signal_strength    = options.signal_strength, 
                                stat_only          = options.stat_only, 
                                verbose            = options.verbose, 
                                merge_cards        = True, 
                                merge_ggH_bbH      = False, 
                                scale              = options.scale, 
                                normalize          = options.normalize, 
                                submit_to_slurm    = options.submit_to_slurm)
