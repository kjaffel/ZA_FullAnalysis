#! /bin/env python
import os, sys, argparse
import copy
import glob
import json
import yaml

import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.transforms as transforms

from matplotlib.font_manager import FontProperties
from collections import OrderedDict
from packaging import version

if version.parse(mpl.__version__) >= version.parse('2.0.0'):
    # Override some of matplotlib 2 new style
    mpl.rcParams['grid.color']            = 'k'
    mpl.rcParams['grid.linestyle']        = 'dotted'
    mpl.rcParams['grid.linewidth']        = 0.5
    mpl.rcParams['figure.figsize']        = [8.0, 8.0]
    mpl.rcParams['figure.dpi']            = 1200
    mpl.rcParams['savefig.dpi']           = 100
    mpl.rcParams['font.size']             = 12
    mpl.rcParams['legend.fontsize']       = 'large'
    mpl.rcParams['figure.titlesize']      = 'medium'
    mpl.rcParams['lines.linewidth']       = 1.0
    mpl.rcParams['lines.dashed_pattern']  = [6, 6]
    mpl.rcParams['lines.dashdot_pattern'] = [3, 5, 1, 5]
    mpl.rcParams['lines.dotted_pattern']  = [1, 3]
    mpl.rcParams['lines.scale_dashes']    = False

import Constants as Constants
import utils.CMSStyle as CMSStyle


th_files = [
    #'sigmaBR_HZA_type-2_tb-0p5_cba-0p01.json',
    #'sigmaBR_HZA_type-2_tb-1p0_cba-0p01.json',
    'data/sigmaBR_HZA_type-2_tb-1p5_cba-0p01.json',
    ]

th_colors  = ['red', 'firebrick', 'salmon']
th_hatches = ['xxx', '+++', '...']
parameters = ['mH', 'mA']

parameter_callPoints = {
    "mH": None,
    "mA": None,
    }
parameter_axis_legend = {
    'mH': r'm_H (GeV)',
    'mA': r'm_A (GeV)',
    }
parameter_legend = {
    'mH': r'm_H (GeV)',
    'mA': r'm_A (GeV)',
    }
parameter_index = {
    "mH": 0,
    "mA": 1,
    }
default_values = {
    "mH": 500,
    "mA": 300,
    }
sm_label_position = {
    "mH": (1.8, 0.95),
    "mA": (0.88, 0.02),
    }
axes_x_limits = {
    "mH": { 'left':   0, 'right': 1000 },
    "mA": { 'left':   0, 'right': 1000 },
    }
axes_y_limits = {
    "mH": {},
    "mA": {'ymin': 0, 'ymax':1000}, 
    }
axes_log_y_limits = {
    "mH": { },
    #"mA": {'ymin': 10e-2, 'ymax':10e6},
    "mA": {'ymin': 10e-3, 'ymax':10e5},
    }
show_markers = {
    'mH': False,
    'mA': True
    }
colors = {
    'MuMu'     : '#7040f5',
    'ElEl'     : '#ff7f0e',
    'OSSF'     : 'black',
    'MuMu_ElEl': 'black',
    'MuMu_MuEl': 'black',
    'ElEl_MuEl': 'black',
    'OSSF_MuEl': 'black',
    'MuMu_ElEl_MuEl': 'black',
    }
channels = {
    'ElEl'     : 'ee',
    'MuMu'     : '$\mu\mu$',
    'MuMu_ElEl': '$\mu\mu$ + ee',
    'OSSF'     : '$\mu\mu$ + ee',
    'ElEl_MuEl': 'ee + $\mu e$',
    'MuMu_MuEl': '$\mu\mu$ + $\mu e$',
    'OSSF_MuEl': '$\mu\mu$ + ee + $\mu e$',
    'MuMu_ElEl_MuEl': '($\mu\mu$ + ee) + $\mu e$',
    }
