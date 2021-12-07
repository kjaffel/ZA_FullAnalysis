#! /bin/env python
import os, sys 
import argparse, json
import stat
import subprocess
import glob
import re

import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
# Open /dev/null to redirect stdout
DEVNULL = open(os.devnull, 'wb')

import numpy as np
from collections import defaultdict


def transform_param(p):
    return float(p.replace("p", "."))

def string_to_mass(s):
    # looks sth like this : s = MH-200_MA-50
    s = s.split('_')
    mH = s[0].split('-')[-1]
    mA = s[1].split('-')[-1]
    return mH, mA

def getLimitsFromFile(input_file, method):
    """
    Extract observed, expected, and 1/2 sigma limits
    """
    if method == 'asymptotic':
        f = ROOT.TFile.Open(input_file)
        print( input_file)
        if not f or f.IsZombie() or f.TestBit(ROOT.TFile.kRecovered):
            return None

        data = {}
        # Index 0 is DOWN error, index 1 is UP error
        one_sigma = data.setdefault('one_sigma', [0, 0])
        two_sigma = data.setdefault('two_sigma', [0, 0])

        limit = f.Get('limit')

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

        data = {}
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

parser = argparse.ArgumentParser(description='Collection non-resonant limits')
parser.add_argument('-i','--inputs', action='store', type=str, required=True,  
                help='List of (ROOT) combine output file to collect the limits (e.g. higgsCombineBLABLA_.AsymptoticLimits.mH125.root) or higgsCombineBLABLA_.HybridNew.mH125.root')
parser.add_argument('--method', action='store', required=True, type=str, choices=['asymptotic', 'hybridnew'], 
                help='Analysis method')
options = parser.parse_args()

if options.method == "asymptotic":
    s = '.AsymptoticLimits.mH125.root'
elif options.method == "hybridnew":
    s = '.HybridNew.mH125.root'

limits = defaultdict(dict)
print("Extracting limits...")
for prod in ['gg_fusion', 'bb_associatedProduction']:
    process = 'ggH' if prod =='gg_fusion' else 'bbH'
    for reg in ['resolved', 'boosted']:
        for flavor in ['ElEl_MuMu', 'ElEl', 'MuMu']:
            
            limits_path = glob.glob(os.path.join(options.inputs, '{}-limits'.format(options.method), '*', '*', '*{}'.format(s)))
            limits['{}_{}_{}'.format(process, reg, flavor)] = []
            for f in limits_path:
                root     =  f.split('/')[-1]
                mH, mA   =  string_to_mass(f.split('/')[-2])
                mode     =  f.split('/')[-3]
                if not root.startswith('higgsCombineHToZATo2L2B_{}_{}_{}'.format(prod, reg, flavor)):
                    continue
                point_limits = getLimitsFromFile(f, options.method)
                print (" working on -- MH, MA: ", mH, mA , 'template:', mode, 'flavor:', flavor)
                #print ("point_limits: ", point_limits)
            
                if point_limits['expected'] == 0:
                    print("Warning: expected is 0, skipping point")
                    continue
                limits['{}_{}_{}'.format(process, reg, flavor)].append({
                    'parameters': (mH, mA),
                    'limits'    : point_limits
                    })

limits_out = os.path.join(options.inputs, '{}-limits'.format(options.method), 'jsons', mode)
if not os.path.exists(limits_out):
    os.makedirs(limits_out)
for k, v in limits.items():
    if not v:
        continue
    output_file = os.path.join(limits_out, 'combinedlimits_{}.json'.format(k))
    with open(output_file, 'w') as jf:
        json.dump(v, jf, indent=4)
    print("Limits saved as %s" % output_file)
