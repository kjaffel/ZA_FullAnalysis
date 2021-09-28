import os, os.path, sys
import collections
import builtins
import math
import argparse
import json
import yaml 
import shutil
from itertools import chain
from functools import partial

import bamboo.scalefactors
from bamboo.analysismodules import NanoAODModule, NanoAODHistoModule, HistogramsModule
from bamboo.analysisutils import makeMultiPrimaryDatasetTriggerSelection
from bamboo import treefunctions as op
from bamboo.root import addIncludePath, loadHeader
from bamboo.scalefactors import BtagSF#, get_correction

import logging
LOG_LEVEL = logging.DEBUG
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
logger = logging.getLogger("run2 Ulegacy H/A ->Z A/H ->llbb Analysis")
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream)

try:
    import colorlog
    from colorlog import ColoredFormatter
    formatter = ColoredFormatter(
                    "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
                    datefmt=None,
                    reset=True,
                    log_colors={
                            'DEBUG':    'cyan',
                            'INFO':     'green',
                            'WARNING':  'blue',
                            'ERROR':    'red',
                            'CRITICAL': 'red',
                        },
                    secondary_log_colors={},
                    style='%'
                    )
    stream.setFormatter(formatter)
except ImportError:
    print(" You can add colours to the output of Python logging module via : https://pypi.org/project/colorlog/")
    pass


zabPath = os.path.dirname(__file__)
if zabPath not in sys.path:
    sys.path.append(zabPath)

import utils
from utils import safeget
from systematics import getTriggerSystematcis, get_tthDYreweighting
from ZAEllipses import MakeEllipsesPLots, MakeMETPlots, MakeExtraMETPlots, MakePuppiMETPlots, MHMAforCombinedLimits
from EXtraPLots import MakeTriggerDecisionPlots, MakeBestBJetsPairPlots, MakeHadronFlavourPLots, zoomplots, ptcuteffectOnJetsmultiplicty, choosebest_jetid_puid, varsCutsPlotsforLeptons, LeptonsInsideJets, makePUIDSF, makerhoPlots
from ControlPLots import *
from boOstedEvents import addBoOstedTagger, getBoOstedWeight
from scalefactorslib import all_scalefactors, all_run2_Ulegacyscalefactors

try:
    profile = builtins.profile
except AttributeError:
    profile = lambda x: x

def get_legacyscalefactor(objType, key, periods=None, combine=None, additionalVariables=dict(), getFlavour=None, isElectron=False, systName=None):
    return bamboo.scalefactors.get_scalefactor(objType, key, periods=periods, combine=combine,
                                        additionalVariables=additionalVariables,
                                        sfLib=all_run2_Ulegacyscalefactors,
                                        paramDefs=bamboo.scalefactors.binningVariables_nano,
                                        getFlavour=getFlavour,
                                        isElectron=isElectron,
                                        systName=systName)

def get_scalefactor(objType, key, periods=None, combine=None, additionalVariables=dict(), getFlavour=None, isElectron=False, systName=None):
    return bamboo.scalefactors.get_scalefactor(objType, key, periods=periods, combine=combine,
                                        additionalVariables=additionalVariables,
                                        sfLib=all_scalefactors,
                                        paramDefs=bamboo.scalefactors.binningVariables_nano,
                                        getFlavour=getFlavour,
                                        isElectron=isElectron,
                                        systName=systName)
def getL1PreFiringWeight(tree):
    return op.systematic(tree.L1PreFiringWeight_Nom, 
                            name="L1PreFiring", 
                            up=tree.L1PreFiringWeight_Up, 
                            down=tree.L1PreFiringWeight_Dn)

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
            "SingleMuon"     : [ hlt.IsoMu24, 
                                 #hlt.IsoMu27, #not in the list of the recomended triggers for 2018 : https://twiki.cern.ch/twiki/bin/view/CMS/MuonHLT2018#Recommended_trigger_paths_for_20
                                 hlt.Mu50, hlt.OldMu100, hlt.TkMu100 ], # OldMu100 and TkMu100 are recommend to recover inefficiencies at high pt but it seems to me for 2016 Only
                                                                         #(https://indico.cern.ch/event/766895/contributions/3184188/attachments/1739394/2814214/IdTrigEff_HighPtMu_Min_20181023_v2.pdf)
            "DoubleMuon"     : [ #hlt.Mu37_TkMu27,
                                 hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,
                                 hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                                 hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8, #  Only DZ_MassX versions unprescaled!! 
                                 hlt.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8 ],
            
            "EGamma"         : [ hlt.Ele30_eta2p1_WPTight_Gsf_CentralPFJet35_EleCleaned, # Lowest unprescaled seed L1_LooseIsoEG30er2p1_Jet34er2p5_dR_Min0p3 (from run 317170 L1_LooseIsoEG28er2p1_Jet34er2p5_dR_Min0p3)
                                 hlt.DiEle27_WPTightCaloOnly_L1DoubleEG,
                                 hlt.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL, hlt.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, #Both DZ and non DZ versions unprescaled 
                                 hlt.Ele32_WPTight_Gsf, #hlt.Ele35_WPTight_Gsf, hlt.Ele38_WPTight_Gsf,
                                 #hlt.Ele28_WPTight_Gsf
                                 #hlt_Ele30_WPTight_Gsf, # [321397,322381], corresponding to runs in Run2018D
                                 hlt.DoubleEle25_CaloIdL_MW, # NON ISOLATED 
                                 # hlt.Ele28_eta2p1_WPTight_Gsf_HT150,    I am not sure I need this :Electron + HT
                                 hlt.Ele50_CaloIdVT_GsfTrkIdT_PFJet165,
                                 hlt.Ele115_CaloIdVT_GsfTrkIdT, 
                                 hlt.Photon200]+ notForEra('Ele28_WPTight_Gsf','AB') +forEra("Ele30_WPTight_Gsf", 'D'),

            "MuonEG"         : [ #hlt.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, # do NOT use the DZ version*, it would be a needless efficiency loss 
                                 hlt.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,
                                 
                                 hlt.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ,  # Non DZ versions are prescaled 
                                 #hlt.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,

                                 hlt.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ, # Non DZ versions are prescaled 
                                 #hlt.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,

                                 hlt.Mu27_Ele37_CaloIdL_MW, 
                                 hlt.Mu37_Ele27_CaloIdL_MW ]
            }

def BTAGcalibration(tagger, wp , noSel, sample, era, nanoaodversion, mistagSF=False ):
    var = [] 
    if mistagSF:
        csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/mistagrates_sfs", "fromJoshua", "%s_%s.csv"%(tagger, era))
        measurement={"UDSG": "incl"}
        systname = 'bjets_mistagRates'
        var.extend(["up_correlated", "up_uncorrelated", "down_correlated", "down_uncorrelated"])
        suffix= 'MistagRate'
    else:
        idx = ( 1 if tagger== 'DeepCSV' else(0))
        EOYcsv = { '2016': ("DeepJet_2016LegacySF_V1.csv", "DeepCSV_2016LegacySF_V1.csv"),
                   '2017': ("DeepFlavour_94XSF_V4_B_F.csv", "DeepCSV_94XSF_V5_B_F.csv"), 
                   '2018': ("DeepJet_102XSF_V1.csv", "DeepCSV_102XSF_V1.csv")
                }
        Ulegacycsv = { '2016': ("DeepJet_2016LegacySF_V1.csv", "DeepCSV_2016LegacySF_V1.csv"),
                       '2017': ("DeepJet_106XUL17SF_WPonly_V2p1.csv", "DeepCSV_106XUL17SF_WPonly_V2p1.csv"), 
                       '2018': ("DeepJet_106XUL18SF_WPonly.csv", "DeepCSV_106XUL18SF_WPonly.csv")
                    }
        
        if  nanoaodversion in ["v8", "v9"]:
            csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/Inputs", '%sUL'%era, "Btag", Ulegacycsv[era][idx])
        else:
            csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/Inputs", '%s'%era, "Btag", EOYcsv[era][idx])

        measurement={"B": "comb", "C": "comb", "UDSG": "incl"}
        systname = 'bjets_SFs'
        suffix= 'Eff'

    if os.path.exists(csv_file):
        sf = BtagSF(tagger.lower(), csv_file, wp=wp, sysType="central", otherSysTypes=var.extend(["up", "down"]), 
                                systName= '%s_%s%s'%(systname, tagger,wp), measurementType=measurement, sel= noSel, 
                                uName='Evaluatebtag%s_On%s_%s%s'%(suffix, sample, tagger, wp[0]))
    else:
        raise RuntimeError("csv file : {0} not found !".format(csv_file))
    
    return sf


def bJetEnergyRegression(bjet):
    return op.map(bjet, lambda j : op.construct("ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>", (j.pt*j.bRegCorr, j.eta, j.phi, j.mass*j.bRegCorr)))

def JetsEnergyRegression(jet):
    corrected_jetEnergyRegression = op.map( jet, lambda j: op.construct("ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >",
                                                                        (op.product( j.pt, op.multiSwitch( (j.hadronFlavour == 5 , j.bRegCorr), (j.hadronFlavour == 4, j.cRegCorr), op.c_float(1) ) ), 
                                                                        j.eta, j.phi, 
                                                                        op.product ( j.mass, op.multiSwitch( (j.hadronFlavour == 5 , j.bRegCorr), (j.hadronFlavour == 4, j.cRegCorr), op.c_float(1) ))  )) )
    return corrected_jetEnergyRegression


