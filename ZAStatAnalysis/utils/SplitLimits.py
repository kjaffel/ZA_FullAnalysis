import json
import os, os.path, sys

import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import pandas as pd


def getLimits(dir, nb2_vs_nb3_vs_nb2PLusnb3=False, reso_vs_boo_nb2PLusnb3=False):
    data = {}
    for p in [ 'ggH', 'bbH']:
        data[p] = {}
        
        if reso_vs_boo_nb2PLusnb3:
            for flav in ['OSSF', 'OSSF_MuEl', 'MuMu_ElEl', 'MuMu_ElEl_MuEl']:
                data[p][flav] = {}
                for nb in ['nb2', 'nb3', 'nb2PLusnb3']:
                    data[p][flav][nb] ={}
                    
                    for i, reg in enumerate(['resolved', 'boosted', 'resolved_boosted']):
                        fNm = f'combinedlimits_{p}_{nb}_{reg}_{flav}_CLs_ULfullrun2.json'
                        if not os.path.exists(os.path.join(dir, fNm)):
                            continue
                        
                        with open(os.path.join(dir, fNm)) as f:
                            limits = json.load(f)
                        for l in limits:
                            params = l['parameters']
                            if not (params[0], params[1]) in data[p][flav][nb].keys():
                                data[p][flav][nb][(params[0], params[1])] ={}
                            
                            data[p][flav][nb][(params[0], params[1])].update({reg: l})
            
        if nb2_vs_nb3_vs_nb2PLusnb3:
            for nb in ['nb2', 'nb3', 'nb2PLusnb3']: 
                data[p][nb] = {}
                for i, reg in enumerate(['resolved', 'boosted', 'resolved_boosted']):
                    data[p][nb][reg] = {}
                    for flav in ['OSSF', 'OSSF_MuEl', 'MuMu_ElEl', 'MuMu_ElEl_MuEl']:
                        
                        fNm = f'combinedlimits_{p}_{nb}_{reg}_{flav}_CLs_ULfullrun2.json'
                        if not os.path.exists(os.path.join(dir, fNm)):
                            continue
                        
                        with open(os.path.join(dir, fNm)) as f:
                            limits = json.load(f)
                        for l in limits:
                            params = l['parameters']
                            if not (params[0], params[1]) in data[p][nb][reg].keys():
                                data[p][nb][reg][(params[0], params[1])] ={}
                            
                            data[p][nb][reg][(params[0], params[1])].update({flav: l})
    return data


def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]


def get_col(sr):
    name=sr.idxmin()
    value = sr[name]
    color = colors[name]
    return pd.Series([value, name, color])


# create our callback function
def update_point(trace, points, selector):
    c = list(scatter.marker.color)
    s = list(scatter.marker.size)
    for i in points.point_inds:
        c[i] = '#bae2be'
        s[i] = 20
        with f.batch_update():
            scatter.marker.color = c
            scatter.marker.size = s


