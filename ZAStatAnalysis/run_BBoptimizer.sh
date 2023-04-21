#!/bin/bash -l
#=================  YOUR INPUTS ===============================
#==============================================================

mode='dnn'        # choices : 'mjj_vs_mlljj', 'mjj_and_mlljj', 'mjj', 'mlljj', 'rho', 'dnn'
scenario='S'      # choices : 'S', 'B', 'hybride'
rebin='bayesian'  # choices : 'bayesian', 'custom', 'standalone'
submit='all'      # choices : 'all', 'test' ( this concern step2 after template are bieng created )
run_on='toys'     # choices : 'toys', 'asimov'

unblind=true
do_step1_template=true
do_step2=false
submit_to_slurm=true        # RECOMMENDED
scale_histos_before_BB=true   # for plotting: scale = xsc * BR* lumi/ sum_genEvents_weight
plot_on_log=true

onlypost=false
plotit=true

n=1

era='fullrun2' # choices: '2016' , '2016preVFP', '2016postVFP', '2017' , '2018', 'fullrun2'

bambooDir='unblind_stage1_full_per_chunk_fullrun2/ext15/ForCombine/results/'
stageOut='hig-22-010/unblinding_stage1/followup1__ext30/splitDY__ver9/'

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


if $unblind; then
    plus_args_step2+=' --unblind '
fi

if $onlypost; then
    plus_args_step2+=' --onlypost'
fi 

if $plotit; then
    plus_args_step2+=' --plotit'
fi

if [ "$run_on" = "toys" ]; then
    plus_args_step1+=' --toys '
    scale=false
    input=$outDir
else
    plus_args_step1+=' --asimov'
    plus_args_step1+=' --scale'
    input=$bambooDir
fi

if $scale_histos_before_BB; then
    plus_args_step1+=' --scale '
fi

if $plot_on_log; then
    plus_args_step1+=' --logy '
fi

#================================================================================================================================
# step1/ [ produce templates ] run on pseudo data : 
#   --toys or --asimov : which is the sum of the total bkg to get template for each histogram of the bayesian blocks binning 
#   these templates are saved in file xxx_template.json 
#=================================================================================================================================
if $do_step1_template; then
    echo "running step1 with the following arguments : " ${plus_args_step1}
    echo "optimizeBinning.py -i $input -o $outDir $plus_args_step1"
    python optimizeBinning.py -i $input -o $outDir $plus_args_step1
fi

#=================================================================================================================================
# step2/ Now let's rebin the original histograms using the json file saved above
#================================================================================================================================
if $do_step2; then
    echo "running step2 with the following arguments : " ${plus_args_step2}
    if $submit_to_slurm; then
        # jobs submssion from bambooDir, 1 root file for each job 
        echo "BB4Slurm.py -i $bambooDir -o $outDir $plus_args_step2"
        python BB4Slurm.py -i $bambooDir -o $outDir $plus_args_step2
    else
        echo "optimizeBinning.py -i $bambooDir -o $outDir $plus_args_step2 --sys --job 'local'"
        python optimizeBinning.py -i $bambooDir -o $outDir $plus_args_step2 --sys --job 'local' 
    fi
fi
