import json
import os, os.path, sys

import matplotlib.pyplot as plt


def getLimits(dir):
    data = {}
    for p in [ 'ggH', 'bbH']:
        data[p] = {}
        for flav in ['OSSF', 'OSSF_MuEl']:
            data[p][flav] = {}
            limits_per_reg ={}
            for i, reg in enumerate(['resolved', 'boosted', 'resolved_boosted']):
                fNm = f'combinedlimits_{p}_nb2PLusnb3_{reg}_{flav}_CLs_ULfullrun2.json'
                if not os.path.exists(os.path.join(dir, fNm)):
                    continue
                
                with open(os.path.join(dir, fNm)) as f:
                    limits = json.load(f)
                
                for l in limits:
                    params = l['parameters']
                    if not (params[0], params[1]) in data[p][flav].keys():
                        data[p][flav][(params[0], params[1])] ={}
                    data[p][flav][(params[0], params[1])].update({reg: l})
    return data




if __name__ == "__main__":

    dir = '../hig-22-010/datacards_nosplitJECs/work__ULfullrun2/bayesian_rebin_on_S/asymptotic-limits__very_good_xbr/dnn/jsons/2POIs_r'
    data = getLimits(dir)
    
    colors  = ['cyan', 'purple', 'chocolate']
    regions = ['resoved', 'boosted', 'resolved_boosted']

    for p, d_per_flav in data.items():
        
        fig= plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111)
        
        for flav, d_per_reg in d_per_flav.items():
            # create fixed legend
            for i in range(3): 
                plt.plot([0.], [0.], 'o', color=colors[i], label=regions[i])
            
            for i, (params, l) in enumerate(d_per_reg.items()):
               
                if not 'resolved' in l.keys() or not 'boosted' in  l.keys() or not 'resolved_boosted' in l.keys():
                    continue
                expected0 = l['resolved']['limits']['expected']*1000
                expected1 = l['boosted']['limits']['expected']*1000
                expected3 = l['resolved_boosted']['limits']['expected']*1000
                
                li_      = [expected0, expected1, expected3 ]
                winner   = li_.index(min(li_))
                color    = colors[winner]
                m_heavy  = float(params[0])
                m_light  = float(params[1])
                
                print( p, flav )
                print( (m_heavy, m_light), li_, 'winner', regions[winner])
                
                plt.plot([m_light], [m_heavy], 'o', color=color)#, label=regions)
            print( '*'*10)

            plt.xlim(0., 1000.)
            plt.ylim(0., 1050.)
    
            plt.xlabel(r'$M_{A} [GeV]$', fontsize=12)
            plt.ylabel(r'$M_{H} [GeV]$', fontsize=12)
    
            plt.title(r"{} 2HDM typeII, run2 ULegacy best expected upper limits at 95% CLs".format(p))
            plt.legend(loc='best')
    
            plt.grid(zorder = 0, alpha = 0.3)
    
            plt.tight_layout()
            plt.savefig(f'ZAmap_forBestLimitsscan_{p}_{flav}.png')
            plt.gcf().clear()

