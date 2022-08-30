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
        
        if   'UL2016'in smp: return f'2016{prefix}', lumi, 0.01
        elif 'UL2017'in smp: return '2017', 41529.152060112, 0.02
        elif 'UL2018'in smp: return '2018', 59740.565201546, 0.015
    else:
        if   'RunIISummer20UL16NanoAODAPV' in smp or 'RunIISummer19UL16NanoAODAPV' in smp: return '2016-preVFP', 19667.812849099, 0.01
        elif 'RunIISummer20UL16NanoAOD' in smp or 'RunIISummer19UL16NanoAOD' in smp: return '2016-postVFP', 16977.701784453, 0.01
        elif 'RunIISummer20UL17' in smp or 'RunIISummer19UL17' in smp: return '2017', 41529.152060112, 0.02
        elif 'RunIISummer20UL18' in smp or 'RunIISummer19UL18' in smp: return '2018', 59740.565201546, 0.015

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
        '# on fat jets',
        'jmr',
        'jms',
        '# on missing energy',
        'unclustEn',
        '# on the jets energy scale ',
        'jesTotal']
    for era in eras.keys():
        era = era.split('-')[0]
        
        n = '7' if era == '2017' else '6'
        sys  += [ 
                '# on DY+jets @nlo',
                f'DYweight_resolved_elel_ployfit_lowmass{n}_highmass5',
                #"   type: shape",
                #"   on: 'DY'",
                f'DYweight_boosted_mumu_ployfit_lowmass{n}',
                #"   type: shape",
                #"   on: 'DY'",
            ]
        if era == '2017':
            sys += [
                '# on HLTZvtx',
                f'HLTZvtx',
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
        '# from btag eff meas '
        'bEff',
        'cEff',
        'lightEff',
        ]
    return sys

