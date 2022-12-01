#!/bin/env python
import os, os.path, sys
import json
import argparse
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.colors as colors
import matplotlib.pyplot as plt

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

def scatter_mH_vs_mA():
    
    for plot in plots:
        
        logger.info('=============='*10)
        logger.info('working on %s plot :: this may take some time' % plot)
        print( jsF )
        
        try:
            xrange
        except NameError:
            xrange = range
        
        if plot == 'theory':
            fig = plt.figure(1, figsize=(7, 7), dpi=300)
            ax  = fig.add_subplot(111)
            CMSStyle.changeFont()
            
            x = theory['mA']
            y = theory['mH']
            z = [theory['sigma'][i] * 1000. * theory['BR'][i] for i,z in enumerate(theory['sigma'])]
            
            x = np.asarray(x)
            y = np.asarray(y)
            z = np.asarray(z)
            
            xmin = 30.
            ymin = 120.
            xmax = ymax = 1010
        
            hb = ax.scatter(x, y, c=z,
                #gridsize=68,
                cmap='coolwarm',
                #norm=LogNorm(vmin=z.min(), vmax=z.max())
                norm=LogNorm(vmin=pow(10,-3), vmax=pow(10,3))
                )
            ax.axis([xmin, xmax, ymin, ymax])
            ax.set_title(r'2HDM Type II, tan($\beta$) = 1.5, cos($\beta-\alpha$) = 0.01, H$\to$ZA')
            bounds = [pow(10,i) for i in xrange(-3,4)]
            cb = fig.colorbar(hb, ax=ax, ticks=bounds)#, extend='min')
            cb.set_label(r'$\sigma(pp\to ZA)\times B(Z\to ll) \times B(A\to bb)$  (fb)')
            plt.xlabel(r'$m_A$ (GeV)', horizontalalignment='right', x=1.0)
            plt.ylabel(r'$m_H$ (GeV)', horizontalalignment='right', y=1.0)
            fig.tight_layout()
            #ax.grid()
    
        if plot == 'expected':
           
            fig = plt.figure(1, figsize=(8, 7), dpi=300)
            fig.tight_layout()
            ax = fig.add_subplot(111)
            fig.subplots_adjust(left=0.17)
            CMSStyle.applyStyle(fig, ax, Constants.getLuminosity(options.era), figures=1)
    
            x = []
            y = []
            z = []
            for l in all_limits:
                x.append(l['parameters'][1])
                y.append(l['parameters'][0])
                z.append(l['limits']['expected']*1000)
            
            x = np.asarray(x).astype(float)
            y = np.asarray(y).astype(float)
            z = np.asarray(z)
            
            xy = np.array([np.array([x[i], y[i]]) for i in xrange(x.size)])
            
            xmin = 30.
            ymin = 30.
            xmax = ymax = 1050
            
            # For now: perform interpolation of the limits:
            interp_x  = np.arange(x.min(), x.max(), 10)
            interp_y  = np.arange(y.min(), y.max(), 10)
            interp_xy = np.array([np.array([interp_x[i], interp_y[j]]) for i in xrange(interp_x.size) for j in xrange(interp_y.size)])
            interp_z  = interpolate.griddata(xy, z, interp_xy, method='linear', fill_value=pow(10,-3))
        
            if Interpolate:
                hb = ax.scatter(interp_xy[:,0], interp_xy[:,1], c=interp_z,
                    alpha=0.6,
                    #gridsize=50,
                    cmap=cmap,
                    norm=LogNorm(vmin=c.min(), vmax=c.max()),
                    )
            #Plot
            plt.scatter(x, y,
                        edgecolors = 'none',
                        norm=LogNorm(vmin=z.min(), vmax=z.max()),
                        c = z,
                        s = 50,
                        cmap=cmap)
           # hb = ax.scatter(x, y, c=z,
           #     #gridsize=50,
           #     cmap=cmap,
           #     norm=LogNorm(vmin=z.min(), vmax=z.max()),
           #     )
            
            ax.axis([xmin, xmax, ymin, ymax])
            #ax.set_title(r'2HDM Type II, tan($\beta$) = 1.5, cos($\beta-\alpha$) = 0.01, H$\to$ZA')
            bounds = [pow(10,i) for i in xrange(-3,4)]
            print( bounds)
            
            cb = plt.colorbar()#ax=ax, ticks=bounds)#, extend='min')
            cb.set_label(r'95% C.L. limit on $\sigma(pp \to H)$ (fb)')#\times B(Z\to ll) \times B(A\to bb)$  (fb)')
            plt.xlabel(r'$m_A$ (GeV)', horizontalalignment='right', x=1.0)
            plt.ylabel(r'$m_H$ (GeV)', horizontalalignment='right', y=1.0)
            
            t = r'''
            2HDM Type-II, 
            tan$\beta$= {}, cos($\beta-\alpha$)= 0.01,
            {},
            {}{}
            '''.format(tb, process, nb, region)
            plt.text(300, 70, t,
                    style='italic', weight='bold', size='small')
            #ax.grid()
    
        if plot == 'expected_over_theory':
            fig = plt.figure(1, figsize=(8, 12), dpi=300)
            ax = fig.add_subplot(111)
            CMSStyle.changeFont()
            
            x = []
            y = []
            z = []
            for l in all_limits:
                x.append(l['parameters'][1])
                y.append(l['parameters'][0])
                z.append(l['limits']['expected']*1000)
            x = np.asarray(x)
            y = np.asarray(y)
            z = np.asarray(z)
            for zval in z:
                print (zval)
            xy = np.array([np.array([x[i], y[i]]) for i in xrange(x.size)])
            
            xmin = 30.
            ymin = 120.
            xmax = ymax = 1010
    
            th_x = theory['mA']
            th_y = theory['mH']
            th_z = [theory['sigma'][i] * 1000. * theory['BR'][i] for i in xrange(len(theory['sigma']))]
            th_xy = np.array([np.array([th_x[i], th_y[i]]) for i in xrange(len(theory['sigma']))])
            th_x = np.asarray(th_x)
            th_y = np.asarray(th_y)
            th_z = np.asarray(th_z)
            # for convenience: interpolate also theory predictions to have matching grids
            th_X = np.arange(th_x.min(), 1010, 10)
            th_Y = np.arange(th_y.min(), 1010, 10)
            th_XY = np.array([np.array([th_X[i], th_Y[j]]) for i in xrange(len(th_X)) for j in xrange(len(th_Y))])
            # trying out griddata (https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html)
            th_Z = interpolate.griddata(th_xy, th_z, th_XY, method='linear', fill_value=pow(10,-4))
            # For now: perform interpolation of the limits:
            interp_x = np.arange(th_x.min(), 1010, 10)
            interp_y = np.arange(th_y.min(), 1010, 10)
            interp_xy = np.array([np.array([interp_x[i], interp_y[j]]) for i in xrange(interp_x.size) for j in xrange(interp_y.size)])
            interp_z = interpolate.griddata(xy, z, interp_xy, method='linear', fill_value=pow(10,-3))
    
            # the actual ratio 
            Z = np.divide(interp_z, th_Z)
            # clean up lower half of the plot
            cond = (th_XY[:,0] < th_XY[:,1])
            th_XY = th_XY[cond]
            Z = Z[cond]
            th_Z = th_Z[cond]
            interp_z = interp_z[cond]
    
            hb = ax.scatter(
               # interp_xy[:,0], interp_xy[:,1], C=interp_z,
                th_XY[:,0], th_XY[:,1], c=Z,
                #gridsize=50,
                cmap='coolwarm',
                norm=LogNorm(vmin=pow(10,-3), vmax=pow(10,3))
                )
            #plt.tricontour(th_XY[:,0], th_XY[:,1], th_Z)
            #plt.tricontour(th_XY[:,0], th_XY[:,1], interp_z)
            plt.tricontour(th_XY[:,0], th_XY[:,1], Z, [1], colors='black', linestyles='dashed')
            ax.axis([xmin, xmax, ymin, ymax])
            ax.set_title(r'2HDM Type II, tan($\beta$) = 1.5, cos($\beta-\alpha$) = 0.01, H$\to$ZA')
            bounds = [pow(10,i) for i in xrange(-3,4)]
            cb = fig.colorbar(hb, ax=ax, ticks=bounds)#, extend='min')
            cb.set_label(r'$95\%\,C.L.\,on\,\sigma_{expected}\,/\,\sigma_{theory}$')
            plt.xlabel(r'$m_A$ (GeV)', horizontalalignment='right', x=1.0)
            plt.ylabel(r'$m_H$ (GeV)', horizontalalignment='right', y=1.0)
            fig.tight_layout()
            #ax.grid()
    
        if fig:
            figNm = '{}/{}_{}'.format(plot_dir, pNm, plot)
            fig.savefig(figNm+'.pdf')
            fig.savefig(figNm+'.png')
            print ( 'plots is saved in ::', figNm+'.pdf')
            print ( 'plots is saved in ::', figNm+'.png')
            # clean the figure before next plot
            plt.gcf().clear()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Draw 2D mass scan')
    parser.add_argument('-p', '--jsonpath', action='store', type=str, required=True,
                help='JSON file containing the limits for all the points (Combined channel)')
    parser.add_argument('--unblind', action='store_true', dest='unblind', help='If set, draw also observed upper limits')
    parser.add_argument('--era', type=str, default=False, required=True, help='data taking of the given limits')
    parser.add_argument('--tanbeta', action='store', type=float, default=None, required=False, help='')
    parser.add_argument('--_2POIs_r', action='store_true', dest='_2POIs_r', required=False, default=True,
                help='This will merge both signal in 1 histogeram and normalise accoridngly, tanbeta will be required')
    parser.add_argument('--expectSignal', action='store', required=False, type=int, default=1, choices=[0, 1],
                help=' Is this S+B or B-Only fit? ')

    options = parser.parse_args()
    
    catagories = OrderedDict({
        # 'ggH_nb2_resolved'        : [['MuMu_ElEl_MuEl'],     'ggH', '$nb2$-',        'resolved'],
        # 'ggH_nb2_boosted'         : [['OSSF_MuEl'],          'ggH', '$nb2$-',        'boosted' ],
        # 'ggH_nb3_resolved'        : [['MuMu_ElEl_MuEl'],     'ggH', '$nb3$-',        'resolved'],
        # 'ggH_nb3_boosted'         : [['OSSF_MuEl'],          'ggH', '$nb3$-',        'boosted' ],
        'ggH_nb2PLusnb3_resolved'   : [['OSSF', 'OSSF_MuEl'],  'ggH', 'nb2+nb3, ',     'resolved'],
        'ggH_nb2PLusnb3_boosted'    : [['OSSF', 'OSSF_MuEl'],  'ggH', 'nb2+nb3, ',     'boosted' ],             
    
        # 'bbH_nb2_resolved'        : [['OSSF_MuEl'],          'bbH', '$nb2$-',        'resolved'],
        # 'bbH_nb2_boosted'         : [['OSSF_MuEl'],          'bbH', '$nb2$-',        'boosted' ],
        # 'bbH_nb3_resolved'        : [['OSSF_MuEl'],          'bbH', '$nb3$-',        'resolved'],
        # 'bbH_nb3_boosted'         : [['OSSF_MuEl'],          'bbH', '$nb3$-',        'boosted' ],
        'bbH_nb2PLusnb3_resolved'   : [['OSSF', 'OSSF_MuEl'],  'bbH', 'nb2+nb3, ',     'resolved'],             
        'bbH_nb2PLusnb3_boosted'    : [['OSSF', 'OSSF_MuEl'],  'bbH', 'nb2+nb3, ',     'boosted' ],   
        
        # combination 1 reso +boo  
        'ggH_nb2PLusnb3_resolved_boosted': [['OSSF', 'OSSF_MuEl'], 'ggH', 'nb2+nb3, ', 'resolved + boosted'],
        'bbH_nb2PLusnb3_resolved_boosted': [['OSSF', 'OSSF_MuEl'], 'bbH', 'nb2+nb3, ', 'resolved + boosted'],
    })
    
    
    plots = [
        #'theory',
        'expected',
        #'expected_over_theory'
        ]
    
    Interpolate = False
    
    
    poi_dir, tb_dir, cl = Constants.locate_outputs("asymptotic", options._2POIs_r, options.tanbeta, options.expectSignal)
    
    jsonpath   = os.path.join(options.jsonpath, poi_dir, tb_dir)
    output_dir = jsonpath
    
    plot_dir   = os.path.join(output_dir, '2D_mH.vs.mA_scatter')
    if not os.path.isdir(plot_dir):
        os.makedirs(plot_dir)
    
   # cmap=plt.cm.get_cmap('jet')
   # cmap='coolwarm'
   # cmap='Purples'
   # cmap='twilight_shifted'
   # cmap='cividis'
   # cmap='viridis'
   # cmap='RdBu_r'
    cmap='RdBu'

    for cat, Cfg in catagories.items():
        
        flavors, prod, nb, region = Cfg

        for flav in flavors:
            jsF = os.path.join(jsonpath, 'combinedlimits_{}_{}_{}_UL{}.json'.format(cat, flav, cl, options.era))
            
            jsFname = jsF.split('/')[-1].replace('.json', '') 
            pNm     = jsFname
            process = "gg-fusion" if "ggH" in jsFname else "b-associated production"
            tb      = '1.5' if 'ggH' in jsFname else '20.'
            
            if not os.path.isfile(jsF):
                continue
            
            with open(jsF) as f:
                all_limits = json.load(f)
            
            scatter_mH_vs_mA()
