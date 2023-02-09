#!/bin/bash -l

#=============== YOUR INPUTS ==============================
#==========================================================
mode='dnn'
#choices: 'mbb', 'mllbb'

era='2018'                     
#choices: '2016' , '2017' , '2018', 'fullrun2'  

scenario='bayesian_rebin_on_S' 
#choices: 'bayesian_rebin_on_S', 'bayesian_rebin_on_B' , 'bayesian_rebin_on_hybride', 'uniform'

do_what='impacts'
#choices: 'nll_shape', 'likelihood_fit', 'fit', 'goodness_of_fit', 'hybridnew', 'generate_toys', 'asymptotic', 'pvalue', 'impacts', 'signal_strength', 

multi_signal=false
# if this true, the cards will contain both signals but using 1 discriminator ggH -> for nb2 and bbH -> for nb3 
# this will allow you to test HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel while freezing or profiling 1 signal at the time

_2POIs_r=true 
# if this false  r_ggH +r_bbH will be combined, so you need to give a tb value

tanbeta=1.5
#choices: any value you want
# Just make sure you already run Sushi and 2HDMC, so you have the results saved in this format
# data/sushi1.7.0-xsc_tanbeta-20.0_2hdm-type2.yml

expectSignal=1
verbose=0 #Verbosity level (-1 = very quiet; 0 = quiet, 1 = verbose, 2+ = debug)
validation_datacards=true
unblind=true
normalize=true
scale=false
x_branchingratio=false

splitJECs=true
splitLep=true          # by default bbH, nb3 and boosted cat. are combined at the level of histograms, if this flag set to true -> the split will be produced too.
splitTTbar=true
splitDrellYan=false

FixbuggyFormat=false   # won't be needed soon 
rm_mix_lo_nlo_bbH_signal=true # as the name sugested won't process bbh signal samples @nlo mixed with lo, when both exist we will go for LO

submit_to_slurm=true
sbatch_time='3-24:59:00'
sbatch_memPerCPU='45000' #7000

n=1

#bambooDir='unblind_stage1_few_fullrun2/results/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext1/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext2/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext3/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext4_remove_qcd_uncer/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext5/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext6/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext8/half/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext9/do_comb_and_split/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext11/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext12/'

#bambooDir='unblind_stage1_full_per_chunk_fullrun2/chunk_'${n}'/results/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext7/chunk_'${n}'/'

bambooDir='unblind_stage1_full_per_chunk_fullrun2/ext4/chunk_'${n}'/results/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext13/chunk_'${n}'/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext14/chunk_'${n}'/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext15/chunk_'${n}'/'
#stageOut='hig-22-010/unblinding_stage1/followup1__ext16/chunk_'${n}'/'
stageOut='hig-22-010/unblinding_stage1/followup1__ext18/back_to_old_cmssw_version/chunk_'${n}'/'

#bambooDir='ul_run2__ver19/results/'
#stageOut='hig-22-010/datacards_nosplitJECs/'

#bambooDir='ul_run2__ver21_AtoZH_vs_HtoZA/results/'
#stageOut='AtoZH_vs_HtoZA/'

#bambooDir='ul_run2__ver22_AtoZH_vs_HtoZA/results/'
#stageOut='hig-22-010/AtoZH_vs_HtoZA_ver22/'

#bambooDir='ul_run2__ver20_splitJES_JER2/results/'
#(old name)stageOut='hig-22-010/jesjer_split__ver2/'
#stageOut='hig-22-010/datacards/'

#================ DO NOT CHANGE =============================
#============================================================
workDir='work__UL'${era/20/""}'/'
inDir=$stageOut$workDir
outDir=$inDir

#================ + flags  ==================================
#============================================================
if [ "$do_what" = "likelihood_fit" ]; then
    multi_signal=true
fi 


plus_args='' 
if $_2POIs_r; then
    plus_args+=' --_2POIs_r'
else
    plus_args+=' --tanbeta'
fi


if $unblind; then
    if [ "$do_what" != "generate_toys" ]; then
        plus_args+=' --unblind'
    fi
fi 

plus_args+=' --expectSignal '${expectSignal}
plus_args2=$plus_args
plus_args+=' --verbose '${verbose}
plus_args+=' --bambooDir '${bambooDir}

if $multi_signal; then
    plus_args+=' --multi_signal'
fi


if $submit_to_slurm; then
    plus_args+=' --slurm'
    plus_args+=' --sbatch_time '${sbatch_time}
    plus_args+=' --sbatch_memPerCPU '${sbatch_memPerCPU}
fi

if $normalize; then
    plus_args+=' --normalize'
fi


if $scale; then
    plus_args+=' --scale'
fi


if $splitJECs; then
    plus_args+=' --splitJECs'
fi


if $splitTTbar; then
    plus_args+=' --splitTTbar'
fi


if $splitDrellYan; then
    plus_args+=' --splitDrellYan'
fi


if $FixbuggyFormat; then
    plus_args+=' --FixbuggyFormat'
fi


if $rm_mix_lo_nlo_bbH_signal; then
    plus_args+=' --rm_mix_lo_nlo_bbH_signal'
