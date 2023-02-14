import os
import collections
import numpy as np 
from functools import partial

from bamboo import scalefactors
from bamboo import treefunctions as op
from bamboo import treedecorators as td
from bamboo.plots import EquidistantBinning as EqB
from bamboo.analysisutils import forceDefine
from bamboo.analysisutils import makePileupWeight
from bamboo.analysisutils import configureRochesterCorrection, configureJets, configureType1MET
from bamboo.scalefactors import get_correction, BtagSF

import utils as utils
from bambooToOls import Plot
from scalefactorslib import all_scalefactors, all_run2_Ulegacyscalefactors


#https://cms-nanoaod.github.io/correctionlib/index.html
#https://cms-nanoaod-integration.web.cern.ch/commonJSONSFs/
#https://indico.cern.ch/event/1096988/contributions/4615134/attachments/2346047/4000529/Nov21_btaggingSFjsons.pdf
#https://gitlab.cern.ch/vanderli/btv-json-sf/-/blob/master/convert_subjetSF.py

eoy_btagging_wpdiscr_cuts = {
                "DeepCSV":{ # era: (loose, medium, tight)
                            "2016":(0.2217, 0.6321, 0.8953), 
                            "2017":(0.1522, 0.4941, 0.8001), 
                            "2018":(0.1241, 0.4184, 0.7527) 
                          },
                "DeepFlavour":{
                            "2016":(0.0614, 0.3093, 0.7221), 
                            "2017":(0.0521, 0.3033, 0.7489), 
                            "2018":(0.0494, 0.2770, 0.7264) 
                          }
                }

legacy_btagging_wpdiscr_cuts = {
                "DeepCSV":{ # era: (loose, medium, tight)
                            "2016-preVFP" :(0.2027, 0.6001, 0.8819),  
                            "2016-postVFP":(0.1918, 0.5847, 0.8767),
                            "2016":(0.2217, 0.6321, 0.8953),
                            "2017":(0.1355, 0.4506, 0.7738), 
                            "2018":(0.1208, 0.4168,  0.7665) 
                          },
                "DeepFlavour":{
                            "2016-preVFP" :(0.0508, 0.2598, 0.6502), 
                            "2016-postVFP":(0.0480, 0.2489, 0.6377),
                            "2016":(0.0614, 0.3093, 0.7221),
                            "2017":(0.0532, 0.3040, 0.7476), 
                            "2018":(0.0490, 0.2783, 0.7100) 
                          }
                }
        
# same discriminator cut for Full run2 
BoostedTopologiesWP = {
    "DeepCSV":{
        "2016-preVFP" : {"L":0.2027, "M":0.6001}, 
        "2016-postVFP": {"L":0.1918, "M":0.5847}, 
        "2017": {"L":0.1355, "M":0.4506}, 
        "2018": {"L":0.1208, "M":0.4506} }, 
    "DoubleB":{
        "L": 0.3, "M1": 0.6, "M2": 0.8, "T": 0.9 },
    "DeepDoubleBvLV2":{
        "L1": 0.64, "L2": 0.7, "M1": 0.86, "M2": 0.89, "T1": 0.91, "T2": 0.92}
    }


scalesfactorsLIB = {
     "DeepFlavour": {
          year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
           {"2016": "2016/Btag/DeepJet_2016LegacySF_V1.csv", 
            "2017": "2017/Btag/DeepFlavour_94XSF_V4_B_F.csv", 
            "2018": "2018/Btag/DeepJet_102XSF_V1.csv"}.items() },
     "DeepCSV" : {
        "Ak4": {
            year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
               {"2016": "2016/Btag/DeepCSV_2016LegacySF_V1.csv" , 
                "2017": "2017/Btag/DeepCSV_94XSF_V5_B_F.csv" , 
                "2018": "2018/Btag/DeepCSV_102XSF_V1.csv"}.items() },
        "softdrop_subjets": {
            year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
               {"2016": "2016/Btag/subjet_DeepCSV_2016LegacySF_V1.csv" , 
                "2017": "2017/Btag/subjet_DeepCSV_94XSF_V4_B_F_v2.csv" , 
                "2018": "2018/Btag/subjet_DeepCSV_102XSF_V1.csv"}.items() }, }
    }


scalesfactorsULegacyLIB = {
    "DeepFlavour": {
        year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
           {"2016-preVFP" : "2016UL/Btag/DeepJet_106XUL16preVFPSF_v1__prelegacyformat.csv", 
            "2016-postVFP": "2016UL/Btag/DeepJet_106XUL16postVFPSF_v2__prelegacyformat.csv", 
            "2017": "2017UL/Btag/wp_deepJet_106XUL17_v3__prelegacyformat.csv", 
            "2018": "2018UL/Btag/wp_deepJet_106XUL18_v2__prelegacyformat.csv"}.items() },
    "DeepCSV" : {
        "Ak4": {
            year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
              {"2016-preVFP"  :"2016UL/Btag/DeepCSV_106XUL16preVFPSF_v1__prelegacyformat.csv", 
                "2016-postVFP":"2016UL/Btag/DeepCSV_106XUL16postVFPSF_v2__prelegacyformat.csv", 
                "2017": "2017UL/Btag/wp_deepCSV_106XUL17_v3__prelegacyformat.csv" , 
                "2018": "2018UL/Btag/wp_deepCSV_106XUL18_v2__prelegacyformat.csv"}.items() },
        "softdrop_subjets": {
            year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
               {"2016-preVFP" :"2016UL/Btag/subjet_deepCSV_106XUL16preVFP_v1.csv",
                "2016-postVFP":"2016UL/Btag/subjet_deepCSV_106XUL16postVFP_v1.csv",
                "2017": "2017UL/Btag/subjet_DeepCSV_106X_UL17_SF.csv" , 
                "2018": "2018UL/Btag/subjet_deepCSV_106XUL18_v1.csv"}.items() }, }
    }


