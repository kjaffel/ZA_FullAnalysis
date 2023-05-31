#!/bin/sh
pushd CMSSW_10_2_13/src
cms_env
cmsenv
popd
#python -m virtualenv cmssw10.2.13env   # only first time
source $HOME/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/cmssw10.2.13env/bin/activate
