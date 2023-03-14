import json
import os, os.path, sys   

import pandas as pd
import numpy as np
import pdfkit as pdf
import matplotlib.pyplot as plt

from pdflatex import PDFLaTeX
from collections import OrderedDict
from operator import getitem
from matplotlib.backends.backend_pdf import PdfPages

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/utils')
import www as www


base_dir="/nfs/user/kjaffel/www-eos-lxplus/hig-22-010/__ver15"

#m = ["MH-500.0_MA-300.0", "MH-500.0_MA-250.0", "MH-300.0_MA-200.0","MH-510.0_MA-130.0", "MH-650.0_MA-50.0", "MH-800.0_MA-140.0",
#     "MH-800.0_MA-200.0","MH-717.96_MA-577.65", "MH-516.94_MA-78.52","MH-379.0_MA-54.59", "MA-800.0_MH-140.0","MA-500.0_MH-250.0","MA-510.0_MH-130.0"]
m = ["MH-500.0_MA-300.0"]

nb2header       = pd.DataFrame(["nb2_impact_r", "nb2_pull  +/- 1 sigma"])
nb3header       = pd.DataFrame(["nb3_impact_r", "nb3_pull  +/- 1 sigma"])
nb2PLusnb3header= pd.DataFrame(["Comb_impact_r","Comb_pull +/- 1 sigma"])

columns0   = pd.MultiIndex.from_frame(nb2header)
columns0_1 = pd.MultiIndex.from_frame(nb3header)
columns0_2 = pd.MultiIndex.from_frame(nb2PLusnb3header)


def _draw_as_table(df, pagesize):
    alternating_colors = [['white'] * len(df.columns), ['lightgray'] * len(df.columns)] * len(df)
    alternating_colors = alternating_colors[:len(df)]
    fig, ax = plt.subplots(figsize=pagesize)
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values,
                        rowLabels=df.index,
                        colLabels=df.columns,
                        rowColours=['lightblue']*len(df),
                        colColours=['lightblue']*len(df.columns),
                        cellColours=alternating_colors,
                        loc='center')
    return fig
  

def dataframe_to_pdf(df, filename, numpages=(1, 1), pagesize=(11, 8.5)):
    with PdfPages(filename) as pdf:
        nh, nv = numpages
        rows_per_page = len(df) // nh
        cols_per_page = len(df.columns) // nv
        for i in range(0, nh):
            for j in range(0, nv):
                page = df.iloc[(i*rows_per_page):min((i+1)*rows_per_page, len(df)),
                            (j*cols_per_page):min((j+1)*cols_per_page, len(df.columns))]
                fig = _draw_as_table(page, pagesize)
                if nh > 1 or nv > 1:
                    # Add a part/page number at bottom-center of page
                    fig.text(0.5, 0.5/pagesize[0],
                            "Part-{}x{}: Page-{}".format(i+1, j+1, i*nv + j + 1),
                            ha='center', fontsize=8)
                pdf.savefig(fig, bbox_inches='tight')
                
                plt.close()


def add_line_to_latex_tabel(c1, c2, c3, c4, c5, c6, c7):
    return R"\cellcolor[HTML]{CBCEFB}\textbf{%s}   & \multicolumn{1}{c|}{%s}  & %s & %s     & \multicolumn{1}{c|}{%s}  & %s & %s  & \multicolumn{1}{c|}{%s}   & %s & %s \\ \hline"%(
    c1, c2, c3[0], f'{c3[1]} / {c3[2]}', c4, c5[0], f'{c5[1]} / {c5[2]}', c6, c7[0], f'{c7[1]} / {c7[2]}')


def add_line_header(m, cat1, cat2, cat3):
    return R"\cellcolor[HTML]{CBCEFB}\textbf{%s} & \multicolumn{3}{c|}{\cellcolor[HTML]{CBCEFB}\textbf{ %s: nb2}} & \multicolumn{3}{c|}{\cellcolor[HTML]{CBCEFB}\textbf{ %s: nb3}} & \multicolumn{3}{c|}{\cellcolor[HTML]{CBCEFB}\textbf{ %s:nb2+nb3}}  \\ \cline{2-10} "%(m, cat1, cat2, cat3)


