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

import utils
from bambooToOls import Plot
from scalefactorslib import all_scalefactors, all_run2_Ulegacyscalefactors

#https://cms-nanoaod-integration.web.cern.ch/commonJSONSFs/
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
        

scalesfactorsLIB = {
     "DeepFlavour": {
          year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
           {"2016": "2016/Btag/DeepJet_2016LegacySF_V1.csv", 
            "2017": "2017/Btag/DeepFlavour_94XSF_V4_B_F.csv", 
            "2018": "2018/Btag/DeepJet_102XSF_V1.csv"}.items() },
     "DeepCSV" : {
        "Ak4": {
            year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
               {"2016":"2016/Btag/DeepCSV_2016LegacySF_V1.csv" , 
                "2017": "2017/Btag/DeepCSV_94XSF_V5_B_F.csv" , 
                "2018": "2018/Btag/DeepCSV_102XSF_V1.csv"}.items() },
        "softdrop_subjets": {
            year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
               {"2016":"2016/Btag/subjet_DeepCSV_2016LegacySF_V1.csv" , 
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
               {"2016-preVFP" :"2016UL/subjet_deepCSV_106XUL16preVFP_v1.csv",
                "2016-postVFP":"2016UL/subjet_deepCSV_106XUL16postVFP_v1.csv",
                "2017": "2017UL/Btag/subjet_DeepCSV_106X_UL17_SF.csv" , 
                "2018": "2018UL/Btag/subjet_deepCSV_106XUL18_v1.csv"}.items() }, }
    }
    
# maps name of systematic to name of correction inside of jsons
leptonSFLib = {
    "electron_ID"     : "UL-Electron-ID-SF",
    "electron_reco"   : "UL-Electron-ID-SF",
    "muon_ID"     : "NUM_MediumID_DEN_TrackerMuons",
    "muon_iso"    : "NUM_TightRelIso_DEN_TightIDandIPCut",
    "muon_trigger": {
        "2016-preVFP" : "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight",
        "2016-postVFP": "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight",
        "2017": "NUM_IsoMu27_DEN_CutBasedIdTight_and_PFIsoTight",
        "2018": "NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight",
    },
    "TkMu50_muon_trigger":{
        "2016-preVFP" : "NUM_Mu50_or_TkMu50_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose",
        "2016-postVFP": "NUM_Mu50_or_TkMu50_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose",
        "2017": "NUM_Mu50_or_OldMu100_or_TkMu100_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose",
        "2018": "NUM_Mu50_or_OldMu100_or_TkMu100_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose",
    },
}

def pogEraFormat(era):
    return era.replace("-", "") + "_UL"


def getYearFromEra(era):
    if '2016' in era: return '16'
    elif '2017' in era: return '17'
    elif '2018' in era: return '18'


def localizePOGSF(era, POG, fileName):
    return os.path.join("/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration", "POG", POG, pogEraFormat(era), fileName)


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


def get_bTagSF_fixWP(tagger, wp, flav, era, sel, dobJetER, isSignal, defineOnFirstUse=False, use_nominal_jet_pt=False, heavy_method="comb",
                     syst_prefix="", decorr_eras=True, full_scheme=False, full_scheme_mapping=None):
    params = { 
            "noJet_bRegCorr" : { "pt": lambda j: op.forSystematicVariation(j.pt, "nominal") if use_nominal_jet_pt else j.pt,
                               "abseta": lambda j: op.abs(j.eta), "working_point": wp, "flavor": flav },
            "Jet_bRegCorr" : { "pt": lambda j: op.forSystematicVariation(j.pt*j.bRegCorr, "nominal") if use_nominal_jet_pt else j.pt*j.bRegCorr,
                               "abseta": lambda j: op.abs(j.eta), "working_point": wp, "flavor": flav }
            }

    syst_prefix=f"btagSF_{tagger}_fixWP_"
    systName = syst_prefix + ("light" if flav == 0 else "heavy")
    systVariations = {}
    
    for d in ("up", "down"):
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

    method = "incl" if flav == 0 else heavy_method
    prefix = "" if tagger =='deepJet'and flav ==5 and dobJetER and isSignal else "no"

    return get_correction(localizePOGSF(era, "BTV", "btagging.json.gz"), f"{tagger}_{method}", params=params[f"{prefix}Jet_bRegCorr"],
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


def makeBtagSF(cleaned_AK4JetsByDeepB, cleaned_AK4JetsByDeepFlav, cleaned_AK8JetsByDeepB, wp, idx, legacy_btagging_wpdiscr_cuts, era, noSel, dobJetER, isSignal):
    
    wFail = op.extMethod("scalefactorWeightForFailingObject", returnType="double")

    base_path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/data/BTagEff_maps/"
    path_Effmaps = { 
            #base_path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_btv_effmaps/"
            #'2016-preVFP' : "ul2016__btv_effmaps__ver8/results/summedProcessesForEffmaps/summedProcesses_2016-preVFP_ratios.root",
            #'2016-postVFP': "ul2016__btv_effmaps__ver8/results/summedProcessesForEffmaps/summedProcesses_2016-postVFP_ratios.root",
            #'2017': "ul2017__btv_effmaps__ver5/results/summedProcessesForEffmaps/summedProcesses_2017_ratios.root",
            #'2018': "ul2018__btv_effmaps__ver3/results/summedProcessesForEffmaps/summedProcesses_2018_ratios.root"
            '2016-preVFP' : "BTagEff_maps_UL16preVFP.json.gz", 
            '2016-postVFP': "BTagEff_maps_UL16postVFP.json.gz",
            '2017': "BTagEff_maps_UL17.json.gz", 
            '2018': "BTagEff_maps_UL18.json.gz", 
            }
    
    run2_bTagEventWeight_PerWP = collections.defaultdict(dict)
    
    bTagEff_file = os.path.join(base_path, path_Effmaps[era])
    
    jets = {'resolved': cleaned_AK4JetsByDeepFlav,
            'boosted' : cleaned_AK8JetsByDeepB, }
    
    def get_bTagSF(tagger, flav):
        return get_bTagSF_fixWP(tagger, wp, flav, era.replace('-',''), noSel, dobJetER, isSignal, syst_prefix=f"btagSF_{tagger}_fixWP_", defineOnFirstUse=False)
        
    bTagSF = { tagger: lambda j: op.multiSwitch( (j.hadronFlavour == 5, get_bTagSF(tagger, 5)(j)),
                                                 (j.hadronFlavour == 4, get_bTagSF(tagger, 4)(j)),
                                                  get_bTagSF(tagger, 0)(j))
                    for tagger in ['deepCSV', 'deepJet']}
    
    
    def get_bTagEff(j, reg, tagger, wp, process):
        systName = f"btagEff_{tagger}_fixWP_"
        prefix = '' if reg =='resolved' and dobJetER and isSignal else 'no'
        
        params = {
                'Jet_bRegCorr'  : {"pt": lambda j: j.pt*j.bRegCorr, "eta": lambda j: j.eta}, #"jetFlavor": lambda j: j.hadronFlavour, "workingPoint": wp
                'noJet_bRegCorr': {"pt": lambda j: j.pt, "eta": lambda j: j.eta}, #"jetFlavor": lambda j: j.hadronFlavour, "workingPoint": wp
                }

        correctionSet = { "b": f"pair_lept_2j_jet_pt_vs_eta_bflav_{reg}_{tagger}_wp{wp}_{process}__mc_eff",
                          "c": f"pair_lept_2j_jet_pt_vs_eta_cflav_{reg}_{tagger}_wp{wp}_{process}__mc_eff",
                          "light": f"pair_lept_2j_jet_pt_vs_eta_lightflav_{reg}_{tagger}_wp{wp}_{process}__mc_eff" }
        
        return op.multiSwitch( (j.hadronFlavour == 5, get_correction(bTagEff_file, correctionSet['b'], params=params[f'{prefix}Jet_bRegCorr'], 
                                                        systParam="ValType", systNomName="sf", 
                                                        systVariations={"beffup": "sfup", "beffdown": "sfdown"}, sel= noSel )(j)),
                               (j.hadronFlavour == 4, get_correction(bTagEff_file, correctionSet['c'], params=params['noJet_bRegCorr'], 
                                                        systParam="ValType", systNomName="sf",
                                                        systVariations={"ceffup": "sfup", "ceffdown": "sfdown"}, sel= noSel)(j)),
                                get_correction(bTagEff_file, correctionSet['light'], params=params['noJet_bRegCorr'], 
                                                        systParam="ValType", systNomName="sf",
                                                        systVariations={"lighteffup": "sfup", "lighteffdown": "sfdown"}, sel= noSel)(j))
    
    def softdrop_SF(flav):
        print( scalesfactorsULegacyLIB['DeepCSV']["softdrop_subjets"][era] ) 
        measurementType= {'heavy':{"B": "lt", "C": "lt"},
                          'light': {"UDSG": "incl"} }
        getters={'Pt': lambda subjet: subjet.pt, 'Eta':  lambda subjet : subjet.eta,'JetFlavour': lambda subjet : op.static_cast("BTagEntry::JetFlavor",
                                    op.multiSwitch((subjet.nBHadrons>0,op.c_int(0)), # b -> flav = 5 -> btv = 0
                                                   (subjet.nCHadrons>0,op.c_int(1)), # c -> flav = 4 -> btv = 1
                                                    op.c_int(2)))},                  # light -> flav = 0 -> btv =2 
        return BtagSF('DeepCSV', scalesfactorsULegacyLIB['DeepCSV']["softdrop_subjets"][era], 
                        wp= getOperatingPoint(wp), sysType="central", otherSysTypes= ["up", "down"],
                        measurementType= measurementType[flav], jesTranslate=transl_flav( era, wp, tagger='subjetdeepcsv', flav=flav),
                        getters= getters, sel= noSel, uName= f'btagSF_subjetdeepcsv_fixWP_{flav}')
                                
    
    def subjetbTag_SF(subjet):
        return op.multiSwitch( (subjet.nBHadrons >0, softdrop_SF('heavy')(subjet)),
                               (subjet.nCHadrons >0, softdrop_SF('heavy')(subjet)),
                                softdrop_SF('light')(subjet))


    def Evaluate(j, reg , process):
        ## if pass btag wp return SF else return (1-SF x eff )/(1 - eff)
        if reg =='resolved':
            return op.switch(j.btagDeepFlavB >= legacy_btagging_wpdiscr_cuts['DeepFlavour'][era][idx], 
                                bTagSF['deepJet'](j), 
                                wFail( bTagSF['deepJet'](j), get_bTagEff( j, reg, 'deepflavour', wp, process) )
                                )
        else:   
            return op.switch( op.OR(j.subJet1.btagDeepB >= legacy_btagging_wpdiscr_cuts['DeepCSV'][era][idx], 
                                    j.subJet2.btagDeepB >= legacy_btagging_wpdiscr_cuts['DeepCSV'][era][idx]), 
                                op.product(subjetbTag_SF(j.subJet1), subjetbTag_SF(j.subJet2)),
                                wFail( op.product(subjetbTag_SF(j.subJet1), subjetbTag_SF(j.subJet2)), get_bTagEff( j, reg, 'deepcsv', wp, process) )
                                )

    for process in ['gg_fusion', 'bb_associatedProduction']:
        for reg, tagger in {'resolved': 'deepJet', 'boosted': 'deepCSV'}.items():
            
            bTag_SF = op.map(jets[reg], lambda j: Evaluate(j, reg , process))
            run2_bTagEventWeight_PerWP[process][reg] = { f'{tagger}{wp}'.replace('deepJet', 'DeepFlavour').replace('deepCSV', 'DeepCSV'): 
                                                         op.rng_product(bTag_SF) }
    
    return run2_bTagEventWeight_PerWP



        #method   = "incl" if flav == 0 else "comb"
        #systName = f"btagSF_{tagger}_fixWP_" + ("light" if flav == 0 else "heavy")
        #params   = { "pt": lambda j: j.pt, "abseta": lambda j: op.abs(j.eta), "working_point": wp, "flavor": flav }
        #sf = get_correction(localizePOGSF(era.replace('-',''), "BTV", "btagging.json.gz"), f"{tagger}_{method}", params=params,
        #                        systParam="systematic", systNomName="central",
        #                        systVariations={f"{systName}up": "up", f"{systName}down": "down"},
        #                        defineOnFirstUse=True, sel=noSel)

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
    



def Top_reweighting(t, noSel, sampleCfg, isMC):
    # https://indico.cern.ch/event/904971/contributions/3857701/attachments/2036949/3410728/TopPt_20.05.12.pdf
    # TODO for 2016 there's diffrents SFs and in all cases you should produce your own following
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopPtReweighting#Use_case_3_ttbar_MC_is_used_to_m 
    binScaling = 1
    plots = []  
    # no ST
    if isMC and "group" in sampleCfg.keys() and sampleCfg["group"] in ['ttbar_FullLeptonic', 'ttbar_SemiLeptonic', 'ttbar_FullHadronic']:
        
        gen_top     = op.select(t.GenPart, lambda gp : op.AND((gp.statusFlags & (0x1<<13)), gp.pdgId== 6))
        gen_antitop = op.select(t.GenPart, lambda gp : op.AND((gp.statusFlags & (0x1<<13)), gp.pdgId==-6))
        noSel = noSel.refine("hasttbar",cut=[op.rng_len(gen_top)>=1,op.rng_len(gen_antitop)>=1])
        
        gen_top_pt     = op.map(gen_top, lambda top: top.pt)
        gen_antitop_pt = op.map(gen_antitop, lambda antitop: antitop.pt)
        
        forceDefine(gen_top_pt, noSel)
        forceDefine(gen_antitop_pt, noSel)
    
        plots.append(Plot.make1D("gen_ToppT_noReweighting", gen_top_pt, noSel, EqB(60 // binScaling, 0., 1000.), title="gen Top p_{T} [GeV]"))
    
       #scalefactor = lambda t : op.exp(-2.02274e-01 + 1.09734e-04*t.pt -1.30088e-07*t.pt**2 + (5.83494e+01/(t.pt+1.96252e+02)))
       #scalefactor = lambda t : 0.103*op.exp(-0.0118*t.pt)-0.000134*t.pt+0.973
        scalefactor = lambda t : op.exp(0.0615-0.0005*t.pt)
        top_weight  = lambda top, antitop : op.sqrt(scalefactor(top)*scalefactor(antitop))
        
        Sel_with_top_reWgt = noSel.refine("top_reweighting", weight=top_weight(gen_top[0], gen_antitop[0]))
        
        forceDefine(gen_top_pt, Sel_with_top_reWgt)
        forceDefine(gen_antitop_pt, Sel_with_top_reWgt)
        
        plots.append(Plot.make1D("gen_ToppT_withReweighting", gen_top_pt, Sel_with_top_reWgt, EqB(60 // binScaling, 0., 1000.), title="rewighted gen Top p_{T} [GeV]")) 
    else: # those are default, otherwise plotit will complain , and you get no plots 
        plots.append(Plot.make1D("gen_ToppT_noReweighting", op.c_int(0), noSel, EqB(60 // binScaling, 0., 1000.), title="gen Top p_{T} [GeV]"))
        plots.append(Plot.make1D("gen_ToppT_withReweighting", op.c_int(0), noSel, EqB(60 // binScaling, 0., 1000.), title="rewighted gen Top p_{T} [GeV]")) 
        Sel_with_top_reWgt = noSel

    return Sel_with_top_reWgt, plots


def DY_reweighting(t, noSel, sample):
    # it will crash if evaluated when there are no two leptons in the matrix element
    plots = []
    if sample in ["DYJetsToLL_0J", "DYJetsToLL_1J", "DYJetsToLL_2J"]:
        genLeptons_hard = op.select(t.GenPart, lambda gp : op.AND((gp.statusFlags & (0x1<<7)), op.in_range(10, op.abs(gp.pdgId), 17)))
        gen_ptll_nlo    = (genLeptons_hard[0].p4+genLeptons_hard[1].p4).Pt()
        
        forceDefine(gen_ptll_nlo, noSel)
        
        plots.append(Plots_gen(gen_ptll_nlo, noSel, "noSel"))
        plots.append(Plot.make1D("nGenLeptons_hard", op.rng_len(genLeptons_hard), noSel, EqB(5, 0., 5.),  title="nbr genLeptons_hard [GeV]")) 
    return plots



puIDSFLib = {
        f"{year}_{wp}" : {
            f"{eom}_{mcsf}" : os.path.join('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_',
                "fromPieter", f"PUID_80X_{eom}_{mcsf}_{year}_{wp}.json")
            for eom in ("eff", "mistag") for mcsf in ("mc", "sf") }
        for year in ("2016", "2017", "2018") for wp in "LMT"
    }

def makePUIDSF(jets, year=None, wp=None, wpToCut=None):
    sfwpyr = puIDSFLib[f"{year}_{wp}"]
    sf_eff = scalefactors.get_scalefactor("lepton", "eff_sf"   , sfLib=sfwpyr, paramDefs=scalefactors.binningVariables_nano)
    sf_mis = scalefactors.get_scalefactor("lepton", "mistag_sf", sfLib=sfwpyr, paramDefs=scalefactors.binningVariables_nano)
    eff_mc = scalefactors.get_scalefactor("lepton", "eff_mc"   , sfLib=sfwpyr, paramDefs=scalefactors.binningVariables_nano)
    mis_mc = scalefactors.get_scalefactor("lepton", "mistag_mc", sfLib=sfwpyr, paramDefs=scalefactors.binningVariables_nano)
    jets_m50 = op.select(jets, lambda j : j.pt < 50.)
    wFail = op.extMethod("scalefactorWeightForFailingObject", returnType="double")
    return op.rng_product(jets_m50, lambda j : op.switch(j.genJet.isValid,
        op.switch(wpToCut[wp](j), sf_eff(j), wFail(sf_eff(j), eff_mc(j))),
        op.switch(wpToCut[wp](j), sf_mis(j), wFail(sf_mis(j), mis_mc(j)))
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