class NanoHtoZABase(NanoAODModule):
    """ H/A ->Z(ll) H/A(bb) full run2 Ulegacy analysis """
    
    def __init__(self, args):
        super(NanoHtoZABase, self).__init__(args)
        self.plotDefaults = {
                            "y-axis"           : "Events",
                            "log-y"            : "both",
                            "y-axis-show-zero" : True,
                            "save-extensions"  : ["pdf", "png"],
                            "show-ratio"       : True,
                            "sort-by-yields"   : False,
                            "legend-columns"   : 2 }

        self.doSysts        = self.args.systematic
        self.doEvaluate     = self.args.DNN_Evaluation
        self.doSplit        = self.args.split
        self.doHLT          = self.args.hlt
        self.BeBlind        = self.args.blinded
        self.nanoaodversion = self.args.nanoaodversion
        self.doMETT1Smear   = self.args.doMETT1Smear
        self.dobJetER       = self.args.dobJetEnergyRegression

    def addArgs(self, parser):
        super(NanoHtoZABase, self).addArgs(parser)
        parser.add_argument("-s", "--systematic", action="store_true", help="Produce systematic variations")
        parser.add_argument("-dnn", "--DNN_Evaluation", action="store_true", help="Pass TensorFlow model and evaluate DNN output")
        parser.add_argument("--split", action="store_true", help="Run 2 reduced set of JES uncertainty splited by sources AND Split JER systematic variation between (kinematic) regions (to decorrelate the nuisance parameter)")
        parser.add_argument("--hlt", action="store_true", help="Produce HLT efficiencies maps")
        parser.add_argument("--blinded", action="store_true", help="Options to be blind on data if you want to Evaluate the training OR The Ellipses model ")
        parser.add_argument("--nanoaodversion", type=str, default="v8", choices = ["v9", "v8", "v7", "v5"], help="version NanoAODv2(== v8) and NanoAODvv9(== ULeagacy), the rest is pre-Legacy(== EOY) ")
        parser.add_argument("--doMETT1Smear", action="store_true", default = False, help="do T1 MET smearing")
        parser.add_argument("--dobJetEnergyRegression", action="store_true", default = False, help="apply b jets energy regreqqion to improve the bjets mass resolution")
        parser.add_argument("--backend", type=str, default="dataframe", help="Backend to use, 'dataframe' (default) or 'lazy'")

    def customizeAnalysisCfg(self, config=None):
        if self.args.distributed == "driver" or not self.args.distributed:
            os.system('(git log -n 1;git diff) &> %s/git.log' % self.args.output)
       #    with open(os.path.join(self.args.output, "config.yml"), "w+") as backupCfg:
       #        yaml.dump(config, backupCfg)

    def prepareTree(self, tree, sample=None, sampleCfg=None):
        era = sampleCfg.get("era") if sampleCfg else None
        isMC = self.isMC(sample)
        preVFPruns = ["2016B", "2016C", "2016D", "2016E", "2016F"]
        postVFPruns = ["2016G", "2016H"]

        if self.nanoaodversion in ["v8", "v9"]:
            metName   = "MET"
            isULegacy = True
        else:
            metName = "METFixEE2017" if era == "2017" else "MET"
            isULegacy = False
        
        ## initializes tree.Jet.calc so should be called first (better: use super() instead)
        from bamboo.treedecorators import NanoAODDescription, nanoRochesterCalc, nanoJetMETCalc, nanoJetMETCalc_METFixEE2017, CalcCollectionsGroups, nanoFatJetCalc
        nanoJetMETCalc_both = CalcCollectionsGroups(Jet=("pt", "mass"), systName="jet", changes={metName: (f"{metName}T1", f"{metName}T1Smear")}, **{metName: ("pt", "phi")})
        nanoJetMETCalc_data = CalcCollectionsGroups(Jet=("pt", "mass"), systName="jet", changes={metName: (f"{metName}T1",)}, **{metName: ("pt", "phi")})

        nanoJetMETCalc_ = (nanoJetMETCalc_METFixEE2017 if era == "2017" and not isULegacy else( (nanoJetMETCalc_both if isMC else nanoJetMETCalc_data) if self.doMETT1Smear else (nanoJetMETCalc)))
        tree,noSel,be,lumiArgs = NanoAODHistoModule.prepareTree(self, tree, sample=sample, sampleCfg=sampleCfg, 
                                                                description=NanoAODDescription.get("v7", year=(era if era else "2016"), 
                                                                                                    isMC=isMC, 
                                                                                                    systVariations=[ nanoRochesterCalc, nanoJetMETCalc_, nanoFatJetCalc ]), 
                                                                                                    backend=self.args.backend ) 
        
        triggersPerPrimaryDataset = {}
        jec, smear, jesUncertaintySources = None, None, None

        from bamboo.analysisutils import configureJets, configureType1MET, configureRochesterCorrection
        isNotWorker = (self.args.distributed != "worker") 
        
        from bamboo.root import gbl, loadHeader
        loadHeader(os.path.abspath(os.path.join(zabPath, "include/masswindows.h")))

        ellipsesName = be.symbol("std::vector<MassWindow> <<name>>{{}}; // for {0}".format(sample), nameHint="hza_ellipses{0}".format("".join(c for c in sample if c.isalnum())))
        ellipses_handle = getattr(gbl, ellipsesName)
        self.ellipses = op.extVar("std::vector<MassWindow>", ellipsesName) ## then use self.ellipses.at(i).radius(...) in your code

        with open("/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZATools/scripts_ZA/ellipsesScripts/vers20.06.03Inputs/fullEllipseParamWindow_MuMu.json") as ellPF:
            self.ellipse_params = json.load(ellPF)
        for params in self.ellipse_params:
            xc, yc, a, b, theta, MA, MH = params
            M11 = math.cos(theta)/math.sqrt(a)
            M12 = math.sin(theta)/math.sqrt(a)
            M21 = -math.sin(theta)/math.sqrt(b)
            M22 = math.cos(theta)/math.sqrt(b)
            ellipses_handle.push_back(gbl.MassWindow(xc, yc, M11, M12, M21, M22))

        if era == "2016-preVFP":
        #if "preVFP" in sample or any(x in sample for x in preVFPruns):
            configureRochesterCorrection(tree._Muon, os.path.join(os.path.dirname(__file__), "data/roccor.Run2.v5", "RoccoR2016aUL.txt"), isMC=isMC, backend=be, uName=sample)
        elif era == "2016-postVFP":
            configureRochesterCorrection(tree._Muon, os.path.join(os.path.dirname(__file__), "data/roccor.Run2.v5", "RoccoR2016bUL.txt"), isMC=isMC, backend=be, uName=sample)

            triggersPerPrimaryDataset = {
                "DoubleMuon" : [ tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                                 tree.HLT.Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL,
                                 tree.HLT.Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ ],
                "DoubleEG"   : [ tree.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ ],  # double electron (loosely isolated)
                "MuonEG"     : [ tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL ]
                }
            
            if self.isMC(sample) or "2016F" in sample or "2016G" in sample or "2016H" in sample:
                triggersPerPrimaryDataset["MuonEG"] += [ 
                        ## added for eras B, C, D, E
                        tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
                        tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ]
            
            if "2016H" not in sample :
                triggersPerPrimaryDataset["MuonEG"] += [ 
                        ## removed for era H
                        tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL]

            if self.isMC(sample):
                if "preVFP" in sample:
                    jec   = "Summer19UL16APV_V7_MC"
                    smear = "Summer20UL16APV_JRV3_MC"
                else:
                    jec   = "Summer19UL16_V7_MC"
                    smear = "Summer20UL16_JRV3_MC"

                if self.doSplit:
                    jesUncertaintySources=['Absolute', 'Absolute_2016', 'BBEC1', 'BBEC1_2016', 'EC2', 'EC2_2016', 'FlavorQCD', 'HF', 'HF_2016', 'RelativeBal', 'RelativeSample_2016']
                else:
                    jesUncertaintySources=["Total"]
                
            else:
                jec   = "Summer19UL16_RunBCDEFGH_Combined_V7_DATA"
                if "preVFP" in sample or any(x in sample for x in preVFPruns):
                    smear = "Summer20UL16APV_JRV3_DATA"
                else:
                    smear = "Summer20UL16_JRV3_DATA"
                    
        elif era == "2017":
            configureRochesterCorrection(tree._Muon, os.path.join(os.path.dirname(__file__), "data/roccor.Run2.v5", "RoccoR2017UL.txt"), isMC=isMC, backend=be, uName=sample)
            
            # https://twiki.cern.ch/twiki/bin/view/CMS/MuonHLT2017
            triggersPerPrimaryDataset = {
                "DoubleMuon" : [ #tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,  # this one is prescaled 
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8,
                                 #tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8  # Not for era B
                                 ],
                # it's recommended to not use the DoubleEG HLT _ DZ version  for 2017 and 2018, 
                # using them it would be a needless efficiency loss !
                #---> https://twiki.cern.ch/twiki/bin/view/CMS/EgHLTRunIISummary
                #*do NOT use the DZ version*, it would be a needless efficiency loss 
                "DoubleEG"   : [ tree.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL, # loosely isolated
                                 #tree.HLT.DoubleEle33_CaloIdL_MW,
                                 ], 
                                 # the MW refers to the pixel match window being "medium window" working point
                                 # also require additional HLT Zvtx Efficiency Scale Factor 
                "MuonEG"     : [ # tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,  #  Not for Era B
                                 tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
                                 # tree.HLT.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,  # Not for Era B
                                 tree.HLT.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ,
                                 # tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,   # Not for Era B
                                 tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ ],
                # FIXME : if you want to include them need to include the primary dataset too !!
                #"SingleElectron": [ tree.HLT.Ele35_WPTight_Gsf,
                #                    tree.HLT.Ele28_eta2p1_WPTight_Gsf_HT150 ],
                #"SingleMuon" :    [ tree.HLT.IsoMu27,
                #                    tree.HLT.IsoMu24_eta2p1],
            }
            
            if "2017B" not in sample:
             ## all are removed for 2017 era B
                triggersPerPrimaryDataset["MuonEG"] += [ 
                        tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,
                        tree.HLT.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,
                        #tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL  : prescaled 
                        ]
                triggersPerPrimaryDataset["DoubleMuon"] += [ 
                        tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8 ]
                triggersPerPrimaryDataset["DoubleEG"] += [ 
                        tree.HLT.DiEle27_WPTightCaloOnly_L1DoubleEG ]
            #if "2017B" not in sample and "2017C" not in sample:
            #    triggersPerPrimaryDataset["DoubleEG"] += [ 
            #            tree.HLT.DoubleEle25_CaloIdL_MW ]

            if self.isMC(sample):
                jec="Summer19UL17_V5_MC"
                smear="Summer19UL17_JRV3_MC"
                if self.doSplit:
                    jesUncertaintySources=['Absolute', 'Absolute_2017', 'BBEC1', 'BBEC1_2017', 'EC2', 'EC2_2017', 'FlavorQCD', 'HF', 'HF_2017', 'RelativeBal', 'RelativeSample_2017']
                else:
                    jesUncertaintySources=["Total"]
            else:
                if "2017B" in sample:
                    jec="Summer19UL17_RunB_V5_DATA"
                elif "2017C" in sample:
                    jec="Summer19UL17_RunC_V5_DATA"
                elif "2017D" in sample:
                    jec="Summer19UL17_RunD_V5_DATA"
                elif "2017E" in sample:
                    jec="Summer19UL17_RunE_V5_DATA"
                elif "2017F" in sample:
                    jec="Summer19UL17_RunF_V5_DATA"

        elif era == "2018":
            year = sampleCfg.get("era")
            suffix = "_UL" if isULegacy else "_"
            eraInYear = "" if isMC else next(tok for tok in sample.split(suffix) if tok.startswith(era))[4:]
            
            configureRochesterCorrection(tree._Muon, os.path.join(os.path.dirname(__file__), "data/roccor.Run2.v5", "RoccoR2018UL.txt"), isMC=isMC, backend=be, uName=sample)
            triggersPerPrimaryDataset = catchHLTforSubPrimaryDataset(era, eraInYear, tree, isMC=isMC)
            
            if self.isMC(sample):
                jec="Summer19UL18_V5_MC"
                smear="Summer19UL18_JRV2_MC"
                if self.doSplit:
                    jesUncertaintySources=['Absolute', 'Absolute_2018', 'BBEC1', 'BBEC1_2018', 'EC2', 'EC2_2018', 'FlavorQCD', 'HF', 'HF_2018', 'RelativeBal', 'RelativeSample_2018']
                else:
                    jesUncertaintySources=["Total"]
            else:
                if "2018A" in sample:
                    jec="Summer19UL18_RunA_V5_DATA"
                elif "2018B" in sample:
                    jec="Summer19UL18_RunB_V5_DATA"
                elif "2018C" in sample:
                    jec="Summer19UL18_RunC_V5_DATA"
                elif "2018D" in sample:
                    jec="Summer19UL18_RunD_V5_DATA"
        else:
            raise RuntimeError("Unknown era {0}".format(era))
        
        #############################
        ## Configure Jet Energy corrections and Jets Energy resolutions 
        # JEC's Recommendation for Full RunII: https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC
        # JER : -----------------------------: https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
        # list of supported para in JER : https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyResolution#List_of_supported_parameters 
        # github : https://github.com/cms-jet/JRDatabase/tree/master/textFiles
        #############################
        
        cmJMEArgs = {
                "jec": jec,
                "smear": smear,
                "splitJER": True,
                "jesUncertaintySources": jesUncertaintySources,
                ## Alternative, for regrouped
                ##"jesUncertaintySources": ("Merged" if isMC else None),
                ##"regroupTag": "V2",
                "mayWriteCache": isNotWorker,
                "isMC": isMC,
                "backend": be,
                "uName": sample
                }
        try:
            configureJets(tree._Jet, "AK4PFchs", **cmJMEArgs)
            configureJets(tree._FatJet, "AK8PFPuppi", mcYearForFatJets=era, **cmJMEArgs)
        except Exception as ex:
            logger.exception("Problem while configuring jet energy corrections and variations")
        
        if self.doSplit:
            try: 
                splitVariation(tree._Jet, "jer", op.multiSwitch(( lambda j: op.abs(j.eta) < 1.93, {"backward" : lambda j : j.pt >0.}) ,
                                                                ( lambda j: op.in_range(1.93, j.eta, 2.5), {"eta_1p93TO2p5" : lambda j : j.pt >0.}),                                        
                                                                ( lambda j: op.in_range(2.5, j.eta, 3), {"eta_2p5TO3_bin1" : lambda j : j.pt <50., "eta_2p5TO3_bin2" : lambda j : j.pt >50.}),
                                                                ( lambda j: op.in_range(3, j.eta, 5), {"eta_3TO2p5_bin1" : lambda j : j.pt <50., "eta_3TO2p5_bin2" : lambda j : j.pt >50.}),
                                                                ({"forward" : lambda j : j.pt >0.})
                                                                )
                                                            )
            except Exception as ex:
                logger.exception("Problem while spliting JER between (kinematic) regions (to decorrelate the nuisance parameter)")
        #############################
        ## Configure Type 1 MET corrections
        #############################
        try:
            if self.doMETT1Smear:
                if isMC:
                    configureType1MET(getattr(tree, f"_{metName}T1Smear"), isT1Smear=True, **cmJMEArgs)
                del cmJMEArgs["uName"]
                configureType1MET(getattr(tree, f"_{metName}T1"), enableSystematics=((lambda v : not v.startswith("jer")) if isMC else None), uName=f"{sample}NoSmear", **cmJMEArgs)
                cmJMEArgs["uName"] = sample
                cmJMEArgs.update({ "jesUncertaintySources": (jesUncertaintySources), "regroupTag": "V2" })
            else:
                configureType1MET(getattr(tree, f"_{metName}"), **cmJMEArgs)
        except Exception as ex:
            logger.exception("Problem while configuring MET correction and variations")
        #############################

        sampleCut = None
        if self.isMC(sample):
            # remove double counting passing TTbar Inclusive + TTbar Full Leptonic ==> mainly for 2016 Analysis 
            if sample == "TT":
                genLeptons_hard = op.select(tree.GenPart, 
                                            lambda gp : op.AND((gp.statusFlags & (0x1<<7)), 
                                                                op.in_range(10, op.abs(gp.pdgId), 17)))
                sampleCut = (op.rng_len(genLeptons_hard) <= 2)
                noSel = noSel.refine("genWeight", weight=tree.genWeight, 
                                                  cut=[sampleCut, op.OR(*chain.from_iterable(triggersPerPrimaryDataset.values())) ], 
                                                  autoSyst=self.doSysts)
            else:
                noSel = noSel.refine("genWeight", weight=tree.genWeight, 
                                                cut=(op.OR(*chain.from_iterable(triggersPerPrimaryDataset.values()))), 
                                                autoSyst=self.doSysts)
            if self.doSysts:
                logger.info("Adding QCD scale variations, ISR and FSR ")
                noSel = utils.addTheorySystematics(self, tree, noSel, qcdScale=True, PSISR=True, PSFSR=True, PDFs=False)
        else:
            noSel = noSel.refine("withTrig", cut=(makeMultiPrimaryDatasetTriggerSelection(sample, triggersPerPrimaryDataset)))
       
        return tree,noSel,be,lumiArgs
   
    def defineObjects(self, t, noSel, sample=None, sampleCfg=None):
        from bamboo.analysisutils import forceDefine
        #from bamboo.plots import Plot
        from bambooToOls import Plot
        from bamboo.plots import EquidistantBinning as EqB
        from bamboo import treefunctions as op
        from bamboo.analysisutils import makePileupWeight
        from METFilter_xyCorr import METFilter, METcorrection, ULMETXYCorrection
        from reweightDY import Plots_gen
        from systematics import getHLTZvtxSF 

        def getIDX(wp = None):
            return (0 if wp=="L" else ( 1 if wp=="M" else 2))
        def getOperatingPoint(wp = None):
            return ("Loose" if wp == 'L' else ("Medium" if wp == 'M' else "Tight"))
        
        isMC = self.isMC(sample)
        era  = sampleCfg.get("era") if sampleCfg else None
        era_ = era if "VFP" not in era else "2016"
        preVFPruns = ["2016B", "2016C", "2016D", "2016E", "2016F"]
        
        globalTag  = "106X" if self.nanoaodversion in ["v8", "v9"] else( "94X" if era != "2018" else ( "102X"))
        isULegacy  = True if globalTag =="106X" else False
        
        elRecoSF_version = 'POG' # Be careful the version from tth is `LOOSE` version 
        noSel = noSel.refine("passMETFlags", cut=METFilter(t.Flag, era, isMC) )
        
        puWeightsFile      = None
        mcprofile          = None
        PUWeight           = None
        version_TriggerSFs = None
        gen_ptll_nlo       = None
        gen_ptll_lo        = None
        yield_object  = makeYieldPlots()
        binScaling    = 1
        plots         = []
        
        ##################################################
        # Pileup 
        # mc profile for 2017 details here: 
        #   https://cp3-mm.irmp.ucl.ac.be/cp3-llbb/pl/w9srgswcabf1xfzxxnw9sjzt4e
        ##################################################
        
        if "2016" in era:
            if isULegacy:
                if "preVFP" in era :
                    puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/run2Ulegacy", "Ulegacy2016-preVFP_pileupWeights.json")
                elif "postVFP" in era:
                    puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/run2Ulegacy", "Ulegacy2016-postVFP_pileupWeights.json")
            else:
                puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/run2EOY", "puweights2016_Moriond17.json")
       
        elif era == "2017":
            if isULegacy:
                puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/run2Ulegacy", "Ulegacy2017_pileupWeights.json")
            else:
                if sample in ['DYJetsToLL_M-10to50', 'ST_tW_antitop_5f', 'ZH_HToBB_ZToLL', 'ggZH_HToBB_ZToLL',  'WWToLNuQQ', 'WZZ', 'TTWJetsToLNu', 'TTZToLLNuNu']:
                    if "pufile" not in sampleCfg:
                        raise KeyError("Could not find 'pufile' entry for sample %s in the YAML file"%sampleCfg["sample"])
                    mcprofile= os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/run2EOY/mcprofile/", "%s_2017.json"%sample)
                else:
                    puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/run2EOY", "puweights2017_Fall17.json")
        
        elif era == "2018":
            if isULegacy:
                puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/run2Ulegacy", "Ulegacy2018_pileupWeights.json")
            else:
                puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/run2EOY", "puweights2018_Autumn18.json")
        
        
        if not os.path.exists(puWeightsFile) and mcprofile is None :
            raise RuntimeError("Could not find pileup file %s"%puWeightsFile)
        
        if self.isMC(sample):
            if mcprofile is not None:
                PUWeight = makePileupWeight(mcprofile, t.Pileup_nTrueInt, variation="Nominal",
                                                   nameHint="puWeight_{0}".format(sample.replace('-','_')))
            else:
                suffix = "UL{}".format(era) if isULegacy else "EOY{}".format(puWeightsFile.split('/')[-1].split('_').split('.')[0])
                PUWeight = makePileupWeight(puWeightsFile, t.Pileup_nTrueInt, systName="pileup-%s"%(suffix))
            noSel = noSel.refine("puWeight", weight=PUWeight)
        
        ###########################################
        # Top reweighting :
        # https://indico.cern.ch/event/904971/contributions/3857701/attachments/2036949/3410728/TopPt_20.05.12.pdf
        ###########################################
        if self.isMC(sample) and sampleCfg["group"] in ['ttbar_FullLeptonic', 'ttbar_SemiLeptonic', 'ttbar_FullHadronic']:
            genTop_pt = op.select(t.GenPart, lambda gp : op.AND((gp.statusFlags & (0x1<<13)), gp.pdgId==6))
            gen_antiTop_pt = op.select(t.GenPart, lambda gp : op.AND((gp.statusFlags & (0x1<<13)), gp.pdgId==-6))
            gen_pt = op.map(genTop_pt, lambda top: top.pt)
            forceDefine(gen_pt, noSel)
            
            plots.append(Plot.make1D("gen_ToppT_noReweighting".format(suffix), gen_pt, noSel, EqB(60 // binScaling, 0., 1200.), title="gen Top p_{T} [GeV]"))

            # func not from the PAG 
            # TODO for 2016 there's diffrents SFs and in all cases you should produce your own following
            # https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopPtReweighting#Use_case_3_ttbar_MC_is_used_to_m 
            scalefactor = lambda t : op.exp(-2.02274e-01 + 1.09734e-04*t.pt -1.30088e-07*t.pt**2 + (5.83494e+01/(t.pt+1.96252e+02)))
            top_weight = lambda top, antitop : op.sqrt(scalefactor(top)*scalefactor(antitop))
            
            noSel = noSel.refine("top_reweighting", weight=top_weight(genTop_pt[0], gen_antiTop_pt[0]))
            forceDefine(gen_pt, noSel)
            plots.append(Plot.make1D("gen_ToppT_withReweighting".format(suffix), gen_pt, noSel, EqB(60 // binScaling, 0., 1200.), title="gen Top p_{T} [GeV]")) 
        
        # it will crash if evaluated when there are no two leptons in the matrix element
        isDY_reweight = (sample in ["DYJetsToLL_0J", "DYJetsToLL_1J", "DYJetsToLL_2J"])
        genLeptons_hard = op.select(t.GenPart, lambda gp : op.AND((gp.statusFlags & (0x1<<7)), op.in_range(10, op.abs(gp.pdgId), 17)))
        if isDY_reweight:
            gen_ptll_nlo = (genLeptons_hard[0].p4+genLeptons_hard[1].p4).Pt()
            forceDefine(gen_ptll_nlo, noSel)
            #plots.extend(Plots_gen(gen_ptll_nlo, noSel, "noSel"))
            #plots.extend(Plot.make1D("nGenLeptons_hard", op.rng_len(genLeptons_hard), noSel, EqB(5, 0., 5.),  title="nbr genLeptons_hard [GeV]")) 
        #elif sampleCfg["group"] == "DYJetsToLL_M-10to50":
        #   gen_ptll_lo = (genLeptons_hard[0].p4+genLeptons_hard[1].p4).Pt()
        #   forceDefine(gen_ptll_lo, noSel)
        
        ###############################################
        # Muons ID , ISO and RECO cuts and scale factors 
        # Working Point for 2016- 2017 -2018 : medium-identification  and tight-isolation 
        # https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Muon_Isolation
        ###############################################
        forceDefine(t._Muon.calcProd, noSel)
        #To suppress nonprompt leptons, the impact parameter in three dimensions of the lepton track, with respect to the primaryvertex, is required to be less than 4 times its uncertainty (|SIP3D|<4)
        sorted_muons = op.sort(t.Muon, lambda mu : -mu.pt)
        muons = op.select(sorted_muons, lambda mu : op.AND(mu.pt > 10., op.abs(mu.eta) < 2.4, mu.mediumId, mu.pfRelIso04_all<0.15, op.abs(mu.sip3d) < 4.))

        # 2016 seprate from 2017 &2018  because SFs need to be combined for BCDEF and GH eras !
        # 2016 ULegacy is split into two different reconstruction versions pre/post VFP 
        if "2016" in era:
            muMediumIDSF  = get_legacyscalefactor("lepton", ("muon_Summer19UL{0}_{1}".format(era, globalTag), "id_medium"), combine="weight", systName="muid-medium")
            muMediumISOSF = get_legacyscalefactor("lepton", ("muon_Summer19UL{0}_{1}".format(era, globalTag), "iso_tightrel_id_medium"), combine="weight", systName="muiso-tight")
        else:
            muMediumIDSF  = get_legacyscalefactor("lepton", ("muon_Summer19UL{0}_{1}".format(era, globalTag), "id_medium"), systName="muid-medium")
            muMediumISOSF = get_legacyscalefactor("lepton", ("muon_Summer19UL{0}_{1}".format(era, globalTag), "iso_tightrel_id_medium"), systName="muiso-tight") 
            #mutrackingSF = get_scalefactor("lepton", ("muon_{0}_{1}".format(era, globalTag), "id_TrkHighPtID_newTuneP"), systName="mutrk")
            
        ########################################
        # Additional SFs 
        ########################################
        # TkMuLowpT_reco = get_correction("Efficiency_muon_generalTracks_Run2018_UL_trackerMuon_below30.json", 
        #                                 "NUM_TrackerMuons_DEN_genTracks", 
        #                                 params={"pt": lambda mu :mu.pt, "abseta": lambda mu: op.abs(mu.eta)}, 
        #                                 systName= "TkMuonLowpTRECO", systParam="weight", systNomName="nominal", systVariations=("up", "down"))
        # 
        # TkMuLowpT_id = get_correction("Efficiency_muon_trackerMuon_Run2018_UL_ID_below30.json", 
        #                               "NUM_MediumID_DEN_TrackerMuons", 
        #                                params={"pt": lambda mu :mu.pt, "abseta": lambda mu: op.abs(mu.eta)}, 
        #                                systName= "TkMuonLowpTID", systParam="weight", systNomName="nominal", systVariations=("up", "down"))
        # 
        TkMuHighMom_reco = get_correction("HighpTMuon_above120_Run2018UL_RECO_POGformat.json", 
                                          "Eff_TrackerMuons_HighMomentum", 
                                           params={"p": lambda mu :mu.p, "abseta": lambda mu: op.abs(mu.eta)}, 
                                           systName= "TkMuonHighpTReco", systParam="weight", systNomName="nominal", systVariations=("up", "down"))
        
        trig_filter = "HLT_Mu50-TkMu100-Mu100" if "VFP" not in era else "HLT_Mu50-TkMu50"
        SLHLTMu  = get_legacyscalefactor("lepton", (f"hlt_Summer19UL{era_}_106X", trig_filter), isElectron=True, systName=trig_filter.lower())
        ###############################################
        # Electrons : ID , RECO cuts and scale factors
        # Wp  // 2016: Electron_cutBased_Sum16==3  -> medium     // 2017 -2018  : Electron_cutBased ==3   --> medium ( Fall17_V2)
        # asking for electrons to be in the Barrel region with dz<1mm & dxy< 0.5mm   //   Endcap region dz<2mm & dxy< 0.5mm 
        # cut-based ID Fall17 V2 the recommended one from POG for the FullRunII
        ###############################################
        sorted_electrons = op.sort(t.Electron, lambda ele : -ele.pt)
        electrons = op.select(sorted_electrons, lambda ele : op.AND(ele.pt > 15., op.abs(ele.eta) < 2.5 , ele.cutBased>=3, op.abs(ele.sip3d) < 4., 
                                                                    op.OR(op.AND(op.abs(ele.dxy) < 0.05, op.abs(ele.dz) < 0.1), 
                                                                          op.AND(op.abs(ele.dxy) < 0.05, op.abs(ele.dz) < 0.2) ))) 
        if "2016" in era:
            elMediumIDSF   = get_legacyscalefactor("lepton", ("electron_Summer19UL{0}_{1}".format(era,globalTag), "id_medium"), isElectron=True, combine="weight", systName="elid-medium")
            elRecoSF_lowpt = get_legacyscalefactor("lepton", ("electron_Summer19UL{0}_{1}".format(era,globalTag), "reco_ptBelow20"), isElectron=True, combine="weight", systName="lowpt-ele_reco")
            elRecoSF_highpt= get_legacyscalefactor("lepton", ("electron_Summer19UL{0}_{1}".format(era,globalTag), "reco_ptAbove20"), isElectron=True, combine="weight", systName="highpt-ele_reco")
        else:
            elMediumIDSF   = get_legacyscalefactor("lepton", ("electron_Summer19UL{0}_{1}".format(era,globalTag), "id_medium"), isElectron=True, systName="elid-medium")
            elRecoSF_lowpt = get_legacyscalefactor("lepton", ("electron_Summer19UL{0}_{1}".format(era,globalTag), "reco_ptBelow20"), isElectron=True, systName="lowpt-ele_reco")
            elRecoSF_highpt= get_legacyscalefactor("lepton", ("electron_Summer19UL{0}_{1}".format(era,globalTag), "reco_ptAbove20"), isElectron=True, systName="highpt-ele_reco")

        #elChargeSF = get_scalefactor("lepton", ("eChargeMisID", "eCharge_{0}".format(era)), isElectron=True, systName="ele_charge")
        
        ###############################################
        # MET 
        ###############################################
        MET = t.MET if isULegacy else (t.MET if era != "2017" else (t.METFixEE2017))
        PuppiMET = t.PuppiMET 
        if isULegacy:
            corrMET = ULMETXYCorrection(MET,t.PV,sample,f"UL{era}",self.isMC(sample))
        else:
            corrMET = METcorrection(MET,t.PV,sample,era,self.isMC(sample))
        
        ###############################################
        # AK4 Jets selections
        # 2016 - 2017 - 2018   ( j.jetId &2) ->      tight jet ID
        # For 2017 data, there is the option of "Tight" or "TightLepVeto", 
        # depending on how much you want to veto jets that overlap with/are faked by leptons
        ###############################################
        puIdWP = "loOse"
        CleanJets_fromPileup = False
        deltaR = 0.4
        jet_puID_wp = {
                    "loOse"    : lambda j : j.puId & 0x4,
                    "medium"   : lambda j : j.puId & 0x2,
                    "tight"    : lambda j : j.puId & 0x1
                }
        
        sorted_AK4jets= op.sort(t.Jet, lambda j : -j.pt)
        if era "2016" in era:
            # j.jetId &2 means tight 
            AK4jetsSel = op.select(sorted_AK4jets, lambda j : op.AND(j.pt > 20., op.abs(j.eta) < 2.4, (j.jetId &2)))        
        else:

            ###############################################
            # Apply Jet Plieup ID 
            #https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD
            # Jet ID flags bit1 is loose (always false in 2017 and 2018 since it does not exist), bit2 is tight, bit3 is tightLepVeto
            #jet.Id==6 means: pass tight and tightLepVeto ID. 
            
            #https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJetID
            
            #puId==0 means 000: fail all PU ID;
            #puId==4 means 100: pass loose ID, fail medium, fail tight;  
            #puId==6 means 110: pass loose and medium ID, fail tight; 
            #puId==7 means 111: pass loose, medium, tight ID.
            ###############################################
            if CleanJets_fromPileup :
                AK4jetsSel = op.select(sorted_AK4jets, lambda j : op.AND(j.pt > 30, op.abs(j.eta) < 2.5, j.jetId & 4, op.switch(j.pt < 50, jet_puID_wp.get(puIdWP), op.c_bool(True)))) 
            else :
                AK4jetsSel = op.select(sorted_AK4jets, lambda j : op.AND(j.pt > 30, op.abs(j.eta) < 2.5, j.jetId & 4))
        
        
        # exclude from the jetsSel any jet that happens to include within its reconstruction cone a muon or an electron.
        AK4jets = op.select(AK4jetsSel, 
                            lambda j : op.AND(
                                            op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < deltaR )), 
                                            op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < deltaR ))))

        cleaned_AK4JetsByDeepFlav = op.sort(AK4jets, lambda j: -j.btagDeepFlavB)
        cleaned_AK4JetsByDeepB = op.sort(AK4jets, lambda j: -j.btagDeepB)
        
        jets_noptcutSel = op.select(sorted_AK4jets, lambda j : op.AND(op.abs(j.eta) < 2.5, j.jetId & 4))
        jets_noptcut= op.select(jets_noptcutSel, 
                            lambda j : op.AND(
                                            op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < deltaR )), 
                                            op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < deltaR ))))
        
        ###############################################
        # Pileup Jets scale factors
        ###############################################
        if CleanJets_fromPileup:
             # FIXME : get_scalefactor works only on b-tagged jets --passed as lepton SFs for now      
            mcEffPUID = get_scalefactor("lepton", ("JetId_InHighPileup_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), 
                                                    "puid_eff_mc_%s"% puIdWP[0].upper()), systName="JetpuID_eff_mc_%s"%puIdWP)
            mcMistagPUID = get_scalefactor("lepton", ("JetId_InHighPileup_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), 
                                                    "puid_mistag_mc_%s"% puIdWP[0].upper()), systName="JetpuID_mistagrates_mc_%s"%puIdWP)
                
            dataEffPUID = get_scalefactor("lepton", ("JetId_InHighPileup_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), 
                                                    "puid_eff_data_%s"% puIdWP[0].upper()), systName="JetpuID_eff_data_%s"%puIdWP)
            dataMistagPUID = get_scalefactor("lepton", ("JetId_InHighPileup_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), 
                                                    "puid_mistag_data_%s"% puIdWP[0].upper()), systName="JetpuID_mistagrates_data_%s"%puIdWP)
    
            sfEffPUID = get_scalefactor("lepton", ("JetId_InHighPileup_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), 
                                                    "puid_eff_sf_%s"% puIdWP[0].upper()), systName="JetpuID_eff_sf_%s"%puIdWP)
            sfMistagPUID = get_scalefactor("lepton", ("JetId_InHighPileup_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), 
                                                    "puid_mistag_sf_%s"% puIdWP[0].upper()), systName="JetpuID_mistagrates_sf_%s"%puIdWP)


        ###############################################
        # AK8 Boosted Jets 
        # ask for two subjet to be inside the fatjet
        # The AK8 jets are required to have the nsubjettiness parameters tau2/tau1< 0.5 
        # to be consistent with an AK8 jet having two subjets.
        ###############################################
        sorted_AK8jets = op.sort(t.FatJet, lambda j : -j.pt)
        AK8jetsSel = op.select(sorted_AK8jets, 
                                lambda j : op.AND(j.pt > 200., op.abs(j.eta) < 2.4, (j.jetId &2), 
                                                  j.subJet1.isValid,
                                                  j.subJet2.isValid
                                                  , j.tau2/j.tau1 < 0.7 ))
        AK8jets = op.select(AK8jetsSel, 
                            lambda j : op.AND(
                                            op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < 0.8 )), 
                                            op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < 0.8 ))))
        
        cleaned_AK8JetsByDeepB = op.sort(AK8jets, lambda j: -j.btagDeepB)
        
        # No tau2/tau1 cut 
        fatjetsel_nosubjettinessCut = op.select(sorted_AK8jets, 
                                                    lambda j : op.AND(j.pt > 200., op.abs(j.eta) < 2.5, (j.jetId &2), 
                                                                      j.subJet1.isValid,
                                                                      j.subJet2.isValid) )
        
        fatjets_nosubjettinessCut = op.select(fatjetsel_nosubjettinessCut, 
                                                    lambda j : op.AND(
                                                        op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < 0.8 )), 
                                                        op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < 0.8 ))))
        cleaned_fatjet = op.sort(fatjets_nosubjettinessCut, lambda j: -j.btagDeepB)

        ###############################################
        # btagging requirements :
        # Now,  let's ask for the jets to be a b-jets 
        # DeepCSV or DeepJet==DeepFlavour medium b-tagging working point
        # bjets ={ "DeepFlavour": {"L": ( pass loose, fail medium, fail tight), 
        #                          "M": ( pass loose, pass medium  fail tight), 
        #                          "T": ( pass tight, fail medium, fail loose)}     
        #          "DeepCSV"    : {"L": (  ----  you get the idea           ;), 
        #                          "M": (  ----                              ), 
        #                          "T": (  ----                              )} }
        ###############################################
        eoy_btagging_wpdiscr_cuts = {
                "DeepCSV":{ # era: (loose, medium, tight)
                            "2016-preVFP" :(0.2217, 0.6321, 0.8953), 
                            "2016-postVFP":(0.2217, 0.6321, 0.8953), 
                            "2017":(0.1522, 0.4941, 0.8001), 
                            "2018":(0.1241, 0.4184, 0.7527) 
                          },
                "DeepFlavour":{
                            "2016-preVFP" :(0.0614, 0.3093, 0.7221), 
                            "2016-postVFP":(0.0614, 0.3093, 0.7221), 
                            "2017":(0.0521, 0.3033, 0.7489), 
                            "2018":(0.0494, 0.2770, 0.7264) 
                          }
                }
        
        legacy_btagging_wpdiscr_cuts = {
                "DeepCSV":{ # era: (loose, medium, tight)
                            "2016-preVFP" :(0.2217, 0.6321, 0.8953),  # FIXME it's the same as EOY working points the btv doesn't not provide 2016UL btagging scale factors yet : to be fixed later on ! 
                            "2016-postVFP":(0.2217, 0.6321, 0.8953),  # FIXME
                            "2017":(0.1355, 0.4506, 0.7738), 
                            "2018":(0.1208, 0.4168,  0.7665) 
                          },
                "DeepFlavour":{
                            "2016-preVFP" :(0.0614, 0.3093, 0.7221), # FIXME The same there are old cuts !
                            "2016-postVFP":(0.0614, 0.3093, 0.7221), # FIXME 
                            "2017":(0.0532, 0.3040, 0.7476), 
                            "2018":(0.0490, 0.2783, 0.7100) 
                          }
                }
        # same cut for run2 
        BoostedTopologiesWP = { 
                    "DoubleB":{
                            "L": 0.3, "M1": 0.6, "M2": 0.8, "T": 0.9 },
                    "DeepDoubleBvL":{
                            "L": 0.7, "M1": 0.86, "M2": 0.89, "T1": 0.91, "T2": 0.92}
                        }
        

        bjets_boosted      = {}
        bjets_resolved     = {}
        lightJets_boosted  = {}
        lightJets_resolved = {}
        
        # WorkingPoints = ["L", "M", "T"] 
        # For Boosted : DeepCSV available as b-tagger with WPs `cut on dicriminator` same as in resolved region for AK4Jets
        # .ie. only L and M are available !
        WorkingPoints = ["L", "M"]
        
        SFsperiod_dependency      = False
        
        nBr_subjets_passBtagDiscr = "atleast_1subjet_pass"
        nBr_light_subjets_NotpassBtagDiscr = "fatjet_notpass"
        
        for tagger  in legacy_btagging_wpdiscr_cuts.keys():
            
            bJets_AK4_deepflavour = {}
            bJets_AK4_deepcsv = {}
            bJets_AK8_deepcsv = {}
            
            lightJets_AK4_deepflavour = {}
            lightJets_AK4_deepcsv = {}
            lightJets_AK8_deepcsv = {}

            for wp in sorted(WorkingPoints):
                
                idx = getIDX(wp)
                suffix  = ("{}".format(getOperatingPoint(wp))).lower()

                wpdiscr_cut = legacy_btagging_wpdiscr_cuts[tagger][era][idx]

                key_fromscalefactors_libray = "btag_Summer19UL{}_106X".format(era) if isULegacy else( "btag_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"))
                    
                subjets_btag_req = { "atleast_1subjet_pass": lambda j : op.OR(j.subJet1.btagDeepB >= wpdiscr_cut, j.subJet2.btagDeepB >= wpdiscr_cut),
                                     "both_subjets_pass"   : lambda j : op.AND(j.subJet1.btagDeepB >= wpdiscr_cut, j.subJet2.btagDeepB >= wpdiscr_cut),
                                     "fatjet_pass"         : lambda j : j.btagDeepB >= wpdiscr_cut,
                                     }
                subjets_btag_req_onlightjets = { "atleast_1subjet_notpass": lambda j : op.OR(j.subJet1.btagDeepB < wpdiscr_cut, j.subJet2.btagDeepB < wpdiscr_cut),
                                                 "both_subjets_notpass"   : lambda j : op.AND(j.subJet1.btagDeepB < wpdiscr_cut, j.subJet2.btagDeepB < wpdiscr_cut),
                                                 "fatjet_notpass"         : lambda j : j.btagDeepB < wpdiscr_cut,
                                               }
                
                logger.info(f"{key_fromscalefactors_libray}: {tagger}{wp}, discriminator_cut = {wpdiscr_cut}" )
                
                if tagger == "DeepFlavour":
                    bJets_AK4_deepflavour[wp] = op.select(cleaned_AK4JetsByDeepFlav, lambda j : j.btagDeepFlavB >= wpdiscr_cut )
                    lightJets_AK4_deepflavour[wp] = op.select(cleaned_AK4JetsByDeepFlav, lambda j : j.btagDeepFlavB < wpdiscr_cut)

                    bjets_resolved[tagger] = bJets_AK4_deepflavour
                    lightJets_resolved[tagger] = lightJets_AK4_deepflavour
                    
                    #############################################################
                        # DeepJet scale factor:  
                        # NB: These one aren't in use anymore !
                    #############################################################
                    Jet_DeepFlavourBDisc = { "BTagDiscri": lambda j : j.btagDeepFlavB }
                    
                    if "2016" in era:  # FIXME no Btag scale factor for 2016UL yet
                        deepBFlavScaleFactor = get_scalefactor("jet", ("btag_2016_94X", "DeepJet_{}".format(suffix)),
                                                            additionalVariables=Jet_DeepFlavourBDisc, 
                                                            getFlavour=(lambda j : j.hadronFlavour),
                                                            systName="DeepFlavour{}sys".format(wp))  
                    else:
                        deepBFlavScaleFactor = get_legacyscalefactor("jet", (key_fromscalefactors_libray, "DeepJet_{}".format(suffix)),
                                                            additionalVariables=Jet_DeepFlavourBDisc, 
                                                            getFlavour=(lambda j : j.hadronFlavour),
                                                            systName="DeepFlavour{}sys".format(wp))  
                    
                else:
                    bJets_AK4_deepcsv[wp] = op.select(cleaned_AK4JetsByDeepB, lambda j : j.btagDeepB >= wpdiscr_cut)   
                    lightJets_AK4_deepcsv[wp] = op.select(cleaned_AK4JetsByDeepB, lambda j : j.btagDeepB < wpdiscr_cut)   
                    
                    bJets_AK8_deepcsv[wp] = op.select(cleaned_AK8JetsByDeepB, subjets_btag_req.get(nBr_subjets_passBtagDiscr))   
                    lightJets_AK8_deepcsv[wp] = op.select(cleaned_AK8JetsByDeepB, subjets_btag_req_onlightjets.get(nBr_light_subjets_NotpassBtagDiscr))
                    
                    bjets_resolved[tagger]     = bJets_AK4_deepcsv
                    bjets_boosted[tagger]      = bJets_AK8_deepcsv
                    lightJets_resolved[tagger] = lightJets_AK4_deepcsv
                    lightJets_boosted[tagger]  = lightJets_AK8_deepcsv
                    
                    #############################################################
                        # DeepCSV scale factors for AK4 Jets
                    #############################################################
                    Jet_DeepCSVBDis = { "BTagDiscri": lambda j : j.btagDeepB }
                    subJet_DeepCSVBDis = { "BTagDiscri": lambda j : op.AND(j.subJet1.btagDeepB, j.subJet2.btagDeepB) }
                    
                    if era == '2017' and SFsperiod_dependency :
                        deepB_AK4ScaleFactor = get_legacyscalefactor("jet", (key_fromscalefactors_libray, "DeepCSV_{}_period_dependency".format(suffix)), 
                                                    additionalVariables=Jet_DeepCSVBDis,
                                                    getFlavour=(lambda j : j.hadronFlavour),
                                                    combine ="weight",
                                                    systName="DeepCSV{}_sysbyEra".format(wp))  
                    else:
                        if "2016" in era: # FIXME NO 2016UL scale factor yet , keep it this way for now
                            deepB_AK4ScaleFactor = get_scalefactor("jet", ("btag_2016_94X", "DeepCSV_{}".format(suffix)), 
                                                    additionalVariables=Jet_DeepCSVBDis,
                                                    getFlavour=(lambda j : j.hadronFlavour),
                                                    systName="DeepCSV{}sys".format(wp))
                        else:
                            deepB_AK4ScaleFactor = get_legacyscalefactor("jet", (key_fromscalefactors_libray, "DeepCSV_{}".format(suffix)), 
                                                    additionalVariables=Jet_DeepCSVBDis,
                                                    getFlavour=(lambda j : j.hadronFlavour),
                                                    systName="DeepCSV{}sys".format(wp))  
                        #############################################################
                        # Subjet b-tagging  scale factors (not in use )
                        #############################################################
                        if era in ["2016-postVFP", "2016-preVFP", "2018"]: # FIXME 
                            deepB_AK8ScaleFactor = get_scalefactor("jet", ("btag_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "subjet_DeepCSV_{}".format(suffix)), 
                                                    additionalVariables=Jet_DeepCSVBDis,
                                                    getFlavour=(lambda j : j.hadronFlavour),
                                                    systName="boostedDeepCSV{}sys".format(wp))  
                        else:
                            deepB_AK8ScaleFactor = get_legacyscalefactor("jet", (key_fromscalefactors_libray, "subjet_DeepCSV_{}".format(suffix)), 
                                                    additionalVariables=Jet_DeepCSVBDis,
                                                    getFlavour=(lambda j : j.hadronFlavour),
                                                    systName="boostedDeepCSV{}sys".format(wp))  
                
        
        ########################################################
        # Zmass reconstruction : Opposite Sign , Same Flavour leptons
        ########################################################
        # supress quaronika resonances and jets misidentified as leptons
        LowMass_cut = lambda lep1, lep2: op.invariant_mass(lep1.p4, lep2.p4)>12.
        ## Dilepton selection: opposite sign leptons in range 70.<mll<120. GeV 
        osdilep_Z = lambda lep1,lep2 : op.AND(lep1.charge != lep2.charge, op.in_range(70., op.invariant_mass(lep1.p4, lep2.p4), 120.))
        osdilep   = lambda lep1,lep2 : op.AND(lep1.charge != lep2.charge)
        
        osLLRng = {
                "MuMu" : op.combine(muons, N=2, pred= osdilep_Z),
                "ElEl" : op.combine(electrons, N=2, pred= osdilep_Z),
                #"ElMu" : op.combine((electrons, muons), pred=lambda ele,mu : op.AND(LowMass_cut(ele, mu), osdilep(ele, mu) , ele.pt > mu.pt )),
                #"MuEl" : op.combine((muons, electrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), osdilep(ele, mu), mu.pt > ele.pt )),
                "MuEl" : op.combine((muons, electrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), osdilep(ele, mu))),
                }
         
        # FIXME maybe for 2017 or 2018 --> The leading pT for the emu or mue channel should be above 20 Gev !
        hasOSLL_cmbRng = lambda cmbRng : op.AND(op.rng_len(cmbRng) > 0, cmbRng[0][0].pt > 25.) 
        
        ## helper selection (OR) to make sure jet calculations are only done once
        hasOSLL = noSel.refine("hasOSLL", cut=op.OR(*( hasOSLL_cmbRng(rng) for rng in osLLRng.values())))
       
        forceDefine(t._Jet.calcProd, hasOSLL)
        metName = ("MET" if isULegacy else ("MET" if era != "2017" else "METFixEE2017"))
        if self.doMETT1Smear:
            forceDefine(getattr(t, f"_{metName}T1").calcProd, hasOSLL)
            if self.isMC(sample):
                forceDefine(getattr(t, f"_{metName}T1Smear").calcProd, hasOSLL)
        else:
            forceDefine(getattr(t, f"_{metName}").calcProd, hasOSLL)


        ########################################################
        # https://lathomas.web.cern.ch/lathomas/TSGStuff/L1Prefiring/PrefiringMaps_2016and2017/
        # https://twiki.cern.ch/twiki/bin/view/CMS/L1PrefiringWeightRecipe#Introduction
        # NANOAOD: The event weights produced by the latest version of the producer are included in nanoAOD starting from version V9. 
        # Lower versions include an earlier version of the ECAL prefiring weight and do not include the muon weights!
        ########################################################
        L1Prefiring = 1.
        if era in ["2016-postVFP", "2016-preVFP", "2017"]:
            L1Prefiring = getL1PreFiringWeight(t) 
        
        ########################################################
        ########################################################
        ZvtxSF = 1.
        if era == '2017':
            ZvtxSF = getHLTZvtxSF(era, sample, splitbyeras=False)
       
        ########################################################
        # HLT 
        ########################################################
        #if era == '2018': # for 2018 data only because SL primary dataset are ON 
        #    #(|eta|<1.479, in Barrel ) and in the endcaps |eta|>1.479 
        #    #single_eletrig = get_legacyscalefactor("lepton", ("eletrig_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "single_electron"), combine="weight", systName="single_eletrig")
        #    single_eletrig = get_scalefactor("lepton", ("eletrig_2018_102X", "ele28_ht150_OR_ele32"), isElectron=True, systName="hltSFs_ele28_ht150_OR_ele32")
        #    endcap_ele  = get_scalefactor("lepton", ("eletrig_2018_102X", "Endcap"), isElectron=True, systName="hltSFs_EndcapEle")
        #    barrel_ele = get_scalefactor("lepton", ("eletrig_2018_102X", "Barrel"), isElectron=True, systName="hltSFs_BarrelEle")
        #    single_mutrig = get_scalefactor("lepton", ("mutrig_2018_102X", "IsoMu24_beforeAfterHLTupdate"), combine="weight", systName="single_mutrig")
        
        if version_TriggerSFs == None or (version_TriggerSFs =='tth' and era=='2018'): # will pass HHMoriond17 the default version 
            
            doubleMuTrigSF = get_scalefactor("dilepton", ("doubleMuLeg_HHMoriond17_2016"), systName="HHMoriond17-mumutrig")  
            doubleEleTrigSF = get_scalefactor("dilepton", ("doubleEleLeg_HHMoriond17_2016"), systName="HHMoriond17-eleltrig")
            elemuTrigSF = get_scalefactor("dilepton", ("elemuLeg_HHMoriond17_2016"), systName="HHMoriond17-elmutrig")
            mueleTrigSF = get_scalefactor("dilepton", ("mueleLeg_HHMoriond17_2016"), systName="HHMoriond17-mueltrig")

        ########################################################
        ########################################################
            if era == "2018":
                llSFs = {
                    "MuMu" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[0]), muMediumISOSF(ll[1]), doubleMuTrigSF(ll), L1Prefiring ]), #single_mutrig(ll[0]), single_mutrig(ll[1]), L1Prefiring ]), # mutrackingSF(ll[0]), mutrackingSF(ll[1]) ]),
                   #"ElMu" : (lambda ll : [ elMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[1]), elRecoSF_lowpt(ll[0]), elRecoSF_highpt(ll[0]), elemuTrigSF(ll), L1Prefiring, ZvtxSF ]), # elChargeSF(ll[0]), mutrackingSF(ll[1])   ]),
                    "MuEl" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumISOSF(ll[0]), elMediumIDSF(ll[1]), elRecoSF_lowpt(ll[1]), elRecoSF_highpt(ll[1]), mueleTrigSF(ll) ]), #, single_eletrig(ll[1]), endcap_ele(ll[1])]),#, barrel_ele(ll[1]), L1Prefiring, ZvtxSF ]), # mutrackingSF(ll[0]), elChargeSF(ll[1])   ]),
                    "ElEl" : (lambda ll : [ elMediumIDSF(ll[0]), elMediumIDSF(ll[1]), elRecoSF_lowpt(ll[0]), elRecoSF_lowpt(ll[1]), elRecoSF_highpt(ll[0]), elRecoSF_highpt(ll[1]), doubleEleTrigSF(ll), L1Prefiring, ZvtxSF]), #, single_eletrig(ll[0]), endcap_ele(ll[1]), barrel_ele(ll[0]), endcap_ele(ll[0]), barrel_ele(ll[1]), single_eletrig(ll[1]), L1Prefiring, ZvtxSF ])   # elChargeSF(ll[0]), elChargeSF(ll[1])     ]),
                    }
            if era == "2017":
                llSFs = {
                    "MuMu" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[0]), muMediumISOSF(ll[1]), doubleMuTrigSF(ll), L1Prefiring ]), # mutrackingSF(ll[0]), mutrackingSF(ll[1]) ]),
                   #"ElMu" : (lambda ll : [ elMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[1]), elRecoSF_lowpt(ll[0]), elRecoSF_highpt(ll[0]), elemuTrigSF(ll), L1Prefiring, ZvtxSF ]), # elChargeSF(ll[0]), mutrackingSF(ll[1])   ]),
                    "MuEl" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumISOSF(ll[0]), elMediumIDSF(ll[1]), elRecoSF_lowpt(ll[1]), elRecoSF_highpt(ll[1]), mueleTrigSF(ll), L1Prefiring, ZvtxSF ]), # mutrackingSF(ll[0]), elChargeSF(ll[1])   ]),
                    "ElEl" : (lambda ll : [ elMediumIDSF(ll[0]), elMediumIDSF(ll[1]), elRecoSF_lowpt(ll[0]), elRecoSF_lowpt(ll[1]), elRecoSF_highpt(ll[0]), elRecoSF_highpt(ll[1]), doubleEleTrigSF(ll), L1Prefiring, ZvtxSF ])   # elChargeSF(ll[0]), elChargeSF(ll[1])     ]),
                    }
            if "2016" in era: 
                llSFs = {
                    "MuMu" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[0]), muMediumISOSF(ll[1]), doubleMuTrigSF(ll), L1Prefiring ]), # mutrackingSF(ll[0]), mutrackingSF(ll[1]) ]),
                   #"ElMu" : (lambda ll : [ elMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[1]), elRecoSF_lowpt(ll[0]), elRecoSF_highpt(ll[0]), elemuTrigSF(ll), L1Prefiring, ZvtxSF ]), # elChargeSF(ll[0]), mutrackingSF(ll[1])   ]),
                    "MuEl" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumISOSF(ll[0]), elMediumIDSF(ll[1]), elRecoSF_lowpt(ll[1]), elRecoSF_highpt(ll[1]), mueleTrigSF(ll), L1Prefiring, ZvtxSF ]), # mutrackingSF(ll[0]), elChargeSF(ll[1])   ]),
                    "ElEl" : (lambda ll : [ elMediumIDSF(ll[0]), elMediumIDSF(ll[1]), elRecoSF_lowpt(ll[0]), elRecoSF_lowpt(ll[1]), elRecoSF_highpt(ll[0]), elRecoSF_highpt(ll[1]), doubleEleTrigSF(ll), L1Prefiring, ZvtxSF ])   # elChargeSF(ll[0]), elChargeSF(ll[1])     ]),
                    }
        else:
            # tth SFs and others ... 
            doubleMuTrigSF= getTriggerSystematcis(era, osLLRng.get('MuMu')[0], 'MuMu', version_TriggerSFs)
            doubleEleTrigSF = getTriggerSystematcis(era, osLLRng.get('ElEl')[0], 'ElEl', version_TriggerSFs)
            elemuTrigSF = getTriggerSystematcis(era, osLLRng.get('ElMu')[0], 'ElMu', version_TriggerSFs)
            mueleTrigSF = getTriggerSystematcis(era, osLLRng.get('MuEl')[0], 'MuEl', version_TriggerSFs)
            
            llSFs = {
                "MuMu" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[0]), muMediumISOSF(ll[1]), doubleMuTrigSF, L1Prefiring ]), # mutrackingSF(ll[0]), mutrackingSF(ll[1]) ]),
               #"ElMu" : (lambda ll : [ elMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[1]), elRecoSF(ll[0]), elemuTrigSF, L1Prefiring, ZvtxSF ]), # elChargeSF(ll[0]), mutrackingSF(ll[1])   ]),
                "MuEl" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumISOSF(ll[0]),elMediumIDSF(ll[1]), elRecoSF(ll[1]), mueleTrigSF, L1Prefiring, ZvtxSF ]),  # mutrackingSF(ll[0]),elChargeSF(ll[1])    ]),
                "ElEl" : (lambda ll : [ elMediumIDSF(ll[0]), elMediumIDSF(ll[1]), elRecoSF(ll[0]), elRecoSF(ll[1]), doubleEleTrigSF, L1Prefiring, ZvtxSF ])   # elChargeSF(ll[0]), elChargeSF(ll[1])     ])
                }

        categories = dict((channel, (catLLRng[0], hasOSLL.refine("hasOs{0}".format(channel), cut=hasOSLL_cmbRng(catLLRng), weight=(llSFs[channel](catLLRng[0]) if isMC else None)) )) for channel, catLLRng in osLLRng.items())

        return noSel, PUWeight, categories, isDY_reweight, WorkingPoints, legacy_btagging_wpdiscr_cuts, deepBFlavScaleFactor, deepB_AK4ScaleFactor, deepB_AK8ScaleFactor, AK4jets, AK8jets, fatjets_nosubjettinessCut, bjets_resolved, bjets_boosted, CleanJets_fromPileup, electrons, muons, MET, corrMET, PuppiMET, elRecoSF_highpt, elRecoSF_lowpt, isULegacy

