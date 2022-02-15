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
    parser.add_argument('-i', '--input', help='desired root files need to checks their yields', required=True)
    parser.add_argument('-o', '--output', help='results to be saved in', required=True)
    parser.add_argument('-e', '--era', help='working year', required=True)
    parser.add_argument('--normalize', help='scale root files if needed', required=False, default=True)

    args = parser.parse_args()
    
    s = 'normalized_' if args.normalize else ''
    
    plotter_p = "../../ZAStatAnalysis/ul__combinedlimits/preapproval/work__v10-ext2/"
    with open(os.path.join(plotter_p, 'plots.yml')) as _f:
        plotConfig = yaml.load(_f, Loader=yaml.FullLoader)

    files = [ f for f in plotConfig["files"] if plotConfig["files"][f]["type"] == "mc" ]
    if not os.path.isdir(os.path.join(args.output, f'summed_{s}processes')):
        os.makedirs(os.path.join(args.output, f'summed_{s}processes'))
        root_files = merge(inputs=files, Cfg=plotConfig, inDir= args.input, outDir=args.output, era =args.era, normalize=args.normalize)
    else:
        logger.info(f'output directory {args.output} is not empty, remove or change output dir path')
        root_files = glob.glob(os.path.join(args.output, f'summed_{s}processes', f'summed_{s}{args.era}*'))
    
    yields = {}
    print( root_files )
    for rf in root_files:

        smp = rf.split('/')[-1]
        smpNm = smp.split('.root')[0]

        inFile  = HT.openFileAndGet(rf)

        yields[smp] = {}
        for hk in inFile.GetListOfKeys():
            hist  = hk.ReadObj()

            if not hist.InheritsFrom("TH1"): continue
            if '__' in hist.GetName(): continue
            if not 'gg_fusion' in hist.GetName(): continue
            if not 'resolved' in hist.GetName(): continue

            stat, error = optimizer.bbbyields( hist )
            yields[smp][hist.GetName()] = {'stat': MarkedList(stat), 
                                          'error': MarkedList(error)}
        inFile.Close()

    y = swapdict(yields)
    with open(os.path.join(args.output, f"yields.json"), 'w') as _f:
        b = json.dumps(y, indent=2, separators=(',', ':'), cls=CustomJSONEncoder)
        b = b.replace('"##<', "").replace('>##"', "")
        _f.write(b)