def latex_table(LatexF, lines, caption, m, cat1, cat2, cat3):
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
    print(R"    \begin{tabular}{|l|ccc|ccc|ccc|}")
    print(R"\hline")
    header = add_line_header(m, cat1, cat2, cat3)
    print(R"%s"%header)
    print(R"\rowcolor[HTML]{CBCEFB}")
    print(R"\cellcolor[HTML]{CBCEFB}\textbf{NPs} & \multicolumn{1}{c|}{\cellcolor[HTML]{CBCEFB}\textbf{impact\_r}} & \textbf{pull}         & \textbf{+/- 1 $\sigma$} & \multicolumn{1}{c|}{\cellcolor[HTML]{CBCEFB}\textbf{impact\_r}} & \textbf{pull}         & \textbf{+/- 1$\sigma$} & \multicolumn{1}{c|}{\cellcolor[HTML]{CBCEFB}\textbf{impact\_r}} & \textbf{pull}         & \textbf{+/- 1$\sigma$} \\ \hline")
    for line in lines:	
        print(R"%s"%line)
    print(R"\end{tabular}%")
    print(R"}")
    print(R"\end{table}")
    sys.stdout = org_stdout
    f.close()
    return



def getrows(base_dir, dir, production, proc, nb, region, flav):
    impacts_dict = {}
    mass  = dir.replace("-","_")
    heavy = mass.split('_')[0].replace('M','')
    light = 'A' if heavy =='H' else 'H'
    
    #region = '+'.join(region.split('-')[1:])
    prefix = www.getCats(proc, nb, region, flav)[0]

    jsFNm = os.path.join(base_dir, dir, production, nb+"-"+region, prefix+':'+flav, 'pulls_and_impacts', 
            "impacts__{}ToZ{}To2L2B_{}_{}_{}_{}_dnn_{}_realdataset.json".format(heavy, light, production, nb, region, flav, mass))
    
    print( jsFNm) 
    if os.path.isfile(jsFNm):
        with open(jsFNm) as f:
            data = json.load(f)
        
        for rnk in range(len(data['params'])):
            
            nuis = data['params'][rnk]
            nuis_nm = str(nuis['name'])
            
            if 'prop' in nuis_nm:
                continue
            
            impcat_r          = round(nuis['impact_r'],3)
            pull_center       = round(nuis['fit'][1],3)
            plul_plus_1sigma  = round(nuis['fit'][2],3) 
            pull_minus_1sigma = round(nuis['fit'][0],3)
            
            if not nuis_nm in impacts_dict.keys():
                impacts_dict[nuis_nm] = {'impact_r': impcat_r, 
                                         'pull_pm_1sigma': (pull_center, plul_plus_1sigma, pull_minus_1sigma)}
    else:
        print( jsFNm, "doesnt exist")
    return  impacts_dict 



