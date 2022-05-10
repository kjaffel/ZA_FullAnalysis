#!/usr/bin/env python
# -*- coding: utf-8 -*
import os, os.path, sys
import yaml
import random
import argparse, optparse
import numpy as np
import pandas as pd
import re
from collections import defaultdict
from faker import Factory
fake = Factory.create()

# TODO 
# 2- finish xsc uncer checks for mc and signal !! 

def get_era_and_luminosity(smp=None, run=None, isdata=False):
    preVFPruns  = ["B", "C", "D", "E"]
    postVFPruns = ["G", "H"]
    
    if isdata:
        prefix = '-preVFP' if any(x in run for x in preVFPruns) else('-postVFP')
        
        if run =="F":
            prefix = '-preVFP' if "HIPM" in smp else '-postVFP'

        lumi   = 19667.812849099 if prefix=='-preVFP' else( 16977.701784453)
        
        if 'UL2016'in smp: return f'2016{prefix}', lumi, 0.012
        elif 'UL2017'in smp: return '2017', 41529.152060112, 0.023
        elif 'UL2018'in smp: return '2018', 59740.565201546, 0.025
    
    else:
        if 'RunIISummer20UL16NanoAODAPV' in smp or 'RunIISummer19UL16NanoAODAPV' in smp: return '2016-preVFP', 19667.812849099, 0.012
        elif 'RunIISummer20UL16NanoAOD' in smp or 'RunIISummer19UL16NanoAOD' in smp: return '2016-postVFP', 16977.701784453, 0.012
        elif 'RunIISummer20UL17' in smp or 'RunIISummer19UL17' in smp: return '2017', 41529.152060112, 0.023
        elif 'RunIISummer20UL18' in smp or 'RunIISummer19UL18' in smp: return '2018', 59740.565201546, 0.025

def mass_to_str(m):
    return str(m).replace('.','p')
    
def get_list_ofsystematics(eras):
    sys =[
        '# total on the jets energy resolution',
        'jer',
        '  # affect shape variations',
        '  # splited  between (kinematic) regions',
        'jer0',
        'jer1',
        'jer2',
        'jer3',
        'jer4',
        'jer5',
        'jmr',
        'jms',
        'unclustEn',
        '# on the jets energy scale ',
        'jesTotal']
    for era in eras.keys():
        era = era.split('-')[0]
        
        if era == '2017':
            sys += [
                '# on pu HLTZvtx',
                    f'HLTZvtx'
            ]
        if not f'jesAbsolute_{era}' in sys:
            sys += [
                f'   #{era}',
                f'pileup_{era}',
            '  # splited by source, uncorrelated per year',
                f'jesAbsolute_{era}',
                f'jesBBEC1_{era}',
                f'jesEC2_{era}',
                f'jesHF_{era}',
                f'jesRelativeSample_{era}',
            ]
            if era != '2018':
                sys += [
                '# L1 pre-firing event correction weight',
                f'L1PreFiring_{era}',
            ]

    sys += [
        '# leptons ID, ISO and RCO SFs ',
        'muid_medium',
        'muiso_tight',
        'elid_medium',
        'lowpt_ele_reco',
        'highpt_ele_reco',
        '# on the trigger',
        'elel_trigSF',
        'muel_trigSF',
        'mumu_trigSF',
        '# sys from theory  ',
        'qcdScale',
        'qcdMuF',
        'qcdMuR',
        'psISR',
        'psFSR',
        'pdf',
        '# on the btagged jets ',
        'btagSF_fixWP_subjetdeepcsvM_light',
        'btagSF_fixWP_subjetdeepcsvM_heavy',
        'btagSF_fixWP_deepcsvM_light',
        'btagSF_fixWP_deepcsvM_heavy',
        'btagSF_fixWP_deepflavourM_light',
        'btagSF_fixWP_deepflavourM_heavy',
        ]
    return sys

