#!/bin/bash
#dir="./2016Cards.ForInputsv10/ellipse/limits"
dir="./run2Cards/2016_resoBoOscan_ZAnode_ver0/dnn/limits/"

cd $dir

for f in *; do
    if [[ -d $f ]]; then
    cd $f
    echo "Accessing " $f "..."
    #workspace=`find -name "HToZATo2L2B*MuMu_ElEl_MuEl_combine_workspace.root"`
    #workspace=`find -name "HToZATo2L2B*MuMu_ElEl_combine_workspace.root"`
    #workspace=`find -name "HToZATo2L2B*ElEl_combine_workspace.root"`
    workspace=`find -name "HToZATo2L2B*MuMu_combine_workspace.root"`
    echo $workspace
    STR=$(echo $workspace | cut -d'c' -f 1)
    SUBSTR=$(echo $STR | cut -d'/' -f 2)
    echo $SUBSTR
    combineTool.py -M AsymptoticLimits -d $workspace -n $SUBSTR -m 125 
    cd ..
    fi
done
