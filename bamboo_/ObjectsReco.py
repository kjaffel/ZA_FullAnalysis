from bamboo.analysismodules import NanoAODModule, NanoAODSkimmerModule
from bamboo.analysisutils import makeMultiPrimaryDatasetTriggerSelection
from bamboo.scalefactors import binningVariables_nano

from bamboo import treefunctions as op
from bamboo import scalefactors

#from bamboo.logging import getLogger
#logger = getLogger(__name__)
import logging
logger = logging.getLogger("H->ZA->llbb Plotter")

from itertools import chain
import os.path
import collections
import math
import argparse
import sys

zabPath = os.path.dirname(__file__)
if zabPath not in sys.path:
    sys.path.append(zabPath)
import utils
import HistogramTools as HT
from boOstedEvents import addBoOstedTagger, getBoOstedWeight
from scalefactorslib import all_scalefactors


binningVariables = {
      "Eta"       : lambda obj : obj.eta
    , "ClusEta"   : lambda obj : obj.eta + obj.deltaEtaSC
    , "AbsEta"    : lambda obj : op.abs(obj.eta)
    , "AbsClusEta": lambda obj : op.abs(obj.eta + obj.deltaEtaSC)
    , "Pt"        : lambda obj : obj.pt
    }

def get_scalefactor(objType, key, periods=None, combine=None, additionalVariables=dict(), getFlavour=None, systName=None):
    return scalefactors.get_scalefactor(objType, key, periods=periods, combine=combine, 
                                        additionalVariables=additionalVariables, 
                                        sfLib=all_scalefactors, 
                                        paramDefs=binningVariables, 
                                        getFlavour=getFlavour,
                                        systName=systName)
def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct
def getL1PreFiringWeight(tree):
    return op.systematic(tree.L1PreFiringWeight_Nom, 
                            name="L1PreFiring", 
                            up=tree.L1PreFiringWeight_Up, 
                            down=tree.L1PreFiringWeight_Dn)

