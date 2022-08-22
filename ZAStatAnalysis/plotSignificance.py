import glob
import argparse
import os, os.path
import json
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict
from labellines import *

import CMSStyle as CMSStyle
import Constants as Constants

parser = argparse.ArgumentParser(description='Draw 1D pvalue scan')
parser.add_argument('-p', '--jsonpath', action='store', type=str, required=True, help='JSON file containing pvalues and significance for all mass points')
parser.add_argument('--unblind', action='store_true', default=False, help='If set, draw also observed significance')
parser.add_argument('--era', type=str, default=False, required=True, help='data taking of the given inputs')
parser.add_argument('--scan', type=str, default='mA', choices=['mA', 'mH'], help='')

options = parser.parse_args()

nm  = 'mH' if options.scan == 'mA' else 'mA'
fix = 'A' if options.scan == 'mH' else 'H'

colors=['black', 'blue', 'purple', 'navy', 'crimson', 'turquoise', 'slateblue', 'darkorange', 'forestgreen', 'indigo', 'limegreen', 'blueviolet', 'plum', 'turquoise', 'hotpink', 'mediumseagreen', 'springgreen', 'aquamarine', 'turquoise', 'aqua', 'mediumslateblue', 'orchid', 'deeppink', 'darkturquoise', 'teal', 'mediumslateblue']

_1_sigma = 0.15865
_2_sigma = 0.02275
_3_sigma = 0.00135
_4_sigma = 3.15e-05
_5_sigma = 2.8499999999999997e-07
_6_sigma = 1e-09

for jsf in glob.glob(os.path.join(options.jsonpath, '*.json')):
    
    with open(jsf) as f:
        params = json.load(f)
    
    name = options.scan + '_' + jsf.split('/')[-1].replace('.json', '') + '_'+ options.era
    
    idx  = 1 if options.scan == 'mH' else 0
    idx2 = 0 if options.scan == 'mH' else 1
    
    to_fix = []
    for l in params:
        if not 'expected_p-value' in l.keys(): continue
        m_fix = l['parameters'][idx]
        if not m_fix in to_fix: 
            to_fix.append(m_fix)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    CMSStyle.changeFont()
    
    #with plt.style.context(matplotx.styles.dufte):
    #matplotx.line_labels(leg)
    masses = np.arange(0., 1200., 200.)
    for i, sig in enumerate([_1_sigma, _2_sigma, _3_sigma, _4_sigma, _5_sigma, _6_sigma]):
        plt.plot(masses, [sig]*len(masses), linestyle='dashed', color='crimson', label=r'%s $\sigma$'%str(i+1))
    labelLines(plt.gca().get_lines(), ha='right', align=True,fontsize=10)#, backgroundcolor="#ffffff00")
    
    plots = []
    for i, m in enumerate(sorted(to_fix)):
        
        to_scan = defaultdict()
        pvalues_scan = defaultdict()
        
        for l in params:
            if not 'expected_p-value' in l.keys(): continue
            m_f = l['parameters'][idx]
            m_s = l['parameters'][idx2]
    
            if not m == m_f: continue
            to_scan.update({m_s :l['expected_p-value']} )
    
        #if len(to_scan.keys()) < 3:
        #    continue
        
        for tup in sorted(to_scan.items()):
            pvalues_scan.update({tup[0] : tup[1] })
        
        print( '- {} fixed m{}= {} :: {}= {}  and  pvalues= {}'.format(i, fix, m, options.scan, pvalues_scan.keys(), pvalues_scan.values()))
        #https://docs.scipy.org/doc/scipy/tutorial/interpolate.html    
        plots += plt.plot(pvalues_scan.keys(), pvalues_scan.values(), "o", linestyle='solid', linewidth=2, color=colors[i], label=r"Expected, $m_{%s}$= %d"%(fix , m))
        if options.unblind:
            plots += plt.plot(pvalues_scan.keys(), pvalues_scan.values(), "o", linestyle='solid', linewidth=2, color=colors[i], label=r"Observed $m_{%s}$= %d"%(fix , m))
            name += '_observed'
    
    labels = [p.get_label() for p in plots]
    plt.legend(plots, labels, prop=dict(size=12), loc='best', frameon=False)
    
    ax.set_xlim([-0.01, 1001])
    ax.set_ylim([1e-10, 1e3])
    
    xlabel = r'$m_{H}$ (GeV)' if options.scan == 'mH' else r'$m_{A}$(GeV)'
    ax.set_xlabel(xlabel)
    ax.set_ylabel('p-value')
    
    plt.title('CMS Preliminary', fontsize=14., loc='left', style='italic', weight="bold")
    plt.title(r'%.2f $fb^{-1}$ (13TeV)'%(Constants.getLuminosity(options.era)/1000.), fontsize=14., loc='right', style='italic')
    ax.set_yscale('log')
    
    fig.savefig(os.path.join(options.jsonpath, name+'.png'))
    fig.savefig(os.path.join(options.jsonpath, name+'.pdf'))
    
    print( 'file saved in : ', os.path.join(options.jsonpath, name+'.png'))
    plt.close(fig)
    plt.gcf().clear()
