
#!/bin/env python
import os, os.path, sys
import json
import yaml
import argparse
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.colors as colors
import matplotlib.pyplot as plt

from matplotlib import ticker, cm
from matplotlib.colors import LogNorm
from collections import OrderedDict
from scipy import interpolate
from packaging import version


if version.parse(mpl.__version__) >= version.parse('2.0.0'):
    # Override some of matplotlib 2 new style
    mpl.rcParams['grid.color'] = 'k'
    mpl.rcParams['grid.linestyle'] = 'dotted'
    mpl.rcParams['grid.linewidth'] = 0.5

    mpl.rcParams['figure.figsize'] = [8.0, 4.0]
    mpl.rcParams['figure.dpi'] = 80
    mpl.rcParams['savefig.dpi'] = 100

    mpl.rcParams['font.size'] = 12
    mpl.rcParams['legend.fontsize'] = 'large'
    mpl.rcParams['figure.titlesize'] = 'medium'

    mpl.rcParams['lines.linewidth'] = 1.0
    mpl.rcParams['lines.dashed_pattern'] = [6, 6]
    mpl.rcParams['lines.dashdot_pattern'] = [3, 5, 1, 5]
    mpl.rcParams['lines.dotted_pattern'] = [1, 3]
    mpl.rcParams['lines.scale_dashes'] = False


import utils.CMSStyle as CMSStyle
import Constants as Constants
logger = Constants.ZAlogger(__name__)


def get_branchingratio(dict_, m_heavy, m_light, process, mode, tb):
    br_Ztoll = 0.067264
    heavy    = mode[0]
    light    = mode[-1]

    given_mass = dict_[mode]['M{}_{}_M{}_{}_tb_{}'.format(heavy, float(m_heavy), light, float(m_light), tb)]
    
    br_HeavytoZlight = given_mass['branching-ratio']['{}ToZ{}'.format(heavy, light)]
    br_lighttobb     = given_mass['branching-ratio']['{}Tobb'.format(light)]
    
    if br_HeavytoZlight is None or br_lighttobb is None:
        return None
    else:
        return float(br_HeavytoZlight) * br_Ztoll* float(br_lighttobb)


parser = argparse.ArgumentParser(description='Draw 2D tb vs mass')
parser.add_argument('-p', '--jsonpath', action='store', type=str, required=True,
                help='JSON file containing the limits for all the points (Combined channel)')
parser.add_argument('--unblind', action='store_true', dest='unblind', help='If set, draw also observed upper limits')
parser.add_argument('--era', type=str, required=True, help='data taking of the given limits')
parser.add_argument('--interpolate', action='store_true', default=False, help='')
parser.add_argument('--_2POIs_r', action='store_true', dest='_2POIs_r', required=False, default=True,
            help='This will merge both signal in 1 histogeram and normalise accoridngly, tanbeta will be required')
parser.add_argument('--tanbeta', action='store', type=float, default=None, required=False, help='')
parser.add_argument('--expectSignal', action='store', required=False, type=int, default=1, choices=[0, 1],
            help=' Is this S+B or B-Only fit? ')
parser.add_argument('--fix', type=str, choices=['mH', 'mA'], required=True, help='2hdm mass to fix ')
parser.add_argument('--mass', type=float, required=True, help='to which value the above mass need to be fixed ?')


options = parser.parse_args()

if options.fix == 'mH': 
    pave        = 'mA'
    idx_mtofix  = 0
    idx_mtopave = 1 
else: 
    pave        = 'mH'
    idx_mtofix  = 1
    idx_mtopave = 0 


cmap='RdBu'
cmap='viridis'
Interpolate = True#options.interpolate

poi_dir, tb_dir, cl = Constants.locate_outputs("asymptotic", options._2POIs_r, options.tanbeta, options.expectSignal)

jsonpath   = os.path.join(options.jsonpath, poi_dir, tb_dir)
plot_dir   = os.path.join(jsonpath, '2D_tb.vs.2hdm_masses_matplotlib')
if not os.path.isdir(plot_dir):
        os.makedirs(plot_dir)

plots = [
    #'theory',
    #'expected_over_theory',
    'expected', 
    ]

