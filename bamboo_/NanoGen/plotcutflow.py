import os, os.path
import matplotlib.pyplot as plt
import json
import glob
import numpy as np
import argparse

plt.rcParams["grid.linestyle"] = (5,9)


def string_to_mass(s):
    m = float(s.replace('p', '.'))
    return m

def computeefficiencies(PATHBASE, path=None):
    for filename in glob.glob(os.path.join(PATHBASE, path, "results/Cutflow", '*.json')):
        
        print(filename)

        split_filename = filename.split('/')
        split_filename = split_filename[-1]
        split_filename = split_filename.split('_')
        MH = string_to_mass(split_filename[2])
        MA = string_to_mass(split_filename[3])
        tb = string_to_mass(split_filename[4])
    
        suffix=('b-associatedproduction' if 'bbH' in split_filename else( 'gg-fusion')) 
        print( MH, MA, tb)
        with open(filename) as f:
            data = json.load(f)
        
        barWidth = 0.1
        fig= plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111)
        colors = ['#1D2F6F', '#8390FA', '#6EAF46', '#FAC748']
        
        sorted_data = sorted( val for val in data.values())
        
        selections= {}
        bars = {}
        for cat, flow in data.items(): 
            selections[cat]= []
            bars[cat] = []
            for list in flow:
                bars[cat].append(float(list[1]))
                if 'has' in list[0]:
                    sel = list[0].replace('hasOs{}'.format(cat),'hasOsSfLep')
                else:
                    sel = list[0].replace('_{}Sel'.format(cat),'')
                selections[cat].append(sel)
            if cat in ['mumu', 'elel']:
                # sort on list1 while retaining order of string list
                sorted_bars = [y for _,y in sorted(zip(selections[cat],bars[cat]),key=lambda x: x[1], reverse=True)]
                sorted_sel = sorted(selections[cat], reverse=True)
                
                selections[cat] = sorted_sel
                bars[cat] = sorted_bars
        
        # FIXME 
        #selections = ['hasOsSfLep', 'at_least_2jets_GenJet', 'at_least_2bjets_GenBJet', 'exactly_2jets_GenJet', 'exactly_2bjets_GenBJet']#, 'at_least_3jets_GenJet', 'at_least_3bjets_GenBJet'] 
        selections = ['hasOsSfLep', 'at_least_2jets_GenJet', 'at_least_2bjets_GenBJet']#, 'at_least_3jets_GenJet', 'at_least_3bjets_GenBJet'] 
        print( selections )
        print( bars )
        xpos= np.arange(0.4, len(selections)/2, 0.5)
        
        ax.bar([0.], bars["total_generated_events"], width = barWidth, color = colors[0], edgecolor='white', align='center', label='total generated events')
        ax.bar(xpos-barWidth/2, bars['elel'], width = barWidth, color = colors[1], edgecolor='white', align='center', label='ee channel')
        ax.bar(xpos+barWidth/2, bars['mumu'], width = barWidth, color = colors[2], edgecolor='white', align='center', label=r'$\mu\mu$ channel')
        plt.xticks(xpos, selections, rotation=20., fontsize=8)
    
        ax.set_ylabel('#Events')
        plt.legend(bbox_to_anchor=([0.55, 1, 0, 0]),frameon=True)
        plt.title(r'$MH={} GeV, MA={} GeV, tan\beta ={}$'.format(MH, MA, tb), loc='center')
        plt.gca().yaxis.grid(True)
        plt.tight_layout()
        plt.savefig('{}/{}/results/Cutflow/{}_MH-{}_MA-{}_tb-{}_cuflow.png'.format(PATHBASE, options.path, suffix, MH, MA, tb))
        plt.gcf().clear()

if __name__ == '__main__':
    
    PATHBASE ="/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/NanoGen/"
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-p', '--path', action='store', type=str, help= 'Path to bamboo Output dir')
    options = parser.parse_args()
    computeefficiencies (PATHBASE, path=options.path) 