if __name__ == "__main__":

    #dir = '../hig-22-010/datacards_nosplitJECs/work__ULfullrun2/bayesian_rebin_on_S/asymptotic-limits__very_good_xbr/dnn/jsons/2POIs_r'
    dir = '../hig-22-010/datacards_nosplitJECs/work__ULfullrun2/bayesian_rebin_on_S/asymptotic-limits/dnn/jsons/2POIs_r/'
    
    nb2_vs_nb3_vs_nb2PLusnb3 =True
    reso_vs_boo_nb2PLusnb3   =False


    if nb2_vs_nb3_vs_nb2PLusnb3:
        data = getLimits(dir, nb2_vs_nb3_vs_nb2PLusnb3=True, reso_vs_boo_nb2PLusnb3=False)
        colors  = { ('nb2', 'resolved'): 'crimson', 
                    ('nb2', 'boosted') : 'violet',
                    ('nb3', 'resolved'): 'darkviolet',
                    ('nb3', 'boosted') : 'darkblue',
                    ('nb2PLusnb3', 'resolved') : 'green',
                    ('nb2PLusnb3', 'boosted')  : 'sienna',
                    ('nb2PLusnb3', 'resolved_boosted'): 'lightskyblue',
                    }
    
        for p, d_per_nb in data.items():
        
            fig= plt.figure(figsize=(8,6))
            ax = fig.add_subplot(111)
            
            for r, c  in colors.items(): 
                plt.plot([0.], [0.], 'o', color=c, label=f"{r[0].replace('nb2PLusnb3', 'nb2+nb3')}, {r[1].replace('_', '+')}")
            
            x = []
            y = []
            c = []
            w = []
            
            limits = {}
            df  = None 
            for nb, d_per_reg in d_per_nb.items():
                for reg, d_per_params in d_per_reg.items():
                    for  params, d_per_flav in d_per_params.items():
                        for flav in d_per_flav.keys():
                            
                            if len(d_per_flav.keys())==2: # I should always take the combination with mue , unless sth went wrong
                                if not 'MuEl' in flav: continue
                            l = d_per_flav[flav]
                            
                            #print( p, nb, reg, flav, params, l )
                            m_heavy  = float(params[0])
                            m_light  = float(params[1])
                       
                            exp = l['limits']['expected']*1000
                            x.append(m_light)
                            y.append(m_heavy)
                            
                            if not (nb, reg) in limits.keys():
                                limits[(nb, reg)] =[]
                            limits[(nb, reg)].append(exp)
                            c.append(colors[(nb, reg)])

            col  = ['x', 'y'] + list(limits.keys())
            rows = zip(x, y, limits[('nb2', 'resolved')], limits[('nb2', 'boosted')],
                             limits[('nb3', 'resolved')], limits[('nb3', 'boosted')],
                             limits[('nb2PLusnb3', 'resolved')], limits[('nb2PLusnb3', 'boosted')], limits[('nb2PLusnb3', 'resolved_boosted')] )
        
            df = pd.DataFrame(list(rows), columns=col)
            df[['Min_val','Min_col', 'Category']] = df[ list(limits.keys())].apply(lambda x : get_col(x), axis=1)
            print (df)
            

            fig = go.Figure()
            fig = px.scatter(df, x='x', y='y', labels={'x':'mA', 'y':'mH'}, color='Category',
                         template = "plotly_dark",
                         color_discrete_map=colors,
                         title = "<b> 2HDM type-II, {} expected upper limits at 95% CLs (full run 2) <b>".format(p),
                        )

            fig.update_traces(
                go.Scatter(
                        showlegend=False,
                        x = df['x'],
                        y = df['y'],
                        customdata= np.stack(( df[('nb2', 'resolved')], df[('nb2', 'boosted')], 
                                               df[('nb3', 'resolved')], df[('nb3', 'boosted')], 
                                               df[('nb2PLusnb3', 'resolved')], df[('nb2PLusnb3', 'boosted')],  df[('nb2PLusnb3', 'resolved_boosted')] ), axis = -1),
                        marker=dict(size=12, color=df['Category']),
                        hoverlabel = {"font_size" : 14, "font_family" : "Courier"},
                        hovertemplate="<br>".join([
                                        "<b>Expected limits (fb):</b>",
                                        "mA: %{x} GeV",
                                        "mH: %{y} GeV",
                                        "nb2, resolved: %{customdata[0]} fb",
                                        "nb2, boosted:  %{customdata[1]} fb",
                                        "nb3, resolved: %{customdata[2]} fb",
                                        "nb3, boosted:  %{customdata[3]} fb",
                                        "nb2+nb3, resolved: %{customdata[4]} fb",
                                        "nb2+nb3, boosted:  %{customdata[5]} fb",
                                        "nb2+nb3, resolved+boosted: %{customdata[6]} fb",
                            ]))
                        )

            # this a mandatory hack to fix crapy legend
            for r, c  in colors.items():
                fig.add_trace(go.Scatter(
                            x=[0],
                            y=[0],
                            mode='markers',
                            name=f"{r[0].replace('nb2PLusnb3', 'nb2+nb3')}, {r[1].replace('_', '+')}",
                            marker=dict(size=12, color=c)
                        ))
                    
            fig.update_xaxes(
                tickfont=dict(size=20),
                range=[0, 900.],
                title_text = 'mA (GeV)',
                title_font = {"size": 20},
                dtick=200, 
                showline=True, linewidth=2, linecolor='black',
                title_standoff = 25)

            fig.update_yaxes(
                tickfont=dict(size=20),
                range=[0, 1050.],
                title_text = 'mH (GeV)',
                title_font = {"size": 20},
                dtick=200, 
                showline=True, linewidth=2, linecolor='black',
                title_standoff = 25)
                    
            fig.update_layout(legend=dict(
                font={"size": 20}, 
                yanchor="bottom",
                x=0.99,
                xanchor="right",
                y=0.01,
                title='<b> Category, ee+µµ+µe<b>',
                ),
                title=dict(x=0.5, font={'size': 20},          
                ),
                font={"size": 20}, 
                #plot_bgcolor='rgba(0, 0, 0, 0)',
                #paper_bgcolor='rgba(0, 0, 0, 0)',
                )
            
            ax.scatter(df['x'], df['y'], c=df['Min_col'].map(colors))

            plt.xlim(0., 1000.)
            plt.ylim(0., 1050.)
        
            plt.xlabel(r'$m_{A} (GeV)$', fontsize=12)
            plt.ylabel(r'$m_{H} (GeV)$', fontsize=12)
    
            plt.title(r"{} 2HDM typeII, run2 ULegacy best expected upper limits at 95% CLs".format(p))
            plt.legend(loc='best')
    
            plt.grid(zorder = 0, alpha = 0.3)
    
            plt.tight_layout()
            plt.savefig(f'ZAmap_forBestLimitsscan_{p}_nb2_vs_nb3.png')
            plt.gcf().clear()
            
            fig.write_html(f'ZAmap_forBestLimitsscan_{p}_nb2_vs_nb3.html')


    elif reso_vs_boo_nb2PLusnb3:
        data = getLimits(dir, nb2_vs_nb3_vs_nb2PLusnb3=False, reso_vs_boo_nb2PLusnb3=True)
        colors  = { 'resolved': 'cyan', 
                    'boosted' : 'purple',
                    'resolved+boosted': 'chocolate' }
        
        for p, d_per_nb in data.items():
        
            fig= plt.figure(figsize=(8,6))
            ax = fig.add_subplot(111)
            
            for flav, d_per_reg in d_per_flav.items():
                    
                x = []
                y = []
                c = []
                w = []
                
                limits = {}
                df = None 
                
                # create fixed legend
                for r, c  in colors.items(): 
                    plt.plot([0.], [0.], 'o', color=c, label=r.replace('_', '+'))
                    limits[r] =[]
                
                for i, (params, l) in enumerate(sorted(d_per_reg['nb2PLusnb3'].items())):
                    
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
                        if (_1st_min / _2nd_min) < 0.05 and winner== 'resolved_boosted': 
                            # resolved+boosted  is below 5% compared to the cat.seperate, so it is not worth the combination
                            winner = get_keys_from_value(expected, _2nd_min)[0]
                    
                    winner   = winner.replace('_', '+')
                    color    = colors[winner]
                    m_heavy  = float(params[0])
                    m_light  = float(params[1])
                    for k, v in expected.items():
                        limits[k.replace('_', '+')].append(v)
                    
                    x.append(m_light)
                    y.append(m_heavy)
                    c.append(color)
                    w.append(winner)
                    print( p, flav, (m_heavy, m_light), expected, 'winner', winner )#, _1st_min / _2nd_min *100)
                
                df = pd.DataFrame(list(zip(x, y, w, c, limits['resolved'], limits['boosted'], limits['resolved+boosted'])),
                                        columns =['x', 'y', 'Category', 'color', 'resolved', 'boosted', 'resolved+boosted'])
                
                if not x: continue
                print( df)
                print( '*'*10)
                ## interactive plot using plotly 
                fig = go.Figure()
                fig = px.scatter(df, x='x', y='y', labels={'x':'mA', 'y':'mH'}, color='Category',
                            template = "plotly_dark",
                            color_discrete_map=colors,
                            custom_data=['resolved', 'boosted', 'resolved+boosted'],
                            title = "<b> 2HDM type-II, {} expected upper limits at 95% CLs (full run 2) <b>".format(p),
                        )

                fig.update_traces(
                        go.Scatter(
                            showlegend=False,
                            x = df['x'],
                            y = df['y'],
                            #title = "<b> 2HDM type-II, {} expected upper limits at 95% CLs (full run 2) <b>".format(p),
                            #template = "plotly_dark",
                            #color='Category',
                            #color_discrete_map=colors,
                            #fig.update_traces(
                            customdata= np.stack((df['resolved'], df['boosted'], df['resolved+boosted']) , axis = -1),
                            marker=dict(size=12, color=df['color']),
                            hoverlabel = {"font_size" : 14, "font_family" : "Courier"},
                            hovertemplate="<br>".join([
                                          "<b>Expected limits (fb):</b>",
                                          "mA: %{x} GeV",
                                          "mH: %{y} GeV",
                                          "resolved: %{customdata[0]} fb",
                                          "boosted:  %{customdata[1]} fb",
                                          "resolved+boosted: %{customdata[2]} fb",
                            ]))
                        )

                # this a mandatory hack to fix crapy legned 
                for r, c  in colors.items():
                    fig.add_trace(go.Scatter(
                        x=[0],
                        y=[0],
                        mode='markers',
                        name=r.replace('_', '+'),
                        marker=dict(size=12, color=c)
                    ))
                
                #names = set()
                #fig.for_each_trace(
                #    lambda trace:
                #        trace.update(showlegend=False)
                #        if (trace.name in names) else names.add(trace.name))
                
                fig.update_xaxes(
                    tickfont=dict(size=20),
                    range=[0, 900.],
                    title_text = 'mA (GeV)',
                    title_font = {"size": 20},
                    dtick=200, 
                    showline=True, linewidth=2, linecolor='black',
                    title_standoff = 25)

                fig.update_yaxes(
                    tickfont=dict(size=20),
                    range=[0, 1050.],
                    title_text = 'mH (GeV)',
                    title_font = {"size": 20},
                    dtick=200, 
                    showline=True, linewidth=2, linecolor='black',
                    title_standoff = 25)
                
                fig.update_layout(legend=dict(
                        font={"size": 20}, 
                        yanchor="bottom",
                        x=0.99,
                        xanchor="right",
                        y=0.01,
                        title='<b> Category, nb2+nb3, ee+µµ+µe<b>',
                        ),
                    title=dict(x=0.5, font={'size': 20},          
                        ),
                    font={"size": 20}, 
                    #plot_bgcolor='rgba(0, 0, 0, 0)',
                    #paper_bgcolor='rgba(0, 0, 0, 0)',
                    )
        
            plt.xlim(0., 1000.)
            plt.ylim(0., 1050.)
    
            plt.xlabel(r'$m_{A} (GeV)$', fontsize=12)
            plt.ylabel(r'$m_{H} (GeV)$', fontsize=12)
    
            plt.title(r"{} 2HDM typeII, run2 ULegacy best expected upper limits at 95% CLs".format(p))
            plt.legend(loc='best')
    
            plt.grid(zorder = 0, alpha = 0.3)
    
            plt.tight_layout()
            plt.savefig(f'ZAmap_forBestLimitsscan_{p}_{flav}.png')
            plt.gcf().clear()
            
            fig.write_html(f'ZAmap_forBestLimitsscan_{p}_{flav}.html')