catagories = OrderedDict({
   # 'ggH_nb2_resolved'        : [['MuMu_ElEl_MuEl'],    'ggH', '$nb2$-',        'resolved'],
   # 'ggH_nb2_boosted'         : [['OSSF_MuEl'],         'ggH', '$nb2$-',        'boosted' ],
   # 'ggH_nb3_resolved'        : [['MuMu_ElEl_MuEl'],    'ggH', '$nb3$-',        'resolved'],
   # 'ggH_nb3_boosted'         : [['OSSF_MuEl'],         'ggH', '$nb3$-',        'boosted' ],
    'ggH_nb2PLusnb3_resolved'  : [['OSSF', 'OSSF_MuEl'], 'ggH', 'nb2+nb3, ',     'resolved'],
    'ggH_nb2PLusnb3_boosted'   : [['OSSF', 'OSSF_MuEl'], 'ggH', 'nb2+nb3, ',     'boosted' ],             
    
   # 'bbH_nb2_resolved'        : [['OSSF_MuEl'],         'bbH', '$nb2$-',        'resolved'],
   # 'bbH_nb2_boosted'         : [['OSSF_MuEl'],         'bbH', '$nb2$-',        'boosted' ],
   # 'bbH_nb3_resolved'        : [['OSSF_MuEl'],         'bbH', '$nb3$-',        'resolved'],
   # 'bbH_nb3_boosted'         : [['OSSF_MuEl'],         'bbH', '$nb3$-',        'boosted' ],
    #'bbH_nb2PLusnb3_resolved'  : [['OSSF', 'OSSF_MuEl'], 'bbH', 'nb2+nb3, ',     'resolved'],             
    #'bbH_nb2PLusnb3_boosted'   : [['OSSF', 'OSSF_MuEl'], 'bbH', 'nb2+nb3, ',     'boosted' ],   
    
    # combination 1 reso +boo  
    #'ggH_nb2PLusnb3_resolved_boosted': [['OSSF', 'OSSF_MuEl'], 'ggH', 'nb2+nb3, ', 'resolved + boosted'],
    #'bbH_nb2PLusnb3_resolved_boosted': [['OSSF', 'OSSF_MuEl'], 'bbH', 'nb2+nb3, ', 'resolved + boosted'],
    })
    


with open("data/2hdmc1.8.0-br_cba-0.01_mAorH-{}_2hdm-type2.yml".format(options.mass)) as f_:
    dict_ = yaml.safe_load(f_)

