import os, os.path
import argparse
import glob 

from CP3SlurmUtils.Configuration import Configuration
from CP3SlurmUtils.SubmitWorker import SubmitWorker

def SlurmCombine(cardDir, method, outDir, time, mem_per_cpu, isTest):
    config = Configuration()
    config.sbatch_partition = 'cp3'
    config.sbatch_qos = 'cp3'
    config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
    config.sbatch_chdir = os.path.join(outDir, 'slurm', method)
    config.sbatch_time  = time
    config.sbatch_memPerCPU = mem_per_cpu
    #config.environmentType = "cms"
    #config.inputSandboxContent = [""]
    #config.stageoutFiles = ['*.root']
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
        m = inF.split('/')[-2]
        #if not script in [ "HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_500.0_MA_300.0_run_goodness_of_fit.sh",
        #                   "HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_500.0_MA_300.0_run_goodness_of_fit.sh",
        #                   "HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_300.0_MA_200.0_run_goodness_of_fit.sh",
        #                   "HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_300.0_MA_200.0_run_goodness_of_fit.sh",
        #                   "HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_run_goodness_of_fit.sh",
        #                   "HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_650.0_MA_50.0_run_goodness_of_fit.sh",
        #                   "HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_650.0_MA_50.0_run_goodness_of_fit.sh",
        #                   "HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_650.0_MA_50.0_run_goodness_of_fit.sh",
        #                   "HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_800.0_MA_200.0_run_goodness_of_fit.sh",
        #                   "HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_800.0_MA_200.0_run_goodness_of_fit.sh"]:
        #    continue
        #if not m in ['MA-800.0_MH-140.0', 'MH-650.0_MA-50.0', 'MH-300.0_MA-200.0', 'MH-379.0_MA-54.59', 'MH-500.0_MA-300.0', 'MH-510.0_MA-130.0', 'MA-510.0_MH-130.0', 'MH-800.0_MA-200.']:
        #    continue
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
    parser.add_argument("-c", "--cards" , default=None, required=True, help="cards dir")
    parser.add_argument("-o", "--output", default=None, required=True, help="output dir") 
    parser.add_argument("--test"       , action='store_true', dest='isTest', default=False, help="")
    parser.add_argument("--method"     , action='store', type=str, required=True, help="combine method") 
    parser.add_argument("--time"       , action='store', type=str, default='02:59:00', help="sbatch_time") 
    parser.add_argument("--mem-per-cpu", action='store', type=str, dest='mem_per_cpu', default='7000', help="sbatch_memPerCPU") 
    options = parser.parse_args()

    SlurmCombine(cardDir=options.cards, method= options.method, outDir=options.output, time=options.time, mem_per_cpu=options.mem_per_cpu, isTest=options.isTest)

