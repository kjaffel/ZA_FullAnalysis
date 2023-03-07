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


def Plot_Eff(path= None, eff_x_acc_vs_mH= False):

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
    
    selec_vals    = defaultdict(dict) 
    SumW_vals     = defaultdict(dict) 
    Nevents_vals  = defaultdict(dict)
    eff_vals      = defaultdict(dict)
    acc_vals      = defaultdict(dict)
    mH_vals       = defaultdict(dict)
    eff_X_acc_vals= defaultdict(dict)

    for cat in ["oslep"]:#"elel", "mumu", "elmu"]:
        for idx, dics in enumerate([lo_dics, nlo_dics]):
            mH_vals[cat]        = []
            eff_X_acc_vals[cat] = []
            for j, (smpNm, vals) in enumerate(sorted(dics.items())):
                
                #print( smpNm, vals )

                MH = string_to_mass(smpNm.split('_')[2])
                MA = string_to_mass(smpNm.split('_')[3])
                tb = string_to_mass(smpNm.split('_')[4])
                
                mH_vals[cat].append(MH)
                
                process = "bbH4F@NLO" if "amcatnlo" in smpNm else "bbH4F@LO"
                
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
                sorted_eff = sorted(eff, reverse=True)
                sorted_cuts = ['generated_events', '2 OSSF Leptons', '>= 3GenJets', '>= 3GenBJets']
                acc = sorted_eff[2]
                eff_X_acc_vals[cat].append(sorted_eff[3]*acc)
                print( " warning : be careful , watch out your selection , xtick labes done manually ") 
                
                if not eff_x_acc_vs_mH:
                    legend ="{}, MH-{}_MA-{}_tb-{}".format(process, string_to_mass(str(MH)), string_to_mass(str(MA)), string_to_mass(str(tb)))
                    ax.plot(sorted_cuts, sorted_eff, "o", linestyle=linestyles[idx], color=colors[j], label="%s"%legend)
                

            order = "LO" if idx==0 else "NLO"
            channel = "bbH, $OSSF-leptons$" if cat =="oslep" else "bbH, ${}$".format(cat.upper())
            if eff_x_acc_vs_mH:
                legend = "{}".format(order)
                ax.plot(mH_vals[cat], eff_X_acc_vals[cat], "o", linestyle=linestyles[idx], color=colors[idx], label="%s"%legend)

        plt.title('CMS Simulation Preliminary', fontsize=14., weight='bold', loc='left')
        plt.title('$\sqrt{s}= 13TeV, 139fb{-1}$', fontsize=14., weight='bold', loc='right')
        plt.legend(fontsize=14., loc="best", frameon=False)
        plt.gca().get_legend().set_title(channel)  
        if eff_x_acc_vs_mH:
            ax.set_ylabel("Acceptance x Efficiency", fontsize=14.)
            ax.set_xlabel("$M_{H} [GeV]$", fontsize=14.)
        else:
            ax.set_xticks([0., 1., 2., 3.])
            ax.set_xticklabels(sorted_cuts, rotation=20., fontsize=14.)
            ax.set_ylabel("Efficiencies @mcatnlo vs lo ", fontsize=14.)
        
        suffix = 'eff_x_acc_vs_mH' if eff_x_acc_vs_mH else 'eff'
        fig.savefig("plots/{}_{}.png".format(suffix, cat))
        print ("plot saved in : plots/{}_{}.png".format(suffix, cat))
        plt.gcf().clear()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--path', required=True, help='bamboo output dir ')
    parser.add_argument('-acc', '--acceptance', action='store_true', default= True, 
            help='Acceptance times efficiency for the full analysis selection as a function of the resonance mass mH')
    options = parser.parse_args()
    
    Plot_Eff(path= options.path, eff_x_acc_vs_mH= options.acceptance)