for plot in plots:
    if plot in ['theory', 'expected_over_theory']:
        print( 'WIP')
    else:
        for cat, Cfg in catagories.items():

            flavors, prod, nb, region = Cfg    
            process = "gg_fusion" if prod =="ggH" else "b-associated_production"
            
            for flav in flavors:
                
                fig = plt.figure(1, figsize=(8, 8), dpi=300)
                fig.subplots_adjust(left=0.17)
                fig.tight_layout()
                ax = fig.add_subplot(111)
                
                CMSStyle.applyStyle(fig, ax, Constants.getLuminosity(options.era), figures=1)
                
                jsF = os.path.join(jsonpath, 'combinedlimits_{}_{}_{}_UL{}.json'.format(cat, flav, cl, options.era))
                jsFname = jsF.split('/')[-1].replace('.json', '') 
                pNm     = jsFname 
                if not os.path.isfile(jsF):
                    continue
                
                logger.info('# working on :: %s %s %s'% (cat, flav, region))

                all_limits = []
                with open(jsF) as f:
                    all_limits = json.load(f)
                
                if not all_limits:
                    continue
                print( jsF)

                x = []
                y = []
                z = []
                z_obs = []
                
                for l in all_limits:
                    if l['parameters'][idx_mtofix] != str(options.mass):
                        continue
                    
                    mTopave = float(l['parameters'][idx_mtopave])
                    mTofix  = options.mass
                    
                    for tb in np.arange(0.05, 50.5, 0.5):
                        if mTopave < mTofix:
                            heavy   = options.fix[-1]
                            light   = pave[-1]
                            m_heavy = mTofix
                            m_light = mTopave
                        else:
                            heavy   = pave[-1]
                            light   = options.fix[-1]
                            m_heavy = mTopave
                            m_light = mTofix

                        mode = '{}ToZ{}'.format(heavy, light) 
                        BR   = get_branchingratio(dict_, m_heavy, m_light, process, mode, tb)
                        if BR is None:
                            continue
                        
                        y.append(tb)
                        x.append(mTopave) 
                    
                        limit_exp = l['limits']['expected']*1000/BR
                        #print('Expected limit 95% {} sigma x BR, tb= {} : {} fb // (m{}, m{})= ({}, {}) GeV'.format(cl, tb, limit_exp, heavy, light, m_heavy, m_light))
                        if options.unblind:
                            limit_obs = l['limits']['observed']*1000/BR
                            #print('Observed limit 95% {} sigma x BR, tb= {} : {} fb // (m{}, m{})= ({}, {}) GeV'.format(cl, tb, limit_exp, heavy, light, m_heavy, m_light))
                
                        z.append(limit_exp)
                        if options.unblind:
                            z_obs.append(limit_obs)
                
                x = np.asarray(x).astype(float)
                y = np.asarray(y).astype(float)
                z = np.asarray(z)
                if options.unblind:
                    z_obs = np.asarray(z_obs)
                
                xy = np.array([np.array([x[i], y[i]]) for i in xrange(x.size)])
                
                xmin = 0.
                ymin = 0.
                xmax = 500.
                ymax = 51.
                
                if Interpolate:
                    # For now: perform interpolation of the limits:
                    tointerp_x = np.linspace(x.min(), x.max(), 1000)
                    tointerp_y = np.linspace(y.min(), y.max(), 1000)
                    
                    interp_x, interp_y = np.meshgrid(tointerp_x, tointerp_y)
                    interp_z  = interpolate.griddata((x, y), z, (interp_x, interp_y), method='cubic')#, fill_value=pow(10,-3))
                    #plt.scatter(interp_xy[:,0], interp_xy[:,1], c=interp_z,
                    #    alpha=0.6,
                    #    s=50,
                    #    cmap=cmap,
                    #    norm=LogNorm(vmin=z.min(), vmax=z.max()),
                    #    )
                    cp = ax.contourf(interp_x, interp_y, interp_z, 
                            s=10000,    # the number of color levels in the heat-map
                            cmap=cmap, 
                            #norm=LogNorm(vmin=interp_z.min(), vmax=interp_z.max())
                            #norm=LogNorm(vmin=0, vmax=z.max())
                            #norm=LogNorm(vmin=10e-4, vmax=10e4)
                            )
                else:
                    #Plot
                    contour_levels = 20
                    contour_colors = 'gray'
                    contour_linewidths = 0.5
                    zzmin, zzmax = np.min(z), np.max(z)
                    norm = cm.colors.Normalize(vmin=zzmin, vmax=zzmax)
                    extent = (x.min(), x.max(), y.min(), y.max())
                    contours = []
                    contours.append(1.)
                    contours = np.asarray(contours)
                    cp = plt.scatter(x, y,
                            edgecolors = 'none',
                            c = z,
                            s = 50,
                            cmap=cmap,
                            #norm=LogNorm(vmin=z.min(), vmax=z.max())
                            norm=LogNorm(vmin=10e-4, vmax=10e4)
                            )
                    ax.contour(z, levels=contours, colors=contour_colors, linewidths=contour_linewidths)
                
                
                cbar = fig.colorbar(cp)
                cbar.set_label(r'95% C.L. limit on $\sigma(pp \to H) \times B(Z\to ll) \times B(A\to bb)$ (fb)')
                #cbar.locator = ticker.LogLocator(10)
                #cbar.set_ticks(cbar.locator.tick_values(interp_z.min(), interp_z.max()))
                #cbar.minorticks_off()
                #bounds = [pow(10,i) for i in xrange(-3,4)]
                #cbar   = plt.colorbar()#ax=ax, ticks=bounds)#, extend='min')

                ax.set(xlim=(xmin, xmax))#, ylim=(ymin, ymax))
                #ax.set_yscale('log')
                #ax.set_zscale('log')
                
                plt.xlabel(r'$m_%s$ (GeV)'%pave[-1], horizontalalignment='right', x=1.0)
                plt.ylabel(r'tan$\beta$', horizontalalignment='right', y=1.0)
                
                p = "gg-fusion" if prod=="ggH" else "b-associated production"
                t = r'''
                2HDM Type-II, 
                $m_{}$= {} GeV, cos($\beta-\alpha$)= 0.01,
                {},
                {} {}
                '''.format(options.fix[-1], int(options.mass), p, nb, region)
                plt.text(300, 10, t,
                        style='italic', weight='bold', size='small')
                #ax.grid()
                
                if fig:
                    figNm = '{}/{}_{}'.format(plot_dir, pNm, plot)
                    fig.savefig(figNm+'.pdf')
                    fig.savefig(figNm+'.png')
                    print ( 'plots is saved in ::', figNm+'.pdf')
                    print ( 'plots is saved in ::', figNm+'.png')
                    # clean the figure before next plot
                    plt.gcf().clear()
