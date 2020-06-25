# H->ZA->llbb : RunII Full Analysis
- Analysis use Bamboo RDataFrame with NanoAODv5
- Know more about the FramWork here: https://cp3.irmp.ucl.ac.be/~pdavid/bamboo/index.html

# Bamboo Installation(1st time):
```
mkdir bamboodev
cd bamboodev
# make a virtualenv
source /cvmfs/sft.cern.ch/lcg/views/LCG_97python3/x86_64-centos7-gcc9-opt/setup.sh
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
```
# Environment setup (always *):
- In your ~/.bashrc add:
```
function cms_env() {
    module purge
    module load grid/grid_environment_sl6
    /cvmfs/cms.cern.ch/cmsset_default.sh
    module load crab/crab3
    module load slurm/slurm_utils
    module load cms/cmssw
}
alias bamboo_env="source /cvmfs/sft.cern.ch/lcg/views/LCG_97python3/x86_64-centos7-gcc9-opt/setup.sh"
alias bambooenv="source $HOME/bamboodev/bamboovenv/bin/activate"
```
- then every time you want to setup your bamboo enviroment:
```
cms_env
voms-proxy-init --voms cms
bamboo_env
bambooenv
```
# Update Bamboo :
```
cd bamboodev/bamboo
git checkout master
git pull upstream master
pip install --upgrade .
```
# How to run:
- I recommend to test locally first with --maxFiles=1, after you can submit to slurm with --distributed=driver

```
-s : --systematics add to your plots PSweight (FSR , ISR) , PDFs and six QCD scale variations, ele_id, ele_reco, pu, BtagWeight, DY, top ...
-v : --verbose     give you more print out for debugging 
-m : --module      your analysis script

bambooRun --distributed=driver -v -s -m ZAtollbb.py:NanoHtoZA config/choose_One_.yml -o ~/path_to_your_Output_dir/
```
- In case you want to run plotIt again (after changing few options such fill color, legend position, unable systematics, etc...)
```
plotIt -i /path_to_your_dir/ -o /path_to_your_dir/plots_{add_era: 2016, 2017, 2018} -y -e era /In_your_Output_dir/plots.yml
```
- Or --onlypost
```
bambooRun --onlypost -v -s -m ZAtollbb.py:NanoHtoZA config/choose_One_.yml -o ~/path_to_your_Output_dir/
```
