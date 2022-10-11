#! /bin/env python
import os, sys 
import argparse, json
import stat
import subprocess
import glob
import re
import numpy as np

from collections import defaultdict

import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
# Open /dev/null to redirect stdout
DEVNULL = open(os.devnull, 'wb')

import Constants as Constants
logger = Constants.ZAlogger(__name__)


def transform_param(p):
    return float(p.replace("p", "."))


def string_to_mass(s):
    # looks sth like this : s = MH-200_MA-50
    s = s.split('_')
    mHeavy = s[0].split('-')[-1]
    mLight = s[1].split('-')[-1]
    return mHeavy, mLight


def getLimitsFromFile(input_file, method):
    """
    Extract observed, expected, and 1/2 sigma limits
    """
    data = {}
    if method == 'asymptotic':
        f = ROOT.TFile.Open(input_file)
        print( input_file)
        if not f or f.IsZombie() or f.TestBit(ROOT.TFile.kRecovered):
            return None

        # Index 0 is DOWN error, index 1 is UP error
        one_sigma = data.setdefault('one_sigma', [0, 0])
        two_sigma = data.setdefault('two_sigma', [0, 0])

        limit = f.Get('limit')

        if limit==None:
            return None 
        limit.GetEntry(2)
        data['expected'] = limit.limit
        limit.GetEntry(5)
        data['observed'] = limit.limit

        limit.GetEntry(4)
        two_sigma[1] = limit.limit - data['expected']
        limit.GetEntry(0)
        two_sigma[0] = data['expected'] - limit.limit

        limit.GetEntry(3)
        one_sigma[1] = limit.limit - data['expected']
        limit.GetEntry(1)
        one_sigma[0] = data['expected'] - limit.limit

    elif method=='hybridnew':
        f_obs = ROOT.TFile.Open(input_file)
        input_file = input_file[:-5]

        input_file_exp = input_file+".quant0.500.root"
        f_exp = ROOT.TFile.Open(input_file_exp)

        input_file_P1sigma = input_file+".quant0.840.root"
        f_P1sigma = ROOT.TFile.Open(input_file_P1sigma)

        input_file_M1sigma = input_file+".quant0.160.root"
        f_M1sigma = ROOT.TFile.Open(input_file_M1sigma)

        input_file_P2sigma = input_file+".quant0.975.root"
        f_P2sigma = ROOT.TFile.Open(input_file_P2sigma)

        input_file_M2sigma = input_file+".quant0.025.root"
        f_M2sigma = ROOT.TFile.Open(input_file_M2sigma)

        if (not f_obs or f_obs.IsZombie() or f_obs.TestBit(ROOT.TFile.kRecovered)) or (not f_exp or f_exp.IsZombie() or f_exp.TestBit(ROOT.TFile.kRecovered)) or (not f_P1sigma or f_P1sigma.IsZombie() or f_P1sigma.TestBit(ROOT.TFile.kRecovered)) or (not f_M1sigma or f_M1sigma.IsZombie() or f_M1sigma.TestBit(ROOT.TFile.kRecovered)) or (not f_P2sigma or f_P2sigma.IsZombie() or f_P2sigma.TestBit(ROOT.TFile.kRecovered)) or (not f_M2sigma or f_M2sigma.IsZombie() or f_M2sigma.TestBit(ROOT.TFile.kRecovered)):
            return None

        # Index 0 is DOWN error, index 1 is UP error
        one_sigma = data.setdefault('one_sigma', [0, 0])
        two_sigma = data.setdefault('two_sigma', [0, 0])

        limit_obs = f_obs.Get('limit')
        limit_exp = f_exp.Get('limit')
        limit_P1sigma = f_P1sigma.Get('limit')
        limit_M1sigma = f_M1sigma.Get('limit')
        limit_P2sigma = f_P2sigma.Get('limit')
        limit_M2sigma = f_M2sigma.Get('limit')

        limit_exp.GetEntry(0)
        data['expected'] = limit_exp.limit

        limit_obs.GetEntry(0)
        data['observed'] = limit_obs.limit

        limit_P2sigma.GetEntry(0)
        two_sigma[1] = limit_P2sigma.limit - data['expected']

        limit_M2sigma.GetEntry(0)
        two_sigma[0] = data['expected'] - limit_M2sigma.limit

        limit_P1sigma.GetEntry(0)
        one_sigma[1] = limit_P1sigma.limit - data['expected']

        limit_M1sigma.GetEntry(0)
        one_sigma[0] = data['expected'] - limit_M1sigma.limit

    return data

