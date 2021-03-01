import os
import sys
import logging
import collections
from collections import defaultdict
logger = logging.getLogger("ZA NanoGen")

from bamboo.analysismodules import NanoAODHistoModule
from bamboo.analysisutils import makePileupWeight

from bamboo.plots import Plot
from bamboo.plots import SummedPlot
from bamboo.plots import CutFlowReport
from bamboo.plots import EquidistantBinning as EqBin
from bamboo import treefunctions as op
GENPath = os.path.dirname(__file__)
if GENPath not in sys.path:
    sys.path.append(GENPath)

import utils
from bamboo.treedecorators import NanoAODDescription
from itertools import product, repeat

nanoGenDescription = NanoAODDescription(
    groups=["HTXS_", "Generator_", "MET_", "GenMET_", "LHE_", "GenVtx_"],
    collections=["nGenPart", "nGenJet", "nGenJetAK8", "nGenVisTau", "nGenDressedLepton", "nGenIsolatedPhoton", "nLHEPart"]
)
class NanoGenHtoZAPlotter(NanoAODHistoModule):
    """ H->Z(ll)A(bb) Nano-Gen studies """
    def __init__(self, args):
        super(NanoGenHtoZAPlotter, self).__init__(args)
        self.plotDefaults = {
                            "y-axis"           : "Events",
                            #"log-y"            : "both",
                            "y-axis-show-zero" : True,
                            "save-extensions"  : ["png"],
                            "show-ratio"       : True,
                            "sort-by-yields"   : False,
                            "legend-columns"   : 2
                            #"normalized"       : True # normalize to 1 
                            }
        self.doSysts = self.args.systematic
        self.doProcess = self.args.process
    def addArgs(self, parser):
        super(NanoGenHtoZAPlotter, self).addArgs(parser)
        parser.add_argument("-s", "--systematic", action="store_true", help="Produce systematic variations")
        parser.add_argument("-p", "--process", type=str, choices=['ggH', 'bbH', 'both'], default='both', help="handle both process in the yml sepertaly if needed")
        parser.add_argument("--backend", type=str, default="dataframe", help="Backend to use, 'dataframe' (default) or 'lazy'")

    def prepareTree(self, tree, sample=None, sampleCfg=None):
        tree,noSel,be,lumiArgs = super(NanoGenHtoZAPlotter, self).prepareTree(tree, sample=sample, sampleCfg=sampleCfg, description=nanoGenDescription)
        if self.isMC(sample):
            # if it's a systematics sample, turn off other systematics
            if "syst" in sampleCfg:
                self.doSysts = False
            noSel = noSel.refine("mcWeight", weight=tree.genWeight, autoSyst=self.doSysts)
            if self.doSysts:
                noSel = utils.addTheorySystematics(self, sample, sampleCfg, tree, noSel)
        return tree,noSel,be,lumiArgs

    def definePlots(self, t, noSel, sample=None, sampleCfg=None):
        plots = []
        selections_for_cutflowreport = []
        binScaling=1
        
        plotsToSum = defaultdict(list)
        selections_for_cutflowreport.append(noSel)

        plots += [ Plot.make1D('GenPartmap_pdgIDs', op.map(t.GenPart, lambda p : p.pdgId), noSel, EqBin(100, -50., 50.), title="GenPart PdgID")]
        plots += [ Plot.make1D('LHEPartmap_pdgIDs', op.map(t.LHEPart, lambda p : p.pdgId), noSel, EqBin(100, -50., 50.), title="LHEPart PdgID")]

        ##############################################################################################
        #                           No Filter Plots 
        ##############################################################################################
        
        h2_fromGenPart = op.select(t.GenPart,lambda obj: obj.pdgId == 35 )
        h3_fromGenPart = op.select(t.GenPart,lambda obj: obj.pdgId == 36 )
        z_fromGenPart  = op.select(t.GenPart,lambda obj: obj.pdgId == 23)
        
        h2_fromLHEPart = op.select(t.LHEPart,lambda obj: obj.pdgId == 35 )
        h3_fromLHEPart = op.select(t.LHEPart,lambda obj: obj.pdgId == 36 )
        z_fromLHEPart  = op.select(t.LHEPart,lambda obj: obj.pdgId == 23)

        #FIXME craches for these three ==> 
        #for obj, genPart in zip(["h2_fromLHEPart", "h3_fromLHEPart", "z_fromLHEPart"], [h2_fromLHEPart, h3_fromLHEPart, z_fromLHEPart]):
        for obj, genPart in zip(["h2_fromGenPart", "h3_fromGenPart", "z_fromGenPart"], [h2_fromGenPart, h3_fromGenPart, z_fromGenPart]):
            plots += [ Plot.make1D(f"{obj}_{nm}", var, noSel, binning,
                    title=f"GEN {obj} {title}")
                    for nm, (var, binning, title) in {
                        "PT" : (genPart[0].p4.Pt() , EqBin(60 // binScaling, 0., 450.), "P_{T} [GeV]"),
                        "Phi": (genPart[0].p4.Phi(), EqBin(50 // binScaling, -3.1416, 3.1416), "#phi"),
                        "Eta": (genPart[0].p4.Eta(), EqBin(50 // binScaling, -3., 3.), "Eta"),
                        "Mass": (genPart[0].p4.M(), EqBin(60//binScaling, 0., 850.), "Mass [GeV]"),
                        }.items() ]
        # https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/mc94Xv2_doc.html#Generator
        plots += [ Plot.make1D(f"Generator_{nm}", var, noSel, binning,
                    title=f"{title}")
                    for nm, (var, binning, title) in {
                    "id1" : (t.Generator.id1, EqBin(100 // binScaling, 0., 100.), "id of 1st parton"),
                    "id2": (t.Generator.id1, EqBin(100 // binScaling, 0., 100.), "id of 2nd parton"),
                    "scalePDF": (t.Generator.scalePDF, EqBin(50 // binScaling, 0., 800.), "Q2 scale for PDF"),
                    "weight":(t.Generator.weight, EqBin(50//binScaling, 50., 800.), "MC generator weight"),
                    "x1":(t.Generator.x1, EqBin(50//binScaling, 50., 800.), "x1 fraction of proton momentum carried by the 1st parton"),
                    "x2":(t.Generator.x2, EqBin(50//binScaling, 50., 800.), "x2 fraction of proton momentum carried by the 2nd parton"),
                    "xpdf1":(t.Generator.xpdf1, EqBin(50//binScaling, 50., 800.), "x1pdf1"),
                    "xpdf2":(t.Generator.xpdf2, EqBin(50//binScaling, 50., 800.), "x2pdf2"),
            }.items() ]
        
        ##############################################################################################
        
        sorted_GenDressedLepton = op.sort(t.GenDressedLepton, lambda lep : -lep.pt)
        genMuons = op.select(sorted_GenDressedLepton, lambda l : op.AND( op.abs(l.pdgId) == 13, op.abs(l.eta) < 2.4, l.pt > 10.))
        genElectrons = op.select(sorted_GenDressedLepton, lambda l : op.AND(op.abs(l.pdgId) == 11, op.abs(l.eta) < 2.5, l.pt > 15.))

        sorted_GenJet= op.sort(t.GenJet, lambda j : -j.pt)
        genJets = op.select(sorted_GenJet, lambda j : op.AND( j.pt > 20., op.abs(j.eta) < 2.4))
        genCleanedJets = op.select(genJets, lambda j: op.AND(
                            op.NOT(op.rng_any(genElectrons, lambda el: op.deltaR(j.p4, el.p4) < 0.4 )),
                            op.NOT(op.rng_any(genMuons, lambda mu: op.deltaR(j.p4, mu.p4) < 0.4 ))
                        ))

        sorted_GenJetAK8= op.sort(t.GenJetAK8, lambda j : -j.pt)
        genJetsAK8 = op.select(sorted_GenJetAK8, lambda j : op.AND(j.pt > 200., op.abs(j.eta) >2.4))

        genBJets = op.select(genCleanedJets, lambda jet: jet.hadronFlavour == 5)
        genLightJets = op.select(genCleanedJets, lambda jet: jet.hadronFlavour != 5)

        Jets_dict = { "nGenJets": genJets,
                      "nGenBJets" : genBJets,
                      "nGenLightJets": genLightJets}

        for key, Obs in Jets_dict.items():
            plots.append(Plot.make1D(f"{key}", op.rng_len(Obs), noSel,
                        EqBin(10, 0., 10.), title=f"{key}"))

        ##############################################################################################
        OSSFLeptons_Zmass = lambda lep1,lep2 : op.AND(lep1.pdgId == -lep2.pdgId, op.in_range(70., op.invariant_mass(lep1.p4, lep2.p4), 120.))
        OSSFLeptons   = lambda lep1,lep2 : op.AND(lep1.pdgId == -lep2.pdgId)
        LowMass_cut = lambda lep1, lep2: op.invariant_mass(lep1.p4, lep2.p4)>12.

        hasOSLL_cmbRng = lambda cmbRng : op.AND(op.rng_len(cmbRng) > 0, cmbRng[0][0].pt > 25.) 
        OSLeptons = { "mumu": op.combine(genMuons, N=2, pred= OSSFLeptons_Zmass),
                      "elel": op.combine(genElectrons, N=2, pred=OSSFLeptons_Zmass),
                      "elmu": op.combine((genMuons, genElectrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), mu.pdgId != -ele.pdgId)),
                    }

        TwoOSLeptonsSel = noSel.refine("hasOSLL", cut=op.OR(*( hasOSLL_cmbRng(rng) for rng in OSLeptons.values())))
        categories = dict((channel, (catLLRng[0], TwoOSLeptonsSel.refine("hasOs{0}".format(channel), cut=hasOSLL_cmbRng(catLLRng)))) for channel, catLLRng in OSLeptons.items())
            
        jetsscenarios = { 'at_least_2jets': op.rng_len(genCleanedJets) > 1,
                          'exactly_2jets' : op.rng_len(genCleanedJets) == 2,
                        }
        
        bjetsscenarios = { 'at_least_2bjets': op.rng_len(genBJets) > 1,
                           'exactly_2bjets' : op.rng_len(genBJets) == 2,
                        }
        
        if "_bbH4F_" in sample :
            jetsscenarios.update( {'at_least_3jets': op.rng_len(genCleanedJets) > 2})
            bjetsscenarios.update( {'at_least_3bjets': op.rng_len(genBJets) > 2})

        ##############################################################################################
        GEN_FLAGS = {
            "IsPrompt": 0,
            "IsDecayedLeptonHadron": 1,
            "IsTauDecayProduct": 2,
            "IsPromptTauDecayProduct": 3,
            "IsDirectTauDecayProduct": 4,
            "IsDirectPromptTauDecayProduct": 5,
            "IsDirectHadronDecayProduct": 6,
            "IsHardProcess": 7,
            "FromHardProcess": 8,
            "IsHardProcessTauDecayProduct": 9,
            "IsDirectHardProcessTauDecayProduct": 10,
            "FromHardProcessBeforeFSR": 11,
            "IsFirstCopy": 12,
            "IsLastCopy": 13,
            "IsLastCopyBeforeFSR": 14,
            }

        GoodGenParticles = op.select(t.GenPart, lambda p : op.OR(p.statusFlags & 2**GEN_FLAGS["IsHardProcess"], p.statusFlags & 2**GEN_FLAGS["FromHardProcess"]))#, p.parent.idx >= 0 ))
        sorted_GoodGenParticles = op.sort(GoodGenParticles, lambda lep : -lep.pt)
        GoodGenElectrons = op.select(sorted_GoodGenParticles, lambda l : op.AND(op.abs(l.pdgId) == 11, op.abs(l.eta) < 2.5, l.pt > 15.))
        GoodGenMuons= op.select(sorted_GenDressedLepton, lambda l : op.AND( op.abs(l.pdgId) == 13, op.abs(l.eta) < 2.4, l.pt > 10.))
        
        
        GoodOSLeptons = { "mumu": op.combine(GoodGenMuons, N=2, pred= OSSFLeptons_Zmass),
                      "elel": op.combine(GoodGenElectrons, N=2, pred=OSSFLeptons_Zmass),
                      "elmu": op.combine((GoodGenMuons, GoodGenElectrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), mu.pdgId != -ele.pdgId)),
                    }
        
        TwoGoodOSLeptonsSel = noSel.refine("hasGoodOSLL", cut=op.OR(*( hasOSLL_cmbRng(rng) for rng in GoodOSLeptons.values())))
        categories2 = dict((channel, (catLLRng[0], TwoGoodOSLeptonsSel.refine("hasGoodOs{0}".format(channel), cut=hasOSLL_cmbRng(catLLRng)))) for channel, catLLRng in GoodOSLeptons.items())



        for channel, (TwoLeptons, catSel) in categories.items():
        
            selections_for_cutflowreport.append(catSel)
            
            plots.append(Plot.make1D(f"{channel}_mll", op.invariant_mass(TwoLeptons[0].p4, TwoLeptons[1].p4), catSel,
                        EqBin(60 // binScaling, 60., 120.), title= "mll [GeV]",
                        plotopts=utils.getOpts(channel)))
            

            leptons_plus_jets_selec ={}
            leptons_plus_bjets_selec ={}
            for (jk, jv), (bk,bv) in zip( jetsscenarios.items(), bjetsscenarios.items()): 
                leptons_plus_jets_selec[jk] = catSel.refine("{0}_GenJet_{1}Sel".format(jk, channel), cut=[jv])
                leptons_plus_bjets_selec[bk] =leptons_plus_jets_selec[jk].refine("{0}_GenBJet_{1}Sel".format(bk, channel), cut=[ bv])
                
                selections_for_cutflowreport.append(leptons_plus_jets_selec[jk])
                selections_for_cutflowreport.append(leptons_plus_bjets_selec[bk])


            for jk_scenario, lepplusjets in leptons_plus_jets_selec.items():
                jj_p4 = genCleanedJets[0].p4+genCleanedJets[1].p4
                lljj_p4 = (TwoLeptons[0].p4 +TwoLeptons[1].p4 + jj_p4)
                plots += [ Plot.make1D(f"{channel}_{jk_scenario}_gen{nm}", var, lepplusjets, binning,
                        title=f"GEN {title}", plotopts=utils.getOpts(channel))
                        for nm, (var, binning, title) in {
                        "jjPT" : (jj_p4.Pt() , EqBin(60 // binScaling, 0., 450.), "jj P_{T} [GeV]"),
                        "jjPhi": (jj_p4.Phi(), EqBin(50 // binScaling, -3.1416, 3.1416), "jj #phi"),
                        "jjEta": (jj_p4.Eta(), EqBin(50 // binScaling, -3., 3.), "jj Eta"),
                        "mjj": (jj_p4.M(), EqBin(60 // binScaling, 0., 850.), "M_{jj} [GeV]"),
                        "mlljj": (lljj_p4.M(), EqBin(60 // binScaling, 120., 1000.), "M_{lljj} [GeV]")
                }.items() ]

                idxtotitle = ["leading", "sub-leading"]
                plots += [ Plot.make1D(f"{channel}_{jk_scenario}_jet{ij+1:d}lep{il+1:d}_deltaR",
                            op.deltaR(genCleanedJets[ij].p4, TwoLeptons[il].p4), lepplusjets,
                            EqBin(50, 0., 8.), title=f"#Delta R ({idxtotitle[ij]} jet, {idxtotitle[il]} lepton)",
                            plotopts=utils.getOpts(channel, **{"log-y": False}))
                        for ij,il in product(*repeat(range(2), 2)) ]
                plots += [ Plot.make1D(f"{channel}_{jk_scenario}_{nm[:3]}1{nm[:3]}2_deltaR", 
                            op.deltaR(objs[0].p4, objs[1].p4), lepplusjets, 
                            EqBin(50, 0., 8.), title=f"#Delta R (leading {nm}, sub-leading {nm})",
                            plotopts=utils.getOpts(channel, **{"log-y": False}))
                        for nm,objs in {"lepton": TwoLeptons, "jet": genCleanedJets}.items() ]

                plots += [ Plot.make2D("{0}_{1}_mlljj_vs_mjj".format(channel, jk_scenario),
                            (jj_p4.M(), lljj_p4.M()), lepplusjets, 
                            (EqBin(60 // binScaling, 0., 1000.), EqBin(60 // binScaling, 120., 1000.)), 
                            title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(channel)) ]
            
                eqBin_pt = EqBin(60 // binScaling, 0., 650.)
                maxJet = ( 3 if 'at_least_' in jk_scenario else(2))
                
                for i in range(2):
                    plots += [ Plot.make1D(f"{channel}_{jk_scenario}_GenJet{i+1}_{nm}",
                            jVar(genCleanedJets[i]), lepplusjets, binning, title=f"{utils.getCounter(i+1)} GenJet {title}",
                            plotopts=utils.getOpts(channel))
                        for nm, (jVar, binning, title) in {
                        "pT" : (lambda j : j.pt, eqBin_pt, "p_{T} [GeV]"),
                        "eta": (lambda j : j.eta, EqBin(50 // binScaling, -2.4, 2.4), "eta"),
                        "phi": (lambda j : j.phi, EqBin(50 // binScaling, -3.1416, 3.1416), "#phi")
                    }.items() ]

            bb_p4 = genBJets[0].p4+genBJets[1].p4
            llbb_p4 = (TwoLeptons[0].p4 +TwoLeptons[1].p4 + bb_p4)
            
            for bk_scenario, lepplusbjets in leptons_plus_bjets_selec.items():
                plots += [ Plot.make1D(f"{channel}_{bk_scenario}_gen{nm}", var, lepplusbjets, binning,
                        title=f"GEN {title}", plotopts=utils.getOpts(channel))
                        for nm, (var, binning, title) in {
                        "bbPT" : (bb_p4.Pt() , EqBin(60 // binScaling, 0., 450.), "bb P_{T} [GeV]"),
                        "bbPhi": (bb_p4.Phi(), EqBin(50 // binScaling, -3.1416, 3.1416), "bb #phi"),
                        "bbEta": (bb_p4.Eta(), EqBin(50 // binScaling, -3., 3.), "bb Eta"),
                        "mbb": (bb_p4.M(), EqBin(60 // binScaling, 0., 850.), "M_{bb} [GeV]"),
                        "mllbb": (lljj_p4.M(), EqBin(60 // binScaling, 120., 1000.), "M_{llbb} [GeV]")
                }.items() ]
        
                maxBJet = ( 3 if 'at_least_' in bk_scenario else(2))
                for i in range(2):
                    plots += [ Plot.make1D(f"{channel}_{bk_scenario}_GenBJet{i+1}_{nm}",
                            jVar(genBJets[i]), lepplusbjets, binning, title=f"{utils.getCounter(i+1)} GenBJet {title}",
                            plotopts=utils.getOpts(channel))
                        for nm, (jVar, binning, title) in {
                        #"pT" : (lambda j : j.pt, eqBin_pt, "p_{T} [GeV]"),
                        "eta": (lambda j : j.eta, EqBin(50 // binScaling, -2.4, 2.4), "eta"),
                        "phi": (lambda j : j.phi, EqBin(50 // binScaling, -3.1416, 3.1416), "#phi")
                    }.items() ]
               

           # Gen1stBJet_pT = Plot.make1D(f"{channel}_at_least_3bjets_GenBJet1_pT",
           #                         genBJets[0].pt, leptons_plus_bjets_selec['at_least_3bjets'], eqBin_pt, title=f"{utils.getCounter(1)} GenBJet PT",
           #                         plotopts=utils.getOpts(channel))
           # Gen2ndBJet_pT = Plot.make1D(f"{channel}_at_least_3bjets_GenBJet2_pT",
           #                         genBJets[1].pt, leptons_plus_bjets_selec['at_least_3bjets'], eqBin_pt, title=f"{utils.getCounter(2)} GenBJet PT",
           #                         plotopts=utils.getOpts(channel))
           # Gen3rdBJet_pT = Plot.make1D(f"{channel}_at_least_3bjets_GenBJet3_pT",
           #                         genBJets[2].pt, leptons_plus_bjets_selec['at_least_3bjets'], eqBin_pt, title=f"{utils.getCounter(3)} GenBJet PT",
           #                         plotopts=utils.getOpts(channel))
           # plotsToSum[(channel, "1st Leading GenBJet")].append(Gen1stBJet_pT)
           # plotsToSum[(channel, "2nd Leading GenBJet")].append(Gen2ndBJet_pT)
           # plotsToSum[(channel, "3rd Leading GenBJet")].append(Gen3rdBJet_pT)
           # plots += [ Gen1stBJet_pT, Gen2ndBJet_pT, Gen3rdBJet_pT ]

        #for pkey, t2plots in plotsToSum.items():
        #    channel = pkey
        #    if 'muel' in channel or 'elmu' in channel:
        #        plots.append(SummedPlot(f"1st3_leadingGenBjets_2lOSOF", t2plots))
        #    else:
        #        plots.append(SummedPlot(f"1st3_leadingGenBjets_2lOSSF", t2plots))

        plots.append(CutFlowReport("Yields", selections_for_cutflowreport))
        return plots

    def postProcess(self, taskList, config=None, workdir=None, resultsdir=None):
        # run plotIt as defined in HistogramsModule - this will also ensure that self.plotList is present
        super(NanoGenHtoZAPlotter, self).postProcess(taskList, config, workdir, resultsdir)

        from bamboo.plots import CutFlowReport, DerivedPlot
        import bambooToOls
        import json

        plotList_cutflowreport = [ ap for ap in self.plotList if isinstance(ap, CutFlowReport) ]
        bambooToOls.SaveCutFlowReports(config, plotList_cutflowreport, resultsdir, self.readCounters)