catagories = OrderedDict({
    'ggH_nb2_resolved'        : [['MuMu_ElEl_MuEl'],    'ggH', '$nb2$-',        'resolved'],
    'ggH_nb2_boosted'         : [['OSSF_MuEl'],         'ggH', '$nb2$-',        'boosted'],
    'ggH_nb3_resolved'        : [['MuMu_ElEl_MuEl'],    'ggH', '$nb3$-',        'resolved'],
    'ggH_nb3_boosted'         : [['OSSF_MuEl'],         'ggH', '$nb3$-',        'boosted'],
    'ggH_nb2PLusnb3_resolved' : [['OSSF', 'OSSF_MuEl'], 'ggH', '$nb2+nb3$, ',   'resolved'],
    'ggH_nb2PLusnb3_boosted'  : [['OSSF_MuEl'],         'ggH', '$nb2+nb3$, ',   'boosted' ],             
    
    'bbH_nb2_resolved'        : [['OSSF_MuEl'],         'bbH', '$nb2$-',        'resolved'],
    'bbH_nb2_boosted'         : [['OSSF_MuEl'],         'bbH', '$nb2$-',        'boosted'],
    'bbH_nb3_resolved'        : [['OSSF_MuEl'],         'bbH', '$nb3$-',        'resolved'],
    'bbH_nb3_boosted'         : [['OSSF_MuEl'],         'bbH', '$nb3$-',        'boosted'],
    'bbH_nb2PLusnb3_resolved' : [['OSSF_MuEl'],         'bbH', '$nb2+nb3$, ',   'resolved'],             
    'bbH_nb2PLusnb3_boosted'  : [['OSSF_MuEl'],         'bbH', '$nb2+nb3$, ',   'boosted' ],   
    
    # combination 1 reso +boo  
    #'ggH_nb2PLusnb3_resolved_boosted': [['OSSF_MuEl'], 'ggH', '$nb2+nb3$, ', 'resolved_boosted'],
    #'bbH_nb2PLusnb3_resolved_boosted': [['OSSF_MuEl'], 'bbH', '$nb2+nb3$, ', 'resolved_boosted'],
    
    # combination 2 ggH +bbH 
        # the limits here set on the opposite process while _r_bbH or _r_ggH mentionned in the name of the file
        # means that that process left to float freely in the fit or freezed to a certain value
    #'freezed_r_bbH_nb2PLusnb3_boosted'          :[['OSSF', 'OSSF_MuEl'], 'ggH', '$nb2+nb3$, ', 'boosted' ],
    #'freezed_r_bbH_nb2PLusnb3_resolved'         :[['OSSF', 'OSSF_MuEl'], 'ggH', '$nb2+nb3$, ', 'resolved'],
    #'freezed_r_ggH_nb2PLusnb3_boosted'          :[['OSSF', 'OSSF_MuEl'], 'bbH', '$nb2+nb3$, ', 'boosted' ],
    #'freezed_r_ggH_nb2PLusnb3_resolved'         :[['OSSF', 'OSSF_MuEl'], 'bbH', '$nb2+nb3$, ', 'resolved' ],
    #'freezed_r_bbH_nb2PLusnb3_resolved_boosted' :[['OSSF', 'OSSF_MuEl'], 'ggH', '$nb2+nb3$, ', 'resolved_boosted'],
    #'freezed_r_ggH_nb2PLusnb3_resolved_boosted' :[['OSSF', 'OSSF_MuEl'], 'bbH', '$nb2+nb3$, ', 'resolved_boosted'],
    
    # combination 3
    #'profiled_r_bbH_nb2PLusnb3_boosted'          :[['OSSF', 'OSSF_MuEl'], 'ggH', '$nb2+nb3$, ', 'boosted' ],
    #'profiled_r_bbH_nb2PLusnb3_resolved'         :[['OSSF', 'OSSF_MuEl'], 'ggH', '$nb2+nb3$, ', 'resolved'],
    #'profiled_r_ggH_nb2PLusnb3_boosted'          :[['OSSF', 'OSSF_MuEl'], 'bbH', '$nb2+nb3$, ', 'boosted' ],
    #'profiled_r_ggH_nb2PLusnb3_resolved'         :[['OSSF', 'OSSF_MuEl'], 'bbH', '$nb2+nb3$, ', 'resolved' ],
    #'profiled_r_bbH_nb2PLusnb3_resolved_boosted' :[['OSSF', 'OSSF_MuEl'], 'ggH', '$nb2+nb3$, ', 'resolved_boosted'],
    #'profiled_r_ggH_nb2PLusnb3_resolved_boosted' :[['OSSF', 'OSSF_MuEl'], 'bbH', '$nb2+nb3$, ', 'resolved_boosted'],
    })


def get_SushiXSC(process, tb , heavy, light, m_heavy, m_light):
    br_Ztoll = 0.066 
    
    with open('data/sushi1.7.0-xsc_tanbeta-{}_2hdm-type2.yml'.format(float(tb))) as f_:
        dict_ = yaml.safe_load(f_)

    given_mass = dict_[thdm]['M{}_{}_M{}_{}'.format(heavy, float(m_heavy), light, float(m_light))]
    
    br_HeavytoZlight = given_mass['branching-ratio']['{}ToZ{}'.format(heavy, light)]
    br_lighttobb     = given_mass['branching-ratio']['{}Tobb'.format(light)]
    br = float(br_HeavytoZlight)* float(br_lighttobb)* br_Ztoll
    
    if process in ['ggH', 'ggA']: xsc  = given_mass['cross-section'][process].split()[0]
    else: xsc  = given_mass['cross-section'][process]['NLO'].split()[0]
    return float(xsc), br 


