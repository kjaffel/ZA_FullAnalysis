#!/bin/bash

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext29/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-300.0'
outputDir='NPs_comparasion/bbH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext29/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-300.0'
outputDir='NPs_comparasion/bbH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext29/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-300.0'
outputDir='NPs_comparasion/bbH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext29/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-300.0'
outputDir='NPs_comparasion/ggH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext29/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-300.0'
outputDir='NPs_comparasion/ggH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext29/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-300.0'
outputDir='NPs_comparasion/ggH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