channels = {
    'ElEl'     : '$ee$',
    'MuMu'     : '$\mu\mu$',
    'MuEl'     : '$\mu e$',
    'MuMu_ElEl': '$\mu\mu + ee$',
    'OSSF'     : '$\mu\mu + ee$',
    'ElEl_MuEl': '$ee + \mu e$',
    'MuMu_MuEl': '$\mu\mu + \mu e$',
    'OSSF_MuEl': '$\mu\mu + ee + \mu e$',
    'MuMu_ElEl_MuEl': '$\mu\mu + ee + \mu e$',
                                            }
def beautify(process, reco, reg, flavor):
    if reco == 'nb2PLusn3':
        reco = 'nb2+nb3'
    if reg == 'resolved_boosted':
        reg = 'resolved+boosted'
    return '${}: {}, {}$, {}'.format(process, reco, reg, channels[flavor])


def WriteLatexTableComparasion(limits, mHeavy, mLight, tanbeta, thdm, rescale_to_za_br=False, _2POI=False, unblind=False):
    heavy = thdm[0]
    light = thdm[-1]
    print(R'\begin{table}[!htb]')
    print(R'     \caption{ Observed and Expected 2HDM-TypeII limits for ($m_{%s}$, $m_{%s}$)= (%s, %s) GeV tan$\beta$= %s.}'%(heavy, light, mHeavy, mLight, tanbeta))
    print(R' \label{table:limits_tab}')
    print(R' \small')
    print(R' \resizebox{\textwidth}{!}{')
    print(R' \begin{tabular}{@{}lcccc@{}} \toprule')
    print(R' \hspace{1cm}')
    print(R' \\')
    print(R'Cat. & Observed (fb) & Expected (fb) & 1 Standard deviation (fb) & 2 Standard deviations (fb) \\')
    print(R' \hline')
    print(R' \\')
    

    tanbeta_gluonfusion = tanbeta_bassociated = tanbeta
    if tanbeta is None:
        tanbeta_gluonfusion= 1.5
        tanbeta_bassociated= 20.

    xsc_gluonfusion, xsc_gluonfusion_err, br = Constants.get_SignalStatisticsUncer(float(mHeavy), float(mLight), 'gg{}'.format(heavy), thdm, tanbeta_gluonfusion)
    xsc_bassociated, xsc_bassociated_err, br = Constants.get_SignalStatisticsUncer(float(mHeavy), float(mLight), 'bb{}'.format(heavy), thdm, tanbeta_bassociated)
    
    sigma_tot  = xsc_gluonfusion + xsc_bassociated
    for k, limits_for_key in sorted(limits.items()):
        if not limits_for_key:
            continue
        for v in limits_for_key:
            if not v['parameters']==(mHeavy, mLight):
                continue
        
            expected     = round(v['limits']['expected']*1000, 3)
            observed     = round(v['limits']['observed']*1000, 3)
            plus_1sigma  = round(v['limits']['one_sigma'][1]*1000, 3)
            minus_1sigma = round(v['limits']['one_sigma'][0]*1000, 3)
            plus_2sigma  = round(v['limits']['two_sigma'][1]*1000, 3)
            minus_2sigma = round(v['limits']['two_sigma'][0]*1000, 3)
       
            print( thdm, expected, br )
            if rescale_to_za_br:
                expected     *= br
                observed     *= br 
                plus_1sigma  *= br
                minus_1sigma *= br
                plus_2sigma  *= br
                minus_2sigma *= br
            
            if not _2POI:
                expected     /= sigma_tot
                observed     /= sigma_tot
                plus_1sigma  /= sigma_tot
                minus_1sigma /= sigma_tot
                plus_2sigma  /= sigma_tot
                minus_2sigma /= sigma_tot

            if not unblind:
                observed = '-'
            
            print (R"%s & %s & %s & %s $\pm$ %s & %s $\pm$ %s \\"%(
                    k[1], 
                    observed,  expected, 
                    plus_1sigma, minus_1sigma,
                    plus_2sigma, minus_2sigma )
                )
    
    print(R'\hline')
    print(R'\bottomrule')
    print(R'\end{tabular}')
    print(R'}')
    print(R'\end{table}')
    return 



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Collection of limits at 95 % C.L.')
    parser.add_argument('-i','--inputs', action='store', type=str, required=True,  
                    help='List of (ROOT) combine output file to collect the limits (e.g. higgsCombineBLABLA_.AsymptoticLimits.mH125.root) or higgsCombineBLABLA_.HybridNew.mH125.root')
    parser.add_argument('--method', action='store', required=True, type=str, choices=['asymptotic', 'hybridnew'], help='Analysis method')
    parser.add_argument('--era', action='store', required=True, help='')
    parser.add_argument('--mode', action='store', required=False, default='dnn', choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'mbb', 'mllbb', 'ellipse', 'dnn'], help='')
    parser.add_argument('--tanbeta', action='store', type=float, default=None, required=False, help='')
    parser.add_argument('--_2POIs_r', action='store_true', dest='_2POIs_r', required=False, default=False,
                    help='This will merge both signal in 1 histogeram and normalise accoridngly, tanbeta will be required')

    options = parser.parse_args()
    
    
    tb_dir = ''
    if options.tanbeta is not None:
        tb_dir = 'tanbeta_{}'.format(options.tanbeta)
    
    poi_dir = '1POIs_r'
    if options._2POIs_r:
        poi_dir = '2POIs_r'
    
    
    for thdm in ['HToZA', 'AToZH']:

        print("Extracting %s limits..."%thdm)
        limits = defaultdict(dict)
        crap_points = {}
        
        heavy = thdm[0]
        light = thdm[-1]

        for process, prod in {'gg{}'.format(heavy): 'gg_fusion', 
                              'bb{}'.format(heavy): 'bb_associatedProduction', 
                              #'profiled_r_gg{}'.format(heavy): 'gg_fusion_bb_associatedProduction', # limit set on bbH while ggH left floating  if thdm == HToZA
                              #'profiled_r_bb{}'.format(heavy): 'gg_fusion_bb_associatedProduction', #         -    ggH    -  bbH         -
                              #'freezed_r_gg{}'.format(heavy) : 'gg_fusion_bb_associatedProduction', # limit set on bbH while ggH set to certain value
                              #'freezed_r_bb{}'.format(heavy) : 'gg_fusion_bb_associatedProduction', #          -   ggH    -  bbH         -  
                              }.items():
            
            if options.method == "asymptotic":
                s = '.AsymptoticLimits.mH125.root'
            elif options.method == "hybridnew":
                s = '.HybridNew.mH125.root'
            
            for reco in ['nb2PLusnb3', 'nb2', 'nb3']:
                for reg in ['resolved', 'boosted', 'resolved_boosted']:
                    for flavor in ['MuMu_ElEl', 'ElEl', 'MuMu', 'MuEl', 'MuMu_ElEl_MuEl', 'ElEl_MuEl', 'MuMu_MuEl', 'OSSF', 'OSSF_MuEl']:
                        
                        # I don't need this for now
                        # too much details I don't need 
                        if flavor in ['ElEl_MuEl', 'MuMu_MuEl', 'ElEl', 'MuMu', 'MuEl']: 
                            continue
                        
                        limits_path = glob.glob(os.path.join(options.inputs, '{}-limits'.format(options.method), options.mode, poi_dir, tb_dir, '*', '*{}'.format(s)))
                        latex_k = beautify(process, reco, reg, flavor)
                        limits[('{}_{}_{}_{}'.format(process, reco, reg, flavor), latex_k)] = []
                        for f in limits_path:
                            root     =  f.split('/')[-1]

                            mHeavy, mLight   =  string_to_mass(f.split('/')[-2])
                           
                            if not root.startswith('higgsCombine{}To2L2B_{}_{}_{}_{}_{}_'.format(thdm, prod, reco, reg, flavor, options.mode)):
                                continue
                            
                            point_limits = getLimitsFromFile(f, options.method)
                            #print ( 'working on::', f)
                            #print ( 'working on -- M%s, M%s:'%(heavy, light), mHeavy, mLight , 'template:', options.mode, 'flavor:', flavor)
                        
                            if point_limits is None:
                                k = '{}_{}_{}_{}'.format(process, reco, reg, flavor)
                                m = (float(mHeavy), float(mLight))
                                if not k in crap_points.keys(): crap_points[k]= []
                                if not m in crap_points[k]: crap_points[k].append(m)
                                print("Warning: limits not found for {} in {}, skipping point".format(m, k))
                                continue

                            if point_limits['expected'] == 0:
                                print("Warning: expected is 0, skipping point")
                                continue
                            
                            limits[('{}_{}_{}_{}'.format(process, reco, reg, flavor), latex_k)].append({
                                'parameters': (mHeavy, mLight),
                                'limits'    : point_limits
                                })
        
        limits_out = os.path.join(options.inputs, '{}-limits'.format(options.method), options.mode, 'jsons', poi_dir, tb_dir)
        if not os.path.exists(limits_out):
            os.makedirs(limits_out)
        
        for k, v in limits.items():
            if not v:
                continue
            
            output_file = os.path.join(limits_out, 'combinedlimits_{}_UL{}.json'.format(k[0], options.era))
            with open(output_file, 'w') as jf:
                json.dump(v, jf, indent=4)
            print("Limits saved as %s" % output_file)

        logger.info(' issues with these %s points no limit is found : %s'%(thdm, crap_points))
        
        WriteLatexTableComparasion(limits, "780.0", "680.0", options.tanbeta, thdm, rescale_to_za_br=True, _2POI=options._2POIs_r, unblind=False)

