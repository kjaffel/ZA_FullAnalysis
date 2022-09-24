import os, os.path
import argparse
import glob 

from CP3SlurmUtils.Configuration import Configuration
from CP3SlurmUtils.SubmitWorker import SubmitWorker

def SlurmCombine(cardDir):
    config = Configuration()
    config.sbatch_partition = 'cp3'
    config.sbatch_qos = 'cp3'
    config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
    config.sbatch_chdir = os.path.join(config.cmsswDir, 'combine4slurm')
    config.sbatch_time = '01:59:00'
    sbatch_memPerCPU = '2000'
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
    parser.add_argument("--cards", default=None, required=True, help="cards dir")
    
    options = parser.parse_args()

    SlurmCombine(cardDir=options.cards)
