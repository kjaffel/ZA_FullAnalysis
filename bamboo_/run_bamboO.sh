#!/bin/bash -l

run='--distributed=driver'
#run='--maxFiles=1'
#run='--onlyprepare'              # useful to update cacheJEC!
#run='--distributed=finalize'

#yml='config/llbbtest_UL16_nanov9.yml'
#yml='config/data_fullanalysisRunIISummer20UL_18_17_16_nanov9.yml'

#output='run2Ulegay_results/unblind_stage2_full_per_chunk_fullrun2/ver0'
output='run2Ulegay_results/unblind_stage2_full_per_chunk_fullrun2/ver2'

#era='2016-preVFP' #choices : 2016-preVFP, 2016-postVFP, 2017, 2018, '' will do full run2 (if all eras are provided in the yml)
eras=('2016-preVFP' '2016-postVFP' '2017' '2018' )
do_what='analysis' #choices : 'btag' or 'analysis'

doSkim=false
doSysts=true
doEvaluate=true   # evaluate DNN 
doChunk=true

if [ "$do_what" == 'btag' ]; then
    module=' BtagEfficiencies.py:ZA_BTagEfficiencies'
else
    module=' ZAtollbb.py:NanoHtoZA'
fi

plus_args=''
if [ "$era" != '' ]; then
    output=${output}/$era
    plus_args=' --era='$era
fi

if $doSkim; then
    plus_args+=' --skim'
fi

if $doEvaluate; then
    plus_args+=' -dnn'
fi

if $doSysts; then
    plus_args+=' -s'
fi

## https://stackoverflow.com/questions/1908610/how-to-get-process-id-of-background-process
if $doChunk; then
    for chunk in $(seq 11 19); do  # me $(seq 0 9)  && sjain will do $(seq 10 19)
        yml='config/fullanalysisRunIISummer20UL_18_17_16_chunk'${chunk}'_nanov9.yml'
        for era in ${eras[*]}; do
            
            #echo 'reset ... !'
            plus_args_loop=$plus_args 
            _output=$output
            #
            _output=${output}/$era/'chunk_'${chunk}
            plus_args_loop+=' --era='$era' --chunk='$chunk
             
            # just do it once, otherwise will take lots of time!
            if [ "$run" = "--distributed=finalize" ]; then
                pushd ${_output}/infiles
                sed -i 's|root://xrootd-cms\..*\.it//|/storage/data/cms|g' *.txt
                popd
            fi
            
            echo " JOBPID=$$ Will do: bambooRun $run -m $module $yml -o ${_output} $plus_args_loop " #&> logs/logs_${era}_chunk_${chunk}.txt"
            #bambooRun $run -m $module $yml -o ${_output} $plus_args_loop & #> logs/logs_${era}_chunk_${chunk}.txt &
        done
        echo '==========================='
    done

else
    echo "Will do: bambooRun $run -m $module $yml -o ${output} $plus_args"
    bambooRun $run -m $module $yml -o ${output} $plus_args
fi

# slurm will complain for long jobs during re-submission of the failed ones,
# the followinf will break the list of long jobs instead, So proceed by running logs/redo_best.sh
if [ "$run" = "--distributed=finalize" ]; then
    find logs/*.txt -type f | xargs grep  "sbatch --array" >& logs/redo.sh
    sed -i "s/.*Resubmit with '//g" logs/redo.sh
    sed -i "s/' (and possibly additional options)*//" logs/redo.sh
    python breakLongJobs.py
fi

