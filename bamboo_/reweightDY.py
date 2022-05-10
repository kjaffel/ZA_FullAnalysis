import math 
import collections

from itertools import count

from bambooToOls import Plot
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op

import ControlPLots as cp 
import utils as utils
logger = utils.ZAlogger(__name__)

from corrections import legacy_btagging_wpdiscr_cuts, getIDX




lowmass_fitdeg = { '2017': 7, '2016': 6, '2018': 6 }

Wbin = { '2018': { 
            'mjj': { 'resolved': 0.8759782968236777, 'boosted': 1.227432451348542} 
            },
         '2017': {
            'mjj': { 'resolved': 0.8770810607491363, 'boosted': 1.348647409536511} 
            },
         '2016': {
            'mjj': { 'resolved': 0.8077143150622658, 'boosted': 1.2013532112004486} 
            },
        }


params= {"2018" : {
            "resolved":{
                "mjj" :{ 
                   "gaus"     : [1.0822423763279263, 56.56398715915372, 116.32754327175016],
                   "polyfit4" : [1.034605718208772, -0.0004270829975634808, 8.473848195198253e-08, 1.1013150137365994e-09, -1.102940957153749e-12],
                   "polyfit5" : [1.2725390495186923, -0.004515846104533641, 2.641063962191633e-05, -7.838236619282709e-08, 1.1187241530607319e-10, -6.080943796872629e-14],
                   "polyfit6" : [0.30084710933170705, 0.015308043684158513, -0.00013327932110435443, 5.722155344676238e-07, -1.3053460715535384e-09, 1.5096578470100668e-12, -6.944025588976976e-16], 
                   #"polyfit5" : [1.08749, 7.08012e-05, -1.20014e-05, 6.1579e-08, -1.16015e-10, 7.47516e-14],
                   #"polyfit6" : [1.00044, 0.0038611, -6.56131e-05, 3.9545e-07, -1.12175e-09, 1.5078e-12, -7.72459e-16],
                   "polyfit7" : [1.3022685317569929, -0.034432491468174446, 0.0016512606176447983, -3.72673536378935e-05, 4.576835606981712e-07, -3.196795999684774e-09, 1.1997919540224064e-11, -1.881459394268026e-14],
                   "polyfit8" : [0.819689, 0.0142191, -0.000273497, 2.40105e-06, -1.16514e-08, 3.31276e-11, -5.48911e-14, 4.90319e-17, -1.82273e-20], },
                "mlljj":{ "polyfit5": [], "polyfit6": [], "polyfit7": [], "polyfit8": [] },
                },
            "boosted":{
                "mjj" :{ 
                   "polyfit4" : [0.5214574601380083, 0.01859214633429711, -0.0002816817953501892, 2.2874559044387608e-06, -6.6731029729626076e-09],
                   "polyfit5" : [0.22511361825034543, 0.056500040958320195, -0.0017110434857865702, 2.4206536904262696e-05, -1.5016722082939275e-07, 3.3196793444291743e-10],
                   "polyfit6" : [0.010484433838894277, 0.09045975300612033, -0.003371923045291945, 5.973819924929447e-05, -5.182080188906546e-07, 2.1372968539882318e-09, -3.3515542865990556e-12],
                   "polyfit7" : [-0.031470798995090955, 0.09801385677398886, -0.0038153855561003595, 7.178633540220176e-05, -6.891969390969502e-07, 3.44040843958064e-09, -8.388068145487661e-12, 7.731554288052468e-15],
                   "polyfit8" : [0.5111142543036492, -0.0072330965574163575, 0.0031826933591692598, -0.00015422962603649465, 3.3460796025493813e-06, -3.833893202377691e-08, 2.4069181251653284e-10, -7.838245227767358e-13, 1.0366323999914486e-15] },
                "mlljj":{ "polyfit5": [], "polyfit6": [], "polyfit7": [], "polyfit8": [] },
                } },
         "2017": {
            "resolved":{
                "mjj" :{ 
                   "polyfit4" : [1.152176598218864, -0.0020422844511127822, 7.152737694025394e-06, -1.1448393189370134e-08, 6.44711781685869e-12],
                   "polyfit5" : [1.3801232178417888, -0.0059492928448710465, 3.223354886264208e-05, -8.691981758367944e-08, 1.1334205398360879e-10, -5.73381544464337e-14],
                   "polyfit6" : [2.0153772985867957, -0.018894833227991133, 0.00013639601619099535, -5.107992475051058e-07, 1.0356078193549463e-09, -1.0780972324389874e-12, 4.507824580682626e-16],
                   "polyfit7" : [1.0054835776605466, 0.008806636030245412, -0.000241771473129821, 2.060425650884798e-06, 1.7659744697556337e-08, -5.007468663004935e-10, 3.5924930516385478e-12, -8.604990265889853e-15],
                   "polyfit8" : [0.995164, 0.00807201, -0.000182662, 1.66017e-06, -8.07044e-09, 2.26621e-11, -3.6796e-14, 3.20529e-17, -1.1586e-20], },
                "mlljj":{ "polyfit5": [], "polyfit6": [], "polyfit7": [], "polyfit8": [] },
                },
            "boosted":{
                "mjj" :{ 
                   "polyfit4" : [0.2584583801399659, 0.041553266007364933, -0.0008937277618853796, 8.442209270637238e-06, -2.7164683244688575e-08],
                   "polyfit5" : [-0.048605960850894615, 0.08584526113799579, -0.0027750961846746114, 4.134523529403004e-05, -2.7662988936943165e-07, 6.773615932996195e-10],
                   "polyfit6" : [0.003475753735330718, 0.07685640670304562, -0.002285133715324669, 2.9438115232154373e-05, -1.3407731208093658e-07, -1.4260891647725791e-10, 1.8055227622291502e-12],
                   "polyfit7" : [0.22231118199244163, 0.03521648017102988, 0.00038290122427623186, -5.17158829667705e-05, 1.183812942000472e-06, -1.18484838648949e-08, 5.533258195319094e-11, -9.837659044637665e-14],
                   "polyfit8" : [-0.09625304340813554, 0.09962380919293297, -0.004212683965644147, 0.00011141716912926973, -2.085932864601584e-06, 2.687537543121554e-08, -2.1309417522946533e-10, 9.074379757262561e-13, -1.5715852886745835e-15] },
                "mlljj":{ "polyfit5": [], "polyfit6": [], "polyfit7": [], "polyfit8": [] },
                } },
         "2016": {
            "resolved":{
                "mjj" :{ 
                   "polyfit4" : [0.9889931848165128, -0.000544589050691719, 7.441951024979822e-08, 1.2387762553168746e-09, -9.705976475823552e-13],
                   "polyfit5" : [1.0624656529782537, -0.0018166952070341605, 8.327241374256804e-06, -2.3857939887818038e-08, 3.49361181341457e-11, -1.9441969667149026e-14],
                   "polyfit6" : [-2.70000225368728, 0.2966474478595168, -0.008649465114158894, 0.00012485839862755695, -9.6726641434877e-07, 3.860837536058572e-09, -6.248369896309235e-12],
                   "polyfit7" : [-0.6093858049230907, 0.03562847576698422, -0.0003326076359470201, 1.6132739914923534e-06, -4.4525714671794065e-09, 7.024079763606414e-12, -5.882545850758073e-15, 2.024007071114549e-18],
                   "polyfit8" : [-1.8943733538339877, 0.07018361450203607, -0.0007235775397023531, 4.044731757291916e-06, -1.3551268066480687e-08, 2.8032805744957324e-11, -3.516598356865861e-14, 2.4598990047233443e-17, -7.385454121405439e-21] },
                "mlljj":{ "polyfit5": [], "polyfit6": [], "polyfit7": [], "polyfit8": [] },
                },
            "boosted":{
                "mjj" :{ 
                   "polyfit4" : [1.0346942029617776, -0.0004280563491231081, 8.842571460544656e-08, 1.0954355472324608e-09, -1.0992945284398048e-12],
                   "polyfit5" : [1.271297157307099, -0.004493960205844131, 2.626716972595754e-05, -7.79440472925773e-08, 1.1124486935085089e-10, -6.046980614735008e-14],
                   "polyfit6" : [0.9224482164809054, 0.004400671529467422, 5.10434954806032e-05, -2.528146229571015e-06, 2.577493957408236e-08, -1.0528039083293618e-10, 1.5135148969961207e-13],
                   "polyfit7" : [2.468475409287014, -0.035866910259390025, 0.000361536506042286, -1.9689892235612242e-06, 6.19184048793147e-09, -1.1224756986985306e-11, 1.0867338375084365e-14, -4.340954656550783e-18], 
                   "polyfit8" : [9.5502249570474, -0.22548830693003025, 0.002497636744210916, -1.519618691719842e-05, 5.548266648142491e-08, -1.245868936809853e-10, 1.6829731244401187e-13, -1.252932939072611e-16, 3.9446667413180274e-20] },
                "mlljj":{ "polyfit5": [], "polyfit6": [], "polyfit7": [], "polyfit8": [] },
                } },
            }


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