def get_mcNmConvention_and_group(smpNm):
    """
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/SummaryTable1G25ns
    https://twiki.cern.ch/twiki/bin/viewauth/CMS/HowToGenXSecAnalyzer
    """
    shortnames = {'DYJetsToLL_M-10to50': ['DY', 18610.0,    None, 'DY+jets', '#0000FF',    6],
                  'DYJetsToLL_0J'      : ['DY', 4757.0,     9.294, 'DY+jets', '#0000FF',    6],
                  'DYJetsToLL_1J'      : ['DY', 859.589402, 6.067, 'DY+jets', '#0000FF',    6],
                  'DYJetsToLL_2J'      : ['DY', 361.4,      3.704, 'DY+jets', '#0000FF',    6],
                  'TTToHadronic'           : ['ttbar', 377.96, 0.5174,             'tt',     '#c4ffff',  5],
                  'TTToSemiLeptonic'       : ['ttbar', 365.35,  '+4.8% -6.1%',      'tt',    '#c4ffff',  5],
                  'TTTo2L2Nu'              : ['ttbar', 88.288,  '+4.8% -6.1%',      'tt',    '#c4ffff',  5],
                  'ST_tW_top_5f'           : ['ST', 35.85,  '+0.90 -0.90 +1.70 -1.70',  'ST',    '#ffc800',  4],
                  'ST_tW_antitop_5f'       : ['ST', 35.85,  '+0.90 -0.90 +1.70 -1.70',  'ST',    '#ffc800',  4],
                  'ST_t-channel_top_4f'    : ['ST', 136.02, None,                       'ST',    '#ffc800',  4],
                  'ST_t-channel_antitop_4f': ['ST', 80.95,  None,                       'ST',    '#ffc800',  4],
                  'ST_s-channel_4f'        : ['ST', 3.36,   +0.13 -0.12 ,               'ST',    '#ffc800',  4],
                  'ZZTo2L2Nu'       : ['VV', 0.5644, 0.0002688,         'VV',   '#ff8d58',  3],
                  'ZZTo2L2Q'        : ['VV', 3.222, 0.004901,           'VV',   '#ff8d58',  3],
                  'ZZTo4L'          : ['VV', 1.256, 0.002271,           'VV',   '#ff8d58',  3],
                  'WWToLNuQQ'       : ['VV', 43.53,     0.,             'VV',   '#ff8d58',  3],
                  'WWTo2L2Nu'       : ['VV', 10.48,     0.,             'VV',   '#ff8d58',  3],
                  'WZTo2L2Q'        : ['VV', 5.595,     0.,             'VV',   '#ff8d58',  3],
                  'WZTo1L3Nu'       : ['VV', 3.033,     2.060e-02,      'VV',   '#ff8d58',  3],
                  'WZTo1L1Nu2Q'     : ['VV', 10.71,     0.,             'VV',   '#ff8d58',  3],
                  'WZTo3LNu'        : ['VV', 4.42965,   0.,             'VV',   '#ff8d58',  3],
                  'HZJ_HToWW_M-125'          : ['SM', 0.0406,    0.,        'ggh, tth, Zh',  '#43294D',  2],
                  'ZH_HToBB_ZToLL_M-125'     : ['SM', 0.07814,   0.0001904, 'ggh, tth, Zh',  '#43294D',  2],
                  'ggZH_HToBB_ZToLL_M-125'   : ['SM', 6.954e-03, 7.737e-06, 'ggh, tth, Zh',  '#43294D',  2],
                  'ggZH_HToBB_ZToNuNu_M-125' : ['SM', 6.954e-03, 7.737e-06, 'ggh, tth, Zh',  '#43294D',  2],
                  'GluGluHToZZTo2L2Q_M125'   : ['SM', 28.87,       0.02027, 'ggh, tth, Zh',  '#43294D',  2],
                  'ttHTobb'                  : ['SM', 0.2934,  0.,          'ggh, tth, Zh',  '#43294D',  2],
                  'ttHToNonbb'               : ['SM', 0.2151,  0.,          'ggh, tth, Zh',  '#43294D',  2],
                  'WWW_4F'          : ['others', 0.2086,    0.,         'VVV, ttV',   '#9370DB',  1],
                  'WWZ_4F'          : ['others', 0.1651,    0.,         'VVV, ttV',   '#9370DB',  1],
                  'WZZ'             : ['others', 0.05565,   0.,         'VVV, ttV',   '#9370DB',  1],
                  'ZZZ'             : ['others', 0.01398,   0.,         'VVV, ttV',   '#9370DB',  1],
                  'WJetsToLNu'      : ['others', 61526.7,   0.,         'VVV, ttV',   '#9370DB',  1],
                  'TTWJetsToQQ'     : ['others', 0.4062,    0.0021,     'VVV, ttV',   '#9370DB',  1],
                  'TTWJetsToLNu'    : ['others', 0.2043,    0.0020,     'VVV, ttV',   '#9370DB',  1],
                  'TTZToQQ'         : ['others', 0.5297,    0.0008,     'VVV, ttV',   '#9370DB',  1],
                  'TTZToLLNuNu_M-10': ['others', 0.2529,    0.0004,     'VVV, ttV',   '#9370DB',  1],
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

def get_legend(process, comp, heavy, light, m_heavy, m_light, smpNm):
    m_heavy    = ('%.2f'%float(m_heavy)).replace('.00', '')
    m_light    = ('%.2f'%float(m_light)).replace('.00', '')
    if heavy == 'H':
        return  "#splitline{%s: (m_{H}, m_{A})}{= (%s, %s) GeV}"%(process, m_heavy, m_light)
    else:
        return  "#splitline{%s: (m_{A}, m_{H})}{= (%s, %s) GeV}"%(process, m_heavy, m_light)

def get_xsc_br_fromSushi(smpNm, mode, base, process, comp):
    if mode == "HToZA":
        benchmarks = loadSushiInfos(len(smpNm),'H', 'A', f"{base}/list_benchmarks_{process}_{comp}_{mode}_datasetnames.txt")
        fullsim    = loadSushiInfos(len(smpNm),'H', 'A', f"{base}/list_fullsim_{process}_{comp}_{mode}_datasetnames.txt")
        all_       = loadSushiInfos(len(smpNm),'H', 'A', f"{base}/list_all_{process}_lo_{mode}_datasetnames.txt")
                
        arr = np.concatenate((benchmarks, fullsim, all_))

    elif mode == "AToZH":
        arr = loadSushiInfos(len(smpNm),'A', 'H', f"{base}/list_benchmarks_{process}_{comp}_{mode}_datasetnames.txt")
    
    for lis in arr:
        if not smpNm == lis[0]: continue
        if 'To2L2B' in smpNm: 
            l = 'A' if 'HToZA' in smpNm else 'H'
            H = 'H' if 'HToZA' in smpNm else 'A'
            m_heavy  = lis[1]
            m_light  = lis[2]
            tb      = lis[3]
            xsc     = lis[4]
            xsc_err = lis[5]
            br_HeavytoZlight  = lis[6]
            br_lighttobb      = lis[7]
            return H, l, m_heavy, m_light, tb, xsc, xsc_err, float(br_HeavytoZlight), float(br_lighttobb)

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
            # It's mainly for pre-/post- VFP I don't want same signal to be plotit twice with diff colors
            save_colors_forSignalGroup = {} 
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
                    heavy    = mode[0]
                    light    = mode[-1]
                    comp     = 'nlo' if 'amcatnlo' in smp else 'lo'
                    process  = f'gg{heavy}' if smpNm.startswith('GluGluTo') else(f'bb{heavy}')
                    tb       = 1.5 if  smpNm.startswith('GluGluTo') else 20.0
                    m_heavy  = float(smpNm.split('_')[1].split('-')[-1].replace('p', '.'))
                    m_light  = float(smpNm.split('_')[2].split('-')[-1].replace('p', '.'))
                
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
                    # deprecated     
                    # H, l, m_heavy, m_light, tb, xsc, xsc_err, br_HeavytoZlight, br_lighttobb = get_xsc_br_fromSushi(smpNm, mode, base, process, comp)
                    
                    # recommended 
                    with open('../data/sushi1.7.0-xsc_tanbeta-{}_2hdm-type2.yml'.format(float(tb))) as f_:
                        dict_ = yaml.safe_load(f_)
                  
                    given_mass = dict_[mode]['M{}_{}_M{}_{}'.format(heavy, float(m_heavy), light, float(m_light))]

                    br_HeavytoZlight = given_mass['branching-ratio']['{}ToZ{}'.format(heavy, light)]
                    br_lighttobb     = given_mass['branching-ratio']['{}Tobb'.format(light)]

                    if process == f'gg{heavy}': 
                        xsc  = given_mass['cross-section'][process].split()[0]
                        xsc_err  = given_mass['cross-section'][process].split()[2]
                    else: 
                        xsc  = given_mass['cross-section'][process]['NLO'].split()[0]
                        xsc_err  = given_mass['cross-section'][process]['NLO'].split()[2]

                    Nm      = smpNm.replace('-','_')+VFP
                    br      = br_HeavytoZlight * br_lighttobb * br_Ztoll
                    leg     = get_legend(process, comp, heavy, light, m_heavy, m_light, smpNm)
                    search  = smpNm
                    details = f'{heavy} -> Z{light} ({br_HeavytoZlight}) * {light} -> bb ({br_lighttobb}) * Z -> ee+ mumu ({br_Ztoll})'
                    
                    if 'VFP' in era:
                        nm_s = Nm.split('_UL')[0]
                        if nm_s in save_colors_forSignalGroup.keys():
                            color = save_colors_forSignalGroup[nm_s]
                        else:
                            save_colors_forSignalGroup = { nm_s: color }

                elif isdata:
                    Nm = f'{smpNm}_UL{era_}{run}{VFP}'
                    run_range = run2_ranges[era][run]
                    # FIXME make sure that this assumption is correct : means the certefication is the same for pre/post VFP
                    cert = certification[era.split('-')[0]] 
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
                    outf.write("    type: mc\n")
                    outf.write("    generated-events: 'genEventSumw'\n")
                    outf.write(f"    cross-section: {xsc} # +/- {uncer} pb\n")
                elif isdata :
                    outf.write("    group: data\n")
                    outf.write("    type: data\n")
                    outf.write(f"    run_range: {run_range}\n")
                    outf.write(f"    certified_lumi_file: {cert}\n")
                elif issignal :
                    outf.write("    type: signal\n")
                    outf.write("    generated-events: 'genEventSumw'\n")
                    outf.write(f"    cross-section: {xsc}   # +/- {xsc_err} pb\n")
                    outf.write(f"    branching-ratio: {br}  # {details}\n")
                    outf.write(f"    line-color: '{color}'\n")
                    outf.write("    line-type: 8\n")
                    outf.write("    line-width: 3\n")
                    outf.write(f"    legend: '{leg}'\n")
                outf.write("\n")
            outf.write("\n")
            outf.write("plotIt:\n")
            outf.write("  configuration:\n")
            outf.write("    width: 800\n")
            outf.write("    height: 800\n")
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
            outf.write("    position: [0.45, 0.5, 0.95, 0.89]\n")
            outf.write("    columns: 3\n")
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