def get_mcNmConvention_and_group(smpNm):
    """
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/SummaryTable1G25ns
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/HowToGenXSecAnalyzer
    """
    shortnames = {'DYJetsToLL_M-10to50': ['DY', 18610.0,    0., 'Drell-Yan', '#0000FF',    8],
                  'DYJetsToLL_0J'      : ['DY', 4757.0,     0., 'Drell-Yan', '#0000FF',    8],
                  'DYJetsToLL_1J'      : ['DY', 859.589402, 0., 'Drell-Yan', '#0000FF',    8],
                  'DYJetsToLL_2J'      : ['DY', 361.4,      0., 'Drell-Yan', '#0000FF',    8],
                  'TTHadronic'             : ['ttbar_FullHadronic', 377.96, 0., 'tt Full Had.',  '#00ffc7',  4],
                  'TTToSemiLeptonic'       : ['ttbar_SemiLeptonic', 365.35, 0., 'tt Semi Lept.', '#9370DB',  5],
                  'TTTo2L2Nu'              : ['ttbar_FullLeptonic', 88.288, 0., 'tt Full Lept.', '#c4ffff',  7],
                  'ST_tW_top_5f'           : ['ST', 34.91,  0.02817, 'Single Top',    '#ffc800',  6],
                  'ST_tW_antitop_5f'       : ['ST', 34.97,  0.02827, 'Single Top',    '#ffc800',  6],
                  'ST_t-channel_top_4f'    : ['ST', 136.02, 0., 'Single Top',    '#ffc800',  6],
                  'ST_t-channel_antitop_4f': ['ST', 80.95,  0., 'Single Top',    '#ffc800',  6],
                  'ST_s-channel_4f'        : ['ST', 3.36,   0., 'Single Top',    '#ffc800',  6],
                  'ZZTo2L2Nu'   : ['ZZ', 0.5644, 0.0002688, 'ZZ',   '#ff4800',  3],
                  'ZZTo2L2Q'    : ['ZZ', 3.222, 0.004901,   'ZZ',   '#ff4800',  3],
                  'ZZTo4L'      : ['ZZ', 1.256, 0.002271,   'ZZ',   '#ff4800',  3],
                  'HZJ_HToWW_M125'          : ['SM', 0.7524,  0.003643, 'tth, Zh',  '#ff0038',  2],
                  'ZH_HToBB_ZToLL_M125'     : ['SM', 0.5269,  0.003834, 'tth, Zh',  '#ff0038',  2],
                  'ggZH_HToBB_ZToLL_M125'   : ['SM', 0.5638,  0.02855,  'tth, Zh',  '#ff0038',  2],
                  'ggZH_HToBB_ZToNuNu_M125' : ['SM', 0.01373, 0.,       'tth, Zh',  '#ff0038',  2],
                  'ttHTobb'                 : ['SM', 0.5638,  0.,       'tth, Zh',  '#ff0038',  2],
                  'ttHToNonbb'              : ['SM', 0.5638,  0.,       'tth, Zh',  '#ff0038',  2],
                  'WWToLNuQQ'       : ['others', 43.53,     0.,     'others',   '#ff8d58',  1],
                  'WWTo2L2Nu'       : ['others', 10.48,     0.,     'others',   '#ff8d58',  1],
                  'WZTo2L2Q'        : ['others', 5.606,     0.,     'others',   '#ff8d58',  1],
                  'WZTo1L3Nu'       : ['others', 3.054,     0.,     'others',   '#ff8d58',  1],
                  'WZTo1L1Nu2Q'     : ['others', 10.73,     0.,     'others',   '#ff8d58',  1],
                  'WZTo3LNu'        : ['others', 4.43,      0.,     'others',   '#ff8d58',  1],
                  'WWW_4F'          : ['others', 0.2086,    0.,     'others',   '#ff8d58',  1],
                  'WWZ_4F'          : ['others', 0.1651,    0.,     'others',   '#ff8d58',  1],
                  'WZZ'             : ['others', 0.05565,   0.,     'others',   '#ff8d58',  1],
                  'ZZZ'             : ['others', 0.01398,   0.,     'others',   '#ff8d58',  1],
                  'WJetsToLNu'      : ['others', 60430.0,   0.,     'others',   '#ff8d58',  1],
                  'TTWJetsToQQ'     : ['others', 0.405,     0.,     'others',   '#ff8d58',  1],
                  'TTWJetsToLNu'    : ['others', 0.2001,    0.,     'others',   '#ff8d58',  1],
                  'TTZToQQ'         : ['others', 0.5297,    0.,     'others',   '#ff8d58',  1],
                  'TTZToLLNuNu_M-10': ['others', 0.2529,    0.,     'others',   '#ff8d58',  1],
                  'HZJ_HToWW_M-125' : ['others', 0.04062,   0.,     'others',   '#ff8d58',  1],
                  'ggZH_HToBB_ZToLL_M-125'  : ['others', 0.00695,   0.,     'others',   '#ff8d58',  1],
                  'ggZH_HToBB_ZToNuNu_M-125': ['others', 0.00695,   0.,     'others',   '#ff8d58',  1],
                  }
    for Nm, val in shortnames.items():
        if smpNm.startswith(Nm):
            return Nm , val[0], val[1], val[2], val[3], val[4], val[5] # name, xsc, uncer, legend, fill_color, order_of_group_in_plotit