# maps name of systematic to name of correction inside of jsons
leptonSFLib = {
    "electron_ID"     : "UL-Electron-ID-SF",
    "electron_reco"   : "UL-Electron-ID-SF",
    "muon_reco"       : "NUM_TrackerMuons_DEN_genTracks",
    "muon_ID"         : "NUM_MediumID_DEN_TrackerMuons",
    "muon_iso"        : "NUM_TightRelIso_DEN_TightIDandIPCut",
    "muon_trigger": {
        "2016-preVFP" : "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight",
        "2016-postVFP": "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight",
        "2017"        : "NUM_IsoMu27_DEN_CutBasedIdTight_and_PFIsoTight",
        "2018"        : "NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight"},
    "TkMu50_muon_trigger":{
        "2016-preVFP" : "NUM_Mu50_or_TkMu50_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose",
        "2016-postVFP": "NUM_Mu50_or_TkMu50_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose",
        "2017"        : "NUM_Mu50_or_OldMu100_or_TkMu100_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose",
        "2018"        : "NUM_Mu50_or_OldMu100_or_TkMu100_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose"},
    }


def pogEraFormat(era):
    return era.replace("-", "") + "_UL"


def POGTaggerFormat(tagger):
    return tagger.replace('DeepFlavour', 'deepJet').replace('DeepCSV', 'deepCSV')


def getIDX(wp):
    return (0 if wp=="loose" else ( 1 if wp=="medium" else 2))


def getYearFromEra(era):
    if '2016' in era: return '16'
    elif '2017' in era: return '17'
    elif '2018' in era: return '18'


def get_subjets_requirements(tagger, wp, wpdiscr_cut, era): 
    subjets_btag_req = { 
        "b": { 
            "atleast_1subjet_pass": lambda j : op.OR(j.subJet1.btagDeepB >= wpdiscr_cut, j.subJet2.btagDeepB >= wpdiscr_cut),
            "both_subjets_pass"   : lambda j : op.AND(j.subJet1.btagDeepB >= wpdiscr_cut, j.subJet2.btagDeepB >= wpdiscr_cut),
            "fatjet_pass"         : lambda j : j.btagDeepB >= wpdiscr_cut,
            },
        "light":{ 
            "atleast_1subjet_notpass": lambda j : op.OR(j.subJet1.btagDeepB < wpdiscr_cut, j.subJet2.btagDeepB < wpdiscr_cut),
            "both_subjets_notpass"   : lambda j : op.AND(j.subJet1.btagDeepB < wpdiscr_cut, j.subJet2.btagDeepB < wpdiscr_cut),
            "fatjet_notpass"         : lambda j : j.btagDeepB < wpdiscr_cut,
            },
    }
    return subjets_btag_req


def localizePOGSF(era, POG, fileName):
    return os.path.join("/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration", "POG", POG, pogEraFormat(era), fileName)


def localize_btv_json_files( era, data, fileName):
    return os.path.join("/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/scripts_ToExtractSFs/", data, 'UL'+era.replace('-',''), fileName)


def getLeptonSF(era, correctionSet,):
    if "muon_trigger" in correctionSet:
        corrName = leptonSFLib[correctionSet][era]
    else:
        corrName = leptonSFLib[correctionSet]
    
    if "muon" in correctionSet:
        path = localizePOGSF(era, "MUO", "muon_Z.json.gz")
    elif correctionSet == "electron_trigger":
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "scale-factors", "eleTrigSFs", era + "_EleTriggerSF_NanoAODv2_v0.json") 
    elif "electron" in correctionSet:
        path = localizePOGSF(era, "EGM", "electron.json.gz")
    
    return path, corrName


def getScaleFactor(era, noSel, correctionSet, systName, pt_=None, wp=None, defineOnFirstUse=True):
    fileName, correction = getLeptonSF(era, correctionSet)

    if "muon" in correctionSet:
        etaParam = "abseta"
        etaExpr  = lambda mu: op.abs(mu.eta)
    elif "electron" in correctionSet:
        etaParam = "eta"
        etaExpr  = lambda el: el.eta + el.deltaEtaSC
    else:
        raise ValueError("Only muon or electron SFs are handled here!")

    if "muon" in correctionSet :
        return get_correction(fileName, correction, params={"pt": lambda mu: mu.pt, etaParam: etaExpr, "year": pogEraFormat(era)},
                              systParam="ValType", systNomName="sf",
                              systVariations={f"{systName}up": "systup", f"{systName}down": "systdown"},
                              defineOnFirstUse=defineOnFirstUse, sel=noSel)
    else:
        return get_correction(fileName, correction, params={"pt": pt_, etaParam: etaExpr, "year": era.replace("-", ""), "WorkingPoint": wp },
                              systParam="ValType", systNomName="sf",
                              systVariations={f"{systName}up": "sfup", f"{systName}down": "sfdown"},
                              defineOnFirstUse=defineOnFirstUse, sel=noSel)


def get_bTagSF_fixWP(tagger, wp, flav, era, sel, dobJetER=False, isSignal=False, defineOnFirstUse=False, use_nominal_jet_pt=False, heavy_method="comb",
                syst_prefix="", decorr_eras=True, full_scheme=False, full_scheme_mapping=None):
    params = { 
            "noJet_bRegCorr" : { "pt": lambda j: op.forSystematicVariation(j.pt, "nominal") if use_nominal_jet_pt else j.pt,
                                 "abseta": lambda j: op.abs(j.eta), "working_point": wp, "flavor": flav },
            "Jet_bRegCorr" : { "pt": lambda j: op.forSystematicVariation(j.pt*j.bRegCorr, "nominal") if use_nominal_jet_pt else j.pt*j.bRegCorr,
                               "abseta": lambda j: op.abs(j.eta), "working_point": wp, "flavor": flav }
            }
    
    syst_prefix = f"btagSF_{tagger}_fixWP_"
    systName = syst_prefix + ("light" if flav == 0 else "heavy")
    systVariations = {}
    
    for d in ("up", "down"):
        if tagger == 'deepCSV_subjet':
            systVariations[f"{systName}{d}"] = d
        else:
            if not decorr_eras and not full_scheme:
                systVariations[f"{systName}{d}"] = d
            if decorr_eras and (not full_scheme or flav == 0):
                systVariations[f"{systName}{d}"] = f"{d}_correlated"
                systVariations[f"{systName}_{era}{d}"] = f"{d}_uncorrelated"
            if full_scheme and flav > 0:
                systVariations[f"{syst_prefix}statistic_{era}{d}"] = f"{d}_statistic"
                for var,varBTV in full_scheme_mapping.items():
                    if varBTV is None:
                        systVariations[f"{syst_prefix}{var}{d}"] = f"{d}_{var}"
                    else:
                        systVariations[f"{var}{d}"] = f"{d}_{varBTV}"
    
    prefix = "" if tagger =='deepJet' and flav ==5 and dobJetER and isSignal else "no"
    
    if tagger == 'deepCSV_subjet':
        #path_localizePOGSF = localize_btv_json_files(era, 'btv-json-sf/data', 'subjet_tagging.json')
        jsf_nm = 'subjet_btagging.json.gz'
        correction = tagger
        method = "incl" if flav == 0 else 'lt'
        params[f"{prefix}Jet_bRegCorr"].update({'method':method }) 
    else:
        jsf_nm = 'btagging.json.gz'
        method = "incl" if flav == 0 else heavy_method
        correction = f"{tagger}_{method}"
        #FIXME tmp fix to the issue here: https://cms-talk.web.cern.ch/t/ul-b-tagging-sf-update/20209
        if tagger == 'DeepJet' and era == "2016-postVFP" and flav == 0:
            era = "2016-preVFP"

    path_localizePOGSF = localizePOGSF(era, "BTV", jsf_nm)
    
    return get_correction(path_localizePOGSF, correction, params=params[f"{prefix}Jet_bRegCorr"],
                          systParam="systematic", systNomName="central",
                          systVariations=systVariations, defineOnFirstUse=defineOnFirstUse, sel=sel)


