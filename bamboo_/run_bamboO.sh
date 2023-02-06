#!/bin/bash -l

#run='--distributed=driver'
#run='--maxFiles=1'
run='--distributed=finalize'

#yml='config/fullanalysisRunIISummer20UL_18_17_16_nanov9_chunk1_for_unblindstage1.yml'
#yml='config/fullanalysisRunIISummer20UL_18_17_16_nanov9_custom_for_unblindstage1.yml'
#yml='config/mc_fullanalysisRunIISummer20UL_18_17_16_nanov9_for_btagEffMaps.yml'
yml='config/fullanalysisRunIISummer20UL_18_17_16_nanov9_noSignal.yml'

#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext4/missing/'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext5/btagEffmaps'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext5/sanitycheck__4'
#output='llbbtests/test_new_changes__3'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__2'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__3'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__4'
#output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__5'
output='run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__6'


era='2017' #choices : 2016-preVFP, 2016-postVFP, 2017, 2018, '' will do full run2
chunk=1
do_what='analysis' #'btag' or 'analysis'

if [ "$do_what" == 'btag' ]; then
    module=' BtagEfficiencies.py:ZA_BTagEfficiencies'
else
    module=' ZAtollbb.py:NanoHtoZA'
fi

#for chunk in {{0..9}}; do 
#echo "Will do: bambooRun $run -m $module $yml -o ${output}/chunk_${chunk}/$era -s -dnn --era=$era --chunk $chunk"
#bambooRun $run -m $module $yml -o ${output}/chunk_${chunk}/$era -s -dnn --era=$era --chunk $chunk
#done

#echo "Will do: bambooRun $run -m $module $yml -o ${output}/chunk_${chunk}/ -s -dnn --chunk $chunk"
#bambooRun $run -m $module $yml -o ${output}/chunk_${chunk}/ -s -dnn --chunk $chunk

echo "Will do: bambooRun $run -m $module $yml -o ${output}/$era --era=$era"
bambooRun $run -m $module $yml -o ${output}/$era --era=$era

#echo "Will do: bambooRun $run -m $module $yml -o ${output}"
#bambooRun $run -m $module $yml -o ${output}
