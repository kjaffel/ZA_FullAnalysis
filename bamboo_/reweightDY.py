from itertools import count

from bambooToOls import Plot
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op

import ControlPLots as cp 
import utils as utils
logger = utils.ZAlogger(__name__)

from corrections import legacy_btagging_wpdiscr_cuts, getIDX


params = { "mjj" :{ 
                   #"polyfit5": [1.13022, -0.00206761, 7.0697e-06, -6.26383e-09,-2.42928e-12, 3.84415e-15], # from Alessia 
                    "polyfit5": [1.14848, -0.00238057, 1.26116e-05, -3.02804e-08, 2.94413e-11, -8.11821e-15],
                    "polyfit6": [1.10581, -0.000579711, -1.24577e-05, 1.24543e-07, -4.35216e-10, 6.53688e-13, -3.5751e-16],
                    "polyfit7": [1.02821, 0.00337486, -8.17319e-05, 6.91043e-07, -2.85085e-09, 6.16721e-12, -6.72335e-15, 2.91445e-18],
                    "polyfit8": [0.913459, 0.0102199, -0.000227116, 2.18773e-06, -1.12665e-08, 3.32601e-11, -5.64071e-14, 5.10749e-17, -1.91183e-20] },
          "mlljj":{ "polyfit5": [],
                    "polyfit6": [],
                    "polyfit7": [],
                    "polyfit8": [] }
          }

def make_polynomial(x, parameters):
    def powers_of(x):
        yield x
        for i in count(2):
            yield pow(x, i)
    return parameters[0] + sum((ip*xp if xp is not None else ip) for xp, ip in zip(powers_of(x), parameters[1:]))

def computeDYweight(n, mass, name):
    #return op.switch(mass < 650., op.define("double", make_polynomial(mass, params[name][f"polyfit{n}"])), op.c_float(1.))
    return op.switch(mass < 650., make_polynomial(mass, params[name][f"polyfit{n}"]), op.c_float(1.))

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


