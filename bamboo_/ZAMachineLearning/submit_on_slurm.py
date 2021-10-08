#! /bin/env python

import copy
import os
import datetime
import sys
import glob
import logging

# Slurm configuration
from CP3SlurmUtils.Configuration import Configuration
from CP3SlurmUtils.SubmitWorker import SubmitWorker
from CP3SlurmUtils.Exceptions import CP3SlurmUtilsException

# Personal files #
import parameters

def submit_on_slurm(name,args,debug=False):
    # Check arguments #
    GPU = args.find("--GPU") != -1
    output = args.find("--output") != -1

    config = Configuration()
    config.sbatch_partition = parameters.partition
    config.sbatch_qos = parameters.QOS
    config.sbatch_chdir = parameters.main_path
    config.sbatch_time = parameters.time
    #config.sbatch_memPerCPU = parameters.mem
    config.sbatch_additionalOptions = ['-n '+str(parameters.tasks)]
    if GPU:
        config.sbatch_additionalOptions += ['--gres gpu:1','--export=NONE']
    config.inputSandboxContent = []
    config.useJobArray = True
    config.inputParamsNames = []
    config.inputParams = []
    if output:
        config.inputParamsNames += ["--verbose"]
        config.inputParams += [[""]]
    if not output:
        config.inputParamsNames += ['scan','task']

    config.payload = """ """

    if GPU:
        config.payload += "export PYTHONPATH=/root6/lib:$PYTHONPATH\n"
        config.payload += "module load cp3\n" # needed on gpu to load slurm_utils
        config.payload += "module load slurm/slurm_utils\n"
    config.payload += "python3 {script} "
    if not output:
        config.payload += "--scan ${{scan}} --task ${{task}} "
    config.payload += args

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    out_dir = parameters.path_out

    slurm_config = copy.deepcopy(config)
    slurm_working_dir = os.path.join(out_dir,'slurm',name)#+'_'+timestamp)

    slurm_config.batchScriptsDir = os.path.join(slurm_working_dir, 'scripts')
    slurm_config.inputSandboxDir = slurm_config.batchScriptsDir
    slurm_config.stageoutDir = os.path.join(slurm_working_dir, 'output')
    slurm_config.stageoutLogsDir = os.path.join(slurm_working_dir, 'logs')
    slurm_config.stageoutFiles = ["*.csv","*.zip","*.png"]

    slurm_config.payload = config.payload.format(script=os.path.join(out_dir,"ZAMachineLearning.py"))

    if not output:
        for f in glob.glob(os.path.join(parameters.main_path,'split',name,'*.pkl')):
            task = os.path.basename(f)
            slurm_config.inputParams.append([name,task])

    # Submit job!
    logging.info("Submitting job...")
    if not debug:
        submitWorker = SubmitWorker(slurm_config, submit=True, yes=True, debug=False, quiet=False)
        submitWorker()
        logging.info("Done")
    else:
        logging.debug(slurm_config.payload)
        logging.debug(slurm_config.inputParamsNames)
        logging.debug(slurm_config.inputParams)
        logging.info('... don\'t worry, jobs not sent')