def computeDYweight(era, reg, n, mass, name, doSysts):
    fits_rng = { '2016': {
                    'resolved': [30., 650.],'boosted': [30., 200.] },
                 '2017': { 
                    'resolved': [0., 650.], 'boosted': [0., 150.]  },
                 '2018': {
                    'resolved': [20., 650.],'boosted': [20., 200.] },
                }

    if reg == 'boosted':
        nom = op.switch(mass < fits_rng[era][reg][1], make_polynomial(mass, params[era][reg][name][f"polyfit{n}"]), op.c_float(Wbin[era][name][reg]))
    elif reg == 'resolved':
        nom = op.multiSwitch( (op.in_range(fits_rng[era][reg][0], mass, 150.), make_polynomial(mass, params[era][reg][name][f"polyfit{lowmass_fitdeg[era]}"])),
                              (op.in_range(150., mass, fits_rng[era][reg][1]), make_polynomial(mass, params[era][reg][name][f"polyfit{n}"]))
                             , op.c_float(Wbin[era][name][reg]))
    
    s = f"_lowmass{lowmass_fitdeg[era]}_highmass{n}" if reg == "resolved" else f"_lowmass{n}"
    #return op.switch(mass < 650., op.define("double", make_polynomial(mass, params[name][f"polyfit{n}"])), op.c_float(1.))
    if doSysts: return op.systematic(op.c_float(nom), name=f"DYweight_{reg}_{name}_ployfit{s}", up=op.c_float(2*nom), down=op.c_float(nom/2))
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


