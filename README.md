# H/A ->Z A/H ->llbb : RunII Full Analysis
- Analysis use Bamboo RDataFrame and works with NanoAODv``{5,7,8 and 9}``, check ``.yml`` configuration in ``bamboo_/config/`` directory to run ZA anslysis with your favourite NanoAOD version. 
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
- In your ``~/.bashrc`` add:
```bash
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
- In your ``~/.config/bamboorc```add:
```
[batch]
backend = slurm

[slurm]
sbatch_qos = cp3
sbatch_partition = cp3
sbatch_additionalOptions = --licenses=cms_storage:3, --exclude=mb-sky002
sbatch_time = 6:59:00
sbatch_memPerCPU = 7000

[das]
sitename = T2_BE_UCL
storageroot = /storage/data/cms
checklocalfiles = no
xrootdredirector = xrootd-cms.infn.it
```
## Environment Setup (Always *):
- Every time you want to setup your bamboo enviroment, simply do:
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
```
# open merge request for fat jet varaitions that you want to test
git fetch upstream merge-requests/150/head:test_fatjet_variations  
git checkout test_fatjet_variations
pip install --upgrade .
```
## How to run ?
I do recommend to test locally first with ``--maxFiles=1``,  to check that the module runs correctly in all cases before submitting to a batch system. If all right you can submit to slurm with ``--distributed=driver``. Avoid as well using ``-v/--verbose`` for slurm submission, will make your jobs slower.
- ``-s``/``--systematics`` add to your plots PSweight (FSR , ISR), PDFs and six QCD scale variations, ele_id, ele_reco, pu, BtagWeight, DY, top ...
- ``-v`` /``--verbose``: give you more print out for debugging. 
- ``-m ``/``--module``    : your analysis script.
- ``-dnn ``/``--DNN_Evaluation`` : Pass TensorFlow model and evaluate DNN output
- ``--split``: if True run2 reduced set of JES uncertainty splited by sources and JER systematic variation will be splitted between kinematics regions to decorrelate the nuisance parameters.
- ``--hlt``: Produce HLT efficiencies maps
- ``--blinded``: blinded data from 0.6 to 1 bin for the dnn output 
- ``--nanoaodversion``: EOY-latest ``v7`` or Ulegacy campaign-working version ``v8`` or the latest ``v9``
- ``--doMETT1Smear``:  This correction is a propagation of L2L3 JEC to pfMET, see [MET Type1 and Type2 corrections for more details](https://twiki.cern.ch/twiki/bin/view/CMS/METType1Type2Formulae#3_The_Type_I_correction).
- ``--dobJetEnergyRegression``:
- ``--yields``:
- ``--skim``:
- ``--backend``:

**Note**: Tensorflow does not work on ``ingrid-ui1``, you need to run on a worker node with a more recent CPU, so run as follow before ``bambooRun`` command whenever ``-dnn`` flag is set to ``True``:
```bash
srun --partition=cp3 --qos=cp3 --time=0-24:00:00 --pty bash 
# you may have to exclude these working nodes as well: 
--exclude=mb-sab[001-005,007-021,081-084,087-088,090,101-103],mb-opt[015-018,021,024-025,031,042,051-052,054,056-064,067-079,111,114-116],mb-ivy[201-208,211-212,214-217,219,220-222,224-227],mb-wes[001-002,003,005-019,021-051,053-055,057-074,076-086,251-252],mb-sky013,mb-neh[070,201-209,211-212]
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
python runSkimmer.py --process ggH --output skim_dir --submit 

# ZAtollbbSkimmer is deprecated( please use the command above) 
bambooRun --distributed=driver -sel 2Lep2bJets -reg resolved  -cat MuMu -Tag DeepFlavour -wp M -proc ggH -s -m ZAtollbbSkimmer.py:Skimedtree_NanoHtoZA config/*.yml -o ~/path_to_your_Output_dir/
```
- ``--submit``: ``driver``, ``worker`` , ``max1`` or ``onlypost`` . ``--driver`` option will submit the independent tasks to a batch scheduler (currently HTCondor and Slurm are supported) instead of running them sequentially, wait for the results to be ready, and combine them (the worker tasks will run the same module, but with ``--worker`` and the actual input and results file names as input and output arguments). ``max1`` same as ``--maxFiles=1``
- ``-o``/``--output``:  skim output dir 
- ``-p``/``--process``: ``ggH`` for gg-fusion and ``bbH`` for b-associated production 
- ``-s``/`` --systematics``: add systematics variations 
- ``--standalone``: if for some reason you need the old skimmer you can pass this flag 

## Produce 2D Efficiencies Maps for Btagging: 
```bash
bambooRun --distributed=driver -v -s -m BtagEfficiencies.py:ZA_BTagEfficiencies config/mc.yml -o outputdir
```
## Trouble-Shooting:
1. Tensorflow issues does not work on ingrid-ui1, you need to run on a worker node with a more recent CPU, e.g. with this:
```bash
srun --partition=cp3 --qos=cp3 --time=0-24:00:00 --pty bash
cms_env
!voms
bamboo_env
bambooenv
```
```bash
Traceback (most recent call last):
    File "ZAtollbb.py", line 1217, in definePlots
        ZAmodel = op.mvaEvaluator(ZAmodel_path,mvaType='Tensorflow',otherArgs=(inputs, outputs), nameHint='tf_ZAModel')
    File "/home/users/k/j/kjaffel/bamboodev/bamboovenv/lib/python3.8/site-packages/bamboo/treefunctions.py", line 916, in mvaEvaluator
        loadTensorflowC()
    File "/home/users/k/j/kjaffel/bamboodev/bamboovenv/lib/python3.8/site-packages/bamboo/root.py", line 93, in __call__
        return self.fun(**kwargs)
    File "/home/users/k/j/kjaffel/bamboodev/bamboovenv/lib/python3.8/site-packages/bamboo/root.py", line 157, in loadTensorflowC
        loader(bambooLib="BambooTensorflowC", headers="bambootensorflowc.h", includePath=incPath, dynamicPath=dynPath, libraries="tensorflow")
    File "/home/users/k/j/kjaffel/bamboodev/bamboovenv/lib/python3.8/site-packages/bamboo/root.py", line 65, in loadDependency
        loadLibrary(f"lib{lib}")
    File "/home/users/k/j/kjaffel/bamboodev/bamboovenv/lib/python3.8/site-packages/bamboo/root.py", line 34, in loadLibrary
        st = gbl.gSystem.Load(libName)
    cppyy.ll.IllegalInstruction: int TSystem::Load(const char* module, const char* entry = "", bool system = kFALSE) =>
        IllegalInstruction: illegal instruction in C++; program state was reset
    
During handling of the above exception, another exception occurred:

Traceback (most recent call last):
    File "/home/users/k/j/kjaffel/bamboodev/bamboovenv/bin/bambooRun", line 8, in <module>
        sys.exit(main())
    File "/home/users/k/j/kjaffel/bamboodev/bamboovenv/lib/python3.8/site-packages/bamboo/scripts/bambooRun.py", line 62, in main
        modInst.run()
    File "/home/users/k/j/kjaffel/bamboodev/bamboovenv/lib/python3.8/site-packages/bamboo/analysismodules.py", line 430, in run
        self.processTrees(task.inputFiles, output, sampleCfg=task.config, **task.kwargs)
    File "/home/users/k/j/kjaffel/bamboodev/bamboovenv/lib/python3.8/site-packages/bamboo/analysismodules.py", line 713, in processTrees
        self.plotList = self.definePlots(tree, noSel, sample=sample, sampleCfg=sampleCfg)
    File "ZAtollbb.py", line 1224, in definePlots
        raise RuntimeError(f'-- {ex} -- when op.mvaEvaluator model: {ZAmodel_path}.')
RuntimeError: -- int TSystem::Load(const char* module, const char* entry = "", bool system = kFALSE) =>
    IllegalInstruction: illegal instruction in C++; program state was reset -- when op.mvaEvaluator model: /home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/ul__results/work__1/keras_tf_onnx_models/all_combined_dict_343_model.pb.
```
