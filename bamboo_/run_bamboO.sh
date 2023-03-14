#!/bin/bash -l

run='--distributed=driver'
#run='--maxFiles=1'
#run='--distributed=finalize'

#yml='config/fullanalysisRunIISummer20UL_18_17_16_nanov9_chunk1_for_unblindstage1.yml'
#yml='config/fullanalysisRunIISummer20UL_18_17_16_nanov9_custom_for_unblindstage1.yml'
#yml='config/mc_fullanalysisRunIISummer20UL_18_17_16_nanov9_for_btagEffMaps.yml'
#yml='config/fullanalysisRunIISummer20UL_18_17_16_nanov9_noSignal.yml'
#yml='config/fullanalysisRunIISummer20UL_18_17_16_nanov9_FewSignals.yml'
#yml='config/fullanalysisRunIISummer20UL_18_17_16_nanov9_for_skim.yml'
#yml='config/llbbtest_UL16_nanov9.yml'
#yml='config/fullanalysisRunIISummer20UL_18_17_16_nanov9_for_dy_ttbar_split.yml'
#yml='config/data_fullanalysisRunIISummer20UL_18_17_16_nanov9.yml'

#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext4/missing/'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext5/btagEffmaps'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext5/sanitycheck__4'
#output='llbbtests/test_new_changes__3'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__2'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__3'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__4'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__5'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__6'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__7'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__8'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__9'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__10/btagEffmaps'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__10/forcombine'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__11'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext7/forcombine/'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext7/skim/'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext8/fix_pre_postVFP/'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext9/fix_pre_postVFP/'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext11'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext12'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext13'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext14'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext15'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext17/data/'
output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext19'

era='' #choices : 2016-preVFP, 2016-postVFP, 2017, 2018, '' will do full run2 (if all eras are provided in the yml)
eras=('2016-preVFP' '2016-postVFP' '2017' '2018' )
do_what='analysis' #choices : 'btag' or 'analysis'

doSkim=false
doSysts=true
doEvaluate=true
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


if $doChunk; then
    for chunk in $(seq 10 19); do
        yml='config/fullanalysisRunIISummer20UL_18_17_16_chunk'${chunk}'_nanov9.yml'
        for era in ${eras[*]}; do
            
            #echo 'reset ... !'
            plus_args_loop=$plus_args 
            _output=$output
            #
            _output=${output}/$era/'chunk_'${chunk}
            plus_args_loop+=' --era='$era' --chunk='$chunk
        
            echo "Will do: bambooRun $run -m $module $yml -o ${_output} $plus_args_loop"
            bambooRun $run -m $module $yml -o ${_output} $plus_args_loop &
        done
        echo '==========================='
    done
fi
