#!/bin/bash -l
#=================  YOUR INPUTS ===============================
#==============================================================

mode='dnn'        # choices : 'mjj_vs_mlljj', 'mjj_and_mlljj', 'mjj', 'mlljj', 'rho', 'dnn'
scenario='S'      # choices : 'S', 'B', 'hybride'
rebin='bayesian'  # choices : 'bayesian', 'custom', 'standalone'
submit='all'      # choices : 'all', 'test'
run_on='toys'     # choices : 'toys', 'asimov'
normalize_histograms=true
plot_on_log=true
submit_to_slurm=true

era='fullrun2'
bambooDir='unblind_stage1_few_fullrun2/results/'
stageOut='hig-22-010/unblinding_stage1/'

#bambooDir='ul_run2__ver22_AtoZH_vs_HtoZA/results/'
#stageOut='hig-22-010/AtoZH_vs_HtoZA_ver22/'

#bambooDir='ul_run2__ver21_AtoZH_vs_HtoZA/results/'
#stageOut='AtoZH_vs_HtoZA/'

#bambooDir='ul_run2__ver19/results/'
#stageOut='hig-22-010/datacards/'

#bambooDir='ul_run2__ver20_splitJES_JER2/results/'
#stageOut='hig-22-010/jesjer_split/'

#bambooDir='ul_run2__ver20_splitJES_JER2/results/'
#stageOut='hig-22-010/jesjer_split__ver2/'

#================ DO NOT CHANGE =============================
#============================================================

workDir='work__UL'${era/20/""}'/'
inDir=$stageOut$workDir
outDir=$inDir

#================ + flags  ==================================
#============================================================

plus_args_step1=''
plus_args_step1+=' --rebin '${rebin}
plus_args_step1+=' --era '${era}
plus_args_step1+=' --mode '${mode}

plus_args_step2=$plus_args_step1
plus_args_step2+=' --submit '${submit}
plus_args_step2+=' --scenario '${scenario}

if [ "$run_on" = "toys" ]; then
    plus_args_step1+=' --toys '
    scale=false
    input=$outDir
else
    plus_args_step1+=' --asimov'
    plus_args_step1+=' --scale'
    input=$bambooDir

fi

if $normalize_histograms; then
    plus_args_step1+=' --scale '
fi

if $plot_on_log; then
    plus_args_step1+=' --logy '
fi

echo "running step1 with the following arguments : " ${plus_args_step1}
echo "running step2 with the following arguments : " ${plus_args_step2}
#================================================================================================================================
# step1/ [ produce templates ] run on pseudo data : 
#   --toys or --asimov : which is the sum of the total bkg to get template for each histogram of the bayesian blocks binning 
#   these templates are saved in file xxx_template.json 
#=================================================================================================================================
python optimizeBinning.py -i $input -o $outDir $plus_args_step1

#=================================================================================================================================
# step2/ Now let's rebin the original histograms using the json file saved above
#================================================================================================================================
if $submit_to_slurm; then
    # jobs submssion from bambooDir, 1 root file for each job 
    python BB4Slurm.py -i $bambooDir -o $outDir $plus_args_step2
else
    python optimizeBinning.py -i $bambooDir -o $outDir $plus_args_step2 --sys --job 'local' 
fi
