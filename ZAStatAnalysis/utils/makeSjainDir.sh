#!/bin/bash                                                                                                         

mine='.'
stageOut='ver3'

eras=('_UL18' '_UL17' '_UL16') ## _UL16preVFP _UL16postVFP
processes=('bb_associatedProduction'  'gg_fusion')

ymls=`find $mine -name "*.yml"`
echo $ymls

for era in ${eras[*]}; do 
    workDir=$stageOut'/work_'$era'/bayesian_rebin_on_S/results/'
    if [ ! -d $workDir ]; then
        mkdir -p $workDir
        echo 'create ' $workDir
    fi
    home=$(pwd)
    
    pushd $workDir
    for proc in ${processes[*]}; do
        if [ ! -d $proc ]; then
            mkdir -p $proc
        fi
        roots=`find $home/$mine/work__ULfullrun2/bayesian_rebin_on_S/results/$proc -name "*$era*.root"`
        #echo  $roots
        
        for rFile in ${roots[*]}; do
            cp $rFile $proc
        done
    done
    popd
done

for cfg in $ymls; do
    cp $cfg $stageOut
done