def get_Ulegacyscalefactor(objType, key, periods=None, combine=None, additionalVariables=dict(), paramDefs= scalefactors.binningVariables_nano, getFlavour=None, systName=None, isElectron=False, isULegacy=False):
    return scalefactors.get_scalefactor(objType, key, periods = periods, 
                                        combine               = combine,
                                        additionalVariables   = additionalVariables,
                                        sfLib                 = all_run2_Ulegacyscalefactors if isULegacy else all_scalefactors,
                                        paramDefs             = paramDefs,
                                        getFlavour            = getFlavour,
                                        isElectron            = isElectron,
                                        systName              = systName)

def getL1PreFiringWeight(tree):
    return op.systematic(tree.L1PreFiringWeight_Nom, name="L1PreFiring", up=tree.L1PreFiringWeight_Up, down=tree.L1PreFiringWeight_Dn)


class makeYieldPlots:
    def __init__(self):
        self.calls = 0
        self.plots = []
    def addYields(self, sel, name, title):
        """
            Make Yield plot and use it also in the latex yield table
            sel     = refine selection
            name    = name of the PDF to be produced
            title   = title that will be used in the LateX yield table
        """
        self.plots.append(Plot.make1D("Yield_"+name,   
                        op.c_int(0),
                        sel,
                        EqB(1, 0., 1.),
                        title = title + " Yield",
                        plotopts = {"for-yields":True, "yields-title":title, 'yields-table-order':self.calls}))
        self.calls += 1
    def returnPlots(self):
        return self.plots


def makePUWeight(tree, era, selection):
    goldenJSON = f"Collisions{getYearFromEra(era)}_UltraLegacy_goldenJSON"
    puTuple = (localizePOGSF(era, "LUM", "puWeights.json.gz"), goldenJSON)
    PUWeight= makePileupWeight(puTuple, tree.Pileup_nTrueInt, systName="pileup", sel=selection)
    return PUWeight


def catchHLTforSubPrimaryDataset(year, fullEra, evt, isMC=False):
    if fullEra:
        era = fullEra[0] ## catch things like "C1" and "C2"
    else:
        era = ""
    hlt = evt.HLT
    def _getSel(hltSel):
        if str(hltSel) != hltSel:
            return [ getattr(hlt, sel) for sel in hltSel ]
        else:
            return [ getattr(hlt, hltSel) ]
    def forEra(hltSel, goodEras):
        if isMC or era in goodEras:
            return _getSel(hltSel)
        else:
            return []
    def notForEra(hltSel, badEras):
        if isMC or era not in badEras:
            return _getSel(hltSel)
        else:
            return []
    def fromRun(hltSel, firstRun, theEra, otherwise=True):
        if isMC:
            return _getSel(hltSel)
        elif fullEra == theEra:
            sel = _getSel(hltSel)
            return [ op.AND((evt.run >= firstRun), (op.OR(*sel) if len(sel) > 1 else sel[0])) ]
        elif otherwise:
            return _getSel(hltSel)
        else:
            return []
    if year == "2018":
        return {
            "SingleMuon"     : [ 
                                hlt.IsoMu24, 
                                hlt.IsoMu27, #not in the list of the recomended triggers for 2018 : 
                                # https://twiki.cern.ch/twiki/bin/view/CMS/MuonHLT2018#Recommended_trigger_paths_for_20
                                #hlt.IsoMu27, 
                                 hlt.Mu50, hlt.OldMu100, hlt.TkMu100 ], 
                                # OldMu100 and TkMu100 are recommend to recover inefficiencies at high pt but it seems to me for 2016 Only
                                # (https://indico.cern.ch/event/766895/contributions/3184188/attachments/1739394/2814214/IdTrigEff_HighPtMu_Min_20181023_v2.pdf)
            "DoubleMuon"     : [
                                 #hlt.Mu37_TkMu27,
                                 hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,
                                 hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                                 hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8, #  Only DZ_MassX versions unprescaled!! 
                                 hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8 ],
                                # Lowest unprescaled seed L1_LooseIsoEG30er2p1_Jet34er2p5_dR_Min0p3 
                                # (from run 317170 L1_LooseIsoEG28er2p1_Jet34er2p5_dR_Min0p3)
            "EGamma"         : [ 
                                 hlt.Ele30_eta2p1_WPTight_Gsf_CentralPFJet35_EleCleaned, 
                                 hlt.DiEle27_WPTightCaloOnly_L1DoubleEG,
                                 hlt.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL, 
                                 #hlt.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, #Both DZ and non DZ versions unprescaled **DO not use DZ version**
                                 hlt.Ele32_WPTight_Gsf, 
                                 #hlt.Ele35_WPTight_Gsf, 
                                 #hlt.Ele38_WPTight_Gsf,
                                 hlt.Ele28_eta2p1_WPTight_Gsf_HT150,  
                                 #hlt_Ele30_WPTight_Gsf, # [321397,322381], corresponding to runs in Run2018D
                                 hlt.DoubleEle25_CaloIdL_MW, # NON ISOLATED 
                                 hlt.Ele50_CaloIdVT_GsfTrkIdT_PFJet165,
                                 hlt.Ele115_CaloIdVT_GsfTrkIdT, 
                                 hlt.DoublePhoton70,
                                 ],#+ notForEra('Ele28_WPTight_Gsf','ABC') +forEra("Ele30_WPTight_Gsf", 'D'),
            "MuonEG"         : [ 
                                 hlt.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, 
                                 hlt.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,
                                 hlt.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ,  # Non DZ versions are prescaled 
                                 hlt.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,
                                 hlt.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ, # Non DZ versions are prescaled 
                                 hlt.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,
                                 #hlt.Mu27_Ele37_CaloIdL_MW, 
                                 #hlt.Mu37_Ele27_CaloIdL_MW 
                                 ]
            }


