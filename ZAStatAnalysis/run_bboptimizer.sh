#!/bin/bash -l

#SBATCH --job-name=pvalue
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=1500
#SBATCH -p debug -n 1
#SBATCH --array=0-104
#echo "My SLURM_ARRAY_TASK_ID: " $SLURM_ARRAY_TASK_ID

#=====================================================================
#  Junks to be removed 
#=====================================================================

#bambooDir='ul_run2__ver3/' 
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver3/work__UL18/'

#bambooDir='ul_run2__ver8/'
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver8/work__UL16/'
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver8/work__fullrun2/'
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver10/work__UL17/'
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver11/work__UL17/'

#bambooDir='ul2017/work__ext1/'
#outDir='ul__combinedlimits/llbbtests/DYrewgtpolyfit5mjj/work__UL17'

#bambooDir='forcombine/ul2017__ver1/'
#workDir='work__UL'${era/20/""}'/'
#outDir='ul__combinedlimits/preapproval__12/ext__1/'$workDir

#bambooDir='ul_run2__ver14'
#workDir='work__UL'${era/20/""}'/'
#outDir='ul__combinedlimits/preapproval__14/'$workDir

#bambooDir='ul_run2__ver17'
#workDir='work__UL'${era/20/""}'/'
#outDir='ul__combinedlimits/preapproval__17/'$workDir

#=================  YOUR INPUTS ===============================
#==============================================================

era='fullrun2'
bambooDir='ul_run2__ver19'
stageOut='ul__combinedlimits/going_for_preapproval/'

#==================== DO NOT CHANGE ===========================
#==============================================================

workDir='work__UL'${era/20/""}'/'
outDir='ul__combinedlimits/going_for_preapproval/'$workDir


#================================================================================================================================
# step1/ [ Template ] run on pseudo data : 
#       --toys or --asimov : which is the sum of the total bkg to get template for each histogram of the bayesian blocks binning 
#       these templates are saved in file xxx_template.json 
#=================================================================================================================================
#python optimizeBinning.py -i $outDir -o $outDir --rebin bayesian --era $era --mode dnn --toys --logy
#python optimizeBinning.py -i $bambooDir -o $outDir --rebin bayesian --era $era --mode dnn --asimov --logy --scale

#=================================================================================================================================
# step2/ [ LOCAL ] Now to rebin the original data with different scenarios using the json file saved above
#=================================================================================================================================
#python optimizeBinning.py -i $bambooDir -o $outDir --rebin bayesian --era $era --mode dnn --submit all --scenario S --sys
#python optimizeBinning.py -i $bambooDir -o $outDir --rebin bayesian --era $era --mode dnn --submit all --scenario B --sys
#python optimizeBinning.py -i $bambooDir -o $outDir --rebin bayesian --era $era --mode dnn --submit all --scenario hybride --sys

#=================================================================================================================================
# step2/ [ SLURM ] jobs submssion from bambooDir, 1 root file for each job 
#=================================================================================================================================
input=${2}
python optimizeBinning.py -i ${input} -o $outDir --rebin bayesian --era $era --mode dnn --submit all --scenario S --sys --job slurm
