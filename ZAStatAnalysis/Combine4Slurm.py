import os, os.path
import argparse
import glob 

from CP3SlurmUtils.Configuration import Configuration
from CP3SlurmUtils.SubmitWorker import SubmitWorker

def SlurmCombine(cardDir, outDir, isTest):
    config = Configuration()
    config.sbatch_partition = 'cp3'
    config.sbatch_qos = 'cp3'
    config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
    config.sbatch_chdir = os.path.join(outDir, 'combine4slurm')
    config.sbatch_time = '02:59:00'
    config.sbatch_memPerCPU = '27000'
    #config.sbatch_memPerCPU = '7000'
    #config.environmentType = "cms"
    #config.inputSandboxContent = [""]
    config.stageoutFiles = ['*.root']
    config.stageoutDir = config.sbatch_chdir
    config.inputParamsNames = ['cmssw', 'dir', 'script']
    config.inputParams = []
    #config.numJobs = 1

    cmssw = config.cmsswDir
    for i, inF in enumerate(glob.glob(os.path.join(cardDir, '*', '*.sh'))): 
        script = os.path.basename(inF)
        dir    = os.path.dirname(inF)
        if isTest and i!=0:
            continue
        config.inputParams.append([cmssw, dir, script])
    config.payload = \
        """
            echo "working on combine scripts :::"
            pushd ${cmssw}/${dir} &> /dev/null
            bash ${script}
            popd &> /dev/null
        """
    submitWorker = SubmitWorker(config, submit=True, yes=True, debug=True, quiet=True)
    submitWorker()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-c", "--cards", default=None, required=True, help="cards dir")
    parser.add_argument("-o", "--output", default=None, required=True, help="output dir") 
    parser.add_argument("--test", action='store_true', dest='isTest', default=False, help="")
    options = parser.parse_args()

    SlurmCombine(cardDir=options.cards, outDir=options.output,  isTest=options.isTest)