def PlotMultipleUpperLimits(m0, m1, catagories, jsonpath, thdm):
    mpl.rcParams['font.size'] = 10
    CMSStyle.changeFont()
    
    heavy = thdm[0]
    light = thdm[-1]
    
    name  = 'all_combined_M{}-{}_M{}-{}'.format(heavy, m0, light, m1)
    print( 'working on ::' , m0, m1)
    
    fig = plt.figure(1, figsize=(7, 7), dpi=300)
    fig.tight_layout()
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.17)
    
    CMSStyle.applyStyle(fig, ax, Constants.getLuminosity(options.era), figures=1)
    
    eras  = []
    yaxis = []
    yaxis_set_ticklabels = []
    limits = OrderedDict()
    
    th_lmax  = 0.
    for cat, Cfg in catagories.items():
        
        flavors, prod, nb, region = Cfg

        for flav in flavors:
            if not 'MuEl' in flav:
                continue
            for era in [2016, 2017, 2018, 'fullrun2']:
                
                th_lmax += 2.5
                js_path = os.path.join(jsonpath, 'combinedlimits_{}_{}_UL{}.json'.format(cat, flav, era))
                if not os.path.isfile(js_path):
                    continue
                
                print( js_path )
                with open(js_path) as f:
                    limits['{}-{}-{}-{}'.format(prod, region, flav, era)] = json.load(f)
    if not limits:
        print('no limits is found !')
        exit()

    theory_line = {} 
    print( limits.keys() )
    for i, (k, params) in enumerate(limits.items()):
       
        process = k.split('-')[0]
        region  = k.split('-')[1]
        flav    = k.split('-')[2]
        era     = k.split('-')[-1]
        tb      = 1.5 if process =='ggH' else 20.

        theory_line.update({process: {}})
        
        if era =='fullrun2':
            ticklabel = 'combined\n' + '%s%s\n'%(nb, region)+'%s'%channels[flav]
        else:
            ticklabel = 'UL%s\n'%era.replace('20','') + '%s%s\n'%(nb, region)+'%s'%channels[flav]

        yaxis_set_ticklabels.append(ticklabel)
        fact = 2
        if i == 0:
            y_ = np.arange(0., fact, 1)
        else:
            i += fact 
            y_ = np.arange(y_[-1]+0.5, y_[-1]+i, 1)
            y_ = y_[:fact]
        
        yaxis.append(y_[1])
       
        for l in params:
        
            m_heavy = l['parameters'][0]
            m_light = l['parameters'][1]
            
            if not (str(m_heavy) == str(m0) and str(m_light) == str(m1)):
                continue
            
            if not era in eras:
                eras.append(era)
            
            print( k, l )
            
            expected       = l['limits']['expected']*1000
            observed       = l['limits']['observed']*1000
            one_sigma_up   = l['limits']['one_sigma'][1]*1000
            one_sigma_down = l['limits']['one_sigma'][0]*1000
            two_sigma_up   = l['limits']['two_sigma'][1]*1000
            two_sigma_down = l['limits']['two_sigma'][0]*1000
        
            exp_plus_1sigma  = expected + one_sigma_up 
            exp_minus_1sigma = expected - one_sigma_down
            exp_plus_2sigma  = expected + two_sigma_up
            exp_minus_2sigma = expected - two_sigma_down
            
            if options.rescale_to_za_br:
                xsc, br = get_SushiXSC(process, tb , heavy, light, m_heavy, m_light)
                
                expected         *= br
                observed         *= br
                exp_plus_1sigma  *= br
                exp_minus_1sigma *= br
                exp_plus_2sigma  *= br
                exp_minus_2sigma *= br

            ax.fill_betweenx(y_, [exp_minus_2sigma]*fact, [exp_plus_2sigma]*fact,
                                    facecolor   ='#FFF04D', 
                                    lw          =0, 
                                    label       =r'Expected $\pm$ 2 std. deviation', 
                                    interpolate =True)
            ax.fill_betweenx(y_, [exp_minus_1sigma]*fact, [exp_plus_1sigma]*fact,
                                    facecolor   ='#00B140', 
                                    lw          =0, 
                                    label       =r'Expected $\pm$ 1 std. deviation', 
                                    interpolate =True)
            expected_line = ax.plot([expected]*fact, y_, 
                                    ls             ='dashed', 
                                    solid_capstyle ='round', 
                                    color          ='black', 
                                    ms             =6, 
                                    marker         ='', 
                                    lw             =1.5, 
                                    label          ="Expected 95% upper limit")[0]
            
            if options.unblind:
                observed_line = ax.plot([observed]*fact, y_, 
                                        ls             ='solid', 
                                        solid_capstyle ='round', 
                                        color          ='black', 
                                        ms             =6, 
                                        marker         ='', 
                                        lw             =1.5, 
                                        label          ="Observed 95% upper limit")[0]

            one_sigma_patch = mpatches.Patch(color='#00B140', label=r'Expected $\pm$ 1 std. deviation')
            two_sigma_patch = mpatches.Patch(color='#FFF04D', label=r'Expected $\pm$ 2 std. deviation')
            
            handles = [expected_line, one_sigma_patch, two_sigma_patch]
            labels  = ['Expected 95% uppper limit', r'Expected $\pm$ 1 std. deviation', r'Expected $\pm$ 2 std. deviation']
            
        if options.unblind:
            handles += [observed_line]
            labels  += ['Observed 95% uppper limit']
        
        for tb in [1.5, 20.]: 
            xsc, br  = get_SushiXSC(process, tb , heavy, light, m_heavy, m_light)
            xsc_x_br = xsc* br* 1000 # fb
            theory_line[process][tb] = ax.plot([xsc_x_br]*fact, y_, #[0., th_lmax],
                                                ls             ='solid' if tb==1.5 else 'dashed', 
                                                solid_capstyle ='round', 
                                                color          ='red' if process=='ggH' else 'blue', 
                                                ms             =6, 
                                                marker         ='', 
                                                lw             =1.5, 
                                                label          =r"{} theory (tan$\beta$ = {})".format(process, tb))[0]
    
    for process, sushi in theory_line.items():
        for tb, sushi_xsc_line in sushi.items():
            handles += [theory_line[process][tb]]
            labels  += [r'{} theory prediction (tan$\beta$ = {})'.format(process, tb)]
   
    ax.set_xlabel(r'$\sigma(pp \rightarrow\, H) B(H \rightarrow\, ZA \rightarrow\, ll b\bar{b})$ (fb)', fontsize=12.)
    yaxis_set_ticklabels.append('')
    ax.set_xscale('log')
    ax.set_xlim(1e-2, 1e5)
    ax.set_ylim(-0.1, y_[-1]+3)
    ax.axes.yaxis.label.set_size(8.)
    
    plt.yticks(yaxis, yaxis_set_ticklabels)
    ax.legend(ncol=1, loc='best', handles= handles, labels=labels, fontsize='medium', frameon=False)
    ax.get_legend().set_title(r"2HDM-II, cos($\beta$ -$\alpha$) = 0.01"+"\n"+r"($m_{%s}, m_{%s}$)= (%s, %s) GeV"%(heavy, light, m0, m1),
                            prop={'size': 8, 'weight': 'heavy'})
    
    outDir = os.path.dirname(jsonpath)
    fig.savefig(os.path.join(outDir, name+'.png'))
    fig.savefig(os.path.join(outDir, name+'.pdf'))
    print( 'file saved in : ', os.path.join(outDir, name+'.png'))
    
    plt.close(fig)
    plt.gcf().clear()
               

