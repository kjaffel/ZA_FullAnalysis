import os, os.path
import argparse
import glob 

from CP3SlurmUtils.Configuration import Configuration
from CP3SlurmUtils.SubmitWorker import SubmitWorker


def SlurmCombine(cardDir, method, outDir, time, mem_per_cpu, isTest):
    config = Configuration()
    config.sbatch_partition = 'Def'
    config.sbatch_qos = 'normal'
    config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
    config.sbatch_chdir = os.path.join(outDir, 'slurm', method)
    config.sbatch_time  = time
    config.sbatch_memPerCPU = mem_per_cpu
    config.sbatch_additionalOptions=['--exclude=mb-ivy220']
    #config.environmentType = "cms"
    #config.inputSandboxContent = [""]
    #config.stageoutFiles = ['*.root']
    config.stageoutDir = config.sbatch_chdir
    config.inputParamsNames = ['cmssw', 'dir', 'script']
    config.inputParams = []
    #config.numJobs = 1
    
    #if os.path.exists(config.sbatch_chdir):
    #    print("Output directory {} exists".format(config.sbatch_chdir))
    #    exit()
    
    #flav = '_dnn_'         # no muel
    #flav = '_MuEl_dnn_'    # with muel
    flav  = '_'             # all
    
    cmssw = config.cmsswDir
    for i, inF in enumerate(glob.glob(os.path.join(cardDir, '*', '*.sh'))): 
        script = os.path.basename(inF)
        dir    = os.path.dirname(inF)
        m      = inF.split('/')[-2]
        
        if isTest and i!=0:
            continue

        if method != 'generatetoys-data': 
                    # H ->ZA 
            if not (script.startswith("HToZATo2L2B_gg_fusion_nb2_resolved_boosted_OSSF{}".format(flav)) or 
                    script.startswith("HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl{}".format(flav)) or 
                    script.startswith("HToZATo2L2B_gg_fusion_nb2_boosted_OSSF{}".format(flav)) or 
                    
                    script.startswith("HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF{}".format(flav)) or
                    script.startswith("HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF{}".format(flav)) or
                    script.startswith("HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF{}".format(flav)) or 
                    # nb2
                    #script.startswith("HToZATo2L2B_bb_associatedProduction_nb2_resolved_boosted_OSSF{}".format(flav)) or
                    #script.startswith("HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF{}".format(flav)) or
                    #script.startswith("HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF{}".format(flav)) or 
                    ## nb3
                    #script.startswith("HToZATo2L2B_bb_associatedProduction_nb3_resolved_boosted_OSSF{}".format(flav)) or
                    #script.startswith("HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF{}".format(flav)) or
                    #script.startswith("HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF{}".format(flav)) or 
                    ## A -> ZH
                    script.startswith("AToZHTo2L2B_gg_fusion_nb2_resolved_boosted_OSSF{}".format(flav)) or 
                    script.startswith("AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl{}".format(flav)) or 
                    script.startswith("AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF{}".format(flav)) or
                    ## 
                    script.startswith("AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF{}".format(flav)) or
                    script.startswith("AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF{}".format(flav)) or
                    script.startswith("AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF{}".format(flav)) 
                    ## nb2
                    #script.startswith("AToZHTo2L2B_bb_associatedProduction_nb2_resolved_boosted_OSSF{}".format(flav)) or
                    #script.startswith("AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF{}".format(flav)) or
                    #script.startswith("AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF{}".format(flav)) or
                    ## nb3
                    #script.startswith("AToZHTo2L2B_bb_associatedProduction_nb3_resolved_boosted_OSSF{}".format(flav)) or
                    #script.startswith("AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF{}".format(flav)) or
                    #script.startswith("AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF{}".format(flav)) 
                    ):
                continue

            #if 'resolved_boosted' in script:
            #    config.sbatch_memPerCPU = '15000'
           
           # if not m in ['MA-200.0_MH-125.0', 'MA-220.0_MH-127.0', 'MA-240.0_MH-130.0', 'MH-157.77_MA-57.85', 'MH-173.52_MA-30.0', 'MH-173.52_MA-37.34', 'MH-173.52_MA-46.48', 'MH-173.52_MA-57.85', 'MH-173.52_MA-72.01', 'MH-190.85_MA-37.34', 'MH-190.85_MA-46.48', 'MH-190.85_MA-71.28', 'MH-209.9_MA-86.79', 'MH-209.9_MA-46.48', 'MH-209.9_MA-30.0', 'MH-209.9_MA-104.53', 'MH-200.0_MA-125.0', 'MH-200.0_MA-100.0', 'MH-190.85_MA-86.78', 'MH-200.0_MA-50.0', 'MH-230.77_MA-45.88', 'MH-230.77_MA-102.72', 'MH-230.77_MA-123.89', 'MH-230.77_MA-30.0', 'MH-230.77_MA-37.1', 'MH-230.77_MA-56.73', 'MH-230.77_MA-69.78', 'MH-250.0_MA-100.0', 'MH-250.0_MA-50.0', 'MH-261.4_MA-85.1', 'MH-261.4_MA-69.66', 'MH-296.1_MA-145.93', 'MH-296.1_MA-120.82', 'MH-261.4_MA-56.73', 'MH-261.4_MA-124.53', 'MH-261.4_MA-37.1', 'MH-261.4_MA-30.0', 'MH-261.4_MA-150.5', 'MH-261.4_MA-102.99', 'MH-261.4_MA-45.88', 'MH-296.1_MA-30.0', 'MH-296.1_MA-36.79', 'MH-296.1_MA-55.33', 'MH-296.1_MA-82.4', 'MH-296.1_MA-99.9', 'MH-300.0_MA-100.0', 'MH-300.0_MA-200.0', 'MH-335.4_MA-55.33', 'MH-335.4_MA-45.12', 'MH-335.4_MA-145.06', 'MH-335.4_MA-30.0', 'MH-335.4_MA-36.79', 'MH-379.0_MA-143.08', 'MH-379.0_MA-205.76', 'MH-379.0_MA-36.63', 'MH-379.0_MA-44.72', 'MH-379.0_MA-54.59', 'MH-379.0_MA-66.57', 'MH-442.63_MA-161.81', 'MH-442.63_MA-135.44', 'MH-516.94_MA-179.35']: 
            #['MH-300.0_MA-200.0', 'MH-379.0_MA-54.59', 'MH-500.0_MA-300.0', 'MH-510.0_MA-130.0', 'MH-650.0_MA-50.0', 'MH-800.0_MA-200.0', 'MA-510.0_MH-130.0', 'MA-800.0_MH-140.0', 'MA-510.0_MH-130.0']:
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

