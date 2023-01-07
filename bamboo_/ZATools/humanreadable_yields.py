import math
import yaml
import os, os.path


def get_cfg(plotit_yml):
    with open(plotit_yml) as file:
        cfg= yaml.safe_load(file)
    return cfg


def get_process(p):
    procl = None
    with open(f"{inDir}/yields_{era}.tex", 'r') as inf:
        for l in inf: 
            if 'Cat.' in l:
                catl = l.split('&')
            if p in l :
                procl = l.split('&')
    return catl, procl


def get_significance(y):
    S = y[-1].split('\pm')[0].replace('$', '') 
    B = y[-2].split('\pm')[0].replace('$', '')
    if '---' in S or '---' in B:
        return '---'
    else:
        S = float(S)
        B = float(B)
        if not B <= 0.:
            signif = math.sqrt(2*( (S+B)*math.log(1+S/B) -S ))
            return '%.4f'%signif
        else:
            return '-' 


def get_SignalCatEff(dict_yields, smp):
    cfg = get_cfg(plotit_yml)
    Eff_dict = {}
    for i, (cat, y) in enumerate(dict_yields.items()):
        if not channel in cat:
            continue
        if nomet in cat:
            continue
        if '---' in y:
            continue
        
        signal_cat = cat.split(':')[0]
        Tot_pass   = y[-1].split('\pm')[0].replace('$', '')
        if not smp in cfg['files'].keys():
            continue
        
        Tot_generated = cfg['files'][smp]["generated-events"]
        eff = float(Tot_pass)/float(Tot_generated)
        Eff_dict[signal_cat] = eff

        #print( signal_cat, Tot_pass, Tot_generated)
    return Eff_dict



