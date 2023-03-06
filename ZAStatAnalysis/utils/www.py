import os
import glob
import subprocess


def run_subprocess_call(cmd):
    try:
        subprocess.call(cmd)
    except subprocess.CalledProcessError:
        print("Failed to run {0}".format(" ".join(cmd)))
    
def _mkdir_cats(m, www):
    for process in ['bb_associatedProduction', 'gg_fusion']:
        for cat in ['nb2-resolved', 'nb2PLusnb3-boosted', 'nb2PLusnb3-resolved-boosted', 'nb2PLusnb3-resolved', 'nb3-boosted', 'nb3-resolved']:
            for flav in ['ElEl', 'MuMu', 'MuEl', 'OSSF', 'OSSF_MuEl', 'split_OSSF', 'split_OSSF_MuEl', 'MuMu_ElEl', 'MuMu_ElEl_MuEl', 'MuMu_MuEl', 'ElEl_MuEl']:
                pout = os.path.join(www, m, process, cat, flav)
                os.makedirs(pout, exist_ok=True)
                _copy_results('index.php', pout)

def _copy_results(res, res_path):
    cmd = ['cp', res, res_path]
    run_subprocess_call(cmd)
    return 

def CopyResultsForEOSWeb(path, do, www):
    all_masses = []
    for p in glob.glob(os.path.join(path, 'M*')):
        m = p.split('/')[-1]
        all_masses.append(m)
    
    print( all_masses )
    for m in all_masses:
        _mkdir_cats(m, www)
        
    for p in glob.glob(os.path.join(path, 'M*')):
        m = p.split('/')[-1]
        if do =='goodness_of_fit_test':
            p = os.path.join(p, 'saturated')

        for process in ['bb_associatedProduction', 'gg_fusion']:
            for cat in ['nb2-resolved', 'nb2PLusnb3-boosted', 'nb2PLusnb3-resolved-boosted', 'nb2PLusnb3-resolved', 'nb3-boosted', 'nb3-resolved']:
                for flav in ['ElEl', 'MuMu', 'MuEl', 'OSSF', 'OSSF_MuEl', 'split_OSSF', 'split_OSSF_MuEl', 'MuMu_ElEl', 'MuMu_ElEl_MuEl', 'MuMu_MuEl', 'ElEl_MuEl']:
                    for _type in ['*.png', '*.json', '*.pdf']:
                        for res in glob.glob(os.path.join(p, _type)):
                            
                            if not cat.replace('-','_') in res:
                                continue
                            if cat == 'nb2PLusnb3-resolved' and 'boosted' in res:
                                continue
                            if not process in res:
                                continue
                            if not flav in res:
                                continue
                            
                            res_path = os.path.join(www, m, process, cat, flav)
                            _copy_results(res, res_path)


base = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/'
www  = os.path.join('www-eos-lxplus', 'hig-22-010', '__ver9')

for do, path in {
                 #'goodness_of_fit_test': 'hig-22-010/unblinding_stage1/followup1__ext11/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r', 
                 #'pulls-impacts': 'hig-22-010/unblinding_stage1/followup1__ext11/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r'
                 
                 #'goodness_of_fit_test': 'hig-22-010/unblinding_stage1/followup1__ext14/chunk_1/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r', 
                 #'pulls-impacts': 'hig-22-010/unblinding_stage1/followup1__ext14/chunk_1/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r'
                 
                 #'goodness_of_fit_test': 'hig-22-010/unblinding_stage1/followup1__ext19/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r___QCDmuRF_is_ON/',
                 #'pulls-impacts': 'hig-22-010/unblinding_stage1/followup1__ext19/chunk_1/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r___QCDmuRF_is_ON/',
                 
                 #'goodness_of_fit_test': 'hig-22-010/unblinding_stage1/followup1__ext19/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/',
                 
                 #'goodness_of_fit_test': 'hig-22-010/unblinding_stage1/followup1__ext29/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/',
                 #'pulls-impacts': 'hig-22-010/unblinding_stage1/followup1__ext29/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r',
                 
                 'goodness_of_fit_test': 'hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/',
                 'pulls-impacts': 'hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r',
                 }.items():
    
    path = os.path.join(base, path)
    CopyResultsForEOSWeb(path, do, www)
