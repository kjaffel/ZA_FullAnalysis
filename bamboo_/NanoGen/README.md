# ZA Full Run2 NANOGEN:
## Setup your enviroment:
- Check my aliases [all in here](https://github.com/kjaffel/ZA_FullAnalysis#environment-setup-always-) 
```bash
cms_env
voms-proxy-init --voms cms
bamboo_env
bambooenv
# In case you want to get your nanogen root files from lxplus;
# So you don't have to copy anything to ingrid-ui1
# passwd should be the same as your lxplus account
kinit -f UserName@CERN.CH
```
## How To Run?
```python
bambooRun -m ZAgenStudies.py:NanoGenHtoZAPlotter configs/gen_2samples.yml -o test
```
