import os, os.path, sys
import subprocess
import yaml
import glob

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/')
import utils as utils
logger = utils.ZAlogger(__name__)


def getTasks(bambooDir, analysisCfgs):
    tasks = []
    with open(analysisCfgs,"r") as file:
        ymlConfiguration = yaml.load(file, Loader=yaml.FullLoader)
    for sName, sConfig in ymlConfiguration["samples"].items():
        if not sConfig['era'] ==era:
            continue
        if 'type' in sConfig.keys() and sConfig['type']=='signal':
            continue # no need for signal 
        if not os.path.exists(os.path.join(bambooDir, 'results', sName+'.root')):
            tasks.append(sName)
    return tasks


def finalize():
    tasks_notfinalized =  getTasks(bambooDir, analysisCfgs)
    print( 'missing outputs :', tasks_notfinalized ) 
    
    os.chdir(outputs)
    cwd = os.getcwd()
    aProblem = False
    for tsk_name in tasks_notfinalized:
        print("Current working directory is:", cwd)
        
        outFiles = []     
        for rf in glob.glob(os.path.join(cwd, '*', f'{tsk_name}.root')): 
            outFiles.append(rf)
        
        os.chdir(bambooDir)
        haddCmd = ["hadd", "-f", os.path.join(bambooDir, "results/{}.root".format(tsk_name))]+outFiles 
        try:
            logger.debug("Merging outputs for sample {} with {}".format(tsk_name, " ".join(haddCmd)))
            subprocess.check_call(haddCmd)#, stdout=subprocess.DEVNULL) 
        except subprocess.CalledProcessError:
            logger.error("Failed to run {0}".format(" ".join(haddCmd)))
            aProblem = True
    if aProblem:
        logger.error("Something went wrong with some of your Jobs, not all tasks are finalized ! ")
        return
    else:
        logger.info("All tasks finalized")
    
    with open(os.path.join(bambooDir, 'results/README'), 'w') as outf:
        outf.write(outFiles)
        outf.write('These outputs are hadded manually, please remove and finalize again when all jobs are finished !!')

if __name__ == '__main__':
    era          = '2018'
    analysisCfgs ='../config/fullanalysisRunIISummer20UL16_17_18_nanov9.yml'
    bambooDir    ='/nfs/scratch/fynu/kjaffel/run2Ulegay_results/forHIG/ul_run2__ver19/'
    outputs      =os.path.join(bambooDir, 'batch/output')
    
    finalize()
