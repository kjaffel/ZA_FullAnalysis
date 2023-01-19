import os
import glob
import subprocess


path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext9/do_comb_and_split/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r"


def run_subprocess_call(cmd):
    try:
        subprocess.call(cmd)
    except subprocess.CalledProcessError:
        print("Failed to run {0}".format(" ".join(cmd)))
    
def _mkdir_cats(m):
    cmd = ['mkdir', '-p']
    for process in ['bb_associatedProduction', 'gg_fusion']:
        for cat in ['nb2-resolved', 'nb2PLusnb3-boosted', 'nb2PLusnb3-resolved-boosted', 'nb2PLusnb3-resolved', 'nb3-boosted', 'nb3-resolved']:
            pout = os.path.join('.', 'hig-22-010', '__ver2', m, process, cat)
            if not os.path.isdir(pout):
                _copy_results('index.php', pout)
                cmd +=[pout]
                run_subprocess_call(cmd)

def _copy_results(res, res_path):
    cmd = ['cp', res, res_path]
    run_subprocess_call(cmd)
    return 

def CopyResultsForEOSWeb(path):
    all_masses = []
    for p in glob.glob(os.path.join(path, 'M*')):
        m = p.split('/')[-1]
        all_masses.append(m)
    
    print( all_masses )
    for m in all_masses:
        _mkdir_cats(m)
        
    for p in glob.glob(os.path.join(path, 'M*')):
        m = p.split('/')[-1]
        p = os.path.join(p, 'saturated')

        for process in ['bb_associatedProduction', 'gg_fusion']:
            for cat in ['nb2-resolved', 'nb2PLusnb3-boosted', 'nb2PLusnb3-resolved-boosted', 'nb2PLusnb3-resolved', 'nb3-boosted', 'nb3-resolved']:
                for _type in ['*.png', '*.json', '*.pdf']:
                    for res in glob.glob(os.path.join(p, _type)):
                        
                        if not cat.replace('-','_') in res:
                            continue
                        if cat == 'nb2PLusnb3-resolved' and 'boosted' in res:
                            continue
                        if not process in res:
                            continue
                        
                        res_path = os.path.join('.', 'hig-22-010', '__ver2', m, process, cat)
                        _copy_results(res, res_path)

CopyResultsForEOSWeb(path)
