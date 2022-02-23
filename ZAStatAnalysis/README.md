# ZAStatAnalysis : ULegacy -full run2 
## CombinedLimit: CC7 release CMSSW_10_2_X - recommended version
- Setting up the environment (once):
```bash
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
```
- Update to a reccomended tag - currently the reccomended tag is v8.2.0: see [release notes](https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/releases/tag/v8.2.0)

```bash
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.2.0
scramv1 b clean; scramv1 b # always make a clean build
```
- Now the repository contains a certain amount of analysis-specific code, the following scripts can be used to clone it with a sparse checkout for just the core [CombineHarvester/CombineTools](https://github.com/cms-analysis/CombineHarvester/tree/master/CombineTools) subpackage, speeding up the checkout and compile times:
- Read more about [CombineHarvester](http://cms-analysis.github.io/CombineHarvester/) framework for the production and analysis of datacards for use with the CMS combine tool. 

## Combine Tools:
This repository is a "top-level" CMSSW package, so it should be located at [$CMSSW_BASE/src/CombineHarvester](https://cms-analysis.github.io/CombineHarvester/index.html#getting-started). 
- git clone via ssh:
```bash
bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-ssh.sh)
```
- git clone via https:
```bash
bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-https.sh)
```
- make sure to run [scram]() to compile the [CombineTools]() package.
## Run ZA Statistics:
### Set-up Your CMSSW Enviroment (1st-time):
```bash
# add the following in your ~/.bashrc
function cms_env() {
    module --force purge
    module load cp3
    module load cms/cmssw
    module load grid/grid_environment_sl7
    module load crab/crab3
    module load slurm/slurm_utils
    }
# then every time you want to setup your env start with;
cms_env
cd ${CMSSW_BASE}/src
cmsenv
```
```bash
git clone -o upstream git@github.com:kjaffel/ZA_FullAnalysis.git
cd ZAStatAnalysis
source first_setup.sh
source setup_python_packages.sh

# Now compile
cd ${CMSSW_BASE}/src

scram b -j7
```
##  Prepare Shape Cards:
**Warning:** make sure that the inputs root file are normalized !
```bash
cms_env
cd ${CMSSW_BASE}/src
cmsenv
./prepareShapesAndCards.py --era -i -o --dataset --mode --method --expectSignal
```
- ``-i``/``--input`` : path to inputs prefit histograms
- **``--normalize``: normalize the inputs histograms if the given ``--inputs`` above are not !**
- ``-o``/``--output``: path to where you want to save the datacards 
- ``-p``/``--parameters``: take a list of float ntuples ``[(MH, MA)]``, by default will do all signal mass points that can be found in ``inputs/results/*.root``
- ``-v``/``--verbose``: for more printout when debugging
- ``--era`` : choices ``[2016, 2017, 2018]``
- ``--expectSignal``: ``0`` for B-Only or ``1`` for S+B hypothesis.
- ``--dataset``: if ``asimov``; ``-t -1``will produce an Asimov dataset in which statistical fluctuations are suppressed. If ``toys``; ``-t N with N > 0`` will be used instead. Combine will generate ``N toy`` datasets from the model and re-run the method once per toy.
- ``--node``: choices of nodes yo want to look at ``[DY, TT, ZA]``, the signal node by default ``ZA`` is the only relevant one.
- ``--mode``: choices of histogram you want to run combined on ``[mjj_vs_mlljj, mjj_and_mlljj, postfit, mjj, mlljj, ellipse, dnn]``
- ``--method``: choices of statistical method ``[asymptotic, hybridnew, fit, impacts, generatetoys]``
- ``--unblind``: if set to False``--run blind`` options will be added to combine commands otherwise real_data will be used instead. 
- ``--scale``: scale signal rate; the signale is usualy normalized to 1pb, this flag will scale signal process to ``BR * cross-section``.

## Collect Limits:
```python
python collectLimits.py -i output_path_of_previous_step/ --method 
```
- ``-i``/``--inputs`` : path to (ROOT) combine output file, the combined limits will be saved by default in ``args.inputs/jsons/*.json``.
- ``--method``: ``asymptotic or hybridnew`` required to collect the limits from ``higgsCombinexxxx_.AsymptoticLimits.mH125.root`` if the method is asymptotic for instance.

## Plot ZA Limits:
```python
python ZAlimits.py -p path_to/jsons/ --era
```
- ``-p``/``--jsonpath``: path to limits in jsons format which are the results of setp2.
- ``--era`` : choices ``[2016, 2017, 2018]``
- ``--unblind``: plot the observed limits.
- ``--rescale-to-za-br``: If set, limits are rescaled to the ZA branching-ratio.
- ``--numbers``: If set, show values of expected limits on top of the plot.
- ``--theory``: plot theory cross-section.
- ``--log`` : make plot in log scale.
## Optimize Binning: 
- Important notes: 
    - If you are running on ingrid-ui1, you need to run on a worker node with a more recent CPU``srun --partition=cp3 --qos=cp3 --time=0-02:00:00 --pty bash``
    - Needs python3 environment, you can use LCG [here](https://github.com/kjaffel/ZA_FullAnalysis#environment-setup-always-).
```python
python optimizeBinning.py -i -o --rebin 
```
- ``-i``/``--inputs``:
- ``-o``/``--outputs``:
- ``--era``: 
- ``--uncertainty``:
- ``--events``:
- ``-p0/--prior``: 
- --onlypost
- --plotit
- --logy 
- --sys
- --mode
- --toys
- --scale 
- --submit 
- ``--rebin``:
- ``--normalized``: 
## Trouble-Shooting:
- If you ever face Segfault in CombineHarvester::WriteDatacard(string, string) in Python[ issue-239](https://github.com/cms-analysis/CombineHarvester/issues/239) you can try with [PR-240](https://github.com/cms-analysis/CombineHarvester/pull/240), simply do:
```bash
git checkout master
git checkout -b master_with_240
git merge origin/102x-debug
```
