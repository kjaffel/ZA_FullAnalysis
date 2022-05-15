import os, os.path, sys
import math 
import collections
import json

from itertools import count

from bambooToOls import Plot
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op

import ControlPLots as cp 
import utils as utils
logger = utils.ZAlogger(__name__)

from corrections import legacy_btagging_wpdiscr_cuts, getIDX



jsf= { 'LL'  : "DYJetsToLL_TuneCP5_13TeV-amcatnloFXFX-pythia8_polyfitWeights_RunIISummer20UL161718NanoAODv9.json",
       'MuMu': "DYJetsToMuMu_TuneCP5_13TeV-amcatnloFXFX-pythia8_polyfitWeights_RunIISummer20UL161718NanoAODv9.json",
       'ElEl': "DYJetsToMuMu_TuneCP5_13TeV-amcatnloFXFX-pythia8_polyfitWeights_RunIISummer20UL161718NanoAODv9.json",
     }

def get_JsonWeights(flav):
    f   = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", jsf[flav]))
    params = json.load(f)
    return params

def make_polynomial(x, parameters):
    def powers_of(x):
        yield x
        for i in count(2):
            yield pow(x, i)
    return parameters[0] + sum((ip*xp if xp is not None else ip) for xp, ip in zip(powers_of(x), parameters[1:]))


def make_gaussian(x, parameters):
    def exp_term_of(x):
        return op.pow((x-parameters[1])/parameters[2], 2)
    return parameters[0]*op.exp(-0.5* exp_term_of(x)) 


def computeDYweight(flav, era, reg, n, mass, name, doSysts):
    lowmass_fitdeg = { '2017': 7, '2016': 6, '2018': 6 }
    fits_rng = {'resolved': [10., 650.], 'boosted': [10., 150.] }
    
    params = get_JsonWeights(flav)
    if reg == 'boosted':
        s   = f"_lowmass{n}"
        nom = op.switch( mass < fits_rng[reg][1], 
                            make_polynomial(mass, params[era][reg][name][f"polyfit{n}"]), 
                        op.c_float(params[era][reg][name]['binWgt']) )
    
    elif reg == 'resolved':
        s   = f"_lowmass{lowmass_fitdeg[era]}_highmass{n}" 
        nom = op.multiSwitch( (op.in_range(fits_rng[reg][0], mass, 150.), make_polynomial(mass, params[era][reg][name][f"polyfit{lowmass_fitdeg[era]}"])),
                              (op.in_range(150., mass, fits_rng[reg][1]), make_polynomial(mass, params[era][reg][name][f"polyfit{n}"]))
                             , op.c_float(params[era][reg][name]['binWgt']))
    
    #return op.switch(mass < 650., op.define("double", make_polynomial(mass, params[name][f"polyfit{n}"])), op.c_float(1.))
    if doSysts: return op.systematic(op.c_float(nom), name=f"DYweight_{reg}_{flav}_ployfit{s}", up=op.c_float(2*nom), down=op.c_float(nom/2))
    else: return nom 



dywBins_mjj   = [ 20., 100., 250., 400., 550., 700., 850., 1000., 1200. ]
dywBins_mlljj = [ 1200., 1000., 750., 600., 450., 300., 150., 100., 0. ]
dywParams_mjj = [ ## increasing with bins
    [  0.989336, -0.0281512,  0.00159644 , -3.26923e-05,  2.91737e-07, -9.62316e-10 ], #  20-100
    [  3.11184 , -0.0588639,  0.000610211, -2.93414e-06,  6.46817e-09, -5.03036e-12 ], # 100-250
    [ -397.166 ,  6.3012   , -0.0396388  ,  0.000123884, -1.92345e-07,  1.18686e-10 ], # 250-400
    [ -2475.04 , 26.5107   , -0.11327    ,  0.000241404, -2.56633e-07,  1.08871e-10 ], # 400-550
    [ -3400.2  , 28.1634   , -0.0929379  ,  0.000152793, -1.25158e-07,  4.08705e-11 ], # 550-700
    [ -24674.3 , 159.938   , -0.41424    ,  0.000535871, -3.46229e-07,  8.93798e-11 ], # 700-850
    None, #  850-1000
    None  # 1000-1200
    ]
dywParams_mlljj = [ ## decreasing with bins
    None, # above 1000
    [   377.449, - 2.2502  ,  0.00537447 , -6.40903e-06,  3.81405e-09, -9.05702e-13 ], # 750-1000
    [  6693.66 , -50.1891  ,  0.150396   , -0.000225099,  1.68271e-07, -5.02592e-11 ], # 600-750
    [  2370.41 , -23.004   ,  0.089117   , -0.000172186,  1.65919e-07, -6.37862e-11 ], # 450-600
    [  3779.94 , -62.4128  ,  0.427584   , -0.00155538 ,  3.1685e-06 , -3.42748e-09,  1.53821e-12 ], # 300-450
    [ -235.825 ,  7.86777  , -0.107775   ,  0.00079528 , -3.43158e-06,  8.68816e-09, -1.19786e-11, 6.94881e-15 ], # 150-300
    None, # 100-150
    None  # below 100
    ]

