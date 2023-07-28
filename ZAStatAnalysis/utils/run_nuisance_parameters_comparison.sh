#!/bin/bash

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-87.1'
outputDir='NPs_comparasion/bb_associatedProduction/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-87.1'
outputDir='NPs_comparasion/bb_associatedProduction/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-87.1'
outputDir='NPs_comparasion/gg_fusion/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-87.1'
outputDir='NPs_comparasion/gg_fusion/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-482.85'
outputDir='NPs_comparasion/bb_associatedProduction/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-482.85'
outputDir='NPs_comparasion/bb_associatedProduction/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-482.85'
outputDir='NPs_comparasion/gg_fusion/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-482.85'
outputDir='NPs_comparasion/gg_fusion/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-411.54'
outputDir='NPs_comparasion/bb_associatedProduction/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-411.54'
outputDir='NPs_comparasion/bb_associatedProduction/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-411.54'
outputDir='NPs_comparasion/gg_fusion/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-411.54'
outputDir='NPs_comparasion/gg_fusion/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-47.37'
outputDir='NPs_comparasion/bb_associatedProduction/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-47.37'
outputDir='NPs_comparasion/bb_associatedProduction/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-47.37'
outputDir='NPs_comparasion/gg_fusion/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-47.37'
outputDir='NPs_comparasion/gg_fusion/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-55.16'
outputDir='NPs_comparasion/bb_associatedProduction/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-55.16'
outputDir='NPs_comparasion/bb_associatedProduction/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-55.16'
outputDir='NPs_comparasion/gg_fusion/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-55.16'
outputDir='NPs_comparasion/gg_fusion/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-74.8'
outputDir='NPs_comparasion/bb_associatedProduction/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-74.8'
outputDir='NPs_comparasion/bb_associatedProduction/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-74.8'
outputDir='NPs_comparasion/gg_fusion/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-74.8'
outputDir='NPs_comparasion/gg_fusion/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-664.66'
outputDir='NPs_comparasion/bb_associatedProduction/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-664.66'
outputDir='NPs_comparasion/bb_associatedProduction/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-664.66'
outputDir='NPs_comparasion/gg_fusion/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-664.66'
outputDir='NPs_comparasion/gg_fusion/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-779.83'
outputDir='NPs_comparasion/bb_associatedProduction/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-779.83'
outputDir='NPs_comparasion/bb_associatedProduction/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-779.83'
outputDir='NPs_comparasion/gg_fusion/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-779.83'
outputDir='NPs_comparasion/gg_fusion/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-64.24'
outputDir='NPs_comparasion/bb_associatedProduction/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-64.24'
outputDir='NPs_comparasion/bb_associatedProduction/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-64.24'
outputDir='NPs_comparasion/gg_fusion/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-64.24'
outputDir='NPs_comparasion/gg_fusion/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-566.51'
outputDir='NPs_comparasion/bb_associatedProduction/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-566.51'
outputDir='NPs_comparasion/bb_associatedProduction/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-566.51'
outputDir='NPs_comparasion/gg_fusion/comp_1_nb2-resolved-boosted__vs__nb2-boosted__vs__nb2-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

inputDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage2/__ver4/chunk_19/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/MH-997.14_MA-566.51'
outputDir='NPs_comparasion/gg_fusion/comp_2_nb2PLusnb3-resolved-boosted__vs__nb2PLusnb3-boosted__vs__nb2PLusnb3-resolved/'
scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'

impacts=(
)

pushd $inputDir
IFS='.json' read -a arr <<< $impacts
#echo ${impacts[@]}
python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir
popd