def draw_theory(ax, mH, mA, br, label=False):
    # Make sure we vary over the right coupling
    params    = [0] * 5
    params[0] = mH
    params[1] = mA
            
    th = {}
    for ifile, th_file in enumerate(th_files):
        with open(th_file) as f:
            th = json.load(f)
        # FIXME there is a 5GeV shift in the theory scan... so we're using mH = 305 for theory for the mH = 300 plot
        shift = 0
        indices = [i for i,x in enumerate(th['mH']) if x == (the_fixmass + shift)]
        if len(indices) == 0:
            shift = 5
            indices = [i for i,x in enumerate(th['mH']) if x == (the_fixmass + shift)]
        x    = [th['mA'][i] for i in indices]
        xs   = [th['sigma'][i] * 1000 * th['BR'][i] for i in indices] # xsec in fb for the plots
        down = [(th['sigma'][i] - pow(pow(th['sigma_err_muRm'][i], 2) + pow(th['sigma_errIntegration'][i], 2), 0.5)) * 1000  * th['BR'][i] for i in indices]
        up   = [(th['sigma'][i] + pow(pow(th['sigma_err_muRp'][i], 2) + pow(th['sigma_errIntegration'][i], 2), 0.5)) * 1000 * th['BR'][i] for i in indices]
                
        if options.rescale_to_za_br:
            xs   *= br
            down *= br
            up   *= br
                
        theory_markers = ax.plot(x, xs , lw=2, color=th_colors[ifile], alpha=0.7, zorder=1000)
        ax.fill_between(x, down, up,
            #facecolor=th_colors[ifile],
            color=th_colors[ifile],
            interpolate=True,
            alpha=0.5,
            zorder=999,
            hatch=th_hatches[ifile]
        )
    # Label
    if label:
        if mA == 1:
            pos = (0.9, 0.44)
            angle = 23
        elif mA == 2:
            pos = (0.9, 0.705)
            angle = 22
            
    ax.text(pos[0], pos[1], "$mA = {:d}$".format(mA), transform=ax.transAxes, ha="center", va="baseline", fontsize="medium", rotation=angle)
    return theory_markers


def TwistedSenarios(nm, thdm):
    if thdm =='AToZH':
        nm = nm.replace('ggH', 'ggA')
        nm = nm.replace('bbH', 'bbA')
    return nm


