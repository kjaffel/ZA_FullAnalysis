#!/bin/bash
echo "Hello Rucio Users !"
source /cvmfs/cms.cern.ch/cmsset_default.sh # cms_env
echo "setup your VOMS-PROXY !"
voms-proxy-init -voms cms -rfc -valid 192:00
source /cvmfs/cms.cern.ch/rucio/setup-py3.sh
export RUCIO_ACCOUNT=kjaffel  # Edit your CERN UserName
echo """
    =====================================================================================================    
    - You can issue the command  
        $ rucio --help  # to understand all your options. 
    - You can list your quota at all sites via the command 
        $ rucio list-account-limits $ RUCIO_ACCOUNT.
    - If you do not have quota in the right place (or enough), you should ask for a quota increase at 
    the RSE(Rucio Storage Elements) you would like to use. 
    To find out who to ask, you can query the RSE attributes to identify the accounts responsible for managing quota.
        $ rucio list-rse-attributes T2_UCL_BE
    - know more about Rucio here: https://twiki.cern.ch/twiki/bin/view/CMSPublic/Rucio
                                : https://twiki.cern.ch/twiki/bin/view/CMSPublic/RucioUserDocsContainers
    =====================================================================================================    
"""
#=======================================================================================
#  Create a User Container 
#=======================================================================================
#container='ZAsamples_ul2016_nanov8andv9'
#container='HToZATo2L2B_bbH_signals_nanov9'
#container='HToZATo2L2B_ggH_signals_nanov9'
#container='AToZHTo2L2B_ggH_signals_nanov9'

#requested_samples=()
declare -a requested_samples=($(cat requests/rucio_signalUL18.txt | tr '\n' ' '))
#=======================================================================================
# !!! The command below is a must for a first time creation of new container only !!!
#=======================================================================================
#rucio add-container user.kjaffel:/Analyses/$container/USER
#=======================================================================================
for smp in ${requested_samples[*]}; do 
    #=======================================================================================
    # ! You have enough quota:: just go ahead with the command below
    #=======================================================================================
    rucio add-rule cms:$smp 1 T2_BE_UCL
    #=======================================================================================
    # ! To be used when you don't have enouh quota; ask IT for approval and then later you can increase 
    #=======================================================================================
    #rucio add-rule --ask-approval cms:$smp 1 T2_BE_UCL
    #=======================================================================================
    # !  Add some initial datasets to the Container 
    #=======================================================================================
    #rucio attach user.kjaffel:/Analyses/$container/USER cms:$smp
done
#=======================================================================================
# ! Subscribe/Transfer the container to a site
#=======================================================================================
#rucio add-rule --account=kjaffel user.kjaffel:/Analyses/$container/USER 1 T2_BE_UCL
#=======================================================================================
# ! Check the current contents of the container 
#=======================================================================================
#rucio list-content user.kjaffel:/Analyses/$container/USER 
#=======================================================================================
# ! Check status of transfered datasets
#=======================================================================================
rucio list-rules --account=$RUCIO_ACCOUNT | grep "REPLICATING"
