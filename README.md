# 2HDM H/A →  Z( → ll) A/H ( → bb) search: ULegcay Full RunII Analysis (nanoAOD working version is 9) :
- Analysis use Bamboo RDataFrame and works with NanoAODv``{5, 7, 8, and 9}``, check ``.yml`` configuration in ``bamboo_/config/`` directory to run ZA anslysis with your favourite NanoAOD version. 
- You can find more about Bamboo in [the UserGuide](https://bamboo-hep.readthedocs.io/en/latest/index.html). Also feel free to report any issue you encounter in [~bamboo](https://mattermost.web.cern.ch/cms-exp/channels/bamboo) channel on the CERN mattermost, or on [Gitlab](https://gitlab.cern.ch/cp3-cms/bamboo/-/issues).

## Bamboo Installation (1st time):
```bash
mkdir bamboodev
cd bamboodev

# make a virtualenv
source /cvmfs/sft.cern.ch/lcg/views/LCG_101/x86_64-centos7-gcc10-opt/setup.sh
python -m venv bamboovenv101
source bamboovenv101/bin/activate

# clone and install bamboo
git clone -o upstream https://gitlab.cern.ch/cp3-cms/bamboo.git
pip install ./bamboo

# clone and install plotIt
git clone -o upstream https://github.com/cp3-llbb/plotIt.git
mkdir build-plotit
cd build-plotit
cmake -DCMAKE_INSTALL_PREFIX=$VIRTUAL_ENV ../plotIt
make -j2 install
cd -

# The last two commands; < pip install ./bamboo > and < make -j2 install > 
# need to be run again, every time you upgrade your LCG working version! 
 
# To use scalefactors and weights in the new CMS JSON format, the correctionlib package should be installed with
# you can ignore torch and sphinx pip errors !
pip install --no-binary=correctionlib correctionlib

# To use the calculators modules for jet and MET corrections and systematic variations
# Please use Tags: 0.1.0 at the moment  
pip install git+https://gitlab.cern.ch/cp3-cms/CMSJMECalculators.git@0.1.0

# To update the JER and JEC from the database: https://github.com/cms-jet
# but I recommend using ``--onlyprepare --maxFiles=1`` arguments when running bamboo for the first time and/or updating your JEC/JER files
checkCMSJMEDatabaseCaches --cachedir cacheJEC/
```
- Let's make things more simpler, in your ``~/.bashrc`` you can add:
```bash
# only for cp3 users working on ingrid-ui1 cluster
function cms_env() {
    module --force purge
    module load cp3
    module load cms/cmssw
    module load grid/grid_environment_sl7
    module load crab/crab3
    module load slurm/slurm_utils
}
alias bamboo_env="source /cvmfs/sft.cern.ch/lcg/views/LCG_101/x86_64-centos7-gcc10-opt/setup.sh"
alias bambooenv="source $HOME/bamboodev/bamboovenv101/bin/activate"
```
- And, in your ``~/.config/bamboorc`` add:
```
[batch]
backend = slurm

[slurm]
sbatch_qos = cp3
sbatch_partition = cp3
sbatch_additionalOptions = --licenses=cms_storage:3
sbatch_time = 6:59:00
sbatch_memPerCPU = 7000

[das]
sitename = T2_BE_UCL
storageroot = /storage/data/cms
checklocalfiles = True
xrootdredirector = xrootd-cms.infn.it
```
## Environment Setup (Always *):
- Every time you want to setup your bamboo enviroment, what you simply need to do:
```bash
cms_env
voms-proxy-init -voms cms -rfc -valid 192:00
bamboo_env
bambooenv
```
## Update Bamboo :
```bash
cd bamboodev/bamboo
git checkout master
git pull upstream master
pip install --upgrade . 
# if the previous did not work try : 
# python -m pip install --upgrade .
```
## Re-install plotIt :
```bash
cd (path to)/plotItclone/
mkdir build-plotit
cd build-plotit
cmake -DCMAKE_INSTALL_PREFIX=$VIRTUAL_ENV (path to)/plotItclone
make -j2 install
cd -
```
## Test a PR:
```bash
git fetch upstream merge-requests/150/head:test_mr-150 
git checkout test_mr-150
pip install --upgrade .
```
## How to run H/A →  Z( → ll) A/H ( → bb) full run 2 analysis ?
I do recommend to test locally first with ``--maxFiles=1``,  to check that the module runs correctly in all cases before submitting to a batch system. If all right you can submit to slurm with ``--distributed=driver``. Avoid as well using ``-v/--verbose`` for slurm submission, will make your jobs slower.

- ``-m ``/``--module``: your analysis script.
- ``-s``/``--systematics``: add to your plots PSweight (FSR , ISR), PDFs and six QCD scale variations, ele_id, ele_reco, pu, BtagWeight, DY, top ...
- ``-y``/``--yields``: add Yields Histograms: not recomended when turning on the systematics uncertainties, jobs may run out of memory very quickly!
- ``-v`` /``--verbose``: give you more print out for debugging. 
- ``--chunk``: because the signal mass points are too many ( ~ 400 ) and when trying to evaluate the DNN model with all systematics the jobs become too heavy/long. I decided to split these points on 20 chunks.  
- ``-dnn ``/``--DNN_Evaluation`` : Pass TensorFlow model and evaluate DNN output
- ``--hlt``: Produce HLT efficiencies maps
- ``--blinded``: blinded data from 0.6 to 1 bin for the DNN output score
- ``--nanoaodversion``: End-Of-Year the latest is ``v7`` or ULegacy campaign-working version is``v8`` or the latest one is ``v9``, see [Release notes](https://cms-nanoaod-integration.web.cern.ch/autoDoc/)
- ``--backend``: ``dataframe (default)`` or ``lazy`` or ``compile`` for debug mode
- ``--doMETT1Smear``: This correction is a propagation of L2L3 JEC to pfMET, see [MET Type1 and Type2 corrections for more details](https://twiki.cern.ch/twiki/bin/view/CMS/METType1Type2Formulae#3_The_Type_I_correction).
- ``--dobJetEnergyRegression``: apply b jets energy regression to improve the bjets mass resolution
- ``--splitJER``: breakup into 6 nuisance parameters per year (correlated among all jets in all events per year, but uncorrelated across years), useful for analysis that are sensitive to JER, i.e. analyses that are able to constrain the single JER nuisance parameter per year w.r.t. their assigned uncertainty
- ``--jes``: Run 2 reduced set of JES uncertainty splited by sources or use total

```bash
bambooRun --maxFiles=1 -m ZAtollbb.py:NanoHtoZA config/fullanalysisRunIISummer20UL_18_17_16_chunk1_nanov9.yml -o test/2018/chunk_1  -dnn -s --era=2018 --chunk=1
```
## Make Skim:
- ``--skim``: this argument will skip control plots and do only skimmed trees to save in the output file.
```bash
bambooRun --maxFiles=1 -m ZAtollbb.py:NanoHtoZA config/fullanalysisRunIISummer20UL_18_17_16_nanov9.yml -o test_full_skim --skim
```
## Produce 2D Efficiencies Maps for Btagging: 
```bash
bambooRun --distributed=driver -m BtagEfficiencies.py:ZA_BTagEfficiencies config/<mc.yml> -o <output_path>
```
## Trouble-Shooting:
- To run on a worker node with a more recent CPU
```bash
srun --partition=cp3 --qos=cp3 --time=0-24:00:00 --pty bash 
```
- In case you want to run [plotIt](https://cp3-llbb.github.io/plotit/) again (after changing few options such fill color, legend position, unable systematics, etc...)
```bash
plotIt -i <output_path> -o <output_path>/plots_<era> -y -e era <output_path>/plots.yml
```
- For post-processing use ``--onlypost``:
```bash
bambooRun --onlypost -m ZAtollbb.py:NanoHtoZA config/<_.yml> -o <output_path>
```
