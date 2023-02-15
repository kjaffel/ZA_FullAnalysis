import collections
from bamboo import treefunctions as op
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB

import utils as utils
import corrections as corr
import ControlPLots as cp

from bambooToOls import Plot



def freeze(d):
    if isinstance(d, dict):
        return frozenset((key, freeze(value)) for key, value in d.items())
    elif isinstance(d, list):
        return tuple(freeze(value) for value in d)
    return d


def key_for_value(d):
    """Return a key in neseted dic `d` having a sub-key ."""
    for k, v in d.items():
        if k == "350-850" or k == "350-840":
            return k


def get_BoostedEventWeight(era, tagger, wp, fatjet):
    if "2016" in era:
        DeepDoubleBvL= {
                "350-850":{  
                    # var: (loose, medium1, medium2, tight1, tight2)
                    "up":      (0.10, 0.11, 0.11, 0.10, 0.20),
                    "down":    (0.04, 0.04, 0.04, 0.08, 0.10),
                    "nominal": (0.95, 0.86, 0.77, 0.74, 0.68)
                    }
                }
        DoubleB= {
                "350-850":{  
                    # var: (loose, medium1, medium2, tight)
                    "up":      (0.06, 0.06, 0.07, 0.08),
                    "down":    (0.13, 0.10, 0.13, 0.14),
                    "nominal": (1.03, 1.01, 0.95, 0.90)
                    }
                }
    elif "2017" in era:
        DeepDoubleBvL= {
                "250-350":{
                    # var: (loose, medium1, medium2, tight1, tight2)
                    "up":      (0.04, 0.04, 0.05, 0.04, 0.05),
                    "down":    (0.04, 0.05, 0.05, 0.05, 0.05),
                    "nominal": (0.92, 0.82, 0.72, 0.62, 0.57)
                    },
                "350-850":{  
                    "up":      (0.07, 0.06, 0.05, 0.06, 0.15),
                    "down":    (0.12, 0.10, 0.07, 0.11, 0.23),
                    "nominal": (1.01, 0.77, 0.68, 0.65, 0.54)
                    }
                }
        DoubleB = { 
                "250-350":{
                    # var: (loose, medium1, medium2, tight)
                    "up":      (0.03, 0.04, 0.04, 0.04),
                    "down":    (0.03, 0.03, 0.04, 0.04),
                    "nominal": (0.96, 0.93, 0.85, 0.78)
                    },
                "350-840":{  
                    "up":      (0.06, 0.08, 0.07, 0.04),
                    "down":    (0.04, 0.04, 0.04, 0.04),
                    "nominal": (0.95, 0.9,  0.8,  0.72)
                    }
                }
    elif "2018" in era:
        DeepDoubleBvL= {
                "250-350":{
                    # var: (loose, medium1, medium2, tight1, tight2)
                    "up":      (0.04, 0.07, 0.06, 0.07, 0.05),
                    "down":    (0.05, 0.05, 0.05, 0.05, 0.05),
                    "nominal": (0.97, 0.81, 0.74, 0.65, 0.61)
                    },
                "350-850":{  
                    "up":      (0.07, 0.06, 0.07, 0.10, 0.07),
                    "down":    (0.06, 0.05, 0.06, 0.05, 0.09),
                    "nominal": (0.96, 0.76, 0.70, 0.67, 0.69)
                    }
                }
        DoubleB= {
                "250-350":{
                    # var: (loose, medium1, medium2, tight)
                    "up":      (0.04, 0.05, 0.08, 0.05),
                    "down":    (0.04, 0.05, 0.04, 0.07),
                    "nominal": (0.93, 0.93, 0.89, 0.82)
                    },
                "350-850":{  
                    "up":      (0.05, 0.06, 0.05, 0.05),
                    "down":    (0.04, 0.04, 0.05, 0.06),
                    "nominal": (0.98, 0.89, 0.84, 0.76)
                    }
                }

    idx = ( 0 if wp=='L' else (1 if wp=='M1' else ( 2 if wp=="M2" else( 3 if wp =="T1"else (4 if wp =="T2" else(3))))))
    dic = (DeepDoubleBvL if tagger =="DeepDoubleBvL" else (DoubleB))
    pTrange = key_for_value(dic)
    pTmax = float(key_for_value(dic).split('-')[-1])    

    if era in ["2017", "2018"]:
        if op.in_range(250., fatjet[0].pt, 350.):
            nominal = dic["250-350"]["nominal"][idx]
            up = nominal + dic["250-350"]["up"][idx] 
            down = nominal - dic["250-350"]["down"][idx]
    elif "2016" in era:
        if op.in_range(350., fatjet[0].pt, pTmax):
            nominal = dic[pTrange]["nominal"][idx] 
            up = nominal + dic[pTrange]["up"][idx]
            down = nominal - dic[pTrange]["down"][idx]
    return op.systematic(op.c_float(nominal), name="{0}{1}".format(tagger, wp), up=op.c_float(up), down=op.c_float(down)) 


