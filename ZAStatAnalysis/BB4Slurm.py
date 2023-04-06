import os, os.path
import datetime
import argparse
import glob 
import numpy as np

from CP3SlurmUtils.Configuration import Configuration
from CP3SlurmUtils.SubmitWorker import SubmitWorker


def get_signal_parameters(f):
    if '_tb_' in f:  # Khawla new version format of signal sample
        split_filename = f.replace('.root','').split('To2L2B_')[-1]
        m_heavy = split_filename.split('_')[1].replace('p', '.')
        m_light = split_filename.split('_')[3].replace('p', '.')
    return float(m_heavy), float(m_light)


def SlurmRunBayesianBlocks(outputDIR, bambooResDIR, rebin, era, mode, submit, scenario, unblind):
    config = Configuration()
    config.sbatch_partition = 'cp3'
    config.sbatch_qos = 'normal'
    config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
    config.sbatch_chdir = os.path.join(outputDIR, 'slurm', 'bayesian')
    config.sbatch_time = '00:59:00'
    config.sbatch_memPerCPU = '1000'
    config.sbatch_additionalOptions=['--exclude=mb-ivy220']
    #config.environmentType = 'cms'
    #config.inputSandboxContent = [""]
    #config.stageoutFiles = ['*.root']
    config.stageoutDir = config.sbatch_chdir
    config.inputParamsNames = ['cmssw', 'input', 'output', 'rebin', 'era', 'mode', 'submit', 'scenario']
    config.inputParams = []
    #config.numJobs = 1
    
    era_  = era.replace('20', '')
    cmssw = config.cmsswDir

    for i, inF in enumerate(glob.glob(os.path.join(bambooResDIR, '*.root'))): 
        smp = inF.split('/')[-1]
        
        if era!='fullrun2':
            if not f"_UL{era_}" in smp:
                continue
        
        if not unblind:
            if any(x in smp for x in ['MuonEG', 'DoubleEG', 'EGamma', 'DoubleMuon', 'SingleMuon', 'SingleElectron']):
                continue
        
        if submit =='test':
            if i !=0:
                continue

        config.inputParams.append([cmssw, inF, outputDIR, rebin, era, mode, submit, scenario])
    
    config.payload = \
        """
            pushd ${cmssw}
            echo "running ::" optimizeBinning.py --input ${input} --output ${output} --rebin ${rebin} --era ${era} --mode ${mode} --submit ${submit} --scenario ${scenario} --sys --job slurm
            python optimizeBinning.py --input ${input} --output ${output} --rebin ${rebin} --era ${era} --mode ${mode} --submit ${submit} --scenario ${scenario} --sys --job slurm
        """
    submitWorker = SubmitWorker(config, submit=True, yes=True, debug=True, quiet=True)
    submitWorker()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bayesian Blocks', formatter_class=argparse.RawTextHelpFormatter)
    
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    parser.add_argument("-i", "--input", default=None, required=True, help="bamboo stageout dir")
    parser.add_argument("-o", "--output", default=None, required=True, help="output dir")
    parser.add_argument("--era", type=str, default='fullrun2', required=False, help="")
    parser.add_argument('--mode', action='store', required=False, default='dnn', choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'mbb', 'mllbb', 'ellipse', 'dnn'], help='')
    parser.add_argument('--unblind', action='store_true', default=False, help="If set to True will produced histogram for data too")
    parser.add_argument('--rebin', action='store', choices= ['custom', 'standalone', 'bayesian'], required=True, help='')
    parser.add_argument('--scenario', action='store', choices= ['hybride', 'S', 'B', 'BB_hybride_good_stat'], required=False, help='')
    parser.add_argument('--submit', action='store', default='test', choices=['all', 'test'], help='')

    options = parser.parse_args()
    
    SlurmRunBayesianBlocks( outputDIR   = options.output, 
                            bambooResDIR= options.input, 
                            rebin       = options.rebin,
                            era         = options.era,
                            mode        = options.mode,
                            submit      = options.submit,
                            scenario    = options.scenario,
                            unblind     = options.unblind 
                           )
