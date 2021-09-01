import os, os.path, sys
import numpy as np
import matplotlib.pyplot as plt
import json
import glob 
import argparse
from collections import defaultdict

def string_to_mass(s):
    m = float(s.replace('p', '.'))
    return m

colors = ['blue', 'purple', 'aquamarine', 'crimson', 'turquoise', 'forestgreen', 'pink', 'magenta', 'indigo', 'limegreen', 'blueviolet', 'plum', 'purple', 'hotpink', 'mediumseagreen', 'springgreen', 'aquamarine', 'turquoise', 'aqua', 'mediumslateblue', 'orchid', 'deeppink', 'darkturquoise', 'teal', 'mediumslateblue']
linestyles = ['-', '--', '-.', ':']


def Plot_Eff(path=None):

    PATHBASE ="/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/NanoGen/"
    
    lo_dics = {}
    nlo_dics = {}
    for i_f, fn in enumerate(glob.glob(os.path.join(PATHBASE, path, "results/Cutflow/", '*.json'))):

        split_filename = fn.split('/')
        split_filename = split_filename[-1]
        
        with open(fn) as data:
            if "amcatnlo" in split_filename:
                nlo_dics[split_filename] = json.load(data)
            else:
                lo_dics[split_filename] = json.load(data)
    
    fig= plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)
    
    nlo_dics_sorted = defaultdict(dict)
    for k in lo_dics.keys():
        nlo_dics_sorted[k.replace("13TeV", "13TeV-amcatnlo")]= nlo_dics[k.replace("13TeV", "13TeV-amcatnlo")]
    
    selec_vals   = defaultdict(dict) 
    SumW_vals    = defaultdict(dict) 
    Nevents_vals = defaultdict(dict)
    eff_vals     = defaultdict(dict)
    for cat in ["oslep"]:#"elel", "mumu", "elmu"]:

        for idx, dics in enumerate([lo_dics, nlo_dics]):
            for j, (smpNm, vals) in enumerate(sorted(dics.items())):
                
                print( smpNm, vals )

                MH = string_to_mass(smpNm.split('_')[2])
                MA = string_to_mass(smpNm.split('_')[3])
                tb = string_to_mass(smpNm.split('_')[4])
                
                process = "bbH4F@NLO" if "amcatnlo" in smpNm else "bbH4F@LO"
                legend ="{}, MH-{}_MA-{}_tb-{}".format(process, string_to_mass(str(MH)), string_to_mass(str(MA)), string_to_mass(str(tb)))
                
                selec_vals[cat]   = []
                SumW_vals[cat]    = []
                Nevents_vals[cat] = []
                eff_vals[cat]     = []
                
                SumW_tot = float(vals["total_generated_events"][0][2])
                for i, list in enumerate(vals[cat]):

                    selec_vals[cat].append(list[0])
                    Nevents_vals[cat].append(float(list[1]))
                    
                    SumW_pass = float(list[2])
                    SumW_vals[cat].append(float(list[2]))
                   
                    
                    eff_vals[cat].append(SumW_pass/SumW_tot)
                eff = eff_vals[cat] +[1.] 
                sorted_cuts = ['generated_events', '2 OSSF Leptons', '>= 3GenJets', '>= 3GenBJets']
                print( " warning : be careful , watch out your selection , xtick labes done manually ") 
                ax.plot(sorted_cuts, sorted(eff, reverse=True), "o", linestyle=linestyles[idx], color=colors[j], label="%s"%legend)
        
        plt.title('CMS Preliminary', fontsize=12., loc='left')
        ax.set_xticks([0., 1., 2., 3.])
        ax.set_xticklabels(sorted_cuts, rotation=20., fontsize=8)
        ax.set_ylabel("Efficiencies @mcatnlo vs lo ")
        plt.legend(loc="best")
        
        fig.savefig("plots/eff_{}.png".format(cat))
        print ("plot saved in : plots/eff_{}.png".format(cat))
        plt.gcf().clear()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--path', required=True, help='bamboo output dir ')
    options = parser.parse_args()
    
    Plot_Eff(path=options.path)
