import math
from bamboo import treefunctions as op
from bambooToOls import Plot
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB

from itertools import count
import json
import utils
from utils import *
import logging
logger = logging.getLogger("DY-Reweighting Plotter")

def make_polynomial(x, parameters):
    def powers_of(x):
        yield x
        for i in count(2):
            yield pow(x, i)
    return parameters[0] + sum((ip*xp if xp is not None else ip) for xp, ip in zip(powers_of(x), parameters[1:]))

def computeMjjDYweight(polyfit, mjj):
    if polyfit == 6:
        params = [0.464072, 0.00858327, -5.59681e-05, 1.84772e-07, -3.13559e-10, 2.60306e-13, -8.34964e-17]
    elif polyfit == 7:
        params = [0.351096, 0.0123158, -9.83683e-05, 4.09614e-07, -9.35209e-10, 1.18034e-12, -7.72464e-16, 2.04656e-19]
    elif polyfit == 8:
        params = [0.235811, 0.0167315, -0.000159053, 8.14858e-07, -2.41448e-09, 4.27276e-12, -4.45537e-15, 2.52335e-18, -5.97895e-22]
    return op.switch(mjj < 1000., make_polynomial(mjj, params), op.c_float(1.))

def computeMlljjDYweight(polyfit, mlljj):
    if polyfit == 6:
        params = [0.95354, -0.0014433, 1.7198e-05, -6.33959e-08, 1.06627e-10, -8.32855e-14, 2.45032e-17]
    elif polyfit == 7:
        params = [0.999776, -0.0031661, 3.72034e-05, -1.65345e-07, 3.67378e-10, -4.31665e-13, 2.56178e-16, -6.04134e-20]
    elif polyfit == 8:
        params = [1.05604, -0.00571127, 7.40208e-05, -4.06435e-07, 1.19328e-09, -2.00697e-12, 1.93595e-15, -9.9492e-19, 2.1092e-22]
    return op.switch(mlljj < 1000., make_polynomial(mlljj, params), op.c_float(1.))

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
_dyw_expr_mjj = None
_dyw_expr_mlljj = None

def getDYWeightAcrossPlane_inBins(mjj, mlljj, withSystematic=False):
    mjj = op.define(mjj)
    mlljj = op.define(mlljj)
    noWeight = op.c_float(1.)
    if _dyw_expr_mjj is None:
        _dyw_expr_mjj   = [ (op.define("double", make_polynomial(mjj  , params)) if params else noWeight) for params in dywParams_mjj   ]
    if _dyw_expr_mlljj is None:
        _dyw_expr_mlljj = [ (op.define("double", make_polynomial(mlljj, params)) if params else noWeight) for params in dywParams_mlljj ]
    if withSystematic:
        def makeSystematic(wExpr, name):
            return op.systematic(wExpr, name=name, up=2*wExpr-1, down=noWeight)
    else:
        def makeSystematic(wExpr, name):
            return wExpr
    return op.multiSwitch(*([
        (mjj < dywBins_mjj[i], op.multiSwitch(*([
            (mlljj > dywBins_mlljj[j],
                makeSystematic(_dyw_expr_mjj[i-1]*_dyw_expr_mlljj[j-1], "DY_weight{i:d}{j:d}")
                ) for j in range(1,len(dwyBins_mlljj))
            ]+[noWeight]))) for i in range(1,len(dywBins_mjj))
        ]+[noWeight]))