def bJetEnergyRegression(bjet):
    return op.map(bjet, lambda j : op.construct("ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>", (j.pt*j.bRegCorr, j.eta, j.phi, j.mass*j.bRegCorr)))


def JetEnergyRegression(jet):
    return op.map( jet, lambda j: op.construct("ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >", (
                                                                        op.product( j.pt, op.multiSwitch( (j.hadronFlavour == 5 , j.bRegCorr), (j.hadronFlavour == 4, j.cRegCorr), op.c_float(1) ) ), 
                                                                        j.eta, j.phi, 
                                                                        op.product( j.mass, op.multiSwitch( (j.hadronFlavour == 5 , j.bRegCorr), (j.hadronFlavour == 4, j.cRegCorr), op.c_float(1) ))  
                                                                    )) )

def transl_flav( era, wp, tagger=None, flav=None):
    return partial(BtagSF.translateFixedWPCorrelation, prefix=f"btagSF_fixWP_{tagger.lower()}{wp}_{flav}", year=era)


def getOperatingPoint(wp):
    return ("Loose" if wp == 'L' else ("Medium" if wp == 'M' else "Tight"))

    
from functools import lru_cache
#@lru_cache()
def call_BTagCalibration(flav, noSel, era, wp):
    measurementType= {'heavy': {"B": "lt", "C": "lt"},
                      'light': {"UDSG": "incl"} 
                          }
    getters={'Pt'   : lambda subjet : subjet.pt, 
            'Eta'   : lambda subjet : subjet.eta,
            'Discri': lambda subjet : subjet.btagDeepB,
            'JetFlavour': lambda subjet : op.static_cast("BTagEntry::JetFlavor",
                                op.multiSwitch((subjet.nBHadrons>0,op.c_int(0)),   # b -> flav = 5 -> btv = 0
                                                (subjet.nCHadrons>0,op.c_int(1)),  # c -> flav = 4 -> btv = 1
                                                op.c_int(2))) }                    # light -> flav = 0 -> btv =2 
    return BtagSF('deepcsvSubjet', scalesfactorsULegacyLIB['DeepCSV']["softdrop_subjets"][era], 
                    wp= getOperatingPoint(wp), sysType="central", otherSysTypes= ["up", "down"],
                    measurementType= measurementType[flav], jesTranslate=transl_flav( era, wp, tagger=f'subjetdeepcsv', flav=flav),
                    getters= getters, sel= noSel, uName= f'btagSF_subjetdeepcsv_fixWP_{flav}')