## do this only once
_dyw_expr_mjj   = None
_dyw_expr_mlljj = None

def splitDYweight(mjj, mlljj, withSystematic=False):
    mjj      = op.define(mjj)
    mlljj    = op.define(mlljj)
    noWeight = op.c_float(1.)
    
    if _dyw_expr_mjj is None:
        _dyw_expr_mjj   = [ (op.define("double", make_polynomial(mjj  , params)) if params else noWeight) for params in dywParams_mjj   ]
    if _dyw_expr_mlljj is None:
        _dyw_expr_mlljj = [ (op.define("double", make_polynomial(mlljj, params)) if params else noWeight) for params in dywParams_mlljj ]
    
    if withSystematic:
        def makeSystematic(wExpr, name):
            return op.systematic(wExpr, name=name, up=2*wExpr, down=wExpr/2)
    else:
        def makeSystematic(wExpr, name):
            return wExpr
    
    return op.multiSwitch(*([
        (mjj < dywBins_mjj[i], op.multiSwitch(*([
            (mlljj > dywBins_mlljj[j],
                makeSystematic(_dyw_expr_mjj[i-1]*_dyw_expr_mlljj[j-1], "DYweight{i:d}{j:d}")
                ) for j in range(1,len(dwyBins_mlljj))
            ]+[noWeight]))) for i in range(1,len(dywBins_mjj))
        ]+[noWeight]))


