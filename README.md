# H/A ->Z A/H ->llbb : RunII Full Analysis
- Analysis use Bamboo RDataFrame and works with NanoAODv{5,7,8 and 9}, check .yaml configuration in ``bamboo_/config/`` directory to run ZA anslysis with your favourite nanoaod version. 
- You can find more about Bamboo in [the UserGuide](https://bamboo-hep.readthedocs.io/en/latest/index.html). Also feel free to report any issue you encounter in [~bamboo](https://mattermost.web.cern.ch/cms-exp/channels/bamboo) channel on the CERN mattermost, or on [Gitlab](https://gitlab.cern.ch/cp3-cms/bamboo/-/issues).

## Bamboo Installation(1st time):
```bash
mkdir bamboodev
cd bamboodev
# make a virtualenv
source /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc10-opt/setup.sh
python -m venv bamboovenv
source bamboovenv/bin/activate
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
#To use scalefactors and weights in the new CMS JSON format, the correctionlib package should be installed with
pip install --no-binary=correctionlib correctionlib
```
## Environment Setup (Always *):
- In your ``~/.bashrc`` add:
```bash
function cms_env() {
    module purge
    module load grid/grid_environment_sl6
    /cvmfs/cms.cern.ch/cmsset_default.sh
    module load crab/crab3
    module load slurm/slurm_utils
    module load cms/cmssw
}
alias bamboo_env="source /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc10-opt/setup.sh"
alias bambooenv="source $HOME/bamboodev/bamboovenv/bin/activate"
```
- then every time you want to setup your bamboo enviroment:
```bash
cms_env
voms-proxy-init --voms cms
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
## Re-install plotIt:
```bash
cd (path to)/plotIt/build-plotit
rm CMakeCache.txt
cmake -DCMAKE_INSTALL_PREFIX=$VIRTUAL_ENV ..
make -j4 install
```
## How to run ?
I do recommend to test locally first with `--maxFiles=1`, after you can submit to slurm with `--distributed=driver`. Avoid as well using ``-v/--verbose`` for slurm submission, will make your jobs slower.
- ``-s : --systematics`` add to your plots PSweight (FSR , ISR), PDFs and six QCD scale variations, ele_id, ele_reco, pu, BtagWeight, DY, top ...
- ``-v : --verbose``     give you more print out for debugging. 
- ``-m : --module``      your analysis script.
- ``-dnn : --DNN_Evaluation`` Pass TensorFlow model and evaluate DNN output
- ``--split``: if True run2 reduced set of JES uncertainty splited by sources and JER systematic variation will be splitted between kinematics regions to decorrelate the nuisance parameters.
- ``--hlt``: Produce HLT efficiencies maps
- ``--blinded``: blinded data from 0.6 to 1 bin for the dnn output 
- ``--nanoaodversion``: EOY-latest ``v7`` or Ulegacy campaign-working version ``v8`` or the latest ``v9``
- ``--doMETT1Smear``:  This correction is a propagation of L2L3 JEC to pfMET, see [MET Type1 and Type2 corrections for more details](https://twiki.cern.ch/twiki/bin/view/CMS/METType1Type2Formulae#3_The_Type_I_correction).
- ``--dobJetEnergyRegression``:
- ``--yields``:
- ``--skim``:
- ``--backend``:

Tensorflow does not work on ``ingrid-ui1``, you need to run on a worker node with a more recent CPU, so run as follow before ``bambooRun`` command whenever ``dnn`` flag is set to ``True``:
```bash
srun --partition=cp3 --qos=cp3 --time=0-02:00:00 --pty bash
```
```bash
bambooRun --distributed=driver -v -s -m ZAtollbb.py:NanoHtoZA config/choose_One_.yml -o ~/path_to_your_Output_dir/
```
In case you want to run plotIt again (after changing few options such fill color, legend position, unable systematics, etc...)
```bash
plotIt -i /path_to_your_dir/ -o /path_to_your_dir/plots_{add_era: 2016, 2017 or 2018} -y -e era /path_to_your_Output_dir/plots.yml
```
Or simply run with ``--onlypost``as follow:
```bash
bambooRun --onlypost -v -s -m ZAtollbb.py:NanoHtoZA config/choose_One_.yml -o ~/path_to_your_Output_dir/
```
## Make Skim:
You can run ``bambooRun`` command for differnt ``--args`` or you can use ``runSkimmer.py`` to submit all of them at once.
```bash
bambooRun --distributed=driver -sel 2Lep2bJets -reg resolved  -cat MuMu -Tag DeepFlavour -wp M -proc ggH -s -m ZAtollbbSkimmer.py:Skimedtree_NanoHtoZA config/*.yml -o ~/path_to_your_Output_dir/
```
- ``-sel``/``--selections``: ``noSel``, ``OsLeptons``, ``2Lep2Jets``, ``2Lep2bJets``
- ``-reg``/``--regions``: ``resolved`` or ``boosted``
- ``-cat``/``--categories``:  ``ElEl``, ``MuMu``, ``ElMu``, ``MuEl``
- ``-proc``/``--processes``: ``ggH`` for gg-fusion and ``bbH`` for bb-associated production 
- ``-Tag``/``--taggers``: ``DeepCSV`` and `` DeepFlavour`` 
- ``-wp``/``--workingpoints``: ``L``, ``M``, ``T`` for ``DeepCSV`` tagger and only ``L``, ``M`` for DeepCSV

## Produce 2D Efficiencies Maps for Btagging: 
```bash
bambooRun --distributed=driver -v -s -m BtagEfficiencies.py:ZA_BTagEfficiencies config/mc.yml -o outputdir
```
