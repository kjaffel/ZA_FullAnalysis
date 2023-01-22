#!/bin/bash

dir1="../hig-22-010/jesjer_split/work__UL17/bayesian_rebin_on_S/pulls-impacts/dnn/2POIs_r/MH-500.0_MA-50.0/"
dir2="../hig-22-010/datacards/work__UL17/bayesian_rebin_on_S/pulls-impacts/dnn/2POIs_r/MH-500.0_MA-50.0/"


for file1 in $dir1*json; do
    for file2 in $dir2*json; do
        cutfile1="$(cut -d'/' -f10 <<<"$file1")"
        cutfile2="$(cut -d'/' -f10 <<<"$file2")"
        if [ "$cutfile1" == "$cutfile2" ]; then
            output="${cutfile1%?????}"
            echo $output
            plotImpacts2.py -i $file1 -i $file2 -o $output
        fi
    done
done