def DYPlusJetsCP(jets, dilepton, sel, uname, reg, n, doWgt=False, doSum=False, do0Btag=False):
    plots = []
    binScaling =1
    plots_ToSum2 = collections.defaultdict(list)

    nm = ''
    if do0Btag:
        nm += "0Btag"
    if doWgt:
        nm += f"DYweight_polyfit{n}"
    
    EqBIns = EqB(60 // binScaling, 0., 1200.)
    jj_p4  = (jets[0].p4 if reg=="boosted" else(jets[0].p4+jets[1].p4))
    mlljj  = (dilepton[0].p4 +dilepton[1].p4+jj_p4).M()
    mjj    = jj_p4.M()
    
    plt_mjj = Plot.make1D(f"{uname}_{reg}_{nm}_mjj",
                op.invariant_mass(jj_p4), sel,
                EqB(60 // binScaling, 0., 1200.), 
                title="m_{jj} (GeV)", plotopts=utils.getOpts(uname))
    
    plt_mlljj = Plot.make1D(f"{uname}_{reg}_{nm}_mlljj", 
                 (dilepton[0].p4 +dilepton[1].p4+jj_p4).M(), sel, EqBIns, 
                 title="m_{lljj} (GeV)", plotopts=utils.getOpts(uname))
    
    if doSum and not uname in ['ElMu', 'MuEl']:
        plots_ToSum2[(f"OSSF_{reg}_{nm}_mjj")].append(plt_mjj)
        plots_ToSum2[(f"OSSF_{reg}_{nm}_mlljj")].append(plt_mlljj)
    
    plots += [plt_mjj, plt_mlljj]
   # plots.append(Plot.make2D("{uname}_{reg}_{nm}_mlljj_vs_mjj", 
   #             (op.invariant_mass(jj_p4), (dilepton[0].p4 + dilepton[1].p4 + jj_p4).M()), sel,
   #             (EqB(60 // binScaling, 0., 1200.), EqB(60 // binScaling, 0., 1200.)), 
   #             title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
   # 
   # plots.append(Plot.make1D(f"{uname}_{reg}_{nm}_Jet_multiplicity", op.rng_len(jets), sel,
   #         EqB(7, 0., 7.), title="Jet multiplicity",
   #         plotopts=utils.getOpts(uname, **{"log-y": True})))
    return plots, plots_ToSum2


def getDYweightFromPolyfit(channel, era, reg, mass, polyfit, doSysts, doreweightDY):
    
    if doreweightDY == "comb": flav = 'LL'
    else: flav = channel if channel in ['ElEl', 'MuMu'] else ( 'LL')
            
    DYweight = { "mjj"          : computeDYweight(flav, era, reg, polyfit, mass, 'mjj', doSysts),
                #"mlljj"        : computeDYweight(flav, era, reg, polyfit, mass, 'mlljj', doSysts),
                #"mjj_vs_mlljj" : op.product( computeDYweight(flav, era, reg, polyfit, mass, 'mjj', doSysts), 
                #                             computeDYweight(flav, era, reg, polyfit, mass, 'mlljj', doSysts)) 
                }
    return DYweight        


def prepareCP_ForDrellYan0Btag(jets, jetType, dilepton, sel, uname, reg, era, wp, corrMET, doMETCut, doWgt, doSum):
    
    plots = []
    binScaling = 1
    non_bjets = {}
    plots_ToSum2 = collections.defaultdict(list)
    
    metCut = {'resolved' : 80. , 'boosted'  : 120. }
    nm = '' 
    if doMETCut:
        nm += 'MECut'
    if doWgt:
        nm += '_DYWeight'

    lambda_failbtag = {'DeepFlavour': lambda j: j.btagDeepFlavB < legacy_btagging_wpdiscr_cuts['DeepFlavour'][era][getIDX(wp)],
                       'DeepCSV'    : lambda j: op.AND(j.subJet1.btagDeepB < legacy_btagging_wpdiscr_cuts['DeepCSV'][era][getIDX(wp)],
                                                      j.subJet2.btagDeepB < legacy_btagging_wpdiscr_cuts['DeepCSV'][era][getIDX(wp)]) }

    for (tagger, lambda_), k in zip( lambda_failbtag.items(), ['resolved', 'boosted']):
        non_bjets[jetType[k]] = op.select(jets[k][tagger], lambda_)

    cut_per_cr = { 'resolved': [ op.rng_len(non_bjets["AK4"]) >= 2,  op.rng_len(non_bjets["AK8"]) == 0 ],
                   'boosted' : [ op.rng_len(non_bjets["AK4"]) >= 0,  op.rng_len(non_bjets["AK8"]) >= 1 ] }
    
    cut_ = cut_per_cr[reg]
    if doMETCut:
        cut_ += [corrMET.pt < metCut[reg]]
    sel = sel.refine(f'{uname}_{reg}_controlregion_2Lep2Jets_0Btag_{nm}_{wp}', cut=cut_ )

    cp_0Btag, cp_0BtagToSum = DYPlusJetsCP(non_bjets[jetType[reg]], dilepton, sel, uname, reg, '', doWgt=doWgt, doSum=doSum, do0Btag=True)
    plots += cp_0Btag
    plots_ToSum2.update(cp_0BtagToSum)

    return plots, plots_ToSum2


def ProduceFitPolynomialDYReweighting(jets, dilepton, sel, uname, reg, sampleCfg, era, isMC, doreweightDY, doSysts, doWgt, doSum):

    plots = []
    binScaling = 1
    plots_ToSum2 = collections.defaultdict(list)
    
    jj_p4  = (jets[0].p4 if reg=="boosted" else(jets[0].p4+jets[1].p4))
    mlljj  = (dilepton[0].p4 +dilepton[1].p4+jj_p4).M()
    mjj    = jj_p4.M()
        
    for deg in [4, 5, 6, 7, 8]:
        
        if isMC and "group" in sampleCfg.keys() and sampleCfg["group"]=='DY':
            sel = sel.refine(f"TwoLep_{uname}_TwoJets_{reg}_DYweight{doreweightDY}_fitpolynomial{deg}_on_mjj", 
                    weight=(getDYweightFromPolyfit(uname, era, reg, mjj, deg, doSysts, doreweightDY)['mjj'])
                    )  
            
        plt, pltToSum = DYPlusJetsCP(jets, dilepton, sel, uname, reg, deg, doWgt, doSum)
        plots += plt
        plots_ToSum2.update(pltToSum)
        
        ## deprecated !! 
       # if doreweightDY == "split":  # this shit split the the bin not the flavour 
       #     DY_weight = splitDYweight(mjj, mlljj, withSystematic=doSysts)
       #     sel       = sel.refine(f"TwoLep_{uname}_TwoJets_{reg}_DYweightsplit_fitpolynomial{deg}", weight= DY_weight)
       #     
       #     for i in range(len(dywBins_mjj)-1):
       #         plots.append(Plot.make1D(f"{uname}_{reg}_DYweight{i+1}_mjj",
       #         mjj, sel,
       #         EqB(60 // binScaling, dywBins_mjj[i], dywBins_mjj[i+1]),
       #         title="m_{jj} (GeV)", plotopts=utils.getOpts(uname)))

       #     for j in range(len(dywBins_mlljj)-1):
       #         plots.append(Plot.make1D(f"{uname}_{reg}_DYweight{i+1}_mjj", 
       #         mlljj, sel, 
       #         EqB(60 // binScaling, dywBins_mlljj[j+1], dywBins_mlljj[j]),
       #         title="m_{lljj} (GeV)", plotopts=utils.getOpts(uname)))
    
       #     for i in range(len(dywBins_mjj)-1):
       #         for j in range(0,len(dywBins_mlljj)-1):
       #             plots.append(Plot.make2D(f"{uname}_{reg}_DYweight{str(i+1)+str(j+1)}_mlljj_vs_mjj"), 
       #             (mjj, mlljj), sel,
       #             (EqB(60 // binScaling, dywBins_mjj[i], dywBins_mjj[i+1]), EqB(60 // binScaling, dywBins_mlljj[j+1], dywBins_mlljj[j])),
       #             title="mlljj vs mjj invariant mass (GeV)", plotopts=utils.getOpts(uname))
    
    return plots, plots_ToSum2
