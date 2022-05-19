#bambooDir='ul_2016__ver10/ext2/' 

#bambooDir='ul_run2__ver3/' 
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver3/work__UL18/'

#bambooDir='ul_run2__ver8/'
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver8/work__fullrun2/'
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver8/work__UL16/'
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver10/work__UL17/'
#outDir='ul__combinedlimits/preapproval/works__ul_run2__ver11/work__UL17/'

#bambooDir='ul2017/work__ext1/'
#outDir='ul__combinedlimits/llbbtests/DYrewgtpolyfit5mjj/work__UL17'

era='2017'
workDir='work__'${era/20/""}'/'
bambooDir='forcombine/ul2017__ver1/'
outDir='ul__combinedlimits/preapproval__12/ext__1/'$workDir



# run on pseudo data : which is the sum of the total bkg: to get template for each histogram of the bayesian blocks you will use in combine
# =====================================================================
#python optimizeBinning.py -i $bambooDir -o $outDir --rebin bayesian --era $era --mode dnn --asimov --scale --logy
#python optimizeBinning.py -i $outDir -o $outDir --rebin bayesian --era $era --mode dnn --toys --logy

# Now to rebin the original data with  different scenarios
# =====================================================================
#python optimizeBinning.py -i $bambooDir -o $outDir --rebin bayesian --era $era --mode dnn --submit all --scenario B --sys
python optimizeBinning.py -i $bambooDir -o $outDir --rebin bayesian --era $era --mode dnn --submit all --scenario S --sys
#python optimizeBinning.py -i $bambooDir -o $outDir --rebin bayesian --era $era --mode dnn --submit all --scenario hybride --sys
#python optimizeBinning.py -i $bambooDir -o $outDir --rebin bayesian --era $era --mode dnn --submit all --scenario BB_hybride_good_stat --sys
