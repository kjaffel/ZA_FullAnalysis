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

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_')
import utils
import HistogramTools as HT
from bambooToOls import Plot

from  ZAEllipses import MakeEllipsesPLots, MakeMETPlots, MakeExtraMETPlots
from EXtraPlots import MakeTriggerDecisionPlots, MakeBestBJetsPairPlots, MakeHadronFlavourPLots
from Btagging import MakeBtagEfficienciesPlots
#from ControlPLots import makeControlPlotsForZpic, makeControlPlotsForBasicSel, makeControlPlotsForFinalSel, makeJetPlots, makeBJetPlots, makeJetmultiplictyPlots
from ControlPLots import *

def localize_myanalysis(aPath, era="FullRunIIv1"):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ScaleFactors_{0}".format(era), aPath)

def localize_trigger(aPath):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "TriggerEfficienciesStudies", aPath)

binningVariables = {
      "Eta"       : lambda obj : obj.eta
    , "ClusEta"   : lambda obj : obj.eta + obj.deltaEtaSC
    , "AbsEta"    : lambda obj : op.abs(obj.eta)
    , "AbsClusEta": lambda obj : op.abs(obj.eta + obj.deltaEtaSC)
    , "Pt"        : lambda obj : obj.pt
    }

all_scalefactors = {
       ############################################
       # 2016 legacy:
       ############################################
       # Electrons:  https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaRunIIRecommendations#Fall17v2
       # Muons  :    https://twiki.cern.ch/twiki/bin/viewauth/CMS/MuonReferenceEffs2016LegacyRereco#Efficiencies
       # Btagging :  https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation2016Legacy
      
       "electron_2016_94X"  : dict((k,localize_myanalysis(v)) for k, v in chain(
                              dict(("id_{wp}".format(wp=wp.lower()), 
                                ("Electron_EGamma_SF2D_2016Legacy_{wp}_Fall17V2.json".format(wp=wp)))
                                for wp in ("Loose", "Medium", "Tight")).items())),
                                #for wp in ("Loose", "Medium", "Tight", "MVA80","MVA90", "MVA80noiso", "MVA90noiso")).items())),

        # DONE  --> updating the SFs with _stat & _syst   for 2016 and 2018 // 
        # DONE : for 2017 : ( missing correction in some bins !! ): no missing corr for mu iso_tight+id_medium the one i use --> should be fine
        # The recommendation is to use the nominal SF and uncertainties of closes pT bin. 
       "muon_2016_94X" : dict((k,( localize_myanalysis(v) 
                            if isinstance(v, str) 
                            else [ (eras, localize_myanalysis(path)) for eras,path in v ])) for k, v in chain(

                            dict(("id_{wp}".format(wp=wp.lower()), [ (tuple("Run2016{0}".format(ltr) for ltr in eras), 
                                "Muon_NUM_{wp}ID_DEN_genTracks_eta_pt_{uncer}_2016Run{era}.json".format(wp=wp, uncer=uncer, era=eras)) 
                                for eras in ("BCDEF", "GH") for uncer in ("syst", "stat")]) for wp in ("Loose", "Medium", "Tight")).items(),

                            dict(("id_{wp}_newTuneP".format(wp=wp.lower()), [ (tuple("Run2016{0}".format(ltr) for ltr in eras), 
                                "Muon_NUM_{wp}ID_DEN_genTracks_eta_pair_newTuneP_probe_pt_{uncer}_2016Run{era}.json".format(wp=wp, uncer=uncer, era=eras)) 
                                for eras in ("BCDEF", "GH") for uncer in ("syst", "stat")]) for wp in ("HighPt",)).items(),

                            dict(("iso_{isowp}_id_{idwp}".format(isowp=(isowp.replace("ID","")).lower(), idwp=(idwp.replace("ID","")).lower()),[ (tuple("Run2016{0}".format(ltr) for ltr in eras), 
                                "Muon_NUM_{isowp}RelIso_DEN_{idwp}_eta_pt_{uncer}_2016Run{era}.json".format(isowp=isowp, idwp=idwp,uncer=uncer, era=eras))
                                for eras in ("BCDEF", "GH") for uncer in (("syst","stat")if eras=="BCDEF" else ("stat",))]) 
                                for (isowp,idwp) in (("Loose", "LooseID"), ("Loose", "MediumID"), ("Loose", "TightIDandIPCut"),("Tight", "MediumID"), ("Tight", "TightIDandIPCut"))).items(),
                    
                            dict(("iso_{isowp}_id_{idwp}_newTuneP".format(isowp=isowp.lower(), idwp=idwp.lower()),[ (tuple("Run2016{0}".format(ltr) for ltr in eras), 
                                "Muon_NUM_{isowp}RelTkIso_DEN_{idwp}_eta_pair_newTuneP_probe_pt_{uncer}_2016Run{era}.json".format(isowp=isowp, idwp=idwp,uncer=uncer, era=eras))
                                for eras in ("BCDEF", "GH") for uncer in (("syst","stat")if eras=="BCDEF" else ("stat",))]) for (isowp,idwp) in (("Loose", "TightIDandIPCut"),)).items()
                        )),
      
       "btag_2016_94X" : dict((k,( tuple(localize_myanalysis(fv) for fv in v) 
                            if isinstance(v,tuple) and all(isinstance(fv, str) for fv in v)
                            else [ (eras, tuple(localize_myanalysis(fpath) for fpath in paths)) for eras,paths in v ])) for k, v in chain(
        ## Resolved:
            # DeepCSV , DeepJet
                            dict(("{algo}_{wp}".format(algo=algo, wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_{algo}_2016Legacy.json".format(wp=wp, flav=flav, calib=calib, algo=algo) 
                            for (flav, calib) in (("lightjets", "incl"), ("cjets", "comb"), ("bjets","comb")))) for wp in ("loose", "medium", "tight") for algo in ("DeepCSV", "DeepJet") ).items(),
        ## Boosted event topologies:
            # FIXME : to be passed later for nanov7
            # DeepCSV ( same WP as AK4jets in DeepCSV but different SFs : *** need to be careful ! )
                            dict(("subjet_{algo}_{wp}".format(algo=algo, wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_subjet_{algo}_2016Legacy.json".format(wp=wp, flav=flav, calib=calib, algo=algo) 
                            for (flav, calib) in (("lightjets", "incl"), ("cjets", "lt"), ("bjets","lt")))) for wp in ("loose", "medium") for algo in ("DeepCSV", ) ).items(),
                         )),
                

    #------- single muon trigger --------------
       "mutrig_2016_94X" : tuple(localize_trigger("{trig}_PtEtaBins_2016Run{eras}.json".format(trig=trig, eras=eras)) 
								  for trig in ("IsoMu24_OR_IsoTkMu24","Mu50_OR_TkMu50" ) for eras in ("BtoF", "GtoH")),
    #-------- double muon trigger ------------ 
       "doubleEleLeg_HHMoriond17_2016" : tuple(localize_trigger("{wp}.json".format(wp=wp)) 
                                            for wp in ("Electron_IsoEle23Leg", "Electron_IsoEle12Leg", "Electron_IsoEle23Leg", "Electron_IsoEle12Leg")),

       "doubleMuLeg_HHMoriond17_2016" : tuple(localize_trigger("{wp}.json".format(wp=wp)) 
                                            for wp in ("Muon_DoubleIsoMu17Mu8_IsoMu17leg", "Muon_DoubleIsoMu17TkMu8_IsoMu8legORTkMu8leg", "Muon_DoubleIsoMu17Mu8_IsoMu17leg", 
                                                "Muon_DoubleIsoMu17TkMu8_IsoMu8legORTkMu8leg")),

       "mueleLeg_HHMoriond17_2016" : tuple(localize_trigger("{wp}.json".format(wp=wp))
                                        for wp in ("Muon_XPathIsoMu23leg", "Muon_XPathIsoMu8leg", "Electron_IsoEle23Leg", "Electron_IsoEle12Leg")),

       "elemuLeg_HHMoriond17_2016" : tuple(localize_trigger("{wp}.json".format(wp=wp)) 
                                        for wp in ("Electron_IsoEle23Leg", "Electron_IsoEle12Leg", "Muon_XPathIsoMu23leg", "Muon_XPathIsoMu8leg")),
      
      ####################################
      # 2017: 
      #####################################
      # Muons:      https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2017
      # Btagging:   https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
       
       "electron_2017_94X"  : dict((k,localize_myanalysis(v)) for k, v in chain(
                               dict(("id_{wp}".format(wp=wp.lower()), 
                                ("Electron_EGamma_SF2D_2017_{wp}_Fall17V2.json".format(wp=wp)))
                                for wp in ("Loose", "Medium", "Tight" )).items()
                              )), 

       "muon_2017_94X"  : dict((k,localize_myanalysis(v)) for k, v in chain(
                           
                           dict(("id_{wp}".format(wp=wp.lower()), 
                               ("Muon_NUM_{wp}ID_DEN_genTracks_pt_abseta_{uncer}_2017RunBCDEF.json".format(wp=wp, uncer=uncer)))
                                for wp in ("Loose", "Medium", "Tight", "Soft", "MediumPrompt")for uncer in ("syst","stat")).items(),

                           dict(("id_{wp}_newTuneP".format(wp=wp.lower()), 
                               ("Muon_NUM_{wp}ID_DEN_genTracks_pair_newTuneP_probe_pt_abseta_{uncer}_2017RunBCDEF.json".format(wp=wp,uncer=uncer))) 
                               for wp in ("HighPt","TrkHighPtID")for uncer in ("syst", "stat")).items(),
                          
                           dict(("iso_{isowp}_id_{idwp}".format(isowp=(isowp.replace("ID","")).lower(), idwp=(idwp.replace("ID","")).lower()),
                                "Muon_NUM_{isowp}RelIso_DEN_{idwp}_pt_abseta_{uncer}_2017RunBCDEF.json".format(isowp=isowp, idwp=idwp,uncer=uncer))
                                for (isowp,idwp) in (("Loose", "LooseID"), ("Loose", "MediumID"), ("Loose", "TightIDandIPCut"),  ("Tight", "MediumID"), ("Tight", "TightIDandIPCut"))
                                for uncer in ("syst", "stat")).items(),
                      
                            dict(("iso_{isowp}_id_{idwp}_newTuneP".format(isowp=(isowp.replace("ID","")).lower(), idwp=(idwp.replace("ID","")).lower()),
                                "Muon_NUM_{isowp}RelTkIso_DEN_{idwp}_pair_newTuneP_probe_pt_abseta_{uncer}_2017RunBCDEF.json".format(isowp=isowp, idwp=idwp,uncer=uncer))
                                for (isowp,idwp) in (("Loose", "TrkHighPtID"), ("Loose", "TightIDandIPCut"),  ("Tight", "HighPtIDandIPCut"), ("Tight", "TightIDandIPCut"))
                                for uncer in ("syst", "stat")).items()
                          )),

       
       "btag_2017_94X" : dict((k,( tuple(localize_myanalysis(fv) for fv in v) 
                            if isinstance(v,tuple) and all(isinstance(fv, str) for fv in v)
                            else [ (eras, tuple(localize_myanalysis(fpath) for fpath in paths)) for eras,paths in v ])) for k, v in chain(
        # Resolved :
                          dict(("{algo}_{wp}".format(algo=algo, wp=wp), 
                            tuple("BTagging_{wp}_{flav}_{calib}_{algo}_2017BtoF.json".format(wp=wp, flav=flav, calib=calib, algo=algo) 
                            for (flav, calib) in (("lightjets", "incl"), ("cjets", "comb"), ("bjets","comb")))) for wp in ("loose", "medium", "tight") 
                            for algo in ("DeepJet", "DeepCSV") ).items(),
        # Boosted :
                          dict(("subjet_{algo}_{wp}".format(algo=algo, wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_subjet_{algo}_2017BtoF.json".format(wp=wp, flav=flav, calib=calib, algo=algo)
                            for (flav, calib) in (("lightjets", "incl"), ("cjets", "lt"), ("bjets","lt")))) for wp in ("loose", "medium") for algo in ("DeepCSV", ) ).items(),
                         )),

        #---- Single Muon trigger ------------------
       "mutrig_2017_94X" : tuple(localize_trigger("{0}_PtEtaBins_2017RunBtoF.json".format(trig)) 
                            for trig in ("IsoMu27", "Mu50")), 
      
      
      ##################################
      # 2018:
      ##################################
      # Muons:      https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2018      
      # Btagging:   https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X

       "electron_2018_102X"  : dict((k,localize_myanalysis(v)) for k, v in chain(  
                                dict(("id_{wp}".format(wp=wp.lower()), 
                                ("Electron_EGamma_SF2D_2018_{wp}_Fall17V2.json".format(wp=wp)))
                                for wp in ("Loose", "Medium", "Tight")).items()
                                
                               )),
       
       "muon_2018_102X"  : dict((k,localize_myanalysis(v)) for k, v in chain(
                            dict(("id_{wp}".format(wp=wp.lower()), 
                               ("Muon_NUM_{wp}ID_DEN_TrackerMuons_pt_abseta_{uncer}_2018RunABCD.json".format(wp=wp, uncer=uncer)))
                                for wp in ("Loose", "Medium", "Tight", "Soft", "MediumPrompt")for uncer in ("syst","stat")).items(),

                            dict(("id_{wp}_newTuneP".format(wp=wp.lower()), 
                               ("Muon_NUM_{wp}ID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta_{uncer}_2018RunABCD.json".format(wp=wp,uncer=uncer))) 
                               for wp in ("HighPt","TrkHighPt")for uncer in ("syst", "stat")).items(),

                            dict(("iso_{isowp}_id_{idwp}".format(isowp=(isowp.replace("ID","")).lower(), idwp=(idwp.replace("ID","")).lower()), 
                               "Muon_NUM_{isowp}RelIso_DEN_{idwp}_pt_abseta_{uncer}_2018RunABCD.json".format(isowp=isowp, idwp=idwp,uncer=uncer))
                                for (isowp,idwp) in (("Loose", "LooseID"), ("Loose", "MediumID"), ("Loose", "TightIDandIPCut"),  ("Tight", "MediumID"), ("Tight", "TightIDandIPCut")) 
                                for uncer in ("syst", "stat")).items(),
                           
                            dict(("iso_{isowp}_id_{idwp}_newTuneP".format(isowp=(isowp.replace("ID","")).lower(), idwp=(idwp.replace("ID","")).lower()), 
                               "Muon_NUM_{isowp}RelTkIso_DEN_{idwp}_pair_newTuneP_probe_pt_abseta_{uncer}_2018RunABCD.json".format(isowp=isowp, idwp=idwp,uncer=uncer))
                                for (isowp,idwp) in (("Loose", "HighPtIDandIPCut"), ("Loose", "TrkHighPtID"), ("Tight", "HighPtIDandIPCut"),  ("Tight", "TrkHighPtID")) 
                                for uncer in ("syst", "stat")).items() 
                           
                           )),

       "btag_2018_102X" : dict((k,( tuple(localize_myanalysis(fv) for fv in v) 
                            if isinstance(v,tuple) and all(isinstance(fv, str) for fv in v)
                            else [ (eras, tuple(localize_myanalysis(fpath) for fpath in paths)) for eras,paths in v ])) for k, v in chain(
        # Resolved :
                            dict(("{algo}_{wp}".format(algo=algo, wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_{algo}_2018.json".format(wp=wp, flav=flav, calib=calib, algo=algo) 
                              for (flav, calib) in (("lightjets", "incl"), ("cjets", "comb"), ("bjets","comb")))) for wp in ("loose", "medium", "tight") 
                              for algo in ("DeepCSV", "DeepJet") ).items(),
        # Boosted :
                            dict(("subjet_{algo}_{wp}".format(algo=algo, wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_subjet_{algo}_2018.json".format(wp=wp, flav=flav, calib=calib, algo=algo)
                              for (flav, calib) in (("lightjets", "incl"), ("cjets", "lt"), ("bjets","lt")))) for wp in ("loose", "medium") for algo in ("DeepCSV", ) ).items(),
                          )),

    # ------------- Single muon trigger  --------------------
       "mutrig_2018_102X" : tuple(localize_trigger("{trig}_PtEtaBins_2018AfterMuonHLTUpdate.json".format(trig=trig)) 
                            for trig in ("IsoMu24_OR_IsoTkMu24","Mu50_OR_OldMu100_OR_TkMu100" ))
            
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


class NanoHtoZA(NanoAODHistoModule):
    """ H->Z(ll)A(bb) analysis for the FullRunII using NanoAODv5 """
    
    def __init__(self, args):
        super(NanoHtoZA, self).__init__(args)
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
        super(NanoHtoZA, self).addArgs(parser)
        parser.add_argument("-s", "--systematic", action="store_true", help="Produce systematic variations")

    def prepareTree(self, tree, sample=None, sampleCfg=None):
        era = sampleCfg.get("era") if sampleCfg else None
        isMC = self.isMC(sample)
        metName = "METFixEE2017" if era == "2017" else "MET"
        ## initializes tree.Jet.calc so should be called first (better: use super() instead)
        # JEC's Recommendation for Full RunII: https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC
        # JER : -----------------------------: https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
        from bamboo.treedecorators import NanoAODDescription, nanoRochesterCalc, nanoJetMETCalc

        tree,noSel,be,lumiArgs = NanoAODHistoModule.prepareTree(self, tree, sample=sample, sampleCfg=sampleCfg, description=NanoAODDescription.get("v5", year=(era if era else "2016"), isMC=isMC, systVariations=[ nanoRochesterCalc, (nanoJetMETCalc_METFixEE2017 if era == "2017" else nanoJetMETCalc) ]),) ## will do Jet and MET variations, and the Rochester correction
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
    
    def definePlots(self, t, noSel, sample=None, sampleCfg=None):    
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
        yield_object = makeYieldPlots()

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
            noSel = noSel.refine("puWeight", weight=makePileupWeight(puWeightsFile, t.Pileup_nTrueInt, systName="pileup"))

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
                                            op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < 0.3 )), 
                                            op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < 0.3 ))))
        
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
                                                        systName="btagging{0}".format(era))  
                    
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
                                                systName="btagging{0}".format(era))  
                    
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
        
        # FIXME maybe for 2017 or 2018 --> The leading pT for the �� or µe channel should be above 20 Gev !
        hasOSLL_cmbRng = lambda cmbRng : op.AND(op.rng_len(cmbRng) > 0, cmbRng[0][0].pt > 25.) 
        
        ## helper selection (OR) to make sure jet calculations are only done once
        hasOSLL = noSel.refine("hasOSLL", cut=op.OR(*( hasOSLL_cmbRng(rng) for rng in osLLRng.values())))
       
        # FIXME move this to other script
        def passTrigByPT( self, sel, leptons, suffix, version):
            # taken from ttH studies:
            # https://gitlab.cern.ch/ttH_leptons/doc/blob/master/Legacy/data_to_mc_corrections.md#trigger-efficiency-scale-factors
            if version == "tth":
                if era == "2016":
                    if suffix == "MuMu":
                        # SF = 1.010   +/-    0.010
                        wgt = op.systematic(op.c_float(1.010), name="mumutrig", up=op.c_float(1.020), down=op.c_float(1.0))
                    elif suffix == "ElEl":
                        # SF = 1.020   +/-    0.020
                        wgt = op.systematic(op.c_float(1.020), name="eleltrig", up=op.c_float(1.040), down=op.c_float(1.0))
                    else:
                        # SF = 1.020   +/-    0.010
                        wgt = op.systematic(op.c_float(1.020), name="elmutrig", up=op.c_float(1.030), down=op.c_float(1.010))
                
                elif era == "2017":
                    if suffix =="MuMu":
                        if op.AND(leptons[0].pt<35., leptons[1].pt< 35.):
                            # SF = 0.972   +/-    0.006
                            wgt = op.systematic(op.c_float(0.972), name="mumutrig", up=op.c_float(0.978), down=op.c_float(0.966))
                        elif op.AND(leptons[0].pt>= 35., leptons[1].pt>= 35.):
                            # SF = 0.994   +/-    0.001
                            wgt = op.systematic(op.c_float(0.994), name="mumutrig", up=op.c_float(0.995), down=op.c_float(0.993))
                
                    elif suffix == "ElEl":
                        if op.AND(leptons[0].pt<30., leptons[1].pt< 30.):
                            # SF = 0.937   +/-    0.027
                            wgt = op.systematic(op.c_float(0.937), name="eleltrig", up=op.c_float(0.964), down=op.c_float(0.91))
                        elif op.AND(leptons[0].pt>= 30., leptons[1].pt>= 30.):
                            # SF = 0.991   +/-    0.002
                            wgt = op.systematic(op.c_float(0.991), name="eleltrig", up=op.c_float(0.993), down=op.c_float(0.989))

                    else:
                        if op.AND(leptons[0].pt<35., leptons[1].pt< 35.):
                            # SF = 0.952   +/-    0.008
                            wgt = op.systematic(op.c_float(0.952), name="elmutrig", up=op.c_float(0.96), down=op.c_float(0.944))
                        elif op.AND(op.in_rng(35., leptons[0].pt, 50), op.in_rng(35., leptons[1].pt, 50)):
                            # SF = 0.983   +/-    0.003
                            wgt = op.systematic(op.c_float(0.983), name="elmutrig", up=op.c_float(0.986), down=op.c_float(0.980))
                        elif op.AND(leptons[0].pt>= 50., leptons[1].pt>= 50.):
                            # SF = 1.000   +/-    0.001
                            wgt = op.systematic(op.c_float(1.000), name="elmutrig", up=op.c_float(0.001), down=op.c_float(0.999))
                else:
                    raise RuntimeError("Trigger SFs for era {0} still missing in tth analysis---> pass to other version ! ".format(era)) 

            elif version == "HHMoriond17":
                # Old SFs passed to 2016 study
                # FIXME not passed properly 
                if era =="2016" or era=="2017" or era=="2018":
                    if suffix == "MuMu":
                        wgt = get_scalefactor("dilepton", ("doubleMuLeg_HHMoriond17_2016"), systName="mumutrig")    
                    if suffix == "ElEl":
                        wgt = get_scalefactor("dilepton", ("doubleEleLeg_HHMoriond17_2016"), systName="eleltrig")
                    if suffix == "ElMu":
                        wgt = get_scalefactor("dilepton", ("elemuLeg_HHMoriond17_2016"), systName="elmutrig")
                    if suffix == "MuEl":
                        wgt = get_scalefactor("dilepton", ("mueleLeg_HHMoriond17_2016"), systName="mueltrig")

            elif version == "CMS_AN-19-140":
                # https://cms.cern.ch/iCMS/jsp/openfile.jsp?tp=draft&files=AN2019_140_v2.pdf
                if era == "2016":
                    if suffix == "MuMu":
                        # SF = 0.996 ± 0.006
                        wgt = op.systematic(op.c_float(0.996), name="mumutrig", up=op.c_float(1.002), down=op.c_float(0.99))
                    elif suffix == "ElEl":
                        # SF = 0.992 ± 0.006
                        wgt = op.systematic(op.c_float(0.992), name="eleltrig", up=op.c_float(0.998), down=op.c_float(0.986))
                    else:
                        # SF = 0.996 ± 0.006
                        wgt = op.systematic(op.c_float(0.996), name="elmutrig", up=op.c_float(1.002), down=op.c_float(0.99))
                elif era == "2017":
                    if suffix == "MuMu":
                        # SF = 0.987 ± 0.005
                        wgt = op.systematic(op.c_float(0.987), name="mumutrig", up=op.c_float(0.992), down=op.c_float(0.982))
                    elif suffix == "ElEl":
                        # SF = 0.975 ± 0.005
                        wgt = op.systematic(op.c_float(0.975), name="eleltrig", up=op.c_float(0.98), down=op.c_float(0.97))
                    else:
                        # SF = 0.985 ± 0.005
                        wgt = op.systematic(op.c_float(0.985), name="elmutrig", up=op.c_float(0.99), down=op.c_float(0.98))
                else:
                    if suffix == "MuMu":
                        # SF = 0.990 ± 0.005
                        wgt = op.systematic(op.c_float(0.990), name="mumutrig", up=op.c_float(0.995), down=op.c_float(0.985))
                    elif suffix == "ElEl":
                        # SF = 0.989 ± 0.005
                        wgt = op.systematic(op.c_float(0.989), name="eleltrig", up=op.c_float(0.994), down=op.c_float(0.984))
                    else:
                        # SF = 0.992 ± 0.005
                        wgt = op.systematic(op.c_float(0.992), name="elmutrig", up=op.c_float(0.997), down=op.c_float(0.987))
            
            selection = sel.refine("hasOs{0}_and_passTrigWgt_BypTRng".format(suffix), weight=(wgt if isMC else None)) 
            
            return selection 

        forceDefine(t._Jet.calcProd, hasOSLL)
        forceDefine(getattr(t, "_{0}".format("MET" if era != "2017" else "METFixEE2017")).calcProd, hasOSLL)
                
        if era =="2016" or era=="2017" or era=="2018":
            doubleMuTrigSF = get_scalefactor("dilepton", ("doubleMuLeg_HHMoriond17_2016"), systName="mumutrig")    
            doubleEleTrigSF = get_scalefactor("dilepton", ("doubleEleLeg_HHMoriond17_2016"), systName="eleltrig")
            elemuTrigSF = get_scalefactor("dilepton", ("elemuLeg_HHMoriond17_2016"), systName="elmutrig")
            mueleTrigSF = get_scalefactor("dilepton", ("mueleLeg_HHMoriond17_2016"), systName="mueltrig")
        
        llSFs = {
            "MuMu" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[0]), muMediumISOSF(ll[1]) , doubleMuTrigSF(ll) ]),
            "ElMu" : (lambda ll : [ elMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[1]), elemuTrigSF(ll) ]),
            "MuEl" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumISOSF(ll[0]), elMediumIDSF(ll[1]), mueleTrigSF(ll) ]),
            "ElEl" : (lambda ll : [ elMediumIDSF(ll[0]), elMediumIDSF(ll[1]), doubleEleTrigSF(ll) ])
            }
        
        categories = dict((channel, (catLLRng[0], hasOSLL.refine("hasOs{0}".format(channel), cut=hasOSLL_cmbRng(catLLRng), weight=(llSFs[channel](catLLRng[0]) if isMC else None)) )) for channel, catLLRng in osLLRng.items())

        ## btagging efficiencies plots
        #plots.extend(MakeBtagEfficienciesPlots(self, jets, bjets, categories))
        
        for channel, (dilepton, catSel) in categories.items():
        #for channel, (dilepton, catSel_ ) in categories.items():
            #----  Zmass (2Lepton OS && SF ) --------
            
            # FIXME pass the version of sys as args 
            #catSel = passTrigByPT( self, catSel_, dilepton, channel, "tth")
            
            optstex = ('$e^+e^-$' if channel=="ElEl" else( '$\mu^+\mu^-$' if channel =="MuMu" else( '$\mu^+e^-$' if channel=="MuEl" else('$e^+\mu^-$'))))
            yield_object.addYields(catSel,"hasOs%s"%channel,"OS leptons + $M_{ll}$ cut (channel : %s)"%optstex)
            
            plots.extend(makeControlPlotsForZpic(self, catSel, dilepton, channel))
            
            plots.append(CutFlowReport("Os_%s"%channel, catSel))

            #for sel, jet, reg in zip ([catSel, catSel], [AK4jets, AK8jets], ["resolved", "boosted"]):
            #    plots.extend(makeJetmultiplictyPlots(self, sel, jet, channel,"_NoCutOnJetsLen_" + reg))
            
            #----  add Jets selection 
            TwoLeptonsTwoJets_Resolved = catSel.refine("TwoJet_{0}Sel_resolved".format(channel), cut=[ op.rng_len(AK4jets) > 1 ])
            TwoLeptonsTwoJets_Boosted = catSel.refine("OneJet_{0}Sel_boosted".format(channel), cut=[ op.rng_len(AK8jets) > 0 ])
            
            yield_object.addYields(TwoLeptonsTwoJets_Resolved,"has2Lep2ResolvedJets_%s"%channel,"2 Lep(OS)+ at least 2 AK4Jets + $M_{ll}$ cut (channel : %s)"%optstex)
            yield_object.addYields(TwoLeptonsTwoJets_Boosted,"has2Lep2BoostedJets_%s"%channel,"2 Lep(OS)+ at least 1 AK8Jets+ $M_{ll}$ cut (channel : %s)"%optstex)
            
            plots.append(CutFlowReport("%sjj_resolved"%channel.lower(), TwoLeptonsTwoJets_Resolved))
            plots.append(CutFlowReport("%sjj_boosted"%channel.lower(), TwoLeptonsTwoJets_Boosted))
            # ----- plots : mll, mlljj, mjj, nVX, pT, eta  : basic selection plots ------
            for sel, jet, reg in zip ([TwoLeptonsTwoJets_Resolved, TwoLeptonsTwoJets_Boosted], [AK4jets, AK8jets], ["resolved", "boosted"]):
                plots.extend(makeJetPlots(self, sel, jet, channel, reg))
            #    plots.extend(makeJetmultiplictyPlots(self, sel, jet, channel, reg))
                plots.extend(makeControlPlotsForBasicSel(self, sel, jet, dilepton, channel, reg))
            
            #FIXME error in passing these plots ....
            #plots.extend(makeAK8JetsPLots(self, TwoLeptonsTwoJets_Boosted, AK8jets, channel))
            
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

                TwoLeptonsTwoBjets_NoMETCut_Res = {
                    "DeepFlavour{0}".format(wp) :  TwoLeptonsTwoJets_Resolved.refine("TwoLeptonsTwoBjets_NoMETcut_DeepFlavour{0}_{1}_Resolved".format(wp, channel),
                                                                        cut=[ op.rng_len(bJets_resolved_PassdeepflavourWP) > 1 ]),
                                                                        # FIXME 
                                                                        #weight=([ deepBFlavScaleFactor(bJets_resolved_PassdeepflavourWP[0]), 
                                                                        #          deepBFlavScaleFactor(bJets_resolved_PassdeepflavourWP[1]) ]if isMC else None)),
                    "DeepCSV{0}".format(wp)     :  TwoLeptonsTwoJets_Resolved.refine("TwoLeptonsTwoBjets_NoMETcut_DeepCSV{0}_{1}_Resolved".format(wp, channel), 
                                                                        cut=[ op.rng_len(bJets_resolved_PassdeepcsvWP) > 1 ])
                                                                        #FIXME --> invistagate more about b-ragging SFs passed
                                                                        #weight=([ deepB_AK4ScaleFactor(bJets_resolved_PassdeepcsvWP[0]), 
                                                                        #          deepB_AK4ScaleFactor(bJets_resolved_PassdeepcsvWP[1]) ]if isMC else None))
                                                }


                TwoLeptonsTwoBjets_NoMETCut_Boo = {
                    "DeepCSV{0}".format(wp)     :  TwoLeptonsTwoJets_Boosted.refine("TwoLeptonsTwoBjets_NoMETcut_DeepCSV{0}_{1}_Boosted".format(wp, channel), 
                                                                        cut=[ op.rng_len(bJets_boosted_PassdeepcsvWP) > 0])
                                                                        # FIXME ! can't pass boosted jets SFs with current version ---> move to v7  
                                                                        #weight=([ deepB_AK8ScaleFactor(bJets_boosted_PassdeepcsvWP[0]), 
                                                                        #          deepB_AK8ScaleFactor(bJets_boosted_PassdeepcsvWP[1]) ]if isMC else None))
                                                }

                
                ## needed to optimize the MET cut 
                # FIXME  Rerun again  &&& pass signal and bkg  
                # The MET cut is passed to TwoLeptonsTwoBjets selection for the # tagger and for the # wp 
                for sel, reg in zip( [TwoLeptonsTwoBjets_NoMETCut_Res,TwoLeptonsTwoBjets_NoMETCut_Boo], ["resolved", "boosted"]):
                    plots.extend(MakeMETPlots(self, sel, corrMET, MET, channel, reg))
                    plots.extend(MakeExtraMETPlots(self, sel, dilepton, MET, channel, reg))
                

                TwoLeptonsTwoBjets_Res = dict((key, selNoMET.refine("TwoLeptonsTwoBjets_{0}_{1}_Resolved".format(key, channel), cut=[ corrMET.pt < 80. ])) for key, selNoMET in TwoLeptonsTwoBjets_NoMETCut_Res.items())
                TwoLeptonsTwoBjets_Boo = dict((key, selNoMET.refine("TwoLeptonsTwoBjets_{0}_{1}_Boosted".format(key, channel), cut=[ corrMET.pt < 80. ])) for key, selNoMET in TwoLeptonsTwoBjets_NoMETCut_Boo.items())
                
                
                # ----- For ttbar Estimation -----
                plots.extend(makehistosforTTbarEstimation(self, TwoLeptonsTwoBjets_Res, dilepton, bjets_resolved, wp, channel, "resolved"))
                
                
                JetType=( 'AK4' if reg=='resolved' else( 'AK8'))
                for sel, bjets, reg in zip([TwoLeptonsTwoBjets_Res, TwoLeptonsTwoBjets_Boo], [bjets_resolved, bjets_boosted], ["resolved", "boosted"]):
                    
                    plots.extend(makeBJetPlots(self, sel, bjets, wp, channel, reg, "_METCut_"))
                    plots.extend(makeControlPlotsForFinalSel(self, sel, bjets, dilepton, wp, channel, reg, "_METCut_"))
                    # --- to get the Ellipses plots  
                    plots.extend(MakeEllipsesPLots(self, sel, bjets, dilepton, wp, channel, reg))
                    
                    for key in sel.keys():
                        yield_object.addYields(sel.get(key),"has2Lep2{0}BJets_METCut_{1}_{2}".format(reg.upper(), channel, key),"2 Lep(OS) + at least 2 {0}BJets {1} pass {2} + METcut (channel : {3})".format(JetType, reg, key, optstex))
                        plots.append(CutFlowReport("{0}jj_{1}_METCut_{2}".format(channel.lower(), key, reg), sel.get(key)))
                
                # -------  NoMETCut ---------
                # Control Plots, Yield Plots, FlowReport (passed to the postprocess)
                for sel, bjets, reg in zip([TwoLeptonsTwoBjets_NoMETCut_Res, TwoLeptonsTwoBjets_NoMETCut_Boo], [bjets_resolved, bjets_boosted], ["resolved", "boosted"]):
                    
                    plots.extend(makeBJetPlots(self, sel, bjets, wp, channel, reg, "_NoMETCut_"))
                    plots.extend(makeControlPlotsForFinalSel(self, sel, bjets, dilepton, wp, channel, reg, "_NoMETCut_"))
                
                    for key in sel.keys():
                        yield_object.addYields(sel.get(key),"has2Lep2{0}BJets_NoMETCut_{1}_{2}".format(reg.upper(), channel, key),"2 Lep(OS) + at least 1 {0}BJets {1} pass {2} + NoMETcut (channel : {3})".format(JetType, reg, key, optstex))
                        plots.append(CutFlowReport("{0}jj_{1}_NoMETCut_{2}".format(channel.lower(), key, reg), sel.get(key)))
        
                #plots.extend(makeExtraFatJetBOostedPlots(self, TwoLeptonsTwoBjets_Boo, bjets_boosted, wp, channel))
        
        plots.extend(yield_object.returnPlots())
        return plots

    def postProcess(self, taskList, config=None, workdir=None, resultsdir=None):
        from bamboo.plots import CutFlowReport
        import bambooToOls
        
        # Get list of plots (taken from bamboo.HistogramsModule)
        if not self.plotList:
            tup, smpName, smpCfg = self.getATree()
            tree, noSel, backend, runAndLS = self.prepareTree(tup, sample=smpName, sampleCfg=smpCfg)
            self.plotList = self.definePlots(tree, noSel, sample=smpName, sampleCfg=smpCfg)
        
        # merge processes using their cross sections
        #utils.normalizeAndMergeSamples(self.plotList, self.readCounters, config, resultsdir, os.path.join(resultsdir, "output_sum.root"))
        
        # save generated-events for each samples--- > mainly needed for the DNN
        plotList_cutflowreport = [ ap for ap in self.plotList if isinstance(ap, CutFlowReport) ]
        bambooToOls.SaveCutFlowReports(config, plotList_cutflowreport, resultsdir, self.readCounters)

        #for (inputs, output), kwargs in taskList:
        #    if self.doSysts and self.isMC(output):
        #        self.qcdScaleVariations= { f"qcdScalevar{i}" for i in [0, 1, 3, 5, 7, 8] }
        #        utils.produceMEScaleEnvelopes(self.plotList, self.qcdScaleVariations, os.path.join(resultsdir, output))
        
        #for smpName, smpCfg in config["samples"].items():
        #    smpCfg.pop("files")

        # finally, run plotIt as defined in HistogramsModule
        super(NanoHtoZA, self).postProcess(taskList, config, workdir, resultsdir)
