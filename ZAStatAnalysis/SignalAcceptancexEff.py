import math
import yaml
import os, sys, os.path
import glob
import matplotlib.pyplot as plt

import Constants as Constants
import utils.CMSStyle as CMSStyle


def get_cfg(plotit_yml):
    with open(plotit_yml) as file:
        cfg= yaml.safe_load(file)
    return cfg

def get_process(process):
    with open(f"{inDir}/yields_{era}.tex", 'r') as inf:
        for l in inf: 
            if 'Cat.' in l:
                catl = l.split('&')
            if process in l :
                procl = l.split('&')
        return catl, procl

def get_channel(cat):
    if '$\mu^{+}\mu^{-}$' in cat:
        return 'mumu'
    if '$e^{+}e^{-}$' in cat:
        return 'elel'
    if '$\mu^{\pm}e^{\pm}$' in cat:
        return 'muel'

def get_SignalParams(rf):
    # this a mass here , but believe me you don't want to have .00 in plotit legend 
    m_heavy  = ('%.2f'%float(rf.split('_')[2].replace('p', '.'))).replace('.00', '')
    m_light  = ('%.2f'%float(rf.split('_')[4].replace('p', '.'))).replace('.00', '')
    process  = 'ggH' if 'GluGlu' in rf else 'bbH'
    return process, m_heavy, m_light


if __name__ == "__main__":

    era         = 2017
    mode        = 'HToZA'
    dict_       = {'mH':500, 'mA': 300}
    m_tofix     = 'mH'
    m_topave    = 'mA' if m_tofix=='mH' else 'mH'
    region      = 'boosted'
    taggerWP    = 'DeepCSVM' if region =='boosted' else 'DeepJetM'
    heavy       = mode[0]
    light       = mode[-1]
    colors      = ['darkblue', 'orange']
    nomet       = 'no $p_{T}^{miss}$ cut' # will be ignored
    inDir       = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/forHIG/ul_2017_ver45'
    plotit_yml  = os.path.join(inDir, 'plots.yml')
    
    dict_yields = {'ggH':{
                         f'nb=2 -{region}':{'x':[], 'y':[]},
                         f'nb=3 -{region}':{'x':[], 'y':[]}
                        },
                   'bbH':{
                         f'nb=2 -{region}':{'x':[], 'y':[]},
                         f'nb=3 -{region}':{'x':[], 'y':[]}
                        }
                   }

    cfg = get_cfg(plotit_yml)
    
    fig = plt.figure(figsize=(8,6))
    ax  = fig.add_subplot(111)
    CMSStyle.applyStyle(fig, ax, Constants.getLuminosity(era), figures=1)

    for i, f in enumerate(glob.glob(os.path.join(inDir, "results", "*.root"))):
        smp = f.split('/')[-1]
        
        if '__skeleton__' in smp:
            continue
        if not cfg['files'][smp]['type'] == 'signal':
            continue
    
        if not mode in smp:
            continue
        
        m = "{:.2f}".format(dict_[m_tofix])
        m = str(m).replace('.', 'p')
        
        if not m in smp:
            continue
        
        r, m_heavy, m_light = get_SignalParams(smp) 
        process       = '$\splitline{%s: (m_{%s}, m_{%s})}{= (%s, %s) GeV}$'%(r, heavy, light, m_heavy, m_light)
        catl, procl   = get_process(process)
        Tot_generated = cfg['files'][smp]["generated-events"]
        m2 = m_light if m_topave[-1]==light else m_heavy
        print(f'{r}, (m_{heavy}, m_{light}) = ({m_heavy}, {m_light}) GeV')
        
        _2chEff = {}
        for cat, y_proc in zip(catl, procl):
            y_proc = y_proc.strip()
            cat    = cat.strip()
            
            if cat =='Cat.':
                continue
            if nomet in cat:
                continue
            if '---' in y_proc:
                continue
            if not region in cat:
                continue
            if not taggerWP in cat:
                continue
            if region =='boosted' and not 'both_subjets_pass' in cat:
                continue
            
            channel    = get_channel(cat)
            signal_cat = cat.split(':')[0]
            Tot_pass   = y_proc.split('\pm')[0].replace('$', '')
            eff = float(Tot_pass)/float(Tot_generated)
            print(f' * cat. {signal_cat} {channel} {taggerWP}= {eff}')
            
            if channel in ['mumu', 'elel']:
                if not signal_cat in _2chEff.keys():
                    _2chEff[signal_cat] = 0.
                _2chEff[signal_cat] += eff
        
        for i, k in enumerate(_2chEff.keys()):
            dict_yields[r][k]['x'].append(float(m2)) 
            dict_yields[r][k]['y'].append(_2chEff[k]) 
            print(f' * cat. {k} elel + mumu {taggerWP}= {_2chEff[k]}')
        print('==='*20)
  
    print( dict_yields )
    for i, (r, yieldForcat) in enumerate(dict_yields.items()):
        for k in yieldForcat.keys():
            ls = 'solid' if 'nb=2' in k else 'dashed'
            xl = yieldForcat[k]['x'] 
            yl = yieldForcat[k]['y'] 
            xl, yl = zip(*sorted(zip(xl, yl)))
            plt.plot(xl, yl, marker='o', linestyle=ls, color=colors[i], label=f'{r}: {k}'+r' ($\mu\mu$ + ee)')
        
    #plt.xlim(0., 1000.)
    #plt.ylim(0., 1.)
        
    plt.xlabel(fr'$m_{m_topave[-1]} [GeV]$', fontsize=12)
    plt.ylabel( r'Acceptance x Efficiencies', fontsize=12)
    plt.legend(loc='best')
    ax.get_legend().set_title(fr"2HDM-II, $m_{m_tofix[-1]}$= {dict_[m_tofix]} GeV")
    plt.grid(zorder = 0, alpha = 0.3)
                    
    plt.tight_layout()
    plt.savefig(f'effxacc_{region}.png')
    plt.gcf().clear()
    print( f'Acceptance x Efficiencies plot is saved in :: effxacc_{region}_{era}.png')