def get_das_path(inf, smp, search, era, run, isdata=False, isMC=False, issignal=False):
    das_tomerge  = []
    das_toignore = []
    
    if not isdata:
        if era == '2016': lookfor = 'asymptotic_'
        else: lookfor = 'realistic_'
        
        version = smp.split('/')[-2].split(lookfor)[1]
        if '_ext' in version: s = version.split('_ext')[0]+'-v'
        else: s = version.split('-')[0]+'_ext'
    
    #https://newbedev.com/python-regular-express-cheat-sheet
    with open(inf, 'r') as file:
        for line in file:
            path   = line.split()[0]
            if isdata:
                regex = re.compile(f"/{search}/Run{era}{run}-ver*", re.IGNORECASE)
            else:
                regex = re.compile(f"/{search}/{smp.split('/')[-2].split(lookfor)[0]+lookfor+ s}*", re.IGNORECASE)
            m = regex.search(path)
            if m:
                # this is an extension add to merge 
                das_tomerge.append('das:{}'.format(path))
                das_tomerge.append('das:{}'.format(smp))
                das_toignore.append(path)
    das_tomerge = pd.unique(das_tomerge).tolist()

    # these versions of das path need to stay sperate as they have different run range 
    if era == '2016-preVFP' and 'B' in run:
        return 'das:{}'.format(smp), [] 
    if das_tomerge:
        return das_tomerge, das_toignore
    else:
        return 'das:{}'.format(smp), []

def get_legend(process, comp, H, l, m_heavy, m_light, smpNm):
    return  f"{process}, (M{H}, M{l}) = (%d, %d) GeV"%(float(m_heavy),float(m_light))

def get_xsc_br_fromSushi(smpNm, arr):
    for lis in arr:
        if not smpNm == lis[0]: continue
        if 'To2L2B' in smpNm: 
            l = 'A' if 'HToZA' in smpNm else 'H'
            H = 'H' if 'HToZA' in smpNm else 'A'
            mHeavy  = lis[1]
            mlight  = lis[2]
            tb      = lis[3]
            xsc     = lis[4]
            xsc_err = lis[5]
            br_HeavytoZlight  = lis[6]
            br_lighttobb      = lis[7]
            return H, l, mHeavy, mlight, tb, xsc, xsc_err, float(br_HeavytoZlight), float(br_lighttobb)

def lumi_block(inf):
    with open(options.das, 'r') as inf:
        eras = defaultdict()
        for smp in inf:
            smp = smp.split()[0]
            run = smp.split('/')[2].split('-')[0][-1]
            smpNm = smp.split('/')[1]
            isdata = True if smpNm in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon', 'SingleElectron'] else(False)
            era, lumi, uncer = get_era_and_luminosity(smp, run, isdata)
            if era not in eras.keys(): 
                eras[era] = {}
                eras[era]['lumi'] = lumi
                eras[era]['uncer'] = uncer
    return eras

