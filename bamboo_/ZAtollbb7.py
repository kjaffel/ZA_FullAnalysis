from bamboo.analysismodules import NanoAODHistoModule
from bamboo.analysisutils import makeMultiPrimaryDatasetTriggerSelection
from bamboo.scalefactors import binningVariables_nano

from bamboo import treefunctions as op
from bamboo import scalefactors

from itertools import chain
import os.path

def localize_myanalysis(aPath, era="FullRunII"):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ScaleFactors_{0}".format(era), aPath)

def localize_trigger(aPath):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "TriggerEfficienciesStudies", aPath)
binningVariables = {
      "Eta"       : lambda obj : obj.p4.Eta()
    , "ClusEta"   : lambda obj : obj.p4.Eta() + obj.deltaEtaSC
    , "AbsEta"    : lambda obj : op.abs(obj.p4.Eta())
    , "AbsClusEta": lambda obj : op.abs(obj.clusterEta) +op.abs(obj.deltaEtaSC)
    , "Pt"        : lambda obj : obj.p4.Pt()
    }
all_scalefactors = {
       # 2016 legacy:
       # https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaRunIIRecommendations#Fall17v2
       # https://twiki.cern.ch/twiki/bin/viewauth/CMS/MuonReferenceEffs2016LegacyRereco#Efficiencies
       # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation2016Legacy
      "electron_2016_94X"  : dict((k,localize_myanalysis(v)) for k, v in chain(
          dict(("id_{wp}".format(wp=wp.lower()), ("Electron_EGamma_SF2D_2016Legacy_{wp}_Fall17V2.json".format(wp=wp)))
         for wp in ("Loose", "Medium", "Tight", "MVA80","MVA90", "MVA80noiso", "MVA90noiso")).items()))

          #  DONE  --> updating the SFs with _stat & _syst   for 2016 and 2018 // #TODO for 2017 : not recomended for now ( missing correction in some bins !! )
          # TODO --> extract the trk SFs for the FullRun from Muon SFs 
    , "muon_2016_94X" : dict((k,( localize_myanalysis(v) if isinstance(v, str)
                               else [ (eras, localize_myanalysis(path)) for eras,path in v ]))
                           for k, v in chain(
          dict(("id_{wp}".format(wp=wp.lower()), [ (tuple("Run2016{0}".format(ltr) for ltr in eras), "Muon_NUM_{wp}ID_DEN_genTracks_eta_pt_{uncer}_2016Run{era}.json".format(wp=wp, uncer=uncer, era=eras)) for eras in ("BCDEF", "GH") for uncer in ("syst", "stat")]) for wp in ("Loose", "Medium", "Tight")).items()
       ,  dict(("idtrk_{wp}".format(wp=wp.lower()), [ (tuple("Run2016{0}".format(ltr) for ltr in eras), "Muon_NUM_{wp}ID_DEN_genTracks_eta_pair_newTuneP_probe_pt_{uncer}_2016Run{era}.json".format(wp=wp, uncer=uncer, era=eras)) for eras in ("BCDEF", "GH") for uncer in ("syst", "stat")]) for wp in ("HighPt",)).items()

       ,  dict(("iso_{isowp}_id_{idwp}".format(isowp=isowp.lower(), idwp=idwp.lower()),[ (tuple("Run2016{0}".format(ltr) for ltr in eras), "Muon_NUM_{isowp}RelIso_DEN_{idwp}ID_eta_pt_{uncer}_2016Run{era}.json".format(isowp=isowp, idwp=idwp,uncer=uncer, era=eras))for eras in ("BCDEF", "GH") for uncer in (("syst","stat")if eras=="BCDEF" else ("stat",))]) for (isowp,idwp) in (("Loose", "Loose"), ("Loose", "Medium"), ("Loose", "TightIDandIPCut"),("Tight", "Medium"), ("Tight", "TightIDandIPCut"))).items() 
       ,  dict(("isotrk_{isowp}_idtrk_{idwp}".format(isowp=isowp.lower(), idwp=idwp.lower()),[ (tuple("Run2016{0}".format(ltr) for ltr in eras), "Muon_NUM_{isowp}RelTrkIso_DEN_{idwp}_eta_pair_newTuneP_probe_pt_{uncer}_2016Run{era}.json".format(isowp=isowp, idwp=idwp,uncer=uncer, era=eras))for eras in ("BCDEF", "GH") for uncer in (("syst","stat")if eras=="BCDEF" else ("stat",))]) for (isowp,idwp) in (("Loose", "TightIDandIPCut"),)).items())) 
      
    , "btag_2016_94X" : dict((k,( tuple(localize_myanalysis(fv) for fv in v) if isinstance(v,tuple) and all(isinstance(fv, str) for fv in v)
                               else [ (eras, tuple(localize_myanalysis(fpath) for fpath in paths)) for eras,paths in v ]))
                           for k, v in
          dict(("{algo}_{wp}".format(algo=algo, wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_{algo}.json".format(wp=wp, flav=flav, calib=calib, algo=algo) for (flav, calib) in (("lightjets", "incl"), ("cjets", "comb"), ("bjets","comb")))) for wp in ("loose", "medium", "tight") for algo in ("DeepCSV", "DeepJet") ).items())

    #------- single muon trigger ----------
    , "mutrig_2016_94X" : tuple(localize_trigger("{trig}_PtEtaBins_2016Run{eras}.json".format(trig=trig, eras=eras)) 
								  for trig in ("IsoMu24_OR_IsoTkMu24","Mu50_OR_TkMu50" ) for eras in ("BtoF", "GtoH"))
    # For now i will use Alessia efficiencies trigger --> To Update this later ***
    #----------------------------------------------------------------------------
    , "doubleEleLeg_HHMoriond17_2016" : tuple(localize_trigger("{wp}.json".format(wp=wp)) 
								  for wp in ("Electron_IsoEle23Leg", "Electron_IsoEle12Leg", "Electron_IsoEle23Leg", "Electron_IsoEle12Leg") )

    , "doubleMuLeg_HHMoriond17_2016" : tuple(localize_trigger("{wp}.json".format(wp=wp)) for wp in ("Muon_DoubleIsoMu17Mu8_IsoMu17leg", "Muon_DoubleIsoMu17TkMu8_IsoMu8legORTkMu8leg", "Muon_DoubleIsoMu17Mu8_IsoMu17leg", "Muon_DoubleIsoMu17TkMu8_IsoMu8legORTkMu8leg"))

    , "mueleLeg_HHMoriond17_2016" : tuple(localize_trigger("{wp}.json".format(wp=wp))for wp in ("Muon_XPathIsoMu23leg", "Muon_XPathIsoMu8leg", "Electron_IsoEle23Leg", "Electron_IsoEle12Leg"))

    , "elemuLeg_HHMoriond17_2016" : tuple(localize_trigger("{wp}.json".format(wp=wp)) for wp in ("Electron_IsoEle23Leg", "Electron_IsoEle12Leg", "Muon_XPathIsoMu23leg", "Muon_XPathIsoMu8leg"))

      # 2017: 
      # https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2017
      # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
   ,  "electron_2017_94X"  : dict((k,localize_myanalysis(v)) for k, v in chain(
          dict(("id_{wp}".format(wp=wp.lower()), ("Electron_EGamma_SF2D_2017{wp}.json".format(wp=wp)))
         for wp in ("Loose", "Medium", "Tight" , "Veto")).items()))


   ,  "muon_2017_94X"  : dict((k,localize_myanalysis(v)) for k, v in chain(
          dict(("id_{wp}".format(wp=wp.lower()), ("Muon_NUM_{wp}ID_DEN_genTracks_pt_abseta_2017RunBCDEF.json".format(wp=wp)))
         for wp in ("Loose", "Medium", "Tight", "Soft", "MediumPrompt")).items()
        , dict(("iso_{isowp}_id_{idwp}".format(isowp=isowp.lower(), idwp=idwp.lower()), "Muon_NUM_{isowp}RelIso_DEN_{idwp}ID_pt_abseta_2017RunBCDEF.json".format(isowp=isowp, idwp=idwp))
            for (isowp,idwp) in (("Loose", "Loose"), ("Loose", "Medium"), ("Loose", "TightIDandIPCut"),  ("Tight", "Medium"), ("Tight", "TightIDandIPCut")) ).items()))

    , "btag_2017_94X" : dict((k,( tuple(localize_myanalysis(fv) for fv in v) if isinstance(v,tuple) and all(isinstance(fv, str) for fv in v)
                               else [ (eras, tuple(localize_myanalysis(fpath) for fpath in paths)) for eras,paths in v ]))
                           for k, v in
          dict(("{algo}_{wp}".format(algo=algo, wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_{algo}_2017BtoF.json".format(wp=wp, flav=flav, calib=calib, algo=algo) for (flav, calib) in (("lightjets", "incl"), ("cjets", "comb"), ("bjets","comb")))) for wp in ("loose", "medium", "tight") for algo in ("DeepFlavour","CSVv2", "DeepCSV") ).items())

    #---- Single Muon trigger ------------------
    , "mutrig_2017_94X" : tuple(localize_trigger("{0}_PtEtaBins_2017RunBtoF.json".format(trig)) for trig in ("IsoMu27", "Mu50"))

      # 2018:
      # https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2018      
      # https://twiki.cg_2016_94X"ern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X
   ,  "electron_2018_102X"  : dict((k,localize_myanalysis(v)) for k, v in chain(  
          dict(("id_{wp}".format(wp=wp.lower()), ("Electron_EGamma_SF2D_2018{wp}.json".format(wp=wp)))
         for wp in ("Loose", "Medium", "Tight", "Veto")).items()))

   ,  "muon_2018_102X"  : dict((k,localize_myanalysis(v)) for k, v in chain(
          dict(("id_{wp}".format(wp=wp.lower()), ("Muon_NUM_{wp}ID_DEN_TrackerMuons_pt_abseta_{uncer}_2018RunABCD.json".format(wp=wp, uncer=uncer)))
         for wp in ("Loose", "Medium", "Tight", "Soft", "MediumPrompt")for uncer in ("syst","stat")).items()
        , dict(("idtrk_{wp}".format(wp=wp.lower()), ("Muon_NUM_Trk{wp}ID_DEN_TrackerMuons_pair_newTuneP_probe_pt_abseta_{uncer}_2018RunABCD.json".format(wp=wp,uncer=uncer))) for wp in ("HighPt",)for uncer in ("syst", "stat")).items()

        , dict(("iso_{isowp}_id_{idwp}".format(isowp=isowp.lower(), idwp=idwp.lower()), "Muon_NUM_{isowp}RelIso_DEN_{idwp}ID_pt_abseta_{uncer}_2018RunABCD.json".format(isowp=isowp, idwp=idwp,uncer=uncer))
            for (isowp,idwp) in (("Loose", "Loose"), ("Loose", "Medium"), ("Loose", "TightIDandIPCut"),  ("Tight", "Medium"), ("Tight", "TightIDandIPCut")) for uncer in ("syst", "stat")).items()))

    , "btag_2018_102X" : dict((k,( tuple(localize_myanalysis(fv) for fv in v) if isinstance(v,tuple) and all(isinstance(fv, str) for fv in v)
                               else [ (eras, tuple(localize_myanalysis(fpath) for fpath in paths)) for eras,paths in v ]))
                           for k, v in
          dict(("{algo}_{wp}".format(algo=algo, wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_{algo}_2018.json".format(wp=wp, flav=flav, calib=calib, algo=algo) for (flav, calib) in (("lightjets", "incl"), ("cjets", "comb"), ("bjets","comb")))) for wp in ("loose", "medium", "tight") for algo in ("DeepCSV", "DeepJet") ).items())


    #--- Single muon trigger ------
    , "mutrig_2018_102X" : tuple(localize_trigger("{trig}_PtEtaBins_2018AfterMuonHLTUpdate.json".format(trig=trig)) for trig in ("IsoMu24_OR_IsoTkMu24","Mu50_OR_OldMu100_OR_TkMu100" ))
            
    }

def get_scalefactor(objType, key, periods=None, combine=None, additionalVariables=dict(), systName=None):
    return scalefactors.get_scalefactor(objType, key, periods=periods, combine=combine, additionalVariables=additionalVariables, sfLib=all_scalefactors, paramDefs=binningVariables, getFlavour=(lambda j : j.hadronFlavour), systName=systName)

class NanoZMuMu(NanoAODHistoModule):
    """ Example module: Z->MuMu histograms from NanoAOD """
    def __init__(self, args):
        super(NanoZMuMu, self).__init__(args)

    def prepareTree(self, tree, era=None, sample=None):
        ## initializes tree.Jet.calc so should be called first (better: use super() instead)
        # JEC's Recommendation for Full RunII: https://twiki.cern.ch/twiki/bin/view/CMS/JECDataMC
        # JER : -----------------------------: https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
        tree,noSel,be,lumiArgs = NanoAODHistoModule.prepareTree(self, tree, era=era, sample=sample)
        triggersPerPrimaryDataset = {}
        from bamboo.analysisutils import configureJets ,configureRochesterCorrection
        isNotWorker = (self.args.distributed != "worker") 
        if era == "2016":
            configureRochesterCorrection(tree._Muon.calc,os.path.join(os.path.dirname(__file__), "data", "RoccoR2016.txt"))
            triggersPerPrimaryDataset = {
                "DoubleMuon" : [ tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                                 tree.HLT.Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL,
                                 tree.HLT.Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ ],
                "DoubleEG"   : [ tree.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ ],  # double electron (loosely isolated)
                "MuonEG"     : [ tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL ]
                }
            if self.isMC(sample) or "2016F" in sample or "2016G" in sample or "2016H" in sample:
                triggersPerPrimaryDataset["MuonEG"] += [ ## added from 2016F on
                        tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
                        tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ
                        ]
            if "2016H" not in sample:
                triggersPerPrimaryDataset["MuonEG"] += [ ## removed for 2016H
                        tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL
                        ]

            if self.isMC(sample):
                configureJets(tree, "Jet", "AK4PFchs",
                    jec="Summer16_07Aug2017_V20_MC",
                    smear="Summer16_25nsV1_MC",
                    jesUncertaintySources=["Total"], mayWriteCache=isNotWorker)
            else:
                if "2016B" in sample or "2016C" in sample or "2016D" in sample:
                    configureJets(tree, "Jet", "AK4PFchs",
                        jec="Summer16_07Aug2017BCD_V11_DATA", mayWriteCache=isNotWorker)
                elif "2016E" in sample or "2016F" in sample:
                    configureJets(tree, "Jet", "AK4PFchs",
                        jec="Summer16_07Aug2017EF_V11_DATA", mayWriteCache=isNotWorker)
                elif "2016G" in sample or "2016H" in sample:
                    configureJets(tree, "Jet", "AK4PFchs",
                        jec="Summer16_07Aug2017GH_V11_DATA", mayWriteCache=isNotWorker)

        elif era == "2017":
            configureRochesterCorrection(tree._Muon.calc,os.path.join(os.path.dirname(__file__), "data", "RoccoR2017.txt"))
            triggersPerPrimaryDataset = {
                "DoubleMuon" : [ tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                                 #tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8,
                                 #tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8 
                                 ],
                "DoubleEG"   : [ tree.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL ],
                # it's recommended to not use the DZ  version  for 2017 and 2018, it would be a needless efficiency loss
                #---> https://twiki.cern.ch/twiki/bin/view/CMS/EgHLTRunIISummary
                "MuonEG"     : [ #tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,
                                 tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
                                 tree.HLT.Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ,
                                 #tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,
                                 #tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ 
                                 ]
                }
            if "2017B" not in sample:
                triggersPerPrimaryDataset["MuonEG"] += [ ## removed for 2017B
                        tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL]

            if self.isMC(sample):
                configureJets(tree, "Jet", "AK4PFchs",
                    jec="Fall17_17Nov2017_V32_MC",
                    smear="Fall17_V3_MC",
                    jesUncertaintySources=["Total"], mayWriteCache=isNotWorker)
            else:
                if "2017B" in sample:
                    configureJets(tree, "Jet", "AK4PFchs", jec="Fall17_17Nov2017B_V32_DATA", mayWriteCache=isNotWorker)
                elif "2017C" in sample:
                    configureJets(tree, "Jet", "AK4PFchs", jec="Fall17_17Nov2017C_V32_DATA", mayWriteCache=isNotWorker)
                elif "2017D" in sample or "2017E" in sample:
                    configureJets(tree, "Jet", "AK4PFchs", jec="Fall17_17Nov2017DE_V32_DATA", mayWriteCache=isNotWorker)
                elif "2017F" in sample:
                    configureJets(tree, "Jet", "AK4PFchs", jec="Fall17_17Nov2017F_V32_DATA", mayWriteCache=isNotWorker)

        elif era == "2018":
            configureRochesterCorrection(tree._Muon.calc,os.path.join(os.path.dirname(__file__), "data", "RoccoR2018.txt"))
            triggersPerPrimaryDataset = {
                "DoubleMuon" : [ tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8 ],
                "EGamma"     : [ tree.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL ], 
                "MuonEG"     : [ tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,
                                 tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
                                 tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,
                                 tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ ]
                }
            if self.isMC(sample):
                configureJets(tree, "Jet", "AK4PFchs",
                    jec="Autumn18_V8_MC",
                    smear="Autumn18_V1_MC",
                    jesUncertaintySources=["Total"], mayWriteCache=isNotWorker)
            else:
                if "2018A" in sample:
                    configureJets(tree, "Jet", "AK4PFchs",
                        jec="Autumn18_RunA_V8_DATA", mayWriteCache=isNotWorker)
                elif "2018B" in sample:
                    configureJets(tree, "Jet", "AK4PFchs",
                        jec="Autumn18_RunB_V8_DATA", mayWriteCache=isNotWorker)
                elif "2018C" in sample:
                    configureJets(tree, "Jet", "AK4PFchs",
                        jec="Autumn18_RunC_V8_DATA", mayWriteCache=isNotWorker)
                elif "2018D" in sample:
                    configureJets(tree, "Jet", "AK4PFchs",
                        jec="Autumn18_RunD_V8_DATA", mayWriteCache=isNotWorker)
        else:
            raise RuntimeError("Unknown era {0}".format(era))

        if self.isMC(sample):
            noSel = noSel.refine("genWeight", weight=tree.genWeight, cut=op.OR(*chain.from_iterable(triggersPerPrimaryDataset.values())))
        else:
            noSel = noSel.refine("withTrig", cut=makeMultiPrimaryDatasetTriggerSelection(sample, triggersPerPrimaryDataset))

        return tree,noSel,be,lumiArgs
        
    def definePlots(self, t, noSel, era=None, sample=None):
        from bamboo.analysisutils import forceDefine
        from bamboo.plots import Plot, EquidistantBinning
        from bamboo import treefunctions as op

        puWeightsFile = None
        if era == "2016":
            sfTag="94X"
            puWeightsFile = os.path.join(os.path.dirname(__file__), "data", "puweights2016.json")
        elif era == "2017":
            sfTag="94X"     
            puWeightsFile = os.path.join(os.path.dirname(__file__), "data", "puweights2017.json")
        elif era == "2018":
            sfTag="102X"
            puWeightsFile = os.path.join(os.path.dirname(__file__), "data", "puweights2018.json")
        if self.isMC(sample) and puWeightsFile is not None:
            from bamboo.analysisutils import makePileupWeight
            noSel = noSel.refine("puWeight", weight=makePileupWeight(puWeightsFile, t.Pileup_nTrueInt, systName="pileup"))
        isMC = self.isMC(sample)
        plots = []

        forceDefine(t._Muon.calcProd, noSel)

        # Wp // 2016- 2017 -2018 : Muon_mediumId   // https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Muon_Isolation
        muons = op.select(t.Muon, lambda mu : op.AND(mu.p4.Pt() > 10., op.abs(mu.p4.Eta()) < 2.4, mu.mediumId, mu.pfRelIso04_all<0.15))
      
        if era=="2016":
            doubleMuTrigSF = get_scalefactor("dilepton", ("doubleMuLeg_HHMoriond17_2016"), systName="mumutrig")    
            muMediumIDSF = get_scalefactor("lepton", ("muon_{0}_{1}".format(era, sfTag), "id_medium"), combine="weight", systName="muid")
            muMediumISOSF = get_scalefactor("lepton", ("muon_{0}_{1}".format(era, sfTag), "iso_tight_id_medium"), combine="weight", systName="muiso")
            #TrkIDSF = get_scalefactor("lepton", ("muon_{0}_{1}".format(era, sfTag), "highpt"), combine="weight")
            #TrkISOSF = get_scalefactor("lepton", ("muon_{0}_{1}".format(era, sfTag), "isotrk_loose_idtrk_tightidandipcut"), combine="weight")
        else:
            muMediumIDSF = get_scalefactor("lepton", ("muon_{0}_{1}".format(era, sfTag), "id_medium"), systName="muid")
            muMediumISOSF = get_scalefactor("lepton", ("muon_{0}_{1}".format(era, sfTag), "iso_tight_id_medium"), systName="muiso") 
            doubleMuTrigSF = get_scalefactor("dilepton", ("doubleMuLeg_HHMoriond17_2016"), systName="mumutrig")    

        #Wp  // 2016: Electron_cutBased_Sum16==3  -> medium     // 2017 -2018  : Electron_cutBased ==3   --> medium ( Fall17_V2)
        # asking for electrons to be in the Barrel region with dz<1mm & dxy< 0.5mm   //   Endcap region dz<2mm & dxy< 0.5mm 
        electrons = op.select(t.Electron, lambda ele : op.AND(ele.p4.Pt() > 15., op.abs(ele.p4.Eta()) < 2.5 , ele.cutBased>=3 )) # //cut-based ID Fall17 V2 the recomended one from POG for the FullRunII

        elMediumIDSF = get_scalefactor("lepton", ("electron_{0}_{1}".format(era,sfTag), "id_medium"), systName="elid")
        doubleEleTrigSF = get_scalefactor("dilepton", ("doubleEleLeg_HHMoriond17_2016"), systName="eleltrig")     

        elemuTrigSF = get_scalefactor("dilepton", ("elemuLeg_HHMoriond17_2016"), systName="elmutrig")
        mueleTrigSF = get_scalefactor("dilepton", ("mueleLeg_HHMoriond17_2016"), systName="mueltrig")

#------------- For debugging purpose; work on electronMVA to check if the e-mu & mu-e channel will screwd up in the same way as working only with Electron
        #working in the inner barrel  |eta|< 0.8
        electronsIB = op.select(t.Electron, lambda ele : op.AND(ele.p4.Pt() > 10., op.abs(ele.p4.Eta()) < 0.8, ele.mvaFall17V2Iso_WPL))
        OsElEl_IB = op.combine(electronsIB, N=2, pred=lambda ele1,ele2 : ele1.charge != ele2.charge)
        firstoselel_IB = OsElEl_IB[0]
        hasOsElEl_IB = noSel.refine("twoosElectronsIB", cut=[op.rng_len(OsElEl_IB) >= 1, firstoselel_IB[0].p4.Pt() > 10. , op.in_range(70, op.invariant_mass(firstoselel_IB[0].p4, firstoselel_IB[1].p4), 110.)], weight=([elMediumIDSF(firstoselel_IB[0]), elMediumIDSF(firstoselel_IB[1]), doubleEleTrigSF(firstoselel_IB) ]if isMC else None))
        # working in the outer barrel  0.8< eta <1.44
        electronsOB = op.select(t.Electron, lambda ele : op.AND(ele.p4.Pt() > 10., op.in_range(0.8,ele.p4.Eta(),1.44), ele.mvaFall17V2Iso_WPL))
        OsElEl_OB = op.combine(electronsOB, N=2, pred=lambda ele1,ele2 : ele1.charge != ele2.charge)
        firstoselel_OB = OsElEl_OB[0]
        hasOsElEl_OB = noSel.refine("twoosElectronsOB", cut=[op.rng_len(OsElEl_OB) >= 1, firstoselel_OB[0].p4.Pt() > 10. , op.in_range(70, op.invariant_mass(firstoselel_OB[0].p4, firstoselel_OB[1].p4), 110.)], weight=([elMediumIDSF(firstoselel_OB[0]), elMediumIDSF(firstoselel_OB[1]), doubleEleTrigSF(firstoselel_OB) ]if isMC else None))
        # working in the Endcap 1.44< eta < 1.57
        electronsEC = op.select(t.Electron, lambda ele : op.AND(ele.p4.Pt() > 10., op.in_range(1.44,ele.p4.Eta(),1.57), ele.mvaFall17V2Iso_WPL))
        OsElEl_EC = op.combine(electronsEC, N=2, pred=lambda ele1,ele2 : ele1.charge != ele2.charge)
        firstoselel_EC = OsElEl_EC[0]
        hasOsElEl_EC = noSel.refine("twoosElectronsEC", cut=[op.rng_len(OsElEl_EC) >= 1, firstoselel_EC[0].p4.Pt() > 10., op.in_range(70, op.invariant_mass(firstoselel_EC[0].p4, firstoselel_EC[1].p4), 110.)], weight=([elMediumIDSF(firstoselel_EC[0]), elMediumIDSF(firstoselel_EC[1]), doubleEleTrigSF(firstoselel_EC) ]if isMC else None))
        

        OsElMu_IB= op.combine((electronsIB, muons), pred=lambda ele,mu : op.AND(ele.charge != mu.charge ,ele.p4.Pt() > mu.p4.Pt() ))
        OsElMu_OB= op.combine((electronsOB, muons), pred=lambda ele,mu : op.AND(ele.charge != mu.charge ,ele.p4.Pt() > mu.p4.Pt() ))
        OsElMu_EC= op.combine((electronsEC, muons), pred=lambda ele,mu : op.AND(ele.charge != mu.charge ,ele.p4.Pt() > mu.p4.Pt() ))
        firstoselmu_IB = OsElMu_IB[0]
        firstoselmu_OB = OsElMu_OB[0]
        firstoselmu_EC = OsElMu_EC[0]
        hasOsElMu_IB = noSel.refine("twoosElectronMuonIB", cut=[ op.rng_len(OsElMu_IB) >= 1, op.in_range(70., op.invariant_mass( firstoselmu_IB[0].p4, firstoselmu_IB[1].p4),110.)], weight=([elMediumIDSF(firstoselmu_IB[0]), muMediumIDSF(firstoselmu_IB[1]),muMediumISOSF(firstoselmu_IB[1]), elemuTrigSF(firstoselmu_IB) ]if isMC else None))
        hasOsElMu_OB = noSel.refine("twoosElectronMuonOB", cut=[ op.rng_len(OsElMu_OB) >= 1, op.in_range(70., op.invariant_mass( firstoselmu_OB[0].p4, firstoselmu_OB[1].p4),110.)], weight=([elMediumIDSF(firstoselmu_OB[0]), muMediumIDSF(firstoselmu_OB[1]),muMediumISOSF(firstoselmu_OB[1]), elemuTrigSF(firstoselmu_OB) ]if isMC else None))
        hasOsElMu_EC = noSel.refine("twoosElectronMuonEC", cut=[ op.rng_len(OsElMu_EC) >= 1, op.in_range(70., op.invariant_mass( firstoselmu_EC[0].p4, firstoselmu_EC[1].p4),110.)], weight=([elMediumIDSF(firstoselmu_EC[0]), muMediumIDSF(firstoselmu_EC[1]),muMediumISOSF(firstoselmu_EC[1]), elemuTrigSF(firstoselmu_EC) ]if isMC else None))

        # no need to plots the e-mu and mu-e channel : one is already enough for debugging !
        #categories_ele_reg = {"emu_IB" : (firstoselmu_IB, hasOsElMu_IB),
        #              "emu_OB" : (firstoselmu_OB, hasOsElMu_OB), 
        #              "emu_EC" : (firstoselmu_EC, hasOsElMu_EC), 
        #              "ee_OB" : (firstoselel_OB, hasOsElEl_OB), 
        #              "ee_IB" : (firstoselel_IB, hasOsElEl_IB), 
        #              "ee_EC" : (firstoselel_EC, hasOsElEl_EC)} 

        #for catN, (dilepton, catSel) in categories_ele_reg.items():
        #    plots.append(Plot.make1D("{0}_leadleptonPT".format(catN), dilepton[0].p4.Pt(), catSel, EquidistantBinning(100, 0., 150.), title="Transverse momentum of the leading lepton", xTitle= "pT(leading lepton)(GeV)"))
        #    plots.append(Plot.make1D("{0}_SubleadleptonPT".format(catN), dilepton[1].p4.Pt(), catSel, EquidistantBinning(100, 0., 150.), title="Transverse momentum of the Subleading lepton", xTitle= "pT(Sub-leading lepton)(GeV)"))


        #    if catN.split("_")[1]=="OB":
        #        plots.append(Plot.make1D("{0}_leadleptonETA".format(catN), dilepton[0].p4.eta(), catSel, EquidistantBinning(10, 0.8,2.), title="Pseudo-rapidity of the leading lepton", xTitle= "Eta(leading lepton)"))
        #        plots.append(Plot.make1D("{0}_subleadleptonETA".format(catN), dilepton[1].p4.eta(), catSel, EquidistantBinning(10, 0.8, 2), title="Pseudo-rapidity of the sub-leading lepton", xTitle= "Eta(Sub-leading lepton)"))
        #    elif catN.split("_")[1]=="IB":
        #        plots.append(Plot.make1D("{0}_leadleptonETA".format(catN), dilepton[0].p4.eta(), catSel, EquidistantBinning(10, -1.4,1.4), title="Pseudo-rapidity of the leading lepton", xTitle= "Eta(leading lepton)"))
        #        plots.append(Plot.make1D("{0}_subleadleptonETA".format(catN), dilepton[1].p4.eta(), catSel, EquidistantBinning(10, -1.4, 1.4), title="Pseudo-rapidity of the sub-leading lepton", xTitle= "Eta(Sub-leading lepton)"))
        #    else:
        #        plots.append(Plot.make1D("{0}_leadleptonETA".format(catN), dilepton[0].p4.eta(), catSel, EquidistantBinning(10, 1.2,2), title="Pseudo-rapidity of the leading lepton", xTitle= "Eta(leading lepton)"))
        #        plots.append(Plot.make1D("{0}_subleadleptonETA".format(catN), dilepton[1].p4.eta(), catSel, EquidistantBinning(10, 1.2, 2), title="Pseudo-rapidity of the sub-leading lepton", xTitle= "Eta(Sub-leading lepton)"))
        #    plots.append(Plot.make1D("{0}_mll".format(catN), op.invariant_mass(dilepton[0].p4, dilepton[1].p4), catSel, EquidistantBinning(100, 70., 110.), title=" dilepton invariant mass", xTitle= "mll(GeV)"))
        #    plots.append(Plot.make1D("{0}_llpT".format(catN), (dilepton[0].p4.Pt() + dilepton[1].p4.Pt()), catSel, EquidistantBinning(100,0.,150.),title= "dilepton transverse momentum" , xTitle= "dilepton pT (GeV)"))

        # select jets   // 2016 - 2017 - 2018   ( j.jetId &2) ->      tight jet ID
        jetsSel = op.select(t.Jet, lambda j : op.AND(j.p4.Pt() > 20., op.abs(j.p4.Eta())< 2.4, (j.jetId &2)))        
        # exclude from the jetsSel any jet that happens to include within its reconstruction cone a muon or an electron.
        jets= op.select(jetsSel, lambda j : op.AND(op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < 0.3 )), op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < 0.3 ))))
        #N.B: DeepJet= DeepFlavour
        # ask for the jets to be a b-jets ## DeepCSV medium b-tag working point
        if era== "2016":
            bJets = op.select(jets, lambda j : j.btagDeepB > 0.6321 ) 
            DeepB_discriVar = { "BTagDiscri": lambda j : j.btagDeepB }
            deepBMediumSF = get_scalefactor("jet", ("btag_2016_94X", "DeepCSV_medium"), additionalVariables=DeepB_discriVar)#, systName="btagging2016")  
        elif era=="2017":
            bJets = op.select(jets, lambda j : j.btagDeepB > 0.4941 ) 
            DeepB_discriVar = { "BTagDiscri": lambda j : j.btagDeepB }
            deepBMediumSF = get_scalefactor("jet", ("btag_2017_94X", "DeepCSV_medium"), additionalVariables=DeepB_discriVar)#, systName="btagging2017")  
        else:
            bJets = op.select(jets, lambda j : j.btagDeepB > 0.4184 )
            DeepB_discriVar = { "BTagDiscri": lambda j : j.btagDeepB }
            deepBMediumSF = get_scalefactor("jet", ("btag_2018_102X", "DeepCSV_medium"), additionalVariables=DeepB_discriVar, systName="btagging2018")  

        ## Dilepton selection: opposite sign & 70.<mll<120. GeV 
        osdilep_Z = lambda l1,l2 : op.AND(l1.charge != l2.charge, op.in_range(70., op.invariant_mass(l1.p4, l2.p4), 120.))

        osLLRng = {
                "MuMu" : op.combine(muons, N=2, pred=osdilep_Z),
                "ElEl" : op.combine(electrons, N=2, pred=osdilep_Z),
                "ElMu" : op.combine((electrons, muons), pred=lambda ele,mu : op.AND(osdilep_Z(ele,mu), ele.p4.Pt() > mu.p4.Pt() )),
                "MuEl" : op.combine((muons, electrons), pred=lambda mu,ele : op.AND(osdilep_Z(mu,ele), mu.p4.Pt() > ele.p4.Pt()))
                }

        hasOSLL_cmbRng = lambda cmbRng : op.AND(op.rng_len(cmbRng) > 0, cmbRng[0][0].p4.Pt() > 25.) # The leading pT for the µµ channel should be above 20 Gev !

        ## helper selection (OR) to make sure jet calculations are only done once
        hasOSLL = noSel.refine("hasOSLL", cut=op.OR(*( hasOSLL_cmbRng(rng) for rng in osLLRng.values())))
        forceDefine(t._Jet.calcProd, hasOSLL)
        for varNm in t._Jet.available:
            forceDefine(t._Jet[varNm], hasOSLL)

        llSFs = {
            "MuMu" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[0]), muMediumISOSF(ll[1]), doubleMuTrigSF(ll) ]),#,TrkIDSF(ll), TrkISOSF(ll)
            "ElMu" : (lambda ll : [ elMediumIDSF(ll[0]), muMediumIDSF(ll[1]), muMediumISOSF(ll[1]), elemuTrigSF(ll) ]),
            "MuEl" : (lambda ll : [ muMediumIDSF(ll[0]), muMediumISOSF(ll[0]), elMediumIDSF(ll[1]), mueleTrigSF(ll) ]),
            "ElEl" : (lambda ll : [ elMediumIDSF(ll[0]), elMediumIDSF(ll[1]), doubleEleTrigSF(ll) ])
            }
        categories = dict((catN, (catLLRng[0], hasOSLL.refine("hasOS{0}".format(catN), cut=hasOSLL_cmbRng(catLLRng), weight=(llSFs[catN](catLLRng[0]) if isMC else None)))) for catN, catLLRng in osLLRng.items())
        for catN, (dilepton, catSel) in categories.items():

            plots.append(Plot.make1D("{0}_leadleptonPT".format(catN), dilepton[0].p4.Pt(), catSel, EquidistantBinning(100, 0., 450.), title="Transverse momentum of the leading lepton", xTitle= "pT(leading lepton)(GeV)"))
            plots.append(Plot.make1D("{0}_SubleadleptonPT".format(catN), dilepton[1].p4.Pt(), catSel, EquidistantBinning(100, 0., 450.), title="Transverse momentum of the Subleading lepton", xTitle= "pT(Sub-leading lepton)(GeV)"))
            plots.append(Plot.make1D("{0}_leadleptonETA".format(catN), dilepton[0].p4.eta(), catSel, EquidistantBinning(10, -3, 3), title="Pseudo-rapidity of the leading lepton", xTitle= "Eta(leading lepton)"))
            plots.append(Plot.make1D("{0}_subleadleptonETA".format(catN), dilepton[1].p4.eta(), catSel, EquidistantBinning(10, -3, 3), title="Pseudo-rapidity of the sub-leading lepton", xTitle= "Eta(Sub-leading lepton)"))
            plots.append(Plot.make1D("{0}_mll".format(catN), op.invariant_mass(dilepton[0].p4, dilepton[1].p4), catSel, EquidistantBinning(100, 70., 110.), title=" dilepton invariant mass", xTitle= "mll(GeV)"))
            plots.append(Plot.make1D("{0}_llpT".format(catN), (dilepton[0].p4.Pt() + dilepton[1].p4.Pt()), catSel, EquidistantBinning(100,0.,450.),title= "dilepton transverse momentum" , xTitle= "dilepton pT (GeV)"))
            plots.append(Plot.make1D("{0}_nVX".format(catN), t.PV.npvs, catSel, EquidistantBinning(10, 0., 60.), title="Distrubtion of the number of the reconstructed vertices", xTitle="nPVX"))
            plots.append(Plot.make2D("{0}_Electron_dzdxy".format(catN), (dilepton[0].dz ,dilepton[0].dxy),catSel, (EquidistantBinning(10, 0., 2.),EquidistantBinning(10, 0., 2.)) ,title="Electron in Barrel/EndCAP region" ))

            TwoJetsTwoLeptons=catSel.refine("twoJet{0}Sel".format(catN), cut=[ op.rng_len(jets) > 1 ]) 

            plots.append(Plot.make1D("{0}_leadJetPT".format(catN), jets[0].p4.Pt(), TwoJetsTwoLeptons, EquidistantBinning(100, 0., 450.), title="Transverse momentum of the leading jet PT", xTitle= "pT(leading Jet)(GeV)"))
            plots.append(Plot.make1D("{0}_subleadJetPT".format(catN), jets[1].p4.Pt(), TwoJetsTwoLeptons,EquidistantBinning(100, 0., 450.), title="Transverse momentum of the sub-leading jet PT", xTitle= "pT(Sub-leading Jet)(GeV)"))
            plots.append(Plot.make1D("{0}_leadJetETA".format(catN), jets[0].p4.eta(), TwoJetsTwoLeptons, EquidistantBinning(10, -3, 3), title="Pseudo-rapidity of the leading jet", xTitle="Eta(leading Jet"))
            plots.append(Plot.make1D("{0}_subleadJetETA".format(catN), jets[1].p4.eta(), TwoJetsTwoLeptons, EquidistantBinning(10, -3, 3), title="Pseudo-rapidity of the sub-leading jet", xTitle="Eta(Sub-leading Jet"))
            plots.append(Plot.make1D("{0}_nJets".format(catN), op.rng_len(jets), TwoJetsTwoLeptons, EquidistantBinning(5, 2., 6.), title="Number of jets", xTitle= "nbr Jets"))
            plots.append(Plot.make1D("{0}_jjpT".format(catN), (jets[0].p4.Pt() + jets[1].p4.Pt()), TwoJetsTwoLeptons, EquidistantBinning(100,0.,450.),title= "dijet transverse momentum" , xTitle= "dijet pT (GeV)"))
            plots.append(Plot.make1D("{0}_mjj".format(catN),op.invariant_mass(jets[0].p4, jets[1].p4) , TwoJetsTwoLeptons, EquidistantBinning(100, 0., 800.), title="mjj", xTitle= "mjj(GeV)"))
            plots.append(Plot.make1D("{0}_mlljj".format(catN), (dilepton[0].p4 +dilepton[1].p4+jets[0].p4+jets[1].p4).M(), TwoJetsTwoLeptons, EquidistantBinning(100, 0., 1000.), title="mlljj", xTitle="mlljj(GeV)"))
            plots.append(Plot.make2D("{0}_mlljjvsmjj".format(catN), (op.invariant_mass(jets[0].p4, jets[1].p4),(dilepton[0].p4 +dilepton[1].p4+jets[0].p4+jets[1].p4).M()), TwoJetsTwoLeptons, (EquidistantBinning(1000, 0., 1000.), EquidistantBinning(1000, 0., 1000.)), title="mlljj vs mjj invariant mass"))

            # asking for bjets -----------------------           
            #TwoLeptonsTwoBjets = TwoJetsTwoLeptons.refine("TwoLeptonsTwoBjets{0}".format(catN), cut=[ op.rng_len(bJets) > 1 ],weight=([ deepBMediumSF(bJets[0]), deepBMediumSF(bJets[1]) ]if isMC else None))
            TwoLeptonsTwoBjets = catSel.refine("TwoLeptonsTwoBjets{0}".format(catN), cut=[ op.rng_len(bJets) > 1 ])#,weight=([ deepBMediumSF(bJets[0]), deepBMediumSF(bJets[1]) ]if isMC else None))
            plots.append(Plot.make1D("{0}_lead_BJetPT".format(catN), jets[0].p4.Pt(), TwoLeptonsTwoBjets, EquidistantBinning(100, 0., 450.), title="Transverse momentum of the leading bjet PT", xTitle= "pT(leading b-Jet)(GeV)"))
            plots.append(Plot.make1D("{0}_sublead_BJetPT".format(catN), jets[1].p4.Pt(), TwoLeptonsTwoBjets,EquidistantBinning(100, 0., 450.), title="Transverse momentum of the sub-leading bjet PT", xTitle= "pT(Sub-leading b-Jet)(GeV)"))
            plots.append(Plot.make1D("{0}_lead_BJetETA".format(catN), jets[0].p4.eta(), TwoLeptonsTwoBjets, EquidistantBinning(10, -3, 3), title="Pseudo-rapidity of the leading bjet", xTitle="Eta(leading b-Jet"))
            plots.append(Plot.make1D("{0}_sublead_BJetETA".format(catN), jets[1].p4.eta(), TwoLeptonsTwoBjets, EquidistantBinning(10, -3, 3), title="Pseudo-rapidity of the sub-leading bjet", xTitle="Eta(Sub-leading b-Jet"))
            plots.append(Plot.make1D("{0}_nBJets".format(catN), op.rng_len(jets), TwoLeptonsTwoBjets, EquidistantBinning(5, 2., 6.), title="Number of bjets", xTitle= "nbr b-Jets"))
            plots.append(Plot.make1D("{0}_twoBtaggedjetspT".format(catN), (jets[0].p4.Pt() + jets[1].p4.Pt()), TwoLeptonsTwoBjets, EquidistantBinning(100,0.,450.),title= "di-bjet transverse momentum" , xTitle= "di-bjet pT (GeV)"))
            plots.append(Plot.make1D("{0}_mjj_btagged".format(catN),op.invariant_mass(jets[0].p4, jets[1].p4) , TwoLeptonsTwoBjets, EquidistantBinning(100, 0., 800.), title="mass of two b-tagged jets", xTitle= "mjj(GeV)"))
            plots.append(Plot.make1D("{0}_mlljj_btagged".format(catN), (dilepton[0].p4 +dilepton[1].p4+jets[0].p4+jets[1].p4).M(),TwoLeptonsTwoBjets, EquidistantBinning(100, 0., 1000.), title="invariant mass of 2 leptons two b-tagged jets", xTitle="mlljj(GeV)"))
            plots.append(Plot.make2D("{0}_mlljjvsmjj_btagged".format(catN), (op.invariant_mass(jets[0].p4, jets[1].p4),(dilepton[0].p4 +dilepton[1].p4+jets[0].p4+jets[1].p4).M()),TwoLeptonsTwoBjets, (EquidistantBinning(1000, 0., 1000.), EquidistantBinning(1000, 0., 1000.)), title="mlljj vs mjj invariant mass"))
            plots.append(Plot.make1D("{0}_mll_btagged".format(catN), op.invariant_mass(dilepton[0].p4, dilepton[1].p4), TwoLeptonsTwoBjets, EquidistantBinning(100, 70., 110.), title=" dilepton invariant mass", xTitle= "mll(GeV)"))

        return plots