def Plot1D_ScanLimits(jsonpath, signal_grid, thdm, do_PLot=False):
    mpl.rcParams['font.size'] = 12
    ToBe_Stacked = {}
    
    for cat, Cfg in catagories.items():
               
        cat = TwistedSenarios(cat, thdm)
        ToBe_Stacked[cat] = {}
        cba     = 0.01
        heavy   = thdm[0]
        light   = thdm[-1]
        flavors, prod, nb, region = Cfg
        prod    = TwistedSenarios(prod, thdm)
        tb      = 20 if prod in ['bbH', 'bbA'] else 1.5
        process = 'gluon-gluon fusion' if prod in ['ggH', 'ggA'] else 'b-associated production'
        
        for the_fixmass in massTofix_list:
            
            if options.scan =='mA': parameter_values = {"mH": the_fixmass}
            else: parameter_values = {"mA": the_fixmass}

            flavors_limits = {}
            for flav in flavors:
                limits = flavors_limits.setdefault(flav, {})
                json_f = os.path.join(jsonpath, 'combinedlimits_{}_{}_UL{}.json'.format(cat, flav, options.era)) 
                
                if not os.path.isfile(json_f):
                    continue

                with open(json_f) as f:
                    print('working on ::', json_f )
                    limits_ = json.load(f)
                    for l in limits_:
                        limits[tuple(l['parameters'])] = l['limits']
            
            #available_parameters = flavors_limits[flavors[0]].keys() # just needed to get the keys 
            #available_parameters = [tuple(map(lambda x: x.encode('utf-8'), tup)) for tup in available_parameters]
            #available_parameters = [ (float(i), float(j)) for i,j in available_parameters]
            #available_parameters = sorted(available_parameters, key=lambda v: v[parameter_index[options.scan]])#, reverse=True)
            #available_parameters = [ (str(i).replace('.0', ''), str(j).replace('.0', '')) for i,j in available_parameters]
             
            flavors_data = {}
            scanning_SM  = False
            print('available_parameters for %s  ---> %s ' %(parameter_values, available_parameters[the_fixmass]))
            if not available_parameters[the_fixmass]:
                continue
            if len(available_parameters[the_fixmass]) ==1:
                continue
    
            for point in available_parameters[the_fixmass]:
                next_point = False
                
                m_heavy = point[0]
                m_light = point[1]
                
                ## Only keep points request by the user for the scan
                for name, value in parameter_values.items():
                    if float(point[parameter_index[name]]) != float(value):
                        next_point = True
                        break
                if next_point:
                   continue
                
                if not point in limits.keys():
                   print("\t => No limits provided for point %s , %s !" %(str(point), cat) )
                   continue
                print("Working on point %s" % str(point))
            
                # If we're including the SM point, draw dotted vertical line
                if point == (1, 1):
                    scanning_SM = True
                
                if options.rescale_to_za_br:
                    xsc, br = get_SushiXSC(prod, tb , heavy, light, m_heavy, m_light)
                    
                for f in flavors:
                    limits = flavors_limits[f]
                    data   = flavors_data.setdefault(f, {})
                    x = data.setdefault('x', [])
                    
                    one_sigma = data.setdefault('one_sigma', [[], []])
                    two_sigma = data.setdefault('two_sigma', [[], []])
                    expected  = data.setdefault('expected', [])
                    observed  = data.setdefault('observed', [])
           
                    param_val = point[parameter_index[options.scan]]
                    x.append(param_val)
            
                    exp = limits[point]['expected']
                    obs = limits[point]['observed']
                    
                    if options.rescale_to_za_br:
                        exp *= br
                        obs *= br
                    
                    # from pb to fb 
                    expected.append(exp*1000)
                    observed.append(obs*1000)
            
                    exp_plus_1sigma  = limits[point]['one_sigma'][1]*1000
                    exp_minus_1sigma = limits[point]['one_sigma'][0]*1000
                    exp_plus_2sigma  = limits[point]['two_sigma'][1]*1000
                    exp_minus_2sigma = limits[point]['two_sigma'][0]*1000
                    
                    if options.rescale_to_za_br:
                        exp_plus_1sigma  *= br
                        exp_minus_1sigma *= br
                        exp_plus_2sigma  *= br
                        exp_minus_2sigma *= br
                    
                    # Index 0 is DOWN error, index 1 is UP error
                    one_sigma[1].append(exp_plus_1sigma)
                    one_sigma[0].append(exp_minus_1sigma)
                    two_sigma[1].append(exp_plus_2sigma)
                    two_sigma[0].append(exp_minus_2sigma)
           
            if not flavors_data:
                continue
    
            ToBe_Stacked[cat][the_fixmass] = flavors_data
            
            if do_PLot:
                # Create a figure instance
                #==============================
                CMSStyle.changeFont()
                fig = plt.figure(1, figsize=(7, 7), dpi=300)
                fig.tight_layout()
                
                # Create an axes instance
                ax = fig.add_subplot(111)
                ax.set_ylabel(r'95% C.L. limit on $\sigma(pp \rightarrow\, Z{})$ (fb)'.format(light))
                ax.set_xlabel('${}$'.format(parameter_axis_legend[options.scan]), fontsize='large', x=0.85)
                if options.rescale_to_za_br:
                    ax.set_ylabel(r'95% C.L. limit on '+r'$\sigma(pp \rightarrow\, %s) \times\, BR(H \rightarrow\, Z%s) \times\, BR(%s \rightarrow\, b\bar{b})$ (fb)'%(heavy, light, light))
                #ax.grid()
                
                CMSStyle.applyStyle(fig, ax, Constants.getLuminosity(options.era), figures=1)
                
                expected_lines = {}
                for f in flavors:
                    color = colors[f]
                    data  = flavors_data[f]
                    
                    data['x'] = np.asarray(data['x'])
                    data['expected']  = np.asarray(data['expected'])
                    data['observed']  = np.asarray(data['observed'])
                    data['one_sigma'] = np.asarray(data['one_sigma'])
                    data['two_sigma'] = np.asarray(data['two_sigma'])
                
                    print ( 'expected  : %s' %data['expected'])
                    print ( 'observed  : %s' %data['observed'])
                    print ( 'one_sigma : %s' %data['one_sigma'])
                    print ( 'two_sigma : %s' %data['two_sigma'])
                    
                    data['x'] = np.array(data['x'], dtype=float)
                    # Plot 2 sigma
                    ax.fill_between(data['x'], 
                                    data['expected'] - data['two_sigma'][0], 
                                    data['expected'] + data['two_sigma'][1], 
                                    facecolor='#FFCC29', lw=0, label=r'Expected $\pm$ 2 std. deviation', interpolate=True) 
                    # Plot 1 sigma
                    ax.fill_between(data['x'], 
                                    data['expected'] - data['one_sigma'][0], 
                                    data['expected'] + data['one_sigma'][1], 
                                    facecolor='#00A859', lw=0, label=r'Expected $\pm$ 1 std. deviation', interpolate=True)
                    # Plot expected limit
                    expected_line = ax.plot(data['x'], 
                                            data['expected'], 
                                            ls='dashed', solid_capstyle='round', color=color, ms=6, 
                                            marker='o' if show_markers[options.scan] else '', lw=1.5, label="Expected 95% upper limits ({})".format(channels[f]))[0]
                    
                    expected_lines[channels[f]] = expected_line 
                    
                    # And observed
                    if options.unblind:
                        observed_markers = ax.plot(data['x'], 
                                                   data['observed'], 
                                                   ls='solid', marker='o' if show_markers[options.scan] else '', color=color, 
                                                   mec=color, lw=1.5, markersize=6, alpha=0.8, label="Observed 95% upper limits ({})".format(channels[f]))
                # And theory
                if options.theory:
                    # Increase a bit the range of the theory curve to cover rectangles width
                    #x_axis_length = ax.get_xlim()[1] - ax.get_xlim()[0]
                    #x = np.linspace(min(data['x']) - x_axis_length * 0.01, max(data['x']) + x_axis_length * 0.01, 200)
                    x  = np.linspace(min(data['x']), max(data['x']), 200)
                
                    if options.scan == "mH":
                        for mA in [1, 2]:
                            params = [0, 0]
                            for p, i in parameter_index.items():
                                if p == options.scan:
                                    params[i] = x * mA
                                else:
                                    params[i] = mA
                
                            theory_markers = draw_theory(ax, *params, label=True)
                    else:
                        params = [0, 0]
                        for p, i in parameter_index.items():
                            if p == options.scan:
                                params[i] = x
                            else:
                                params[i] = parameter_values[p]
                
                        theory_markers = draw_theory(ax, *params)
                
                # Set Y axis range
                if not options.log:
                    ax.set_ylim(**axes_y_limits[options.scan])
                else:
                    ax.set_yscale('log')
                    ax.set_ylim(**axes_log_y_limits[options.scan])
                
                # Set x axis range
                ax.margins(0.05, 0.1)
                ax.set_xlim(**axes_x_limits[options.scan])
                
                # Legends
                one_sigma_patch = mpatches.Patch(color='#00A859', label=r'Expected $\pm$ 1 std. deviation')
                two_sigma_patch = mpatches.Patch(color='#FFCC29', label=r'Expected $\pm$ 2 std. deviation')
                
                handles = [l for l in expected_lines.values()] + [one_sigma_patch, two_sigma_patch]
                labels  = [r'Expected 95% upper limit ({})'.format(k) for k in  expected_lines.keys()] + [r'Expected $\pm$ 1 std. deviation', r'Expected $\pm$ 2 std. deviation']
                
                if options.unblind:
                    handles = observed_markers + handles
                    labels = ['Observed 95% upper limit'] + labels
                
                # Create theory label
                if options.theory:
                    parameters_formatted_text = []
                    for p in parameters:
                        if p == options.scan:
                            continue
                    
                        parameter_value = parameter_values[p]
                        if parameter_value == default_values[p]:
                            parameter_value = parameter_legend[p] + '^{SM}'
                        parameters_formatted_text.append("${} = {}$".format(parameter_legend[p], parameter_value))
                    parameters_text = ', '.join(parameters_formatted_text)
                    
                    #label = "Theory ($%s$, %s)" % (parameter_legend[options.scan], parameters_text)
                    for i, f in enumerate(th_files):
                        # expect a file format of the type: sigmaBR_HZA_type-2_tb-1p0_cba-0p01.json
                        tb = [x for x in f.split('_') if 'tb-' in x][0].strip('tb-').replace('p', '.')
                        tb = float(tb)
                        label = r'$\sigma_{th}$ (tan($\beta$) = %s)' % (tb)
                        theory_line  = mlines.Line2D([], [], color=th_colors[i], marker=None, linewidth=2)
                        theory_patch = mpatches.Patch(color=th_colors[i], hatch=th_hatches[i], alpha=0.5)
                        handles = handles + [(theory_line, theory_patch)]
                        labels  = labels + [label]
                
                # Format legend text...
                # text = ""
                # text_elements = range(5)
                # for p, i in parameter_index.items():
                    # if p == options.scan:
                        # continue
                    # text_elements[i] = "$" + parameter_legend[p] + "$ = {}, ".format(parameter_values[p])
                # for p in [ x for x in text_elements if isinstance(x, str) ]:
                    # text += p
                # text = text[:len(text)-2]
                
                legend_y_anchor = 1
                legend_x_anchor = 0.035 if options.leg_pos == 'left' else 1
                loc = 2 if options.leg_pos == 'left' else 1
                lgd = ax.legend(handles, labels, loc=loc, numpoints=1, fontsize='medium', frameon=False, bbox_to_anchor=(legend_x_anchor, legend_y_anchor), ncol=1)
                #lgd = ax.legend(loc=loc, numpoints=1, fontsize='medium', frameon=False, bbox_to_anchor=(legend_x_anchor, legend_y_anchor), ncol=2)
                
                #ax.text(0.06, 0.8, r"$m_H = {:d}$ GeV, 2HDM Type-II, tan$\beta$= {}, cos($\beta-\alpha$) = {}".format(int(the_fixmass), tb, cba), transform=ax.transAxes, ha='left', va='baseline')
                #ax.minorticks_on()
                ax.get_legend().set_title(r"2HDM-II, ${}$= {} GeV, cos($\beta$ -$\alpha$) = 0.01, tan$\beta$= {}".format(m_fix, round(the_fixmass,2), tb)+"\n"+ "{}, {}{}".format(process, nb, region), 
                        prop={'size': 12, 'weight': 'heavy'})
                
                # Actually draw the figure to have access to legend size
                fig.canvas.draw()
                
                # Detect if the plot content overlap with the legend
                # Get legend height and width
                inv_data_trans = ax.transData.inverted()
                
                legend_pos_display = lgd.get_window_extent(renderer=fig.canvas.get_renderer())
                legend_pos_data    = inv_data_trans.transform(legend_pos_display)
                
                # Find maximum in the legend range
                slicing = (data["x"] >= legend_pos_data[0][0]) & (data["x"] <= legend_pos_data[1][0])
                values  = (data['expected'] + data['two_sigma'][1])[slicing]
                if len(values):
                    maximum = max((data['expected'] + data['two_sigma'][1])[slicing])
                
                    for l in ax.lines:
                        x = l.get_xdata()
                        slicing = (x >= legend_pos_data[0][0]) & (x <= legend_pos_data[1][0])
                        values = np.asarray(l.get_ydata())[slicing]
                        if len(values) > 0:
                            maximum = max(maximum, max(values))
                
                    for c in ax.collections:
                        for p in c.get_paths():
                            for v in p.vertices:
                                if v[0] >= legend_pos_data[0][0] and v[0] <= legend_pos_data[1][0]:
                                    maximum = max(maximum, v[1])
                    delta = legend_pos_data[0][1] - maximum
                
                    if delta < 0:
                        # Overlap between the legend and the plot content
                        print("Legend overlap with the plot content, make room for the legend")
                        if options.log:
                            import math
                            op = math.log10
                            inv_op = lambda t: math.pow(10, t)
                        else:
                            op = lambda t: t
                            inv_op = lambda t: t
                
                        y_lim = ax.get_ylim()
                
                        delta = op(legend_pos_data[0][1]) - op(maximum)
                        padding_top = op(y_lim[1]) - op(maximum)
                
                        new_top = op(y_lim[1]) - delta + padding_top
                        ax.set_ylim(top=inv_op(new_top))
                
                # Build plot name
                plot_name = 'limits_{}_1Dscan_{}_'.format(cat, options.scan)
                name_elements = list(range(5))
                for p, i in parameter_index.items():
                    if p == options.scan:
                        continue
                    name_elements[i] = "{}={}_".format(p, parameter_values[p])
                
                for p in [ x for x in name_elements if isinstance(x, str) ]:
                    plot_name += p
                plot_name = plot_name[:len(plot_name)-1]
                
                if options.rescale_to_za_br:
                    plot_name += '_rescaled_to_Z{}_BR'.format(light)
                
                if not options.no_latex:
                    with open('%s/%s.tex' % (output_dir, plot_name), 'w') as f:
                        f.write(R'\begin{tabular}{@{}ccccc@{}} \toprule' + '\n')
                        f.write(R'\hline' + '\n')
                        f.write(R'\\' + '\n')
                        f.write('${}$'.format(parameter_legend[options.scan]) + 
                                R' & Observed (fb) & Expected (fb) & $\mp$ 1 Standard deviation (fb) & $\mp$ 2 Standard deviation (fb) \\ \midrule' + '\n')
                        f.write(R'\\' + '\n')
                        f.write(R'\hline' + '\n')
                        f.write(R'\\' + '\n')
                
                        for index in range(len(data['x'])):
                            fmt = R"%.1f & " + ("$%.2e}$" if options.unblind else "%s") + R" & $%.2e}$ & $-%.2e}$ / $+%.2e}$ & $-%.2e}$ / $+%.2e}$ \\"
                            f.write( (fmt % (data['x'][index], 
                                             data['observed'][index] if options.unblind else '-', 
                                             data['expected'][index], 
                                             data['one_sigma'][0][index], 
                                             data['one_sigma'][1][index], 
                                             data['two_sigma'][0][index], 
                                             data['two_sigma'][1][index]) + '\n').replace('e+0', R'\,.\,10^{').replace('e-0', R'\,.\,10^{') )
                            f.write(R'\\' + '\n')
                        f.write(R'\hline' + '\n')
                        f.write(R'\bottomrule' + '\n')
                        f.write(R'\end{tabular}' + '\n')
                    print('LaTeX table saved as %r' % ('%s/%s.tex' % (output_dir, plot_name)))
                
                if options.log:
                    plot_name = plot_name + "_logy"
                if options.unblind:
                    plot_name = plot_name + "_unblind"
                
                fig.savefig(os.path.join(output_dir, plot_name + '.pdf'), bbox_inches='tight')
                fig.savefig(os.path.join(output_dir, plot_name + '.png'), bbox_inches='tight')
               
                print("Plot saved as %r"% os.path.join(output_dir, plot_name + '.pdf'))
                print("Plot saved as %r"% os.path.join(output_dir, plot_name + '.png'))
                print("="*40)
                
                # clean the figure before next plot
                plt.gcf().clear() 

    return ToBe_Stacked



