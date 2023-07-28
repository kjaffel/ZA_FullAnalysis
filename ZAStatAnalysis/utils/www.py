import os
import glob
import subprocess


def run_subprocess_call(cmd):
    try:
        print( "Processing...  {0}".format(" ".join(cmd)))
        subprocess.call(cmd)
    except subprocess.CalledProcessError:
        print("Failed to run {0}".format(" ".join(cmd)))
   

def getKey(dct,value):
    return [key for key in dct if (dct[key] == value)]


def getCats(proc, nb, region, flav):
    x='' 
    if proc.startswith('gg') and region == 'resolved' and nb=='nb2PLusnb3':
        if flav == 'OSSF': x =  4
        elif flav == 'OSSF_MuEl': x = 5
    else:
        if flav == 'OSSF': x = 6
        elif flav == 'OSSF_MuEl': x = 7
    
    flavours = {'ElEl': 'ee',
                'MuMu': 'mumu',
                'MuEl': 'muel',
                'MuMu_MuEl': 'mumu+muel',
                'ElEl_MuEl': 'ee+muel',
                'MuMu_ElEl': 'mumu+ee',
                'MuMu_ElEl_MuEl': 'mumu+ee+muel',
                'OSSF': 'OSSF',
                'OSSF_MuEl': 'OSSF+muel',
                'split_OSSF': 'mumu+ee',
                'split_OSSF_MuEl': 'mumu+ee+muel' }
    
    categories ={ 'Cat1'  : (proc, '(nb2, ee)'  , region),
                  'Cat2'  : (proc, '(nb2, mumu)', region),
                  'Cat3'  : (proc, '(nb2, muel)', region),
                  'Cat4'  : (proc, '(nb2, mumu+ee)', region),
                  'Cat5'  : (proc, '(nb2, mumu+ee+muel)', region),
                  'Cat6'  : (proc, '(nb2, OSSF)', region),
                  'Cat7'  : (proc, '(nb2, OSSF+muel)', region),
                  'Cat8'  : (proc, '(nb3, ee)'  , region),
                  'Cat9'  : (proc, '(nb3, mumu)', region),
                  'Cat10' : (proc, '(nb3, muel)', region),
                  'Cat11' : (proc, '(nb3, mumu+ee)', region),
                  'Cat12' : (proc, '(nb3, mumu+ee+muel)', region),
                  'Cat13' : (proc, '(nb3, OSSF)', region),
                  'Cat14' : (proc, '(nb3, OSSF+muel)', region),
                  'Cat15={}+13'.format(x): (proc, '(nb2PLusnb3, OSSF)', region),
                  'Cat16={}+14'.format(x): (proc, '(nb2PLusnb3, OSSF+muel)', region),
                  'Cat17=4+11': (proc, '(nb2PLusnb3, mumu+ee)', region),
                  'Cat18=5+12': (proc, '(nb2PLusnb3, mumu+ee+muel)', region),
                }

    categories_details ={ 'Cat15=4+13': (proc, '(nb2, ee+mumu)+(nb3, OSSF)', region),
                          'Cat15=6+13': (proc, '(nb2, OSSF)+(nb3, OSSF)', region),
                          'Cat16=5+14': (proc, '(nb2, ee+mumu+muel)+(nb3, OSSF+muel)', region),
                          'Cat16=7+14': (proc, '(nb2, OSSF+muel)+(nb3, OSSF+muel)', region),
                          'Cat17=4+11': (proc, '(nb2, ee+mumu)+(nb3, ee+mumu)', region),
                          'Cat18=5+12': (proc, '(nb2, ee+mumu+muel)+(nb3, ee+mumu+muel)', region) 
                          }
    v = (proc, f'({nb}, {flavours[flav]})', region)
    k = getKey(categories,v)
    #print( proc, nb, region, flav, k[0], v )
    if not k: 
        return '', None
    else:
        if nb == 'nb2PLusnb3': v = categories_details[k[0]]
        return k[0], v