fi


if $splitLep; then
    plus_args+=' --splitLep'
fi


if $validation_datacards; then
    plus_args+=' --validation_datacards'
fi


if $unblind; then
    if [ "$do_what" == "generate_toys" ]; then
        plus_args+=' --dataset asimov'
    fi
fi


if $x_branchingratio; then
    plus_args2+=' --rescale-to-za-br'
fi


if [ "$expectSignal"==1 ]; then
    cl='CLs'
else
    cl='CLsplusb'
fi


echo "running ${do_what} Combine with the following arguments : " ${plus_args}
echo "running ${do_what} post-processing step with the following arguments : " ${plus_args2}

#=============================================
# generate toys data only 
#=============================================
if [ "$do_what" = "generate_toys" ]; then
    ./prepareShapesAndCards.py --era $era -i $bambooDir -o $stageOut/$workDir --dataset toys --mode $mode --method generatetoys --stat $plus_args
    #./run_combine_${mode}_generatetoys.sh
fi

#=============================================
# signal strength
#=============================================
if [ "$do_what" = "signal_strength" ]; then
    ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --mode $mode --method signal_strength $plus_args
    ./run_combine_${mode}_signal_strength.sh
fi

#=============================================
# pre-fit/ post-fit  
#=============================================
if [ "$do_what" = "fit" ]; then
    #./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --mode $mode --method fit $plus_args
    #./run_combine_${mode}_fitprepost.sh

    #python utils/getSystematicsTable.py -i $outDir/$scenario/ --mode $mode $plus_args2
    python3 producePrePostFitPlots.py -i $outDir/$scenario/ --mode $mode --era $era --reshape
fi 

#=====================================================================
# pulls and impacts S(--expectSignal 1) or S+B(--expectSignal 0) fit
#=====================================================================
if [ "$do_what" = "impacts" ]; then
    ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --mode $mode --method impacts $plus_args
    #./run_combine_${mode}_impactspulls.sh
fi

#==================================================================
# CLs ( --expectSignal 1 )/CLsplusb (--expectSignal 0) limits 
#==================================================================
if [ "$do_what" = "asymptotic" ]; then
    #./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/ -o $outDir/$scenario/ --mode $mode --method asymptotic $plus_args
    #./run_combine_${mode}_asymptoticlimits.sh

    jsP=$outDir/$scenario/asymptotic-limits/$mode/jsons/
    #jsP=$outDir/$scenario/asymptotic-limits/dnn_r_xBR/jsons/
    #jsP=$outDir/$scenario/asymptotic-limits__very_good_xbr/$mode/jsons/

    #python collectLimits.py -i $outDir/$scenario/ --method asymptotic --era $era $plus_args2 
    #python ZAlimits.py --jsonpath $jsP --log --era $era $plus_args2

    #python draw2D_mH_vs_mA_withRoot.py --jsonpath $jsP --era $era $plus_args2
    #python draw2D_mH_vs_mA_scatter.py --jsonpath $jsP --era $era $plus_args2

    python draw2D_tb_vs_cba_withRoot.py --jsonpath $jsP --era $era $plus_args2 --prod bbH
    #python draw2D_tb_vs_cba_withRoot.py --jsonpath $jsP --era $era $plus_args2 --prod ggH
    
    #python draw2D_tb_vs_2hdmmass_withRoot.py --jsonpath $jsP --era $era $plus_args2 --fix mH --mass 500 
    #python draw2D_tb_vs_2hdmmass_withRoot.py --jsonpath $jsP --era $era $plus_args2 --fix mH --mass 997.14 
    #python 2hdmtbvsmass.py --jsonpath $jsP --era $era $plus_args2 --fix mH --mass 500 
fi

#============================================================
# pvalue/ Significance scan : expecting signal 1
#============================================================
if [ "$do_what" = "pvalue" ]; then
    ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results -o $outDir/$scenario/ --mode $mode --method pvalue $plus_args
    #./run_combine_${mode}_pvalue.sh

    jsP=$outDir/$scenario/pvalue-significance/$mode/jsons/

    #python collectPvalue.py --inputs $outDir/$scenario/
    #python plotSignificance.py --jsonpath $jsP --era $era --scan mA
    #python plotSignificance.py --jsonpath $jsP --era $era --scan mH

    #python plotPValue.py --input $jsP --era $era
fi

#=============================================================
# Goodness of fit 
#============================================================
if [ "$do_what" = "goodness_of_fit" ]; then
    ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results -o $outDir/$scenario/ --mode $mode --method goodness_of_fit $plus_args
    #./run_combine_${mode}_goodness_of_fit.sh
fi 

#=============================================================
# NLL shape 
#============================================================
if [ "$do_what" = "nll_shape" ]; then
    ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results -o $outDir/$scenario/ --mode $mode --method nll_shape $plus_args
    ./run_combine_${mode}_nll_shape.sh
fi 

#=============================================================
# Likelihood Fits and Scans
#============================================================
if [ "$do_what" = "likelihood_fit" ]; then
    ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results -o $outDir/$scenario/ --mode $mode --method likelihood_fit $plus_args
    #./run_combine_${mode}_likelihood_fit.sh
fi 
