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
from itertools import product, repeat

from bamboo.treedecorators import NanoAODDescription
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
                            "legend-columns"   : 2,
                            "normalized"       : True # normalize to 1 
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

        doPlot_fromGenPart = True
        doPlot_fromLHEPart = False
        doPlot_GenratorVars = False
        doPlot_Leptonsdistributions = True
        doPlot_GenJetsPlot = True
        doPlot_LeptonsPlusGenJets = True
        doPlot_deltaR_betweenLepAndGenJets= False
        doPlot_GenBJets = True
        doPlot_LeptonsPLusGenBJets = True
        
        select_fromHardprocess =False
        suffix = ( 'from_Hardprocess' if select_fromHardprocess else(''))
        ################################################################################################
        ################################################################################################
        if doPlot_fromLHEPart:
            # Not stored in the nanogen  !
            #h2_fromLHEPart = op.select(t.LHEPart,lambda obj: obj.pdgId == 35 )
            #h3_fromLHEPart = op.select(t.LHEPart,lambda obj: obj.pdgId == 36 )
            #z_fromLHEPart = op.select(t.LHEPart,lambda obj: obj.pdgId == 23 )
            #gamma_fromLHEPart  = op.select(t.LHEPart,lambda obj: obj.pdgId == 22)
        
            plots += [ Plot.make1D('LHEPartmap_pdgIDs', op.map(t.LHEPart, lambda p : p.pdgId), noSel, EqBin(100, -50., 50.), title="LHEPart PdgID")]
        
        ################################################################################################
        ################################################################################################
        if doPlot_fromGenPart:
            # mother_of_h2 = op.select(h2_fromGenPart, lambda p : op.AND(p.genPartMother, p.genPartMother.isValid))
            # mother_of_h3 = op.select(h3_fromGenPart, lambda p : op.AND(p.genPartMother, p.genPartMother.isValid))
            # mother_of_z = op.select(z_fromGenPart, lambda p : op.AND(p.genPartMother, p.genPartMother.isValid))
            
            plots += [ Plot.make1D('GenPartmap_pdgIDs', op.map(t.GenPart, lambda p : p.pdgId), noSel, EqBin(100, -50., 50.), title="GenPart PdgID")]
            
            genbs = op.select(t.GenPart, lambda j : op.abs(j.pdgId)==5 )
            plots += [ Plot.make1D('bs_statusflags_map', op.map(genbs, lambda jb: jb.statusFlags), noSel, EqBin(1000 // binScaling, 0., 30000.), title="genBjets status Flags")]
            
            h2_fromGenPart = op.select(t.GenPart,lambda obj: obj.pdgId == 35 )
            h3_fromGenPart = op.select(t.GenPart,lambda obj: obj.pdgId == 36 )
            z_fromGenPart  = op.select(t.GenPart,lambda obj: obj.pdgId == 23)
            gamma_fromGenPart  = op.select(t.GenPart,lambda obj: obj.pdgId == 22)
            
            for obj, genPart in {"h2_fromGenPart":h2_fromGenPart, 
                                 "h3_fromGenPart": h3_fromGenPart, 
                                 "z_fromGenPart" : z_fromGenPart, 
                                 "gamma_fromGenPart" : gamma_fromGenPart, 
                                }.items():
                plots.append(Plot.make1D(f"Nbr_{suffix}_{obj}", op.rng_len(genPart), noSel, EqBin(10, 0., 10.), title=f"Nbr {obj}"))
                plots.append(Plot.make1D(f"{obj}_mother_pdgids", op.map(genPart, lambda p: op.switch(p.genPartMother.isValid, p.genPartMother.pdgId, op.c_int(-1))), noSel, EqBin(100, -50., 50.), title=f"pdgid of {obj} mother particle"))
                onegenPart_atleast = noSel.refine(f'remove_empty_{obj}_events', cut=(op.rng_len(genPart) > 0))
                plots += [ Plot.make1D(f"{obj}_{nm}", var, onegenPart_atleast, binning,
                        title=f"GEN {obj} {title}")
                        for nm, (var, binning, title) in {
                            "PT" : (genPart[0].p4.Pt() , EqBin(60 // binScaling, 0., 450.), "P_{T} [GeV]"),
                            "Phi": (genPart[0].p4.Phi(), EqBin(50 // binScaling, -3.1416, 3.1416), "#phi"),
                            "Eta": (genPart[0].p4.Eta(), EqBin(50 // binScaling, -3., 3.), "Eta"),
                            "Mass": (genPart[0].p4.M(), EqBin(60//binScaling, 0., 1200.), "Mass [GeV]"),
                    }.items() ]

            mRanges = {
                "H": EqBin(50, 0., 1300.),
                "A": EqBin(50, 0., 1300.),
                "Z": EqBin(50, 60., 120.),
                #"Z": EqBin(50, 0., 650.),
                #"gamma": EqBin(50,  0., 650.)
                }
    
            for resNm, resID in {"H": 35, "A": 36, "Z": 23}.items():#, "gamma": 22}.items():
                res_children = op.select(t.GenPart, lambda p : op.AND(p.genPartMother.pdgId == resID, p.pdgId != resID))
                plots += [
                        Plot.make1D(f"{resNm}_nChildren", op.rng_len(res_children), noSel, EqBin(10, 0., 10.), title=f"Number of children for {resNm}"),
                        Plot.make1D(f"{resNm}_child_pdgids", op.map(res_children, lambda gp : gp.pdgId), noSel, EqBin(100, -50., 50.), title=f"{resNm} children pdgid"), ]
                has2Ch = noSel.refine(f"{resNm}Has2Children", cut=(op.rng_len(res_children) > 0))
                plots.append(Plot.make1D(f"{resNm}_m2ChME", (res_children[0].p4+res_children[1].p4).M(), has2Ch, mRanges[resNm], title=f"{resNm} first two children invariant mass"))
    
            #for flag in ["IsFirstCopy", "IsHardProcess", "FromHardProcess"]:
            #    genB= op.select(t.GenPart, lambda j :  op.AND( op.abs(j.pdgId)==5, j.statusFlags & 2**GEN_FLAGS[flag], j.parent.idx >= 0))
            #    twogenBs =noSel.refine("{0}_GenBJet_Sel".format(flag), cut=[op.rng_len(genB) > 1]) 
            #    plots.append(Plot.make1D(f"Nbr_{flag}_Bhadrons", op.rng_len(genB), noSel, EqBin(10, 0., 10.), title=f"Nbr {flag} B-hadrons"))
            #    plots += [ Plot.make1D(f'Mbb_{flag}_fromGenPart', (genB[0].p4 + genB[1].p4).M(), twogenBs, EqBin(50 // binScaling, 0., 800.), title=f"GenPart {flag} Mbb [GeV]")]
            
        ################################################################################################
        ################################################################################################
        if doPlot_GenratorVars:
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
        
        ################################################################################################
        ################################################################################################
        sorted_GenDressedLepton = op.sort(t.GenDressedLepton, lambda lep : -lep.pt)
        genMuons = op.select(sorted_GenDressedLepton, lambda l : op.AND( op.abs(l.pdgId) == 13, op.abs(l.eta) < 2.4, l.pt > 10.))
        genElectrons = op.select(sorted_GenDressedLepton, lambda l : op.AND(op.abs(l.pdgId) == 11, op.abs(l.eta) < 2.5, l.pt > 15.))
        genLeptons = op.select(sorted_GenDressedLepton, lambda l : op.AND(op.OR(op.abs(l.pdgId) == 11, op.abs(l.pdgId) == 13), op.abs(l.eta) < 2.4, l.pt > 10.))

        sorted_GenJet= op.sort(t.GenJet, lambda j : -j.pt)
        genJets = op.select(sorted_GenJet, lambda j : op.AND( j.pt > 20., op.abs(j.eta) < 2.4))
        genCleanedJets = op.select(genJets, lambda j: op.AND(
                            op.NOT(op.rng_any(genElectrons, lambda el: op.deltaR(j.p4, el.p4) < 0.4 )),
                            op.NOT(op.rng_any(genMuons, lambda mu: op.deltaR(j.p4, mu.p4) < 0.4 ))
                        ))

        sorted_GenJetAK8= op.sort(t.GenJetAK8, lambda j : -j.pt)
        genJetsAK8 = op.select(sorted_GenJetAK8, lambda j : op.AND(j.pt > 200., op.abs(j.eta) >2.4))
        genCleanedJetsAK8 = op.select(genJetsAK8, lambda j: op.AND(
                            op.NOT(op.rng_any(genElectrons, lambda el: op.deltaR(j.p4, el.p4) < 0.8 )),
                            op.NOT(op.rng_any(genMuons, lambda mu: op.deltaR(j.p4, mu.p4) < 0.8 ))
                        ))
        resID = ( 35 if 'HToZATo2L2B' in sample else (36))
        genBJets = op.select(genCleanedJets, lambda jet: jet.hadronFlavour == 5)#, jet.genPartMother.pdgId == resID, jet.pdgId != resID) )
        genLightJets = op.select(genCleanedJets, lambda jet: jet.hadronFlavour != 5)#, jet.genPartMother.pdgId == resID, jet.pdgId != resID))
        
        genBJetsAK8 = op.select(genCleanedJetsAK8, lambda jet: jet.hadronFlavour == 5)#, jet.genPartMother.pdgId == resID, jet.pdgId != resID))
        genLightJetsAK8 = op.select(genCleanedJetsAK8, lambda jet: jet.hadronFlavour != 5)#, jet.genPartMother.pdgId == resID, jet.pdgId != resID))


        resolved_Jets_dict = { "nGenJets": genCleanedJets,
                               "nGenBJets" : genBJets,
                               "nGenLightJets": genLightJets}
        boosted_Jets_dict = { "nGenFatJets": genCleanedJetsAK8,
                              "nGenBFatJets" : genBJetsAK8,
                              "nGenLightFatJets": genLightJetsAK8}
        ################################################################################################
        ################################################################################################
        for dict_ in [resolved_Jets_dict, boosted_Jets_dict]:
            for key, Obs in dict_.items():
                plots.append(Plot.make1D(f"{key}", op.rng_len(Obs), noSel,
                        EqBin(10, 0., 10.), title=f"{key}"))

        ################################################################################################
        ################################################################################################
        OSSFLeptons_Zmass = lambda lep1,lep2 : op.AND(lep1.pdgId == -lep2.pdgId)#, op.in_range(70., op.invariant_mass(lep1.p4, lep2.p4), 120.))
        OSSFLeptons = lambda lep1,lep2 : op.AND(lep1.pdgId == -lep2.pdgId)
        LowMass_cut = lambda lep1, lep2: op.invariant_mass(lep1.p4, lep2.p4)>12.

        hasOSLL_cmbRng = lambda cmbRng : op.AND(op.rng_len(cmbRng) > 0, cmbRng[0][0].pt > 25.) 
        OSLeptons = { "mumu": op.combine(genMuons, N=2, pred= OSSFLeptons_Zmass),
                      "elel": op.combine(genElectrons, N=2, pred=OSSFLeptons_Zmass),
                      #"elmu":op.combine((genMuons, genElectrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), mu.pdgId != -ele.pdgId)), 
                      "oslep":op.combine(genLeptons, N=2) 
                    }

        TwoOSLeptonsSel = noSel.refine("hasOSLL", cut=op.OR(*( hasOSLL_cmbRng(rng) for rng in OSLeptons.values())))
        categories = dict((channel, (catLLRng[0], TwoOSLeptonsSel.refine("hasOs{0}".format(channel), cut=hasOSLL_cmbRng(catLLRng)))) for channel, catLLRng in OSLeptons.items())
        
        jetsscenarios = { "resolved": { 'at_least_2jets': op.rng_len(genCleanedJets) > 1,
                                        #'exactly_2jets' : op.rng_len(genCleanedJets) == 2 
                                        },
                         #"boosted": { 'at_least_1fatjet': op.rng_len(genCleanedJetsAK8) > 0} 
                         }
        
        bjetsscenarios = { "resolved": { 'at_least_2bjets': op.rng_len(genBJets) > 1,
                                         #'exactly_2bjets' : op.rng_len(genBJets) == 2 
                                         },
                           #"boosted": { 'at_least_1fatbjet': op.rng_len(genBJetsAK8) > 1} 
                         }
        
        #if "_bbH4F_" in sample :
        #    jetsscenarios.update( {'at_least_3jets': op.rng_len(genCleanedJets) > 2})
        #    bjetsscenarios.update( {'at_least_3bjets': op.rng_len(genBJets) > 2})

        ################################################################################################
        ################################################################################################
        if select_fromHardprocess:
            GoodGenParticles = op.select(t.GenPart, lambda p : op.OR(p.statusFlags & 2**GEN_FLAGS["IsHardProcess"], p.statusFlags & 2**GEN_FLAGS["FromHardProcess"], p.parent.idx >= 0 ))
            sorted_GoodGenParticles = op.sort(GoodGenParticles, lambda lep : -lep.pt)
            GoodGenElectrons = op.select(sorted_GoodGenParticles, lambda l : op.AND(op.abs(l.pdgId) == 11, op.abs(l.eta) < 2.5, l.pt > 15.))
            GoodGenMuons= op.select(sorted_GenDressedLepton, lambda l : op.AND( op.abs(l.pdgId) == 13, op.abs(l.eta) < 2.4, l.pt > 10.))
            
            
            GoodOSLeptons = { "mumu": op.combine(GoodGenMuons, N=2, pred= OSSFLeptons_Zmass),
                              "elel": op.combine(GoodGenElectrons, N=2, pred=OSSFLeptons_Zmass),
                            # "elmu": op.combine((GoodGenMuons, GoodGenElectrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), mu.pdgId != -ele.pdgId)),
                            }
            
            TwoGoodOSLeptonsSel = noSel.refine("hasGoodOSLL", cut=op.OR(*( hasOSLL_cmbRng(rng) for rng in GoodOSLeptons.values())))
            categories = dict((channel, (catLLRng[0], TwoGoodOSLeptonsSel.refine("hasGoodOs{0}".format(channel), cut=hasOSLL_cmbRng(catLLRng)))) for channel, catLLRng in GoodOSLeptons.items())

        ################################################################################################
        ################################################################################################

        for channel, (TwoLeptons, catSel) in categories.items():
        
            selections_for_cutflowreport.append(catSel)
            if doPlot_Leptonsdistributions:# and sample not in ["HToZATo2L2B_200p00_125p00_1p50_ggH_TuneCP5_13TeV_pythia8","AToZHTo2L2B_200p00_125p00_1p50_ggH_TuneCP5_13TeV_pythia8"]:
                for i in range(2):
                    plots.append(Plot.make1D(f"{channel}_lep{i+1}_pt", TwoLeptons[i].pt, catSel,
                                    EqBin(60 // binScaling, 0., 530.), title=f"{utils.getCounter(i+1)} Lepton pT [GeV]" ,
                                    plotopts=utils.getOpts(channel)))
                    plots.append(Plot.make1D(f"{channel}_lep{i+1}_eta", TwoLeptons[i].eta, catSel,
                                    EqBin(50 // binScaling, -2.5, 2.5), title=f"{utils.getCounter(i+1)} Lepton eta",
                                    plotopts=utils.getOpts(channel)))
                    plots.append(Plot.make1D(f"{channel}_lep{i+1}_phi", TwoLeptons[i].phi, catSel,
                                    EqBin(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} Lepton #phi",
                                    plotopts=utils.getOpts(channel))) 
                
                plots.append(Plot.make1D(f"{channel}_llpT", (TwoLeptons[0].p4 + TwoLeptons[1].p4).Pt(), catSel, 
                            EqBin(60, 0., 450.), title= "dilepton P_{T} [GeV]", 
                            plotopts=utils.getOpts(channel)))
                plots.append(Plot.make1D(f"{channel}_llphi", (TwoLeptons[0].p4 + TwoLeptons[1].p4).Phi(), catSel, 
                            EqBin(50 // binScaling, -3.1416, 3.1416), title= "dilepton #phi ", 
                            plotopts=utils.getOpts(channel)))
                plots.append(Plot.make1D(f"{channel}_lleta", (TwoLeptons[0].p4 + TwoLeptons[1].p4).Eta(), catSel, 
                            EqBin(50 // binScaling, -2.5, 2.5), title= "dilepton eta", 
                            plotopts=utils.getOpts(channel)))
                plots.append(Plot.make1D(f"{channel}_mll_2lepselection_mllcut", op.invariant_mass(TwoLeptons[0].p4, TwoLeptons[1].p4), catSel,
                            EqBin(60 // binScaling, 60., 120.), title= "mll [GeV]",
                            plotopts=utils.getOpts(channel)))
            
        ################################################################################################
        ################################################################################################
            for regime in jetsscenarios.keys():
                leptons_plus_jets_selec ={}
                leptons_plus_bjets_selec ={}
                for (jk, jv), (bk,bv) in zip( jetsscenarios[regime].items(), bjetsscenarios[regime].items()): 
                    leptons_plus_jets_selec[jk] = catSel.refine("{0}_GenJet_{1}Sel_{2}".format(jk, channel, regime), cut=[jv])
                    leptons_plus_bjets_selec[bk] =leptons_plus_jets_selec[jk].refine("{0}_GenBJet_{1}Sel_{2}".format(bk, channel, regime), cut=[bv])
                    
                    selections_for_cutflowreport.append(leptons_plus_jets_selec[jk])
                    selections_for_cutflowreport.append(leptons_plus_bjets_selec[bk])
                if regime == "resolved":
                    jj_p4 = genCleanedJets[0].p4+genCleanedJets[1].p4
                    bb_p4 = genBJets[0].p4+genBJets[1].p4
                    gen_Jets = genCleanedJets
                    gen_BJets = genBJets
                else:
                    jj_p4 = genCleanedJetsAK8[0].p4
                    bb_p4 = genBJetsAK8[0].p4
                    gen_Jets = genCleanedJetsAK8
                    gen_BJets = genBJetsAK8

                lljj_p4 = (TwoLeptons[0].p4 +TwoLeptons[1].p4 + jj_p4)
                llbb_p4 = (TwoLeptons[0].p4 +TwoLeptons[1].p4 + bb_p4)

        ################################################################################################
        ################################################################################################
                for jk_scenario, lepplusjets in leptons_plus_jets_selec.items():
                        
                    if doPlot_LeptonsPlusGenJets:
                        plots += [ Plot.make1D(f"{channel}_{regime}_{jk_scenario}_gen{nm}", var, lepplusjets, binning,
                                title=f"GEN {title}", plotopts=utils.getOpts(channel))
                                for nm, (var, binning, title) in {
                                "jjPT" : (jj_p4.Pt() , EqBin(60 // binScaling, 0., 450.), "jj P_{T} [GeV]"),
                                "jjPhi": (jj_p4.Phi(), EqBin(50 // binScaling, -3.1416, 3.1416), "jj #phi"),
                                "jjEta": (jj_p4.Eta(), EqBin(50 // binScaling, -3., 3.), "jj Eta"),
                                "mjj": (jj_p4.M(), EqBin(60 // binScaling, 0., 1300.), "M_{jj} [GeV]"),
                                "mlljj": (lljj_p4.M(), EqBin(60 // binScaling, 120., 1300.), "M_{lljj} [GeV]")
                        }.items() ]
                        plots += [ Plot.make2D("{0}_{1}_{2}_mlljj_vs_mjj".format(channel, regime, jk_scenario),
                                (jj_p4.M(), lljj_p4.M()), lepplusjets, 
                                (EqBin(60 // binScaling, 0., 1000.), EqBin(60 // binScaling, 120., 1000.)), 
                                title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(channel)) ]
        ################################################################################################
        ################################################################################################
                        
                    if doPlot_deltaR_betweenLepAndGenJets:
                        rng = ( 2 if regime =="resolved" else(1))
                        idxtotitle = ["leading", "sub-leading", "3rd"]
                        plots += [ Plot.make1D(f"{channel}_{regime}_{jk_scenario}_jet{ij+1:d}lep{il+1:d}_deltaR",
                                        op.deltaR(gen_Jets[ij].p4, TwoLeptons[il].p4), lepplusjets,
                                        EqBin(50, 0., 8.), title=f"#Delta R ({idxtotitle[ij]} jet, {idxtotitle[il]} lepton)",
                                        plotopts=utils.getOpts(channel, **{"log-y": False}))
                                    for ij,il in product(*repeat(range(rng), 2)) ]
                        plots += [ Plot.make1D(f"{channel}_{regime}_{jk_scenario}_{nm[:3]}1{nm[:3]}2_deltaR", 
                                        op.deltaR(objs[0].p4, objs[1].p4), lepplusjets, 
                                        EqBin(50, 0., 8.), title=f"#Delta R (leading {nm}, sub-leading {nm})",
                                        plotopts=utils.getOpts(channel, **{"log-y": False}))
                                    for nm,objs in {"lepton": TwoLeptons, "jet": gen_Jets}.items() ]
        
        ################################################################################################
        ################################################################################################
                    eqBin_pt = EqBin(60 // binScaling, 0., 650.)
                    maxJet = ( 3 if 'at_least_3' in jk_scenario else(1 if regime=="boosted" else(2)))
                    if doPlot_GenJetsPlot:             
                        for i in range(maxJet):
                            plots += [ Plot.make1D(f"{channel}_{regime}_{jk_scenario}_GenJet{i+1}_{nm}",
                                        jVar(gen_Jets[i]), lepplusjets, binning, title=f"{utils.getCounter(i+1)} GenJet {title}",
                                        plotopts=utils.getOpts(channel))
                                    for nm, (jVar, binning, title) in {
                                    "pT" : (lambda j : j.pt, eqBin_pt, "p_{T} [GeV]"),
                                    "eta": (lambda j : j.eta, EqBin(50 // binScaling, -2.4, 2.4), "eta"),
                                    "phi": (lambda j : j.phi, EqBin(50 // binScaling, -3.1416, 3.1416), "#phi")
                                }.items() ]
    
        ################################################################################################
        ################################################################################################
                for bk_scenario, lepplusbjets in leptons_plus_bjets_selec.items():
                    if doPlot_LeptonsPLusGenBJets:
                        plots += [ Plot.make1D(f"{channel}_{regime}_{bk_scenario}_gen{nm}", var, lepplusbjets, binning,
                                    title=f"GEN {title}", plotopts=utils.getOpts(channel))
                                for nm, (var, binning, title) in {
                                "bbPT" : (bb_p4.Pt() , EqBin(60 // binScaling, 0., 450.), "bb P_{T} [GeV]"),
                                "bbPhi": (bb_p4.Phi(), EqBin(50 // binScaling, -3.1416, 3.1416), "bb #phi"),
                                "bbEta": (bb_p4.Eta(), EqBin(50 // binScaling, -3., 3.), "bb Eta"),
                                "mbb": (bb_p4.M(), EqBin(60 // binScaling, 0., 1300.), "M_{bb} [GeV]"),
                                "mllbb": (llbb_p4.M(), EqBin(60 // binScaling, 120., 1300.), "M_{llbb} [GeV]")
                            }.items() ]
        
        ################################################################################################
        ################################################################################################
                    maxBJet = ( 3 if 'at_least_3' in bk_scenario else(1 if regime=="boosted" else(2)))
                    if doPlot_GenBJets:
                        for i in range(maxBJet):
                            plots += [ Plot.make1D(f"{channel}_{regime}_{bk_scenario}_GenBJet{i+1}_{nm}",
                                    jVar(gen_BJets[i]), lepplusbjets, binning, title=f"{utils.getCounter(i+1)} GenBJet {title}",
                                    plotopts=utils.getOpts(channel))
                                for nm, (jVar, binning, title) in {
                                "pT" : (lambda j : j.pt, eqBin_pt, "p_{T} [GeV]"),
                                "eta": (lambda j : j.eta, EqBin(50 // binScaling, -2.4, 2.4), "eta"),
                                "phi": (lambda j : j.phi, EqBin(50 // binScaling, -3.1416, 3.1416), "#phi")
                            }.items() ]
    
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