def get_label(eras):
    # I am not gonna do more then this split : 2016 pre/-postVFP, 2017, 2018 
    #                                        or all combined : run2
    if len(eras.keys())==2 and ('2016-' in x for x in eras.keys() ):
        suffix = 'pre-/postVFP 2016'
    else:
        if len(eras.keys()) == 1 :
            suffix = era
        elif len(eras.keys()) == 4 :
            suffix = 'run2'
        else:
            suffix = ''
            for k in eras.keys():
                suffix  += f' {k},' 
    plot_label = f'{suffix} ULegacy'
    return plot_label 

def loadSushiInfos(len_, H, l, fileName):
    in_dtypes = [
            ("DatasetName",  f'U{len_}'),
            ("Sushi_xsc@NLO[pb]", float),
            ("Sushi_xsc_err[pb]", float),
            (f"BR({H} -> Z{l} )", float),
            (f"BR({l}  -> bb)", float),
            ("Ymb,H[GeV]", float),
            ("Ymb,A[GeV]", float),
            ("Partialwidth(H ->bb)[GeV]", float),
            ("Partial_width(A ->bb)[GeV]", float),
            ("Totalwidth,H[GeV]", float),
            ("Totalwidth,A[GeV]", float),
            ("WHMHPercent", float),
            ("WAMAPercent", float)
            ]
    with open(fileName) as inF:
        arr = np.genfromtxt(inF, skip_header=1, dtype=in_dtypes)
    #print( arr.dtype.type )#names) 
    pars = np.array([ [ float(tk.replace("p", ".").split('-')[-1]) for tk in dsNm.split("_")[1:4] ] for dsNm in arr["DatasetName"] ])
    return np.hstack((
        arr["DatasetName"][:,None],
        pars[:,:3], ## mH,mA,tb 
        arr["Sushi_xscNLOpb"][:,None],
        arr["Sushi_xsc_errpb"][:,None],
        arr[f"BR{H}__Z{l}_"][:,None],
        arr[f"BR{l}___bb"][:,None]
        ))

