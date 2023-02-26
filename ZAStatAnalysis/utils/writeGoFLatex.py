import glob 
import json
import os, os.path, sys


sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/')
import utils as utils
logger = utils.ZAlogger(__name__)



def print_multiSignal_table(_res, LatexF, heavy, light, m_heavy, m_light, caption=''):
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
    print(R"\caption{%s}"%caption)
    print(R"\label{tab:my-table}")
    print(R"\resizebox{\textwidth}{!}{%")
    print(R"	\begin{tabular}{|ll|cc|}")
    print(R"\hline")
        
    print(R"\multicolumn{2}{|l|}{{\begin{tabular}[c]{@{}l@{}}saturated GOF p-value\\ ($\m_{%s},  m_{%s}$) = (%s,%s) GeV\end{tabular}}} & \multicolumn{2}{c|}{\begin{tabular}[c]{@{}c@{}}multi-signal fit, \\ r\_gg%s+ r\_bb%s\end{tabular}} \\ \cline{3-4}\multicolumn{2}{|l|}{}    & \multicolumn{1}{c|}{resolved} & boosted               \\ \hline "%(heavy, light, m_heavy, m_light, heavy, heavy))
	# nb2 
    print(R"\multicolumn{1}{|l|}{{nb2}}     		       & 1. ee                                  &\multicolumn{1}{c|}{%s}                & 				\multicolumn{1}{c|}{%s}        \\ \cline{2-4} "%(
        _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['ElEl'], _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['ElEl'] ))
    print(R"\multicolumn{1}{|l|}{}                         & 2. $\mu\mu$                           	& \multicolumn{1}{c|}{%s}         		&             %s                 \\ \cline{2-4} "%(
        _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['MuMu'], _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['MuMu'] ))
    print(R"\multicolumn{1}{|l|}{}                         & 3. $\mu e$                 			& \multicolumn{1}{c|}{%s}         		&             %s                 \\ \cline{2-4} "%(
        _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['MuEl'], _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['MuEl'] ))
    print(R"\multicolumn{1}{|l|}{}                         & 4. $\mu\mu + ee$                       & \multicolumn{1}{c|}{%s}         		&             %s                 \\ \cline{2-4} "%(
        _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['MuMu_ElEl'], _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['MuMu_ElEl'] ))
    print(R"\multicolumn{1}{|l|}{}                         & 5. $\mu\mu + ee + \mu e$               & \multicolumn{1}{c|}{%s}         		&             %s                 \\ \cline{2-4} "%(
        _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['MuMu_ElEl_MuEl'], _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['MuMu_ElEl_MuEl'] ))
    print(R"\multicolumn{1}{|l|}{}                         & 6. OSSF                                & \multicolumn{1}{c|}{%s}         		&             %s                 \\ \cline{2-4} "%(
        _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['OSSF'], _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['OSSF'] ))
    print(R"\multicolumn{1}{|l|}{}                         & 7. OSSF + $\mu e$                      & \multicolumn{1}{c|}{%s}         		&             %s                 \\ \hline"%(
        _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['OSSF_MuEl'], _res['nb2']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['OSSF_MuEl'] ))
	# nb3
    print(R"\multicolumn{1}{|l|}{{nb3}}     		       & 8. ee                                  &\multicolumn{1}{c|}{%s}                & 				\multicolumn{1}{c|}{%s}        \\ \cline{2-4} "%(
        _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['ElEl'], _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['ElEl'] ))
    print(R"\multicolumn{1}{|l|}{}                         & 9. $\mu\mu$                            & \multicolumn{1}{c|}{%s}         		&             %s                \\ \cline{2-4} "%(
	    _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['MuMu'], _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['MuMu'] ))
    print(R"\multicolumn{1}{|l|}{}                         & 10. $\mu e$                            & \multicolumn{1}{c|}{%s}         		&             %s                 \\ \cline{2-4} "%(
        _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['MuEl'], _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['MuEl'] ))
    print(R"\multicolumn{1}{|l|}{}                         & 11. $\mu\mu + ee$                      & \multicolumn{1}{c|}{%s}         		&             %s                 \\ \cline{2-4} "%(
        _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['MuMu_ElEl'], _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['MuMu_ElEl'] ))
    print(R"\multicolumn{1}{|l|}{}                         & 12. $\mu\mu + ee + \mu e$              & \multicolumn{1}{c|}{%s}         		&             %s                 \\ \cline{2-4} "%(
        _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['MuMu_ElEl_MuEl'], _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['MuMu_ElEl_MuEl'] ))
    print(R"\multicolumn{1}{|l|}{}                         & 13. OSSF                               & \multicolumn{1}{c|}{%s}         		&             %s                 \\ \cline{2-4} "%(
        _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['OSSF'], _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['OSSF'] ))
    print(R"\multicolumn{1}{|l|}{}                         & 14. OSSF + $\mu e$                     & \multicolumn{1}{c|}{%s}         		&             %s                 \\ \hline"%(
        _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['OSSF_MuEl'], _res['nb3']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['OSSF_MuEl'] ))
	
	# nb2 +nb3
    print(R"\multicolumn{1}{|l|}{{nb2+nb3}} &")
    print(R"{\begin{tabular}[c]{@{}l@{}}15. OSSF  (x+13)\\ x= \\     4, if nb2-resolved, ggH\\     6, otherwise\end{tabular}} &")
    print(R"\multicolumn{1}{c|}{%s} & \multicolumn{1}{c|}{%s} \\ \cline{3-4} "%(
        _res['nb2PLusnb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['OSSF'], _res['nb2PLusnb3']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['OSSF'] ))
    print(R"\multicolumn{1}{|l|}{}                     &                                                    & \multicolumn{2}{c|}{%s}                                  \\ \cline{2-4}  "%(
        _res['nb2PLusnb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved_boosted']['OSSF'] ))
	
    print(R"\multicolumn{1}{|l|}{} &")
    print(R"{\begin{tabular}[c]{@{}l@{}}16. OSSF + $\mu e$ (x+14)\\ x= \\     5, if nb2-resolved, ggH\\     7, otherwise\end{tabular}} &")
    print(R"\multicolumn{1}{c|}{%s} & %s \\ \cline{3-4} "%(
        _res['nb2PLusnb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['OSSF_MuEl'], _res['nb2PLusnb3']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['OSSF_MuEl'] ))
    print(R"\multicolumn{1}{|l|}{}                     &                                                    & \multicolumn{2}{c|}{%s}                                  \\ \cline{2-4} "%(
        _res['nb2PLusnb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved_boosted']['OSSF_MuEl'] ))


    print(R"\multicolumn{1}{|l|}{}                     & {17. $ \mu\mu + ee$ (4+11)}         & \multicolumn{1}{c|}{%s}        & %s                        \\ \cline{3-4} "%(
        _res['nb2PLusnb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['split_OSSF'], _res['nb2PLusnb3']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['split_OSSF'] ))
    print(R"\multicolumn{1}{|l|}{}                     &                                                    & \multicolumn{2}{c|}{%s}                                    \\ \cline{2-4} "%(
        _res['nb2PLusnb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved_boosted']['split_OSSF']))
	
	
    print(R"\multicolumn{1}{|l|}{}                     & {18. $\mu\mu + ee + \mu e$ (5+ 12)} & \multicolumn{1}{c|}{%s}        & %s                        \\ \cline{3-4} "%(
        _res['nb2PLusnb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved']['split_OSSF_MuEl'], _res['nb2PLusnb3']['gg{}_bb{}'.format(heavy, heavy)]['boosted']['split_OSSF_MuEl'] ))
    print(R"\multicolumn{1}{|l|}{}                     &                                                    & \multicolumn{2}{c|}{%s}                                    \\ \hline "%(
        _res['nb2PLusnb3']['gg{}_bb{}'.format(heavy, heavy)]['resolved_boosted']['split_OSSF_MuEl'] ))
	
    print(R"\end{tabular}%")
    print(R"}")
    print(R"\end{table}")
    sys.stdout = org_stdout
    f.close()
    return 

def print_table(_res, LatexF, heavy, light, m_heavy, m_light, caption=''):
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
    print(R"\caption{%s}"%caption)
    print(R"\label{tab:my-table}")
    print(R"\resizebox{\textwidth}{!}{%")
    print(R"\begin{tabular}{|ll|cc|cc|}")
    print(R"\hline")
    print(R"     \multicolumn{2}{|c|}{{\begin{tabular}[c]{@{}c@{}}Saturated GOF, p-value \\ ($m_{%s}$, $m_{%s}$) = (%s, %s) GeV\end{tabular}}} & \multicolumn{2}{c|}{gg%s}            & \multicolumn{2}{c|}{bb%s}                \\ \cline{3-6} "%(
        heavy, light, m_heavy, m_light, heavy, heavy))
    print(R"     \multicolumn{2}{|c|}{}                                                                                                               & \multicolumn{1}{c|}{resolved} & boosted & \multicolumn{1}{c|}{resolved} & boosted \\ \hline")
    
    # nb2 
    print(R"     \multicolumn{1}{|l|}{{nb2}}                      & 1. ee                                                                             & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{2-6} "%(
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
    print(R"     \multicolumn{1}{|l|}{{nb2+nb3}}                  & {\begin{tabular}[c]{@{}l@{}}15. OSSF  (x+13)\\ x= \\     4, if nb2-resolved, ggH\\     6, otherwise\end{tabular}} ")
    print(R"& \multicolumn{1}{c|}{%s}     & %s          & \multicolumn{1}{c|}{%s}      & %s       \\ \cline{3-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved']['OSSF'], _res['nb2PLusnb3']['gg{}'.format(heavy)]['boosted']['OSSF'], 
        _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved']['OSSF'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['boosted']['OSSF'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          &                                                                    & \multicolumn{2}{c|}{%s}                   & \multicolumn{2}{c|}{%s}                  \\ \cline{2-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved_boosted']['OSSF'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved_boosted']['OSSF'] ))
    
    print(R"     \multicolumn{1}{|l|}{}                                          & {\begin{tabular}[c]{@{}l@{}}16. OSSF + $\mu e$ (x+14)\\ x= \\     5, if nb2-resolved, ggH\\     7, otherwise\end{tabular}} ")
    print(R"& \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{3-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved']['OSSF_MuEl'], _res['nb2PLusnb3']['gg{}'.format(heavy)]['boosted']['OSSF_MuEl'], 
        _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved']['OSSF_MuEl'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['boosted']['OSSF_MuEl'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          &                                                                    & \multicolumn{2}{c|}{%s}                   & \multicolumn{2}{c|}{%s}                  \\ \cline{2-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved_boosted']['OSSF_MuEl'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved_boosted']['OSSF_MuEl'] ))
    
    print(R"     \multicolumn{1}{|l|}{}                                          & {17. $\mu\mu +ee$ ( 4+ 11)}                                        & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{3-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved']['split_OSSF'], _res['nb2PLusnb3']['gg{}'.format(heavy)]['boosted']['split_OSSF'], 
        _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved']['split_OSSF'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['boosted']['split_OSSF'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          &                                                                    & \multicolumn{2}{c|}{%s}                   & \multicolumn{2}{c|}{%s}                  \\ \cline{2-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved_boosted']['split_OSSF'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved_boosted']['split_OSSF'] ))
    
    print(R"     \multicolumn{1}{|l|}{}                                          & {18. $\mu\mu + ee +\mu e$ (5 +12)}                                 & \multicolumn{1}{c|}{%s}        & %s       & \multicolumn{1}{c|}{%s}        & %s       \\ \cline{3-6} "%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved']['split_OSSF_MuEl'], _res['nb2PLusnb3']['gg{}'.format(heavy)]['boosted']['split_OSSF_MuEl'], 
        _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved']['split_OSSF_MuEl'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['boosted']['split_OSSF_MuEl'] ))
    print(R"     \multicolumn{1}{|l|}{}                                          &                                                                    & \multicolumn{2}{c|}{%s}                   & \multicolumn{2}{c|}{%s}                  \\ \hline"%(
        _res['nb2PLusnb3']['gg{}'.format(heavy)]['resolved_boosted']['split_OSSF_MuEl'], _res['nb2PLusnb3']['bb{}'.format(heavy)]['resolved_boosted']['split_OSSF_MuEl'] ))
    
    
    print(R"\end{tabular}%")
    print(R"}")
    print(R"\end{table}")
    sys.stdout = org_stdout
    f.close()
    return 


#path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext9/do_comb_and_split/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test_with_toysFrequentist/dnn/2POIs_r" 
#path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext11/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r"
#path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext8/half/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r"
### decorrelate all theory uncer.
#path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext12/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r"
#path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext13/chunk_1/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r"
#path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext14/chunk_1/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r"
#path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext15/chunk_1/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r"
### split DY + ttbar
#path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/hig-22-010/unblinding_stage1/followup1__ext16/chunk_1/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r"
#path = "../hig-22-010/unblinding_stage1/followup1__ext19/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/"
#path = "../hig-22-010/unblinding_stage1/followup1__ext19/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r___QCDmuRF_is_ON/"
### split 2016 , ttbar , dy 
#path = "../hig-22-010/unblinding_stage1/followup1__ext20/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/"
### split 2016, ttbar
#path = '/nfs/user/sjain/ver1/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/'
# other attempt  to fix NPs correlation between UL16 pre-/post-VFP
#path = '../hig-22-010/unblinding_stage1/followup1__ext22/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/'
#path = '../hig-22-010/unblinding_stage1/followup1__ext23/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/'
#path = '../hig-22-010/unblinding_stage1/followup1__ext24/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/'
#path = '../hig-22-010/unblinding_stage1/followup1__ext25/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/'
##split theory uncer betwee resol and boosted , 2016 is full 
#path = '../hig-22-010/unblinding_stage1/followup1__ext26/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/'
#path = '../hig-22-010/unblinding_stage1/followup1__ext27/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/'
#path = '../hig-22-010/unblinding_stage1/followup1__ext28/with_split_prepostVFP/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/'
#path = '../hig-22-010/unblinding_stage1/followup1__ext29/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/'
path  = '../hig-22-010/unblinding_stage1/followup1__ext29/work__ULfullrun2/bayesian_rebin_on_S/goodness_of_fit_test/dnn/2POIs_r/multi_signal/'


flavors   = ['ElEl', 'MuMu', 'MuEl', 'OSSF', 'OSSF_MuEl', 'split_OSSF', 'split_OSSF_MuEl', 'MuMu_ElEl', 'MuMu_ElEl_MuEl', 'MuMu_MuEl', 'ElEl_MuEl']
regions   = ['resolved', 'boosted' , 'resolved_boosted']
reco      = ['nb2', 'nb2PLusnb3', 'nb3']

tb= ''
multi_signal_fit = False
if 'multi_signal' in path:
    multi_signal_fit = True
    tb = 'tanbeta*'

print( glob.glob(os.path.join(path, tb, 'M*')) )
for gof in glob.glob(os.path.join(path, tb, 'M*')):
    m = gof.split('/')[-1]
    
    heavy = m.split('-')[0].replace('M','')
    light = 'A' if heavy =='H' else 'H'
    
    m_heavy = float(m.split('_')[0].split('-')[-1])
    m_light = float(m.split('_')[-1].split('-')[-1])

    if multi_signal_fit:
        dict_ = {'gg%s_bb%s'%(heavy, heavy):'gg_fusion_bb_associatedProduction'}
    else:
        dict_ = {'bb%s'%heavy:'bb_associatedProduction', 'gg%s'%heavy:'gg_fusion'}
    _res  = {}
    for nb in reco:
        _res[nb] = {}
        for p in dict_.keys():
            _res[nb][p] = {}
            for reg in regions:
                _res[nb][p][reg] ={}
                for flav in flavors:
                    _res[nb][p][reg][flav]={}
    
    for p, process in dict_.items():
        for nb in reco:
            for reg in regions:
                for flav in flavors:
                    
                    others = [x for x in flavors if flav in x]
                    others.remove(flav)

                    for f in glob.glob(os.path.join(path, tb, m, 'saturated', '*.json')):
                        
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
                        if "125.0" in data.keys():
                            pvalue =  round(data["125.0"]["p"],3)
                            if pvalue <= 0.05:
                                pvalue = '\cellcolor[HTML]{E44F4B}'+str(pvalue)
                            _res[nb][p][reg][flav] = pvalue
                            print( jsF, p, nb, reg, flav, pvalue)
                        else:
                            logger.warning("== sth wrong might happend with  this file: == %s"%f)
    
    #caption = ' followup1__ext27, full 2016, split ttbar , correlate top pt rwgt'
    #caption = ' followup1\_\_ext28 split 2016 , split ttbar '  
    caption  = ' followup1\_\_ext29, split ttbar, no split DY, sno split 2016, fix btag SF'

    os.makedirs(os.path.join(path, m, 'saturated'), exist_ok=True) 
    if os.path.isdir(os.path.join(path, m, 'saturated')):
        LatexF = os.path.join(path, m, 'saturated','GOF.tex')
        print( 'file saved in ::', LatexF)
        if multi_signal_fit:
            print_multiSignal_table(_res, LatexF, heavy, light, m_heavy, m_light, caption)
        else:
            print_table(_res, LatexF, heavy, light, m_heavy, m_light, caption)