class NanoHtoZABase(NanoAODModule):
    """ H->Z(ll)A(bb) analysis for the FullRunII using NanoAODv5 """
    
    def __init__(self, args):
        super(NanoHtoZABase, self).__init__(args)
        self.plotDefaults = {
                            "y-axis"           : "Events",
                            "log-y"            : "both",
                            "y-axis-show-zero" : True,
                            "save-extensions"  : ["pdf"],
                            "show-ratio"       : True,
                            "sort-by-yields"   : False,
                            }

        self.doSysts = self.args.systematic
    def addArgs(self, parser):
        super(NanoHtoZABase, self).addArgs(parser)
        parser.add_argument("--backend", type=str, default="dataframe", help="Backend to use, 'dataframe' (default) or 'lazy'")
        parser.add_argument("-s", "--systematic", action="store_true", help="Produce systematic variations")

    def prepareTree(self, tree, sample=None, sampleCfg=None):
        era = sampleCfg.get("era") if sampleCfg else None
        isMC = self.isMC(sample)
        metName = "METFixEE2017" if era == "2017" else "MET"
        ## initializes tree.Jet.calc so should be called first (better: use super() instead)
        # JEC's Recommendation for Full RunII: https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC
        # JER : -----------------------------: https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
        from bamboo.treedecorators import NanoAODDescription, nanoRochesterCalc, nanoJetMETCalc

        tree,noSel,be,lumiArgs =  super(NanoHtoZABase,self).prepareTree(tree, 
                                                                        sample=sample, 
                                                                        sampleCfg=sampleCfg, 
                                                                        description=NanoAODDescription.get("v5", year=(era if era else "2016"), 
                                                                        isMC=isMC, 
                                                                        systVariations=[ nanoRochesterCalc, (nanoJetMETCalc_METFixEE2017 if era == "2017" else nanoJetMETCalc) ]),
                                                                        lazyBackend   = (self.args.backend == "lazy")) ## will do Jet and MET variations, and the Rochester correction
        triggersPerPrimaryDataset = {}
        jec, smear, jesUncertaintySources = None, None, None

        from bamboo.analysisutils import configureJets, configureType1MET, configureRochesterCorrection
        isNotWorker = (self.args.distributed != "worker") 
        

        if era == "2016":

            configureRochesterCorrection(tree._Muon, os.path.join(os.path.dirname(__file__), "data", "RoccoR2016.txt"), isMC=isMC, backend=be, uName=sample)
            
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
                jec = "Summer16_07Aug2017_V20_MC"
                smear="Summer16_25nsV1_MC"
                jesUncertaintySources=["Total"]
                
            else:
                if "2016B" in sample or "2016C" in sample or "2016D" in sample:
                    jec="Summer16_07Aug2017BCD_V11_DATA"

                elif "2016E" in sample or "2016F" in sample:
                    jec="Summer16_07Aug2017EF_V11_DATA"
                    
                elif "2016G" in sample or "2016H" in sample:
                    jec="Summer16_07Aug2017GH_V11_DATA"
                    
        elif era == "2017":
            
            configureRochesterCorrection(tree._Muon, os.path.join(os.path.dirname(__file__), "data", "RoccoR2017.txt"), isMC=isMC, backend=be, uName=sample)
            
            # https://twiki.cern.ch/twiki/bin/view/CMS/MuonHLT2017
            triggersPerPrimaryDataset = {
                "DoubleMuon" : [ tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8,
                                 #tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8  # Not for era B
                                 ],
                    
                # it's recommended to not use the DoubleEG HLT _ DZ version  for 2017 and 2018, 
                # using them it would be a needless efficiency loss !
                #---> https://twiki.cern.ch/twiki/bin/view/CMS/EgHLTRunIISummary
                "DoubleEG"   : [ tree.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL], # loosely isolated
                                 #tree.HLT.DoubleEle33_CaloIdL_MW],
                                    
                "MuonEG"     : [ #tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,  #  Not for Era B
                                 tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
                                 
                                 # tree.HLT.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,  # Not for Era B
                                 tree.HLT.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ,
                                 
                                 #tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,   # Not for Era B
                                 tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ ]
            }
            
            if "2017B" not in sample:
                triggersPerPrimaryDataset["MuonEG"] += [ 
                        ## removed for 2017B
                        tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,
                        tree.HLT.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,
                        tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL]
                
                triggersPerPrimaryDataset["DoubleMuon"] += [ 
                         ## removed for 2017B
                         tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8]

            if self.isMC(sample):
                jec="Fall17_17Nov2017_V32_MC"
                smear="Fall17_V3_MC"
                jesUncertaintySources=["Total"]

                configureJets(tree._Jet, "AK4PFchs",
                    jec="Fall17_17Nov2017_V32_MC",
                    smear="Fall17_V3_MC",
                    jesUncertaintySources=["Total"], 
                    mayWriteCache=isNotWorker, isMC=isMC, backend=be, uName=sample)
            else:
                if "2017B" in sample:
                    jec="Fall17_17Nov2017B_V32_DATA"

                elif "2017C" in sample:
                    jec="Fall17_17Nov2017C_V32_DATA"

                elif "2017D" in sample or "2017E" in sample:
                    jec="Fall17_17Nov2017DE_V32_DATA"
                
                elif "2017F" in sample:
                    jec="Fall17_17Nov2017F_V32_DATA"

        elif era == "2018":
            configureRochesterCorrection(tree._Muon, os.path.join(os.path.dirname(__file__), "data", "RoccoR2018.txt"), isMC=isMC, backend=be, uName=sample)
            
            triggersPerPrimaryDataset = {
                "DoubleMuon" : [ tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8, #  - Unprescaled for the whole year 
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8 ],
                
                "EGamma"     : [ tree.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL ], 
                
                "MuonEG"     : [ tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,
                                 tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
                                 
                                 tree.HLT.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,
                                 tree.HLT.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ,

                                 tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,
                                 tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ,
                                 
                                 #tree.HLT.Mu27_Ele37_CaloIdL_MW, 
                                 #tree.HLT.Mu37_Ele27_CaloIdL_MW
                                 ],
                #"SingleElectron":[ tree.HLT.Ele32_WPTight_Gsf  ],
                # OldMu100 and TkMu100 are recommend to recover inefficiencies at high pt 
                # here: (https://indico.cern.ch/event/766895/contributions/3184188/attachments/1739394/2814214/IdTrigEff_HighPtMu_Min_20181023_v2.pdf)
                #"SingleMuon": [ tree.HLT.IsoMu24, 
                #                tree.HLT.IsoMu27, 
                #                tree.HLT.Mu50, 
                #                tree.HLT.OldMu100, 
                #                tree.HLT.TkMu100 ], 
                }

            if self.isMC(sample):
                jec="Autumn18_V8_MC"
                smear="Autumn18_V1_MC"
                jesUncertaintySources=["Total"]

            else:
                if "2018A" in sample:
                    jec="Autumn18_RunA_V8_DATA"

                elif "2018B" in sample:
                    jec="Autumn18_RunB_V8_DATA"

                elif "2018C" in sample:
                    jec="Autumn18_RunC_V8_DATA"
        
                elif "2018D" in sample:
                    jec="Autumn18_RunD_V8_DATA"
        else:
            raise RuntimeError("Unknown era {0}".format(era))
        ## Configure jets 
        try:
            configureJets(tree._Jet, "AK4PFchs", jec=jec, smear=smear, jesUncertaintySources=jesUncertaintySources, mayWriteCache=isNotWorker, isMC=isMC, backend=be, uName=sample)
            # FIXME
            #configureJets(tree._Jet, "AK8", jec=jec, smear=smear, jesUncertaintySources=jesUncertaintySources, mayWriteCache=isNotWorker, isMC=isMC, backend=be, uName=sample)
        except Exception as ex:
            logger.exception("Problem while configuring jet correction and variations")
        
        ## Configure MET
        try:
            configureType1MET(getattr(tree, f"_{metName}"), jec=jec, smear=smear, jesUncertaintySources=jesUncertaintySources, mayWriteCache=isNotWorker, isMC=isMC, backend=be, uName=sample)
        except Exception as ex:
            logger.exception("Problem while configuring MET correction and variations")
        
        
        sampleCut = None
        if self.isMC(sample):
            # remove double counting passing TTbar Inclusive + TTbar Full Leptonic ==> mainly for 2016 Analysis 
            if sample =="TT":
                genLeptons_hard = op.select(tree.GenPart, 
                                            lambda gp : op.AND((gp.statusFlags & (0x1<<7)), 
                                                                op.in_range(10, op.abs(gp.pdgId), 17)))
                sampleCut = (op.rng_len(genLeptons_hard) == 0)
                noSel = noSel.refine("genWeight", weight=tree.genWeight, 
                                                  cut=[sampleCut, op.OR(*chain.from_iterable(triggersPerPrimaryDataset.values())) ], 
                                                  autoSyst=self.doSysts)
            else:
                noSel = noSel.refine("genWeight", weight=tree.genWeight, 
                                                  cut=op.OR(*chain.from_iterable(triggersPerPrimaryDataset.values())), 
                                                  autoSyst=self.doSysts)

            if self.doSysts:
                logger.info("Adding QCD scale variations, ISR and FSR ")
                noSel = utils.addTheorySystematics(self, tree, noSel)
        else:
            noSel = noSel.refine("withTrig", cut=makeMultiPrimaryDatasetTriggerSelection(sample, triggersPerPrimaryDataset) )
        
        return tree,noSel,be,lumiArgs
    
    def defineObjects(self, t, noSel, sample=None, sampleCfg=None):    
        from bamboo.analysisutils import forceDefine
        #from bamboo.plots import Plot
        from bambooToOls import Plot
        from bamboo.plots import CutFlowReport
        from bamboo.plots import EquidistantBinning as EqB
        from bamboo import treefunctions as op
        from bamboo.analysisutils import makePileupWeight
        from METFilter_xyCorr import METFilter, METcorrection

        era = sampleCfg.get("era") if sampleCfg else None
        noSel = noSel.refine("passMETFlags", cut=METFilter(t.Flag, era) )
        puWeightsFile = None

        if era == "2016":
            sfTag="94X"
            # TO invistgate more about the pileup ... ! 
            puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/", "puweights2016_Moriond17.json")
        
        elif era == "2017":
            sfTag="94X"     
            puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/", "puweights2017_Fall17.json")
        
        elif era == "2018":
            sfTag="102X"
            puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/", "puweights2018_Autumn18.json")
        
        if self.isMC(sample) and puWeightsFile is not None:
            PUWeight = makePileupWeight(puWeightsFile, t.Pileup_nTrueInt, systName="pileup")
            noSel = noSel.refine("puWeight", weight=PUWeight)
        
        isMC = self.isMC(sample)
        plots = []
        forceDefine(t._Muon.calcProd, noSel)

        # Wp // 2016- 2017 -2018 : Muon_mediumId   // https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Muon_Isolation
        #To suppress nonprompt leptons, the impact parameter in three dimensions of the lepton track, with respect to the primaryvertex, is required to be less than 4 times its uncertainty (|SIP3D|<4)
        sorted_muons = op.sort(t.Muon, lambda mu : -mu.pt)
        muons = op.select(sorted_muons, lambda mu : op.AND(mu.pt > 10., op.abs(mu.eta) < 2.4, mu.mediumId, mu.pfRelIso04_all<0.15, op.abs(mu.sip3d) < 4.))

        # I pass 2016 seprate from 2017 &2018  because SFs need to be combined for BCDEF and GH eras !
        if era=="2016":
            muMediumIDSF = get_scalefactor("lepton", ("muon_{0}_{1}".format(era, sfTag), "id_medium"), combine="weight", systName="muid")
            muMediumISOSF = get_scalefactor("lepton", ("muon_{0}_{1}".format(era, sfTag), "iso_tight_id_medium"), combine="weight", systName="muiso")
        else:
            muMediumIDSF = get_scalefactor("lepton", ("muon_{0}_{1}".format(era, sfTag), "id_medium"), systName="muid")
            muMediumISOSF = get_scalefactor("lepton", ("muon_{0}_{1}".format(era, sfTag), "iso_tight_id_medium"), systName="muiso") 
        
        #Wp  // 2016: Electron_cutBased_Sum16==3  -> medium     // 2017 -2018  : Electron_cutBased ==3   --> medium ( Fall17_V2)
        # asking for electrons to be in the Barrel region with dz<1mm & dxy< 0.5mm   //   Endcap region dz<2mm & dxy< 0.5mm 
        # cut-based ID Fall17 V2 the recomended one from POG for the FullRunII
        sorted_electrons = op.sort(t.Electron, lambda ele : -ele.pt)
        electrons = op.select(sorted_electrons, 
                                lambda ele : op.AND(ele.pt > 15., op.abs(ele.eta) < 2.5 , ele.cutBased>=3, op.abs(ele.sip3d) < 4., 
                                                    op.OR(op.AND(op.abs(ele.dxy) < 0.05, op.abs(ele.dz) < 0.1), 
                                                          op.AND(op.abs(ele.dxy) < 0.05, op.abs(ele.dz) < 0.2) ))) 

        elMediumIDSF = get_scalefactor("lepton", ("electron_{0}_{1}".format(era,sfTag), "id_medium"), systName="elid")
        
        MET = t.MET if era != "2017" else t.METFixEE2017
        corrMET=METcorrection(MET,t.PV,sample,era,self.isMC(sample))
        
        
        #######  select jets  
        ##################################
        #// 2016 - 2017 - 2018   ( j.jetId &2) ->      tight jet ID
        # For 2017 data, there is the option of "Tight" or "TightLepVeto", depending on how much you want to veto jets that overlap with/are faked by leptons
        sorted_AK4jets=op.sort(t.Jet, lambda j : -j.pt)
        AK4jetsSel = op.select(sorted_AK4jets, lambda j : op.AND(j.pt > 20., op.abs(j.eta)< 2.4, (j.jetId &2)))#   j.jetId == 6))#        
        
        if era== '2016':
            # exclude from the jetsSel any jet that happens to include within its reconstruction cone a muon or an electron.
            AK4jets= op.select(AK4jetsSel, 
                                lambda j : op.AND(
                                                op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < 0.3 )), 
                                                op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < 0.3 ))))
        else:
            AK4jets= op.select(AK4jetsSel, 
                                lambda j : op.AND(
                                    op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < 0.4 )), 
                                    op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < 0.4 ))))

        cleaned_AK4JetsByDeepFlav = op.sort(AK4jets, lambda j: -j.btagDeepFlavB)
        cleaned_AK4JetsByDeepB = op.sort(AK4jets, lambda j: -j.btagDeepB)

        # Boosted Region
        sorted_AK8jets=op.sort(t.FatJet, lambda j : -j.pt)
        # ask for two subjet to be inside the fatjet
        # The AK8 jets are required to have the nsubjettiness parameters tau2/tau1< 0.5 to be consistent with an AK8 jet having two subjets.
        AK8jetsSel = op.select(sorted_AK8jets, 
                                lambda j : op.AND(j.pt > 200., op.abs(j.eta)< 2.4, (j.jetId &2), 
                                                  j.subJet1._idx.result != -1, 
                                                  j.subJet2._idx.result != -1, 
                                                  j.tau2/j.tau1 < 0.5))
        
        AK8jets= op.select(AK8jetsSel, 
                            lambda j : op.AND(
                                            op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < 0.8 )), 
                                            op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < 0.8 ))))
        
        cleaned_AK8JetsByDeepB = op.sort(AK8jets, lambda j: -j.btagDeepB)
        
        # Now,  let's ask for the jets to be a b-jets 
        # DeepCSV or deepJet Medium b-tag working point
        btagging = {
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
        # same cut for run2 
        BoostedTopologiesWP = { 
                    "DoubleB":{
                            "L": 0.3,
                            "M1": 0.6,
                            "M2": 0.8,
                            "T": 0.9,
                            },
                    "DeepDoubleBvL":{
                            "L": 0.7,
                            "M1": 0.86,
                            "M2": 0.89,
                            "T1": 0.91,
                            "T2": 0.92,
                            }
                        }
        
        # bjets ={ "DeepFlavour": {"L": jets pass loose  , "M":  jets pass medium  , "T":jets pass tight    }     
        #          "DeepCSV"    : {"L":    ---           , "M":         ---        , "T":   ----            }
        #        }
        bjets_boosted = {}
        bjets_resolved = {}
        
        #WorkingPoints = ["L", "M", "T"]
        WorkingPoints = ["M"]
        for tagger  in btagging.keys():
            
            bJets_AK4_deepflavour ={}
            bJets_AK4_deepcsv ={}
            bJets_AK8_deepcsv ={}
            for wp in sorted(WorkingPoints):
                
                suffix = ("loose" if wp=='L' else ("medium" if wp=='M' else "tight"))
                idx = ( 0 if wp=="L" else ( 1 if wp=="M" else 2))
                if tagger=="DeepFlavour":
                    
                    print ("Btagging: Era= {0}, Tagger={1}, Pass_{2}_working_point={3}".format(era, tagger, suffix, btagging[tagger][era][idx] ))
                    print ("btag_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "{0}_{1}".format('DeepJet', suffix))
                    
                    bJets_AK4_deepflavour[wp] = op.select(cleaned_AK4JetsByDeepFlav, lambda j : j.btagDeepFlavB >= btagging[tagger][era][idx] )
                    
                    Jet_DeepFlavourBDisc = { "BTagDiscri": lambda j : j.btagDeepFlavB }
                    deepBFlavScaleFactor = get_scalefactor("jet", ("btag_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "{0}_{1}".format('DeepJet', suffix)),
                                                        additionalVariables=Jet_DeepFlavourBDisc, 
                                                        getFlavour=(lambda j : j.hadronFlavour),
                                                        systName="DeepFlavour{0}".format(wp))  
                    
                    bjets_resolved[tagger]=bJets_AK4_deepflavour
                    
                else:
                    print ("Btagging: Era= {0}, Tagger={1}, Pass_{2}_working_point={3}".format(era, tagger, suffix, btagging[tagger][era][idx] ))
                    print ("btag_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "{0}_{1}".format('DeepCSV', suffix))
                    
                    bJets_AK4_deepcsv[wp] = op.select(cleaned_AK4JetsByDeepB, lambda j : j.btagDeepB >= btagging[tagger][era][idx] )   
                    bJets_AK8_deepcsv[wp] = op.select(cleaned_AK8JetsByDeepB, 
                                                        lambda j : op.AND(j.subJet1.btagDeepB >= btagging[tagger][era][idx] , 
                                                                          j.subJet2.btagDeepB >= btagging[tagger][era][idx]))   
                    Jet_DeepCSVBDis = { "BTagDiscri": lambda j : j.btagDeepB }
                    subJet_DeepCSVBDis = { "BTagDiscri": lambda j : op.AND(j.subJet1.btagDeepB, j.subJet2.btagDeepB) }
                    
                    deepB_AK4ScaleFactor = get_scalefactor("jet", ("btag_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "{0}_{1}".format('DeepCSV', suffix)), 
                                                additionalVariables=Jet_DeepCSVBDis,
                                                getFlavour=(lambda j : j.hadronFlavour),
                                                systName="DeepCSV{0}".format(wp))  
                    
                    # FIXME --> can be done with nanov7
                    #deepB_AK8ScaleFactor = get_scalefactor("jet", ("btag_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "subjet_{0}_{1}".format('subjet_DeepCSV', suffix)), 
                                                #additionalVariables=Jet_DeepCSVBDis,
                                                #getFlavour=(lambda j : j.subJet1.hadronFlavour),
                                                #systName="btagging{0}".format(era))  
                    
                    bjets_resolved[tagger]=bJets_AK4_deepcsv
                    bjets_boosted[tagger]=bJets_AK8_deepcsv
        
        bestDeepFlavourPair={}
        bestDeepCSVPair={}
        bestJetPairs= {}
        bjets = {}
        # For the Resolved only 
        class GetBestJetPair(object):
            JetsPair={}
            def __init__(self, JetsPair, tagger, wp):
                def ReturnHighestDiscriminatorJet(tagger, wp):
                    if tagger=="DeepCSV":
                        return op.sort(safeget(bjets_resolved, tagger, wp), lambda j: - j.btagDeepB)
                    elif tagger=="DeepFlavour":
                        return op.sort(safeget(bjets_resolved, tagger, wp), lambda j: - j.btagDeepFlavB)
                    else:
                        raise RuntimeError("Something went wrong in returning {0} discriminator !".format(tagger))
               
                firstBest=ReturnHighestDiscriminatorJet(tagger, wp)[0]
                JetsPair[0]=firstBest
                secondBest=ReturnHighestDiscriminatorJet(tagger, wp)[1]
                JetsPair[1]=secondBest
        #  bestJetPairs= { "DeepFlavour": bestDeepFlavourPair,
        #                  "DeepCSV":     bestDeepCSVPair    
        #                }
        
        #######  Zmass reconstruction : Opposite Sign , Same Flavour leptons
        ########################################################
        # supress quaronika resonances and jets misidentified as leptons
        LowMass_cut = lambda lep1, lep2: op.invariant_mass(lep1.p4, lep2.p4)>12.
        ## Dilepton selection: opposite sign leptons in range 70.<mll<120. GeV 
        osdilep_Z = lambda l1,l2 : op.AND(l1.charge != l2.charge, op.in_range(70., op.invariant_mass(l1.p4, l2.p4), 120.))

        osLLRng = {
                "MuMu" : op.combine(muons, N=2, pred= osdilep_Z),
                "ElEl" : op.combine(electrons, N=2, pred=osdilep_Z),
                "ElMu" : op.combine((electrons, muons), pred=lambda ele,mu : op.AND(LowMass_cut(ele, mu), osdilep_Z(ele,mu), ele.pt > mu.pt )),
                "MuEl" : op.combine((muons, electrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), osdilep_Z(mu,ele), mu.pt > ele.pt))
                }
        
        # FIXME maybe for 2017 or 2018 --> The leading pT for the �µ or µe channel should be above 20 Gev !
        hasOSLL_cmbRng = lambda cmbRng : op.AND(op.rng_len(cmbRng) > 0, cmbRng[0][0].pt > 25.) 
        
        ## helper selection (OR) to make sure jet calculations are only done once
        hasOSLL = noSel.refine("hasOSLL", cut=op.OR(*( hasOSLL_cmbRng(rng) for rng in osLLRng.values())))
       
        forceDefine(t._Jet.calcProd, hasOSLL)
        forceDefine(getattr(t, "_{0}".format("MET" if era != "2017" else "METFixEE2017")).calcProd, hasOSLL)
                
        doubleMuTrigSF = get_scalefactor("dilepton", ("doubleMuLeg_HHMoriond17_2016"), systName="mumutrig")    
        doubleEleTrigSF = get_scalefactor("dilepton", ("doubleEleLeg_HHMoriond17_2016"), systName="eleltrig")
        elemuTrigSF = get_scalefactor("dilepton", ("elemuLeg_HHMoriond17_2016"), systName="elmutrig")
        mueleTrigSF = get_scalefactor("dilepton", ("mueleLeg_HHMoriond17_2016"), systName="mueltrig")
        
        L1Prefiring = None
        if era in ["2016", "2017"]:
            L1Prefiring = getL1PreFiringWeight(t) 
        
        llSFs = {
            "MuMu" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[0]), muMediumISOSF(ll[1]), doubleMuTrigSF(ll), L1Prefiring]),
            "ElMu" : (lambda ll : [ elMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[1]), elemuTrigSF(ll), L1Prefiring]),
            "MuEl" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumISOSF(ll[0]), elMediumIDSF(ll[1]), mueleTrigSF(ll), L1Prefiring ]),
            "ElEl" : (lambda ll : [ elMediumIDSF(ll[0]), elMediumIDSF(ll[1]), doubleEleTrigSF(ll), L1Prefiring])
            }
        
        categories = dict((channel, (catLLRng[0], hasOSLL.refine("hasOs{0}".format(channel), cut=hasOSLL_cmbRng(catLLRng), weight=(llSFs[channel](catLLRng[0]) if isMC else None)) )) for channel, catLLRng in osLLRng.items())

        selections_2lep2jets = {}
        selections_2lep2bjets_NoMET = {}
        selections_2lep2bjets_METCut = {}
        for channel, (dilepton, catSel) in categories.items():
            
            TwoLeptonsTwoJets_Resolved = catSel.refine("TwoJet_{0}Sel_resolved".format(channel), cut=[ op.rng_len(AK4jets) > 1 ])
            TwoLeptonsTwoJets_Boosted = catSel.refine("OneJet_{0}Sel_boosted".format(channel), cut=[ op.rng_len(AK8jets) > 0 ])
            selections_2lep2jets[channel]= [TwoLeptonsTwoJets_Resolved, TwoLeptonsTwoJets_Boosted]
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #                                       Boosted Events : DeepDoubleB tagger
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            BoOstedJets = addBoOstedTagger( self, AK8jets, BoostedTopologiesWP) 
            for wp in sorted(safeget(BoostedTopologiesWP, 'DeepDoubleBvL').keys()):
                bJets_boosted_DeepDoubleBvL=safeget(BoOstedJets, "DeepDoubleBvL", wp)
                _2Lep2bjets_boOsted_NoMETcut = { 
                        "DeepDoubleBvL{0}".format(wp)  :  
                                            TwoLeptonsTwoJets_Boosted.refine("TwoLeptonsTwoBjets_NoMETcut_DeepDoubleBvL{0}_{1}_Boosted".format(wp, channel), 
                                            cut=[ op.rng_len(bJets_boosted_DeepDoubleBvL) > 0],
                                            weight=( getBoOstedWeight(self, era, 'DeepDoubleBvL', wp, AK8jets) if isMC else None))
                                        }

                _2Lep2bjets_boOsted = dict((key, selNoMET.refine("TwoLeptonsTwoBjets_{0}_{1}_Boosted".format(key, channel), cut=[ corrMET.pt < 80. ])) for key, selNoMET in _2Lep2bjets_boOsted_NoMETcut.items())
                

            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #                               Resolved : DeepCSV & DeepFlavour (L, M, T)   ---- Boosted :DeepCSV (L, M)
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            resolved_2lep2bjets_nomet = {}
            boosted_2lep2bjets_nomet = {}

            resolved_2lep2bjets_withmet = {}
            boosted_2lep2bjets_withmet = {}
            
            for wp in WorkingPoints: 
                # Get the best AK4 JETS 
                GetBestJetPair(bestDeepCSVPair,"DeepCSV", wp)
                GetBestJetPair(bestDeepFlavourPair,"DeepFlavour", wp)
                bestJetPairs["DeepCSV"]=bestDeepCSVPair
                bestJetPairs["DeepFlavour"]=bestDeepFlavourPair
                print ("bestJetPairs AK4--->", bestJetPairs, wp)
                print ("bestJetPairs_deepcsv  AK4--->", bestJetPairs["DeepCSV"][0], bestJetPairs["DeepCSV"][1], wp)
                print ("bestJetPairs_deepflavour  AK4 --->", bestJetPairs["DeepFlavour"][0],bestJetPairs["DeepFlavour"][1], wp)
                # resolved 
                bJets_resolved_PassdeepflavourWP=safeget(bjets_resolved, "DeepFlavour", wp)
                bJets_resolved_PassdeepcsvWP=safeget(bjets_resolved, "DeepCSV", wp)
                # boosted
                bJets_boosted_PassdeepcsvWP=safeget(bjets_boosted, "DeepCSV", wp)

                
                                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                #               Final  slection : 2 leptons ( opposite sign) + 2 jets (resolved or boosted) + NoMET cut
                                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                TwoLeptonsTwoBjets_NoMETCut_Res = {
                    "DeepFlavour{0}".format(wp) :  TwoLeptonsTwoJets_Resolved.refine("TwoLeptonsTwoBjets_NoMETcut_DeepFlavour{0}_{1}_Resolved".format(wp, channel),
                                                                        cut=[ op.rng_len(bJets_resolved_PassdeepflavourWP) > 1 ],
                                                                        weight=([ deepBFlavScaleFactor(bJets_resolved_PassdeepflavourWP[0]), 
                                                                                  deepBFlavScaleFactor(bJets_resolved_PassdeepflavourWP[1]) ]if isMC else None)),
                    "DeepCSV{0}".format(wp)     :  TwoLeptonsTwoJets_Resolved.refine("TwoLeptonsTwoBjets_NoMETcut_DeepCSV{0}_{1}_Resolved".format(wp, channel), 
                                                                        cut=[ op.rng_len(bJets_resolved_PassdeepcsvWP) > 1 ],
                                                                        weight=([ deepB_AK4ScaleFactor(bJets_resolved_PassdeepcsvWP[0]), 
                                                                                  deepB_AK4ScaleFactor(bJets_resolved_PassdeepcsvWP[1]) ]if isMC else None))
                                                }


                TwoLeptonsTwoBjets_NoMETCut_Boo = {
                    "DeepCSV{0}".format(wp)     :  TwoLeptonsTwoJets_Boosted.refine("TwoLeptonsTwoBjets_NoMETcut_DeepCSV{0}_{1}_Boosted".format(wp, channel), 
                                                                        cut=[ op.rng_len(bJets_boosted_PassdeepcsvWP) > 0])
                                                                        # FIXME ! can't pass boosted jets SFs with current version ---> move to v7  
                                                                        #weight=([ deepB_AK8ScaleFactor(bJets_boosted_PassdeepcsvWP[0]), 
                                                                        #          deepB_AK8ScaleFactor(bJets_boosted_PassdeepcsvWP[1]) ]if isMC else None))
                                                }
                resolved_2lep2bjets_nomet [wp] = TwoLeptonsTwoBjets_NoMETCut_Res
                boosted_2lep2bjets_nomet [wp] = TwoLeptonsTwoBjets_NoMETCut_Boo
                selections_2lep2bjets_NoMET[channel] = [ resolved_2lep2bjets_nomet, boosted_2lep2bjets_nomet]
                                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                #               Final  slection : 2 leptons ( opposite sign) + 2 jets (resolved or boosted) + MET cut < 80. GeV
                                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                
                TwoLeptonsTwoBjets_Res = dict((key, selNoMET.refine("TwoLeptonsTwoBjets_{0}_{1}_Resolved".format(key, channel), cut=[ corrMET.pt < 80. ])) for key, selNoMET in TwoLeptonsTwoBjets_NoMETCut_Res.items())
                TwoLeptonsTwoBjets_Boo = dict((key, selNoMET.refine("TwoLeptonsTwoBjets_{0}_{1}_Boosted".format(key, channel), cut=[ corrMET.pt < 80. ])) for key, selNoMET in TwoLeptonsTwoBjets_NoMETCut_Boo.items())
                
                resolved_2lep2bjets_withmet [wp] = TwoLeptonsTwoBjets_Res
                boosted_2lep2bjets_withmet [wp] = TwoLeptonsTwoBjets_Boo
                selections_2lep2bjets_METCut[channel] = [ resolved_2lep2bjets_withmet, boosted_2lep2bjets_withmet]
        return noSel, PUWeight, corrMET, muons, electrons, AK4jets, AK8jets, bjets_resolved, bjets_boosted, categories, WorkingPoints, selections_2lep2bjets_METCut, selections_2lep2bjets_NoMET, selections_2lep2jets