def getDYweightFromPolyfit(era, reg, mass, polyfit, doSysts):
            
    DYweight = { "mjj"          : computeDYweight(era, reg, polyfit, mass, 'mjj', doSysts),
                #"mlljj"        : computeDYweight(era, reg, polyfit, mass, 'mlljj', doSysts),
                #"mjj_vs_mlljj" : op.product(computeDYweight(era, reg, polyfit, mass, 'mjj', doSysts), computeDYweight(era, reg, polyfit, mass, 'mlljj', doSysts)) 
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
                       'DeepCSV'    : lambda j: op.OR(j.subJet1.btagDeepB < legacy_btagging_wpdiscr_cuts['DeepCSV'][era][getIDX(wp)],
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


def ProduceFitPolynomialDYReweighting(jets, dilepton, sel, uname, reg, reweightDY, sampleCfg, era, isMC, doSysts, doWgt, doSum):

    plots = []
    binScaling = 1
    plots_ToSum2 = collections.defaultdict(list)
    
    jj_p4  = (jets[0].p4 if reg=="boosted" else(jets[0].p4+jets[1].p4))
    mlljj  = (dilepton[0].p4 +dilepton[1].p4+jj_p4).M()
    mjj    = jj_p4.M()
        
    for polyfit in [4, 5, 6, 7, 8]:
        if reweightDY == "comb":            
            if isMC and "group" in sampleCfg.keys() and sampleCfg["group"]=='DY':
                sel = sel.refine(f"TwoLep_{uname}_TwoJets_{reg}_DYweightcomb_fitpolynomial{polyfit}_on_mjj", weight=(getDYweightFromPolyfit(era, reg, mjj, polyfit, doSysts)['mjj']))  
            
            plt, pltToSum = DYPlusJetsCP(jets, dilepton, sel, uname, reg, polyfit, doWgt, doSum)
            plots += plt
            plots_ToSum2.update(pltToSum)

        if reweightDY == "split": 
            if isMC and "group" in sampleCfg.keys() and sampleCfg["group"]=='DY' and uname in ['ElEl','MuMu']:
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
    
    return plots, plots_ToSum2
