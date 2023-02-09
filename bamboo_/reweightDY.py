import os, os.path, sys
import math 
import collections
import json
import importlib
import numpy as np

from itertools import count

from bambooToOls import Plot
from bamboo import treefunctions as op
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo.plots import VariableBinning as VarBin

import ControlPLots as cp 
import utils as utils
logger = utils.ZAlogger(__name__)

from corrections import legacy_btagging_wpdiscr_cuts, getIDX

def pogEraFormat(era):
    return "UL" + era.replace('20', '').replace('-','')


def BinFormat(_tup):
    return '{}_to_{}'.format(int(_tup[0]),int(_tup[1]))


def get_JsonWeights(era, flav):
    era_ = pogEraFormat(era)
    jsf  = f"DYJetsTo{flav}_TuneCP5_13TeV-amcatnloFXFX-pythia8_polyfitWeights_RunIISummer20{era_}_NanoAODv9.json"
    f    = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "DYreweighting_run2", jsf))
    params = json.load(f)
    return params


def TMultiLayerPerceptron(mass, reg, flav, era):
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "DYreweighting_run2", "perceptron_nn"))
    dyrwt = importlib.import_module(f"dyrwt_fct_{reg}_{flav}_{era}")
    dyrwt_fct  = getattr(dyrwt, f"dyrwt_fct_{reg}_{flav}_{era}")
    w = dyrwt_fct()
    return w.value(0, mass)


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


def computeDYweight(flav, era, reg, fitdegree, fitrange, mass, name, doSysts):
    params   = get_JsonWeights(era, flav)
    
    if reg == 'boosted':
        s   = f"_lowmass{fitdegree}"
        #nom= op.c_float(TMultiLayerPerceptron(mass, reg, flav, era))
        nom = op.switch( mass < fitrange[0][1], 
                            make_polynomial(mass, params[era][reg][name][f"lowmass_{BinFormat(fitrange[0])}"][f"polyfit{fitdegree}"]), 
                        op.c_float(params[era][reg][name][f"binWgt_above_{int(fitrange[0][1])}"]['binWgt']) )
    
    elif reg == 'resolved':
        s   = f"_lowmass{fitdegree[0]}_highmass{fitdegree[1]}" 
        nom = op.multiSwitch( (op.in_range(fitrange[0][0], mass, fitrange[0][1]), make_polynomial(mass, params[era][reg][name][f"lowmass_{BinFormat(fitrange[0])}"][f"polyfit{fitdegree[0]}"])),
                              (op.in_range(fitrange[1][0], mass, fitrange[1][1]), make_polynomial(mass, params[era][reg][name][f"highmass_{BinFormat(fitrange[1])}"][f"polyfit{fitdegree[1]}"]))
                             , op.c_float(params[era][reg][name][f"binWgt_above_{int(fitrange[1][1])}"]['binWgt']))
    
    if doSysts: return op.systematic(op.c_float(nom), name=f"DYweight_{reg}_{flav.lower()}_ployfit{s}", up=op.c_float(2*(nom-1)+1), down=op.c_float((nom-1)/2+ 1))
    else: return nom 


### depreacted , no longer in use
#dywBins_mjj   = [ 20., 100., 250., 400., 550., 700., 850., 1000., 1200. ]
#dywBins_mlljj = [ 1200., 1000., 750., 600., 450., 300., 150., 100., 0. ]
#dywParams_mjj = [ ## increasing with bins
#    [  0.989336, -0.0281512,  0.00159644 , -3.26923e-05,  2.91737e-07, -9.62316e-10 ], #  20-100
#    [  3.11184 , -0.0588639,  0.000610211, -2.93414e-06,  6.46817e-09, -5.03036e-12 ], # 100-250
#    [ -397.166 ,  6.3012   , -0.0396388  ,  0.000123884, -1.92345e-07,  1.18686e-10 ], # 250-400
#    [ -2475.04 , 26.5107   , -0.11327    ,  0.000241404, -2.56633e-07,  1.08871e-10 ], # 400-550
#    [ -3400.2  , 28.1634   , -0.0929379  ,  0.000152793, -1.25158e-07,  4.08705e-11 ], # 550-700
#    [ -24674.3 , 159.938   , -0.41424    ,  0.000535871, -3.46229e-07,  8.93798e-11 ], # 700-850
#    None, #  850-1000
#    None  # 1000-1200
#    ]
#dywParams_mlljj = [ ## decreasing with bins
#    None, # above 1000
#    [   377.449, - 2.2502  ,  0.00537447 , -6.40903e-06,  3.81405e-09, -9.05702e-13 ], # 750-1000
#    [  6693.66 , -50.1891  ,  0.150396   , -0.000225099,  1.68271e-07, -5.02592e-11 ], # 600-750
#    [  2370.41 , -23.004   ,  0.089117   , -0.000172186,  1.65919e-07, -6.37862e-11 ], # 450-600
#    [  3779.94 , -62.4128  ,  0.427584   , -0.00155538 ,  3.1685e-06 , -3.42748e-09,  1.53821e-12 ], # 300-450
#    [ -235.825 ,  7.86777  , -0.107775   ,  0.00079528 , -3.43158e-06,  8.68816e-09, -1.19786e-11, 6.94881e-15 ], # 150-300
#    None, # 100-150
#    None  # below 100
#    ]
#
### do this only once
#_dyw_expr_mjj   = None
#_dyw_expr_mlljj = None
#

def getIDX(wp = None):
    return (0 if wp=="L" else ( 1 if wp=="M" else 2))


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

