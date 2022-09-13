import os, os.path
import datetime
import argparse
import glob 

from CP3SlurmUtils.Configuration import Configuration
from CP3SlurmUtils.SubmitWorker import SubmitWorker

import logging
LOG_LEVEL = logging.DEBUG
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
logger = logging.getLogger("Bayesian")
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream)


def SlurmRunBayesianBlocks(outputDIR, bambooDIR, era, isTest, unblind):
    config = Configuration()
    config.sbatch_partition = 'cp3'
    config.sbatch_qos = 'cp3'
    config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
    config.sbatch_chdir = os.path.join(outputDIR, 'slurm')
    config.sbatch_time = '01:59:00'
    sbatch_memPerCPU = '7000'
    #config.environmentType = 'cms'
    config.inputSandboxContent = ["run_bboptimizer.sh"]
    config.stageoutFiles = ['*.root']
    config.stageoutDir = config.sbatch_chdir
    config.inputParamsNames = ['cmssw', 'input']
    config.inputParams = []
    #config.numJobs = 1
    
    era_ = era.replace('20', '')
    cmssw = config.cmsswDir

    for i, inF in enumerate(glob.glob(os.path.join(bambooDIR, 'results', '*.root'))): 
        smp = inF.split('/')[-1]
        
        if era!='fullrun2':
            if not f"_UL{era_}" in smp:
                continue
        
        if not unblind:
            if any(x in smp for x in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon']):
                continue

        if isTest and i!=0:
            continue
        
        config.inputParams.append([cmssw, inF])
    
    config.payload = \
        """
                pushd ${cmssw}
                bash run_bboptimizer.sh ${cmssw} ${input}
        """
    submitWorker = SubmitWorker(config, submit=True, yes=True, debug=True, quiet=True)
    submitWorker()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bayesian Blocks', formatter_class=argparse.RawTextHelpFormatter)
    
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    parser.add_argument("-o", "--output", default=None, required=True, help="output dir")
    parser.add_argument("-i", "--input", default=None, required=True, help="bamboo stageout dir")
    parser.add_argument("--era", type=str, required=True, help="")
    parser.add_argument("--test", action='store_true', dest='isTest', default=False, help="")
    parser.add_argument("--unblind", action='store_true', default=False, help="If set to Trur will produced histogram for data too")
    
    options = parser.parse_args()

    SlurmRunBayesianBlocks(outputDIR=options.output, bambooDIR=options.input, era=options.era, isTest=options.isTest, unblind=options.unblind)