if __name__ == "__main__":
    
    # [(240.0, 130.0), (300.0, 135.0), (700.0, 200.0), (250.0, 125.0), (750.0, 610.0), (500.0, 250.0), (800.0, 140.0), (200.0, 125.0), (510.0, 130.0), (780.0, 680.0), (220.0, 127.0), (670.0, 500.0), (550.0, 300.0)]
    
    mass        = (200, 125)
    era         = '2017'
    year        = era.replace('20', '').replace('-','')
    nomet       = 'no $p_{T}^{miss}$ cut' # will be ignored 
    #inDir      = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/forHIG/ul_2017_ver45'
    #inDir      = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/llbbtests/atozh_vs_htoza2'
    inDir       = f'/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/llbbtests/atozh_vs_htoza3/{era}/'
    plotit_yml  = os.path.join(inDir, 'plots.yml')
    mHeavy      = "{:.2f}".format(mass[0])
    mLight      = "{:.2f}".format(mass[1])
    mHeavy      = str(mHeavy).replace('.', 'p')
    mLight      = str(mLight).replace('.', 'p')
    
    print(R'\begin{table}[!htb]')
    print(R'     \caption{ Comparaison of %s signal acceptance in the production mechanismes H $\rightarrow$ ZA and A $\rightarrow$ ZH in the llbb final state}'%(era))
    print(R' \label{table:limits_tab}')
    print(R' \small')
    print(R' \resizebox{\textwidth}{!}{')
    print(R' \begin{tabular}{@{}lc@{}} \toprule')
    print(R' \hspace{1cm}')
    
    Leptons = {'mumu': '$\mu^{+}\mu^{-}$', 
               'elel': '$e^{+}e^{-}$',
               'elel + mumu': '$\mu^{+}\mu^{-} + e^{+}e^{-}$'}

    for mode in ['HToZA', 'AToZH']:
        heavy = mode[0]
        light = mode[-1]
        
        print(R'\\\hline')
        for prod, orders in {'gluon-gluon fusion':['lo'], 
                             'b-associated production': ['lo', 'nlo']}.items():
            for o in orders:
                
                r           = f'gg{heavy}' if prod=='gluon-gluon fusion' else f'bb{heavy}'
                process     = '$\splitline{%s-%s: (m_{%s}, m_{%s})}{= %s GeV}$'%(o, r, heavy, light, str(mass))
                cols        = ['DY', 'SM', 'others', 'ST', 'VV', 'ttbar', 'Data/MC', 'Tot. MC'] + [process]    
                cols       += ['Significance \\\\'] 
                
                if r == f'gg{heavy}':
                    smp = f'GluGluTo{heavy}ToZ{light}To2L2B_M{heavy}_{mHeavy}_M{light}_{mLight}_tb_1p50_TuneCP5_13TeV_madgraph_pythia8_UL{year}.root'
                
                elif r == f'bb{heavy}':
                    if o == 'nlo': smp = f'{heavy}ToZ{light}To2L2B_M{heavy}_{mHeavy}_M{light}_{mLight}_tb_20p00_TuneCP5_bbH4F_13TeV_amcatnlo_pythia8_UL{year}.root'
                    else: smp = f'{heavy}ToZ{light}To2L2B_M{heavy}_{mHeavy}_M{light}_{mLight}_tb_20p00_TuneCP5_bbH4F_13TeV_madgraph_pythia8_UL{year}.root'
                
                catl, procl = get_process(process)
                
                print('\n')
                #print(R'Cat. & ' + R' & '.join(cols)+ R'\hline\\')
                print(fR"{process} & Acceptance x Efficiencies \\\hline\\" )
                
                if procl is None:
                    print("%"*10)
                    continue
                
                for region, taggerWP in {'resolved':'DeepJetM', 
                                         'boosted' : 'DeepCSVM'}.items(): #'DeepDoubleBvLV2custom'  also for boosted 
                    
                    _2chEff ={}
                    for channel, flavor in {'$\mu^{+}\mu^{-}$': 'mumu', 
                                            '$e^{+}e^{-}$': 'elel'}.items():
                        
                        dict_yields = {}
                        for i, p in enumerate(cols):
                            for cat, y_proc in zip(catl, procl):
                                y_proc = y_proc.strip()
                                cat    = cat.strip()
                                
                                if cat !='Cat.':
                                    if not region in cat: 
                                        continue
                                    if not taggerWP in cat:
                                        continue
                                
                                if i == 0:
                                    dict_yields[cat] = [y_proc]
                                else:
                                    dict_yields[cat].append(y_proc)
                        
                        Eff_dict = get_SignalCatEff(dict_yields, smp)
                        
                        if not flavor in _2chEff.keys():
                            _2chEff[flavor]=Eff_dict

                        if not 'elel + mumu' in _2chEff.keys():
                             _2chEff['elel + mumu']={}
                        for k, v in Eff_dict.items():
                            if not k in _2chEff['elel + mumu'].keys():
                                _2chEff['elel + mumu'][k] = 0.
                            _2chEff['elel + mumu'][k] += Eff_dict[k]
                            print(fR"{k}, {channel} & {round(Eff_dict[k],5)} \\")
                        
                        for i, (cat, y) in enumerate(dict_yields.items()):
                            if not channel in cat:
                                continue
                            if nomet in cat:
                                continue
                            
                            sigma = get_significance(y)
                            y += [sigma]
                            all_y = ' & '.join(y)
                            cat   = cat.replace('_', '\_')
                            #print(fR"{cat} & {all_y} \\")
                    
                    #print(fR"\\")
                    for flav, s_per_flav in _2chEff.items():
                        for signal_cat, eff in s_per_flav.items():
                            if flav == 'elel + mumu':
                                print(fR'{signal_cat}, ({Leptons[flav]}) & {round(eff, 5)} \\')
                    print(R"\\\hline\\")
                print("%"*10)
    print(R'\bottomrule')
    print(R'\end{tabular}')
    print(R'}')
    print(R'\end{table}')
    
    with open(f"{inDir}/yields_{era}.tex", 'r') as inf:
        with open(f"{inDir}/yields_{era}_formatted.tex", 'w+') as outf:
            for line in inf:
                
                if any( x in line for x in ['DY', 'SM', 'others', 'ST', 'VV', 'ttbar']):
                    continue
    
                if '&' in line:
                    newl = line.split('&')
                    for col in newl:
                        outf.write(f'& {col.strip()}\n')
                else:
                    outf.write(line)
