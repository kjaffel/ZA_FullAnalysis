#!/bin/bash -l

#=============== YOUR INPUTS ==============================
#==========================================================
mode='dnn'
#choices: 'mbb', 'mllbb'

era='2017'                     
#choices: '2016' , '2017' , '2018', 'fullrun2'  

scenario='bayesian_rebin_on_S' 
#choices: 'bayesian_rebin_on_S', 'bayesian_rebin_on_B' , 'bayesian_rebin_on_hybride', 'uniform'

do_what='asymptotic'
#choices:

tanbeta=1.5
#choices: any value you want
# Just make sure you already run Sushi and 2HDMC, so you have the results saved in this format
# data/sushi1.7.0-xsc_tanbeta-20.0_2hdm-type2.yml

bambooDir='ul_run2__ver19/results/'
stageOut='ul__combinedlimits/going_for_preapproval/'

#================ DO NOT CHANGE =============================
#============================================================
workDir='work__UL'${era/20/""}'/'
inDir=$stageOut$workDir
outDir=$inDir

#===================================================================
# Junks To be removed 
# Some Cross check dnn, mbb, and mllbb unblinded and using uniform bins
#===================================================================

#bambooDir='ul_2016__ver10/ext2/results/'
#inDir='ul__combinedlimits/preapproval/work__v10-ext2/work__3/'
#outDir='ul__combinedlimits/preapproval/work__v10-ext2/work__3/'

#bambooDir='ul_run2__ver3/results/'
#inDir='ul__combinedlimits/preapproval/works__ul_run2__ver3/work__UL18/'
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver3/work__UL18/'

#bambooDir='ul_run2__ver8/results/'
#inDir='ul__combinedlimits/preapproval/works__ul_run2__ver9/work__UL16/'
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver9/work__UL16/'

#bambooDir='ul2017/work__ext1/results/'
#inDir='ul__combinedlimits/llbbtests/DYrewgtpolyfit5mjj/work__UL17/'
#outDir='ul__combinedlimits/llbbtests/DYrewgtpolyfit5mjj/work__UL17/'

#inDir='ul__combinedlimits/preapproval/works__ul_run2__ver9/'
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver9/work__fullrun2'

#bambooDir='forcombine/ul2017__ver1/results/'
#workDir='work__UL'${era/20/""}'/ext__1'
#inDir='ul__combinedlimits/preapproval__12/ext__1/'$workDir
#outDir='ul__combinedlimits/preapproval__12/ext__1/'$workDir

#bambooDir='ul_run2__ver14/results/'
#workDir='work__UL'${era/20/""}'/ext__2/'
#inDir='ul__combinedlimits/preapproval__12/'$workDir
#outDir='ul__combinedlimits/preapproval__12/'$workDir

#bambooDir='ul_run2__ver8/'
#inDir='ul__combinedlimits/preapproval/works__ul_run2__ver8/work__UL16/'
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver8/work__UL16/'

#bambooDir='ul_run2__ver14/results/'
#workDir='work__UL'${era/20/""}'/'
#inDir='ul__combinedlimits/preapproval__14/'$workDir
#outDir='ul__combinedlimits/preapproval__14/'$workDir

#bambooDir='ul_run2__ver17/results/'
#workDir='work__UL'${era/20/""}'/'
#inDir='ul__combinedlimits/preapproval__17/'$workDir
#outDir='ul__combinedlimits/preapproval__17/'$workDir


#./prepareShapesAndCards.py --era $era -i $bambooDir  -o $outDir/unblind --mode $mode --method fit --expectSignal 1 --unblind --normalize
#./run_combined_${mode}_fitprepost.sh

#./prepareShapesAndCards.py --era $era -i $bambooDir  -o $outDir/unblind --mode $mode --method impacts --unblind --normalize
#./run_combined_${mode}_impactspulls.sh

#./prepareShapesAndCards.py --era $era -i $bambooDir  -o $outDir/unblind  --mode $mode --method goodness_of_fit --unblind --normalize
#./run_combined_${mode}_goodness_of_fit.sh

