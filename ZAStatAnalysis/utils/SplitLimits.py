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


def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]


if __name__ == "__main__":

    dir = '../hig-22-010/datacards_nosplitJECs/work__ULfullrun2/bayesian_rebin_on_S/asymptotic-limits__very_good_xbr/dnn/jsons/2POIs_r'
    data = getLimits(dir)
    
    colors  = {'resolved': 'cyan', 
               'boosted': 'purple',
               'resolved_boosted': 'chocolate' }

    for p, d_per_flav in data.items():
        
        fig= plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111)
        
        for flav, d_per_reg in d_per_flav.items():
            # create fixed legend
            for r, c  in colors.items(): 
                plt.plot([0.], [0.], 'o', color=c, label=r)
            
            for i, (params, l) in enumerate(d_per_reg.items()):
               
                if not 'resolved' in l.keys() or not 'boosted' in  l.keys() or not 'resolved_boosted' in l.keys():
                    continue

                expected = { 'resolved': l['resolved']['limits']['expected']*1000,
                             'boosted' : l['boosted']['limits']['expected']*1000,
                             'resolved_boosted': l['resolved_boosted']['limits']['expected']*1000 }
                
                if expected['resolved'] == expected[ 'resolved_boosted']:
                    winner = 'resolved'
                elif expected['boosted'] == expected[ 'resolved_boosted']:
                    winner = 'boosted'
                else:
                    li_      = sorted(expected.values())
                    _1st_min = li_[0]
                    _2nd_min = li_[1]
                    winner   = get_keys_from_value(expected, _1st_min)[0]
                    if (_2nd_min - _1st_min) < 1 and winner== 'resolved_boosted': 
                        # 2nd min is just 2fb-1 larger than the 1st min, is not worth the combination
                        winner = get_keys_from_value(expected, _2nd_min)[0]

                color    = colors[winner]
                m_heavy  = float(params[0])
                m_light  = float(params[1])
                
                print( p, flav, (m_heavy, m_light), expected, 'winner', winner)
                
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