def _mkdir_cats(m,  heavy, light, www, do):
    for proc, process in {f'bb{heavy}': 'bb_associatedProduction', f'gg{heavy}': 'gg_fusion'}.items():
        for cat in cats:
            for flav in flavors:
                
                nb     = cat.split('-')[0]
                if nb in ['nb2', 'nb3'] and 'split' in flav:
                    continue
                if nb == 'nb2PLusnb3' and not 'OSSF' in flav:
                    continue
                
                region = '+'.join(cat.split('-')[1:])
                prefix = getCats(proc, nb, region, flav)[0]
                pout   = os.path.join(www, m, process, cat, prefix+':'+flav, do)
                os.makedirs(pout, exist_ok=True)
                _copy_results('index.php', pout)



def _mkdir_cats_method2(m, cat, proc, flav, heavy, light, www, do):
    nb      = cat.split('-')[0]
    process = 'bb_associatedProduction' if proc.startswith('bb') else 'gg_fusion'
    region  = '+'.join(cat.split('-')[1:])
    prefix  = getCats(proc, nb, region, flav)[0]
    pout    = os.path.join(www, m, process, cat, prefix+':'+flav, do)
    os.makedirs(pout, exist_ok=True)
    _copy_results('index.php', pout)
    return 


def _copy_results(res, res_path, isdir=False):
    if isdir: cmd = ['cp', '-r', res, res_path]
    else: cmd = ['cp', res, res_path]
    run_subprocess_call(cmd)
    return 


def ComparePullsImpacts(path, output):
    with open('run_nuisance_parameters_comparison.sh', 'w+') as outf:
        outf.write('#!/bin/bash\n\n')
        for p in glob.glob(os.path.join(path, 'M*')):
            m = p.split('/')[-1]
            heavy = m.split('-')[0].replace('M','')
            light = 'A' if heavy =='H' else 'H'
            
            #if not m =='MH-500.0_MA-300.0': # just for test
            #    continue
            for proc, process in {f'bb{heavy}': 'bb_associatedProduction', f'gg{heavy}': 'gg_fusion'}.items():
                for i, listcats in enumerate([ ['nb2-resolved-boosted', 'nb2-boosted', 'nb2-resolved'],
                                               ['nb2PLusnb3-resolved-boosted', 'nb2PLusnb3-boosted', 'nb2PLusnb3-resolved'], 
                                               #['nb2PLusnb3-boosted', 'nb2-boosted', 'nb3-boosted'], 
                                               #['nb2PLusnb3-resolved', 'nb2-resolved', 'nb3-resolved'], 
                                               #['nb2PLusnb3-resolved-boosted', 'nb2-boosted', 'nb3-boosted', 'nb2-resolved', 'nb3-resolved']
                                               ] ): 
                    
                    listjsons = []
                    for cat in listcats:
                        for flav in flavors:
                            for res in glob.glob(os.path.join(p, '*.json')):
                                
                                jsFile = res.split('/')[-1]
                                reco = cat.replace('-','_')
                                if not f'{process}_{reco}_{flav}_dnn' in res:
                                    continue
                                nb       = cat.split('-')[0] 
                                region   = '+'.join(cat.split('-')[1:])
                                prefix, name   = getCats(proc, nb, region, flav)
                                listjsons.append("'{}:'".format(', '.join(name))+jsFile)

                    outputDir= os.path.join('NPs_comparasion', process, 'comp_{}_{}/'.format(i+1, '__vs__'.join(listcats)) )
                    outf.write(f"inputDir='{p}'\n")
                    outf.write(f"outputDir='{outputDir}'\n")
                    outf.write("scriptDir='/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils'\n")
                   
                    outf.write('\n')
                    outf.write("impacts=(\n")
                    outf.write("{}".format(" \n".join(listjsons)))
                    outf.write(')\n')
                    outf.write('\n')
                    
                    outf.write('pushd $inputDir\n')
                    outf.write("IFS='.json' read -a arr <<< $impacts\n")
                    outf.write("#echo ${impacts[@]}\n")
                    outf.write('python $scriptDir/plot_nuisance_pull_comparison.py -i "${impacts[@]}" -o $outputDir\n')
                    outf.write('popd\n')
                    
                    outf.write('\n')
    return


