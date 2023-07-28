import os, os.path
import argparse
import glob 

from CP3SlurmUtils.Configuration import Configuration
from CP3SlurmUtils.SubmitWorker import SubmitWorker

import Constants as Constants
logger = Constants.ZAlogger(__name__)

def SlurmCombine(cardDir, method, outDir, time, mem_per_cpu, isTest):
    config = Configuration()
    config.sbatch_partition = 'cp3'
    config.sbatch_qos = 'cp3'
    config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
    config.sbatch_chdir = os.path.join(outDir, 'slurm', method)
    config.sbatch_time  = time
    config.sbatch_memPerCPU = mem_per_cpu
    #config.sbatch_additionalOptions=['--exclude=mb-sky[002,005-014,016-018,020],mb-ivy220,mb-ivy213,mb-ivy212,mb-ivy211']
    #config.environmentType = "cms"
    #config.inputSandboxContent = [""]
    #config.stageoutFiles = ['*.root']
    config.stageoutDir = config.sbatch_chdir
    config.inputParamsNames = ['cmssw', 'dir', 'script']
    config.inputParams = []
    #config.numJobs = 1
    
    if os.path.exists(config.sbatch_chdir):
        logger.warning("Output directory {}/ , already exists !!".format(config.sbatch_chdir))
        exit()
    
    #flav = '_dnn_'         # no muel
    #flav = '_MuEl_dnn_'    # with muel
    flav  = '_'             # all
    
    cmssw = config.cmsswDir
    for i, inF in enumerate(glob.glob(os.path.join(cardDir, '*', '*.sh'))): 
        script = os.path.basename(inF)
        dir    = os.path.dirname(inF)
        m      = inF.split('/')[-2]
        
        #if isTest and i!=0:
        #   continue

        if method != 'generatetoys-data': 
            # just keep what I need for now        
            # A->ZH and H->ZA
            if not( # multi-signal fit
                    any(x in script for x in [
                        "gg_fusion_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF{}".format(flav),
                        "gg_fusion_bb_associatedProduction_nb2PLusnb3_resolved_OSSF{}".format(flav),
                        "gg_fusion_bb_associatedProduction_nb2_resolved_OSSF{}".format(flav), 
                        "gg_fusion_bb_associatedProduction_nb2_resolved_boosted_OSSF{}".format(flav)] ) or
                    any(x in script for x in [
                        # comb b-associated production
                        "bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF{}".format(flav),
                        "bb_associatedProduction_nb2PLusnb3_resolved_OSSF{}".format(flav),
                        "bb_associatedProduction_nb2PLusnb3_boosted_OSSF{}".format(flav),
                        # nb2
                        "bb_associatedProduction_nb2_resolved_boosted_OSSF{}".format(flav),
                        "bb_associatedProduction_nb2_resolved_OSSF{}".format(flav),
                        "bb_associatedProduction_nb2_boosted_OSSF{}".format(flav), 
                        #
                        "gg_fusion_nb2_resolved_boosted_OSSF{}".format(flav), 
                        "gg_fusion_nb2_resolved_MuMu_ElEl{}".format(flav), 
                        "gg_fusion_nb2_boosted_OSSF{}".format(flav),
                        # nb3
                        "bb_associatedProduction_nb3_resolved_boosted_OSSF{}".format(flav),
                        "bb_associatedProduction_nb3_resolved_OSSF{}".format(flav),
                        "bb_associatedProduction_nb3_boosted_OSSF{}".format(flav) 
                        ] ) 
                    ):
                continue

        config.inputParams.append([cmssw, dir, script])
    config.payload = \
        """
            echo "working on combine scripts :::"
            pushd ${cmssw}/${dir} &> /dev/null
            which python
            bash ${script}
            popd &> /dev/null
        """
    submitWorker = SubmitWorker(config, submit=True, yes=True, debug=True, quiet=True)
    submitWorker()
    return 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-c", "--cards" , default=None, required=True, help="cards dir")
    parser.add_argument("-o", "--output", default=None, required=True, help="output dir") 
    parser.add_argument("--test"       , action='store_true', dest='isTest', default=False, help="")
    parser.add_argument("--method"     , action='store', type=str, required=True, help="combine method") 
    parser.add_argument("--time"       , action='store', type=str, default='02:59:00', help="sbatch_time") 
    parser.add_argument("--mem-per-cpu", action='store', type=str, dest='mem_per_cpu', default='7000', help="sbatch_memPerCPU") 
    options = parser.parse_args()

    SlurmCombine(cardDir     = options.cards, 
                 method      = options.method, 
                 outDir      = options.output, 
                 time        = options.time, 
                 mem_per_cpu = options.mem_per_cpu, 
                 isTest      = options.isTest)

