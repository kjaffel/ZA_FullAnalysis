#!/bin/bash
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/HiggsPAGPreapprovalChecks
# https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/nonstandard/#fit-parameter-uncertainties

val=${1:?"Missing arg 1 : --expectSignal => expected 1 for S+B and 0 for B-Only"}
dir=${2:?"Missing arg 2 : --dir          => path_to_cards_dir/<options.method>-limits/<options.mode>/"}
mode=${3:?"Missing arg 3: --mode         => choices are [mjj_vs_mlljj, mjj_and_mlljj, postfit, mjj, mlljj, ellipse, dnn] needed for fit diagnostics 
                          and the path to dir will be :: path_to_cards_dir/fit/<options.mode>/"}

pushd $dir

fit_diagDIR='FitDiagnostics/expectSignal'$val
if [[ ! -d "$fit_diagDIR" ]]; then
    mkdir -p $fit_diagDIR
fi

pushd fit/$mode

for f in *; do
    if [[ -d $f ]]; then
        pushd $f
        echo "Accessing " $f "..."
        
        datacards=`find -name "*.dat"`
        for p in $datacards; do
            datacard=${p##*/}
            output=${datacard/.dat/.log}
            pwd 
           #combine -M FitDiagnostics -m 125 --rMin -20 --rMax 20 -t -1 --expectSignal $val $datacard --toysFrequentist >> $fit_diagDIR/$output
            combine -M FitDiagnostics -m 125 --rMin -20 --rMax 20 -t -1 --expectSignal $val $datacard >>  $CMSSW_BASE/$dir/$fit_diagDIR/$output
            python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a fitDiagnostics.root -g plots.root >>  $CMSSW_BASE/$dir/$fit_diagDIR/$output
        done
        popd
    fi
done
popd
