import json
import os, os.path, sys

import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import pandas as pd

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

    dir = '../hig-22-010/datacards_nosplitJECs/work__ULfullrun2/bayesian_rebin_on_S/asymptotic-limits__very_good_xbr/dnn/jsons/2POIs_r'
    data = getLimits(dir)
    
    colors  = {'resolved': 'cyan', 
               'boosted': 'purple',
               'resolved+boosted': 'chocolate' }

    for p, d_per_flav in data.items():
        
        fig= plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111)
        
        for flav, d_per_reg in d_per_flav.items():
            # create fixed legend
            limits = {}
            df = None 
            for r, c  in colors.items(): 
                plt.plot([0.], [0.], 'o', color=c, label=r.replace('_', '+'))
                limits[r] =[]
            
            x = []
            y = []
            c = []
            w = []
            for i, (params, l) in enumerate(sorted(d_per_reg.items())):
               
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
                
                plt.plot([m_light], [m_heavy], 'o', color=color)
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
            #fig.add_scatter(df, x='x', y='y', labels={'x':'mA', 'y':'mH'}, color='Category',
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