def Plot1D_StackedLimits(masses_tofix, upper_limits, thdm):
    mpl.rcParams['font.size'] = 12

    for cat, Cfg in catagories.items():
        
        cat = TwistedSenarios(cat, thdm)
        
        flavors, prod, nb, region = Cfg
        prod = TwistedSenarios(prod, thdm)
        
        region  = ', resolved + boosted' if region == 'resolved_boosted' else '-'+region
        tb      = 20 if prod in ['bbH', 'bbA'] else 1.5
        process = 'gluon-gluon fusion' if prod in ['ggH', 'ggA'] else 'b-associated production'

        for flav in flavors:
            color = colors[flav]
            # Create a figure instance
            CMSStyle.changeFont()
            fig = plt.figure(1, figsize=(8, 7), dpi=300)
            fig.tight_layout()
            
            # Create an axes instance
            ax = fig.add_subplot(111)
            ax.set_ylabel(r'95% C.L. upper limit on $\sigma(pp \rightarrow\, ZA)$ (fb)')
            ax.set_xlabel('${}$'.format(parameter_axis_legend[options.scan]), fontsize='large', x=0.85)
            if options.rescale_to_za_br:
                ax.set_ylabel(r'$\sigma(pp \rightarrow\, H) B(H \rightarrow\, ZA \rightarrow\, ll b\bar{b})$ (fb)')
            
            CMSStyle.applyStyle(fig, ax, Constants.getLuminosity(options.era), figures=1)
            
            poww = 0
            for j, m in enumerate(sorted(upper_limits[cat].keys())):
                
                multi = pow(10, poww)

                data  = upper_limits[cat][m][flav]
                data['x'] = np.array(data['x'])
                data['expected']  = np.asarray(data['expected'])* multi
                data['observed']  = np.asarray(data['observed'])* multi
                data['one_sigma'] = np.asarray(data['one_sigma'])* multi
                data['two_sigma'] = np.asarray(data['two_sigma'])* multi
                
                data['x'] = np.array(data['x'], dtype=float)
               
                exp_plus_1sigma  = data['expected'] + data['one_sigma'][1]
                exp_minus_1sigma = data['expected'] - data['one_sigma'][0]
                exp_plus_2sigma  = data['expected'] + data['two_sigma'][1]
                exp_minus_2sigma = data['expected'] - data['two_sigma'][0]
                
                exp_plus_1sigma  = np.array(exp_plus_1sigma, dtype=float)
                exp_minus_1sigma = np.array(exp_minus_1sigma, dtype=float)
                exp_plus_2sigma  = np.array(exp_plus_2sigma, dtype=float)
                exp_minus_2sigma = np.array(exp_minus_2sigma, dtype=float)
                
                print( m , exp_plus_1sigma, exp_minus_1sigma, exp_plus_2sigma, exp_minus_2sigma, data['x']) 
                print( '==============='*10)
                # keep always sigma 2 first, otherwise won't appear in the plot
                # because will be hidden by sigma 1
                # Plot 2 sigma
                ax.fill_between(data['x'], 
                                exp_minus_2sigma, 
                                exp_plus_2sigma, 
                                facecolor='#FFCC29', 
                                lw=0, 
                                label=r'Expected $\pm$ 2 std. deviation', 
                                interpolate=True) 
                
                # Plot 1 sigma
                ax.fill_between(data['x'], 
                                exp_minus_1sigma, 
                                exp_plus_1sigma, 
                                facecolor='#00A859', 
                                lw=0, 
                                label=r'Expected $\pm$ 1 std. deviation', 
                                interpolate=True)

                # Plot expected limit
                expected_line = ax.plot(data['x'], 
                                        data['expected'], 
                                        ls='dashed', 
                                        solid_capstyle='round', 
                                        color=color, 
                                        ms=6, 
                                        marker='o',
                                        lw=1.5, 
                                        label="Expected 95% upper limits")[0]
                
                ax.annotate(r' $%s$= %s GeV (x $10^{%s}$)'%(m_fix, m, poww), xy=(data['x'][-1], data['expected'][-1]), xytext=(data['x'][-1]+50, data['expected'][-1]), fontsize=8,
                            arrowprops=dict(arrowstyle="->",facecolor='w', connectionstyle="arc3"), horizontalalignment='left')
                
                # And observed
                if options.unblind:
                    observed_line = ax.plot(data['x'], 
                                            data['observed'], 
                                            ls='solid', 
                                            marker='o', 
                                            color=color, 
                                            mec=color, 
                                            lw=1.5, 
                                            markersize=6, 
                                            alpha=0.8, 
                                            label="Observed 95% upper limits")
                poww  += 3
                if region == 'boosted':
                    poww +=1

            
            one_sigma_patch = mpatches.Patch(color='#00A859', label=r'Expected $\pm$ 1 std. deviation')
            two_sigma_patch = mpatches.Patch(color='#FFCC29', label=r'Expected $\pm$ 2 std. deviation')
            
            handles = [expected_line, one_sigma_patch, two_sigma_patch]
            labels  = [r'Expected 95% upper limit', r'Expected $\pm$ 1 std. deviation', r'Expected $\pm$ 2 std. deviation']
            
            if options.unblind:
                handles += [observed_line]
                labels  += [r'Observed 95% upper limit']
        
            legend_y_anchor = 1
            legend_x_anchor = 0.035 if options.leg_pos == 'left' else 1
            loc = 2 if options.leg_pos == 'left' else 1
            lgd = ax.legend(handles, labels, loc=loc, numpoints=1, fontsize='medium', frameon=False, bbox_to_anchor=(legend_x_anchor, legend_y_anchor), ncol=1)
            
            if not options.log:
                ax.set_ylim(**axes_y_limits[options.scan])
            else:
                ax.set_yscale('log')
                ax.set_ylim(10e-3, 10e90)
            
            ax.margins(0.1, 0.1)
            ax.set_xlim(**axes_x_limits[options.scan])
            ax.get_legend().set_title(r"2HDM-II, cos($\beta$ -$\alpha$) = 0.01, tan$\beta$= {}".format(tb)+"\n"+ "{}, {}{}".format(process, nb, region), 
                    prop={'size': 12, 'weight': 'heavy'})
            
            fig.canvas.draw()
            plot_name = '1Dstacked_limits_{}_{}_{}'.format(options.era, cat, flav)
            fig.savefig(os.path.join(output_dir, plot_name + '.pdf'), bbox_inches='tight')
            fig.savefig(os.path.join(output_dir, plot_name + '.png'), bbox_inches='tight')
            
            plt.gcf().clear()
    
    return 