class NanoHtoZA(NanoHtoZABase, HistogramsModule):
    def __init__(self, args):
        super(NanoHtoZA, self).__init__(args)
    #@profile
    # https://stackoverflow.com/questions/276052/how-to-get-current-cpu-and-ram-usage-in-python
    def definePlots(self, t, noSel, sample=None, sampleCfg=None):
        #from bamboo.plots import Plot
        from bambooToOls import Plot
        from bamboo.plots import CutFlowReport
        from reweightDY import plotsWithDYReweightings, Plots_gen, PLots_withtthDYweight
    
        def getIDX(wp = None):
            return (0 if wp=="L" else ( 1 if wp=="M" else 2))
        def getOperatingPoint(wp = None):
            return ("Loose" if wp == 'L' else ("Medium" if wp == 'M' else "Tight"))
        
        noSel, PUWeight, categories, isDY_reweight, WorkingPoints, legacy_btagging_wpdiscr_cuts, deepBFlavScaleFactor, deepB_AK4ScaleFactor, deepB_AK8ScaleFactor, AK4jets, AK8jets, fatjets_nosubjettinessCut, bjets_resolved, bjets_boosted, CleanJets_fromPileup, electrons, muons, MET, corrMET, PuppiMET, elRecoSF_highpt, elRecoSF_lowpt, isULegacy = super(NanoHtoZA, self).defineObjects(t, noSel, sample, sampleCfg)
        
        era = sampleCfg.get("era") if sampleCfg else None
        yield_object = makeYieldPlots()
        isMC = self.isMC(sample)
        binScaling = 1 
        
        plots = []
        selections_for_cutflowreport = []

        scalesfactorsLIB = {
            "DeepFlavour": {
                year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
                    {"2016": "2016/Btag/DeepJet_2016LegacySF_V1.csv", "2017": "2017/Btag/DeepFlavour_94XSF_V4_B_F.csv", "2018": "2018/Btag/DeepJet_102XSF_V1.csv"}.items() },
            "DeepCSV" :{
                "Ak4": {
                        year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
                            {"2016":"2016/Btag/DeepCSV_2016LegacySF_V1.csv" , "2017": "2017/Btag/DeepCSV_94XSF_V5_B_F.csv" , "2018": "2018/Btag/DeepCSV_102XSF_V1.csv"}.items() },
                "softdrop_subjets": {
                        year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
                            {"2016":"2016/Btag/subjet_DeepCSV_2016LegacySF_V1.csv" , "2017": "2017/Btag/subjet_DeepCSV_94XSF_V4_B_F_v2.csv" , "2018": "2018/Btag/subjet_DeepCSV_102XSF_V1.csv"}.items() }, }
            }
        
        scalesfactorsULegacyLIB = {
            "DeepFlavour": {
                year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
                {"2016-preVFP": "2016/Btag/DeepJet_2016LegacySF_V1.csv", "2016-postVFP": "2016/Btag/DeepJet_2016LegacySF_V1.csv", "2017": "2017UL/Btag/DeepJet_106XUL17SF_WPonly_V2p1.csv", "2018": "2018UL/Btag/DeepJet_106XUL18SF_WPonly.csv"}.items() },
            "DeepCSV" :{
                "Ak4": {
                        year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
                        {"2016-preVFP":"2016/Btag/DeepCSV_2016LegacySF_V1.csv", "2016-postVFP":"2016/Btag/DeepCSV_2016LegacySF_V1.csv", "2017": "2017UL/Btag/DeepCSV_106XUL17SF_WPonly_V2p1.csv" , "2018": "2018UL/Btag/DeepCSV_106XUL18SF_WPonly.csv"}.items() },
                "softdrop_subjets": {
                        year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
                        {"2016-preVFP":"2016/Btag/subjet_DeepCSV_2016LegacySF_V1.csv", "2016-postVFP":"2016/Btag/subjet_DeepCSV_2016LegacySF_V1.csv", "2017": "2017UL/Btag/subjet_DeepCSV_106X_UL17_SF.csv" , "2018": "2018/Btag/subjet_DeepCSV_102XSF_V1.csv"}.items() }, }
            }

        addIncludePath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "include"))
        loadHeader("BTagEffEvaluator.h")

        cleaned_AK4JetsByDeepFlav = op.sort(AK4jets, lambda j: -j.btagDeepFlavB)
        cleaned_AK4JetsByDeepB = op.sort(AK4jets, lambda j: -j.btagDeepB)
        cleaned_AK8JetsByDeepB = op.sort(AK8jets, lambda j: -j.btagDeepB)

        if self.doEvaluate:
            ZAmodel_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'ZAMachineLearning/tf_model','tf_bestmodel_max_eval_mean_trainResBoOv0_fbversion.pb')
            if not os.path.exists(ZAmodel_path):
                raise RuntimeError(f'Could not find model file {ZAmodel_path}')
            else:
                try:
                    ZAmodel = op.mvaEvaluator(ZAmodel_path,mvaType='Tensorflow',otherArgs=(['IN'], 'OUT/Softmax'), nameHint='tf_ZAModel')
                except:
                    raise RuntimeError(f'Could not op.mvaEvaluator Tensorflow model : {ZAmodel_path}')
        
        masses_seen = [
        #part0 : 21 signal samples 
        #( MH, MA)
        ( 200, 50), ( 200, 100),
        ( 250, 50), ( 250, 100),
        ( 300, 50), ( 300, 100), ( 300, 200),
        ( 500, 50), ( 500, 200), ( 500, 300), ( 500, 400),
        ( 650, 50),
        ( 800, 50), ( 800, 200), ( 800, 400), ( 800, 700),
        (1000, 50), (1000, 200), (1000, 500),    
        (2000, 1000),        
        (3000, 2000), 
        ]
        #part1
        masses_notseen = [
        (173.52,  72.01), #(209.90,  30.00), (209.90,  37.34), (261.40, 102.99), (261.40, 124.53),
        (296.10, 145.93), #(296.10,  36.79), (379.00, 205.76), (442.63, 113.53), (442.63,  54.67),
        (442.63,  80.03), (609.21, 298.01), (717.96,  30.00), #(717.96, 341.02), (846.11, 186.51),
        (846.11, 475.64), (846.11,  74.80), (997.14, 160.17), (997.14, 217.19), (997.14, 254.82), (997.14, 64.24) ]


        make_ZpicPlots              = True #*
        make_JetmultiplictyPlots    = True #*
        make_JetschecksPlots        = True # check the distance in deltaR of the closest electron to a given jet and a view more control histograms which might be of interest. 
        make_JetsPlusLeptonsPlots   = True #*
        make_DeepDoubleBPlots       = False
        make_METPlots               = False
        make_METPuppiPlots          = False
        make_ttbarEstimationPlots   = False
        make_ellipsesPlots          = False #*
        make_PlotsforCombinedLimits = False
        
        # One of these two should be True if you want to get the final sel plots (.ie. ll + bb )
        make_bJetsPlusLeptonsPlots_METcut   = False
        make_bJetsPlusLeptonsPlots_NoMETcut = False
        
        make_FinalSelControlPlots    = False #*
        make_zoomplotsANDptcuteffect = False
        make_2017Checksplots         = False
        make_LookInsideJets          = False
        
        make_reconstructedVerticesPlots  = False
        make_DYReweightingPlots_2017Only = False #*
        
        # don't forget to set these 
        split_DYWeightIn64Regions   = False
        istthDY_weight              = False
        
        HighPileupJetIdWeight       = None
        
        chooseJetsLen  = '_at_least2Jets_'
        #chooseJetsLen = '_only2Jets_' 
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                               # more plots to invistagtes 2017 problems  
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if make_2017Checksplots :
            plots += choosebest_jetid_puid(t, muons, electrons, categories, era, sample, isMC)
        
        for channel, (dilepton, catSel) in categories.items():
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                            # check low pt && high pt ele (< 20 GeV)- POG SFs
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
           # if era != '2018':
           #     ele_recoweight = None
           #     if channel =='ElEl':
           #         ele_recoweight= [ elRecoSF_highpt(dilepton[0]), elRecoSF_lowpt(dilepton[1]), elRecoSF_highpt(dilepton[1])]
           #     elif channel =='ElMu':
           #         ele_recoweight = [elRecoSF_highpt(dilepton[0])]
           #     elif channel =='MuEl':
           #         ele_recoweight = [elRecoSF_lowpt(dilepton[1]), elRecoSF_highpt(dilepton[1])]
           #     refine_Oslepsel = catSel.refine( 'ele_reco_SF_%s'%channel, weight=(( ele_recoweight )if isMC else None))
           #     makeControlPlotsForZpic(refine_Oslepsel, dilepton, 'oslepSel_add_eleRecoSF', channel, '_' )

           # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # Zmass (2Lepton OS && SF ) 
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                
            optstex = ('e^{+}e^{-}' if channel=="ElEl" else( '$\mu^+\mu^-$' if channel=="MuMu" else( '$\mu^+e^-$' if channel=="MuEl" else('$e^+\mu^-$'))))
            yield_object.addYields(catSel,"hasOs%s"%channel,"OS leptons+ M_{ll} cut(channel: %s)"%optstex)
            selections_for_cutflowreport.append(catSel)
            if make_ZpicPlots:
                plots += varsCutsPlotsforLeptons(dilepton, catSel, channel)
                plots.extend(makeControlPlotsForZpic(catSel, dilepton, 'oslepSel', channel, '_'))
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # Jets multiplicty  
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            if make_JetmultiplictyPlots :
                for jet, reg in zip ([AK4jets, AK8jets], ["resolved", "boosted"]):
                    plots.extend(makeJetmultiplictyPlots(catSel, jet, channel,"_NoCutOnJetsLen_" + reg))
            
            # This's an Inclusive selection *** 
            #       boosted : at least 1 AK8jets  && resolved: at least 2 AK4jets  
            # I don't care about my CR if boosted and resolved are inclusive , what's matter for me is my SR  ** 
            TwoLeptonsTwoJets_Resolved= catSel.refine("TwoJet_{0}Sel_resolved".format(channel), cut=[ op.rng_len(AK4jets) > 1])
            TwoLeptonsOneJet_Boosted = catSel.refine("OneJet_{0}Sel_boosted".format(channel), cut=[ op.rng_len(AK8jets) > 0 ])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # High Pileup JetId Weight 
            # N.B : boosted is unlikely to have pu jets ; jet pt > 200 in the boosted cat 
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            
            if CleanJets_fromPileup:
                TwoLeptonsTwoJets_Resolved_NopuWeight = TwoLeptonsTwoJets_Resolved
                if isMC:
                    pu_weight= makePUIDSF(AK4jets, era, wp=puIdWP[0].upper(), wpToCut=jet_puID_wp.get(puIdWP))
                TwoLeptonsTwoJets_Resolved = TwoLeptonsTwoJets_Resolved_NopuWeight.refine( "TwoJet_{0}Sel_resolved_inclusive_puWeight_{0}".format(channel, puIdWP), weight= pu_weight)
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # Catagories
            # gg fusion :  
            #              resolved :  exactly 2 AK4 b jets 
            #              boosted:    exactly 1 fat bjet
            # b-associated production : 
            #              resolved : at least 3 AK4 bjets 
            #              boosted: at least 1 fat bjets && 1 AK4 bjets

            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            
            lljjSelections = { "resolved": TwoLeptonsTwoJets_Resolved,
                               "boosted" : TwoLeptonsOneJet_Boosted }
            
            jlenOpts = { "resolved": ('at least 2' if chooseJetsLen=='_at_least2Jets_' else ( 'exactly 2')),
                         "boosted" :  'at least 1'}
            
            lljj_jetType = { "resolved": "AK4",
                             "boosted" : "AK8"}
            
            lljj_selName = { "resolved": "has2Lep2ResolvedJets",
                             "boosted" : "has2Lep1BoostedJets"}
            
            lljj_jets = { "resolved": AK4jets,
                          "boosted" : AK8jets }
            
            lljj_bJets = { "resolved": bjets_resolved,
                           "boosted" : bjets_boosted }
        
            for regi,sele in lljjSelections.items():
                yield_object.addYields(sele, f"{lljj_selName[regi]}_{channel}" , f"2 Lep(OS)+ {jlenOpts[regi]} {lljj_jetType[regi]}Jets+ $M_{{ll}}$ cut(channel: {optstex})")
                selections_for_cutflowreport.append(sele)

            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                     # DY - Reweighting  
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            if channel in ['ElEl', 'MuMu']:
                if isDY_reweight:
                    plots.extend(Plots_gen(gen_ptll_nlo, lljjSelections["resolved"], '%s_resolved_2lep2jSel'%channel, sample))
                if istthDY_weight:
                    plots.extend(PLots_withtthDYweight(channel, dilepton, AK4jets, lljjSelections["resolved"], 'resolved', isDY_reweight, era))
            #FIXME lightJets_resolved it seems to me empty list ! 
            #if make_DYReweightingPlots_2017Only and era =='2017':
                #    TwoLepTwoNonBjets_resolvedSel  = lljjSelections["resolved"].refine( "2lep{0}_atleast2lightJets_selection".format(channel), 
                #                                                                cut = [op.rng_len(safeget(lightJets_resolved, "DeepCSV", "M")) > 1])
                #    plots.extend(plotsWithDYReweightings(AK4jets, dilepton, TwoLepTwoNonBjets_resolvedSel, channel, 'resolved', isDY_reweight, split_DYWeightIn64Regions))
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                # more Investigation pffff ... :(
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            
            if make_zoomplotsANDptcuteffect:
                plots.extend(ptcuteffectOnJetsmultiplicty(catSel, dilepton, jets_noptcut, AK4jets, corrMET, era, channel))
                plots.extend(zoomplots(catSel, lljjSelections["resolved"], dilepton, AK4jets, 'resolved', channel))
            
            if make_METPuppiPlots:
                plots.extend(MakePuppiMETPlots(PuppiMET, lljjSelections["resolved"], channel))
            if make_LookInsideJets:
                plots.extend(LeptonsInsideJets(AK4jets, lljjSelections["resolved"], channel))

            if make_reconstructedVerticesPlots:
                plots.extend( makePrimaryANDSecondaryVerticesPlots(t, catSel, channel))
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                # Control Plots in boosted and resolved  
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # ----- plots : mll, mlljj, mjj, nVX, pT, eta  : basic selection plots ------
            for reg, sel in lljjSelections.items():
                jet = lljj_jets[reg]
                if make_JetschecksPlots:
                    plots.extend(makedeltaRPlots(sel, jet, dilepton, channel, reg))
                    plots.extend(makeJetmultiplictyPlots(sel, jet, channel, reg))
                if make_JetsPlusLeptonsPlots:
                    plots.extend(makeJetPlots(sel, jet, channel, reg, era))
                    plots.extend(makeControlPlotsForBasicSel(sel, jet, dilepton, channel, reg))
                if make_ZpicPlots:
                    plots.extend(makeControlPlotsForZpic(sel, dilepton, 'lepplusjetSel', channel, reg))
           
            plots.extend(makeNsubjettinessPLots(lljjSelections["boosted"], AK8jets, catSel, fatjets_nosubjettinessCut, channel))
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # DeepDoubleB for boosted events (L, M1, M2, T1, T2)  wp   
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            if make_DeepDoubleBPlots and "DeepDoubleBvL" in BoostedTopologiesWP:
                for wp in sorted(BoostedTopologiesWP["DeepDoubleBvL"].keys()):
                   _2Lep2bjets_boOsted_NoMETcut = { "DeepDoubleBvL{0}".format(wp) :
                           lljjSelections["boosted"].refine("TwoLeptonsOneBjets_NoMETcut_DeepDoubleBvL{0}_{1}_Boosted".format(wp, channel),
                               cut=[ op.rng_len(BoOstedJets["DeepDoubleBvL"][wp]) > 0],
                               weight=( getBoOstedWeight(era, 'DeepDoubleBvL', wp, AK8jets) if isMC else None))
                           }
                   for suffix, sel in {
                            '_NoMETCut_' : _2Lep2bjets_boOsted_NoMETcut,
                            '_METCut_' : { key: selNoMET.refine(selNoMET.name.replace("NoMETcut_", ""), cut=(corrMET.pt < 80.))
                                for key, selNoMET in _2Lep2bjets_boOsted_NoMETcut.keys() }
                            }.items():
                        plots.extend(makeBJetPlots(sel, BoOstedJets, wp, channel, "boosted", suffix, era))
                        plots.extend(makeControlPlotsForFinalSel(sel, BoOstedJets, dilepton, wp, channel, "boosted", suffix))
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # DeepCSV for both boosted && resolved , DeepFlavour  
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            bestJetPairs = {}
            
            for wp in WorkingPoints: 
                
                idx = getIDX(wp) 
                OP  = getOperatingPoint(wp) 
                
                run2_bTagEventWeight_PerWP = collections.defaultdict(dict)
                
                for tagger,bScore in {"DeepCSV": "btagDeepB", "DeepFlavour": "btagDeepFlavB"}.items():
                    jets_by_score = op.sort(bjets_resolved[tagger][wp], partial((lambda j,bSc=None : -getattr(j, bSc)), bSc=bScore))
                    bestJetPairs[tagger] = (jets_by_score[0], jets_by_score[1])
                
                # resolved 
                bJets_resolved_PassdeepflavourWP  = bjets_resolved["DeepFlavour"][wp]
                bJets_resolved_PassdeepcsvWP      = bjets_resolved["DeepCSV"][wp]
                # boosted
                bJets_boosted_PassdeepcsvWP       = bjets_boosted["DeepCSV"][wp]
                
                for suffix, bjet in { "resolved_DeepFlavour{}".format(wp): bJets_resolved_PassdeepflavourWP, 
                                      "resolved_DeepCSV{}".format(wp): bJets_resolved_PassdeepcsvWP,
                                      "boosted_DeepCSV{}".format(wp): bJets_boosted_PassdeepcsvWP }.items():
                    plots.extend(makeJetmultiplictyPlots(catSel, bjet, channel,"_NoCutOnbJetsLen_"+ suffix))
                
                if self.dobJetER:
                    bJets_resolved_PassdeepflavourWP = bJetEnergyRegression( bJets_resolved_PassdeepflavourWP)
                    bJets_resolved_PassdeepcsvWP     = bJetEnergyRegression( bJets_resolved_PassdeepcsvWP)
                    bJets_boosted_PassdeepcsvWP      = bJetEnergyRegression( bJets_boosted_PassdeepcsvWP)
                
                
                pathtoRoOtmaps = { '2016-preVFP' : "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ul2016__btv_effmaps/results/summedProcessesForEffmaps/summedProcesses_2016_ratios.root",
                                   '2016-postVFP': "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ul2016__btv_effmaps/results/summedProcessesForEffmaps/summedProcesses_2016_ratios.root",
                                   '2017': "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ul2017__btv_effmaps__ext2/results/summedProcessesForEffmaps/summedProcesses_2017_ratios.root",
                                   '2018': "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ul2018__btv_effmaps/results/summedProcessesForEffmaps/summedProcesses_2018_ratios.root"
                                   }
                
                if isULegacy:
                    csv_deepcsvAk4     = scalesfactorsULegacyLIB['DeepCSV']['Ak4'][era]
                    csv_deepcsvSubjets = scalesfactorsULegacyLIB['DeepCSV']['softdrop_subjets'][era]
                    csv_deepflavour    = scalesfactorsULegacyLIB['DeepFlavour'][era]
                else:
                    csv_deepcsvAk4     = scalesfactorsLIB['DeepCSV']['Ak4'][era]
                    csv_deepcsvSubjets = scalesfactorsLIB['DeepCSV']['softdrop_subjets'][era]
                    csv_deepflavour    = scalesfactorsLIB['DeepFlavour'][era]

                btagSF_deepcsv     = BtagSF('deepcsv', csv_deepcsvAk4, wp=OP, sysType="central", otherSysTypes=["up", "down"],
                                                        systName= f'mc_eff_deepcsv{wp}', measurementType={"B": "comb", "C": "comb", "UDSG": "incl"}, sel= noSel,
                                                        uName=f'sf_eff_{channel}_On{sample}_deepcsv{wp}')
                btagSF_deepflavour = BtagSF('deepflavour', csv_deepflavour, wp=OP, sysType="central", otherSysTypes=["up", "down"],
                                                        systName= f'mc_eff_deepflavour{wp}', measurementType={"B": "comb", "C": "comb", "UDSG": "incl"}, sel= noSel,
                                                        uName=f'sf_eff_{channel}_On{sample}_deepflavour{wp}')
                if 'Tight' not in OP : 
                    btagSF_subjets = BtagSF('deepcsv', csv_deepcsvSubjets, wp=OP, sysType="central", otherSysTypes=["up", "down"],
                                                        systName= f'mc_eff_subjets_deepcsv{wp}', measurementType={"B": "lt", "C": "lt", "UDSG": "incl"}, sel= noSel,
                                                        uName=f'sf_eff_{channel}_On{sample}_subjets_deepcsv{wp}')
                

                for process in ['gg_fusion', 'bb_associatedProduction']:
                    if os.path.exists(pathtoRoOtmaps[era]):
                        bTagEff_deepcsvAk4  = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "resolved", "deepcsv", {%s}, "%s");'%(pathtoRoOtmaps[era], wp, legacy_btagging_wpdiscr_cuts['DeepCSV'][era][idx], process))
                        bTagEff_deepflavour = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "resolved", "deepflavour", {%s}, "%s");'%(pathtoRoOtmaps[era], wp, legacy_btagging_wpdiscr_cuts['DeepFlavour'][era][idx], process))
                        if 'T' not in wp:
                            bTagEff_deepcsvAk8 = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "boosted", "deepcsv", {%s}, "%s");'%(pathtoRoOtmaps[era], wp, legacy_btagging_wpdiscr_cuts['DeepCSV'][era][idx], process))
                    else:
                        raise RuntimeError(f"{era} efficiencies maps not found !")

                    if isMC:
                        bTagSF_DeepCSVPerJet     = op.map(cleaned_AK4JetsByDeepB, lambda j: bTagEff_deepcsvAk4.evaluate(j.hadronFlavour, j.btagDeepB, j.pt, op.abs(j.eta), btagSF_deepcsv(j)))
                        bTagSF_DeepFlavourPerJet = op.map(cleaned_AK4JetsByDeepFlav, lambda j: bTagEff_deepflavour.evaluate(j.hadronFlavour, j.btagDeepFlavB, j.pt, op.abs(j.eta), btagSF_deepflavour(j)))
                        bTagSF_DeepCSVPerSubJet  = op.map(cleaned_AK8JetsByDeepB, lambda j: op.product(bTagEff_deepcsvAk8.evaluate( op.static_cast("BTagEntry::JetFlavor", 
                                                                                                            op.multiSwitch((j.nBHadrons >0, op.c_int(5)), (j.nCHadrons >0, op.c_int(4)), op.c_int(0)) ), 
                                                                                                                            j.subJet1.btagDeepB, j.subJet1.pt, op.abs(j.subJet1.eta), btagSF_subjets(j)) , 
                                                                                                       bTagEff_deepcsvAk8.evaluate( op.static_cast("BTagEntry::JetFlavor",
                                                                                                            op.multiSwitch((j.nBHadrons >0, op.c_int(5)), (j.nCHadrons >0, op.c_int(4)), op.c_int(0)) ), 
                                                                                                                            j.subJet2.btagDeepB, j.subJet2.pt, op.abs(j.subJet2.eta), btagSF_subjets(j))  )
                                                                                                        )
                        

                        run2_bTagEventWeight_PerWP[process]['resolved'] = { 'DeepCSV{0}'.format(wp): op.rng_product(bTagSF_DeepCSVPerJet), 'DeepFlavour{0}'.format(wp): op.rng_product(bTagSF_DeepFlavourPerJet) }
                        run2_bTagEventWeight_PerWP[process]['boosted']  = { 'DeepCSV{0}'.format(wp): op.rng_product(bTagSF_DeepCSVPerSubJet) }

                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # No MET cut : selections 2 lep + at least 2b-tagged jets
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
               ###########################
                # NO PROCESS SPLITTING  
               ###########################
               # TwoLeptonsTwoBjets_NoMETCut_NobTagEventWeight_Res = {
               #     "DeepFlavour{0}".format(wp) :  lljjSelections["resolved"].refine("TwoLeptonsTwoBjets_NoMETcut_NobTagEventWeight_DeepFlavour{0}_{1}_Resolved".format(wp, channel),
               #                                                         cut=[ op.rng_len(bJets_resolved_PassdeepflavourWP) > 1, op.rng_len(bJets_boosted_PassdeepflavourWP) == 0] ),
               #     "DeepCSV{0}".format(wp)     :  lljjSelections["resolved"].refine("TwoLeptonsTwoBjets_NoMETcut_NobTagEventWeight_DeepCSV{0}_{1}_Resolved".format(wp, channel),
               #                                                         cut=[ op.rng_len(bJets_resolved_PassdeepcsvWP) > 1, op.rng_len(bJets_boosted_PassdeepcsvWP) == 0])
               #                             }
    
               # TwoLeptonsOneBjets_NoMETCut_NobTagEventWeight_Boo = {
               #     "DeepCSV{0}".format(wp)     :  lljjSelections["boosted"].refine("TwoLeptonsOneBjets_NoMETcut_NobTagEventWeight_DeepCSV{0}_{1}_Boosted".format(wp, channel),
               #                                                         cut=[ op.rng_len(bJets_boosted_PassdeepcsvWP) > 0 ] )
               #                             }
                    
               ###########################
                # ADD PROCESS SPLITTING
               ###########################
                LeptonsPlusBjets_NoMETCut_NobTagEventWeight_Res = {
                        "gg_fusion": {
                                    "DeepFlavour{0}".format(wp) :  lljjSelections["resolved"].refine("TwoLeptonsExactlyTwoBjets_NoMETcut_NobTagEventWeight_DeepFlavour{0}_{1}_Resolved".format(wp, channel),
                                                                        cut=[ op.rng_len(bJets_resolved_PassdeepflavourWP) == 2 ] ),
                                    "DeepCSV{0}".format(wp)     :  lljjSelections["resolved"].refine("TwoLeptonsExactlyTwoBjets_NoMETcut_NobTagEventWeight_DeepCSV{0}_{1}_Resolved".format(wp, channel),
                                                                        cut=[ op.rng_len(bJets_resolved_PassdeepcsvWP) == 2, op.rng_len(bJets_boosted_PassdeepcsvWP) == 0]) },
                        "bb_associatedProduction": {
                                    "DeepFlavour{0}".format(wp) :  lljjSelections["resolved"].refine("TwoLeptonsAtLeast3Bjets_NoMETcut_NobTagEventWeight_DeepFlavour{0}_{1}_Resolved".format(wp, channel),
                                                                        cut=[ op.rng_len(bJets_resolved_PassdeepflavourWP) >= 3] ),
                                    "DeepCSV{0}".format(wp)     :  lljjSelections["resolved"].refine("TwoLeptonsAtLeast3Bjets_NoMETcut_NobTagEventWeight_DeepCSV{0}_{1}_Resolved".format(wp, channel),
                                                                        cut=[ op.rng_len(bJets_resolved_PassdeepcsvWP) >= 3, op.rng_len(bJets_boosted_PassdeepcsvWP) == 0]) },
                            }
    
                LeptonsPlusBjets_NoMETCut_NobTagEventWeight_Boo = {
                        "gg_fusion": {
                                    "DeepCSV{0}".format(wp)     :  lljjSelections["boosted"].refine("TwoLeptonsAtLeast1FatBjets_NoMETcut_NobTagEventWeight_DeepCSV{0}_{1}_Boosted".format(wp, channel),
                                                                        cut=[ op.rng_len(bJets_boosted_PassdeepcsvWP) == 1, op.rng_len(bJets_resolved_PassdeepcsvWP) == 0] ) },
                        "bb_associatedProduction": {
                                    "DeepCSV{0}".format(wp)     :  lljjSelections["boosted"].refine("TwoLeptonsAtLeast1FatBjets_with_AtLeast1AK4_NoMETcut_NobTagEventWeight_DeepCSV{0}_{1}_Boosted".format(wp, channel),
                                                                        cut=[ op.OR( op.AND(op.rng_len(bJets_boosted_PassdeepcsvWP) >= 2 , op.rng_len(bJets_resolved_PassdeepcsvWP) == 0),
                                                                                     op.AND(op.rng_len(bJets_boosted_PassdeepcsvWP) >= 1 , op.rng_len(bJets_resolved_PassdeepcsvWP) >= 1)
                                                                                     )] )},
                            }
                
                
                
                
                llbbSelections_NoMETCut_NobTagEventWeight = { "gg_fusion":{ "resolved": LeptonsPlusBjets_NoMETCut_NobTagEventWeight_Res["gg_fusion"],
                                                                            "boosted" : LeptonsPlusBjets_NoMETCut_NobTagEventWeight_Boo["gg_fusion"] },
                                                              "bb_associatedProduction":{ "resolved": LeptonsPlusBjets_NoMETCut_NobTagEventWeight_Res["bb_associatedProduction"], 
                                                                                          "boosted" : LeptonsPlusBjets_NoMETCut_NobTagEventWeight_Boo["bb_associatedProduction"] }
                                                              }
                
                for process, allsel_fortaggerWp_per_reg_and_process in llbbSelections_NoMETCut_NobTagEventWeight.items():
                    for reg,  dic_selections in allsel_fortaggerWp_per_reg_and_process.items():
                        for key, sel in dic_selections.items():
                            yield_object.addYields(sel, f"has2Lep2{reg.upper()}BJets_NoMETCut_NobTagEventWeight_{channel}_{key}_{process}",
                                    f"{process}: 2 Lep(OS)+ {jlenOpts[reg]} {lljj_jetType[reg]}BJets {reg} pass {key}+ NoMETCut+ NobTagEventWeight(channel: {optstex})")
                
                
                llbbSelections_NoMETCut_bTagEventWeight = { process: 
                                                                { reg: 
                                                                    { key: selNobTag.refine(f"TwoLeptonsTwoBjets_NoMETCut_bTagEventWeight_{key}_{channel}_{reg}_{process}", weight = (run2_bTagEventWeight_PerWP[process][reg][key] if isMC else None))
                                                                    for key, selNobTag in NobTagEventWeight_selections_per_tagger.items() }
                                                                for reg, NobTagEventWeight_selections_per_tagger in NobTagEventWeight_selections_per_process.items()}
                                                            for process, NobTagEventWeight_selections_per_process in llbbSelections_NoMETCut_NobTagEventWeight.items() 
                                                        }
                llbbSelections_noMETCut = llbbSelections_NoMETCut_bTagEventWeight
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    #  to optimize the MET cut 
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # you should get them for both signal && bkg  
                if make_METPlots:
                    for process , Selections_noMETCut_per_process in llbbSelections_noMETCut.items():
                        for reg, sel in Selections_noMETCut_per_process.items():
                            plots.extend(MakeMETPlots(sel, corrMET, MET, channel, reg, process))
                            plots.extend(MakeExtraMETPlots(sel, dilepton, MET, channel, reg, process))
                
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    #  refine previous selections for SR : with MET cut  < 80. 
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                llbbSelections = { process: 
                                        { reg:
                                            { key: selNoMET.refine(f"TwoLeptonsTwoBjets_METCut_bTagEventWeight_{key}_{channel}_{reg}_{process}", cut=[ corrMET.pt < 80. ])
                                            for key, selNoMET in noMETSels.items() }
                                        for reg, noMETSels in llbbSelections_noMETCut_per_process.items() }
                                    for process, llbbSelections_noMETCut_per_process in llbbSelections_noMETCut.items() 
                                }
                
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                        # Evaluate the training  
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if self.doEvaluate:
                    plotOptions = utils.getOpts(channel)
                    signal_grid = { 'seen_byDNN': masses_seen,
                                    'notseen_byDNN': masses_notseen }
                    if self.BeBlind:
                        plotOptions["blinded-range"] = [0.6, 1.0] 

                    for process, Selections_per_process in llbbSelections.items():
                        for key, selections in Selections_per_process.items(): 
                            for TAGWP, sel in selections.items():
                                
                                bjets_  = safeget(lljj_bJets[key],TAGWP.replace(wp,''), wp)
                                
                                jj_p4   = ( (bjets_[0].p4 + bjets_[1].p4) if key=="resolved" else( bjets_[0].p4))
                                lljj_p4 = ( dilepton[0].p4 + dilepton[1].p4 + jj_p4)
                                
                                bb_M   = jj_p4.M()
                                llbb_M = lljj_p4.M()
    
                                for k, val in signal_grid.items():
                                    for parameters in val: 
                                        mA= parameters[1]
                                        mH= parameters[0]
                                        DNN_Inputs= [bb_M,llbb_M,op.c_float(mA),op.c_float(mH)]
                                        DNN_Output = ZAmodel(*DNN_Inputs) # [DY, TT, ZA]
                                        mA=str(mA).replace('.','p')
                                        mH=str(mH).replace('.','p')
                                        plots.append(Plot.make1D(f"DNNOutput_{channel}channel_{key}selection_{TAGWP}_withmetCut_ZAscan_{process}_MA_{mA}_MH_{mH}", 
                                            DNN_Output[2], sel, 
                                            EqB(50, 0., 1.), 
                                            title='DNN_Output ZA', plotopts=plotOptions))
                                            
                                        plots.append(Plot.make2D(f"mbbInput_vs_DNNOutput_{channel}channel_{key}selection_{TAGWP}_withmetCut_ZAscan_{process}_MA_{mA}_MH_{mH}",
                                            (bb_M, DNN_Output[2]), sel,
                                            (EqB(50, 0., 1000.), EqB(10, 0., 1.)),
                                            title="mbb mass Input vs DNN Output", plotopts=plotOptions))
                                        plots.append(Plot.make2D(f"mllbbInput_vs_DNNOutput_{channel}channel_{key}selection_{TAGWP}_withmetCut_ZAscan_{process}_MA_{mA}_MH_{mH}",
                                            (llbb_M, DNN_Output[2]), sel,
                                            (EqB(50, 0., 1000.), EqB(10, 0., 1.)),
                                            title="mllbb mass Input vs DNN Output", plotopts=plotOptions))
                        
                                        #OutmaxIDx =op.rng_max_element_index(DNN_Output)
                                        #trainSel= sel['DeepCSVM'].refine(f'DNN_On{node}node_llbb_{channel}_{key}selection_withmetcut_MA_{mA}_MH_{mH}',cut=[OutmaxIDx == op.c_int(i)])                
                                        #plots.append(Plot.make1D(f"DNNOutput_trainSel_{node}node_ll{channel}_jj{key}_btaggedDeepcsvM_withmetCut_scan_MA{mA}_MH{mH}", DNN_Output[i], trainSel,
                                        #    EqB(50, 0., 1.), title='DNN_Output %s'%node, plotopts=plotOptions))
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    #  TTbar Esttimation  
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if make_ttbarEstimationPlots:
                    # High met is Only included in this part for ttbar studies 
                    for process, Selections_per_process in llbbSelections.items():
                        for metReg, sel in {
                                "METCut" : Selections_per_process["resolved"],
                                "HighMET": {key: selNoMET.refine("TwoLeptonsTwoBjets_{0}_{1}_Resolved_with_inverted_METcut".format(key, channel),
                                    cut=[ corrMET.pt > 80. ])
                                    for key, selNoMET in llbbSelections_noMETCut[process]["resolved"].items() }
                                }.items():
                            plots.extend(makeHistosForTTbarEstimation(sel, dilepton, bjets_resolved, wp, channel, "resolved", metReg, process))
                
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    #  Control Plots for  Final selections
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                llbb_metCut_forPlots = {}
                if make_bJetsPlusLeptonsPlots_METcut :
                    llbb_metCut_forPlots["METCut"] = llbbSelections
                if make_bJetsPlusLeptonsPlots_NoMETcut :
                    llbb_metCut_forPlots["NoMETCut"] = llbbSelections_noMETCut
                for metCutNm, metCutSelections_llbb in llbb_metCut_forPlots.items():
                    bJER_status = "bJetER" if self.dobJetER else "NobJetER"
                    metCutNm_   = f"_{metCutNm}_{bJER_status}"
                    
                    for process, metCutSelections_llbb_per_process in metCutSelections_llbb.items():
                        for reg, selDict in metCutSelections_llbb_per_process.items():
                            bjets = lljj_bJets[reg]
                            
                            if make_FinalSelControlPlots:
                                plots.extend(makeBJetPlots(selDict, bjets, wp, channel, reg, metCutNm_, era, process))
                                plots.extend(makeControlPlotsForFinalSel(selDict, bjets, dilepton, wp, channel, reg, metCutNm_, process))

                            if make_PlotsforCombinedLimits:
                                plots.extend(makerhoPlots(selDict, bjets, dilepton, self.ellipses, self.ellipse_params, reg, metCutNm_, wp, channel, self.BeBlind, process))
                                plots.extend(MHMAforCombinedLimits( selDict, bjets, dilepton, wp, channel, reg, self.BeBlind, process))

                            if make_ellipsesPlots:
                                plots.extend(MakeEllipsesPLots(selDict, bjets, dilepton, wp, channel, reg, metCutNm_, process))

                            for key, sel in selDict.items():
                                yield_object.addYields(sel, f"has2Lep2{reg.upper()}BJets_{metCutNm}_{channel}_{key}_{process}",
                                        f"{process}: 2 Lep(OS)+ {jlenOpts[reg]} {lljj_jetType[reg]}BJets {reg} pass {key}+ {metCutNm}+ bTagEventWeight(channel: {optstex})")
                                
                                selections_for_cutflowreport.append(sel)
            
                for process in ['gg_fusion', 'bb_associatedProduction']:
                    plots.extend(makeExtraFatJetBOostedPlots(llbbSelections[process]['boosted'], lljj_bJets['boosted'], wp, channel, 'withmetCut', process))
        
        plots.append(CutFlowReport("Yields", selections_for_cutflowreport))
        plots.extend(yield_object.returnPlots())
        
        return plots

    def postProcess(self, taskList, config=None, workdir=None, resultsdir=None):
        # run plotIt as defined in HistogramsModule - this will also ensure that self.plotList is present
        super(NanoHtoZA, self).postProcess(taskList, config, workdir, resultsdir)

        from bamboo.plots import CutFlowReport, DerivedPlot
        from utils import normalizeAndMergeSamplesForCombined
        import bambooToOls
        import json 

        # memory usage
        #start= timer()
        #end= timer()
        #maxrssmb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
        #logger.info(f"{len(self.plotList):d} plots defined in {end - start:.2f}s, max RSS: {maxrssmb:.2f}MB")
        #with open(os.path.join(resultsdir=".","memoryusage.json"%suffix), "w") as handle:
        #    json.dump(len(self.plotList), handle, indent=4)
        #    json.dump(maxrssmb, handle, indent=4)
        #    json.dump(end - start, handle, indent=4)

        plotstoNormalized = []
        for plots in self.plotList:
            if plots.name.startswith('rho_steps_') or plots.name.startswith('jj_M_') or plots.name.startswith('lljj_M_') or plots.name.startswith('DNNOutput_'):
                plotstoNormalized.append(plots)
        if not os.path.isdir(os.path.join(resultsdir, "normalizedForCombined")):
            os.makedirs(os.path.join(resultsdir,"normalizedForCombined"))
        normalizeAndMergeSamplesForCombined(plotstoNormalized, self.readCounters, config, resultsdir, os.path.join(resultsdir, "normalizedForCombined"))
        
        # save generated-events for each samples--- > mainly needed for the DNN
        plotList_cutflowreport = [ ap for ap in self.plotList if isinstance(ap, CutFlowReport) ]
        bambooToOls.SaveCutFlowReports(config, plotList_cutflowreport, resultsdir, self.readCounters)

        plotList_2D = [ ap for ap in self.plotList if ( isinstance(ap, Plot) or isinstance(ap, DerivedPlot) ) and len(ap.binnings) == 2 ]
        logger.debug("Found {0:d} plots to save".format(len(plotList_2D)))

        from bamboo.analysisutils import loadPlotIt
        #p_config, samples, plots_2D, systematics, legend = loadPlotIt(config, plotList_2D, eras=self.args.eras, workdir=workdir, resultsdir=resultsdir, readCounters=self.readCounters, vetoFileAttributes=self.__class__.CustomSampleAttributes, plotDefaults=self.plotDefaults)
        p_config, samples, plots_2D, systematics, legend = loadPlotIt(config, plotList_2D, eras=None, workdir=workdir, resultsdir=resultsdir, readCounters=self.readCounters, vetoFileAttributes=self.__class__.CustomSampleAttributes, plotDefaults=self.plotDefaults)
        from plotit.plotit import Stack
        from bamboo.root import gbl
        for plot in plots_2D:
            if ('_2j_jet_pt_eta_') in plot.name  or plot.name.startswith('pair_lept_2j_jet_pt_vs_eta_'):
                expStack = Stack(smp.getHist(plot) for smp in samples if smp.cfg.type == "MC")
                cv = gbl.TCanvas(f"c{plot.name}")
                cv.cd(1)
                expStack.obj.Draw("COLZ0")
                cv.Update()
                cv.SaveAs(os.path.join(resultsdir, f"{plot.name}.png"))
            else:
                logger.debug(f"Saving plot {plot.name}")
                obsStack = Stack(smp.getHist(plot) for smp in samples if smp.cfg.type == "DATA")
                expStack = Stack(smp.getHist(plot) for smp in samples if smp.cfg.type == "MC")
                cv = gbl.TCanvas(f"c{plot.name}")
                cv.Divide(2)
                cv.cd(1)
                expStack.obj.Draw("COLZ0")
                cv.cd(2)
                obsStack.obj.Draw("COLZ0")
                cv.Update()
                cv.SaveAs(os.path.join(resultsdir, f"{plot.name}.png"))