def DYPlusJetsCP(jets, dilepton, sel, uname, reg, n, doWgt):
    plots = []
    binScaling =1

    nm     = "" if doWgt else "no"
    EqBIns = EqB(60 // binScaling, 0., 1200.)
    jj_p4  = (jets[0].p4 if reg=="boosted" else(jets[0].p4+jets[1].p4))
    mlljj  = (dilepton[0].p4 +dilepton[1].p4+jj_p4).M()
    mjj    = jj_p4.M()
    
    plots.append(Plot.make1D(f"{uname}_{reg}_{nm}DYweight_fit{n}_mjj",
                op.invariant_mass(jj_p4), sel,
                EqB(60 // binScaling, 0., 1200.), 
                title="m_{jj} (GeV)", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make1D(f"{uname}_{reg}_{nm}DYweight_fit{n}_mlljj", 
                (dilepton[0].p4 +dilepton[1].p4+jj_p4).M(), sel, EqBIns, 
                title="m_{lljj} (GeV)", plotopts=utils.getOpts(uname)))
    
   # plots.append(Plot.make2D("{uname}_{reg}_{nm}DYweight_fit{n}_mlljj_vs_mjj", 
   #             (op.invariant_mass(jj_p4), (dilepton[0].p4 + dilepton[1].p4 + jj_p4).M()), sel,
   #             (EqB(60 // binScaling, 0., 1200.), EqB(60 // binScaling, 0., 1200.)), 
   #             title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
   # 
   # plots.append(Plot.make1D(f"{uname}_{reg}_{nm}DYweight_fit{n}_Jet_multiplicity", op.rng_len(jets), sel,
   #         EqB(7, 0., 7.), title="Jet multiplicity",
   #         plotopts=utils.getOpts(uname, **{"log-y": True})))

    return plots


def getDYSysts(nom, polyfit, mass):
    # Assuming up and down variations of 100%
    return op.systematic(op.c_float(nom), name=f"DYweight_{mass}_ployfit{polyfit}", up=op.c_float(2*nom-1), down= op.c_float(1.))


def getDYweightFromPolyfit(mass, polyfit, doSysts):
            
    DYweight = { "mjj"          : computeDYweight(polyfit, mass, 'mjj'),
                #"mlljj"        : computeDYweight(polyfit, mass, 'mlljj'),
                #"mjj_vs_mlljj" : op.product(computeDYweight(polyfit, mass, 'mjj'), computeDYweight(polyfit, mass, 'mlljj')) 
                }
    if doSysts:
        fullDYweight = { "mjj"          : getDYSysts(DYweight['mjj'], polyfit, 'mjj'),
                        #"mlljj"        : getDYSysts(DYweight['mlljj'], polyfit, 'mlljj'),
                        #"mjj_vs_mlljj" : op.product(getDYSysts(DYweight['mjj'], polyfit, 'mjj_vs_mlljj'),  getDYSysts(DYweight['mlljj'], polyfit, 'mjj_vs_mlljj')) 
                        }
    else:
        fullDYweight = DYweight
    return  fullDYweight        


def prepareCP_ForDrellYan0Btag(jets, jetType, dilepton, sel, uname, reg, era, wp, corrMET, doMETCut):
    
    plots = []
    binScaling = 1
    
    metCut = {'resolved' : 80. , 'boosted'  : 120. }
    nm = '' if doMETCut else 'no'
    lambda_failbtag = {'DeepFlavour': lambda j: j.btagDeepFlavB < legacy_btagging_wpdiscr_cuts['DeepFlavour'][era][getIDX(wp)],
                       'DeepCSV'    : lambda j: op.OR(j.subJet1.btagDeepB < legacy_btagging_wpdiscr_cuts['DeepCSV'][era][getIDX(wp)],
                                                      j.subJet2.btagDeepB < legacy_btagging_wpdiscr_cuts['DeepCSV'][era][getIDX(wp)])
                      }
    non_bjets = {}
    for (tagger, lambda_), k in zip( lambda_failbtag.items(), ['resolved', 'boosted']):
        non_bjets[jetType[k]] = op.select(jets[k][tagger], lambda_)

    cut_per_cr = { 'resolved': [ op.rng_len(non_bjets["AK4"]) >= 2,  op.rng_len(non_bjets["AK8"]) == 0 ],
                   'boosted' : [ op.rng_len(non_bjets["AK4"]) >= 0,  op.rng_len(non_bjets["AK8"]) >= 1 ] }
    
    cut_ = cut_per_cr[reg]
    if doMETCut:
        cut_ += [corrMET.pt < metCut[reg]]
    sel = sel.refine(f'{uname}_{reg}_controlregion_2Lep2Jets_0btag_{nm}MET_{wp}', cut=cut_ )

    plots.extend(cp.makeControlPlotsForBasicSel(sel, non_bjets[jetType[reg]], dilepton, f'{uname}_noBtag', reg))
    
    return plots


def DYReweightingValidationPlots(jets, dilepton, sel, uname, reg, reweightDY, sampleCfg, isMC, doSysts):

    plots = []
    binScaling = 1
    
    jj_p4  = (jets[0].p4 if reg=="boosted" else(jets[0].p4+jets[1].p4))
    mlljj  = (dilepton[0].p4 +dilepton[1].p4+jj_p4).M()
    mjj    = jj_p4.M()
        
    for polyfit in [5, 6, 7, 8]:
        if reweightDY == "comb":            
            if isMC and "group" in sampleCfg.keys() and sampleCfg["group"]=='DY':
                sel = sel.refine(f"TwoLep_{uname}_TwoJets_{reg}_DYweightcomb_fitpolynomial{polyfit}_on_mjj", weight=(getDYweightFromPolyfit(mjj, polyfit, doSysts)['mjj']))  
            plots += DYPlusJetsCP(jets, dilepton, sel, uname, reg, polyfit, doWgt=True)

        if reweightDY == "split": 
            if isMC and "group" in sampleCfg.keys() and sampleCfg["group"]=='DY':
                DY_weight = splitDYweight(mjj, mlljj, withSystematic=doSysts)
                sel       = sel.refine(f"TwoLep_{uname}_TwoJets_{reg}_DYweightsplit_fitpolynomial{polyfit}", weight= DY_weight)
            
            for i in range(len(dywBins_mjj)-1):
                plots.append(Plot.make1D(f"{uname}_{reg}_DYweight{i+1}_mjj",
                mjj, sel,
                EqB(60 // binScaling, dywBins_mjj[i], dywBins_mjj[i+1]),
                title="m_{jj} (GeV)", plotopts=utils.getOpts(uname)))

            for j in range(len(dywBins_mlljj)-1):
                plots.append(Plot.make1D(f"{uname}_{reg}_DYweight{i+1}_mjj", 
                mlljj, sel, 
                EqB(60 // binScaling, dywBins_mlljj[j+1], dywBins_mlljj[j]),
                title="m_{lljj} (GeV)", plotopts=utils.getOpts(uname)))
    
            for i in range(len(dywBins_mjj)-1):
                for j in range(0,len(dywBins_mlljj)-1):
                    plots.append(Plot.make2D(f"{uname}_{reg}_DYweight{str(i+1)+str(j+1)}_mlljj_vs_mjj"), 
                    (mjj, mlljj), sel,
                    (EqB(60 // binScaling, dywBins_mjj[i], dywBins_mjj[i+1]), EqB(60 // binScaling, dywBins_mlljj[j+1], dywBins_mlljj[j])),
                    title="mlljj vs mjj invariant mass (GeV)", plotopts=utils.getOpts(uname))
    return plots