def CopyResultsForEOSWeb(path, do, www):
    for p in glob.glob(os.path.join(path, 'M*')):
        print( p )
        m     = p.split('/')[-1]
        heavy = m.split('-')[0].replace('M','')
        light = 'A' if heavy =='H' else 'H'
        
        if do =='goodness_of_fit':
            p = os.path.join(p, 'saturated')
        
        if do == 'pulls_and_impacts': _endwith = 'dnn'
        elif do == 'goodness_of_fit': _endwith = 'M'
        
        for proc, process in {f'bb{heavy}': 'bb_associatedProduction', f'gg{heavy}': 'gg_fusion'}.items():
            """
            if do == 'pulls_and_impacts':
                for dest in glob.glob(os.path.join(p, 'NPs_comparasion', process, '*')):
                    comp = dest.split('/')[-1]
                    dest_path = os.path.join(www, m, process, comp)
                    _copy_results(dest, dest_path, isdir=True)
            """
            for cat in cats:
                nb  = cat.split('-')[0] 
                for flav in flavors:
                    for _type in ['*.png', '*.json', '*.pdf']:
                        
                        if do == 'pre-Fit_and_post-Fit':
                            for fit_type in ['fit_s', 'fit_b']:
                                for plt_path in glob.glob(os.path.join(p, f"plotIt_{process}_{cat.replace('-','_')}_{flav}", fit_type, "reshaped",  _type)):
                                    print( plt_path )    
                                    region    = '+'.join(cat.split('-')[1:])
                                    prefix    = getCats(proc, nb, region, flav)[0]
                                    plt       = plt_path.split('/')[-1]
                                    newplt    = plt.replace('dnn_scores', f"dnn_{proc}_{m.replace('-','_')}_{cat.replace('-','_')}_{flav}_{fit_type}")
                                    dest_path = os.path.join(www, m, process, cat, prefix+':'+flav, do, newplt)
                                    _mkdir_cats_method2(m,  cat, proc, flav, heavy, light, www, do)          
                                    _copy_results(plt_path, dest_path)
                        else: 
                            for res in glob.glob(os.path.join(p, _type)):
                                if not f"{process}_{cat.replace('-','_')}_{flav}_{_endwith}" in res:
                                    continue
                                
                                region   = '+'.join(cat.split('-')[1:])
                                prefix   = getCats(proc, nb, region, flav)[0]
                                res_path = os.path.join(www, m, process, cat, prefix+':'+flav, do)
                                _mkdir_cats_method2(m,  cat, proc, flav, heavy, light, www, do)          
                                _copy_results(res, res_path)

