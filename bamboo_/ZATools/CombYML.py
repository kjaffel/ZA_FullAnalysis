import os, os.path, sys
import yaml
import shutil

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/')
import Constants as Constants


#path = '../run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext4/chunk_1/'
#path = '../run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__1'
path = '../run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__3'
eras = ['2016-preVFP', '2016-postVFP', '2017', '2018']

shutil.copy(os.path.join(path,'2016-preVFP', 'plots.yml'), os.path.join(path, 'plots.yml'))

lumi    = {}
run2Yml = {}
for e in eras:
    lumi[e] = Constants.getLuminosity(e)
    run2Yml = os.path.join( path, e, 'plots.yml')

run2data = {}
alleras = ['2016-preVFP', '2016-postVFP', '2017', '2018', 'fullrun2']
for e in alleras:
    preffix = '' if e=='fullrun2' else  e
    with open ( os.path.join(path, preffix, 'plots.yml'), 'r' ) as outf:
        run2data[e]=yaml.safe_load(outf)
    
run2data['fullrun2']['configuration']['eras']= eras
run2data['fullrun2']['configuration']['luminosity'] = lumi

run2data['fullrun2']['files']={}
for e in eras:
    run2data['fullrun2']['files'].update(run2data[e]['files'])

with open(os.path.join(path, 'plots.yml'), 'w+') as yaml_file:
    yaml.dump(run2data['fullrun2'], yaml_file, default_flow_style=False)
