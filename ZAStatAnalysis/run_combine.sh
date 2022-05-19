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
#era='fullrun2'

era='2017'      # or '2016' , '2017' , '2018', 'fullrun2'  

workDir='work__'${era/20/""}'/'
bambooDir='forcombine/ul2017__ver1/results/'
inDir='ul__combinedlimits/preapproval__12/ext__1/'$workDir
outDir='ul__combinedlimits/preapproval__12/ext__1/'$workDir

scenario='bayesian_rebin_on_S' # or  'bayesian_rebin_on_B' , 'bayesian_rebin_on_hybride', 'rebin_on_uniform50bins'
methods=('generatetoys', 'fit', 'impacts', 'asymptotic', 'pvalue', 'signal_strength')

#=============================================
# generate toys data only 
#=============================================
./prepareShapesAndCards.py --era $era -i $bambooDir -o $outDir --dataset toys --mode dnn --method generatetoys --expectSignal 0 --normalize --stat
#./run_combined_dnn_generatetoys.sh

#=============================================
# signal strength
#=============================================
#./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --dataset asimov --mode dnn --method signal_strength --expectSignal 1 --normalize
#./run_combined_dnn_signal_strength.sh

#=============================================
# pre-fit/ post-fit  
#=============================================
#./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --dataset asimov --mode dnn --method fit --expectSignal 1 --unblind --normalize
#./run_combined_dnn_fitprepost.sh

#=============================================
# pulls and impacts S+B fit
#=============================================
#./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --dataset asimov --mode dnn --method impacts --expectSignal 0 --normalize
#./run_combined_dnn_impactspulls.sh

#=============================================
# pulls and impacts S only fit 
#=============================================
#./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --dataset asimov --mode dnn --method impacts --expectSignal 1 --normalize
#./run_combined_dnn_impactspulls.sh

#=============================================
# CLs limits 
#=============================================
#./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/ -o $outDir/$scenario/ --dataset asimov --mode dnn --method asymptotic --expectSignal 1 --normalize #--verbose
#./run_combined_dnn_asymptoticlimits.sh

#python collectLimits.py -i $outDir/$scenario/ --method asymptotic --era $era
#python ZAlimits.py -p $outDir/$scenario/asymptotic-limits/jsons/dnn/ --log --era $era #&>logs/limits___$scenario.log

#=============================================
# pvalue scan : expecting signal 1
#=============================================
#./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results -o $outDir/$scenario/ --dataset asimov --mode dnn --method pvalue --expectSignal 1 --normalize
#./run_combined_dnn_pvalue.sh
#python collectPvalue.py --inputs $outDir/$scenario/

#=============================================
# full run2 combination 
#=============================================

#./prepareShapesAndCards.py --era $era -i $inDir  -o $outDir  --dataset asimov --mode dnn --method asymptotic --expectSignal 1 --normalize
#./run_combined_dnn_asymptoticlimits_run2.sh

#python collectLimits.py -i $outDir/$scenario/ --method asymptotic --era $era
#python ZAlimits.py -p $outDir/$scenario/asymptotic-limits/jsons/dnn/ --log --era $era 

#./prepareShapesAndCards.py --era $era -i $inDir  -o $outDir --dataset asimov --mode dnn --method fit --expectSignal 1 --unblind --normalize
#./run_combined_dnn_fitprepost_run2.sh
#=============================================