if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Draw 95%CL Limits')
    parser.add_argument('-p', '--jsonpath', action='store', type=str, dest='jsonpath', 
                                        help='path to json limits for different catagories, looking for all_limits_{cat}.josn format ', required=True)
    parser.add_argument('-r', '--rescale-to-za-br', action='store_true', dest='rescale_to_za_br', 
                                        help='If flagged True, limits in HToZA mode will be x to BR( Z -> ll) x BR(A -> bb ) x (H -> ZA)')
    parser.add_argument('--era'     , action='store', type=str, default='fullrun2', choices=['2016', '2017', '2018', 'fullrun2'], help='Output directory')
    parser.add_argument('--unblind' , action='store_true', dest='unblind', help='If set, draw also observed upper limits')
    parser.add_argument('--theory'  , action='store_true', dest='theory', help='If set, draw theoretical cross-section')
    parser.add_argument('--log'     , action='store_true', dest='log', help='If set, draw limits plot in log-scale')
    parser.add_argument('--no-latex', action='store_true', dest='no_latex', help='Do not create LaTeX table of limits')
    parser.add_argument('--leg-pos' , action='store', type=str, dest='leg_pos', default='left', choices=['left', 'right'], help='Legend position')
    parser.add_argument('--scan'    , action='store', type=str, dest='scan', default='mA', choices=['mA', 'mH'], 
                                        help='Parameter being scanned in the x axis wihle the other is fixed for a certain value')
    parser.add_argument('--tanbeta', action='store', type=float, default=None, required=False, help='')
    parser.add_argument('--_2POIs_r', action='store_true', dest='_2POIs_r', required=False, default=False,
                                        help='This will merge both signal in 1 histogeram and normalise accoridngly, tanbeta will be required')

    options = parser.parse_args()
    
    
    tb_dir = ''
    if options.tanbeta is not None:
        tb_dir = 'tanbeta_{}'.format(options.tanbeta)

    poi_dir = '1POIs_r'
    if options._2POIs_r:
        poi_dir = '2POIs_r'


    jsonpath   = os.path.join(options.jsonpath, poi_dir, tb_dir) 
    output_dir = jsonpath
    m_fix = 'm_{H}' if options.scan =='mA' else 'm_{A}'
    
    for thdm in ['HToZA']: #'AToZH', 'HToZA']:
       
        heavy = thdm[0]
        light = thdm[-1]
        signal_grid = []
        for dir_p in glob.glob(os.path.join(output_dir.split('jsons')[0], poi_dir, tb_dir, 'M{}*'.format(heavy))):
            dir_ = dir_p.split('/')[-1]
            m0   = float(dir_.split('_')[0].split('-')[1])
            m1   = float(dir_.split('_')[1].split('-')[1])
            if not (m0, m1) in signal_grid:
                signal_grid.append((m0, m1))
   
        # bad binning
        #if thdm == 'HToZA':
        #    signal_grid.remove((650., 50.))
        #    signal_grid.remove((780., 680.))
        #    signal_grid.remove((240., 130.))
        if thdm == 'AToZH':
            signal_grid.remove((200., 125.))
            signal_grid.remove((300., 135.))
            signal_grid.remove((510., 130.))
            signal_grid.remove((700., 200.))
            signal_grid.remove((750., 610.))
            signal_grid.remove((500., 250.))
            signal_grid.remove((220., 127.))
            signal_grid.remove((670., 500.))
        
        #signal_grid =[(200., 125), (240., 130.), (500., 125.), (200., 125), (240., 130.), (800., 140.,), (500., 250.), (780., 680.)]
        
        massTofix_list = []
        available_parameters={}
        for mH, mA in signal_grid:
            if options.scan == 'mA':
                if not mH in massTofix_list:
                    massTofix_list.append(mH)
                    available_parameters[mH]= []
            else:
                if not mA in massTofix_list:
                    massTofix_list.append(mA)
                    available_parameters[mA]= []
        
        for m in massTofix_list:
            for tup in sorted(signal_grid):
                if options.scan=='mA':
                    if m ==tup[0]: available_parameters[m].append((str(tup[0]),str(tup[1])))
                else:
                    if m ==tup[1]: available_parameters[m].append((str(tup[0]),str(tup[1])))

        print( signal_grid )
        print( available_parameters )
        print( massTofix_list )
        
        #massTofix_list = [800.0, 1000.0, 500.0, 700.0, 300.0, 200.0, 750.0, 650.0] 
        
        #for (m0, m1) in signal_grid:
        #   PlotMultipleUpperLimits(m0, m1, catagories, jsonpath, thdm)
    
        ToBe_Stacked = Plot1D_ScanLimits(jsonpath, available_parameters, thdm, do_PLot=False)    
        Plot1D_StackedLimits(massTofix_list, ToBe_Stacked, thdm)
