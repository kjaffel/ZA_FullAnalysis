import os, sys 
import argparse
import json
import glob
from collections import defaultdict

parser = argparse.ArgumentParser(description='Collection of pvalue_significance')
parser.add_argument('-i','--inputs', action='store', type=str, required=True, help='')

options = parser.parse_args()

def string_to_mass(s):
    # looks sth like this : s = MH-200_MA-50
    s = s.split('_')
    mH = s[0].split('-')[-1]
    mA = s[1].split('-')[-1]
    return mH, mA

def getValuesFromFile(file):
    val = None
    with open(file) as f:
        lines = f.readlines()
    for line in lines:
        if 'Significance:' in line:
            val = float(line.split()[-1])
            break
        elif 'p-value of background:' in line:
            val = float(line.split()[-1])
            break
    return val

pvalue_significance = defaultdict(dict)
print("Extracting pvalue_significance...")

for prod in ['gg_fusion', 'bb_associatedProduction']:
    process = 'ggH' if prod =='gg_fusion' else 'bbH'
    for reg in ['resolved', 'boosted']:
        for flavor in ['MuMu_ElEl', 'OSSF']:
            
            pvalue_path = glob.glob(os.path.join(options.inputs, 'pvalue-significance/dnn/', '*', '*expectSignal1_{}_{}_{}.log'.format(prod, reg, flavor)))
            pvalue_significance['{}_{}_{}'.format(process, reg, flavor)] = []
            for i, f in enumerate(pvalue_path):
                root     =  f.split('/')[-1]
                mH, mA   =  string_to_mass(f.split('/')[-2])

                if not 'pvalue' in root or 'significance' in root:
                    continue
                
                if 'expected' in root: key = 'expected_'
                elif 'observed' in root: key = 'observed_'
                
                if 'pvalue' in root: key += 'p-value' 
                else: key += 'significance'
                
                point_pvalue_significance = getValuesFromFile(f)
                if point_pvalue_significance is None:
                    continue
                
                print (" working on -- MH, MA: ", mH, mA , 'flavor:', flavor)
                #print ("point_pvalue_significance: ", point_pvalue_significance)
            
                masses = {'parameters'     : (float(mH), float(mA)) }
                masses.update({'{}'.format(key) :point_pvalue_significance})
                pvalue_significance['{}_{}_{}'.format(process, reg, flavor)].append( masses)

pvalue_significance_out = os.path.join(options.inputs, 'pvalue-significance/dnn/jsons')
if not os.path.exists(pvalue_significance_out):
    os.makedirs(pvalue_significance_out)

for k, v in pvalue_significance.items():
    if not v:
        continue
    output_file = os.path.join(pvalue_significance_out, 'pvalue_significance_{}.json'.format(k))
    with open(output_file, 'w') as jf:
        json.dump(v, jf, indent=4)
    print("Pvalue saved as %s" % output_file)