if __name__ == "__main__":
    
    base = "/home/ucl/cp3/kjaffel/ZAPrivateProduction/data/"
    
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--das', required=True, action='store', help=' a Text files of dataset path')
    parser.add_argument('-o', '--output', required=True, action='store', help='Name of the output .yml file')
    options = parser.parse_args()
    
    certification = {'2016':'https://cms-service-dqmdc.web.cern.ch//CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt', 
                     '2017':'https://cms-service-dqmdc.web.cern.ch//CAF/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt',
                     '2018':'https://cms-service-dqmdc.web.cern.ch//CAF/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt', }
    
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVDataReprocessingUL2018#Datasets_for_Eras_2018A_B_C_D
    run2_ranges = {
                '2016-preVFP':
                    {'B_ver1':[272760, 273017],
                     'B_ver2':[273150, 275376],
                     'C':[275656, 276283],
                     'D':[276315, 276811],
                     'E':[276831, 277420],
                     'F':[277932, 278807],
                     },
                '2016-postVFP':
                    {'F':[278769, 278808],
                     'G':[278820, 280385],
                     'H':[281613, 284044] },
                '2017':
                    {'B':[297047, 299329],
                     'C':[299368, 302029],
                     'D':[302030, 302663],
                     'E':[303824, 304797],
                     'F':[305040, 306460],
                     },
                '2018':
                    {'A':[315257, 316995],
                     'B':[317080, 319310],
                     'C':[319337, 320065],
                     'D':[320500, 325175] }}
    
    eras = lumi_block(options.das)
    print( eras)
    with open(options.das, 'r') as inf:
        with open(options.output, 'w+') as outf:
            
            groups = defaultdict()
            merged_daspath = []
            
            # =======================================================
            outf.write(f"tree: Events\n")
            outf.write(f"eras:\n")
            for era , opt in eras.items() : 
                outf.write(f"   '{era}':\n")
                outf.write(f"     luminosity: {opt['lumi']} #pb \n")
                outf.write(f"     luminosity-error: {opt['uncer']}\n")
            outf.write("\n")
            outf.write("samples:\n")
            # =======================================================
            run = None
            for i, smp in enumerate(inf):
                isMC     = False
                isdata   = False
                issignal = False
                smp   = smp.split()[0]
                smpNm = smp.split('/')[1]
               
                print( 'working on :', smp )
                if "HToZATo2L2B" in smp or "AToZHTo2L2B" in smp : 
                    issignal = True
                    mode     = 'AToZH' if 'AToZH' in smpNm else 'HToZA'
                    comp     = 'nlo' if 'amcatnlo' in smp else 'lo'
                    process  = 'ggH' if smpNm.startswith('GluGluTo') else('bbH')
                elif smpNm in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon', 'SingleElectron']: 
                    isdata   = True
                else: 
                    isMC     = True
                
                color  = fake.hex_color()
                #color = '#%06x' % random.randint(0, 0xFFFFFF)
                
                if isdata:
                    run = smp.split('/')[2].split('-')[0][-1]
                era, lumi, uncer = get_era_and_luminosity(smp, run, isdata)
                if era == '2016-preVFP' and run =='B':
                    run = 'B_ver1' if '2016B-ver1' in smp else 'B_ver2'
                year = era.replace('20', '')
                if  'VFP' in era :
                    era_ = era.split('-')[0]
                    VFP  = f"_UL16{era.split('-')[1]}"
                else:
                    era_ = era
                    VFP = f"_UL{year}"

                if issignal:
                    br_Ztoll = 0.067264
                    
                    if mode == "HToZA":
                        benchmarks = loadSushiInfos(len(smpNm),'H', 'A', f"{base}/list_benchmarks_{process}_{comp}_{mode}_datasetnames.txt")
                        fullsim    = loadSushiInfos(len(smpNm),'H', 'A', f"{base}/list_fullsim_{process}_{comp}_{mode}_datasetnames.txt")
                        all_       = loadSushiInfos(len(smpNm),'H', 'A', f"{base}/list_all_{process}_lo_{mode}_datasetnames.txt")
                        
                        arrs = np.concatenate((benchmarks, fullsim, all_))
                    
                    elif mode == "AToZH":
                        arrs = loadSushiInfos(len(smpNm),'A', 'H', f"{base}/list_benchmarks_{process}_{comp}_{mode}_datasetnames.txt")
                        
                    H, l, mHeavy, mlight, tb, xsc, xsc_err, br_HeavytoZlight, br_lighttobb = get_xsc_br_fromSushi(smpNm, arrs)
                    Nm      = smpNm.replace('-','_')+VFP
                    br      = br_HeavytoZlight * br_lighttobb * br_Ztoll
                    leg     = get_legend(process, comp, H, l, mHeavy, mlight, smpNm)
                    search  = smpNm
                    details = f'{H} -> Z{l} ({br_HeavytoZlight}) * {l} -> bb ({br_lighttobb}) * Z -> ee+ mumu ({br_Ztoll})'
                elif isdata:
                    Nm = f'{smpNm}_UL{era_}{run}{VFP}'
                    run_range = run2_ranges[era][run]
                    cert = certification[era.split('-')[0]] # FIXME make sure that this assumption is correct : means the certefication is the same for pre/post VFP
                    split  = 4
                    search = smpNm
                elif isMC:
                    Nm, group, xsc, uncer, legend, fill_color, order = get_mcNmConvention_and_group(smpNm)
                    Nm = Nm + VFP
                    split = 150
                    search = smpNm
                    if group not in groups.keys(): 
                        groups[group] = {}
                        groups[group]['legend'] = legend
                        groups[group]['fill_color'] = fill_color
                        groups[group]['order'] = order
                
                if str(smp) in merged_daspath:
                    continue
                das__path, to_ignore = get_das_path(options.das, smp, search, era_, run, isdata, isMC, issignal)
                merged_daspath.extend( to_ignore)
                
                outf.write(f"  {Nm}:\n")
                outf.write(f'    db: {das__path}\n'.replace("'" , ""))
                outf.write(f"    files: dascache/nanov9/{era}/{Nm}.dat\n")
                if not issignal:
                    outf.write(f"    split: {split}\n")
                outf.write(f"    era: '{era}'\n")
                if isMC :
                    outf.write(f"    group: {group}\n")
                    outf.write("    generated-events: 'genEventSumw'\n")
                    outf.write(f"    cross-section: {xsc} # +- {uncer} pb\n")
                elif isdata :
                    outf.write("    group: data\n")
                    outf.write(f"    run_range: {run_range}\n")
                    outf.write(f"    certified_lumi_file: {cert}\n")
                elif issignal :
                    outf.write("    type: signal\n")
                    outf.write("    generated-events: 'genEventSumw'\n")
                    outf.write(f"    cross-section: {xsc}   # +- {xsc_err} pb\n")
                    outf.write(f"    Branching-ratio: {br}  # {details}\n")
                    outf.write(f"    line-color: '{color}'\n")
                    outf.write("    line-type: 1\n")
                    outf.write(f"    legend: {leg}\n")
                outf.write("\n")
            outf.write("\n")
            outf.write("plotIt:\n")
            outf.write("  configuration:\n")
            outf.write("    width: 800\n")
            outf.write("    height: 600\n")
            outf.write("    luminosity-label: '%1$.2f fb^{-1} (13 TeV)' \n")
            outf.write("    experiment: CMS\n")
            outf.write(f"    extra-label: {get_label(eras)} --Work in progress\n")
            outf.write("    show-overflow: true\n")
            outf.write("    blinded-range-fill-style: 4050\n")
            outf.write("    blinded-range-fill-color: '#FDFBFB'\n")
            outf.write("    #error-fill-style: 3154\n")
            outf.write("    #error-fill-color: '#ee556270'\n")
            outf.write("    #ratio-fit-error-fill-style: 1001\n")
            outf.write("    #ratio-fit-error-fill-color: '#aa556270'\n")
            outf.write("    #ratio-fit-line-color: '#0B486B'\n")
            outf.write("    y-axis-format: '%1% / %2$.2f'\n")
            outf.write("  legend:\n")
            outf.write("    position: [0.6, 0.7, 0.9, 0.9]\n")
            outf.write("    #columns: 2\n")
            outf.write("  groups:\n")
            outf.write("    data:\n")
            outf.write("      legend: data\n")
            outf.write("    signal:\n")
            outf.write("      legend: Signal\n")
            for gp, opt in groups.items():
                outf.write(f"    {gp}:\n")
                outf.write(f"      fill-color: '{opt['fill_color']}'\n")
                outf.write(f"      legend: {opt['legend']}\n")
                outf.write(f"      order: {opt['order']}\n")
            outf.write("  plotdefaults:\n")
            outf.write("      y-axis: Events\n")
            outf.write("      log-y: both\n")
            outf.write("      y-axis-show-zero: True\n")
            outf.write("      save-extensions: [pdf]\n")
            outf.write("      show-ratio: True\n")
            outf.write("      ratio-y-axis-range: [0.6,1.4]\n")
            outf.write("      sort-by-yields: False \n")
            outf.write("  systematics:\n")
            for sys in get_list_ofsystematics(eras):
                line = '    - '+sys+'\n'
                sys_line = line.replace('-','') if '#' in line else(line)
                outf.write(sys_line)
            outf.write("    # on the cross section : 1+xsec_uncer(pb)/xsec(pb)\n")
    print( ' \tfile successfully written and saved in :', options.output)