if __name__ == '__main__':

    base = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/'
    #www  = os.path.join('www-eos-lxplus', 'hig-22-010', 'unblinding_stage2/__ver1')
    #www  = os.path.join('www-eos-lxplus', 'hig-22-010', 'unblinding_stage2/__ver2')
    #www  = os.path.join('www-eos-lxplus', 'hig-22-010', 'unblinding_stage2/__ver3')
    www  = os.path.join('www-eos-lxplus', 'hig-22-010', 'unblinding_stage2/__ver4')
    
    cats    = ['nb2-resolved', 'nb2-boosted', 'nb3-resolved', 'nb2-resolved-boosted', 'nb3-boosted', 'nb2PLusnb3-resolved', 'nb2PLusnb3-boosted', 'nb2PLusnb3-resolved-boosted']
    flavors = ['ElEl', 'MuMu', 'MuEl', 'OSSF', 'OSSF_MuEl', 'split_OSSF', 'split_OSSF_MuEl', 'MuMu_ElEl', 'MuMu_ElEl_MuEl', 'MuMu_MuEl', 'ElEl_MuEl']
    
    done_per_chunk = True

    for do, subdir in {
                     #'goodness_of_fit_test': 'hig-22-010/unblinding_stage1/followup1__ext11/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r', 
                     #'pulls-impacts': 'hig-22-010/unblinding_stage1/followup1__ext11/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r'
                     #'goodness_of_fit_test': 'hig-22-010/unblinding_stage1/followup1__ext14/chunk_1/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r', 
                     #'pulls-impacts': 'hig-22-010/unblinding_stage1/followup1__ext14/chunk_1/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r'
                     #'goodness_of_fit_test': 'hig-22-010/unblinding_stage1/followup1__ext19/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r___QCDmuRF_is_ON/',
                     #'pulls-impacts': 'hig-22-010/unblinding_stage1/followup1__ext19/chunk_1/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r___QCDmuRF_is_ON/',
                     #'goodness_of_fit_test': 'hig-22-010/unblinding_stage1/followup1__ext19/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/',
                     #'goodness_of_fit_test': 'hig-22-010/unblinding_stage1/followup1__ext29/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/',
                     #'pulls_and_impacts': 'hig-22-010/unblinding_stage1/followup1__ext29/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r',
                     #'goodness_of_fit': 'hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/',
                     #'pulls_and_impacts': 'hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r',
                     #'pre-Fit_and_post-Fit': 'hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/fit/dnn/2POIs_r', 
                     #'pre-Fit_and_post-Fit': 'hig-22-010/unblinding_stage1/followup1__ext30/splitDY__ver2/work__ULfullrun2/bayesian_rebin_on_S/fit/dnn/2POIs_r', 
                     #'goodness_of_fit': 'hig-22-010/unblinding_stage1/followup1__ext30/splitDY/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/',
                     
                     #'pre-Fit_and_post-Fit': 'hig-22-010/unblinding_stage2/__ver1/',
                     #'goodness_of_fit': 'hig-22-010/unblinding_stage2/__ver1/',
                     'pulls_and_impacts': 'hig-22-010/unblinding_stage2/__ver1/',
                     
                     #'pre-Fit_and_post-Fit': 'hig-22-010/unblinding_stage2/__ver2/',
                     #'goodness_of_fit': 'hig-22-010/unblinding_stage2/__ver2/',
                     
                     
                     #'pre-Fit_and_post-Fit': 'hig-22-010/unblinding_stage2/__ver4/',
                     #'pulls_and_impacts': 'hig-22-010/unblinding_stage2/__ver4/',
                     #'goodness_of_fit': 'hig-22-010/unblinding_stage2/__ver4/',
                     #'pre-Fit_and_post-Fit': 'hig-22-010/unblinding_stage1/followup1__ext30/splitDY__ver8/work__ULfullrun2/bayesian_rebin_on_S/fit/dnn/2POIs_r',
                     }.items():
        
        if done_per_chunk:
            for n in range(20):
                if do == 'goodness_of_fit': dir_per_chunk = f'chunk_{n}/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/'
                elif do == 'pre-Fit_and_post-Fit': dir_per_chunk = f'chunk_{n}/work__ULfullrun2/bayesian_rebin_on_S/fit/dnn/2POIs_r/'
                elif do == 'pulls_and_impacts': dir_per_chunk = f'chunk_{n}/work__ULfullrun2/bayesian_rebin_on_S/pulls-impacts/dnn/CLs/2POIs_r/'
                
                path = os.path.join(base, subdir, dir_per_chunk)
                #if do == 'pulls_and_impacts':
                #    ComparePullsImpacts(path, www)
                #    run_subprocess_call(["bash", "run_nuisance_parameters_comparison.sh"])
                CopyResultsForEOSWeb(path, do, www)
        else:
            path = os.path.join(base, subdir)
            print( path )
            if do == 'pulls_and_impacts':
                ComparePullsImpacts(path, www)
            CopyResultsForEOSWeb(path, do, www)