def get_DeepDoubleX(AK8jets, discr, discr_cut):
    
    if discr == 'btagDDBvLV2':
        # DeepDoubleX (mass-decorrelated) discriminator for H(Z)->bb vs QCD
        cleaned_AK8JetsbtagDDBvL = op.sort(AK8jets, lambda j: -j.btagDDBvLV2)
        return op.select(cleaned_AK8JetsbtagDDBvL, lambda j : j.btagDDBvLV2 >= discr_cut)
    
    elif discr == 'btagDDBvL_noMD':
        # DeepDoubleX discriminator (no mass-decorrelation) for H(Z)->bb vs QCD
        cleaned_AK8JetsbtagDDBvL_noMD = op.sort(AK8jets, lambda j: -j.btagDDBvL_noMD)
        return op.select(cleaned_AK8JetsbtagDDBvL_noMD, lambda j : j.btagDDBvL_noMD >= discr_cut)
    
    elif discr == 'deepTagMD_HbbvsQCD':
        # Mass-decorrelated DeepBoostedJet tagger H->bb vs QCD discriminator
        cleaned_AK8JetsdeepTagMD_HbbvsQCD = op.sort(AK8jets, lambda j: -j.deepTagMD_HbbvsQCD)
        return op.select(cleaned_AK8JetsdeepTagMD_HbbvsQCD, lambda j : j.deepTagMD_HbbvsQCD >= discr_cut)
    
    elif discr == 'deepTagMD_ZHbbvsQCD':
        # Mass-decorrelated DeepBoostedJet tagger Z/H->bb vs QCD discriminator
        cleaned_AK8JetsdeepTagMD_ZHbbvsQCD = op.sort(AK8jets, lambda j: -j.deepTagMD_ZHbbvsQCD)
        return op.select(cleaned_AK8JetsdeepTagMD_ZHbbvsQCD, lambda j : j.deepTagMD_ZHbbvsQCD >= discr_cut)
    else:
        raise RuntimeError(f'sorry {discr} is unkown')


def get_bestSubjetsCut(wp, sel, bJets_resolved_PassdeepflavourWP_noPuppi, bTagEventWeight4WP, channel, ll, fatjet, corrMET, optstex, era, doProduceSum, btv, doPass_bTagEventWeight, isMC):
    plots = []
    plots_ToSum2 = collections.defaultdict(list)
    binScaling = 1
    cfr = {} 
    
    weight = { 'nb3-boosted' : None, 'nb2-boosted' : None }

    if doPass_bTagEventWeight and isMC:
        weight = { 'nb3-boosted' : [ bTagEventWeight['bb_associatedProduction']['boosted'][f'DeepCSV{wp}'],
                                     bTagEventWeight['bb_associatedProduction']['mix_ak4_rmPuppi'][f'DeepFlavour{wp}'] ],
                    'nb2-boosted': [ bTagEventWeight['gg_fusion']['boosted'][f'DeepCSV{wp}'],
                                     bTagEventWeight['gg_fusion']['mix_ak4_rmPuppi'][f'DeepFlavour{wp}'] ] }
    
    
    cleaned_AK8JetsByDeepB = op.sort(fatjet, lambda j: -j.btagDeepB)
    wpdiscr_cut      = corr.BoostedTopologiesWP['DeepCSV'][era][wp]
    subjets_btag_req = corr.get_subjets_requirements('DeepCSV', wp, wpdiscr_cut, era)
    
    for scenario, lambda_f in subjets_btag_req['b'].items(): 

        subjets_AK8_scenarios = op.select(cleaned_AK8JetsByDeepB, lambda_f)

        llxsubjets_noMET_boosted = { 
                "nb2": sel.refine("{}_ll_jj_{}_METcut_NobTagEventWeight_DeepCSV{}_{}_ggH_Boosted".format(channel, scenario, wp, channel),
                                cut    = [ op.rng_len(subjets_AK8_scenarios) >= 1, corrMET.pt < 80.],
                                weight = weight['nb2-boosted']),
                "nb3": sel.refine("{}_ll_jj_{}_METcut_NobTagEventWeight_DeepCSV{}_{}_bbH_Boosted".format(channel, scenario, wp, channel),
                                cut    = [ op.rng_len(subjets_AK8_scenarios) >= 1, op.rng_len(bJets_resolved_PassdeepflavourWP_noPuppi) >= 1, corrMET.pt < 80.],
                                weight = weight['nb3-boosted'])
                }
        
        cfr[f'{channel}_DeepCSV{wp}_{scenario}'] = { 
                "nb2":
                        ( f"nb=2 -boosted: {optstex} + == 1 AK8 b-jets boosted (DeepCSV{wp}, {scenario}) + "+"$p_{T}^{miss}$ cut",
                            llxsubjets_noMET_boosted["nb2"] ),
                "nb3":
                        ( f"nb=3 -boosted: {optstex} + $>1$ AK8 b-jets boosted (DeepCSV{wp}, {scenario}) + "+"$p_{T}^{miss}$ cut",
                            llxsubjets_noMET_boosted["nb3"] ),
                }

        for reco, sel in llxsubjets_noMET_boosted.items():
            
            selDict = {f'DeepCSV{wp}': sel}
            bjets   = { 'DeepCSV': {wp: subjets_AK8_scenarios }}
            suffix  = 'METCut_{}bTagWgt_{}'.format('No' if weight==None else '', scenario) 

            final_cp, final_cpToSum = cp.makeControlPlotsForFinalSel(selDict, bjets, ll, channel, 'boosted', suffix, reco, doProduceSum, btv)
            bjets_cp, bjets_cpToSum = cp.makeBJetPlots(selDict, bjets, channel, 'boosted', suffix, era, reco, doProduceSum, btv)
            
            plots.extend(final_cp)
            plots.extend(bjets_cp)
            plots_ToSum2.update(final_cpToSum)
            plots_ToSum2.update(bjets_cpToSum)
        
    return plots, plots_ToSum2, cfr
