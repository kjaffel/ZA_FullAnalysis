from bamboo.analysismodules import NanoAODHistoModule
from bamboo.analysisutils import makeMultiPrimaryDatasetTriggerSelection
from bamboo.scalefactors import binningVariables_nano

from bamboo import treefunctions as op
from bamboo.plots import EquidistantBinning as EqB
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
from systematics import getTriggerSystematcis, get_tthDYreweighting
import HistogramTools as HT
from bambooToOls import Plot

from  ZAEllipses import MakeEllipsesPLots, MakeMETPlots, MakeExtraMETPlots, MakePuppiMETPlots
from EXtraPlots import MakeTriggerDecisionPlots, MakeBestBJetsPairPlots, MakeHadronFlavourPLots
from BtagEfficiencies_BTV import MakeBtagEfficienciesPlots
#from ControlPLots import makeControlPlotsForZpic, makeControlPlotsForBasicSel, makeControlPlotsForFinalSel, makeJetPlots, makeBJetPlots, makeJetmultiplictyPlots
from ControlPLots import *
from boOstedEvents import addBoOstedTagger, getBoOstedWeight
from extraplots2017 import zoomplots, ptcuteffectOnJetsmultiplicty, choosebest_jetid_puid, varsCutsPlotsforLeptons, LeptonsInsideJets
from scalefactorslib import all_scalefactors
from za_selections import get_selections

binningVariables = {
      "Eta"       : lambda obj : obj.eta
    , "ClusEta"   : lambda obj : obj.eta + obj.deltaEtaSC
    , "AbsEta"    : lambda obj : op.abs(obj.eta)
    , "AbsClusEta": lambda obj : op.abs(obj.eta + obj.deltaEtaSC)
    , "Pt"        : lambda obj : obj.pt
    }

puScenarios = {
    "2016" : "Moriond17",
    "2017" : "Fall17",
    "2018" : "Autumn18"
    }

puIDSFLib = {
        f"{year}_{wp}" : {
            f"{eom}_{mcsf}" : os.path.join('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_',
                "PileupJetID", "fromPieter", f"PUID_80X_{eom}_{mcsf}_{year}_{wp}.json")
            for eom in ("eff", "mistag") for mcsf in ("mc", "sf")
        }
    for year in ("2016", "2017", "2018") for wp in "LMT"
    }

import bamboo.scalefactors

def makePUIDSF(jets, year=None, wp=None, wpToCut=None):
    sfwpyr = puIDSFLib[f"{year}_{wp}"]
    sf_eff = bamboo.scalefactors.get_scalefactor("lepton", "eff_sf"   , sfLib=sfwpyr, paramDefs=bamboo.scalefactors.binningVariables_nano)
    sf_mis = bamboo.scalefactors.get_scalefactor("lepton", "mistag_sf", sfLib=sfwpyr, paramDefs=bamboo.scalefactors.binningVariables_nano)
    eff_mc = bamboo.scalefactors.get_scalefactor("lepton", "eff_mc"   , sfLib=sfwpyr, paramDefs=bamboo.scalefactors.binningVariables_nano)
    mis_mc = bamboo.scalefactors.get_scalefactor("lepton", "mistag_mc", sfLib=sfwpyr, paramDefs=bamboo.scalefactors.binningVariables_nano)
    jets_m50 = op.select(jets, lambda j : j.pt < 50.)
    wFail = op.extMethod("scalefactorWeightForFailingObject", returnType="double")
    return op.rng_product(jets_m50, lambda j : op.switch(j.genJet.isValid,
        op.switch(wpToCut[wp](j), sf_eff(j), wFail(sf_eff(j), eff_mc(j))),
        op.switch(wpToCut[wp](j), sf_mis(j), wFail(sf_mis(j), mis_mc(j)))
        ))

