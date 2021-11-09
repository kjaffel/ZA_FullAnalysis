# ZA-Analysis- CombinedLimit: CC7 release CMSSW_10_2_X - recommended version
- Setting up the environment (once):
```bash
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
```
- Update to a reccomended tag - currently the reccomended tag is v8.1.0: see [release notes](https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/releases/tag/v8.1.0)

```bash
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.1.0
scramv1 b clean; scramv1 b # always make a clean build
```

- Now the repository contains a certain amount of analysis-specific code, the following scripts can be used to clone it with a sparse checkout for just the core [CombineHarvester/CombineTools](https://github.com/cms-analysis/CombineHarvester/tree/master/CombineTools) subpackage, speeding up the checkout and compile times:
Read more about [CombineHarvester](http://cms-analysis.github.io/CombineHarvester/)framework for the production and analysis of datacards for use with the CMS combine tool. 

# Combine Tools:
This repository is a "top-level" CMSSW package, so it should be located at [$CMSSW_BASE/src/CombineHarvester](). 
- git clone via ssh:
```bash
bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-ssh.sh)
```
- git clone via https:
```bash
bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-https.sh)
```
- make sure to run [scram]() to compile the [CombineTools]() package.

- If you ever face Segfault in CombineHarvester::WriteDatacard(string, string) in Python[issue-239](https://github.com/cms-analysis/CombineHarvester/issues/239)you can try with [PR-240](https://github.com/cms-analysis/CombineHarvester/pull/240) do:
```bash
git checkout master
git checkout -b master_with_240
git merge origin/102x-debug
```
# ZAStatAnalysis:
```bash
git clone -o upstream -b Moriond2018 git@github.com:cp3-llbb/ZAStatAnalysis.git
cd ZAStatAnalysis
source first_setup.sh
source setup_python_packages.sh

# Now compile
cd ${CMSSW_BASE}/src

scram b -j7
```
# Running the limits:
- First start by setting up your CMSSW enviroment 
```bash
cms_env
cd ${CMSSW_BASE}/src
cmsenv
# add the following in your ~/.bashrc
function cms_env() {
    module --force purge
    module load cp3
    module load grid/grid_environment_sl7
    /cvmfs/cms.cern.ch/cmsset_default.sh
    module load crab/crab3
    module load slurm/slurm_utils
    module load cms/cmssw
    }
```
1.  Prepare shape cards to run combine:
```python
./prepareShapesAndCards.py --era -i -o --blind --dataset 
```
**Warning:** make sure that the inputs root file are normalized !
- ``-i``/``--input`` : path to inputs prrefit histograms
- ``-o``/``--output``: path to where you want to save the datacards 
- ``-p``/``--parameters``: 
- ``-v``/``--verbose``: for more printout when debugging
- ``--era`` : choices ``[2016, 2017, 2018]``
- ``--scale``:
- ``--node``: choices of nodes yo want to look at ``[DY, TT, ZA]``, the signal node ``ZA`` is the only relevant one.
- ``--mode``: choices of histogram you want to run combined on ``[mjj_vs_mlljj, mjj_and_mlljj, postfit, mjj, mlljj, ellipse, dnn]``
- ``--method``: choices of statistical method [asymptotic, hybridnew, fit]
- ``--blind``: 
- ``--signal-strength``:
- ``--ellipses-mumu-file``:
2. Collect limits:
```python
python collectLimits.py -i 
```
The combined limits in jsons format will be saved by default in ``args.inputs/jsons/*.json``.

3. Plot the limits: 
```python
python ZAlimits.py -p path_to/jsons/ --era
```
- ``-p``/``--jsonpath``: path to limits in jsons format which are the results of setp2.
- ``--era`` : choices ``[2016, 2017, 2018]``
- ``--unblind``: pass if you want to have a look to the observe limits