def makeBtagSF(_cleaned_jets, wp, idx, legacy_btagging_wpdiscr_cuts, era, noSel, sample, dobJetER, doCorrect, isSignal, defineOnFirstUse, decorr_eras, full_scheme, full_scheme_mapping, nano="v9"):
    
    wFail = op.extMethod("scalefactorWeightForFailingObject", returnType="double")

    #base_path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_btv_effmaps/"
    base_path  = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/data/BTagEff_maps/"
    
    path_Effmaps = { 
            #'2016-preVFP' : "ul2016__btv_effmaps__ver8/results/summedProcessesForEffmaps/summedProcesses_2016-preVFP_ratios.root",
            #'2016-postVFP': "ul2016__btv_effmaps__ver8/results/summedProcessesForEffmaps/summedProcesses_2016-postVFP_ratios.root",
            #'2017': "ul2017__btv_effmaps__ver5/results/summedProcessesForEffmaps/summedProcesses_2017_ratios.root",
            #'2018': "ul2018__btv_effmaps__ver3/results/summedProcessesForEffmaps/summedProcesses_2018_ratios.root"
            '2016-preVFP' : "BTagEff_maps_UL16preVFP.json.gz", 
            '2016-postVFP': "BTagEff_maps_UL16postVFP.json.gz",
            '2017': "BTagEff_maps_UL17.json.gz", 
            '2018': "BTagEff_maps_UL18.json.gz", 
            }
    
    
    bTagEff_file = os.path.join(base_path, path_Effmaps[era])
    
    
    def get_bTagSF(tagger, flav):
        return get_bTagSF_fixWP(tagger=tagger, wp=wp, flav=flav, era=era.replace('-',''), 
                                sel=noSel, dobJetER=dobJetER, isSignal=isSignal, defineOnFirstUse=defineOnFirstUse, decorr_eras=decorr_eras, 
                                full_scheme=full_scheme, full_scheme_mapping=full_scheme_mapping )
    
    def bTagSF(j, tagger ):
        return op.multiSwitch( (j.hadronFlavour == 5, get_bTagSF(tagger, 5)(j)),
                               (j.hadronFlavour == 4, get_bTagSF(tagger, 4)(j)),
                                                      get_bTagSF(tagger, 0)(j))
    def subjet_bTagSF(subJet, tagger):
        if nano =="v9":
            return bTagSF(subJet, tagger)
        else:
            return op.multiSwitch((subJet.nBHadrons >0, get_bTagSF(tagger, 5)(subJet)), 
                                  (subJet.nCHadrons >0, get_bTagSF(tagger, 4)(subJet)),
                                   get_bTagSF(tagger, 0)(subJet))
    
    def get_bTagEff(j, jtype, reg, tagger, wp, process):
        prefix   = '' if reg =='resolved' and dobJetER and isSignal else 'no'
        params   = {
                'Jet_bRegCorr'  : {"pt": lambda j: j.pt*j.bRegCorr, "eta": lambda j: j.eta}, 
                'noJet_bRegCorr': {"pt": lambda j: j.pt, "eta": lambda j: j.eta} }
        
        correctionSet = { 
                "b": f"pair_lept_2j_jet_pt_vs_eta_bflav_{reg}_{tagger}_wp{wp}_{process}_{jtype}__mc_eff",
                "c": f"pair_lept_2j_jet_pt_vs_eta_cflav_{reg}_{tagger}_wp{wp}_{process}_{jtype}__mc_eff",
            "light": f"pair_lept_2j_jet_pt_vs_eta_lightflav_{reg}_{tagger}_wp{wp}_{process}_{jtype}__mc_eff" }
        
        def call_get_correction(flav):
            return get_correction(bTagEff_file, correctionSet[flav], params=params[f'{prefix}Jet_bRegCorr'],
                                systParam="ValType", systNomName="sf",
                                systVariations={}, #{f"{flav}Effup": "sfup", f"{flav}Effdown": "sfdown"}, 
                                defineOnFirstUse=defineOnFirstUse, sel= noSel )

        if reg == 'boosted' and nano !="v9":
            return op.multiSwitch( (j.nBHadrons > 0 , call_get_correction('b')(j)),
                                   (j.nCHadrons > 0 , call_get_correction('c')(j)),
                                    call_get_correction('light')(j) )
        else:
            return op.multiSwitch( (j.hadronFlavour == 5, call_get_correction('b')(j)),
                                   (j.hadronFlavour == 4, call_get_correction('c')(j)),
                                    call_get_correction('light')(j) )
    

    def Evaluate(j, reg=None , process=None, tagger=None):
        ## if pass btag wp return SF else return (1-SF x eff )/(1 - eff)
        POGTagger = POGTaggerFormat(tagger)
        subjetTagger = 'deepCSV_subjet'
        if reg in ['resolved', 'mix_ak4_rmPuppi']:
            priority = 'boosted' if reg == 'mix_ak4_rmPuppi' else 'resolved'
            jtype    = 'AK4_cleaned' if reg == 'mix_ak4_rmPuppi' else 'AK4'
            return op.switch(j.btagDeepFlavB >= legacy_btagging_wpdiscr_cuts[tagger][era][idx], 
                                bTagSF(j, POGTagger), 
                                wFail( bTagSF(j, POGTagger), get_bTagEff( j, jtype, priority, tagger.lower(), wp, process) ) )
        else:
            jtype = 'AK8'
            if doCorrect == 'fatjet':
                return op.switch(j.btagDeepB >= legacy_btagging_wpdiscr_cuts[tagger][era][idx], 
                                    bTagSF(j, POGTagger), 
                                    wFail( bTagSF(j, POGTagger), get_bTagEff( j, jtype, reg, tagger.lower(), wp, process) ) )
            
            elif doCorrect == 'subjets':
                return op.product( op.switch( op.abs(j.subJet1.eta) < 2.5, 
                                                   op.switch(j.subJet1.btagDeepB >= legacy_btagging_wpdiscr_cuts[tagger][era][idx], 
                                                            subjet_bTagSF(j.subJet1, subjetTagger),
                                                            wFail( subjet_bTagSF(j.subJet1, subjetTagger), get_bTagEff( j.subJet1, jtype, reg, tagger.lower(), wp, process) ) ),
                                              op.c_float(1.) ),

                                   op.switch( op.abs(j.subJet2.eta) < 2.5,
                                                    op.switch(j.subJet2.btagDeepB >= legacy_btagging_wpdiscr_cuts[tagger][era][idx],
                                                            subjet_bTagSF(j.subJet2, subjetTagger),
                                                            wFail( subjet_bTagSF(j.subJet2, subjetTagger), get_bTagEff( j.subJet2, jtype, reg, tagger.lower(), wp, process) ) ),
                                              op.c_float(1.) )
                                )
    
    # reco of the signals processes 
    run2_bTagEventWeight_PerWP = collections.defaultdict(dict)
    for process in ['gg_fusion', 'bb_associatedProduction']:
        
        run2_bTagEventWeight_PerWP[process] = {}
        for reg, jets4tagger in _cleaned_jets.items():
            
            run2_bTagEventWeight_PerWP[process][reg] = {}
            for tagger, jet in jets4tagger.items():
                
                if wp =='T' and tagger == 'DeepCSV' and reg in ['boosted', 'mix_ak4_rmPuppi']:
                    run2_bTagEventWeight_PerWP[process][reg].update({ f'{tagger}{wp}': op.c_float(1.) })
                else:
                    bTag_SF = op.map(jet, lambda j: Evaluate(j, reg, process, tagger))
                    run2_bTagEventWeight_PerWP[process][reg].update({ f'{tagger}{wp}': op.rng_product(bTag_SF) })

    return run2_bTagEventWeight_PerWP
        
        # ///  not in use anymore ///
        #for fl in ['heavy', 'light']:
        #    flav = 5 if fl == 'heavy' else 0
        #    for tagger in ['deepCSV', 'deepJet']:
        #        bTagSF[fl][tagger] = get_bTagSF_fixWP(tagger, 'M', flav, era.replace('-',''), noSel, use_nominal_jet_pt=False, heavy_method="comb",
        #                                            syst_prefix=f"btagSF_{tagger}_fixWP_", decorr_eras=True, full_scheme=False, full_scheme_mapping=None)
        #def getbtagSF_flavor(j, tagger):
        #    return op.multiSwitch((j.hadronFlavour == 5, bTagSF['heavy'][tagger](j)), 
        #                          (j.hadronFlavour == 4, bTagSF['heavy'][tagger](j)), 
        #                            bTagSF['light'][tagger](j))
                                    
        #if os.path.exists(bTagEff_file):
        #    bTagEff_deepflavour = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "resolved", "deepflavour", {%s}, "%s");'%(bTagEff_file, wp, legacy_btagging_wpdiscr_cuts['DeepFlavour'][era][idx], process))
        #    bTagEff_deepcsvAk4  = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "resolved", "deepcsv", {%s}, "%s");'%(bTagEff_file, wp, legacy_btagging_wpdiscr_cuts['DeepCSV'][era][idx], process))
        #    bTagEff_deepcsvAk8  = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "boosted", "deepcsv", {%s}, "%s");'%(bTagEff_file, wp, legacy_btagging_wpdiscr_cuts['DeepCSV'][era][idx], process))
        #else:
        #    raise RuntimeError(f"{bTagEff_file} : efficiencies maps not found !")

        #bTagSF_DeepFlavourPerJet = op.map(cleaned_AK4JetsByDeepFlav, lambda j: bTagEff_deepflavour.evaluate(j.hadronFlavour, j.btagDeepFlavB, j.pt, op.abs(j.eta), getbtagSF_flavor(j, 'deepJet') ) )
        #
        #bTagSF_DeepCSVPerJet     = op.map(cleaned_AK8JetsByDeepB, lambda j: bTagEff_deepcsvAk4.evaluate(j.hadronFlavour, j.btagDeepB, j.pt, op.abs(j.eta), getbtagSF_flavor(j, 'deepCSV') ) )
        #bTagSF_DeepCSVPerSubJet  = op.map(cleaned_AK8JetsByDeepB, lambda j: op.product(bTagEff_deepcsvAk8.evaluate( op.static_cast("BTagEntry::JetFlavor", 
        #                                                                                                            op.multiSwitch((j.nBHadrons >0, op.c_int(5)), 
        #                                                                                                                        (j.nCHadrons >0, op.c_int(4)), 
        #                                                                                                                        op.c_int(0)) ), 
        #                                                                                                            j.subJet1.btagDeepB, j.subJet1.pt, op.abs(j.subJet1.eta), getbtagSF_flavor(j, 'deepCSV') ), 
        #                                                                                bTagEff_deepcsvAk8.evaluate( op.static_cast("BTagEntry::JetFlavor",
        #                                                                                                            op.multiSwitch((j.nBHadrons >0, op.c_int(5)), 
        #                                                                                                                        (j.nCHadrons >0, op.c_int(4)), 
        #                                                                                                                            op.c_int(0)) ), 
        #                                                                                                            j.subJet2.btagDeepB, j.subJet2.pt, op.abs(j.subJet2.eta), getbtagSF_flavor(j, 'deepCSV') )  
        #                                                                                )
        #                                                                            )

        