def get_scalefactor(objType, key, periods=None, combine=None, additionalVariables=dict(), getFlavour=None, isElectron=False, systName=None):
    return scalefactors.get_scalefactor(objType, key, periods=periods, combine=combine, 
                                        additionalVariables=additionalVariables, 
                                        sfLib=all_scalefactors, 
                                        paramDefs=binningVariables, 
                                        getFlavour=getFlavour,
                                        isElectron=isElectron,
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


class NanoHtoZA(NanoAODHistoModule):
    """ H->Z(ll)A(bb) analysis for the FullRunII using NanoAODv5 """
    
    def __init__(self, args):
        super(NanoHtoZA, self).__init__(args)
        self.plotDefaults = {
                            "y-axis"           : "Events",
                            "log-y"            : "both",
                            "y-axis-show-zero" : True,
                            "save-extensions"  : ["pdf", "png"],
                            "show-ratio"       : True,
                            "sort-by-yields"   : False,
                            }

        self.doSysts = self.args.systematic
    def addArgs(self, parser):
        super(NanoHtoZA, self).addArgs(parser)
        parser.add_argument("-s", "--systematic", action="store_true", help="Produce systematic variations")
        parser.add_argument("--backend", type=str, default="dataframe", help="Backend to use, 'dataframe' (default) or 'lazy'")

    def prepareTree(self, tree, sample=None, sampleCfg=None):
        era = sampleCfg.get("era") if sampleCfg else None
        isMC = self.isMC(sample)
        metName = "METFixEE2017" if era == "2017" else "MET"
        ## initializes tree.Jet.calc so should be called first (better: use super() instead)
        # JEC's Recommendation for Full RunII: https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC
        # JER : -----------------------------: https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
        from bamboo.treedecorators import NanoAODDescription, nanoRochesterCalc, nanoJetMETCalc, nanoJetMETCalc_METFixEE2017

        tree,noSel,be,lumiArgs = NanoAODHistoModule.prepareTree(self, tree, sample=sample, sampleCfg=sampleCfg, description=NanoAODDescription.get("v5", year=(era if era else "2016"), isMC=isMC, systVariations=[ nanoRochesterCalc, (nanoJetMETCalc_METFixEE2017 if era == "2017" else nanoJetMETCalc) ]),lazyBackend=(self.args.backend == "lazy")) ## will do Jet and MET variations, and the Rochester correction
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
                "DoubleEG"   : [ tree.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL, # loosely isolated
                                 #tree.HLT.DoubleEle33_CaloIdL_MW,
                                 ], # the MW refers to the pixel match window being "medium window" working point
                                # also require additional HLT Zvtx Efficiency Scale Factor 
                                    
                "MuonEG"     : [ #tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,  #  Not for Era B
                                 tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
                                 
                                 # tree.HLT.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,  # Not for Era B
                                 tree.HLT.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ,
                                 
                                 #tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,   # Not for Era B
                                 tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ ],
                
                # FIXME : if you want to include them need to include the primary dataset too !!
                #"SingleElectron": [ tree.HLT.Ele35_WPTight_Gsf,
                #                    tree.HLT.Ele28_eta2p1_WPTight_Gsf_HT150 ],
                #"SingleMuon" :    [ tree.HLT.IsoMu27,
                #                    tree.HLT.Mu50   ],

                
            }
            
            if "2017B" not in sample:
             ## all are removed for 2017 era B
                triggersPerPrimaryDataset["MuonEG"] += [ 
                        tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,
                        tree.HLT.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,
                        tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL ]
                
                triggersPerPrimaryDataset["DoubleMuon"] += [ 
                        tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8 ]

                triggersPerPrimaryDataset["DoubleEG"] += [ 
                        tree.HLT.DiEle27_WPTightCaloOnly_L1DoubleEG ]

            #if "2017B" not in sample and "2017C" not in sample:
            #    triggersPerPrimaryDataset["DoubleEG"] += [ 
            #            tree.HLT.DoubleEle25_CaloIdL_MW ]

            if self.isMC(sample):
                jec="Fall17_17Nov2017_V32_MC"
                smear="Fall17_V3_MC"
                jesUncertaintySources=["Total"]

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
                                                  cut=(op.OR(*chain.from_iterable(triggersPerPrimaryDataset.values()))), 
                                                  autoSyst=self.doSysts)

            if self.doSysts:
                logger.info("Adding QCD scale variations, ISR and FSR ")
                noSel = utils.addTheorySystematics(self, tree, noSel)
        else:
            noSel = noSel.refine("withTrig", cut=(makeMultiPrimaryDatasetTriggerSelection(sample, triggersPerPrimaryDataset)))
       

        return tree,noSel,be,lumiArgs
    
    def definePlots(self, t, noSel, sample=None, sampleCfg=None):    
        from bamboo.analysisutils import forceDefine
        #from bamboo.plots import Plot
        from bambooToOls import Plot
        from bamboo.plots import CutFlowReport
        from bamboo.plots import EquidistantBinning as EqB
        from bamboo import treefunctions as op
        from bamboo.analysisutils import makePileupWeight
        from METFilter_xyCorr import METFilter, METcorrection

        isMC = self.isMC(sample)
        era = sampleCfg.get("era") if sampleCfg else None
        noSel = noSel.refine("passMETFlags", cut=METFilter(t.Flag, era, isMC) )
        puWeightsFile = None
        mcprofile= None
        yield_object = makeYieldPlots()


        if era == "2016":
            sfTag ="94X"
            suffix = '2016_Moriond17'
            puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/", "puweights2016_Moriond17.json")
       
        # details here: https://cp3-mm.irmp.ucl.ac.be/cp3-llbb/pl/w9srgswcabf1xfzxxnw9sjzt4e
        elif era == "2017":
            sfTag="94X"
            suffix = '2017_Fall17'
            if sample in ['DYJetsToLL_M-10to50', 'ST_tW_antitop_5f', 'ZH_HToBB_ZToLL', 'ggZH_HToBB_ZToLL',  'WWToLNuQQ', 'WZZ', 'TTWJetsToLNu', 'TTZToLLNuNu']:
                if "pufile" not in sampleCfg:
                    raise KeyError("Could not find 'pufile' entry for sample %s in the YAML file"%sampleCfg["sample"])
                mcprofile= os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/mcprofile/", "%s_2017.json"%sample)
            else:
                puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/", "puweights2017_Fall17.json")
        
        elif era == "2018":
            sfTag="102X"
            suffix = '2018_Autumn18'
            puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/", "puweights2018_Autumn18.json")
        
        #if not os.path.exists(puWeightsFile) and mcprofile is None :
        #    raise RuntimeError("Could not find pileup file %s"%puWeightsFile)
        
        if self.isMC(sample):
            if mcprofile is not None:
                PUWeight = makePileupWeight(mcprofile, t.Pileup_nTrueInt, variation="Nominal",
                                                   nameHint="puWeight_{0}".format(sample.replace('-','_')))
            else:
                PUWeight = makePileupWeight(puWeightsFile, t.Pileup_nTrueInt, systName="puweights%s"%suffix)
            noSel = noSel.refine("puWeight", weight=PUWeight)

        #top reweighting :
        if era != '2016' and self.isMC(sample) and sampleCfg["group"] in ['ttbar_FullLeptonic', 'ttbar_SemiLeptonic', 'ttbar_FullHadronic']:
            # https://indico.cern.ch/event/904971/contributions/3857701/attachments/2036949/3410728/TopPt_20.05.12.pdf
            genTop_pt = op.select(t.GenPart, lambda gp : op.AND((gp.statusFlags & (0x1<<13)), gp.pdgId==6))
            gen_antiTop_pt = op.select(t.GenPart, lambda gp : op.AND((gp.statusFlags & (0x1<<13)), gp.pdgId==-6))
            
            # func not from the PAG 
            # TODO for 2016 there's another one and you should produce yor own folowing
            # https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopPtReweighting#Use_case_3_ttbar_MC_is_used_to_m 
            scalefactor = lambda t : op.exp(-2.02274e-01 + 1.09734e-04*t.pt -1.30088e-07*t.pt**2 + (5.83494e+01/(t.pt+1.96252e+02)))
            top_weight = lambda top, antitop : op.sqrt(scalefactor(top)*scalefactor(antitop))
                
            noSel = noSel.refine("top_reweighting", weight=top_weight(genTop_pt[0], gen_antiTop_pt[0]))

                
        plots = []
        gen_ptll_nlo = None
        gen_ptll_lo = None
        from reweightDY import Plots_gen
        if era=='2016':
            DYsamples= ["DYJetsToLL_0J", "DYJetsToLL_1J", "DYJetsToLL_2J"] 
        else:
            DYsamples= ["DYToLL_0J", "DYToLL_1J", "DYToLL_2J"] 
        # it will crash if evaluated when there are no two leptons in the matrix element
        if sample in DYsamples:
            genLeptons_hard = op.select(t.GenPart, lambda gp : op.AND((gp.statusFlags & (0x1<<7)), op.in_range(10, op.abs(gp.pdgId), 17)))
            gen_ptll_nlo = (genLeptons_hard[0].p4+genLeptons_hard[1].p4).Pt()
            
            forceDefine(gen_ptll_nlo, noSel)
            plots.extend(Plots_gen( self, gen_ptll_nlo, noSel, "noSel", sample))
            plots.extend(Plot.make1D("nGenLeptons_hard", op.rng_len(genLeptons_hard), noSel, EqB(5, 0., 5.),  title="nbr genLeptons_hard [GeV]")) 
        
        #elif sampleCfg["group"] == "DYJetsToLL_M-10to50":
        #   gen_ptll_lo = (genLeptons_hard[0].p4+genLeptons_hard[1].p4).Pt()
        #   forceDefine(gen_ptll_lo, noSel)
        
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
            #mutrackingSF =  get_scalefactor("lepton", ("muon_{0}_{1}".format(era, sfTag), "id_TrkHighPtID_newTuneP"), systName="mutrk")
        #Wp  // 2016: Electron_cutBased_Sum16==3  -> medium     // 2017 -2018  : Electron_cutBased ==3   --> medium ( Fall17_V2)
        # asking for electrons to be in the Barrel region with dz<1mm & dxy< 0.5mm   //   Endcap region dz<2mm & dxy< 0.5mm 
        # cut-based ID Fall17 V2 the recomended one from POG for the FullRunII
        sorted_electrons = op.sort(t.Electron, lambda ele : -ele.pt)
        electrons = op.select(sorted_electrons, 
                                lambda ele : op.AND(ele.pt > 15., op.abs(ele.eta) < 2.5 , ele.cutBased>=3, op.abs(ele.sip3d) < 4., 
                                                    op.OR(op.AND(op.abs(ele.dxy) < 0.05, op.abs(ele.dz) < 0.1), 
                                                          op.AND(op.abs(ele.dxy) < 0.05, op.abs(ele.dz) < 0.2) ))) 
       # cuts =[]
       # if era == '2017': 
       #     cuts.append(op.OR(
       #                         op.AND(t.HLT.Ele32_WPTight_Gsf_L1DoubleEG, 
       #                                 op.rng_any(t.TrigObj, lambda obj: op.AND(op.deltaR(obj.p4, ele_kin[0].p4) < 0.1, obj.filterBits & 1024))),
       #                         t.HLT.Ele28_eta2p1_WPTight_Gsf_HT150))
       # electrons = op.select( ele_kin, cuts)
       # 
        elMediumIDSF = get_scalefactor("lepton", ("electron_{0}_{1}".format(era,sfTag), "id_medium"), isElectron=True, systName="elid")
        # FIXME  Need to be careful I didn't pass this before for 2016 -- and the plots are perfect  **** need to be tested *** 
        
        elRecoSF_splitby_Hi_LO_pT = False
        elRecoSF_version = 'POG' # Be careful the version from tth is `LOOSE` version 

        if elRecoSF_splitby_Hi_LO_pT == True and era !='2018':
            elRecoSF_lowpt = get_scalefactor("lepton", ("electron_{0}_{1}".format(era,sfTag), "reco_ptL20_%s"%elRecoSF_version), isElectron=True, systName="lowele_reco")
            elRecoSF_highpt = get_scalefactor("lepton", ("electron_{0}_{1}".format(era,sfTag), "reco_ptG20_%s"%elRecoSF_version), isElectron=True, systName="highele_reco")
        else:
            passpt = ('ptG20' if era !='2018' else(''))
            elRecoSF= get_scalefactor("lepton", ("electron_{0}_{1}".format(era,sfTag), "reco_%s_%s"%(passpt, elRecoSF_version)), isElectron=True, systName="ele_reco")


        elChargeSF = get_scalefactor("lepton", ("eChargeMisID", "eCharge_{0}".format(era)), isElectron=True, systName="ele_charge")
        
        MET = t.MET if era != "2017" else t.METFixEE2017
        corrMET=METcorrection(MET,t.PV,sample,era,self.isMC(sample))
        PuppiMET = t.PuppiMET 
        
        #######  select jets  
        ##################################
        #// 2016 - 2017 - 2018   ( j.jetId &2) ->      tight jet ID
        # For 2017 data, there is the option of "Tight" or "TightLepVeto", depending on how much you want to veto jets that overlap with/are faked by leptons
        puIdWP = "loOse"
        CleanJets_fromPileup =False
        deltaR = (0.3 if era == '2016' else (0.4))
        jet_puID_wp = {
                    "loOse"    : lambda j : j.puId & 0x4,
                    "medium"   : lambda j : j.puId & 0x2,
                    "tight"    : lambda j : j.puId & 0x1
                }
        
        sorted_AK4jets = op.sort(t.Jet, lambda j : -j.pt)
        if era == '2016':
            # j.jetId &2 means tight 
            AK4jetsSel = op.select(sorted_AK4jets, lambda j : op.AND(j.pt > 20., op.abs(j.eta) < 2.4, (j.jetId &2)))        
        else:
            #https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD
            # Jet ID flags bit1 is loose (always false in 2017 and 2018 since it does not exist), bit2 is tight, bit3 is tightLepVeto
            #jet.Id==6 means: pass tight and tightLepVeto ID. 
            
            #https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJetID
            #puId==0 means 000: fail all PU ID;
            #puId==4 means 100: pass loose ID, fail medium, fail tight;  
            #puId==6 means 110: pass loose and medium ID, fail tight; 
            #puId==7 means 111: pass loose, medium, tight ID.
            if CleanJets_fromPileup :
                AK4jetsSel = op.select(sorted_AK4jets, lambda j : op.AND(j.pt > 30, op.abs(j.eta) < 2.5, j.jetId & 4, op.switch(j.pt < 50, jet_puID_wp.get(puIdWP), op.c_bool(True)))) 
            else :
                AK4jetsSel = op.select(sorted_AK4jets, lambda j : op.AND(j.pt > 30, op.abs(j.eta) < 2.5, j.jetId & 4))
        # exclude from the jetsSel any jet that happens to include within its reconstruction cone a muon or an electron.
        AK4jets= op.select(AK4jetsSel, 
                            lambda j : op.AND(
                                            op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < deltaR )), 
                                            op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < deltaR ))))

        jets_noptcutSel = op.select(sorted_AK4jets, lambda j : op.AND(op.abs(j.eta) < 2.5, j.jetId & 4))
        jets_noptcut= op.select(jets_noptcutSel, 
                            lambda j : op.AND(
                                            op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < deltaR )), 
                                            op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < deltaR ))))
        
        if era != '2016' and CleanJets_fromPileup !=False:
             # FIXME : get_scalefactor works only on b-tagged jets --passed as lepton SFs for now      
            mcEffPUID = get_scalefactor("lepton", ("JetId_InHighPileup_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "puid_eff_mc_%s"% puIdWP[0].upper()), systName="JetpuID_eff_mc_%s"%puIdWP)
            mcMistagPUID = get_scalefactor("lepton", ("JetId_InHighPileup_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "puid_mistag_mc_%s"% puIdWP[0].upper()), systName="JetpuID_mistagrates_mc_%s"%puIdWP)
                
            dataEffPUID = get_scalefactor("lepton", ("JetId_InHighPileup_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "puid_eff_data_%s"% puIdWP[0].upper()), systName="JetpuID_eff_data_%s"%puIdWP)
            dataMistagPUID = get_scalefactor("lepton", ("JetId_InHighPileup_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "puid_mistag_data_%s"% puIdWP[0].upper()), systName="JetpuID_mistagrates_data_%s"%puIdWP)
    
            sfEffPUID = get_scalefactor("lepton", ("JetId_InHighPileup_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "puid_eff_sf_%s"% puIdWP[0].upper()), systName="JetpuID_eff_sf_%s"%puIdWP)
            sfMistagPUID = get_scalefactor("lepton", ("JetId_InHighPileup_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "puid_mistag_sf_%s"% puIdWP[0].upper()), systName="JetpuID_mistagrates_sf_%s"%puIdWP)
            
            if isMC:
                effPUID = lambda j : op.switch(j.genJet.isValid, mcEffPUID(j), mcMistagPUID(j))
                data_effPUID = lambda j : op.switch(j.genJet.isValid, dataEffPUID(j), dataMistagPUID(j))
                sfPUID = lambda j : op.switch(j.genJet.isValid, sfEffPUID(j), sfMistagPUID(j))
                    
                #puidWeight = op.rng_product( AK4jets, lambda j : op.switch(j.puId == puid, sfPUID(j), (1.-sfPUID(j)*effPUID(j))/(1.-effPUID(j))))
                puidWeight = op.rng_product( AK4jets, lambda j : op.switch(jet_puID_wp.get("loOse"), (sfPUID(j)*data_effPUID(j))/effPUID(j), (1.-sfPUID(j)*data_effPUID(j))/(1.-effPUID(j))))

        cleaned_AK4JetsByDeepFlav = op.sort(AK4jets, lambda j: -j.btagDeepFlavB)
        cleaned_AK4JetsByDeepB = op.sort(AK4jets, lambda j: -j.btagDeepB)

        # Boosted Region
        sorted_AK8jets=op.sort(t.FatJet, lambda j : -j.pt)
        # ask for two subjet to be inside the fatjet
        # The AK8 jets are required to have the nsubjettiness parameters tau2/tau1< 0.5 to be consistent with an AK8 jet having two subjets.
        AK8jetsSel = op.select(sorted_AK8jets, 
                                lambda j : op.AND(j.pt > 200., op.abs(j.eta) < 2.4, (j.jetId &2), 
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
        # Need to be careful; as the boosted have only DeepCSV as tagger with WPs 'cut' same as AK4jets in resolved region , only L and M are available 
        WorkingPoints = ["M"]
        SFsperiod_dependency = False # FIXME 
        btagging_Onboth_subjets = True
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
                    if btagging_Onboth_subjets :
                        bJets_AK8_deepcsv[wp] = op.select(cleaned_AK8JetsByDeepB, 
                                                            lambda j : op.AND(j.subJet1.btagDeepB >= btagging[tagger][era][idx] , 
                                                                              j.subJet2.btagDeepB >= btagging[tagger][era][idx]))   
                    else:
                        bJets_AK8_deepcsv[wp] = op.select(cleaned_AK8JetsByDeepB, lambda j : j.btagDeepB >= btagging[tagger][era][idx]) 
                    
                    Jet_DeepCSVBDis = { "BTagDiscri": lambda j : j.btagDeepB }
                    subJet_DeepCSVBDis = { "BTagDiscri": lambda j : op.AND(j.subJet1.btagDeepB, j.subJet2.btagDeepB) }
                    
                    if era == '2017' and SFsperiod_dependency :
                        deepB_AK4ScaleFactor = get_scalefactor("jet", ("btag_2017_94X", "DeepCSV_{1}_period_dependency".format(suffix)), 
                                                    additionalVariables=Jet_DeepCSVBDis,
                                                    getFlavour=(lambda j : j.hadronFlavour),
                                                    combine ="weight",
                                                    systName="DeepCSV{0}_SFsperiod_dependency".format(wp))  
                    else:
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
                "ElMu" : op.combine((electrons, muons), pred=lambda ele,mu : op.AND(LowMass_cut(ele, mu), ele.pt > mu.pt )),
                "MuEl" : op.combine((muons, electrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), mu.pt > ele.pt )),
                
                #"comb" : op.combine((muons, electrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), osdilep_Z(mu,ele))),
                
                #"MuMu" : op.combine((muons, muons), pred=lambda mu1, mu2 : op.AND(osdilep_Z(mu1, mu2), mu1.pt > 25.)),
                #"ElEl" : op.combine((electrons, electrons), pred=lambda ele1, ele2 : op.AND(osdilep_Z(ele1, ele2), ele1.pt > 25.)),
                #"ElMu" : op.combine((electrons, muons), pred=lambda ele,mu : op.AND(LowMass_cut(ele, mu), osdilep_Z(ele,mu), ele.pt > mu.pt , ele.pt > 25.)),
                #"MuEl" : op.combine((muons, electrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), osdilep_Z(mu,ele), mu.pt > ele.pt, mu.pt > 20.))
                }
         
        # FIXME maybe for 2017 or 2018 --> The leading pT for the �µ or µe channel should be above 20 Gev !
        hasOSLL_cmbRng = lambda cmbRng : op.AND(op.rng_len(cmbRng) > 0, cmbRng[0][0].pt > 25.) 
        #hasOSLL_cmbRng = lambda cmbRng : op.rng_len(cmbRng) > 0
        
        ## helper selection (OR) to make sure jet calculations are only done once
        hasOSLL = noSel.refine("hasOSLL", cut=op.OR(*( hasOSLL_cmbRng(rng) for rng in osLLRng.values())))
       
        forceDefine(t._Jet.calcProd, hasOSLL)
        forceDefine(getattr(t, "_{0}".format("MET" if era != "2017" else "METFixEE2017")).calcProd, hasOSLL)
        
        L1Prefiring = 1.
        if era in ["2016", "2017"]:
            L1Prefiring = getL1PreFiringWeight(t) 
        
        #single_mutrig = get_scalefactor("lepton", ("mutrig_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "single_muon"), combine="weight", systName="single_mutrig")
        #single_eletrig = get_scalefactor("lepton", ("eletrig_{0}_94X".format(era).replace("94X", "102X" if era=="2018" else "94X"), "single_electron"), combine="weight", systName="single_eletrig")
        
        version = None
        if version == None or (version =='tth' and era=='2018'): # will pass HHMoriond17 the default version 
            
            doubleMuTrigSF = get_scalefactor("dilepton", ("doubleMuLeg_HHMoriond17_2016"), systName="mumutrig")  
            doubleEleTrigSF = get_scalefactor("dilepton", ("doubleEleLeg_HHMoriond17_2016"), systName="eleltrig")
            elemuTrigSF = get_scalefactor("dilepton", ("elemuLeg_HHMoriond17_2016"), systName="elmutrig")
            mueleTrigSF = get_scalefactor("dilepton", ("mueleLeg_HHMoriond17_2016"), systName="mueltrig")
            
            #lepUnknownFlav= osLLRng.get("comb")[0][1]
            #if lepUnknownFlav.pt > 15. :
            #    mixed_catgoriesSFs = lambda ll : [ elMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[1]), elRecoSF(ll[0]), elemuTrigSF(ll), L1Prefiring]
            #elif lepUnknownFlav.pt > 10.:
            #    mixed_catgoriesSFs = lambda ll : [ muMediumIDSF(ll[0]), muMediumISOSF(ll[0]), elMediumIDSF(ll[1]), elRecoSF(ll[1]), mueleTrigSF(ll), L1Prefiring]
            
            llSFs = {
                "MuMu" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[0]), muMediumISOSF(ll[1]), doubleMuTrigSF(ll), L1Prefiring]),#, mutrackingSF(ll[0]), mutrackingSF(ll[1])]),
                "ElMu" : (lambda ll : [ elMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[1]), elRecoSF(ll[0]), elemuTrigSF(ll), L1Prefiring]), #, elChargeSF(ll[0])]),
                "MuEl" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumISOSF(ll[0]), elMediumIDSF(ll[1]), elRecoSF(ll[1]), mueleTrigSF(ll), L1Prefiring]), #,  elChargeSF(ll[1])]),
                "ElEl" : (lambda ll : [ elMediumIDSF(ll[0]), elMediumIDSF(ll[1]), elRecoSF(ll[0]), elRecoSF(ll[1]), doubleEleTrigSF(ll), L1Prefiring]) #FIXME, elChargeSF(ll[0]), elChargeSF(ll[1])]),
                #"comb" : ( mixed_catgoriesSFs)
                }
        else:
            # tth SFs and others ... 
            doubleMuTrigSF= getTriggerSystematcis(self, era, osLLRng.get('MuMu')[0], 'MuMu', version)
            doubleEleTrigSF = getTriggerSystematcis(self, era, osLLRng.get('ElEl')[0], 'ElEl', version)
            elemuTrigSF = getTriggerSystematcis(self, era, osLLRng.get('ElMu')[0], 'ElMu', version)
            mueleTrigSF = getTriggerSystematcis(self, era, osLLRng.get('MuEl')[0], 'MuEl', version)
            
            lepUnknownFlav= osLLRng.get("comb")[0][1]
            if lepUnknownFlav.pt > 15. :
                mixed_catgoriesSFs = getTriggerSystematcis(self, era, osLLRng.get('comb')[0], 'comb', version)

            llSFs = {
                "MuMu" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[0]), muMediumISOSF(ll[1]), doubleMuTrigSF, L1Prefiring]),
                "ElMu" : (lambda ll : [ elMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[1]), elRecoSF(ll[0]), elemuTrigSF, L1Prefiring]),#, elChargeSF(ll[0])]),
                "MuEl" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumISOSF(ll[0]),elMediumIDSF(ll[1]), elRecoSF(ll[1]), mueleTrigSF, L1Prefiring]),#, elChargeSF(ll[1])]),
                "ElEl" : (lambda ll : [ elMediumIDSF(ll[0]), elMediumIDSF(ll[1]), elRecoSF(ll[0]), elRecoSF(ll[1]), doubleEleTrigSF, L1Prefiring])#, elChargeSF(ll[0]), elChargeSF(ll[1])])
                }
        print ( llSFs) 
        categories = dict((channel, (catLLRng[0], hasOSLL.refine("hasOs{0}".format(channel), cut=hasOSLL_cmbRng(catLLRng), weight=(llSFs[channel](catLLRng[0]) if isMC else None)) )) for channel, catLLRng in osLLRng.items())

        make_ZpicPlots = True
        make_JetmultiplictyPlots = True
        make_JetschecksPlots = False
        make_JetsPlusLeptonsPlots = True
        make_DeepDoubleBPlots = False
        make_METPlots = True
        make_METPuppiPlots = False
        make_ttbarEstimationPlots = False
        make_ellipsesPlots = True
        make_bJetsPlusLeptonsPlots_METcut = True
        make_bJetsPlusLeptonsPlots_NoMETcut = False
        make_zoomplotsANDptcuteffect = False
        make_2017Checksplots = False
        make_LookInsideJets = False
        make_reconstructedVerticesPlots = False
        make_DYReweightingPlots_2017Only = False
        # don't forget to set these 
        split_DYWeightIn64Regions = False
        HighPileupJetIdWeight = None
        chooseJetsLen ='_at_least2Jets_'
        #chooseJetsLen = '_only2Jets_' 
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                               # more plots to invistagtes 2017 problems  
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if make_2017Checksplots :
            plots += choosebest_jetid_puid(self, t, muons, electrons, categories, era, sample, isMC)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                               # b- tagging studies 
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ## btagging efficiencies plots
        #plots.extend(MakeBtagEfficienciesPlots(self, jets, bjets, categories, era))

        for channel, (dilepton, catSel) in categories.items():
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                            # check low pt && high pt ele (< 20 GeV)- POG SFs
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            if era != '2018':
                ele_recoweight = None
                if channel =='ElEl':
                    ele_recoweight= [ elRecoSF_highpt(dilepton[0]), elRecoSF_lowpt(dilepton[1]), elRecoSF_highpt(dilepton[1])]
                if channel =='ElMu':
                    ele_recoweight = [elRecoSF_highpt(dilepton[0])]
                if channel =='MuEl':
                    ele_recoweight = [elRecoSF_lowpt(dilepton[1]), elRecoSF_highpt(dilepton[1])]
                refine_Oslepsel = catSel.refine( 'ele_reco_SF_ptlower20_%s'%channel, weight=(( ele_recoweight )if isMC else None))
                makeControlPlotsForZpic(self, refine_Oslepsel, dilepton, 'oslepSel_add_lowpt_eleRecoSF', channel, '_' )

            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # Zmass (2Lepton OS && SF ) 
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            plots += varsCutsPlotsforLeptons (self, dilepton, catSel, channel)
                
            optstex = ('$e^+e^-$' if channel=="ElEl" else( '$\mu^+\mu^-$' if channel =="MuMu" else( '$\mu^+e^-$' if channel=="MuEl" else('$e^+\mu^-$'))))
            yield_object.addYields(catSel,"hasOs%s"%channel,"OS leptons + $M_{ll}$ cut (channel : %s)"%optstex)
            plots.append(CutFlowReport("Os_%s"%channel, catSel))
            if make_ZpicPlots:
                plots.extend(makeControlPlotsForZpic(self, catSel, dilepton, 'oslepSel', channel, '_'))
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # Jets multiplicty  
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            if make_JetmultiplictyPlots :
                for sel, jet, reg in zip ([catSel, catSel], [AK4jets, AK8jets], ["resolved", "boosted"]):
                    plots.extend(makeJetmultiplictyPlots(self, catSel, AK4jets, channel,"_NoCutOnJetsLen_" + reg))
            
            # Inclusive selections *** boosted : at least 1 AK8jets  
            #                          resolved: at least 2 AK4jets  
            TwoLeptonsTwoJets_Resolved= catSel.refine("TwoJet_{0}Sel_resolved".format(channel), cut=[ op.rng_len(AK4jets) > 1])
            TwoLeptonsOneJet_Boosted = catSel.refine("OneJet_{0}Sel_boosted".format(channel), cut=[ op.rng_len(AK8jets) > 0 ])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # High Pileup JetId Weight 
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            
            if era != '2016' and CleanJets_fromPileup:
                TwoLeptonsTwoJets_Resolved_NopuWeight = TwoLeptonsTwoJets_Resolved
                if isMC:
                    pu_weight= makePUIDSF(AK4jets, era, wp=puIdWP[0].upper(), wpToCut=jet_puID_wp.get(puIdWP))
                    #pu_weight= op.switch(op.OR(op.in_range(30., AK4jets[0].pt, 50.), op.in_range(30, AK4jets[1].pt, 50.)), puidWeight, op.c_float(1.))
                TwoLeptonsTwoJets_Resolved = TwoLeptonsTwoJets_Resolved_NopuWeight.refine( "TwoJet_{0}Sel_resolved_inclusive_puWeight_{0}".format(channel, puIdWP), weight= pu_weight)
            # N.B : boosted is unlikely to have pu jets ; jet pt > 200 in the boosted cat 
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            
            jlenOpts_resolved = (' at least 2' if chooseJetsLen=='_at_least2Jets_' else ( 'exactly 2'))
            yield_object.addYields(TwoLeptonsTwoJets_Resolved,"has2Lep2ResolvedJets_%s"%channel,"2 Lep(OS)+ %s AK4Jets + $M_{ll}$ cut (channel : %s)"%(jlenOpts_resolved, optstex))
            yield_object.addYields(TwoLeptonsOneJet_Boosted,"has2Lep1BoostedJets_%s"%channel,"2 Lep(OS)+ at least 1 AK8Jets+ $M_{ll}$ cut (channel : %s)"%optstex)
            
            plots.append(CutFlowReport("%sjj_resolved"%channel.lower(), TwoLeptonsTwoJets_Resolved))
            plots.append(CutFlowReport("%sjj_boosted"%channel.lower(), TwoLeptonsOneJet_Boosted))
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                     # DY - Reweighting  
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #ptllDYW_NLO = (0.876979+gen_ptll*(4.11598e-03)-(2.35520e-05)*gen_ptll*gen_ptll)*(1.10211 * (0.958512 - 0.131835*TMath::Erf((gen_ptll-14.1972)/10.1525)))*(gen_ptll<140)+0.891188*(gen_ptll>=140)
            #ptllDYW_LO  = (8.61313e-01+gen_ptll*4.46807e-03-1.52324e-05*gen_ptll*gen_ptll)*(1.08683 * (0.95 - 0.0657370*TMath::Erf((gen_ptll-11.)/5.51582)))*(gen_ptll<140)+1.141996*(gen_ptll>=140)
            #TwoLeptonsTwoJets_Resolved_DYReweighting = TwoLeptonsTwoJets_Resolved.refine("{0}_2lep2jets_DYweight_fromtth".format(channel), weight=(get_tthDYreweighting(self, era, sample, AK4jets)))
            from reweightDY import plotsWithDYReweightings, Plots_gen, PLots_withtthDYweight
            if channel in ['ElEl', 'MuMu']:
                if sample in DYsamples:
                    plots.extend(Plots_gen( self, gen_ptll_nlo, TwoLeptonsTwoJets_Resolved, '%s_resolved_2lep2jSel'%channel, sample))
                plots.extend(PLots_withtthDYweight(self, channel, dilepton, AK4jets, TwoLeptonsTwoJets_Resolved, 'resolved', sample, era))
                if make_DYReweightingPlots_2017Only and era =='2017':
                    plots.extend(plotsWithDYReweightings(self, AK4jets, dilepton, TwoLeptonsTwoJets_Resolved, channel, 'resolved', sample, split_DYWeightIn64Regions))
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                # more Investigation pffff ... :(
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            
            if make_zoomplotsANDptcuteffect:
                plots.extend(ptcuteffectOnJetsmultiplicty(self, catSel, dilepton, jets_noptcut, AK4jets, corrMET, era, channel))
                plots.extend(zoomplots(self, catSel, TwoLeptonsTwoJets_Resolved, dilepton, AK4jets, 'resolved', channel)) 
            
            if make_METPuppiPlots:
                plots.extend(MakePuppiMETPlots( self, PuppiMET, TwoLeptonsTwoJets_Resolved, channel))
            if make_LookInsideJets:
                plots.extend(LeptonsInsideJets(self, AK4jets, TwoLeptonsTwoJets_Resolved, channel))

            if make_reconstructedVerticesPlots:
                plots.extend( makePrimaryANDSecondaryVerticesPlots( self, t, catSel, channel))
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                # Control Plots in boosted and resolved  
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # ----- plots : mll, mlljj, mjj, nVX, pT, eta  : basic selection plots ------
            for sel, jet, reg in zip ([TwoLeptonsTwoJets_Resolved, TwoLeptonsOneJet_Boosted], [AK4jets, AK8jets], ["resolved", "boosted"]):
                
                if make_JetschecksPlots:
                    #plots.extend(makedeltaRPlots( self, sel, jet, dilepton, channel, reg))
                    plots.extend(makeJetmultiplictyPlots(self, sel, jet, channel, reg))
                if make_JetsPlusLeptonsPlots:
                    plots.extend(makeJetPlots(self, sel, jet, channel, reg, era))
                    plots.extend(makeControlPlotsForBasicSel(self, sel, jet, dilepton, channel, reg))
                if make_ZpicPlots:
                    plots.extend(makeControlPlotsForZpic(self, sel, dilepton, 'lepplusjetSel', channel, reg))
            
            #FIXME errors when passing these plots ....
            #plots.extend(makeAK8JetsPLots(self, TwoLeptonsOneJet_Boosted, AK8jets, channel))
            
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # DeepDoubleB for boosted events (L, M1, M2, T1, T2)  wp   
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            if make_DeepDoubleBPlots:
                BoOstedJets = addBoOstedTagger( self, AK8jets, BoostedTopologiesWP) 
                for wp in sorted(safeget(BoostedTopologiesWP, 'DeepDoubleBvL').keys()):
                    bJets_boosted_DeepDoubleBvL=safeget(BoOstedJets, "DeepDoubleBvL", wp)
                    _2Lep2bjets_boOsted_NoMETcut = { 
                        "DeepDoubleBvL{0}".format(wp)  :  
                                            TwoLeptonsOneJet_Boosted.refine("TwoLeptonsOneBjets_NoMETcut_DeepDoubleBvL{0}_{1}_Boosted".format(wp, channel), 
                                            cut=[ op.rng_len(bJets_boosted_DeepDoubleBvL) > 0],
                                            weight=( getBoOstedWeight(self, era, 'DeepDoubleBvL', wp, AK8jets) if isMC else None))
                                        }

                    _2Lep2bjets_boOsted = dict((key, selNoMET.refine("TwoLeptonsOneBjets_{0}_{1}_Boosted".format(key, channel), cut=[ corrMET.pt < 80. ])) for key, selNoMET in _2Lep2bjets_boOsted_NoMETcut.items())
                    for sel, suffix in zip([ _2Lep2bjets_boOsted_NoMETcut, _2Lep2bjets_boOsted], [ '_NoMETCut_', '_METCut_']):
                        plots.extend(makeBJetPlots(self, sel, BoOstedJets, wp, channel, "boosted", suffix, era))
                        plots.extend(makeControlPlotsForFinalSel(self, sel, BoOstedJets, dilepton, wp, channel, "boosted", suffix))
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # DeepCSV for both boosted && resolved , DeepFlavour  
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    # No MET cut : selections 2 lep +2b-tagged jets
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # FIXME Wgt from DY can't pass on L, or T like this : problem with None
                TwoLeptonsTwoBjets_NoMETCut_Res = {
                    "DeepFlavour{0}".format(wp) :  TwoLeptonsTwoJets_Resolved.refine("TwoLeptonsTwoBjets_NoMETcut_DeepFlavour{0}_{1}_Resolved".format(wp, channel),
                                                                        cut=[ op.rng_len(bJets_resolved_PassdeepflavourWP) > 1 ],
                                                                        weight=([ deepBFlavScaleFactor(bJets_resolved_PassdeepflavourWP[0]), 
                                                                                  deepBFlavScaleFactor(bJets_resolved_PassdeepflavourWP[1]) 
                                                                                  #get_tthDYreweighting(self, era, sample, AK4jets, bJets_resolved_PassdeepflavourWP, wp)
                                                                                ] if isMC else None
                                                                                )),

                    "DeepCSV{0}".format(wp)     :  TwoLeptonsTwoJets_Resolved.refine("TwoLeptonsTwoBjets_NoMETcut_DeepCSV{0}_{1}_Resolved".format(wp, channel), 
                                                                        # remove boosted bjets that pass deepcsv WP
                                                                        cut=[ op.rng_len(bJets_resolved_PassdeepcsvWP) > 1, op.rng_len(bJets_boosted_PassdeepcsvWP) ==0],
                                                                        weight=([ deepB_AK4ScaleFactor(bJets_resolved_PassdeepcsvWP[0]), 
                                                                                  deepB_AK4ScaleFactor(bJets_resolved_PassdeepcsvWP[1])
                                                                                  #get_tthDYreweighting(self, era, sample, AK4jets, bJets_resolved_PassdeepcsvWP, wp)  
                                                                                ] if isMC else None
                                                                                ))
                                                }


                TwoLeptonsOneBjets_NoMETCut_Boo = {
                    "DeepCSV{0}".format(wp)     :  TwoLeptonsOneJet_Boosted.refine("TwoLeptonsOneBjets_NoMETcut_DeepCSV{0}_{1}_Boosted".format(wp, channel), 
                                                                        cut=[ op.rng_len(bJets_boosted_PassdeepcsvWP) > 0 ])
                                                                        # FIXME ! can't pass boosted jets SFs with current version ---> move to v7  
                                                                        #weight=([ get_tthDYreweighting(self, era, sample, AK8jets, bJets_boosted_PassdeepcsvWP, wp)
                                                                        #         deepB_AK8ScaleFactor(bJets_boosted_PassdeepcsvWP[0]), 
                                                                        #         deepB_AK8ScaleFactor(bJets_boosted_PassdeepcsvWP[1]) 
                                                                        #        ] if isMC else None))
                                                }
                
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    #  to optimize the MET cut 
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # pass signal && bkg  
                if make_METPlots:
                    for sel, reg in zip( [TwoLeptonsTwoBjets_NoMETCut_Res,TwoLeptonsOneBjets_NoMETCut_Boo], ["resolved", "boosted"]):
                        plots.extend(MakeMETPlots(self, sel, corrMET, MET, channel, reg))
                        plots.extend(MakeExtraMETPlots(self, sel, dilepton, MET, channel, reg))
                
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    #  refine previous selections for SR : with MET cut  < 80. 
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                TwoLeptonsTwoBjets_Res = dict((key, selNoMET.refine("TwoLeptonsTwoBjets_{0}_{1}_Resolved".format(key, channel), cut=[ corrMET.pt < 80. ])) for key, selNoMET in TwoLeptonsTwoBjets_NoMETCut_Res.items())
                TwoLeptonsOneBjets_Boo = dict((key, selNoMET.refine("TwoLeptonsOneBjets_{0}_{1}_Boosted".format(key, channel), cut=[ corrMET.pt < 80. ])) for key, selNoMET in TwoLeptonsOneBjets_NoMETCut_Boo.items())
                
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    #  TTbar Esttimation  
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # ----- For ttbar Estimation -----
                if make_ttbarEstimationPlots:
                    TwoLeptonsTwoBjets_Res_InHighMET = dict((key, selNoMET.refine("TwoLeptonsTwoBjets_{0}_{1}_Resolved_with_inverted_METcut".format(key, channel), cut=[ corrMET.pt > 80. ])) for key, selNoMET in TwoLeptonsTwoBjets_NoMETCut_Res.items())
                
                    for sel , met in zip([ TwoLeptonsTwoBjets_Res, TwoLeptonsTwoBjets_Res_InHighMET ], [ "METCut", "HighMET"]) :
                        plots.extend(makehistosforTTbarEstimation(self, sel, dilepton, bjets_resolved, wp, channel, "resolved", met))
                
                
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    #  Control Plots for  Final selections  : 2lep +2 bjets 
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    #  MET cut included 
                            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                JetType=( 'AK4' if reg=='resolved' else( 'AK8'))
                if make_bJetsPlusLeptonsPlots_METcut :
                    for sel, bjets, reg, jlen in zip([TwoLeptonsTwoBjets_Res, TwoLeptonsOneBjets_Boo], [bjets_resolved, bjets_boosted], ["resolved", "boosted"], [jlenOpts_resolved, 'at least 1']):
                        plots.extend(makeBJetPlots(self, sel, bjets, wp, channel, reg, "_METCut_", era))
                        plots.extend(makeControlPlotsForFinalSel(self, sel, bjets, dilepton, wp, channel, reg, "_METCut_"))
                   
                        if make_ellipsesPlots:
                            plots.extend(MakeEllipsesPLots(self, sel, bjets, dilepton, wp, channel, reg))
                    
                        for key in sel.keys():
                            yield_object.addYields(sel.get(key),"has2Lep2{0}BJets_METCut_{1}_{2}".format(reg.upper(), channel, key),"2 Lep(OS) + {0} {1}BJets {2} pass {3} + METcut (channel : {4})".format(jlen, JetType, reg, key, optstex))
                            plots.append(CutFlowReport("{0}jj_{1}_METCut_{2}".format(channel.lower(), key, reg), sel.get(key)))
                
                            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                                    #  NO MET cut  
                            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if make_bJetsPlusLeptonsPlots_NoMETcut :
                    # Control Plots, Yield Plots, FlowReport (passed to the postprocess)
                    for sel, bjets, reg, jlen in zip([TwoLeptonsTwoBjets_NoMETCut_Res, TwoLeptonsOneBjets_NoMETCut_Boo], [bjets_resolved, bjets_boosted], ["resolved", "boosted"], [jlenOpts_resolved, 'at least 1']):
                        
                        plots.extend(makeBJetPlots(self, sel, bjets, wp, channel, reg, "_NoMETCut_", era))
                        plots.extend(makeControlPlotsForFinalSel(self, sel, bjets, dilepton, wp, channel, reg, "_NoMETCut_"))
                    
                        for key in sel.keys():
                            yield_object.addYields(sel.get(key),"has2Lep2{0}BJets_NoMETCut_{1}_{2}".format(reg.upper(), channel, key),"2 Lep(OS) + {0} {1}BJets {2} pass {3} + NoMETcut (channel : {4})".format(jlen, JetType, reg, key, optstex))
                            plots.append(CutFlowReport("{0}jj_{1}_NoMETCut_{2}".format(channel.lower(), key, reg), sel.get(key)))
            
                #plots.extend(makeExtraFatJetBOostedPlots(self, TwoLeptonsOneBjets_Boo, bjets_boosted, wp, channel))
        
        plots.extend(yield_object.returnPlots())
        return plots

    def postProcess(self, taskList, config=None, workdir=None, resultsdir=None):
        from bamboo.plots import CutFlowReport, DerivedPlot
        import bambooToOls
        import json 

        # Get list of plots (taken from bamboo.HistogramsModule)
        #if not self.plotList:
        #    tup, smpName, smpCfg = self.getATree()
        #    tree, noSel, backend, runAndLS = self.prepareTree(tup, sample=smpName, sampleCfg=smpCfg)
        #    self.plotList = self.definePlots(tree, noSel, sample=smpName, sampleCfg=smpCfg)
            
        # memory usage 
        # FIXME I want to plots these ! 
        #start= timer()
        #end= timer()
        #maxrssmb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
        #logger.info(f"{len(self.plotList):d} plots defined in {end - start:.2f}s, max RSS: {maxrssmb:.2f}MB")
        #with open(os.path.join(resultsdir=".","memoryusage.json"%suffix), "w") as handle:
        #    json.dump(len(self.plotList), handle, indent=4)
        #    json.dump(maxrssmb, handle, indent=4)
        #    json.dump(end - start, handle, indent=4)

        # merge processes using their cross sections
        #utils.normalizeAndMergeSamples(self.plotList, self.readCounters, config, resultsdir, os.path.join(resultsdir, "output_sum.root"))
        
        # save generated-events for each samples--- > mainly needed for the DNN
        plotList_cutflowreport = [ ap for ap in self.plotList if isinstance(ap, CutFlowReport) ]
        bambooToOls.SaveCutFlowReports(config, plotList_cutflowreport, resultsdir, self.readCounters)

        # QCD scale variations .
        #for (inputs, output), kwargs in taskList:
        #    if self.doSysts and self.isMC(output):
        #        self.qcdScaleVariations= { f"qcdScalevar{i}" for i in [0, 1, 3, 5, 7, 8] }
        #        utils.produceMEScaleEnvelopes(self.plotList, self.qcdScaleVariations, os.path.join(resultsdir, output))
       
        
        # finally, run plotIt as defined in HistogramsModule
        # keep above your changes in the post-process 
        super(NanoHtoZA, self).postProcess(taskList, config, workdir, resultsdir)
        
        plotList_2D = [ ap for ap in self.plotList if ( isinstance(ap, Plot) or isinstance(ap, DerivedPlot) ) and len(ap.binnings) == 2 ]
        logger.debug("Found {0:d} plots to save".format(len(plotList_2D)))

        from bamboo.analysisutils import loadPlotIt
        p_config, samples, plots_2D, systematics, legend = loadPlotIt(config, plotList_2D, eras=self.args.eras, workdir=workdir, resultsdir=resultsdir, readCounters=self.readCounters, vetoFileAttributes=self.__class__.CustomSampleAttributes, plotDefaults=self.plotDefaults)
        from plotit.plotit import Stack
        from bamboo.root import gbl
        for plot in plots_2D:
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
        
        #for smpName, smpCfg in config["samples"].items():
        #    smpCfg.pop("files")

