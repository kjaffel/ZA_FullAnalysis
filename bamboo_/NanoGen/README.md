#ZA Full Run2 NANOGEN 
## Setup your enviroment:
```bash
# Check my aliases [all in here](https://github.com/kjaffel/ZA_FullAnalysis#environment-setup-always-) 
cms_env
voms-proxy-init --voms cms
bamboo_env
bambooenv
# In case you want to get your nanogen root files from lxplus;
# So you don't have to copy anything to ingrid-ui1
# passwd should be the same as your lxplus account
kinit -f LxplusUserName@CERN.CH
```
##How To Run?
```python
bambooRun --maxFiles=1 -m ZAgenStudies.py:NanoGenHtoZAPlotter gen_samples.yml -o test
```
## HEFT vs Loop Induced:
## 4FS vs 5FS:
