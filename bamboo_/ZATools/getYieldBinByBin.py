import os, os.path, sys
import glob
import json
import yaml
import ROOT as R
R.gROOT.SetBatch(True)
import argparse

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/')
import HistogramTools as HT
import utils as utils
logger = utils.ZAlogger(__name__)

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/')
import Harvester as H
import Constants as Constants
import optimizer as optimizer

from json import JSONEncoder
from plotSystematicsVars import get_mergedBKG_processes as merge

class MarkedList:
    _list = None
    def __init__(self, l):
        self._list = l

class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, MarkedList):
            return "##<{}>##".format(o._list)

def swapdict(dic):
    channels = []
    for k, v in dic.items():
        for k2, v2 in v.items():
            if not k2 in channels:
                channels.append(k2)
    newdic = {}
    for ch in channels:
        newdic[ch] = {}
        for k,v in dic.items():
            newdic[ch][k] = v[ch]
    return newdic

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bin by Bin factory yields')
    parser.add_argument('-i', '--input', help='desired root files you want to check their yields', required=True)
    parser.add_argument('-o', '--output', help='results to be saved in', required=False)
    parser.add_argument('-e', '--era', help='working year', required=True)
    parser.add_argument('--normalize', help='scale root files if needed', required=False, default=True)

    args = parser.parse_args()
    
    if args.output ==None:
        args.output = args.input.split('bayesian_rebin')[0]

    s = 'normalized_' if args.normalize else ''
    
    with open(os.path.join(args.input.split('bayesian_rebin')[0], 'plots.yml')) as _f:
        plotConfig = yaml.load(_f, Loader=yaml.FullLoader)

    all_files  = [ f for f in plotConfig["files"] if plotConfig["files"][f]["type"] == "mc" ]
    all_files += [ f for f in plotConfig["files"] if plotConfig["files"][f]["type"] == "signal" ]
    files      = [f for  f in all_files if H.EraFromPOG(args.era) in f.split('/')[-1]]

    if not os.path.isdir(os.path.join(args.output, f'summed_{s}processes')):
        os.makedirs(os.path.join(args.output, f'summed_{s}processes'))
        merge(inputs=files, Cfg=plotConfig, inDir= args.input, outDir=args.output, era =args.era, normalize=args.normalize)
    else:
        logger.info(f'output directory {args.output}/summed_{s}processes/ is not empty, remove or change output dir path')
    
    root_files = glob.glob(os.path.join(args.output, f'summed_{s}processes', f'summed_{s}{args.era}*'))
    signal_root_files =  glob.glob(os.path.join(args.output, f'summed_{s}processes', '*_normalized_.root'))
    
    yields_b = {}
    yields_s = {}
    print( root_files )
    print( signal_root_files)
    for rf in root_files:

        smp = rf.split('/')[-1]
        smpNm = smp.split('.root')[0]

        inFile  = HT.openFileAndGet(rf)

        yields_b[smp] = {}
        for hk in inFile.GetListOfKeys():
            hist  = hk.ReadObj()
            
            if not hist.InheritsFrom("TH1"): continue
            if '__' in hist.GetName(): continue
            if not 'gg_fusion' in hist.GetName(): continue
            if not 'resolved' in hist.GetName(): continue
            
            m = hist.GetName().split('gg_fusion_')[1].split('_')
            masses = m[0] + '_' +m[1]+ 'p00_'+ m[2] + '_'+ m[3] +'p00_'
            
            for sf in signal_root_files:
                sf_nm  = sf.split('/')[-1]
                if not masses in sf_nm: continue
                
                yields_s[sf_nm] = {}
                inFile_s  = HT.openFileAndGet(sf)
                hist_s = inFile_s.Get(hist.GetName())
                
                stat_s, error_s = optimizer.bbbyields( hist_s )
                yields_s[sf_nm][hist.GetName()] = {'stat': MarkedList(stat_s), 
                                                'error': MarkedList(error_s)}
                inFile_s.Close() 

            stat, error = optimizer.bbbyields( hist )
            yields_b[smp][hist.GetName()] = {'stat': MarkedList(stat), 
                                          'error': MarkedList(error)}
        inFile.Close()

    for i, y in enumerate([yields_s, yields_b]):
        #y = swapdict(y)
        suffix = 's' if i == 0 else 'b' 
        with open(os.path.join(args.output, f"yields_{suffix}.json"), 'w') as _f:
            b = json.dumps(y, indent=2, separators=(',', ':'), cls=CustomJSONEncoder)
            b = b.replace('"##<', "").replace('>##"', "")
            _f.write(b)
        logger.info(f"yield file have been created in : {os.path.join(args.output, 'yields_%s.json')}"%suffix)
