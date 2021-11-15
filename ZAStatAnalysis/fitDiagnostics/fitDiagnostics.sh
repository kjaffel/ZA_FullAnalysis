#!/bin/bash
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/HiggsPAGPreapprovalChecks
# https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/nonstandard/#fit-parameter-uncertainties

val=${1:?"Missing arg 1 for --expectSignal => expected 1 for S+B and 0 for B-Only"}

#dir="../Cards_part0_exp_sx100_forImpacts/ZA/ellipse/limits/"
dir="../ul__combinedlimits/ul2016_cards__ver1/dnn/limits/"
cd $dir

channel="MuMu"

for f in *; do
    if [[ -d $f ]]; then
        pushd $f
        echo "Accessing " $f "..."
        #HToZATo2L2B_ElEl_dnn_ggH_resolved_MH_300_MA_50.dat
        datacard=`find -name "HToZATo2L2B_$channel*.dat"`
        echo $datacard
        output="${datacard/.dat/.txt}"
        
        fit_diagDIR='FitDiagnostics/expectSignal'$val
        if [[ ! -d "$fit_diagDIR" ]]; then
            mkdir -p $fit_diagDIR
        fi
        pwd 
        #combine -M FitDiagnostics -m 125 -t -1 --expectSignal $val --toysFrequentist --rMin -20 --rMax 20 $datacard >> "$fit_diagDIR/$output"
        combine -M FitDiagnostics -m 125 -t -1 --expectSignal $val $datacard >> "$fit_diagDIR/$output"
        python ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a fitDiagnostics.root -g plots.root >> "$fit_diagDIR/$output"
    
        popd
    fi
done
