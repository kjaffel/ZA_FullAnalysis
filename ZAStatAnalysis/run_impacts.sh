#!/bin/bash

#dir="./Cards/ZA/ellipse/limits/"
#dir="./2016Cards.v2/mjj_and_mlljj/limits/"
#dir="./2016Cards.v4/mjj/limits/"
#dir="./2016Cards.v5/mjj/fit/"
#dir="./2016Cards.v8/ellipse/limits"
#dir="./2016Cards.ForInputsv10/ellipse/limits"
dir="./run2Cards/2016_resoBoOscan_ZAnode_ver0/dnn/limits"

cd $dir

for f in *; do
    if [[ -d $f ]]; then
    cd $f
    echo "Accessing " $f "..."
    #workspace=`find -name "HToZATo2L2B*MuMu_ElEl_MuEl_combine_workspace.root"`
    workspace=`find -name "HToZATo2L2B*MuMu_ElEl_combine_workspace.root"` # for now Only
    echo $workspace
    #combineTool.py -M Impacts -d $workspace -m 125 --rMin -20 --rMax 20 --expectSignal=0. --doInitialFit --robustFit 1 -t -1 
    #combineTool.py -M Impacts -d $workspace -m 125 --rMin -20 --rMax 20 --expectSignal=0. --robustFit 1 --doFits -t -1 --parallel 30
    combineTool.py -M Impacts -d $workspace -m 125 --rMin -20 --rMax 20 --expectSignal=0. -t -1 -o impacts__expectSignal0__doInitialFit__robustFit1_t-1.json 
    
    #combineTool.py -M Impacts -d $workspace -m 125 --rMin -20 --rMax 20 --doInitialFit --robustFit 1
    #combineTool.py -M Impacts -d $workspace -m 125 --rMin -20 --rMax 20 --robustFit 1 --doFits --parallel 30
    #combineTool.py -M Impacts -d $workspace -m 125 --rMin -20 --rMax 20 -o impacts.json
    
    plotImpacts.py -i impacts__expectSignal0__doInitialFit__robustFit1_t-1.json -o impacts
    impacts="impacts_$f.pdf"
    mv impacts.pdf $impacts
    impacts_json="impacts_$f.json"
    mv impacts.json $impacts_json
    cp $impacts ../../../../../impacts_obs_bkgOnly_unblinding_step0/
    cp $impacts_json ../../../../../impacts_obs_bkgOnly_unblinding_step0/
    cd ..
    fi
done