def Top_reweighting(t, noSel, sampleCfg, isMC, doplots=False):
    # https://indico.cern.ch/event/904971/contributions/3857701/attachments/2036949/3410728/TopPt_20.05.12.pdf
    # TODO for 2016 there's diffrents SFs and in all cases you should produce your own following
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopPtReweighting#Use_case_3_ttbar_MC_is_used_to_m 
    binScaling = 1
    plots = []  
    if isMC and "group" in sampleCfg.keys() and sampleCfg["group"] in ['ttbar', 'tt', 'ttB', 'ttbar_FullLeptonic', 'ttbar_SemiLeptonic', 'ttbar_FullHadronic']:
        
        gen_top     = op.select(t.GenPart, lambda gp : op.AND((gp.statusFlags & (0x1<<13)), gp.pdgId== 6))
        gen_antitop = op.select(t.GenPart, lambda gp : op.AND((gp.statusFlags & (0x1<<13)), gp.pdgId==-6))
        noSel = noSel.refine("hasttbar",cut=[op.rng_len(gen_top)>=1,op.rng_len(gen_antitop)>=1])
        
        gen_top_pt     = op.map(gen_top, lambda top: top.pt)
        gen_antitop_pt = op.map(gen_antitop, lambda antitop: antitop.pt)
        
        forceDefine(gen_top_pt, noSel)
        forceDefine(gen_antitop_pt, noSel)
    
        if doplots:
            plots.append(Plot.make1D("gen_ToppT_noReweighting", gen_top_pt, noSel, EqB(60 // binScaling, 0., 1000.), title="gen Top p_{T} [GeV]"))
    
        #scalefactor = lambda t : op.exp(-2.02274e-01 + 1.09734e-04*t.pt -1.30088e-07*t.pt**2 + (5.83494e+01/(t.pt+1.96252e+02)))
        #scalefactor = lambda t : 0.103*op.exp(-0.0118*t.pt)-0.000134*t.pt+0.973
        scalefactor  = lambda t : op.exp(0.0615-0.0005*t.pt)
        top_weight   = lambda top, antitop : op.sqrt(scalefactor(top)*scalefactor(antitop))
        
        getTopPtWeight      = top_weight(gen_top[0], gen_antitop[0])
        Sel_with_top_reWgt  = noSel.refine("TopPt_reweighting", weight=op.systematic(op.c_float(1.), name="TopPt_reweighting", up=getTopPtWeight, down=op.c_float(1.)))

        forceDefine(gen_top_pt, Sel_with_top_reWgt)
        forceDefine(gen_antitop_pt, Sel_with_top_reWgt)
        
        if doplots:
            plots.append(Plot.make1D("gen_ToppT_withReweighting", gen_top_pt, 
                Sel_with_top_reWgt, EqB(60 // binScaling, 0., 1000.), 
                title="rewighted gen Top p_{T} [GeV]")) 
        return Sel_with_top_reWgt, plots
    else: 
        # those are default, otherwise plotit will complain , and you get no plots 
        if doplots:
            plots.append(Plot.make1D("gen_ToppT_noReweighting", op.c_int(0), 
                noSel, EqB(60 // binScaling, 0., 1000.), 
                title="gen Top p_{T} [GeV]"))
            plots.append(Plot.make1D("gen_ToppT_withReweighting", op.c_int(0), 
                noSel, EqB(60 // binScaling, 0., 1000.), 
                title="rewighted gen Top p_{T} [GeV]")) 
        return noSel, plots


def DrellYanreweighting(noSel, j, tagger, era, doSysts):
    
    def get_DYweight(era, k, var):
        era_ = '2016' if 'VFP' in era else era
        DYWeights = { ">=2b-medium & >=4j": {'2016': [0.868, 0.141], '2017': [1.453, 0.081], '2018':[1.329, 0.140]},
                      ">=2b-medium & ==3j": {'2016': [0.779, 0.066], '2017': [1.054, 0.036], '2018':[1.012, 0.046]},
                      ">=2b-medium & ==2j": {'2016': [0.754, 0.080], '2017': [0.884, 0.033], '2018':[0.822, 0.021]},
                      "==1b-medium & >=2b-loose & >=4j": {'2016': [1.062, 0.058], '2017': [1.361, 0.035], '2018':[1.444, 0.043]},
                      "==1b-medium & >=2b-loose & ==3j": {'2016': [0.864, 0.104], '2017': [1.091, 0.066], '2018':[1.049, 0.023]},
                      "==1b-medium & >=2b-loose & ==2j": {'2016': [0.785, 0.028], '2017': [0.904, 0.013], '2018':[0.886, 0.009]},
                      "==1b-medium & ==1b-loose & >=4j": {'2016': [1.098, 0.049], '2017': [1.432, 0.032], '2018':[1.493, 0.046]},
                      "==1b-medium & ==1b-loose & ==3j": {'2016': [0.960, 0.032], '2017': [1.145, 0.030], '2018':[1.110, 0.025]},
                      "==1b-medium & ==1b-loose & ==2j": {'2016': [0.894, 0.011], '2017': [0.979, 0.006], '2018':[0.941, 0.006]},
                      "==0b-medium & >=2b-loose & >=4j": {'2016': [1.031, 0.021], '2017': [1.296, 0.034], '2018':[1.424, 0.025]},
                      "==0b-medium & >=2b-loose & ==3j": {'2016': [0.853, 0.056], '2017': [1.053, 0.023], '2018':[1.082, 0.025]},
                      "==0b-medium & >=2b-loose & ==2j": {'2016': [0.800, 0.007], '2017': [0.950, 0.020], '2018':[0.927, 0.018]},
                    }

        if var == 'nom': 
            return op.c_float(DYWeights[k][era_][0])
        elif var == 'up':
            up = DYWeights[k][era_][0]+DYWeights[k][era_][1]
            return op.c_float(up)
        else:
            down = DYWeights[k][era_][0]-DYWeights[k][era_][1]
            return op.c_float(down)

    def rng_len(jet, wp):

        lambda_f = {'DeepFlavour': lambda j: j.btagDeepFlavB >= legacy_btagging_wpdiscr_cuts['DeepFlavour'][era][getIDX(wp)],
                    'DeepCSV'    : lambda j: op.OR(j.subJet1.btagDeepB >= legacy_btagging_wpdiscr_cuts['DeepCSV'][era][getIDX(wp)],
                                                   j.subJet2.btagDeepB >= legacy_btagging_wpdiscr_cuts['DeepCSV'][era][getIDX(wp)])
                    }
        
        cleaned_jets = op.select(jet, lambda_f[tagger] ) 
        return op.rng_len(cleaned_jets)

    def switchjetlen(j, var):
        default = 1. if var=='nom' else 0.
        return op.multiSwitch( (op.AND( rng_len(j, 'medium') >= 2 , op.rng_len(j) >=4), get_DYweight(era, ">=2b-medium & >=4j", var)), 
                               (op.AND( rng_len(j, 'medium') >= 2 , op.rng_len(j) ==3), get_DYweight(era, ">=2b-medium & ==3j", var)),
                               (op.AND( rng_len(j, 'medium') >= 2 , op.rng_len(j) ==2), get_DYweight(era, ">=2b-medium & ==2j", var)),
                               (op.AND( rng_len(j, 'medium') == 1 , rng_len(j, 'loose') >= 2, op.rng_len(j) >=4), get_DYweight(era, "==1b-medium & >=2b-loose & >=4j", var)), 
                               (op.AND( rng_len(j, 'medium') == 1 , rng_len(j, 'loose') >= 2, op.rng_len(j) ==3), get_DYweight(era, "==1b-medium & >=2b-loose & ==3j", var)),
                               (op.AND( rng_len(j, 'medium') == 1 , rng_len(j, 'loose') >= 2, op.rng_len(j) ==2), get_DYweight(era, "==1b-medium & >=2b-loose & ==2j", var)),
                               (op.AND( rng_len(j, 'medium') == 1 , rng_len(j, 'loose') == 1, op.rng_len(j) >=4), get_DYweight(era, "==1b-medium & ==1b-loose & >=4j", var)),
                               (op.AND( rng_len(j, 'medium') == 1 , rng_len(j, 'loose') == 1, op.rng_len(j) ==3), get_DYweight(era, "==1b-medium & ==1b-loose & ==3j", var)),
                               (op.AND( rng_len(j, 'medium') == 1 , rng_len(j, 'loose') == 1, op.rng_len(j) ==2), get_DYweight(era, "==1b-medium & ==1b-loose & ==2j", var)),
                               (op.AND( rng_len(j, 'medium') == 0 , rng_len(j, 'loose') >= 2, op.rng_len(j) >=4), get_DYweight(era, "==0b-medium & >=2b-loose & >=4j", var)),
                               (op.AND( rng_len(j, 'medium') == 0 , rng_len(j, 'loose') >= 2, op.rng_len(j) ==3), get_DYweight(era, "==0b-medium & >=2b-loose & ==3j", var)),
                               (op.AND( rng_len(j, 'medium') == 0 , rng_len(j, 'loose') >= 2, op.rng_len(j) ==2), get_DYweight(era, "==0b-medium & >=2b-loose & ==2j", var)),
                               op.c_float(default) )
    
    if doSysts:
        DYWeight = op.systematic(switchjetlen(j, var='nom'), name="DYReWeight", up=switchjetlen(j, var='up'), down=switchjetlen(j, var='down'))
    else:
        DYWeight = switchjetlen(j, var='nom')
    return noSel.refine( 'DY_reweighting', weight=(DYWeight))



Old_puIDSFLib = {
        f"{year}_{wp}" : {
            f"{eom}_{mcsf}" : os.path.join('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/data/PileupFullRunII/',
                "fromPieter", f"PUID_80X_{eom}_{mcsf}_{year}_{wp}.json")
            for eom in ("eff", "mistag") for mcsf in ("mc", "sf") }
        for year in ("2016", "2017", "2018") for wp in "LMT"
    }
puIDSFLib = {
        f"{year}_{wp}" : {
            f"{eos}_{eom}_{mcsf}" : os.path.join('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/data/PileupFullRunII/',
                "fromflorian", f"PUID_{eos}_h2_{eom}_{mcsf}{year}_{wp}.json")
            for eom in ("eff", "mistag") for mcsf in ("mc", "sf") for eos in ("EFF", "SF")}
        for year in ("2016", "2017", "2018") for wp in "LMT"
    }

def makePUIDSF(jets, year=None, wp=None, wpToCut=None):
    sfwpyr = puIDSFLib[f"{year}_{wp}"]
    sf_eff = scalefactors.get_scalefactor("lepton", "SF_eff_sf"   , sfLib=sfwpyr, paramDefs=scalefactors.binningVariables_nano)
    sf_mis = scalefactors.get_scalefactor("lepton", "SF_mistag_sf", sfLib=sfwpyr, paramDefs=scalefactors.binningVariables_nano)
    eff_mc = scalefactors.get_scalefactor("lepton", "EFF_eff_mc"   , sfLib=sfwpyr, paramDefs=scalefactors.binningVariables_nano)
    mis_mc = scalefactors.get_scalefactor("lepton", "EFF_mistag_mc", sfLib=sfwpyr, paramDefs=scalefactors.binningVariables_nano)
    jets_m50 = op.select(jets, lambda j : j.pt < 50.)
    wFail = op.extMethod("scalefactorWeightForFailingObject", returnType="double")
    return op.rng_product(jets_m50, lambda j : op.switch(j.genJet.isValid,
        op.switch(wpToCut(j), sf_eff(j), wFail(sf_eff(j), eff_mc(j))),
        op.switch(wpToCut(j), sf_mis(j), wFail(sf_mis(j), mis_mc(j)))
        ))


def BtagSFMethod_deprectaed( channel, sample, wp, OP, isULegacy, noSel):
    
    #sysToLoad = ["up_correlated", "down_correlated", "up_uncorrelated", "down_uncorrelated"]
    sysToLoad = ["up", "down"]
    
    btagSF_light = collections.defaultdict(dict)
    btagSF_heavy = collections.defaultdict(dict)
    
    if isULegacy:
        csv_deepcsvAk4     = scalesfactorsULegacyLIB['DeepCSV']['Ak4'][era]
        csv_deepcsvSubjets = scalesfactorsULegacyLIB['DeepCSV']['softdrop_subjets'][era]
        csv_deepflavour    = scalesfactorsULegacyLIB['DeepFlavour'][era]
    else:
        csv_deepcsvAk4     = scalesfactorsLIB['DeepCSV']['Ak4'][era]
        csv_deepcsvSubjets = scalesfactorsLIB['DeepCSV']['softdrop_subjets'][era]
        csv_deepflavour    = scalesfactorsLIB['DeepFlavour'][era]
    
    if os.path.exists(csv_deepcsvAk4): 
        btagSF_light['DeepCSV']     = BtagSF('DeepCSV', csv_deepcsvAk4, wp= OP, sysType= "central", otherSysTypes= sysToLoad,
                                            measurementType=  {"UDSG": "incl"}, jesTranslate=transl_flav( era, wp, tagger='DeepCSV', flav='light'),
                                            getters={"Pt": lambda j : j.pt}, sel= noSel, uName= f'sf_eff_{channel}_{sample}_deepcsv{wp}_lightflav')
        btagSF_heavy['DeepCSV']     = BtagSF('DeepCSV', csv_deepcsvAk4, wp=OP, sysType= "central", otherSysTypes= sysToLoad,
                                            measurementType= {"B": "comb", "C": "comb"}, jesTranslate=transl_flav( era, wp, tagger='DeepCSV', flav='heavy'),
                                            getters={"Pt": lambda j : j.pt}, sel= noSel, uName= f'sf_eff_{channel}_{sample}_deepcsv{wp}_heavyflav')
    if os.path.exists(csv_deepflavour):
        btagSF_light['DeepFlavour']  = BtagSF('DeepFalvour', csv_deepflavour, wp= OP, sysType= "central", otherSysTypes= sysToLoad,
                                            measurementType= {"UDSG": "incl"}, jesTranslate=transl_flav( era, wp, tagger='DeepFlavour', flav='light'),
                                            getters={"Pt": lambda j : j.pt}, sel= noSel, uName= f'sf_eff_{channel}_{sample}_deepflavour{wp}_lightflav')
        btagSF_heavy['DeepFlavour']  = BtagSF('DeepFalvour', csv_deepflavour, wp= OP, sysType= "central", otherSysTypes= sysToLoad,
                                            measurementType= {"B": "comb", "C": "comb"}, jesTranslate=transl_flav( era, wp, tagger='DeepFlavour', flav='heavy'),
                                            getters={"Pt": lambda j : j.pt}, sel= noSel, uName= f'sf_eff_{channel}_{sample}_deepflavour{wp}_heavyflav')
    
    if os.path.exists(csv_deepcsvSubjets):
        if 'Tight' not in OP : 
            btagSF_light['subjets'] = BtagSF('DeepCSV', csv_deepcsvSubjets, wp= OP, sysType="central", otherSysTypes= sysToLoad,
                                            measurementType= {"UDSG": "incl"}, jesTranslate=transl_flav( era, wp, tagger='subjetdeepcsv', flav='light'),
                                            getters={"Pt": lambda j : j.pt}, sel= noSel, uName= f'sf_eff_{channel}_{sample}_subjets_deepcsv{wp}_lightflav')
            btagSF_heavy['subjets'] = BtagSF('DeepCSV', csv_deepcsvSubjets, wp= OP, sysType="central", otherSysTypes= sysToLoad,
                                            measurementType= {"B": "lt", "C": "lt"}, jesTranslate=transl_flav( era, wp, tagger='subjetdeepcsv', flav='heavy'),
                                            getters={"Pt": lambda j : j.pt}, sel= noSel, uName= f'sf_eff_{channel}_{sample}_subjets_deepcsv{wp}_heavyflav')
    
    return btagSF_light, btagSF_heavy