def DYPlusJetsCP(jets, dilepton, sel, uname, reg, fitdegree, doWgt=False, doSum=False, do0Btag=False):
    plots = []
    binScaling =1
    plots_ToSum2 = collections.defaultdict(list)
    
    nm = ''
    if do0Btag:
        nm += "0Btag"
    if doWgt:
        if reg == 'resolved': s = f"_lowmass{fitdegree[0]}_highmass{fitdegree[1]}" 
        else: s = f"_lowmass{fitdegree}_highmassBinWgt"
        nm += f"DYweight_polyfit{s}"
   
    #BIns  = EqB(60 // binScaling, 0., 1200.)
    BIns   = { 'resolved': VarBin(np.arange(0., 600., 10).tolist()+np.arange(600., 1201., 200).tolist()),
               'boosted' : VarBin(np.arange(0., 150., 10).tolist()+[150., 600., 800., 1000., 1200.]), 
               } 
    
    jj_p4  = (jets[0].p4 if reg=="boosted" else(jets[0].p4+jets[1].p4))
    mlljj  = (dilepton[0].p4 +dilepton[1].p4+jj_p4).M()
    mjj    = jj_p4.M()
    
    plt_mjj = Plot.make1D(f"{uname}_{reg}_{nm}_mjj",
                op.invariant_mass(jj_p4), sel, BIns[reg],
                title="m_{jj} (GeV)", plotopts=utils.getOpts(uname))
    
    plt_mlljj = Plot.make1D(f"{uname}_{reg}_{nm}_mlljj", 
                 (dilepton[0].p4 +dilepton[1].p4+jj_p4).M(), sel, BIns[reg], 
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


def getDYweightFromPolyfit(channel, era, reg, k, mass, polyfit, fitrange, doSysts=False, doreweightDY=''):
    
    if doreweightDY == "comb": flav = 'LL'
    else: flav = channel if channel in ['ElEl', 'MuMu'] else ( 'LL')
            
    DYweight = { "mjj"          : computeDYweight(flav, era, reg, polyfit, fitrange, mass, 'mjj', doSysts),
                #"mlljj"        : computeDYweight(flav, era, reg, polyfit, fitrange, mass, 'mlljj', doSysts),
                #"mjj_vs_mlljj" : op.product( computeDYweight(flav, era, reg, polyfit, fitrange, mass, 'mjj', doSysts), 
                #                             computeDYweight(flav, era, reg, polyfit, fitrange, mass, 'mlljj', doSysts)) 
                }
    return DYweight[k]

def prepareCP_ForDrellYan0Btag(jets, bjets, dilepton, sel, uname, reg, era, wp, fitdegree, corrMET, doMETCut=False, doWgt=False, doSum=False):
    plots = []
    binScaling = 1
    plots_ToSum2 = collections.defaultdict(list)
    
    nm = '' 
    if doMETCut:
        nm += 'MECut'
    if doWgt:
        nm += '_DYWeight'
    _tag = 'DeepCSV' if reg == 'boosted' else 'DeepFlavour'

    _0btag = { 'resolved': [ op.rng_len(bjets['resolved']['DeepFlavour'][wp]) < 2,  op.rng_len(bjets['boosted']['DeepCSV'][wp]) == 0 ],
               'boosted' : [ op.rng_len(bjets['boosted']['DeepCSV'][wp]) < 1 ] }
    
    _0btag_cuts = _0btag[reg]
    if doMETCut:
        _0btag_cuts += [corrMET.pt < 80.]
    
    sel = sel.refine(f'{uname}_{reg}_controlregion_2Lep2Jets_0Btag_{nm}_{wp}', cut=_0btag_cuts )

    cp_0Btag, cp_0BtagToSum = DYPlusJetsCP(jets, dilepton, sel, uname, reg, fitdegree, doWgt=doWgt, doSum=doSum, do0Btag=True)
    plots += cp_0Btag
    plots_ToSum2.update(cp_0BtagToSum)
    return plots, plots_ToSum2


def ProduceFitPolynomialDYReweighting(jets, dilepton, sel, uname, reg, sampleCfg, era, isMC, fitrange, doreweightDY='split', doSysts=False, doWgt=False, doSum=False):
    plots = []
    binScaling = 1
    plots_ToSum2 = collections.defaultdict(list)
    
    jj_p4  = (jets[0].p4 if reg=="boosted" else(jets[0].p4+jets[1].p4))
    mlljj  = (dilepton[0].p4 +dilepton[1].p4+jj_p4).M()
    mjj    = jj_p4.M()
    
    TestFits = {"resolved":[ (4,4), (5,4), (6,4), (7,4), (8,4)], # (low,high) mass degree fit
                "boosted" :[ 2, 3, 4, 5, 6, 7, 8] } # just one fit 
    
    for fitdegree in TestFits[reg]:
        if isMC and "group" in sampleCfg.keys() and sampleCfg["group"]=='DY' and uname in ['MuMu', 'ElEl']:
            
            if reg == 'resolved':   s   = f"_lowmass{fitdegree[0]}_highmass{fitdegree[1]}" 
            else: s   = f"_lowmass{fitdegree}_highmassBinWgt"
            
            sel = sel.refine(f"TwoLep_{uname}_TwoJets_{reg}_DYweight{doreweightDY}_fitpolynomial{s}_on_mjj", 
                    weight=(getDYweightFromPolyfit(channel=uname, era=era, reg=reg, k='mjj', mass=mjj, polyfit=fitdegree, fitrange=fitrange, doSysts=doSysts, doreweightDY=doreweightDY)) )  
            
        plt, pltToSum = DYPlusJetsCP(jets, dilepton, sel, uname, reg, fitdegree, doWgt, doSum)
        plots += plt
        plots_ToSum2.update(pltToSum)
    return plots, plots_ToSum2
        
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
    
