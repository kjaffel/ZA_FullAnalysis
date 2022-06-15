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
## Optimize Binning: 
- Commands for the Bayesian Blocks method can be found in ``run_bboptimizer.sh``
```python
python optimizeBinning.py -i $bambooDir -o $outDir --rebin bayesian --era $era --mode dnn --asimov --scale --logy
```
- ``-i``/``--inputs``    : Bamboo results dir 
- ``-o``/``--outputs``   : Path to the output dir of the new rebinned histogram. 
- ``--era``              : Choices ``['2016', '2017', '2018', 'fullrun2']``
- ``--scale``            : Re-create the input histograms scaled to`` scale = lumi * xsc / sumGenEvts`` and ``scale *= BR`` in case of signal.  
- ``--rebin``            : Choices ``['custom', 'standalone', 'bayesian']``.
- ``--scenario```        : Choices ``['hybride', 'S', 'B']``.
- ``-p0``/``--prior``    : False positive probability betwee 0 and 1 which is the relative frequency with which the algorithm falsely reports detection of change-point in data with no signal present. 
- ``--toys``/``--asimov``:
- ``--sys``              : Rebin ssytematic histograms as well.
- ``--submit``           : Choices ``['all','test']`` first will rebin all histogram found in the input files, second weill do only a test. Useful for debugging.
### For plotting: 
- ``--onlypost``         : Do just plotting. 
- ``--plotit``           : Do plots after rebining.
- ``--logy``             : log scale for plotit.
- ``--mode``             : Choices ``['mjj_vs_mlljj', 'mjj_and_mlljj', 'mjj', 'mlljj', 'rho', 'dnn']``.
- ``--normalized``       : normalize histogram for plotting. 
### For Custom rebinning: 
- ``--uncertainty``      : max stat. uncertainty needed in each bin.
- ``--events``           : max entries in each bin.

##  Prepare DataCards and how to run combine:
```bash
cms_env
cd ${CMSSW_BASE}/src
cmsenv
```
- Have a look about the available commands written in ``run_combine.sh``ii
bash run_combine.sh
###1. Generate toys data only: 
```python
./prepareShapesAndCards.py --era $era -i $bambooDir -o $outDir --dataset toys --mode dnn --method generatetoys --expectSignal 0 --normalize --stat
```
###2. Pulls and impacts:
```python
./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/  -o $outDir/$scenario/ --dataset asimov --mode dnn --method fit --expectSignal 1 --unblind --normalize
```
###3. CLs limits:
```python
./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results/ -o $outDir/$scenario/ --dataset asimov --mode dnn --method asymptotic --expectSignal 1 --normalize #--verbose
./run_combined_dnn_asymptoticlimits.sh
```
###4. P-value/Significane:
```python
./prepareShapesAndCards.py --era $era -i $inDir/$scenario/results -o $outDir/$scenario/ --dataset asimov --mode dnn --method pvalue --expectSignal 1 --normalize
./run_combined_dnn_pvalue.sh
python collectPvalue.py --inputs $outDir/$scenario/
```
###Details about the available options:
- ``-i``/``--input``  : Path to inputs prefit histograms
- ``-o``/``--output`` : Path to the output datacards to be saved.
- ``--era``           : Choices ``['2016', '2017', '2018', 'fullrun2']``.
- ``--dataset``       : if ``asimov``; 
- **``--normalize``   : Normalize the inputs histograms  lumi x xsc / sumGenEvts if the given ``--inputs`` are not !**
- ``--expectSignal``  : ``0`` for B-Only or ``1`` for S+B hypothesis.
                            ``-t -1``will produce an Asimov dataset in which statistical fluctuations are suppressed. 
                        elif ``toys``; 
                            ``-t N with N > 0`` will be used instead. Combine will generate ``N toy`` datasets from the model and re-run the method once per toy.
- ``--node``          : Choices of nodes yo want to look at ``[DY, TT, ZA]``, the signal node by default ``ZA`` is the only relevant one.
- ``--mode``          : Choices of histogram you want to run combined on ``['mjj_vs_mlljj', 'mjj_and_mlljj', 'mjj', 'mlljj', 'ellipse', 'dnn']``.
- ``--method``        : Choices of statistical method ``['asymptotic', 'hybridnew', 'fit', 'impacts', 'generatetoys', 'signal_strength', 'pvalue', 'goodness_of_fit']``.
- ``--unblind``       : If set to False``--run blind`` options will be added to all combine commands otherwise real_data will be used instead. 
- ``--slurm``         : Submit to slurm for long jobs. Supported for pullls and impacts
- ``-v``/``--verbose``: For more printout when debugging in combine.

## Collect Limits:
```python
python collectLimits.py -i output_path_of_previous_step/ --method 
```
- ``-i``/``--inputs`` : Path to (ROOT) combine output file, the combined limits will be saved by default in ``args.inputs/jsons/*.json``.
- ``--method``        : ``asymptotic or hybridnew`` required to collect the limits from ``higgsCombinexxxx_.AsymptoticLimits.mH125.root`` if the method is asymptotic for instance.

## Plot ZA Limits:
```python
python ZAlimits.py -p path_to_dir/jsons/ --era
```
- ``-p``/``--jsonpath`` : path to limits in jsons format which are the results of setp2.
- ``--era``             : Choices ``['2016', '2017', '2018', 'fullrun2']``.
- ``--unblind``         : Plot the observed limits.
- ``--rescale-to-za-br``: If set, limits are rescaled to the ZA branching-ratio.
- ``--theory``          : Plot 2HDM signal theory cross-section.
- ``--log``             : Make plot in log scale.

## Trouble-Shooting:
- If you ever face Segfault in CombineHarvester::WriteDatacard(string, string) in Python[ issue-239](https://github.com/cms-analysis/CombineHarvester/issues/239) you can try with [PR-240](https://github.com/cms-analysis/CombineHarvester/pull/240), simply do:
```bash
git checkout master
git checkout -b master_with_240
git merge origin/102x-debug
```
