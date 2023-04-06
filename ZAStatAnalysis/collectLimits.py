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
    if reco == 'nb2PLusnb3':
        reco = 'nb2+nb3'
    if reg == 'resolved_boosted':
        reg = 'resolved+boosted'
    if '_r_' in process:
        process = process.replace('_', '\_')
    return '${}: {}, {}$, {}'.format(process, reco, reg, channels[flavor])

    
def get_rescale_to_za_br(k, br_gg, br_bb):
    if '_r_' in k:
        if 'gg' in k:
            return br_bb
        else:
            return br_gg
    else:
        if 'gg' in k:
            return br_gg
        else:
            return br_bb


def WriteLatexTableComparasion(limits, limits_pathOut, cl, mHeavy, mLight, tanbeta, thdm, era, rescale_to_za_br=False, _2POI=False, unblind=False):
    mHeavy = str(float(mHeavy))
    mLight = str(float(mLight))
    
    xbr = ''
    if rescale_to_za_br:
        xbr = 'xbr'

    heavy  = thdm[0]
    light  = thdm[-1]
    
    sys.stdout = open(os.path.join(limits_pathOut, 'xsc_{}_{}_m{}-{}_m{}-{}_{}_UL{}.tex'.format(xbr, thdm, heavy, mHeavy, light, mLight, cl, era)), "w+")
    cl = '$CL_{s}$' if cl == 'CLs' else '$CL_{s+b}$'
    tanbeta_gluonfusion = tanbeta_bassociated = tanbeta
    
    tb = R', tan$\beta$= %s'%tanbeta
    if tanbeta is None:
        tb = R''
        tanbeta_gluonfusion= 1.5
        tanbeta_bassociated= 20.
    
    
    
    print(R'\begin{table}[!htb]')
    print(R'     \caption{ 95\% '+ R'%s upper limits on %s $\rightarrow$ Z%s $\rightarrow$ llbb production cross section times branching ratio for ($m_{%s}$, $m_{%s}$)= (%s, %s) GeV%s, 2HDM-II, %s data.}'%(cl, heavy, light, heavy, light, mHeavy, mLight, tb, era))
    print(R' \label{table:limits_tab}')
    print(R' \small')
    print(R' \resizebox{\textwidth}{!}{')
    print(R' \begin{tabular}{@{}lcccc@{}} \toprule')
    print(R' \hspace{1cm}')
    print(R' \\')
    print(R'Cat. & Observed (fb) & Expected (fb) & $\pm$1 Standard deviation (fb) & $\pm$2 Standard deviations (fb) \\')
    print(R' \hline')
    print(R' \\')

    if rescale_to_za_br:
        xsc_gluonfusion, xsc_gluonfusion_err, br1 = Constants.get_SignalStatisticsUncer(float(mHeavy), float(mLight), 'gg{}'.format(heavy), thdm, tanbeta_gluonfusion)
        xsc_bassociated, xsc_bassociated_err, br2 = Constants.get_SignalStatisticsUncer(float(mHeavy), float(mLight), 'bb{}'.format(heavy), thdm, tanbeta_bassociated)
        
        sigma_tot  = xsc_gluonfusion + xsc_bassociated
    
    for k, limits_for_key in sorted(limits.items()):
        #if 'MuEl' not in k[0]:
        #    continue
        if not limits_for_key:
            continue
        
        if rescale_to_za_br:
            br = get_rescale_to_za_br(k=k[0], br_gg=br1, br_bb=br2)

        for v in limits_for_key:
            if not v['parameters']==(mHeavy, mLight):
                continue
        
            expected     = v['limits']['expected']*1000 # from pb to fb
            observed     = v['limits']['observed']*1000
            _1sigma_up   = v['limits']['one_sigma'][1]*1000
            _1sigma_down = v['limits']['one_sigma'][0]*1000
            _2sigma_up   = v['limits']['two_sigma'][1]*1000
            _2sigma_down = v['limits']['two_sigma'][0]*1000

            if rescale_to_za_br:
                expected     *= br
                observed     *= br 
                _1sigma_up   *= br
                _1sigma_down *= br
                _2sigma_up   *= br
                _2sigma_down *= br
            
            if not _2POI:
                expected     /= sigma_tot
                observed     /= sigma_tot
                _1sigma_up   /= sigma_tot
                _1sigma_down /= sigma_tot
                _2sigma_up   /= sigma_tot
                _2sigma_down /= sigma_tot
            
            expected     = round(expected,3)
            observed     = round(observed,3)
            _1sigma_up   = round(_1sigma_up,3)
            _1sigma_down = round(_1sigma_down,3)
            _2sigma_up   = round(_2sigma_up,3)
            _2sigma_down = round(_2sigma_down,3)

            if not unblind:
                observed = '-'
            
            print (R"%s & %s & %s & %s $\pm$ %s & %s $\pm$ %s \\"%(
                    k[1], 
                    observed,  expected, 
                    _1sigma_up, _1sigma_down,
                    _2sigma_up, _2sigma_down )
                )
    
    print(R'\\')
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
    parser.add_argument('--unblind', action='store_true', default=False,
                    help='unblind data in dnn score template')
    parser.add_argument('--multi_signal',       action='store_true', dest='multi_signal', required=False, default=False,
                    help='The cards will contain both signals but using 1 discriminator nb2 for gg-fusion and nb3 for bb-associated production')
    parser.add_argument('--method', action='store', required=True, type=str, choices=['asymptotic', 'hybridnew'], help='Analysis method')
    parser.add_argument('--era', action='store', required=True, help='')
    parser.add_argument('--mode', action='store', required=False, default='dnn', choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'mbb', 'mllbb', 'ellipse', 'dnn'], help='')
    parser.add_argument('--tanbeta', action='store', type=float, default=None, required=False, help='')
    parser.add_argument('--_2POIs_r', action='store_true', dest='_2POIs_r', required=False, default=False,
                    help='This will merge both signal in 1 histogeram and normalise accoridngly, tanbeta will be required')
    parser.add_argument('--expectSignal', action='store', required=False, type=int, default=1, choices=[0, 1],
                    help=' Is this S+B or B-Only fit? ')
    parser.add_argument('-r', '--rescale-to-za-br', action='store_true', dest='rescale_to_za_br',
                    help='If flagged True, limits in HToZA mode will be x to BR( Z -> ll) x BR(A -> bb ) x (H -> ZA)')

    options = parser.parse_args()
    
    
    poi_dir, tb_dir, CL_dir = Constants.locate_outputs( options.method, options._2POIs_r, options.tanbeta, options.expectSignal, options.multi_signal) 
    for thdm in ['HToZA', 'AToZH']:

        #print("Extracting %s limits..."%thdm)
        limits = defaultdict(dict)
        crap_points = {}
        
        heavy = thdm[0]
        light = thdm[-1]

        for process, prod in {'gg{}'.format(heavy): 'gg_fusion', 
                              'bb{}'.format(heavy): 'bb_associatedProduction', 
                              'profiled_r_gg{}'.format(heavy): 'gg_fusion_bb_associatedProduction', # limit set on bbH while ggH left floating  if thdm == HToZA
                              'profiled_r_bb{}'.format(heavy): 'gg_fusion_bb_associatedProduction', #         -    ggH    -  bbH         -
                              'freezed_r_gg{}'.format(heavy) : 'gg_fusion_bb_associatedProduction', # limit set on bbH while ggH set to certain value
                              'freezed_r_bb{}'.format(heavy) : 'gg_fusion_bb_associatedProduction', #          -   ggH    -  bbH         -  
                              }.items():
            
            s0 =''
            if '_r_' in process: s0 = process 

            if options.method == "asymptotic":
                s = '{}.AsymptoticLimits.mH125.root'.format(s0)
            elif options.method == "hybridnew":
                s = '{}.HybridNew.mH125.root'.format(s0)
            
            for reco in ['nb2PLusnb3', 'nb2', 'nb3']:
                for reg in ['resolved', 'boosted', 'resolved_boosted']:
                    for flavor in ['MuMu_ElEl', 'MuMu_ElEl_MuEl', 'OSSF', 'OSSF_MuEl']: #'ElEl_MuEl', 'MuMu_MuEl', 'ElEl', 'MuMu', 'MuEl']: 
                        
                        limits_path = glob.glob(os.path.join(options.inputs, '{}-limits'.format(options.method), options.mode, CL_dir, poi_dir, tb_dir, '*', '*{}'.format(s)))
                        
                        latex_k = beautify(process, reco, reg, flavor)
                        limits[('{}_{}_{}_{}'.format(process, reco, reg, flavor), latex_k)] = []
                        for f in limits_path:
                            root     =  f.split('/')[-1]

                            mHeavy, mLight   =  string_to_mass(f.split('/')[-2])
               
                            if not root.startswith('higgsCombine{}To2L2B_{}_{}_{}_{}_{}_'.format(thdm, prod, reco, reg, flavor, options.mode)):
                                continue
                            
                            point_limits = getLimitsFromFile(f, options.method)
                            print ( 'working on::', f)
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
        
        limits_pathOut = os.path.join(options.inputs, '{}-limits'.format(options.method), options.mode, 'jsons', poi_dir, tb_dir)
        if not os.path.exists(limits_pathOut):
            os.makedirs(limits_pathOut)
        
        for k, v in limits.items():
            if not v:
                continue
            
            output_file = os.path.join(limits_pathOut, 'combinedlimits_{}_{}_UL{}.json'.format(k[0], CL_dir, options.era))
            with open(output_file, 'w') as jf:
                json.dump(v, jf, indent=4)
            print("Limits saved as %s" % output_file)

        logger.info(' issues with these %s points no limit is found : %s'%(thdm, crap_points))
       
        # not computed yet : (550.0, 300.0), (670.0, 500.0), (300.0, 135.0), (250.0, 125.0), (220.0, 127.0),
        for (m_heavy, m_light) in [(240.0, 130.0), (700.0, 200.0), (750.0, 610.0), (500.0, 250.0), (800.0, 140.0), (200.0, 125.0), (510.0, 130.0), (780.0, 680.0)]:
            WriteLatexTableComparasion(limits, limits_pathOut, CL_dir, m_heavy, m_light, options.tanbeta, thdm, options.era, rescale_to_za_br=options.rescale_to_za_br, _2POI=options._2POIs_r, unblind=False)