def plotsWithDYReweightings(jets, dilepton, TwoLepTwoJetsSel_NoDYweight, uname, suffix, isDY_reweight, splitDY_weightIn64Regions):
    # TODO up and down variations
    plots = []
    binScaling =1
    reweightDY_acrossmassplane = False # need to get the splitted plots first 
    Jets_ = (jets[0].p4 if suffix=="boosted" else(jets[0].p4+jets[1].p4))
    mlljj = (dilepton[0].p4 +dilepton[1].p4+Jets_).M()
    mjj = op.invariant_mass(Jets_)
   
    #mass distribution plots not reweighted: needed for comaparaison later : better keep all plots with 0. to 1200. GeV bins 
    EqBIns = EqB(60 // binScaling, 0., 1200.)
    
    plots.append(Plot.make1D("{0}_{1}_noDYweight_mjj".format(uname, suffix),
                op.invariant_mass(Jets_), TwoLepTwoJetsSel_NoDYweight,
                EqB(60 // binScaling, 0., 1200.), 
                title="mjj [GeV]", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make1D("{0}_{1}_noDYweight_mlljj".format(uname, suffix), 
                (dilepton[0].p4 +dilepton[1].p4+Jets_).M(), TwoLepTwoJetsSel_NoDYweight, EqBIns, 
                title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make2D("{0}_{1}_noDYweight_mlljj_vs_mjj".format(uname, suffix), 
                (op.invariant_mass(Jets_), (dilepton[0].p4 + dilepton[1].p4 + Jets_).M()), TwoLepTwoJetsSel_NoDYweight,
                (EqB(60 // binScaling, 0., 1200.), EqB(60 // binScaling, 0., 1200.)), 
                title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make1D(f"{uname}_{suffix}_noDYweight_Jet_mulmtiplicity".format(suffix=suffix), op.rng_len(jets), TwoLepTwoJetsSel_NoDYweight,
            EqB(7, 0., 7.), title="Jet mulmtiplicity",
            plotopts=utils.getOpts(uname, **{"log-y": True})))
    
    
    for sys in ["nominal"]:#, "up_and_down"]:
        for polyfit in [6, 7, 8]:
                
            mjj_DYweight = computeMjjDYweight(polyfit, mjj)
            mlljj_DYweight = computeMlljjDYweight(polyfit, mlljj)
            NLO_DYweight = op.product(mjj_DYweight, mlljj_DYweight) if isDY_reweight else op.c_float(1.)
            
            logger.info(" start DY reweighting no mass range splits ** ")
            print (mjj_DYweight, mlljj_DYweight, NLO_DYweight)  
            # Assuming up and down variations of 100%
            if sys == "up_and_down":
                mjj_DYweight = op.systematic(op.c_float(mjj_DYweight), name="DY_weight_mjjployfit%s"%polyfit, up=op.c_float(2*mjj_DYweight-1), down= op.c_float(1.))
                mlljj_DYweight = op.systematic(op.c_float(mlljj_DYweight), name="DY_weight_mlljjpolyfit%s"%polyfit, up=op.c_float(2*mlljj_DYweight-1), down= op.c_float(1.))
                NLO_DYweight = op.systematic(op.c_float(NLO_DYweight), name="DY_weight_mjjmlljjpolyfit%s"%polyfit, up=op.c_float(2*NLO_DYweight-1), down= op.c_float(1.))
                
            
            for DYweight, mass_distribution in zip( [mjj_DYweight, mlljj_DYweight, NLO_DYweight ],['mjj', 'mlljj', 'mjjmlljj']):
                sel = TwoLepTwoJetsSel_NoDYweight.refine("add_%s_DYweight_%s_fitpolynomial%s_%s_%s"%(mass_distribution, sys, polyfit, suffix, uname), weight=(DYweight))  
            
                plots.append(Plot.make1D("{0}_{1}_{2}DYweight_{3}_fitpolynomial{4}_Jet_mulmtiplicity".format(uname, suffix, mass_distribution, sys, polyfit), 
                            op.rng_len(jets), sel,
                            EqB(7, 0., 7.), title="Jet mulmtiplicity",
                            plotopts=utils.getOpts(uname, **{"log-y": True})))
    
                plots.append(Plot.make1D("{0}_{1}_{2}DYweight_{3}_fitpolynomial{4}_mjj".format(uname, suffix, mass_distribution, sys, polyfit),
                            op.invariant_mass(Jets_), sel,
                            EqB(60 // binScaling, 0., 1200.), 
                            title="mjj [GeV]", plotopts=utils.getOpts(uname, **{"log-y": True})))
        
                plots.append(Plot.make1D("{0}_{1}_{2}DYweight_{3}_fitpolynomial{4}_mlljj".format(uname, suffix, mass_distribution, sys, polyfit),
                            (dilepton[0].p4 +dilepton[1].p4+Jets_).M(), sel, EqBIns, 
                            title="mlljj [GeV]", plotopts=utils.getOpts(uname, **{"log-y": True})))
                
                plots.append(Plot.make2D("{0}_{1}_{2}DYweight_{3}_fitpolynomial{4}_mlljjvsmjj".format(uname, suffix, mass_distribution, sys, polyfit),
                            (op.invariant_mass(Jets_), (dilepton[0].p4 + dilepton[1].p4 + Jets_).M()), sel, 
                            (EqB(60 // binScaling, 0., 1200.), EqB(60 // binScaling, 0., 1200.)), 
                            title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname, **{"log-y": True})))
        
    if splitDY_weightIn64Regions: # split to reweight later 
        for i in range(len(dywBins_mjj)-1):
            plots.append(Plot.make1D("{0}_{1}_DY_weight{2}_mjj".format(uname, suffix, i+1),
                    op.invariant_mass(Jets_), TwoLepTwoJetsSel_NoDYweight,
                    EqB(60 // binScaling, dywBins_mjj[i], dywBins_mjj[i+1]),
                    title="mjj [GeV]", plotopts=utils.getOpts(uname)))
    
        for j in range(len(dywBins_mlljj)-1):
            plots.append(Plot.make1D("{0}_{1}_DY_weight{2}_mlljj".format(uname, suffix, j+1), 
                    (dilepton[0].p4 +dilepton[1].p4+Jets_).M(), TwoLepTwoJetsSel_NoDYweight, 
                    EqB(60 // binScaling, dywBins_mlljj[j+1], dywBins_mlljj[j]),
                    title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
        for i in range(len(dywBins_mjj)-1):
            for j in range(0,len(dywBins_mlljj)-1):
                plots.append(Plot.make2D("{0}_{1}_DY{2}_mlljj_vs_mjj".format(uname, suffix, str(i+1)+str(j+1)), 
                        (op.invariant_mass(Jets_), (dilepton[0].p4 + dilepton[1].p4 + Jets_).M()), TwoLepTwoJetsSel_NoDYweight,
                        (EqB(60 // binScaling, dywBins_mjj[i], dywBins_mjj[i+1]), EqB(60 // binScaling, dywBins_mlljj[j+1], dywBins_mlljj[j])),
                        title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
    
    if reweightDY_acrossmassplane:    
        for systematic in ["nominal"]:#, "up_and_down"]:
            DY_weight = getDYWeightAcrossPlane_inBins(mjj, mlljj, withSystematic=False)
            selection = TwoLepTwoJetsSel_NoDYweight.refine("TwoLep_%s_atleastTwoJets_selection_%s_DY_weight%s_%s"%(uname, suffix, ij, systematic), weight= DY_weight)
            plots.append(Plot.make1D("{0}_{1}_{2}_DYweightsplit64_mjj".format(uname, suffix, systematic),
                        mjj, selection,
                        EqBIns, title="mjj [GeV]", plotopts=utils.getOpts(uname)))
    
            plots.append(Plot.make1D("{0}_{1}_{2}_DYweightsplit64_mlljj".format(uname, suffix, systematic),
                        mlljj, selection, 
                        EqBIns, title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
        
            plots.append(Plot.make2D("{0}_{1}_{2}_DYweightsplit64_mlljjvsmjj".format(uname, suffix, systematic),
                        (mjj, mlljj), selection, 
                        (EqBIns, EqBIns), title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
    return plots
    
def Plots_gen(gen_ptll_nlo, sel, suffix):
    plots =[]
    binScaling = 1
    EqBIns = EqB(60 // binScaling, 0., 1200.)
    plots.append(Plot.make1D("{0}_genptll_nlo".format(suffix),
                    gen_ptll_nlo, sel,
                    EqBIns, title="gen pt [GeV]"))
        
    # follow xavier methods 
    return plots
def PLots_withtthDYweight(uname, dilepton, jets, sel, suffix, isDY_reweight, era):
    plots =[]
    binScaling = 1
    EqBIns = EqB(60 // binScaling, 0., 1200.)
    from systematics import get_tthDYreweighting
    nloDYweight= get_tthDYreweighting(era, jets) if isDY_reweight else None
    sel.refine("%s_DY_reweighting_%s_fromtthanalysis"%(uname, suffix), weight=nloDYweight)
    
    plots.append(Plot.make1D("{0}_{1}_njets_tthDYnloweight".format(uname, suffix),
                        op.rng_len(jets), sel,
                        EqB(7, 0., 7.), title="Jet mulmtiplicity", plotopts=utils.getOpts(uname, **{"log-y": True})))
    
    Jets_ = (jets[0].p4 if suffix=="boosted" else(jets[0].p4+jets[1].p4))
    mlljj = (dilepton[0].p4 +dilepton[1].p4+Jets_).M()
    mjj = op.invariant_mass(Jets_)

    plots.append(Plot.make1D("{0}_{1}_mjj_tthDYnloweight".format(uname, suffix),
                        mjj, sel,
                        EqBIns, title="mjj [GeV]", plotopts=utils.getOpts(uname)))
    plots.append(Plot.make1D("{0}_{1}_mlljj_tthDYnloweight".format(uname, suffix),
                        mlljj, sel,
                        EqBIns, title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
    return plots
