#!/bin/bash -l

#=============== YOUR INPUTS ==============================
#==========================================================
mode='dnn'
#choices: 'mbb', 'mllbb'

era='fullrun2'                     
#choices: '2016' , '2016preVFP', '2016postVFP', '2017' , '2018', 'fullrun2'  

scenario='bayesian_rebin_on_S' 
#choices: 'bayesian_rebin_on_S', 'bayesian_rebin_on_B' , 'bayesian_rebin_on_hybride', 'uniform'

do_what='fit'
#choices: 'nll_shape', 'likelihood_fit', 'fit', 'goodness_of_fit', 'hybridnew', 'generate_toys', 'asymptotic', 'pvalue', 'impacts', 'signal_strength', 

post_processing=false
multi_signal=false
# if this true, the cards will contain both signals r_ggH & r_bbH, but using 1 discriminator, nb2 for ggH and nb3 for bbH
# this will allow you to test HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel while freezing or profiling 1 signal at the time
# tanbeta will be required

_2POIs_r=true 
# if this false, ggH and bbH signals will be merged in 1histogram, 
# but scalinf of the cross-section will be applied, 
# tanbeta will be required

declare -A tanbeta
tanbeta['gg']=5.
tanbeta['bb']=5.
#choices: any value you want
# Just make sure you already run Sushi and 2HDMC, so you have the results saved in this format
# data/sushi1.7.0-xsc_tanbeta-20.0_2hdm-type2.yml

expectSignal=1
verbose=0 #Verbosity level (-1 = very quiet; 0 = quiet, 1 = verbose, 2+ = debug)
validation_datacards=true
unblind=false
dataset='asimov'      
# choices: 'asimov', 'toys'  will be used if unblind ==false
normalize=true
scale=false
x_branchingratio=false

splitEraUL2016=false
splitJECs=true
splitLep=true          # by default bbH, nb3 and boosted cat. are combined at the level of histograms, if this flag set to true -> the split will be produced too.
splitTTbar=true
splitDrellYan=true

rm_mix_lo_nlo_bbH_signal=true # as the name sugested won't process bbh signal samples @nlo mixed with lo, when both exist we will go for LO

submit_to_slurm=true
sbatch_time='16:59:00'
sbatch_memPerCPU='15000'

#================ + flags  ==================================
#============================================================
plus_args='' 

if [ "$do_what" = "likelihood_fit" ]; then
    multi_signal=true
fi 
if $_2POIs_r; then
    plus_args+=' --_2POIs_r'
fi
if [[ $multi_signal || ! $_2POIs_r ]]; then
    if [  ${tanbeta['gg']} != ${tanbeta['bb']} ]; then
        echo 'This does not make any sense, tanbeta need to be the same for both processes !'
        exit 1
    fi
    #FIXME plus_args+=" --tanbeta="'{"gg":'${tanbeta['gg']}',"bb":'${tanbeta['bb']}'}'
fi
if $multi_signal; then
    plus_args+=' --multi_signal'
    _2POIs_r=true
fi

plus_args+=' --expectSignal '${expectSignal}
plus_args2=$plus_args
plus_args+=' --verbose '${verbose}

if $x_branchingratio; then
    plus_args2+=' --rescale-to-za-br'
fi
if $unblind; then
    if [ "$do_what" == "generate_toys" ]; then
        plus_args+=' --dataset asimov'
    else
        plus_args+=' --unblind'
    fi
else
    plus_args+=' --dataset asimov'
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
if $splitLep; then
    plus_args+=' --splitLep'
fi
if $splitEraUL2016; then
    plus_args+=' --splitEraUL2016'
    if [  "${era}"==2016 ]; then
        echo 'This should not happend, era=2016 while splitEraUL2016=true'
        echo 'Needed era are [ 2016preVFP, 2016postVFP]'
        exit 1
    fi
fi
if $rm_mix_lo_nlo_bbH_signal; then
    plus_args+=' --rm_mix_lo_nlo_bbH_signal'
fi
if $validation_datacards; then
    plus_args+=' --validation_datacards'
fi
if [ "$expectSignal"==1 ]; then
    cl='CLs'
else
    cl='CLsplusb'
fi

