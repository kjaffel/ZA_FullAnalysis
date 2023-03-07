#!/bin/bash

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-379.0_MA-54.59'
outputDir='NPs_comparasion/bbH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-379.0_MA-54.59'
outputDir='NPs_comparasion/bbH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-379.0_MA-54.59'
outputDir='NPs_comparasion/bbH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-379.0_MA-54.59'
outputDir='NPs_comparasion/ggH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-379.0_MA-54.59'
outputDir='NPs_comparasion/ggH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-379.0_MA-54.59'
outputDir='NPs_comparasion/ggH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_379.0_MA_54.59_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_379.0_MA_54.59_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-510.0_MA-130.0'
outputDir='NPs_comparasion/bbH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-510.0_MA-130.0'
outputDir='NPs_comparasion/bbH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-510.0_MA-130.0'
outputDir='NPs_comparasion/bbH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-510.0_MA-130.0'
outputDir='NPs_comparasion/ggH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-510.0_MA-130.0'
outputDir='NPs_comparasion/ggH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-510.0_MA-130.0'
outputDir='NPs_comparasion/ggH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_510.0_MA_130.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_510.0_MA_130.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-717.96_MA-577.65'
outputDir='NPs_comparasion/bbH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-717.96_MA-577.65'
outputDir='NPs_comparasion/bbH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-717.96_MA-577.65'
outputDir='NPs_comparasion/bbH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-717.96_MA-577.65'
outputDir='NPs_comparasion/ggH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-717.96_MA-577.65'
outputDir='NPs_comparasion/ggH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-717.96_MA-577.65'
outputDir='NPs_comparasion/ggH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_717.96_MA_577.65_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_717.96_MA_577.65_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-300.0_MA-200.0'
outputDir='NPs_comparasion/bbH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-300.0_MA-200.0'
outputDir='NPs_comparasion/bbH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-300.0_MA-200.0'
outputDir='NPs_comparasion/bbH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-300.0_MA-200.0'
outputDir='NPs_comparasion/ggH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-300.0_MA-200.0'
outputDir='NPs_comparasion/ggH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-300.0_MA-200.0'
outputDir='NPs_comparasion/ggH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_300.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_300.0_MA_200.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-800.0_MA-200.0'
outputDir='NPs_comparasion/bbH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-800.0_MA-200.0'
outputDir='NPs_comparasion/bbH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-800.0_MA-200.0'
outputDir='NPs_comparasion/bbH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-800.0_MA-200.0'
outputDir='NPs_comparasion/ggH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-800.0_MA-200.0'
outputDir='NPs_comparasion/ggH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-800.0_MA-200.0'
outputDir='NPs_comparasion/ggH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_800.0_MA_200.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_200.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-800.0_MH-140.0'
outputDir='NPs_comparasion/bbA/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbA, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, mumu+ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, mumu+ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-800.0_MH-140.0'
outputDir='NPs_comparasion/bbA/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbA, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, mumu+ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, mumu+ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-800.0_MH-140.0'
outputDir='NPs_comparasion/bbA/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbA, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, mumu+ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, mumu+ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, mumu+ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb2, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, mumu+ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'bbA, (nb3, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-800.0_MH-140.0'
outputDir='NPs_comparasion/ggA/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggA, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, mumu+ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, mumu+ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-800.0_MH-140.0'
outputDir='NPs_comparasion/ggA/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggA, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, mumu+ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, OSSF), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, mumu+ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-800.0_MH-140.0'
outputDir='NPs_comparasion/ggA/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggA, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, mumu+ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, mumu+ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, mumu+ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb2, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, OSSF), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, mumu+ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MA_800.0_MH_140.0_realdataset.json 
'ggA, (nb3, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MA_800.0_MH_140.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-300.0'
outputDir='NPs_comparasion/bbH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
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

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-300.0'
outputDir='NPs_comparasion/bbH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
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

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-300.0'
outputDir='NPs_comparasion/bbH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
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

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-300.0'
outputDir='NPs_comparasion/ggH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
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

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-300.0'
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

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-300.0'
outputDir='NPs_comparasion/ggH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_500.0_MA_300.0_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_500.0_MA_300.0_realdataset.json 
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

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-250.0'
outputDir='NPs_comparasion/bbH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-250.0'
outputDir='NPs_comparasion/bbH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-250.0'
outputDir='NPs_comparasion/bbH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-250.0'
outputDir='NPs_comparasion/ggH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-250.0'
outputDir='NPs_comparasion/ggH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-500.0_MA-250.0'
outputDir='NPs_comparasion/ggH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_500.0_MA_250.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_500.0_MA_250.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-510.0_MH-130.0'
outputDir='NPs_comparasion/bbA/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbA, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, mumu+ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, mumu+ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-510.0_MH-130.0'
outputDir='NPs_comparasion/bbA/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbA, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, mumu+ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, mumu+ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-510.0_MH-130.0'
outputDir='NPs_comparasion/bbA/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbA, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, mumu+ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, mumu+ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, mumu+ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb2, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, mumu+ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'bbA, (nb3, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-510.0_MH-130.0'
outputDir='NPs_comparasion/ggA/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggA, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, mumu+ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, mumu+ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-510.0_MH-130.0'
outputDir='NPs_comparasion/ggA/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggA, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, mumu+ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, OSSF), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, mumu+ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-510.0_MH-130.0'
outputDir='NPs_comparasion/ggA/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggA, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, mumu+ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, mumu+ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, mumu+ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb2, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, OSSF), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, mumu+ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MA_510.0_MH_130.0_realdataset.json 
'ggA, (nb3, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MA_510.0_MH_130.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-650.0_MA-50.0'
outputDir='NPs_comparasion/bbH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-650.0_MA-50.0'
outputDir='NPs_comparasion/bbH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-650.0_MA-50.0'
outputDir='NPs_comparasion/bbH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-650.0_MA-50.0'
outputDir='NPs_comparasion/ggH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-650.0_MA-50.0'
outputDir='NPs_comparasion/ggH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-650.0_MA-50.0'
outputDir='NPs_comparasion/ggH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_650.0_MA_50.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_650.0_MA_50.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-516.94_MA-78.52'
outputDir='NPs_comparasion/bbH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-516.94_MA-78.52'
outputDir='NPs_comparasion/bbH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-516.94_MA-78.52'
outputDir='NPs_comparasion/bbH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'bbH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-516.94_MA-78.52'
outputDir='NPs_comparasion/ggH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-516.94_MA-78.52'
outputDir='NPs_comparasion/ggH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-516.94_MA-78.52'
outputDir='NPs_comparasion/ggH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_516.94_MA_78.52_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_516.94_MA_78.52_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-800.0_MA-140.0'
outputDir='NPs_comparasion/bbH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-800.0_MA-140.0'
outputDir='NPs_comparasion/bbH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-800.0_MA-140.0'
outputDir='NPs_comparasion/bbH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-800.0_MA-140.0'
outputDir='NPs_comparasion/ggH/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-800.0_MA-140.0'
outputDir='NPs_comparasion/ggH/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-800.0_MA-140.0'
outputDir='NPs_comparasion/ggH/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggH, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__HToZATo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, mumu), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, OSSF), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, OSSF+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, mumu+ee), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), boosted:'impacts__HToZATo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb2, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, mumu), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, OSSF), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, OSSF+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, mumu+ee), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MH_800.0_MA_140.0_realdataset.json 
'ggH, (nb3, mumu+ee+muel), resolved:'impacts__HToZATo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MH_800.0_MA_140.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-500.0_MH-250.0'
outputDir='NPs_comparasion/bbA/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbA, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, mumu+ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, mumu+ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-500.0_MH-250.0'
outputDir='NPs_comparasion/bbA/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbA, (nb2, OSSF)+(nb3, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_split_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, mumu+ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, mumu+ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-500.0_MH-250.0'
outputDir='NPs_comparasion/bbA/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'bbA, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, OSSF+muel)+(nb3, OSSF+muel), resolved+boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, mumu+ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_boosted_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, mumu), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, OSSF), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, mumu+ee), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_boosted_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, mumu+ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb2, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb2_resolved_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, mumu), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, OSSF), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, mumu+ee), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'bbA, (nb3, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_bb_associatedProduction_nb3_resolved_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-500.0_MH-250.0'
outputDir='NPs_comparasion/ggA/comp_0/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggA, (nb2, OSSF)+(nb3, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, OSSF+muel)+(nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_boosted_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, ee+mumu)+(nb3, ee+mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_boosted_split_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, mumu+ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, mumu+ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-500.0_MH-250.0'
outputDir='NPs_comparasion/ggA/comp_1/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggA, (nb2, ee+mumu)+(nb3, OSSF), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, ee+mumu+muel)+(nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, ee+mumu)+(nb3, ee+mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_split_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, mumu+ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, OSSF), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, mumu+ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MA-500.0_MH-250.0'
outputDir='NPs_comparasion/ggA/comp_2/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
'ggA, (nb2, OSSF)+(nb3, OSSF), resolved+boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, ee+mumu)+(nb3, ee+mumu), resolved+boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, ee+mumu+muel)+(nb3, ee+mumu+muel), resolved+boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2PLusnb3_resolved_boosted_split_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, mumu+ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb2_boosted_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, mumu), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, OSSF), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, OSSF+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, mumu+ee), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, mumu+ee+muel), boosted:'impacts__AToZHTo2L2B_gg_fusion_nb3_boosted_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, mumu+ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb2, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb2_resolved_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, mumu), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, OSSF), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_OSSF_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, OSSF+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_OSSF_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, mumu+ee), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_dnn_MA_500.0_MH_250.0_realdataset.json 
'ggA, (nb3, mumu+ee+muel), resolved:'impacts__AToZHTo2L2B_gg_fusion_nb3_resolved_MuMu_ElEl_MuEl_dnn_MA_500.0_MH_250.0_realdataset.json)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

