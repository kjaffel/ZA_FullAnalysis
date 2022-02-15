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

from bamboo import treefunctions as op
from bamboo.analysismodules import NanoAODModule, NanoAODHistoModule, HistogramsModule
from bamboo.analysisutils import makeMultiPrimaryDatasetTriggerSelection
from bamboo.analysisutils import configureJets, configureType1MET, configureRochesterCorrection
from bamboo.root import gbl, addIncludePath, loadHeader

zaPath = os.path.dirname(__file__)
if zaPath not in sys.path: sys.path.append(zaPath)

import utils as utils
import corrections as corr
import ControlPLots as cp
logger = utils.ZAlogger(__name__)
from EXtraPLots import * 
from boOstedEvents import get_DeepDoubleXDeepBoostedJet, get_BoostedEventWeight


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

        self.doSysts          = self.args.systematic
        self.doEvaluate       = self.args.DNN_Evaluation
        self.doSplitJER       = self.args.splitJER
        self.doSplitJES       = self.args.splitJES
        self.doHLT            = self.args.hlt
        self.doBlinded        = self.args.blinded
        self.doNanoAODversion = self.args.nanoaodversion
        self.doMETT1Smear     = self.args.doMETT1Smear
        self.dobJetER         = self.args.dobJetEnergyRegression
        self.doYields         = self.args.yields
        self.doSkim           = self.args.skim
        
        self.doPass_bTagEventWeight = False
        self.CleanJets_fromPileup   = False
        self.doDY_reweighting       = False
        self.doSplit_DYWeights      = False
        self.doTop_reweighting      = False
        self.qcdScaleVarMode        = "separate"  # "separate" : (muR/muF variations)  or combine : (7-point envelope)
        self.pdfVarMode             = "simple"    # simple  : (event-based envelope) (only if systematics enabled)
                                                  # or full : PDF uncertainties (100 histogram variations) 
    def addArgs(self, parser):
        super(NanoHtoZABase, self).addArgs(parser)
        parser.add_argument("-s", "--systematic", action="store_true", help="Produce systematic variations")
        parser.add_argument("-dnn", "--DNN_Evaluation", action="store_true", help="Pass TensorFlow model and evaluate DNN output")
        parser.add_argument("--splitJER", action="store_true", default= False, help="breakup into 6 nuisance parameters per year (correlated among all jets in all events per year, but uncorrelated across years), useful for analysis that are sensitive to JER, i.e. analyses that are able to constrain the single JER nuisance parameter per year w.r.t. their assigned uncertainty")
        parser.add_argument("--splitJES", action="store_true", default= False, help="Run 2 reduced set of JES uncertainty splited by sources")
        parser.add_argument("--hlt", action="store_true", help="Produce HLT efficiencies maps")
        parser.add_argument("--blinded", action="store_true", help="Options to be blind on data if you want to Evaluate the training OR The Ellipses model ")
        parser.add_argument("--nanoaodversion", default="v8", choices = ["v9", "v8", "v7", "v5"], help="version NanoAODv2(== v8 == ULegacy) and NanoAODvv9(== ULeagacy), the rest is pre-Legacy(== EOY) ")
        parser.add_argument("--process", required=False, nargs="+", choices = ["ggH", "bbH"], help="signal process that you wanna to look to ")
        parser.add_argument("--doMETT1Smear", action="store_true", default = False, help="do T1 MET smearing")
        parser.add_argument("--dobJetEnergyRegression", action="store_true", default = False, help="apply b jets energy regreqqion to improve the bjets mass resolution")
        parser.add_argument("--yields", action="store_true", default = False, help=" add Yields Histograms: not recomended if you turn off the systematics, jobs may run out of memory")
        parser.add_argument("--skim", action="store_true", default = False, help="make skim instead of plots")
        parser.add_argument("--backend", type=str, default="dataframe", help="Backend to use, 'dataframe' (default) or 'lazy' or 'compile' for debug mode")

    def customizeAnalysisCfg(self, config=None):
        if self.args.distributed == "driver" or not self.args.distributed:
            os.system('(git log -n 1;git diff .) &> %s/git.log' % self.args.output)
            #with open(os.path.join(self.args.output, "config.yml"), "w+") as backupCfg:
            #    yaml.dump(config, backupCfg)

    def prepareTree(self, tree, sample=None, sampleCfg=None):
        era  = sampleCfg.get("era") if sampleCfg else None
        isMC = self.isMC(sample)
        preVFPruns  = ["2016B", "2016C", "2016D", "2016E", "2016F"]
        postVFPruns = ["2016G", "2016H"]

        if self.doNanoAODversion in ["v8", "v9"]:
            self.isULegacy = True
            metName   = "MET"
        else:
            self.isULegacy = False
            metName   = "METFixEE2017" if era == "2017" else "MET"
        
        from bamboo.treedecorators import NanoAODDescription, nanoRochesterCalc, nanoJetMETCalc, nanoJetMETCalc_METFixEE2017, CalcCollectionsGroups, nanoFatJetCalc
        nanoJetMETCalc_both = CalcCollectionsGroups(Jet=("pt", "mass"), systName="jet", changes={metName: (f"{metName}T1", f"{metName}T1Smear")}, **{metName: ("pt", "phi")})
        nanoJetMETCalc_data = CalcCollectionsGroups(Jet=("pt", "mass"), systName="jet", changes={metName: (f"{metName}T1",)}, **{metName: ("pt", "phi")})
        
        if self.doMETT1Smear: nanoJetMETCalc_var = nanoJetMETCalc_both if isMC else nanoJetMETCalc_data
        else: nanoJetMETCalc_var = nanoJetMETCalc
        
        if self.isULegacy: nanoJetMETCalc_ = nanoJetMETCalc_var
        else: nanoJetMETCalc_ = nanoJetMETCalc_METFixEE2017 if era == "2017" else nanoJetMETCalc_var

        tree,noSel,be,lumiArgs = NanoAODHistoModule.prepareTree(self, tree, sample=sample, sampleCfg=sampleCfg, 
                                            description=NanoAODDescription.get("v7", year=(era if "VFP" not in era else "2016"), 
                                                                                isMC=isMC, 
                                                                                systVariations=[ nanoRochesterCalc, nanoJetMETCalc_, nanoFatJetCalc ]), 
                                                                                backend=self.args.backend ) 
        #############################################################
        # Ellipses :
        #############################################################
        loadHeader(os.path.abspath(os.path.join(zaPath, "include/masswindows.h")))

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
        #############################################################
        
        isNotWorker = (self.args.distributed != "worker") 
        era_ = '2016' if 'VFP' in era else era
        
        roccor = {'2016-preVFP' : "RoccoR2016aUL.txt", 
                  '2016-postVFP': "RoccoR2016aUL.txt",
                  '2017'        : "RoccoR2017UL.txt",
                  '2018'        : "RoccoR2018UL.txt"
                  }
        configureRochesterCorrection(tree._Muon, os.path.join(os.path.dirname(__file__), "data/roccor.Run2.v5", roccor[era]), isMC=isMC, backend=be, uName=sample)
        
        #############################################################
        ## Configure Jet Energy corrections and Jets Energy resolutions 
        # JEC's Recommendation for Full RunII: https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC
        # JER : -----------------------------: https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
        # list of supported para in JER : https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyResolution#List_of_supported_parameters 
        # github : https://github.com/cms-jet/JRDatabase/tree/master/textFiles
        ## Configure Type 1 MET corrections
        #############################################################
        if self.isMC(sample):
            if self.doSplitJES:
                jesUncertaintySources = ['Absolute', f'Absolute_{era_}', 'BBEC1', f'BBEC1_{era_}', 'EC2', f'EC2_{era_}', 'FlavorQCD', 'HF', f'HF_{era_}', 'RelativeBal', f'RelativeSample_{era_}']
            else:
                jesUncertaintySources = ["Total"]
            JECs = {'2016-preVFP' : "Summer19UL16APV_V7_MC",
                    '2016-postVFP': "Summer19UL16_V7_MC",
                    '2017'        : "Summer19UL17_V5_MC", 
                    '2018'        : "Summer19UL18_V5_MC"
                    }
            
            JERs = {'2016-preVFP' : "Summer20UL16APV_JRV3_MC", 
                    '2016-postVFP': "Summer20UL16_JRV3_MC",
                    '2017'        : "Summer19UL17_JRV3_MC",
                    '2018'        : "Summer19UL18_JRV2_MC"
                    }
        else:
            jesUncertaintySources = None
            JECs = {'2016-preVFP' : "Summer19UL16APV_RunBCDEF_V7_DATA", 
                    '2016-postVFP': "Summer19UL16_RunFGH_V7_DATA", 
                    '2017'        : "Summer19UL17_RunBCDEF_V5_DATA",
                    '2018'        : "Summer19UL18_V5_DATA",
                    }
            
            JERs = {'2016-preVFP' : "Summer20UL16APV_JRV3_DATA", 
                    '2016-postVFP': "Summer20UL16_JRV3_DATA", 
                    '2017'        : "Summer19UL18_JRV2_DATA",
                    '2018'        : "Summer19UL18_JRV2_DATA",
                    }
        
        cmJMEArgs = {
                "jec": JECs[era],
                "smear": JERs[era],
                "splitJER": self.doSplitJER,
                "jesUncertaintySources": jesUncertaintySources,
                #"jecLevels":[], #  default : L1FastJet, L2Relative, L3Absolute, and also L2L3Residual for data
                #"regroupTag": "V2",
                "addHEM2018Issue": (era == "2018"),
                "mayWriteCache": isNotWorker,
                "isMC": isMC,
                "backend": be,
                "uName": sample
                }
        configureJets(tree._Jet, "AK4PFchs", **cmJMEArgs)
        configureJets(tree._FatJet, "AK8PFPuppi", mcYearForFatJets=(era if "VFP" not in era else "2016"), **cmJMEArgs)
    
        if self.doMETT1Smear:
            if isMC:
                configureType1MET(getattr(tree, f"_{metName}T1Smear"), isT1Smear=True, **cmJMEArgs)
            del cmJMEArgs["uName"]
            configureType1MET(getattr(tree, f"_{metName}T1"), enableSystematics=((lambda v : not v.startswith("jer")) if isMC else None), uName=f"{sample}NoSmear", **cmJMEArgs)
        else:
            configureType1MET(getattr(tree, f"_{metName}"), **cmJMEArgs)
        
        #############################################################
        # triggers path 
        #############################################################
        triggersPerPrimaryDataset = {}
        if "2016" in era:
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

        elif era == "2017":
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
                #"SingleMuon"    : [ tree.HLT.IsoMu27,
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
        elif era == "2018":
            suffix    = "_UL" if self.isULegacy else "_"
            eraInYear = "" if isMC else next(tok for tok in sample.split(suffix) if tok.startswith(era))[4:]
            triggersPerPrimaryDataset = corr.catchHLTforSubPrimaryDataset(era, eraInYear, tree, isMC=isMC)
        
        #############################################################
        if self.isMC(sample):
            # remove double counting passing TTbar Inclusive + TTbar Full Leptonic ==> mainly for 2016 Analysis 
            sampleCut = None
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
                logger.info("Adding QCD scale variations, ISR , FSR and PDFs")
                noSel = utils.addTheorySystematics(self, sample, sampleCfg, tree, noSel, qcdScale=True, PSISR=True, PSFSR=True, PDFs=False, pdf_mode=self.pdfVarMode)
        else:
            noSel = noSel.refine("withTrig", cut=(makeMultiPrimaryDatasetTriggerSelection(sample, triggersPerPrimaryDataset)))
         
        return tree,noSel,be,lumiArgs
   
    def defineObjects(self, t, noSel, sample=None, sampleCfg=None):
        from bamboo.analysisutils import forceDefine
        from bamboo.plots import Skim
        from bamboo.plots import EquidistantBinning as EqB
        from bamboo import treefunctions as op
        
        from bambooToOls import Plot
        from METFilter_xyCorr import METFilter, METcorrection, ULMETXYCorrection
        from reweightDY import Plots_gen

        def getIDX(wp = None):
            return (0 if wp=="L" else ( 1 if wp=="M" else 2))
        
        def getOperatingPoint(wp = None):
            return ("Loose" if wp == 'L' else ("Medium" if wp == 'M' else "Tight"))
        
        isMC = self.isMC(sample)
        era  = sampleCfg.get("era") if sampleCfg else None
        era_ = era if "VFP" not in era else "2016"
        
        noSel = noSel.refine("passMETFlags", cut=METFilter(t.Flag, era, isMC) )
        ##################################################
        # Pileup 
        ##################################################
        if self.isMC(sample):
            self.PUWeight = corr.makePUWeight(t, era, noSel)
            noSel = noSel.refine("puWeight", weight=corr.makePUWeight(t, era, noSel))
        
        ###############################################
        # Muons ID , ISO and RECO cuts and scale factors 
        # Working Point for 2016- 2017 -2018 : medium-identification  and tight-isolation 
        # https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Muon_Isolation
        ###############################################
        forceDefine(t._Muon.calcProd, noSel)
        
        #To suppress nonprompt leptons, the impact parameter in three dimensions of the lepton track, with respect to the primaryvertex, is required to be less than 4 times its uncertainty (|SIP3D|<4)
        sorted_muons = op.sort(t.Muon, lambda mu : -mu.pt)
        muons = op.select(sorted_muons, lambda mu : op.AND(mu.pt > 15., op.abs(mu.eta) < 2.4, mu.mediumId, mu.pfRelIso04_all<0.15, op.abs(mu.sip3d) < 4.))

        muMediumIDSF = corr.getScaleFactor(era, noSel, "muon_ID", "muid_medium", defineOnFirstUse=True)
        muTightIsoSF = corr.getScaleFactor(era, noSel, "muon_iso", "muiso_tight", defineOnFirstUse=True)
        muTriggerSF  = corr.getScaleFactor(era, noSel, "muon_trigger", "mu_trigger", defineOnFirstUse=True)
        ###############################################
        # Electrons : ID , RECO cuts and scale factors
        # Wp  // 2016: Electron_cutBased_Sum16==3  -> medium     // 2017 -2018  : Electron_cutBased ==3   --> medium ( Fall17_V2)
        # asking for electrons to be in the Barrel region with dz<1mm & dxy< 0.5mm   //   Endcap region dz<2mm & dxy< 0.5mm 
        # cut-based ID Fall17 V2 the recommended one from POG for the FullRunII
        ###############################################
        sorted_electrons = op.sort(t.Electron, lambda ele : -ele.pt)
        electrons = op.select(sorted_electrons, lambda ele : op.AND(ele.pt > 20., op.abs(ele.eta) < 2.5 , ele.cutBased>=3, op.abs(ele.sip3d) < 4., 
                                                                    op.OR(op.AND(op.abs(ele.dxy) < 0.05, op.abs(ele.dz) < 0.1), 
                                                                          op.AND(op.abs(ele.dxy) < 0.05, op.abs(ele.dz) < 0.2) ))) 
        #def elRecoSF(el):
        #    lowpt_ele_reco  = corr.getScaleFactor(era, noSel, "electron_reco", "highpt_ele_reco", wp= "RecoBelow20", defineOnFirstUse=True)
        #    highpt_ele_reco = corr.getScaleFactor(era, noSel, "electron_reco", "highpt_ele_reco", wp= "RecoAbove20", defineOnFirstUse=True)
        #    return op.multiSwitch( ( el.pt < 20. , lowpt_ele_reco), ( el.pt > 20. , highpt_ele_reco), op.c_float(1.))
        
        elRecoSF     = corr.getScaleFactor(era, noSel, "electron_reco", "highpt_ele_reco", wp="Medium", defineOnFirstUse=True)
        elMediumIDSF = corr.getScaleFactor(era, noSel, "electron_ID", "elid_medium", wp="Medium", defineOnFirstUse=True)
        #elTriggerSF = corr.getScaleFactor(era, noSel, "electron_trigger", "ele_trigger", defineOnFirstUse=True)
        
        ###############################################
        # MET 
        ###############################################
        MET = t.MET if self.isULegacy else (t.MET if era != "2017" else (t.METFixEE2017))
        PuppiMET = t.PuppiMET 
        if self.isULegacy:
            corrMET = ULMETXYCorrection(MET,t.PV,sample,f"UL{era_}",self.isMC(sample))
        else:
            corrMET = METcorrection(MET,t.PV,sample,era,self.isMC(sample))
        
        ###############################################
        # AK4 Jets selections
        # 2016 - 2017 - 2018   ( j.jetId &2) ->      tight jet ID
        # For 2017 data, there is the option of "Tight" or "TightLepVeto", 
        # depending on how much you want to veto jets that overlap with/are faked by leptons
        ###############################################
        deltaR = 0.4
        eta    = 2.4 if '2016' in era else 2.5
        pt     = 20. if '2016' in era else 30.

        jet_ID = { '2016-preVFP' : lambda j : j.jetId & 2, # tight
                   '2016-postVFP': lambda j : j.jetId & 2,
                   '2017'        : lambda j : j.jetId & 4,
                   '2018'        : lambda j : j.jetId & 4}
        
        puIdWP = "loose"
        jet_puID = { "loose"   : lambda j : j.jetpuId & 0x4,
                     "medium"  : lambda j : j.jetpuId & 0x2,
                     "tight"   : lambda j : j.jetpuId & 0x1 }
        
        sorted_AK4jets= op.sort(t.Jet, lambda j : -j.pt)
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
        if self.CleanJets_fromPileup :
            AK4jetsSel = op.select(sorted_AK4jets, lambda j : op.AND(j.pt > pt, op.abs(j.eta) < eta, jet_ID[era], op.switch(j.pt < 50, jet_puID[puIdWP], op.c_bool(True)))) 
        else:    
            AK4jetsSel = op.select(sorted_AK4jets, lambda j : op.AND(j.pt > pt, op.abs(j.eta) < eta, (jet_ID[era])))        
        
        # exclude from the jetsSel any jet that happens to include within its reconstruction cone a muon or an electron.
        AK4jets = op.select(AK4jetsSel, 
                            lambda j : op.AND(
                                            op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < deltaR )), 
                                            op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < deltaR ))))

        self.cleaned_AK4JetsByDeepFlav = op.sort(AK4jets, lambda j: -j.btagDeepFlavB)
        self.cleaned_AK4JetsByDeepB    = op.sort(AK4jets, lambda j: -j.btagDeepB)
        
        AK4jets_noptcutSel = op.select(sorted_AK4jets, lambda j : op.AND(op.abs(j.eta) < eta, jet_ID[era]))
        AK4jets_noptcut    = op.select(AK4jets_noptcutSel, 
                            lambda j : op.AND(
                                            op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < deltaR )), 
                                            op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < deltaR ))))
        
        if self.CleanJets_fromPileup:
            if self.isMC(sample):
                self.pu_weight = corr.makePUIDSF(AK4jets, era_, wp=puIdWP, wpToCut=jet_puID[puIdWP])
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
        
        self.cleaned_AK8JetsByDeepB = op.sort(AK8jets, lambda j: -j.btagDeepB)
        
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
        # Now,  let's ask for the jets to be a b tagged b-jets 
        # DeepCSV or DeepJet==DeepFlavour medium b-tagging working point
        # bjets ={ "DeepFlavour": {"L": ( pass loose, fail medium, fail tight), 
        #                          "M": ( pass loose, pass medium  fail tight), 
        #                          "T": ( pass tight, fail medium, fail loose)}     
        #          "DeepCSV"    : {"L": (  ----  you get the idea           ;), 
        #                          "M": (  ----                              ), 
        #                          "T": (  ----                              )} }
        ###############################################
        self.eoy_btagging_wpdiscr_cuts = {
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
        
        self.legacy_btagging_wpdiscr_cuts = {
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
        
        
        bjets_boosted      = {}
        bjets_resolved     = {}
        lightJets_boosted  = {}
        lightJets_resolved = {}
        
        # self.WorkingPoints = ["L", "M", "T"] 
        # For Boosted AK8Jets : DeepCSV available as b-tagger with WPs `cut on dicriminator` same as in resolved region for AK4Jets
        # .ie. only L and M are available !
        self.WorkingPoints = ["M"]
        
        nBr_subjets_passBtagDiscr = "atleast_1subjet_pass"
        nBr_light_subjets_NotpassBtagDiscr = "atleast_1subjet_notpass"
        
        for tagger  in self.legacy_btagging_wpdiscr_cuts.keys():
            
            bJets_AK4_deepflavour = {}
            bJets_AK4_deepcsv = {}
            bJets_AK8_deepcsv = {}
            
            lightJets_AK4_deepflavour = {}
            lightJets_AK4_deepcsv = {}
            lightJets_AK8_deepcsv = {}

            for wp in sorted(self.WorkingPoints):
                
                idx = getIDX(wp)
                wpdiscr_cut = self.legacy_btagging_wpdiscr_cuts[tagger][era][idx]

                key_fromscalefactors_libray = "btag_Summer19UL{}_106X".format(era_) if self.isULegacy else( "btag_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"))
                    
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
                    bJets_AK4_deepflavour[wp]     = op.select(self.cleaned_AK4JetsByDeepFlav, lambda j : j.btagDeepFlavB >= wpdiscr_cut )
                    lightJets_AK4_deepflavour[wp] = op.select(self.cleaned_AK4JetsByDeepFlav, lambda j : j.btagDeepFlavB < wpdiscr_cut)

                    bjets_resolved[tagger]     = bJets_AK4_deepflavour
                    lightJets_resolved[tagger] = lightJets_AK4_deepflavour
                
                elif tagger == "DeepCSV":
                    bJets_AK4_deepcsv[wp]     = op.select(self.cleaned_AK4JetsByDeepB, lambda j : j.btagDeepB >= wpdiscr_cut)   
                    lightJets_AK4_deepcsv[wp] = op.select(self.cleaned_AK4JetsByDeepB, lambda j : j.btagDeepB < wpdiscr_cut)   
                    
                    bJets_AK8_deepcsv[wp]     = op.select(self.cleaned_AK8JetsByDeepB, subjets_btag_req.get(nBr_subjets_passBtagDiscr))   
                    lightJets_AK8_deepcsv[wp] = op.select(self.cleaned_AK8JetsByDeepB, subjets_btag_req_onlightjets.get(nBr_light_subjets_NotpassBtagDiscr))
                    
                    bjets_resolved[tagger]     = bJets_AK4_deepcsv
                    bjets_boosted[tagger]      = bJets_AK8_deepcsv
                    lightJets_resolved[tagger] = lightJets_AK4_deepcsv
                    lightJets_boosted[tagger]  = lightJets_AK8_deepcsv
                    
        ########################################################
        # Zmass reconstruction : Opposite Sign , Same Flavour leptons
        ########################################################
        # supress quaronika resonances and jets misidentified as leptons
        LowMass_cut = lambda lep1, lep2: op.invariant_mass(lep1.p4, lep2.p4)>12.
        # Dilepton selection: opposite sign leptons in range 70.<mll<120. GeV 
        osdilep_Z  = lambda lep1,lep2 : op.AND(lep1.charge != lep2.charge, op.in_range(70., op.invariant_mass(lep1.p4, lep2.p4), 120.))
        osdilep    = lambda lep1,lep2 : op.AND(lep1.charge != lep2.charge)
        
        osLLRng = {
                "MuMu" : op.combine(muons, N=2, pred= osdilep_Z),
                "ElEl" : op.combine(electrons, N=2, pred= osdilep_Z),
               #"ElMu" : op.combine((electrons, muons), pred=lambda ele,mu : op.AND(LowMass_cut(ele, mu), osdilep(ele, mu) , ele.pt > mu.pt )),
               #"MuEl" : op.combine((muons, electrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), osdilep(ele, mu), mu.pt > ele.pt )),
                "MuEl" : op.combine((muons, electrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), osdilep(ele, mu))),
               #"2OSSFLep" : op.AND(op.combine(muons, N=2, pred= osdilep_Z), op.combine(electrons, N=2, pred= osdilep_Z)) 
                }
         
        hasOSLL_cmbRng = lambda cmbRng : op.AND(op.rng_len(cmbRng) > 0, cmbRng[0][0].pt > 25.) 
        
        ## helper selection (OR) to make sure jet calculations are only done once
        hasOSLL = noSel.refine("hasOSLL", cut=op.OR(*( hasOSLL_cmbRng(rng) for rng in osLLRng.values())))
       
        forceDefine(t._Jet.calcProd, hasOSLL)
        
        ########################################################
        metName = ("MET" if self.isULegacy else ("MET" if era != "2017" else "METFixEE2017"))
        if self.doMETT1Smear:
            if self.isMC(sample):
                forceDefine(getattr(t, f"_{metName}T1Smear").calcProd, hasOSLL)
            forceDefine(getattr(t, f"_{metName}T1").calcProd, hasOSLL)
        else:
            forceDefine(getattr(t, f"_{metName}").calcProd, hasOSLL)

        ########################################################
        # https://lathomas.web.cern.ch/lathomas/TSGStuff/L1Prefiring/PrefiringMaps_2016and2017/
        # https://twiki.cern.ch/twiki/bin/view/CMS/L1PrefiringWeightRecipe#Introduction
        # NANOAOD: The event weights produced by the latest version of the producer are included in nanoAOD starting from version V9. 
        # Lower versions include an earlier version of the ECAL prefiring weight and do not include the muon weights!
        ########################################################
        mumu_sf = []
        elmu_sf = []
        muel_sf = []
        elel_sf = []
        if isMC:
            if era != '2018':
                mumu_sf.append(corr.getL1PreFiringWeight(t))
                elmu_sf.append(corr.getL1PreFiringWeight(t))
                muel_sf.append(corr.getL1PreFiringWeight(t))
                elel_sf.append(corr.getL1PreFiringWeight(t))
            if era == '2017':
                HLTZvtx = op.systematic(op.c_float(0.991), name='HLTZvtx', up=op.c_float(0.001), down=op.c_float(0.001))
                elmu_sf.append(HLTZvtx)
                muel_sf.append(HLTZvtx)
                elel_sf.append(HLTZvtx)

            llSFs = { "MuMu" : (lambda ll : 
                        [ muMediumIDSF(ll[0]), muMediumIDSF(ll[1]), 
                          muTightIsoSF(ll[0]), muTightIsoSF(ll[1]), 
                          #doubleMuTrigSF(ll), muTriggerSF(ll[0]), muTriggerSF(ll[1]) 
                          ] + mumu_sf ),
                    #"ElMu" : (lambda ll : 
                    #  [ elMediumIDSF(ll[0]), muMediumIDSF(ll[1]), 
                    #    muTightIsoSF(ll[1]), 
                    #    elRecoSF(ll[0]), 
                    #    elemuTrigSF(ll) 
                    #    ] + elmu_sf ),
                    "MuEl" : (lambda ll : 
                        [ muMediumIDSF(ll[0]), muTightIsoSF(ll[0]),
                          elMediumIDSF(ll[1]), elRecoSF(ll[1]), 
                          #mueleTrigSF(ll), muTriggerSF(ll[0]),
                          ] + muel_sf ),                                       
                    "ElEl" : (lambda ll :
                        [ elMediumIDSF(ll[0]), elMediumIDSF(ll[1]), 
                          elRecoSF(ll[0]), elRecoSF(ll[1]), 
                          #doubleEleTrigSF(ll) 
                          ] + elel_sf )
                    }

        categories = dict( (channel, (catLLRng[0], 
                                      hasOSLL.refine("hasOs{0}".format(channel), 
                                                        cut=hasOSLL_cmbRng(catLLRng), 
                                                        weight=(llSFs[channel](catLLRng[0]) if isMC else None) 
                                                        ) 
                                      )) for channel, catLLRng in osLLRng.items())
        
        return noSel, categories, AK4jets, AK8jets, fatjets_nosubjettinessCut, bjets_resolved, bjets_boosted, electrons, muons, MET, corrMET, PuppiMET