for dir in m: 
    heavy = dir.split('-')[0].replace('M','')
    light = 'A' if heavy =='H' else 'H'
    m_heavy = float(dir.split('_')[0].split('-')[-1])
    m_light = float(dir.split('_')[-1].split('-')[-1])

    for proc, production in {f'bb{heavy}': 'bb_associatedProduction', f'gg{heavy}': 'gg_fusion'}.items(): 
        mass  = '%s: ($m_{%s}$, $m_{%s}$) = (%s, %s) GeV'%(proc, heavy, light, m_heavy, m_light)
        for region in ["resolved","boosted"]:
            for flav in ["OSSF_MuEl", 'split_OSSF_MuEl', 'MuMu_ElEl_MuEl']:
                rows = {}
                prefix = {}
                for nb in ["nb2", "nb3", "nb2PLusnb3"]:
                   
                    #if  proc.startswith('gg') and region == 'resolved' and nb == 'nb2':
                    #    flav = 'MuMu_ElEl_MuEl'
                    
                    prefix[nb] = www.getCats(proc, nb, region, flav)        
                    rows[nb]   = getrows(base_dir, dir, production, proc, nb, region, flav)
    
                nb2_rows = rows['nb2']
                nb3_rows = rows['nb3'] 
                nb2PLusnb3_rows = rows['nb2PLusnb3']
                
                sorted_nb2PLusnb3_rows = OrderedDict(sorted(nb2PLusnb3_rows.items(),
                           key = lambda x: getitem(x[1], 'impact_r'), reverse=True))
                
                high_rankedNPs = list(sorted_nb2PLusnb3_rows)[0:30]
                print( high_rankedNPs )

                file_name = dir.replace("-","_")+"_"+production+"_"+region+"_"+flav
                LatexF  = file_name+'.tex'
                caption = f"The first 30 high ranked pulls/impcats: {prefix['nb2'][0]}:{prefix['nb2'][1]} .vs. {prefix['nb3'][0]}:{prefix['nb3'][1]} .vs. {prefix['nb2PLusnb3'][0]}:{prefix['nb2PLusnb3'][1]}" 
                lines = []
                for nuis in high_rankedNPs:
                    params = R"\cellcolor[HTML]{CBCEFB}\textbf{%s}"%(nuis.replace('_','\_'))
                    line = add_line_to_latex_tabel(params, nb2_rows[nuis]['impact_r'], nb2_rows[nuis]['pull_pm_1sigma'], 
                            nb3_rows[nuis]['impact_r'], nb3_rows[nuis]['pull_pm_1sigma'],
                            nb2PLusnb3_rows[nuis]['impact_r'], nb2PLusnb3_rows[nuis]['pull_pm_1sigma'],
                            )
                    lines.append(line)
                cat1=prefix['nb2'][0]
                cat2=prefix['nb3'][0]
                cat3=prefix['nb2PLusnb3'][0]
                latex_table(LatexF, lines, caption, mass, cat1, cat2, cat3)

                #pdfl = PDFLaTeX.from_texfile(LatexF)
                #pdf, log, completed_process = pdfl.create_pdf(keep_pdf_file=True, keep_log_file=True)

                #nb2_rows.sort(key = lambda x:x[1],  reverse=True)
                #nb2_rows = [list(x) for x in nb2_rows]
                #nb3_rows.sort(key = lambda x:x[1],  reverse=True)
                #nb3_rows = [list(x) for x in nb3_rows]
                #
                #
                ##### to produce DF and sorting wrt their NP ####
                #arr_new = [0]
                ##Covert list2 to numpy array
                #nb2_numpy= np.array(nb2_rows, dtype=object)
                #nb3_numpy= np.array(nb3_rows, dtype=object)
                #nb2PLusnb3_numpy= np.array(nb2PLusnb3_rows, dtype=object)
                ##Extract the specific columns from rows according to arr_new
                #nb2np_list=[]
                #nb3np_list=[]
                #nb2PLusnb3np_list = []
                #if(len(nb2_numpy)): 
                #    nb2_np = nb2_numpy[:,arr_new]
                #    nb2np_list = sum(nb2_np.tolist(),[])
                #if(len(nb3_numpy)): 
                #    nb3_np = nb3_numpy[:,arr_new]
                #    nb3np_list = sum(nb3_np.tolist(),[])
                #if(len(nb2PLusnb3_numpy)): 
                #    nb2PLusnb3_np = nb2PLusnb3_numpy[:,arr_new]
                #    nb2PLusnb3np_list = sum(nb2PLusnb3_np.tolist(),[])

                ##print(np_list)
                #for j in nb2_rows: 
                #    del j[0]
                #for j in nb3_rows: 
                #    del j[0]
                #for j in nb2PLusnb3_rows: 
                #    del j[0]
                #nb2_df = pd.DataFrame()
                #nb3_df = pd.DataFrame()
                #nb2PLusnb3_df = pd.DataFrame()
                #if(len(nb2_rows)):    
                #    nb2_df = pd.DataFrame(nb2_rows, columns=columns0, index=nb2np_list)
                #if(len(nb3_rows)):
                #    nb3_df = pd.DataFrame(nb3_rows, columns=columns0_1, index=nb3np_list)
                #if(len(nb2PLusnb3_rows)):    
                #    nb2PLusnb3_df = pd.DataFrame(nb2PLusnb3_rows, columns=columns0_2, index=nb2PLusnb3np_list)
                #
                #tog  = nb2_df.join(nb3_df, how='outer')
                #tog2 = tog.join(nb2PLusnb3_df, how='outer')
                #
                #print (tog2) 
                #if tog2.empty:
                #    continue
                #file_name = dir.replace("-","_")+"_"+production+"_"+region+"_"+flav
                #tog2.style.format("{:.4f}").to_excel(file_name+".xlsx")
                #
                ##tog2.to_html(file_name+'.html')
                ##pdf.from_file(file_name+'.html', file_name+'.pdf')
                #dataframe_to_pdf(tog2, file_name+'.pdf', numpages=(3, 2))
                #dataframe_to_pdf(tog2, file_name+'.png', numpages=(3, 2))
