from bamboo.analysismodules import NanoAODHistoModule
from bamboo.analysisutils import makeMultiPrimaryDatasetTriggerSelection
from bamboo.scalefactors import binningVariables_nano

from bamboo import treefunctions as op
from bamboo import scalefactors

from itertools import chain
import os.path

def localize_myanalysis(aPath, era="FullRunII"):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ScaleFactors_{0}".format(era), aPath)

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
          dict(("id_{wp}".format(wp=wp.lower()), ("Electron_EGamma_SF2D_2016{wp}.json".format(wp=wp)))
         for wp in ("Loose", "Medium", "Tight")).items()))

    #  TODO   --> update later with _stat & _syst   for 2016 and 2018 // for 2017 not recomended for now ( missing correction in some bins !! )
    , "muon_2016_94X" : dict((k,( localize_myanalysis(v) if isinstance(v, str)
                               else [ (eras, localize_myanalysis(path)) for eras,path in v ]))
                           for k, v in chain(
          dict(("id_{wp}".format(wp=wp.lower()), [ (tuple("Run2016{0}".format(ltr) for ltr in eras), "Muon_NUM_{wp}ID_DEN_genTracks_eta_pt_2016Run{era}.json".format(wp=wp, era=eras)) for eras in ("BCDEF", "GH") ]) for wp in ("Loose", "Medium", "Tight")).items()
        , dict(("iso_{isowp}_id_{idwp}".format(isowp=isowp.lower(), idwp=idwp.lower()),[ (tuple("Run2016{0}".format(ltr) for ltr in eras), "Muon_NUM_{isowp}RelIso_DEN_{idwp}ID_eta_pt_2016Run{era}.json".format(isowp=isowp, idwp=idwp, era=eras))for eras in ("BCDEF", "GH") ]) for (idwp,isowp) in (("Loose", "Loose"), ("Loose", "Medium"), ("Loose", "TightIDandIPCut"),  ("Tight", "Medium"), ("Tight", "TightIDandIPCut")) ).items()))

    , "btag_2016_94X" : dict((k,( tuple(localize_myanalysis(fv) for fv in v) if isinstance(v,tuple) and all(isinstance(fv, str) for fv in v)
                               else [ (eras, tuple(localize_myanalysis(fpath) for fpath in paths)) for eras,paths in v ]))
                           for k, v in
          dict(("{algo}_{wp}".format(algo=algo, wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_{algo}.json".format(wp=wp, flav=flav, calib=calib, algo=algo) for (flav, calib) in (("lightjets", "incl"), ("cjets", "comb"), ("bjets","comb")))) for wp in ("loose", "medium", "tight") for algo in ("DeepCSV", "DeepJet") ).items())

      # 2017: 
      # https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2017
      # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
   ,  "electron_2017_94X"  : dict((k,localize_myanalysis(v)) for k, v in chain(
          dict(("id_{wp}".format(wp=wp.lower()), ("Electron_EGamma_SF2D_2017{wp}.json".format(wp=wp)))
         for wp in ("Loose", "Medium", "Tight" , "Veto")).items()))


   ,  "muon_2017_94X"  : dict((k,localize_myanalysis(v)) for k, v in chain(
          dict(("id_{wp}".format(wp=wp.lower()), ("Muon_NUM_{wp}ID_DEN_genTracks__pt_abseta_2017RunBCDEF.json".format(wp=wp)))
         for wp in ("Loose", "Medium", "Tight", "Soft", "MediumPrompt")).items()
        , dict(("iso_{isowp}_id_{idwp}".format(isowp=isowp.lower(), idwp=idwp.lower()), "Muon_NUM_{isowp}RelIso_DEN_{idwp}ID_pt_abseta_2017RunBCDEF.json".format(isowp=isowp, idwp=idwp))
            for (idwp,isowp) in (("Loose", "Loose"), ("Loose", "Medium"), ("Loose", "TightIDandIPCut"),  ("Tight", "Medium"), ("Tight", "TightIDandIPCut")) ).items()))

    , "btag_2017_94X" : dict((k,( tuple(localize_myanalysis(fv) for fv in v) if isinstance(v,tuple) and all(isinstance(fv, str) for fv in v)
                               else [ (eras, tuple(localize_myanalysis(fpath) for fpath in paths)) for eras,paths in v ]))
                           for k, v in
          dict(("{algo}_{wp}".format(algo=algo, wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_{algo}_2017BtoF.json".format(wp=wp, flav=flav, calib=calib, algo=algo) for (flav, calib) in (("lightjets", "incl"), ("cjets", "comb"), ("bjets","comb")))) for wp in ("loose", "medium", "tight") for algo in ("CSVv2", "DeepCSV") ).items())
 
      # 2018:
      # https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2018      
      # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X
   ,  "electron_2018_102X"  : dict((k,localize_myanalysis(v)) for k, v in chain(  
          dict(("id_{wp}".format(wp=wp.lower()), ("Electron_EGamma_SF2D_2018{wp}.json".format(wp=wp)))
         for wp in ("Loose", "Medium", "Tight", "Veto")).items()))

   ,  "muon_2018_102X"  : dict((k,localize_myanalysis(v)) for k, v in chain(
          dict(("id_{wp}".format(wp=wp.lower()), ("Muon_NUM_{wp}ID_DEN_TrackerMuons_pt_abseta_2018RunABCD.json".format(wp=wp)))
         for wp in ("Loose", "Medium", "Tight", "Soft", "MediumPrompt")).items()
        , dict(("iso_{isowp}_id_{idwp}".format(isowp=isowp.lower(), idwp=idwp.lower()), "Muon_NUM_{isowp}RelIso_DEN_{idwp}ID_pt_abseta_2018RunABCD.json".format(isowp=isowp, idwp=idwp))
            for (idwp,isowp) in (("Loose", "Loose"), ("Loose", "Medium"), ("Loose", "TightIDandIPCut"),  ("Tight", "Medium"), ("Tight", "TightIDandIPCut")) ).items()))

    , "btag_2018_102X" : dict((k,( tuple(localize_myanalysis(fv) for fv in v) if isinstance(v,tuple) and all(isinstance(fv, str) for fv in v)
                               else [ (eras, tuple(localize_myanalysis(fpath) for fpath in paths)) for eras,paths in v ]))
                           for k, v in
          dict(("{algo}_{wp}".format(algo=algo, wp=wp), tuple("BTagging_{wp}_{flav}_{calib}_{algo}.json".format(wp=wp, flav=flav, calib=calib, algo=algo) for (flav, calib) in (("lightjets", "incl"), ("cjets", "comb"), ("bjets","comb")))) for wp in ("loose", "medium", "tight") for algo in ("DeepCSV", "DeepJet") ).items())
   
    }

def get_scalefactor(objType, key, periods=None, combine=None, additionalVariables=dict()):
    return scalefactors.get_scalefactor(objType, key, periods=periods, combine=combine, additionalVariables=additionalVariables, sfLib=all_scalefactors, paramDefs=binningVariables)

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
        from bamboo.analysisutils import configureJets
        if era == "2016":
            triggersPerPrimaryDataset = {
                "DoubleMuon" : [ tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                                 tree.HLT.Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL,
                                 tree.HLT.Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ ],
                "DoubleEG"   : [ tree.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ ],
                "MuonEG"     : [ tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,
                                 tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
                                 tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,
                                 tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ ]
                }
            if self.isMC(sample):
                configureJets(tree.Jet.calc, "AK4PFchs",
                    jec="Summer16_07Aug2017_V20_MC",
                    smear="Summer16_25nsV1_MC",
                    jesUncertaintySources=["Total"])
            else:
                if "2016B" in sample or "2016C" in sample or "2016D" in sample:
                    configureJets(tree.Jet.calc, "AK4PFchs",
                        jec="Summer16_07Aug2017BCD_V11_DATA")
                elif "2016E" in sample or "2016F" in sample:
                    configureJets(tree.Jet.calc, "AK4PFchs",
                        jec="Summer16_07Aug2017EF_V11_DATA")
                elif "2016G" in sample or "2016H" in sample:
                    configureJets(tree.Jet.calc, "AK4PFchs",
                        jec="Summer16_07Aug2017GH_V11_DATA")

        elif era == "2017":
            triggersPerPrimaryDataset = {
                "DoubleMuon" : [ tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8,
                                 tree.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8 ],
                "DoubleEG"   : [ tree.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL ],
                # it's recommended to not use the DZ  version  for 2017 and 2018, it would be a needless efficiency loss
                #---> https://twiki.cern.ch/twiki/bin/view/CMS/EgHLTRunIISummary
                "MuonEG"     : [ tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL,
                                 tree.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,
                                 tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL,
                                 tree.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ ]
                }
            if self.isMC(sample):
                configureJets(tree.Jet.calc, "AK4PFchs",
                    jec="Fall17_17Nov2017_V32_94X_MC",
                    smear="Fall17_V3_MC",
                    jesUncertaintySources=["Total"])
            else:
                configureJets(tree.Jet.calc, "AK4PFchs", jec="Fall17_17Nov2017_V32_94X_DATA")

        elif era == "2018":
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
                configureJets(tree.Jet.calc, "AK4PFchs",
                    jec="Autumn18_V8_MC",
                    smear="Autumn18_V1_MC",
                    jesUncertaintySources=["Total"])
            else:
                configureJets(tree.Jet.calc, "AK4PFchs", jec="Autumn18_RunABCD_V8_DATA")
        else:
            raise RuntimeError("Unknown era {0}".format(era))

        if self.isMC(sample):
            noSel = noSel.refine("genWeight", weight=tree.genWeight, cut=op.OR(*chain.from_iterable(triggersPerPrimaryDataset.values())))
        else:
            noSel = noSel.refine("withTrig", cut=makeMultiPrimaryDatasetTriggerSelection(sample, triggersPerPrimaryDataset))

        return tree,noSel,be,lumiArgs

    def definePlots(self, t, noSel, systVar="nominal", era=None, sample=None):

        from bamboo.plots import Plot, EquidistantBinning
        from bamboo import treefunctions as op

        puWeightsFile = None
        if era == "2016":
            sfTag="94X"
            puWeightsFile = os.path.join(os.path.dirname(__file__), "data", "puweights2016.json")
        elif era == "2017":
            sfTag="94X"     
        elif era == "2018":
            sfTag="102X"
        if self.isMC(sample) and puWeightsFile is not None:
            from bamboo.analysisutils import makePileupWeight
            noSel = noSel.refine("puWeight", weight=makePileupWeight(puWeightsFile, t.Pileup_nTrueInt, variation="Nominal"))

        plots = []

        # TODO add the ID & ISO depeneding on the era select muons with pT>10. GeV  and  eta ...
        # Wp // 2016- 2017 -2018 : Muon_mediumId   
        #muons = op.select(t.Muon, lambda mu : op.AND(mu.p4.Pt() > 10., op.abs(mu.p4.Eta()) < 2.4, mu.mediumId, mu.pfRelIso04_all<0.15))    
        muons = op.select(t.Muon, lambda mu : op.AND(mu.p4.Pt() > 10., op.abs(mu.p4.Eta()) < 2.4, mu.mediumId, mu.pfRelIso04_all<0.15))
        # search for opposite signe muons from the one that pass the selection
        OsMuMu = op.combine(muons, N=2, pred=lambda mu1,mu2 : mu1.charge != mu2.charge)
        firstosmumu = OsMuMu[0]
        # find at least one pair of opposite signe muons where the leading one is above 25 GeV  & apply SFs  also i ask for 70GeV < mll <110Gev to suppress quarkonia resonances and jets misidentified as leptons, the Trigger selection is applied here for now
        muMediumIDSF = get_scalefactor("lepton", ("muon_{0}_{1}".format(era, sfTag), "id_medium"), combine="weight")
        hasOsMuMu = noSel.refine("twoosMuons", cut=[ op.rng_len(OsMuMu) >= 1 , firstosmumu[0].p4.Pt() > 20. ,op.in_range(70, op.invariant_mass( firstosmumu[0].p4, firstosmumu[1].p4),110.) ], weight=[muMediumIDSF(firstosmumu[0]), muMediumIDSF(firstosmumu[1])])
        # cut where the muons are not opposite signe, the leading muons is set to be above 20GeV, where the subleading is intialize first in the muons selection : choice up to you in the selection !
        hasTwoMuons=noSel.refine("hasMuon", cut=[op.rng_len(muons) > 1 , muons[0].p4.Pt() > 20.,  op.in_range(70., op.invariant_mass(muons[0].p4, muons[1].p4) ,110.) ], weight=[muMediumIDSF(muons[0]), muMediumIDSF(muons[1])])

#---------------------------------------
 
        # Wp  // 2016: Electron_cutBased_Sum16==3  -> medium     // 2017 -2018  : Electron_cutBased_Fall17_V1 ==3   --> medium
        if era=="2016":        
            electrons = op.select(t.Electron, lambda ele : op.AND(ele.p4.Pt() > 15., op.abs(ele.p4.Eta()) < 2.5 , ele.cutBased_Sum16>=3 ))
        else: 
            electrons = op.select(t.Electron, lambda ele : op.AND(ele.p4.Pt() > 15., op.abs(ele.p4.Eta()) < 2.5 , ele.cutBased_Fall17_V1>=3 ))

        elMediumIDSF = get_scalefactor("lepton", ("electron_{0}_{1}".format(era,sfTag), "id_medium"))
        OsElEl = op.combine(electrons, N=2, pred=lambda ele1,ele2 : ele1.charge != ele2.charge)
        firstoselel = OsElEl[0]
        hasOsElEl = noSel.refine("twoosElectrons", cut=[op.rng_len(OsElEl) >= 1, firstoselel[0].p4.Pt() > 25. , op.in_range(70, op.invariant_mass(firstoselel[0].p4, firstoselel[1].p4), 110.)], weight=[elMediumIDSF(firstoselel[0]), elMediumIDSF(firstoselel[1])])
        hasTwoElectrons = noSel.refine("hasElectron", cut=[op.rng_len(electrons) >1 , electrons[0].p4.Pt() > 25., op.in_range(70., op.invariant_mass( electrons[0].p4, electrons[1].p4),110.)], weight=[elMediumIDSF(electrons[0]), elMediumIDSF(electrons[1])])


#--------------------
        # select jets   // 2016 - 2017 - 2018   ( j.jetId &2) ->      tight jet ID
        jetsSel = op.select(t.Jet["nominal"], lambda j : op.AND(j.p4.Pt() > 20., op.abs(j.p4.Eta())< 2.4, (j.jetId &2)))        
        # exclude from the jetsSel any jet that happens to include within its reconstruction cone a muon or an electron.
        jets= op.select(jetsSel, lambda j : op.AND(op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < 0.3 )), op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < 0.3 ))))
                        

        hasElectronMuon = noSel.refine("hasElectronMuon", cut=[ op.rng_len(muons) > 0, op.rng_len(electrons) > 0, electrons[0].p4.Pt() > 25. , muons[1].p4.pt() > 10., op.in_range(70., op.invariant_mass( electrons[0].p4, muons[1].p4), 110.) ])
        OsElMu = op.combine((electrons, muons), pred=lambda ele,mu : ele.charge != mu.charge)
        firstoselmu = OsElMu[0]
        hasOsElMu = noSel.refine("twoosElectronMuon", cut=[ op.rng_len(OsElMu) >= 1, op.in_range(70., op.invariant_mass( firstoselmu[0].p4, firstoselmu[1].p4),110.)])


        hasMuonElectron = noSel.refine("hasMuonElectron", cut=[op.rng_len(muons) > 0, op.rng_len(electrons) > 0, muons[0].p4.Pt() > 25. , electrons[1].p4.pt() > 15., op.in_range(70., op.invariant_mass( muons[0].p4, electrons[1].p4), 110.) ])
        OsMuEl = op.combine((muons, electrons), N=2, pred=lambda ele,mu : ele.charge != mu.charge)
        firstosmuel = OsMuEl[0]
        hasOsMuEl= noSel.refine("twoosMuonElectron", cut=[op.rng_len(OsMuEl) >= 1, op.in_range(70., op.invariant_mass( firstosmuel[0].p4, firstosmuel[1].p4),110.)])

#--------------------------
        #met=noSel.refine("MissingEnergyTransverse", cut=[]) #TODO

        #categories for non opposite signe leptons 
        #categories = {"ElEl" : (firstoselel, hasTwoElectrons),
                     # "ElMu" : (firstoselmu, hasElectronMuon), 
                     # "MuEl" : (firstosmuel, hasMuonElectron), 
                     # "MuMu" : (firstosmumu, hasTwoMuons)}


        categories = {"ElEl" : (firstoselel, hasOsElEl),
                      "ElMu" : (firstoselmu, hasOsElMu), 
                      "MuEl" : (firstosmuel, hasOsMuEl), 
                      "MuMu" : (firstosmumu, hasOsMuMu)}


        #plots.append(Plot.make1D("lead muon_miniPFRelIso_all ", ??miniPFRelIso_all,hasOsMuMu, EquidistantBinning(100, 0., 10.), title="lead_Muon_miniPFRelIso_all", xTitle= "lead Muon_miniPFRelIso_all"))
        #plots.append(Plot.make1D("lead Muon_minipfRelIso03_all ", ??miniPFRelIso3_all,hasOsMuMu, EquidistantBinning(100, 0., 10.), title="lead_Muon_miniPFRelIso03_all", xTitle= "lead Muon_miniPFRelIso03_all"))
        #plots.append(Plot.make1D("lead Muon_pfRelIso03_all ", ??PFRelIso4_all,hasOsMuMu, EquidistantBinning(100, 0., 10.), title="lead_Muon_PFRelIso04_all", xTitle= "lead Muon_PFRelIso04_all"))

        for catN, (dilepton, catSel) in categories.items():

            plots.append(Plot.make1D("{0}_leadleptonPT".format(catN), dilepton[0].p4.Pt(), catSel, EquidistantBinning(100, 0., 600.), title="Transverse momentum of the leading lepton", xTitle= "pT(leadin lepton)(GeV)"))
            plots.append(Plot.make1D("{0}_SubleadleptonPT".format(catN), dilepton[1].p4.Pt(), catSel, EquidistantBinning(100, 0., 600.), title="Transverse momentum of the Subleading lepton", xTitle= "pT(Sub-leading lepton)(GeV)"))
            plots.append(Plot.make1D("{0}_leadleptonETA".format(catN), dilepton[0].p4.eta(), catSel, EquidistantBinning(10, -3, 3), title="Pseudo-rapidity of the leading lepton", xTitle= "Eta(leading lepton)"))
            plots.append(Plot.make1D("{0}_subleadleptonETA".format(catN), dilepton[1].p4.eta(), catSel, EquidistantBinning(10, -3, 3), title="Pseudo-rapidity of the sub-leading lepton", xTitle= "Eta(Sub-leading lepton)"))
            plots.append(Plot.make1D("{0}_mll".format(catN), op.invariant_mass(dilepton[0].p4, dilepton[1].p4), catSel, EquidistantBinning(100, 60., 120.), title=" dilepton invariant mass", xTitle= "mll(GeV)"))
            plots.append(Plot.make1D("{0}_llpT".format(catN), (dilepton[0].p4.Pt() + dilepton[1].p4.Pt()), catSel, EquidistantBinning(100,0.,600.),title= "dilepton transverse momentum" , xTitle= "dilepton pT (GeV)"))
            #plots.append(Plot.make1D("{0}_nleptons".format(catN),op.rng_len(dilepton), catSel, EquidistantBinning(5,2.,5.),title= "Number of leptons" , xTitle= "nbr leptons"))
            plots.append(Plot.make1D("{0}_nVX".format(catN), t.PV.npvs, catSel, EquidistantBinning(10, 0., 60.), title="Distrubtion of the number of the reconstructed vertices", xTitle="nPVX"))


            from bamboo.analysisutils import forceDefine
            forceDefine(t.Jet.calcProd, catSel)

            TwoJetsTwoLeptons=catSel.refine("twoJet{0}Sel".format(catN), cut=[ op.rng_len(jets) > 1 ]) 

            plots.append(Plot.make1D("{0}_leadJetPT".format(catN), jets[0].p4.Pt(), TwoJetsTwoLeptons, EquidistantBinning(100, 0., 600.), title="Transverse momentum of the leading jet PT", xTitle= "pT(leading Jet)(GeV)"))
            plots.append(Plot.make1D("{0}_subleadJetPT".format(catN), jets[1].p4.Pt(), TwoJetsTwoLeptons,EquidistantBinning(100, 0., 600.), title="Transverse momentum of the sub-leading jet PT", xTitle= "pT(Sub-leading Jet)(GeV)"))
            plots.append(Plot.make1D("{0}_leadJetETA".format(catN), jets[0].p4.eta(), TwoJetsTwoLeptons, EquidistantBinning(10, -3, 3), title="Pseudo-rapidity of the leading jet", xTitle="Eta(leading Jet"))
            plots.append(Plot.make1D("{0}_subleadJetETA".format(catN), jets[1].p4.eta(), TwoJetsTwoLeptons, EquidistantBinning(10, -3, 3), title="Pseudo-rapidity of the sub-leading jet", xTitle="Eta(Sub-leading Jet"))
            plots.append(Plot.make1D("{0}_nJets".format(catN), op.rng_len(jets), TwoJetsTwoLeptons, EquidistantBinning(5, 2., 5.), title="Number of jets", xTitle= "nbr Jets"))

            plots.append(Plot.make1D("{0}_jjpT".format(catN), (jets[0].p4.Pt() + jets[1].p4.Pt()), TwoJetsTwoLeptons, EquidistantBinning(100,0.,600.),title= "dijet transverse momentum" , xTitle= "dijet pT (GeV)"))

            plots.append(Plot.make1D("{0}_mjj".format(catN),op.invariant_mass(jets[0].p4, jets[1].p4) , TwoJetsTwoLeptons, EquidistantBinning(100, 0., 800.), title="mjj", xTitle= "mjj(GeV)"))
            plots.append(Plot.make1D("{0}_mlljj".format(catN), (dilepton[0].p4 +dilepton[1].p4+jets[0].p4+jets[1].p4).M(), TwoJetsTwoLeptons, EquidistantBinning(100, 0., 800.), title="mlljj", xTitle="mlljj(GeV)"))
            plots.append(Plot.make2D("{0}_mlljjvsmjj".format(catN), (op.invariant_mass(jets[0].p4, jets[1].p4),(dilepton[0].p4 +dilepton[1].p4+jets[0].p4+jets[1].p4).M()), TwoJetsTwoLeptons, (EquidistantBinning(1000, 0., 1000.), EquidistantBinning(1000, 0., 1000.)), title="mlljj vs mjj invariant mass"))


            #plots.append(Plot.make1D("{0}_MET_pT".format(catN),!!!!! , TwoJetsTwoLeptons, EquidistantBinning(100, 0., 800.), title="MET_pT", xTitle= "missing pT(GeV)"))  #TODO


        return plots