class NanoHtoZA(NanoHtoZABase, HistogramsModule):
    def __init__(self, args):
        super(NanoHtoZA, self).__init__(args)
    #@profile
    # https://stackoverflow.com/questions/276052/how-to-get-current-cpu-and-ram-usage-in-python
    def definePlots(self, t, noSel, sample=None, sampleCfg=None):
        from bamboo.plots import VariableBinning as VarBin
        from bamboo.plots import Skim, CutFlowReport
        
        from bambooToOls import Plot
        from reweightDY import plotsWithDYReweightings, Plots_gen, PLots_withtthDYweight
    
        def getIDX(wp = None):
            return (0 if wp=="L" else ( 1 if wp=="M" else 2))
        
        def getOperatingPoint(wp = None):
            return ("Loose" if wp == 'L' else ("Medium" if wp == 'M' else "Tight"))
        
        def mass_to_str(m):
            return str(m).replace('.','p')
        
        def inputStaticCast(inputDict,cast='float'):
            return [op.static_cast(cast,v) for v in inputDict.values()]
        
        noSel, categories, AK4jets, AK8jets, fatjets_nosubjettinessCut, bjets_resolved, bjets_boosted, electrons, muons, MET, corrMET, PuppiMET = super(NanoHtoZA, self).defineObjects(t, noSel, sample, sampleCfg)
        
        era  = sampleCfg.get("era") if sampleCfg else None
        era_ = era if "VFP" not in era else "2016"
        
        yield_object = corr.makeYieldPlots()
        isMC = self.isMC(sample)
        binScaling = 1 
        
        onnx__version = False
        tf__version   = False
        
        plots = []
        selections_for_cutflowreport = []

        addIncludePath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "include"))
        loadHeader("BTagEffEvaluator.h")

        if self.doEvaluate:
            #ZAmodel_path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/tf_models/tf_bestmodel_max_eval_mean_trainResBoOv0_fbversion.pb'
            #ZAmodel_path = "/home/ucl/cp3/kjaffel/scratch/ul__results/test__4/model/tf_bestmodel.pb"
            #ZAmodel_path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/onnx_models/prob_model.onnx"
            #ZAmodel_path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/ul__results/work__1/keras_tf_onnx_models/all_combined_dict_343_model.pb"
            #ZAmodel_path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/ul__results/work__1/keras_tf_onnx_models/prob_model.onnx"
            #ZAmodel_path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/ML-Tools/keras_tf_onnx_models/prob_model_work__1.onnx"
            #ZAmodel_path = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/ul__results/work_nanov9__1/keras_tf_onnx_models/prob_model_work_nanov9__1.onnx"
            #ZAmodel_path  = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/ul__results/work_nanov9__1/keras_tf_onnx_models/all_combined_dict_241_model.onnx"
            ZAmodel_path  = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/ul__results/work_nanov9__1/ext1/keras_tf_onnx_models/all_combined_dict_216_model.pb"
            
            if ZAmodel_path.split('/')[-1].endswith('.onnx'):
                onnx__version = True
            elif ZAmodel_path.split('/')[-1].endswith('.pb'):
                tf__version   = True
            
            if not os.path.exists(ZAmodel_path):
                raise RuntimeError(f'Could not find model: {ZAmodel_path}')
            else:
                try:
                    #===============================================================================
                    # Tensorflow : The otherArgs keyword argument should be (inputNodeNames, outputNodeNames), 
                    # where each of the two can be a single string, or an iterable of them.
                    if tf__version:
                        outputs = 'Identity'
                        inputs  = ['l1_pdgId', 'era', 'bb_M', 'llbb_M', 'bb_M_squared','llbb_M_squared', 'bb_M_x_llbb_M', 'mA','mH', 'isResolved', 'isBoosted', 'isggH', 'isbbH']
                        ZA_mvaEvaluator = op.mvaEvaluator(ZAmodel_path,mvaType='Tensorflow',otherArgs=(inputs, outputs), nameHint='tf_ZAModel')
                    #===============================================================================
                    # ONNX : The otherArgs keyword argument should the name of the output node (or a list of those)
                    elif onnx__version:
                        ZA_mvaEvaluator = op.mvaEvaluator(ZAmodel_path, mvaType='ONNXRuntime',otherArgs=("out"), nameHint='ONNX_ZAModel')
                    #===============================================================================
                except Exception as ex:
                    raise RuntimeError(f'-- {ex} -- when op.mvaEvaluator model: {ZAmodel_path}.')

            bayesian_blocks = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/ul__combinedlimits/preapproval__6/rebinned_edges_bayesian_all.json"
            if not os.path.exists(bayesian_blocks):
                raise RuntimeError(f'Could not find model: {bayesian_blocks}')
            else:
                f = open(bayesian_blocks)
                bayesian_blocks_binnings = json.load(f)

        masses_seen = [
        #part0 : 21 signal samples 
        #( MH, MA)
        ( 200, 50),
        ( 200, 100), ( 200, 125),
        ( 250, 50),  ( 250, 100),
        ( 300, 50),  ( 300, 100), ( 300, 200),
        ( 500, 50),  ( 500, 200), ( 500, 300), ( 500, 400), (510, 130),
        ( 650, 50),  ( 609.21, 253.68), 
        ( 750, 610), 
        ( 800, 50), ( 800, 200), ( 800, 400), ( 800, 700),
        (1000, 50), (1000, 200), (1000, 500),    
        ]
        #part1
        masses_notseen = [
        #( 173.52,  72.01),  
        #( 209.90,  30.00), ( 209.90,  37.34), ( 261.40, 102.99), ( 261.40, 124.53),
        #( 296.10, 145.93), ( 296.10,  36.79),
        #( 379.00, 205.76), 
        #( 442.63, 113.53), ( 442.63,  54.67),( 442.63,  80.03), 
        #( 609.21, 298.01), 
        #( 717.96,  30.00), ( 717.96, 341.02), 
        #( 846.11, 186.51), ( 846.11, 475.64), ( 846.11,  74.80), 
        #( 997.14, 160.17), ( 997.14, 217.19), ( 997.14, 254.82), ( 997.14, 64.24) 
        ]

        make_ZpicPlots              = False 
        make_JetmultiplictyPlots    = False 
        make_JetschecksPlots        = False  # check the distance in deltaR of the closest electron to a given jet and a view more control histograms which might be of interest. 
        make_tau2tau1RatioPlots     = False
        make_JetsPlusLeptonsPlots   = False 
        make_DeepDoubleBPlots       = False 
        make_METPlots               = False
        make_METPuppiPlots          = False
        make_ttbarEstimationPlots   = False
        make_PlotsforCombinedLimits = False
        
        # One of these two at least should be "True" if you want to get the final sel plots (.ie. ll + bb )
        make_bJetsPlusLeptonsPlots_METcut   = True
        make_bJetsPlusLeptonsPlots_NoMETcut = False
        
        make_FinalSelControlPlots    = False 
        make_recoVerticesPlots       = False
        
        make_zoomplotsANDptcuteffect = False
        make_2017Checksplots         = False
        make_LookInsideJets          = False
        make_ExtraFatJetsPlots       = False
        make_DYReweightingPlots      = False 
        
        rebin_bayesian       = False
        rebin_uniform_50bins = True
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                               # more plots to invistagtes 2017 problems  
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if make_2017Checksplots :
            plots += choosebest_jetid_puid(t, muons, electrons, categories, era, sample, isMC)
        
        for channel, (dilepton, catSel) in categories.items():
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # Zmass (2Lepton OS && SF ) 
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            optstex = ('e^{+}e^{-}' if channel=="ElEl" else( '$\mu^+\mu^-$' if channel=="MuMu" else( '$\mu^+e^-$' if channel=="MuEl" else('$e^+\mu^-$'))))
            yield_object.addYields(catSel,"hasOs%s"%channel,"OS leptons+ M_{ll} cut(channel: %s)"%optstex)
            selections_for_cutflowreport.append(catSel)
            
            if make_ZpicPlots:
                #plots += varsCutsPlotsforLeptons(dilepton, catSel, channel)
                plots.extend(cp.makeControlPlotsForZpic(catSel, dilepton, 'oslepSel', channel, 'inclusive'))
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # Jets multiplicty  
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            if make_JetmultiplictyPlots :
                for jet, reg in zip ([AK4jets, AK8jets], ["resolved", "boosted"]):
                    plots.extend(cp.makeJetmultiplictyPlots(catSel, jet, channel,"_NoCutOnJetsLen_" + reg))
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # This's an Inclusive selection *** 
            #       boosted : at least 1 AK8jets  && resolved: at least 2 AK4jets  
            # I don't care about my CR if boosted and resolved are inclusive , what's matter for me is my SR  ** 
            # boosted is unlikely to have pu jets ; jet pt > 200 in the boosted cat 
            
            # gg fusion :  
            #              resolved :  exactly 2 AK4 b jets 
            #              boosted:    exactly 1 fat bjet
            # b-associated production : 
            #              resolved : at least 3 AK4 bjets 
            #              boosted: at least 1 fat bjets && 1 AK4 bjets
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            TwoLeptonsTwoJets_Resolved = catSel.refine(f"TwoJet_{channel}Sel_resolved", cut=[ op.rng_len(AK4jets) >= 2])
            TwoLeptonsOneJet_Boosted   = catSel.refine(f"OneJet_{channel}Sel_boosted", cut=[ op.rng_len(AK8jets) >= 1 ])
            
            if self.CleanJets_fromPileup:
                TwoLeptonsTwoJets_Resolved = TwoLeptonsTwoJets_Resolved.refine( f"TwoJet_{channel}Sel_resolved_inclusive_puWeight", weight= self.pu_weight)
            
            lljjSelections = { "resolved": TwoLeptonsTwoJets_Resolved,
                               "boosted" : TwoLeptonsOneJet_Boosted }
            
            jlenOpts       = { "resolved": 'at least 2',
                               "boosted" : 'at least 1'}
            
            lljj_jetType   = { "resolved": "AK4",
                               "boosted" : "AK8"}
            
            lljj_selName   = { "resolved": "has2Lep2ResolvedJets",
                               "boosted" : "has2Lep1BoostedJets"}
            
            lljj_jets      = { "resolved": AK4jets,
                               "boosted" : AK8jets }
                
            lljj_bJets     = { "resolved": bjets_resolved,
                               "boosted" : bjets_boosted }
        
            for regi, sel in lljjSelections.items():
                yield_object.addYields(sel, f"{lljj_selName[regi]}_{channel}" , f"2 Lep(OS)+ {jlenOpts[regi]} {lljj_jetType[regi]}Jets+ $M_{{ll}}$ cut(channel: {optstex})")
                selections_for_cutflowreport.append(sel)

            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            
            if make_zoomplotsANDptcuteffect:
                plots.extend(ptcuteffectOnJetsmultiplicty(catSel, dilepton, AK4jets_noptcut, AK4jets, corrMET, era, channel))
                plots.extend(zoomplots(catSel, lljjSelections["resolved"], dilepton, AK4jets, 'resolved', channel))
            
            if make_METPuppiPlots:
                plots.extend(cp.MakePuppiMETPlots(PuppiMET, lljjSelections["resolved"], channel))
            
            if make_LookInsideJets:
                plots.extend(LeptonsInsideJets(AK4jets, lljjSelections["resolved"], channel))

            if make_recoVerticesPlots:
                plots.extend( cp.makePrimaryANDSecondaryVerticesPlots(t, catSel, channel))
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                # Control Plots in boosted and resolved  
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            for reg, sel in lljjSelections.items():
                jet = lljj_jets[reg]
                if make_JetschecksPlots:
                    plots.extend(cp.makedeltaRPlots(sel, jet, dilepton, channel, reg))
                    plots.extend(cp.makeJetmultiplictyPlots(sel, jet, channel, reg))
                
                if make_JetsPlusLeptonsPlots:
                    plots.extend(cp.makeJetPlots(sel, jet, channel, reg, era))
                    plots.extend(cp.makeControlPlotsForBasicSel(sel, jet, dilepton, channel, reg))
                
                if make_ZpicPlots:
                    plots.extend(cp.makeControlPlotsForZpic(sel, dilepton, 'lepplusjetSel', channel, reg))
            
            if make_tau2tau1RatioPlots:  
                plots.extend(cp.makeNsubjettinessPLots(lljjSelections["boosted"], AK8jets, catSel, fatjets_nosubjettinessCut, channel))
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # DeepDoubleB for boosted events (L, M1, M2, T1, T2) 
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # same discriminator cut for Full run2 
            BoostedTopologiesWP = { 
                    "DoubleB":{
                            "L": 0.3, "M1": 0.6, "M2": 0.8, "T": 0.9 },
                    "DeepDoubleBvL":{
                            "L": 0.7, "M1": 0.86, "M2": 0.89, "T1": 0.91, "T2": 0.92}
                        }
            
            if make_DeepDoubleBPlots:
                BoostedWP = sorted(BoostedTopologiesWP["DeepDoubleBvL"].keys())
                FatJet_btagged = get_DeepDoubleXDeepBoostedJet(AK8jets, 'btagDDBvL', BoostedTopologiesWP["DeepDoubleBvL"])
                for wp in BoostedWP:
                   _2Lep2bjets_boOsted_NoMETcut = { "DeepDoubleBvL{0}".format(wp) :
                           lljjSelections["boosted"].refine("TwoLeptonsOneBjets_NoMETcut_DeepDoubleBvL{0}_{1}_Boosted".format(wp, channel),
                               cut=[ op.rng_len(FatJet_btagged[wp]) > 0],
                               weight=( get_BoostedEventWeight(era, 'DeepDoubleBvL', wp, FatJet_btagged[wp]) if isMC else None))
                           }
                   for suffix, sel in {
                            '_NoMETCut_' : _2Lep2bjets_boOsted_NoMETcut,
                            '_METCut_' : { key: selNoMET.refine(selNoMET.name.replace("NoMETcut_", ""), cut=(corrMET.pt < 80.))
                                for key, selNoMET in _2Lep2bjets_boOsted_NoMETcut.items() }
                            }.items():
                        plots.extend(cp.makeBJetPlots(sel, FatJet_btagged[wp], wp, channel, "boosted", suffix, era, "combined"))
                        plots.extend(cp.makeControlPlotsForFinalSel(sel, FatJet_btagged[wp], dilepton, wp, channel, "boosted", suffix, "combined"))
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # DeepCSV for both boosted && resolved , DeepFlavour  
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            bestJetPairs = {}
            for wp in self.WorkingPoints: 
                
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
                
                
                if make_JetmultiplictyPlots:
                    for suffix, bjet in { "resolved_DeepFlavour{}".format(wp): bJets_resolved_PassdeepflavourWP, 
                                          "resolved_DeepCSV{}".format(wp)    : bJets_resolved_PassdeepcsvWP,
                                          "boosted_DeepCSV{}".format(wp)     : bJets_boosted_PassdeepcsvWP }.items():
                        plots.extend(cp.makeJetmultiplictyPlots(catSel, bjet, channel,"_NoCutOnbJetsLen_"+ suffix))
                
                if self.dobJetER:
                    bJets_resolved_PassdeepflavourWP = corr.bJetEnergyRegression( bJets_resolved_PassdeepflavourWP)
                    bJets_resolved_PassdeepcsvWP     = corr.bJetEnergyRegression( bJets_resolved_PassdeepcsvWP)
                    bJets_boosted_PassdeepcsvWP      = corr.bJetEnergyRegression( bJets_boosted_PassdeepcsvWP)
    
                
               #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # No MET cut : selections 2 lep + at least 2b-tagged jets
               #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
                                                                        cut=[ op.rng_len(bJets_boosted_PassdeepcsvWP) >= 1, op.rng_len(bJets_resolved_PassdeepcsvWP) >= 0] ) },
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
                                
                
                if self.doPass_bTagEventWeight:
                    run2_bTagEventWeight_PerWP = corr.makeBtagSF(self.cleaned_AK4JetsByDeepB, self.cleaned_AK4JetsByDeepFlav, self.cleaned_AK8JetsByDeepB, 
                                                        OP, wp, idx, self.legacy_btagging_wpdiscr_cuts, 
                                                        channel, 
                                                        sample, 
                                                        era, 
                                                        noSel,
                                                        isMC, 
                                                        self.isULegacy)
                
                    llbbSelections_NoMETCut_bTagEventWeight = { process: 
                                                                { reg: 
                                                                    { key: selNobTag.refine(f"TwoLeptonsTwoBjets_NoMETCut_bTagEventWeight_{key}_{channel}_{reg}_{process}", weight = (run2_bTagEventWeight_PerWP[process][reg][key] if isMC else None))
                                                                    for key, selNobTag in NobTagEventWeight_selections_per_tagger.items() }
                                                                for reg, NobTagEventWeight_selections_per_tagger in NobTagEventWeight_selections_per_process.items()}
                                                            for process, NobTagEventWeight_selections_per_process in llbbSelections_NoMETCut_NobTagEventWeight.items() 
                                                        }
                    
                    llbbSelections_noMETCut = llbbSelections_NoMETCut_bTagEventWeight
                else:
                    llbbSelections_noMETCut = llbbSelections_NoMETCut_NobTagEventWeight
                
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
                                # make Skimmer
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if self.doSkim:
                    for process , Selections_per_process in llbbSelections.items():
                        process_ = 'ggH' if process =='gg_fusion' else 'bbH'
                        for reg, Selections_per_taggerWP in Selections_per_process.items():
                            for taggerWP, FinalSel in Selections_per_taggerWP.items():

                                if reg =="resolved":
                                    bJets  = bjets_resolved[taggerWP.replace(wp, "")][wp]
                                    llbb_M = (dilepton[0].p4 +dilepton[1].p4+bJets[0].p4+bJets[1].p4).M()
                                    bb_M   = op.invariant_mass(bJets[0].p4+bJets[1].p4)
                                    
                                elif reg =="boosted":
                                    bJets  = bjets_boosted[taggerWP.replace(wp, "")][wp]
                                    llbb_M = (dilepton[0].p4 +dilepton[1].p4+bJets[0].p4).M()
                                    bb_M   = bJets[0].mass
                                    bb_softDropM = bJets[0].msoftdrop

                                plots.append(Skim(  f"LepPlusJetsSel_{process_}_{reg}_{channel.lower()}_{taggerWP.lower()}", {
                                        # just copy the variable as it is in the nanoAOD input
                                        "run"            : None,
                                        "event"          : None,
                                        "luminosityBlock": None,  
                                        
                                        "l1_charge"      : dilepton[0].charge,
                                        "l2_charge"      : dilepton[1].charge,
                                        "l1_pdgId"       : dilepton[0].pdgId,
                                        "l2_pdgId"       : dilepton[1].pdgId,
                                        'bb_M'           : bb_M,
                                        'llbb_M'         : llbb_M,
                                        'bb_M_squared'   : op.pow(bb_M, 2),
                                        'llbb_M_squared' : op.pow(llbb_M, 2),
                                        'bb_M_x_llbb_M'  : op.product(bb_M, llbb_M),
                                        
                                        'isResolved'     : op.c_bool(reg == 'resolved'), 
                                        'isBoosted'      : op.c_bool(reg == 'boosted'), 
                                        'isElEl'         : op.c_bool(channel == 'ElEl'), 
                                        'isMuMu'         : op.c_bool(channel == 'MuMu'), 
                                        'isggH'          : op.c_bool(process_ == 'ggH'), 
                                        'isbbH'          : op.c_bool(process_ == 'bbH'), 

                                        'era'            : op.c_int(int(era_)),
                                        'total_weight'   : FinalSel.weight,
                                        'PU_weight'      : self.PUWeight if isMC else op.c_float(1.), 
                                        'MC_weight'      : t.genWeight if isMC else op.c_float(1.),

                                        f'nB_{lljj_jetType[reg]}bJets': op.static_cast("UInt_t", op.rng_len(bJets))
                                    }, FinalSel))
                
                else:
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                        #  to optimize the MET cut 
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    # you should get them for both signal && bkg  
                    if make_METPlots:
                        for process , Selections_noMETCut_per_process in llbbSelections_noMETCut.items():
                            for reg, sel in Selections_noMETCut_per_process.items():
                                plots.extend(cp.MakeMETPlots(sel, corrMET, MET, channel, reg, process))
                    
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                            # Evaluate the training  
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    if self.doEvaluate:
                        signal_grid = { 'seen_byDNN': masses_seen,
                                        'notpassed_to_bayesianblocks': masses_notseen }
                        plotOptions = utils.getOpts(channel)
                        if self.doBlinded:
                            plotOptions["blinded-range"] = [0.6, 1.0] 

                        for process, Selections_per_process in llbbSelections.items():
                            for region, selections_per_region in Selections_per_process.items(): 
                                for tag_plus_wp, sel in selections_per_region.items():
                                   
                                    if not tag_plus_wp =='DeepCSVM': continue
                                    if not process == 'gg_fusion': continue
                                    
                                    process_ = 'ggH' if process =='gg_fusion' else 'bbH'
                                    bjets_   = lljj_bJets[region][tag_plus_wp.replace(wp,'')][wp]
                                    jj_p4    = ( (bjets_[0].p4 + bjets_[1].p4) if region=="resolved" else( bjets_[0].p4))
                                    lljj_p4  = ( dilepton[0].p4 + dilepton[1].p4 + jj_p4)
                                    
                                    bb_M    = jj_p4.M()
                                    llbb_M  = lljj_p4.M()
                                    for k, tup in signal_grid.items():
                                        for parameters in tup: 
                                            mH = parameters[0]
                                            mA = parameters[1]
                                            
                                            inputsCommon = {'l1_pdgId'        : dilepton[0].pdgId               ,
                                                            'myera'           : op.c_int(int(era_))             ,
                                                            'bb_M'            : jj_p4.M()                       ,
                                                            'llbb_M'          : lljj_p4.M()                     ,
                                                            'bb_M_squared'    : op.pow(bb_M, 2)                 ,
                                                            'llbb_M_squared'  : op.pow(llbb_M, 2)               ,
                                                            'bb_M_x_llbb_M'   : op.product(bb_M, llbb_M)        ,
                                                            'mA'              : op.c_float(mA)                  ,
                                                            'mH'              : op.c_float(mH)                  ,  
                                                            'isResolved'      : op.c_bool(region == 'resolved') ,
                                                            'isBoosted'       : op.c_bool(region == 'boosted')  ,
                                                            'isggH'           : op.c_bool(process_ == 'ggH')    ,
                                                            'isbbH'           : op.c_bool(process_ == 'bbH')    ,
                                                            }
                                            
                                            histNm = f"DNNOutput_ZAnode_{channel}_{region}_{tag_plus_wp}_METCut_{process}_MH_{mass_to_str(mH)}_MA_{mass_to_str(mA)}"
                                            if rebin_bayesian :
                                                # I did not optimize the bayesian blocks for these catagories yet !!# FIXME
                                                look_for = histNm
                                                if region == 'boosted':
                                                    look_for = look_for.replace('boosted', 'resolved')
                                                if process == 'bb_associatedProduction':
                                                    look_for = look_for.replace('bb_associatedProduction', 'gg_fusion')
                                                print(f"working on rebinning of {histNm} :: bayesian blocks {bayesian_blocks_binnings['histograms'][look_for][0][0]}") 
                                                binning = VarBin(bayesian_blocks_binnings['histograms'][look_for][0][0])
                                            
                                            elif rebin_uniform_50bins:
                                                binning = EqB(50, 0., 1.)

                                            DNN_Inputs   = [op.array("float",val) for val in inputStaticCast(inputsCommon,"float")]
                                            DNN_Output   = ZA_mvaEvaluator(*DNN_Inputs) # [DY, TT, ZA]
                                             
                                            plots.append(Plot.make1D(histNm, DNN_Output[2], sel, binning, title='DNN_Output ZA', plotopts=plotOptions))
                                            #plots.append(Plot.make2D(f"mbb_vs_DNNOutput_ZAnode_{channel}_{region}_{tag_plus_wp}_METCut_{process}_MH_{mass_to_str(mH)}_MA_{mass_to_str(mA)}",
                                            #            (jj_p4.M(), DNN_Output[2]), sel,
                                            #            (EqB(50, 0., 1000.), EqB(50, 0., 1.)),
                                            #            title="mbb mass Input vs DNN Output", plotopts=plotOptions))
                                            #plots.append(Plot.make2D(f"mbb_vs_DNNOutput_ZAnode_{channel}_{region}_{tag_plus_wp}_METCut_{process}_MH_{mass_to_str(mH)}_MA_{mass_to_str(mA)}",
                                            #            (lljj_p4.M(), DNN_Output[2]), sel,
                                            #            (EqB(50, 0., 1000.), EqB(50, 0., 1.)),
                                            #            title="mllbb mass Input vs DNN Output", plotopts=plotOptions))
                                           # #OutmaxIDx =op.rng_max_element_index(DNN_Output)
                                           # trainSel= sel['DeepCSVM'].refine(f'DNN_On{node}node_llbb_{channel}_{region}selection_withmetcut_MA_{mA}_MH_{mH}',cut=[OutmaxIDx == op.c_int(i)])                
                                           # plots.append(Plot.make1D(f"DNNOutput_trainSel_{node}node_ll{channel}_jj{region}_btaggedDeepcsvM_withmetCut_scan_MA{mA}_MH{mH}", DNN_Output[i], trainSel,
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
                                plots.extend(cp.makeHistosForTTbarEstimation(sel, dilepton, bjets_resolved, wp, channel, "resolved", metReg, process))
                    
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
                                    plots.extend(cp.makeBJetPlots(selDict, bjets, wp, channel, reg, metCutNm_, era, process))
                                    plots.extend(cp.makeControlPlotsForFinalSel(selDict, bjets, dilepton, wp, channel, reg, metCutNm_, process))

                                if make_PlotsforCombinedLimits:
                                    plots.extend(makerhoPlots(selDict, bjets, dilepton, self.ellipses, self.ellipse_params, reg, metCutNm_, wp, channel, self.doBlinded, process))

                                for key, sel in selDict.items():
                                    yield_object.addYields(sel, f"has2Lep2{reg.upper()}BJets_{metCutNm}_{channel}_{key}_{process}",
                                            f"{process}: 2 Lep(OS)+ {jlenOpts[reg]} {lljj_jetType[reg]}BJets {reg} pass {key}+ {metCutNm}+ bTagEventWeight(channel: {optstex})")
                                    
                                    selections_for_cutflowreport.append(sel)
                    
                    if make_ExtraFatJetsPlots:
                        for process in ['gg_fusion', 'bb_associatedProduction']:
                            plots.extend(makeExtraFatJetBOostedPlots(llbbSelections[process]['boosted'], lljj_bJets['boosted'], wp, channel, 'METCut', process))
        
        if self.doYields:
            plots.append(CutFlowReport("Yields", selections_for_cutflowreport))
            plots.extend(yield_object.returnPlots())
        
        return plots

    def postProcess(self, taskList, config=None, workdir=None, resultsdir=None):
        # run plotIt as defined in HistogramsModule - this will also ensure that self.plotList is present
        super(NanoHtoZA, self).postProcess(taskList, config, workdir, resultsdir)

        import json 
        import bambooToOls
        import pandas as pd
        from bamboo.plots import CutFlowReport, DerivedPlot, Skim

        # memory usage
        #start= timer()
        #end= timer()
        #maxrssmb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
        #logger.info(f"{len(self.plotList):d} plots defined in {end - start:.2f}s, max RSS: {maxrssmb:.2f}MB")
        #with open(os.path.join(resultsdir=".","memoryusage.json"%suffix), "w") as handle:
        #    json.dump(len(self.plotList), handle, indent=4)
        #    json.dump(maxrssmb, handle, indent=4)
        #    json.dump(end - start, handle, indent=4)

        if self.doSysts:
            for task in taskList:
                if self.isMC(task.name) and "syst" not in task.config:
                    if self.pdfVarMode == "full" and task.config.get("pdf_full", False):
                        utils.producePDFEnvelopes(self.plotList, task, resultsdir)
        
        plotstoNormalized = []
        for plots in self.plotList:
            if plots.name.startswith('rho_steps_') or plots.name.startswith('jj_M_') or plots.name.startswith('lljj_M_') or plots.name.startswith('DNNOutput_'):
                plotstoNormalized.append(plots)
        if not os.path.isdir(os.path.join(resultsdir, "normalizedForCombined")):
            os.makedirs(os.path.join(resultsdir,"normalizedForCombined"))

        if plotstoNormalized:
            utils.normalizeAndMergeSamplesForCombined(plotstoNormalized, self.readCounters, config, resultsdir, os.path.join(resultsdir, "normalizedForCombined"))
        
        # save generated-events for each samples--- > mainly needed for the DNN
        plotList_cutflowreport = [ ap for ap in self.plotList if isinstance(ap, CutFlowReport) ]
        #bambooToOls.SaveCutFlowReports(config, plotList_cutflowreport, resultsdir, self.readCounters)
        
        from bamboo.root import gbl
        
        for era in config["eras"]:
            xsec = dict()
            sumw = dict()
            for smpNm, smpCfg in config["samples"].items():
                outName = f"{smpNm}.root"
                if 'data' in smpCfg.values(): 
                    continue
                if smpCfg["era"] != era:
                    continue
                f = gbl.TFile.Open(os.path.join(resultsdir, outName))
                xsec[outName]  = smpCfg["cross-section"]
                sumw[outName]  = self.readCounters(f)[smpCfg["generated-events"]]
            xsecSumw_dir = os.path.join(resultsdir, "data")
            if not os.path.isdir(xsecSumw_dir):
                os.makedirs(xsecSumw_dir)
            with open(os.path.join(xsecSumw_dir, f"ulegacy{era}_xsec.json"), "w") as normF:
                json.dump(xsec, normF, indent=4)
            with open(os.path.join(xsecSumw_dir, f"ulegacy{era}_event_weight_sum.json"), "w") as normF:
                json.dump(sumw, normF, indent=4)

        plotList_2D = [ ap for ap in self.plotList if ( isinstance(ap, Plot) or isinstance(ap, DerivedPlot) ) and len(ap.binnings) == 2 ]
        logger.debug("Found {0:d} plots to save".format(len(plotList_2D)))

        from bamboo.analysisutils import loadPlotIt
        p_config, samples, plots_2D, systematics, legend = loadPlotIt(config, plotList_2D, eras=None, workdir=workdir, resultsdir=resultsdir, readCounters=self.readCounters, vetoFileAttributes=self.__class__.CustomSampleAttributes, plotDefaults=self.plotDefaults)
        
        from plotit.plotit import Stack
        
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
                if not not expStack:
                    cv.cd(1)
                    expStack.obj.Draw("COLZ0")
                if not not obsStack:
                    cv.cd(2)
                    obsStack.obj.Draw("COLZ0")
                cv.Update()
                cv.SaveAs(os.path.join(resultsdir, f"{plot.name}.png"))
        
        skims = [ap for ap in self.plotList if isinstance(ap, Skim)]
        if self.doSkim and skims:
            try:
                for skim in skims:
                    frames = []
                    for smp in samples:
                        for cb in (smp.files if hasattr(smp, "files") else [smp]):  # could be a helper in plotit
                            # Take specific columns
                            tree = cb.tFile.Get(skim.treeName)
                            if not tree:
                                print( f"KEY TTree {skim.treeName} does not exist, we are gonna skip this {smp}\n")
                            else:
                                N = tree.GetEntries()
                                # https://indico.cern.ch/event/775679/contributions/3244724/attachments/1767054/2869505/RDataFrame.AsNumpy.pdf
                                # https://stackoverflow.com/questions/33813815/how-to-read-a-parquet-file-into-pandas-dataframe
                                #print (f"Entries in {smp} // KEY TTree {skim.treeName}: {N}")
                                cols = gbl.ROOT.RDataFrame(cb.tFile.Get(skim.treeName)).AsNumpy()
                                cols["total_weight"] *= cb.scale
                                cols["process"] = [smp.name]*len(cols["total_weight"])
                                frames.append(pd.DataFrame(cols))
                    df = pd.concat(frames)
                    df["process"] = pd.Categorical(df["process"], categories=pd.unique(df["process"]), ordered=False)
                    pqoutname = os.path.join(resultsdir, f"{skim.name}.parquet")
                    df.to_parquet(pqoutname)
                    logger.info(f"Dataframe for skim {skim.name} saved to {pqoutname}")
            except ImportError as ex:
                logger.error("Could not import pandas, no dataframes will be saved")