#============================================================
#============================================================
bambooDir='unblind_stage1_full_per_chunk_fullrun2/ext15/ForCombine/results/'
stageOut='hig-22-010/unblinding_stage1/followup1__ext30/splitDY__ver8/'
plus_args+=' --bambooDir '${bambooDir}

if $post_processing; then
    echo "running ${do_what} post-processing step with the following arguments : " ${plus_args2}
else
    echo "running ${do_what} Combine with the following arguments : " ${plus_args}
fi
#================ DO NOT CHANGE =============================
#============================================================
workDir='work__UL'${era/20/""}'/'
inDir=$stageOut/$workDir
outDir=$inDir

#=============================================
# generate toys data only 
#=============================================
if [ "$do_what" = "generate_toys" ]; then
    echo ./prepareShapesAndCards.py --era $era -i $bambooDir -o $stageOut/$workDir --dataset toys --mode $mode --method generatetoys --stat $plus_args
    ./prepareShapesAndCards.py --era $era -i $bambooDir -o $stageOut/$workDir --dataset toys --mode $mode --method generatetoys --stat $plus_args
    ./run_combine_${mode}_generatetoys.sh
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
    if $post_processing; then
        python3 producePrePostFitPlots.py -i $outDir/$scenario/ --mode $mode --era $era --unblind --reshape
        #python3 utils/getSystematicsTable.py -i $outDir/$scenario/ --mode $mode $plus_args2
    else
        ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --mode $mode --method fit $plus_args
        ./run_combine_${mode}_fitprepost.sh
    fi 
fi
#=====================================================================
# pulls and impacts S(--expectSignal 1) or S+B(--expectSignal 0) fit
#=====================================================================
if [ "$do_what" = "impacts" ]; then
    ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --mode $mode --method impacts $plus_args
    ./run_combine_${mode}_impactspulls.sh
    fi
#==================================================================
# CLs ( --expectSignal 1 )/CLsplusb (--expectSignal 0) limits 
#==================================================================
if [ "$do_what" = "asymptotic" ]; then
    if $post_processing; then
        jsP=$outDir/$scenario/asymptotic-limits/$mode/jsons/
        #jsP=$outDir/$scenario/asymptotic-limits/dnn_r_xBR/jsons/
        #jsP=$outDir/$scenario/asymptotic-limits__very_good_xbr/$mode/jsons/
        
        python collectLimits.py -i $outDir/$scenario/ --method asymptotic --era $era $plus_args2 
        #python ZAlimits.py --jsonpath $jsP --log --era $era $plus_args2
    
        #python draw2D_mH_vs_mA_withRoot.py --jsonpath $jsP --era $era $plus_args2
        #python draw2D_mH_vs_mA_scatter.py --jsonpath $jsP --era $era $plus_args2
    
        #python draw2D_tb_vs_cba_withRoot.py --jsonpath $jsP --era $era $plus_args2 --prod bbH
        #python draw2D_tb_vs_cba_withRoot.py --jsonpath $jsP --era $era $plus_args2 --prod ggH
        
        #python draw2D_tb_vs_2hdmmass_withRoot.py --jsonpath $jsP --era $era $plus_args2 --fix mH --mass 500 
        #python draw2D_tb_vs_2hdmmass_withRoot.py --jsonpath $jsP --era $era $plus_args2 --fix mH --mass 997.14 
        #python 2hdmtbvsmass.py --jsonpath $jsP --era $era $plus_args2 --fix mH --mass 500 
    else
        ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/ -o $outDir/$scenario/ --mode $mode --method asymptotic $plus_args
        #./run_combine_${mode}_asymptoticlimits.sh
    fi
fi
#============================================================
# pvalue/ Significance scan : expecting signal 1
#============================================================
if [ "$do_what" = "pvalue" ]; then
    if $post_processing; then
        jsP=$outDir/$scenario/pvalue-significance/$mode/jsons/

        #python collectPvalue.py --inputs $outDir/$scenario/
        
        #python plotSignificance.py --jsonpath $jsP --era $era --scan mA
        #python plotSignificance.py --jsonpath $jsP --era $era --scan mH
        
        #python plotPValue.py --input $jsP --era $era
    else
        ./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results -o $outDir/$scenario/ --mode $mode --method pvalue $plus_args
        ./run_combine_${mode}_pvalue.sh
    fi
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
    ./run_combine_${mode}_likelihood_fit.sh
fi
