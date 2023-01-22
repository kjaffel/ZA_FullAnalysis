import glob 
import json
import os, os.path, sys



def print_table(_res, LatexF, heavy, light, m_heavy, m_light):
    
    # we need this to restore our sys.stdout later on
    org_stdout = sys.stdout
    # we open a file
    f = open(LatexF, "w+")
    # we redirect standard out to the file
    sys.stdout = f
    
    print(R"% Please add the following required packages to your document preamble:")
    print(R"% \usepackage{multirow}")
    print(R"% \usepackage{graphicx}")
    print(R"% \usepackage[table,xcdraw]{xcolor}")
    print(R"\begin{table}[]")
    print(R"\caption{}")
    print(R"\label{tab:my-table}")
    print(R"\resizebox{\textwidth}{!}{%")
    print(R"\begin{tabular}{|ll|cc|cc|}")
    print(R"\hline")
    print(R"     \multicolumn{2}{|c|}{{\begin{tabular}[c]{@{}c@{}}Saturated GOF, p-value \\ ($m_{%s}$, $m_{%s}$) = (%s, %s) GeV\end{tabular}}} & \multicolumn{2}{c|}{gg%s}                & \multicolumn{2}{c|}{bb%s}                \\ \cline{3-6} "%(
        heavy, light, m_heavy, m_light, heavy, heavy))
    print(R"     \multicolumn{2}{|c|}{}                                                                                                               & \multicolumn{1}{c|}{resolved} & boosted & \multicolumn{1}{c|}{resolved} & boosted \\ \hline")
    
    # nb2 
    print(R"     \multicolumn{1}{|l|}{{nb2}}                      & 1. ee                                                              & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
        _res['nb2']['gg{}'.format(heavy)]['resolved']['ElEl'], _res['nb2']['gg{}'.format(heavy)]['boosted']['ElEl'], 
        _res['nb2']['bb{}'.format(heavy)]['resolved']['ElEl'], _res['nb2']['bb{}'.format(heavy)]['boosted']['ElEl'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          & 2. $\mu\mu$                                                        & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
        _res['nb2']['gg{}'.format(heavy)]['resolved']['MuMu'], _res['nb2']['gg{}'.format(heavy)]['boosted']['MuMu'], 
        _res['nb2']['bb{}'.format(heavy)]['resolved']['MuMu'], _res['nb2']['bb{}'.format(heavy)]['boosted']['MuMu'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          & 3. $\mu e$                                                         & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
        _res['nb2']['gg{}'.format(heavy)]['resolved']['MuEl'], _res['nb2']['gg{}'.format(heavy)]['boosted']['MuEl'], 
        _res['nb2']['bb{}'.format(heavy)]['resolved']['MuEl'], _res['nb2']['bb{}'.format(heavy)]['boosted']['MuEl'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          & 4. $\mu\mu +ee$                                                    & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
        _res['nb2']['gg{}'.format(heavy)]['resolved']['MuMu_ElEl'], _res['nb2']['gg{}'.format(heavy)]['boosted']['MuMu_ElEl'], 
        _res['nb2']['bb{}'.format(heavy)]['resolved']['MuMu_ElEl'], _res['nb2']['bb{}'.format(heavy)]['boosted']['MuMu_ElEl'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          & 5. $\mu\mu +ee +\mu e$                                             & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
        _res['nb2']['gg{}'.format(heavy)]['resolved']['MuMu_ElEl_MuEl'], _res['nb2']['gg{}'.format(heavy)]['boosted']['MuMu_ElEl_MuEl'], 
        _res['nb2']['bb{}'.format(heavy)]['resolved']['MuMu_ElEl_MuEl'], _res['nb2']['bb{}'.format(heavy)]['boosted']['MuMu_ElEl_MuEl'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          & 6. OSSF                                                            & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
        _res['nb2']['gg{}'.format(heavy)]['resolved']['OSSF'], _res['nb2']['gg{}'.format(heavy)]['boosted']['OSSF'], 
        _res['nb2']['bb{}'.format(heavy)]['resolved']['OSSF'], _res['nb2']['bb{}'.format(heavy)]['boosted']['OSSF'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          & 7. OSSF + $\mu e$                                                  & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \hline"%(
        _res['nb2']['gg{}'.format(heavy)]['resolved']['OSSF_MuEl'], _res['nb2']['gg{}'.format(heavy)]['boosted']['OSSF_MuEl'], 
        _res['nb2']['bb{}'.format(heavy)]['resolved']['OSSF_MuEl'], _res['nb2']['bb{}'.format(heavy)]['boosted']['OSSF_MuEl'] ))
        
    # nb3 
    print(R"     \multicolumn{1}{|l|}{{nb3}}                      & 8. ee                                                                             & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
        _res['nb3']['gg{}'.format(heavy)]['resolved']['ElEl'], _res['nb3']['gg{}'.format(heavy)]['boosted']['ElEl'], 
        _res['nb3']['bb{}'.format(heavy)]['resolved']['ElEl'], _res['nb3']['bb{}'.format(heavy)]['boosted']['ElEl'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          & 9. $\mu\mu$                                                        & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
        _res['nb3']['gg{}'.format(heavy)]['resolved']['MuMu'], _res['nb3']['gg{}'.format(heavy)]['boosted']['MuMu'], 
        _res['nb3']['bb{}'.format(heavy)]['resolved']['MuMu'], _res['nb3']['bb{}'.format(heavy)]['boosted']['MuMu'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          & 10. $\mu e$                                                        & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
        _res['nb3']['gg{}'.format(heavy)]['resolved']['MuEl'], _res['nb3']['gg{}'.format(heavy)]['boosted']['MuEl'], 
        _res['nb3']['bb{}'.format(heavy)]['resolved']['MuEl'], _res['nb3']['bb{}'.format(heavy)]['boosted']['MuEl'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          & 11. $\mu\mu +ee$                                                   & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
        _res['nb3']['gg{}'.format(heavy)]['resolved']['MuMu_ElEl'], _res['nb3']['gg{}'.format(heavy)]['boosted']['MuMu_ElEl'], 
        _res['nb3']['bb{}'.format(heavy)]['resolved']['MuMu_ElEl'], _res['nb3']['bb{}'.format(heavy)]['boosted']['MuMu_ElEl'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          & 12. $\mu\mu +ee +\mu e$                                            & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
        _res['nb3']['gg{}'.format(heavy)]['resolved']['MuMu_ElEl_MuEl'], _res['nb3']['gg{}'.format(heavy)]['boosted']['MuMu_ElEl_MuEl'], 
        _res['nb3']['bb{}'.format(heavy)]['resolved']['MuMu_ElEl_MuEl'], _res['nb3']['bb{}'.format(heavy)]['boosted']['MuMu_ElEl_MuEl'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          & 13. OSSF                                                           & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
        _res['nb3']['gg{}'.format(heavy)]['resolved']['OSSF'], _res['nb3']['gg{}'.format(heavy)]['boosted']['OSSF'], 
        _res['nb3']['bb{}'.format(heavy)]['resolved']['OSSF'], _res['nb3']['bb{}'.format(heavy)]['boosted']['OSSF'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          & 14. OSSF + $\mu e$                                                 & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \hline"%(
        _res['nb3']['gg{}'.format(heavy)]['resolved']['OSSF_MuEl'], _res['nb3']['gg{}'.format(heavy)]['boosted']['OSSF_MuEl'], 
        _res['nb3']['bb{}'.format(heavy)]['resolved']['OSSF_MuEl'], _res['nb3']['bb{}'.format(heavy)]['boosted']['OSSF_MuEl'] ))
    
    # nb2 +nb3
    print(R"     \multicolumn{1}{|l|}{{nb2+nb3}}                  & {15. OSSF  (4 +13)}                                 & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}      & %s       \\ \cline{3-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved']['OSSF'], _res['nb2PLusnb3']['gg{}'.format(heavy)]['boosted']['OSSF'], 
        _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved']['OSSF'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['boosted']['OSSF'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          &                                                                    & \multicolumn{2}{c|}{%s}                  & \multicolumn{2}{c|}{%s}                  \\ \cline{2-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved_boosted']['OSSF'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved_boosted']['OSSF'] ))
    
    print(R"     \multicolumn{1}{|l|}{}                                          & {16. OSSF +$\mu e$ ( 5 +14)}                        & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{3-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved']['OSSF_MuEl'], _res['nb2PLusnb3']['gg{}'.format(heavy)]['boosted']['OSSF_MuEl'], 
        _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved']['OSSF_MuEl'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['boosted']['OSSF_MuEl'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          &                                                                    & \multicolumn{2}{c|}{%s}                  & \multicolumn{2}{c|}{%s}                  \\ \cline{2-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved_boosted']['OSSF_MuEl'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved_boosted']['OSSF_MuEl'] ))
    
    print(R"     \multicolumn{1}{|l|}{}                                          & {17. $\mu\mu +ee$ ( 4+ 11)}                         & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{3-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved']['split_OSSF'], _res['nb2PLusnb3']['gg{}'.format(heavy)]['boosted']['split_OSSF'], 
        _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved']['split_OSSF'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['boosted']['split_OSSF'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          &                                                                    & \multicolumn{2}{c|}{%s}                  & \multicolumn{2}{c|}{%s}                  \\ \cline{2-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved_boosted']['OSSF'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved_boosted']['OSSF'] ))
    
    print(R"     \multicolumn{1}{|l|}{}                                          & {18. $\mu\mu + ee +\mu e$ (5 +12)}                  & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{3-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved']['split_OSSF_MuEl'], _res['nb2PLusnb3']['gg{}'.format(heavy)]['boosted']['split_OSSF_MuEl'], 
        _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved']['split_OSSF_MuEl'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['boosted']['split_OSSF_MuEl'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          &                                                                    & \multicolumn{2}{c|}{%s}                  & \multicolumn{2}{c|}{%s}                  \\ \hline"%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved_boosted']['split_OSSF_MuEl'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved_boosted']['split_OSSF_MuEl'] ))
    
    
    print(R"\end{tabular}%")
    print(R"}")
    print(R"\end{table}")
    sys.stdout = org_stdout
    f.close()
    return 



#path      = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext9/do_comb_and_split/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test_with_toysFrequentist/dnn/2POIs_r" 
path      = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext11/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r"

flavors   = ['ElEl', 'MuMu', 'MuEl', 'OSSF', 'OSSF_MuEl', 'split_OSSF', 'split_OSSF_MuEl', 'MuMu_ElEl', 'MuMu_ElEl_MuEl', 'MuMu_MuEl', 'ElEl_MuEl']
regions   = ['resolved', 'boosted' , 'resolved_boosted']
reco      = ['nb2', 'nb2PLusnb3', 'nb3']


print( glob.glob(os.path.join(path, 'M*')) )
for gof in glob.glob(os.path.join(path, 'M*')):
    m = gof.split('/')[-1]
    
    heavy = m.split('-')[0].replace('M','')
    light = 'A' if heavy =='H' else 'H'
    
    m_heavy = float(m.split('_')[0].split('-')[-1])
    m_light = float(m.split('_')[-1].split('-')[-1])

    #if not m =='MH-650.0_MA-50.0':
    #    continue

    _res = {}
    for nb in reco:
        _res[nb] = {}
        for p in ['bb%s'%heavy, 'gg%s'%heavy]:
            _res[nb][p] = {}
            for reg in regions:
                _res[nb][p][reg] ={}
                for flav in flavors:
                    _res[nb][p][reg][flav]={}
    
    for p, process in {'bb%s'%heavy:'bb_associatedProduction', 'gg%s'%heavy:'gg_fusion'}.items():
        for nb in reco:
            for reg in regions:
                for flav in flavors:
                    
                    others = [x for x in flavors if flav in x]
                    others.remove(flav)

                    for f in glob.glob(os.path.join(path, m, 'saturated', '*.json')):
                        
                        jsF = f.split('/')[-1]
                        if not process in jsF:
                            continue
                        
                        if not nb in jsF:
                            continue
                        if nb in ['nb2', 'nb3'] and 'nb2PLusnb3' in jsF:
                            continue
                        
                        if not reg in jsF:
                            continue
                        if reg in ['resolved', 'boosted'] and 'resolved_boosted' in jsF:
                            continue
                        
                        if not flav in jsF:
                            continue
                        
                        if any(x in jsF for x in others):
                            continue
                        
                        openF  = open(f)
                        data   = json.load(openF)
                        pvalue =  data["125.0"]["p"]
                        if pvalue <= 0.05:
                            pvalue = '\cellcolor[HTML]{E44F4B}'+str(pvalue)
                        _res[nb][p][reg][flav] = pvalue
                        
                        print( jsF, p, nb, reg, flav, pvalue)
    
    LatexF = os.path.join(path, m, 'saturated','GOF.tex')
    print( 'file saved in ::', LatexF)
    print_table(_res, LatexF, heavy, light, m_heavy, m_light)