#./prepareShapesAndCards.py --era $era -i $bambooDir -o $outDir/uniform  --mode $mode --method asymptotic --expectSignal 0 --unblind --normalize
#./run_combined_${mode}_asymptoticlimits.sh

#./prepareShapesAndCards.py --era $era -i $bambooDir  -o $outDir/uniform/ --mode $mode --method signal_strength --expectSignal 1 --dataset asimov --normalize
#./run_combined_${mode}_signal_strength.sh

#./prepareShapesAndCards.py --era $era -i ul__combinedlimits/preapproval__17/work__UL18/standalone_rebin/results/  -o $outDir/test --mode $mode --method impacts --unblind --normalize
#./run_combined_${mode}_impactspulls.sh

#=============================================
# generate toys data only 
#=============================================
if [ "$do_what" = "generate_toys" ]; then
    ./prepareShapesAndCards.py --era fullrun2 -i $bambooDir -o $outDir --dataset toys --mode $mode --method generatetoys --expectSignal 0 --normalize --stat
    ./run_combined_${mode}_generatetoys.sh
fi

#=============================================
# signal strength
#=============================================
if [ "$do_what" = "signal_strength" ]; then
    ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --dataset asimov --mode $mode --method signal_strength --expectSignal 1 --normalize
    ./run_combined_${mode}_signal_strength.sh
fi

#=============================================
# pre-fit/ post-fit  
#=============================================
if [ "$do_what" = "fit" ]; then
    ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --dataset asimov --mode $mode --method fit --expectSignal 1 --normalize
    ./run_combined_${mode}_fitprepost.sh

    #python3 producePrePostFitPlots.py -i $outDir/$scenario/ --mode $mode --era $era --reshape
    #python utils/getSystematicsTable.py -i $outDir/$scenario/ --mode $mode
fi 

#=====================================================================
# pulls and impacts S(--expectSignal 1)/S+B (--expectSignal 0) fit
#=====================================================================

if [ "$do_what" = "impacts" ]; then
    ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --dataset asimov --mode $mode --method impacts --expectSignal 0 --normalize
    ./run_combined_${mode}_impactspulls.sh
fi

#==================================================================
# CLs ( --expectSignal 1 )/Clsplusb (--expectSignal 0) limits 
#==================================================================
if [ "$do_what" = "asymptotic" ]; then
    ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/ -o $outDir/$scenario/ --dataset asimov --mode $mode --method asymptotic --expectSignal 0 --normalize --tanbeta $tanbeta
    ./run_combined_${mode}_asymptoticlimits.sh

    #python collectLimits.py -i $outDir/$scenario/ --method asymptotic --era $era 
    #python ZAlimits.py --jsonpath $outDir/$scenario/asymptotic-limits/jsons/$mode/ --log --era $era --rescale-to-za-br #&>logs/limits___$scenario.log

    #python draw2D_mH_vs_mA_withRoot.py --jsonpath $outDir/$scenario/asymptotic-limits/jsons/$mode/ --era $era
    #python draw2D_tb_vs_cba_withRoot.py --jsonpath $outDir/$scenario/asymptotic-limits/jsons/$mode/ --era $era --prod ggH
fi

#============================================================
# pvalue/ Significance scan : expecting signal 1
#============================================================
if [ "$do_what" = "pvalue" ]; then
    ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results -o $outDir/$scenario/ --dataset asimov --mode $mode --method pvalue --expectSignal 1 --normalize
    ./run_combined_${mode}_pvalue.sh

    #python collectPvalue.py --inputs $outDir/$scenario/
    #python plotSignificance.py --jsonpath $outDir/$scenario/pvalue-significance/$mode/jsons/ --era $era --scan mA
    #python plotSignificance.py --jsonpath $outDir/$scenario/pvalue-significance/$mode/jsons/ --era $era --scan mH

    #python plotPValue.py --input $outDir/$scenario/pvalue-significance/$mode/jsons/ --era $era
fi

#=============================================================
