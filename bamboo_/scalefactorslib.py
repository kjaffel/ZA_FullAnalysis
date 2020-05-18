from itertools import chain
import os.path
import sys

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_')

def localize_myanalysis(aPath, version="FullRunIIv1"):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ScaleFactors_{0}".format(version), aPath)

def localize_trigger(aPath):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "TriggerEfficienciesStudies", aPath)

def localize_PileupJetID(aPath):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "PileupJetID", aPath)

def localize_eChargeMisIDRates(aPath):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "eChargeMisId", aPath)

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
                                for wp in ("Loose", "Medium", "Tight")).items(),
                                #for wp in ("Loose", "Medium", "Tight", "MVA80","MVA90", "MVA80noiso", "MVA90noiso")).items())),
                              
                               dict(("reco_{pt}_{ver}".format(pt=pt, ver=ver), 
                                ("Electron_EGamma_SF2D_RECO_2016_RunBtoH_{pt}_from{ver}.json".format(pt=pt, ver=ver)))
                                for pt in ("ptL20", "ptG20") for ver in ('POG', 'tth')).items(),
                              )),
       #"electronReco_2016_94X" : { "reco": localize_myanalysis("Electron_EGamma_SF2D_RecoSF_Legacy2016_RunBtoH_ptabove20GeV.json")},
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
      
       "JetId_InHighPileup_2016_94X" : dict((k, localize_PileupJetID(v)) for k, v in chain(
                                        dict(("puid_{wp}".format(wp=wp), 
                                            ("puID_SFs_2016{wp}.json".format(wp=wp))) 
                                            for wp in ("L", "M", "T")).items() 
                                        )),
        
       ####################################
      # 2017: 
      #####################################
      # Muons:      https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2017
      # Btagging:   https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
       
       "electron_2017_94X"  : dict((k,localize_myanalysis(v)) for k, v in chain(
                               dict(("id_{wp}".format(wp=wp.lower()), 
                                ("Electron_EGamma_SF2D_2017_{wp}_Fall17V2.json".format(wp=wp)))
                                for wp in ("Loose", "Medium", "Tight" )).items(),
                                                            
                               dict(("reco_{pt}_{ver}".format(pt=pt, ver=ver), 
                                ("Electron_EGamma_SF2D_RECO_2017RunBCDEF_{pt}_from{ver}.json".format(pt=pt, ver=ver)))
                                for pt in ("ptL20", "ptG20") for ver in ('POG', 'tth')).items(),
                               
                              )), 
       #"electronReco_2017_94X" : { "reco": localize_myanalysis("Electron_EGamma_SF2D_RECO_2017RunBCDEF_ptabove20GeV.json")},

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
                          # periode dependency:
                          dict(("{algo}_{wp}_period_dependency".format(algo=algo, wp=wp), [ (tuple("Run2017{0}".format(ltr)for ltr in eras),
                            "BTagging_{wp}_{flav}_{calib}_{algo}_2017{era}.json".format(wp=wp, flav=flav, calib=calib, algo=algo, era=eras))
                            #for eras in ("B", "CtoE_upto304671", "E_from304672_toF") for (flav, calib) in (("lightjets", "incl"), ("cjets", "comb"), ("bjets","comb"))])
                            for eras in ("B", "CDE", "EF") for (flav, calib) in (("lightjets", "incl"), ("cjets", "comb"), ("bjets","comb"))])
                            for wp in ("loose", "medium", "tight") for algo in ("DeepCSV",)).items(),
        # Boosted :
                          dict(("subjet_{algo}_{wp}".format(algo=algo, wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_subjet_{algo}_2017BtoF.json".format(wp=wp, flav=flav, calib=calib, algo=algo)
                            for (flav, calib) in (("lightjets", "incl"), ("cjets", "lt"), ("bjets","lt")))) for wp in ("loose", "medium") for algo in ("DeepCSV", ) ).items(),
                         )),

        #---- Single Lepton trigger ------------------
       "mutrig_2017_94X" : { "single_muon": localize_trigger("IsoMu27_PtEtaBins_2017RunBtoF.json"),},
       "eletrig_2017_94X" : { "single_electron": localize_trigger("Electron_ele28_ht150_OR_ele32.json"),},
                           #tuple(localize_trigger("{0}_PtEtaBins_2017RunBtoF.json".format(trig)) 
                           # for trig in ("IsoMu27", )), #"Mu50")), 
       
       "JetId_InHighPileup_2017_94X" : dict((k,localize_PileupJetID(v)) for k, v in chain(
                                            dict(("puid_eff_sf_{wp}".format(wp=wp), ("puId_h2_eff_sf2017_{wp}.json".format(wp=wp))) for wp in ("L", "M", "T")).items(),
                                            
                                            dict(("puid_eff_mc_{wp}".format(wp=wp), ("puId_h2_eff_mc2017_{wp}.json".format(wp=wp))) for wp in ("L", "M", "T")).items(),
                                            dict(("puid_eff_data_{wp}".format(wp=wp), ("puId_h2_eff_data2017_{wp}.json".format(wp=wp))) for wp in ("L", "M", "T")).items(),
                                            
                                            dict(("puid_mistag_mc_{wp}".format(wp=wp), ("puId_h2_mistag_mc2017_{wp}.json".format(wp=wp))) for wp in ("L", "M", "T")).items(),
                                            dict(("puid_mistag_data_{wp}".format(wp=wp), ("puId_h2_mistag_data2017_{wp}.json".format(wp=wp))) for wp in ("L", "M", "T")).items(),
                                            
                                            dict(("puid_mistag_sf_{wp}".format(wp=wp), ("puId_h2_mistag_sf2017_{wp}.json".format(wp=wp))) for wp in ("L", "M", "T")).items(),
                                    )),
      ##################################
      # 2018:
      ##################################
      # Muons:      https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2018      
      # Btagging:   https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X

       "electron_2018_102X"  : dict((k,localize_myanalysis(v)) for k, v in chain(  
                                dict(("id_{wp}".format(wp=wp.lower()), 
                                 ("Electron_EGamma_SF2D_2018_{wp}_Fall17V2.json".format(wp=wp)))
                                 for wp in ("Loose", "Medium", "Tight")).items(),
                               
                               dict(("reco__{ver}".format(ver=ver), 
                                ("Electron_EGamma_SF2D_RECO_2018_from{ver}.json".format(ver=ver)))
                                for ver in ('POG', 'tth')).items(),
                               
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
                            for trig in ("IsoMu24_OR_IsoTkMu24","Mu50_OR_OldMu100_OR_TkMu100" )),
       # -------------- Pileup -----------------------------------------
       "JetId_InHighPileup_2018_102X" : dict((k,localize_PileupJetID(v)) for k, v in chain(
                                            dict(("puid_eff_sf_{wp}".format(wp=wp), ("puId_h2_eff_sf2018_{wp}.json".format(wp=wp))) for wp in ("L", "M", "T")).items(),
                                            
                                            dict(("puid_eff_mc_{wp}".format(wp=wp), ("puId_h2_eff_mc2018_{wp}.json".format(wp=wp))) for wp in ("L", "M", "T")).items(),
                                            dict(("puid_eff_data_{wp}".format(wp=wp), ("puId_h2_eff_data2018_{wp}.json".format(wp=wp))) for wp in ("L", "M", "T")).items(),
                                            
                                            dict(("puid_mistag_mc_{wp}".format(wp=wp), ("puId_h2_mistag_mc2018_{wp}.json".format(wp=wp))) for wp in ("L", "M", "T")).items(),
                                            dict(("puid_mistag_data_{wp}".format(wp=wp), ("puId_h2_mistag_data2018_{wp}.json".format(wp=wp))) for wp in ("L", "M", "T")).items(),
                                            
                                            dict(("puid_mistag_sf_{wp}".format(wp=wp), ("puId_h2_mistag_sf2018_{wp}.json".format(wp=wp))) for wp in ("L", "M", "T")).items(),
                                        )),

       "eChargeMisID" : dict((k,localize_eChargeMisIDRates(v)) for k, v in chain(
                            dict(("eCharge_{era}".format(era=era), ("eCharge_misidentification_rates_{era}.json".format(era=era))) for era in ("2016", "2017", "2018")).items(),
                            )),
    }
