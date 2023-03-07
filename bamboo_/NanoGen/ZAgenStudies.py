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
        
        self.doProcess = self.args.process
    def addArgs(self, parser):
        super(NanoGenHtoZAPlotter, self).addArgs(parser)
        parser.add_argument("-p", "--process", type=str, choices=['ggH', 'bbH', 'both'], default='both', help="handle both process in the yml sepertaly if needed")
        parser.add_argument("--backend", type=str, default="dataframe", help="Backend to use, 'dataframe' (default) or 'lazy'")

    def prepareTree(self, tree, sample=None, sampleCfg=None):
        tree,noSel,be,lumiArgs = super(NanoGenHtoZAPlotter, self).prepareTree(tree, sample=sample, sampleCfg=sampleCfg, description=nanoGenDescription)
        if self.isMC(sample):
            noSel = noSel.refine("mcWeight", weight=tree.genWeight)
        return tree,noSel,be,lumiArgs

    def definePlots(self, t, noSel, sample=None, sampleCfg=None):
        plots = []
        selections_for_cutflowreport = []
        binScaling=1
        isbbH = False
        isggH = False
        if "_bbH4F_" in sample : isbbH = True
        if "_ggH_" in sample: isggH = True
        plotsToSum = defaultdict(list)
        selections_for_cutflowreport.append(noSel)
       

        bTagWorkingPoints = {
                "DeepCSV":{ # era: (loose, medium, tight)
                            "2016":(0.2217, 0.6321, 0.8953),  
                            "2017":(0.1355, 0.4506, 0.7738), 
                            "2018":(0.1208, 0.4168,  0.7665) 
                          },
                "btagDeepFlavB":{
                            "2016":(0.0614, 0.3093, 0.7221), 
                            "2017":(0.0532, 0.3040, 0.7476), 
                            "2018":(0.0490, 0.2783, 0.7100) 
                          }
                }

        bTagWP_idx = "1" # medium WP
        def isTagB(jet):
            return (jet.btagDeepFlavB >= bTagWorkingPoints["btagDeepFlavB"]["2018"][bTagWP_idx])
        def isTagL(jet):
            return op.NOT(isTagB(jet))
        def isTrueBeauty(jet):
            return (jet.hadronFlavour == 5)
        def isTrueLight(jet):
            return op.NOT(isTrueBeauty(jet))
        def matchJetToGenJet(jet, genJet, nMatchGenJet):
            return op.AND(jet.genJet.idx >= 0, nMatchGenJet > 0, jet.genJet == genJet, op.deltaR(jet.p4, jet.genJet.p4) < match_jet_genJet_DR)
        def mkPlt(*args, **kwargs):
            plots.append(Plot.make1D(*args, **kwargs))


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

        doPlot_fromGenPart          = True
        doPlot_fromLHEPart          = False
        doPlot_GenratorVars         = False
        doPlot_Leptonsdistributions = True
        doPlot_GenJetsPlot          = True
        doPlot_LeptonsPlusGenJets   = True
        doPlot_GenBJets             = True
        doPlot_LeptonsPLusGenBJets  = True
        doPlot_deltaR_CR            = False  # Control Region 
        doPlot_deltaR_SR            = False  # Signal Region 
        doPlot_ForwardBJets         = False
        doGen_Matching              = False
        doPlot_MET                  = False
        ################################################################################################
        # IMPORTANT FLAGG 
        doSelect_fromHardprocess    = False 
        suffix = ( 'from_Hardprocess' if doSelect_fromHardprocess else(''))
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
            sorted_genbs =  op.select(genbs, lambda b: -b.pt )
            plots += [ Plot.make1D('bs_statusflags_map', op.map(sorted_genbs, lambda jb: jb.statusFlags), noSel, EqBin(1000 // binScaling, 0., 30000.), title="genBjets status Flags")]
            
            h1_fromGenPart = op.select(t.GenPart,lambda obj: obj.pdgId == 25 )
            h2_fromGenPart = op.select(t.GenPart,lambda obj: obj.pdgId == 35 )
            h3_fromGenPart = op.select(t.GenPart,lambda obj: obj.pdgId == 36 )
            z_fromGenPart  = op.select(t.GenPart,lambda obj: obj.pdgId == 23)
            gamma_fromGenPart  = op.select(t.GenPart,lambda obj: obj.pdgId == 22)
            
            for obj, genPart in {
                                 #"h1_fromGenPart": op.sort(h1_fromGenPart, lambda j : -j.pt),
                                 "h2_fromGenPart": op.sort(h2_fromGenPart, lambda j : -j.pt), 
                                 "h3_fromGenPart": op.sort(h3_fromGenPart,  lambda j : -j.pt),
                                 "z_fromGenPart" : op.sort(z_fromGenPart, lambda j : -j.pt),
                                 "gamma_fromGenPart" : op.sort(gamma_fromGenPart, lambda j : -j.pt), 
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
    
            for flag in ["IsFirstCopy", "IsHardProcess", "FromHardProcess"]:
                genB= op.select(t.GenPart, lambda j :  op.AND( op.abs(j.pdgId)==5, j.statusFlags & 2**GEN_FLAGS[flag], j.parent.idx >= 0))
                genB_notfromA=op.select(t.GenPart, lambda j :  op.AND( op.abs(j.pdgId)==5, j.statusFlags & 2**GEN_FLAGS[flag], j.parent.idx >= 0, op.NOT(j.genPartMother.pdgId ==36)))
                
                twogenBs =noSel.refine("{0}_GenBJet_Sel".format(flag), cut=[op.rng_len(genB) > 1]) 
                twogenBs_notfromA =noSel.refine("{0}_GenBJet_notfromh3_Sel".format(flag), cut=[op.rng_len(genB_notfromA) > 1]) 
                
                plots.append(Plot.make1D(f"Nbr_{flag}_Bhadrons", op.rng_len(genB), noSel, EqBin(10, 0., 10.), title=f"Nbr {flag} B-hadrons"))
                plots += [ Plot.make1D(f'Mbb_{flag}_fromGenPart', (genB[0].p4 + genB[1].p4).M(), twogenBs, EqBin(50 // binScaling, 0., 800.), title=f"GenPart {flag} Mbb [GeV]")]
                plots += [ Plot.make1D(f'Mbb_{flag}_fromGenPart_notfromA', (genB[0].p4 + genB[1].p4).M(), twogenBs, EqBin(50 // binScaling, 0., 800.), title=f"GenPart Mbb {flag} NotFromADecay [GeV]")]
                plots += [ Plot.make1D(f'Pt_{flag}_fromGenPart_notfromA', (genB[0].p4 + genB[1].p4).Pt(), twogenBs, EqBin(50 // binScaling, 0., 800.), title=f"GenPart pT(bb) {flag} NotFromADecay [GeV]")]
                plots += [ Plot.make1D(f'Eta_{flag}_fromGenPart_notfromA', (genB[0].p4 + genB[1].p4).Eta(), twogenBs, EqBin(40, -2.5, 2.5), title=f"GenPart #eta(bb) {flag} NotFromADecay")]
                plots += [ Plot.make1D(f'Phi_{flag}_fromGenPart_notfromA', (genB[0].p4 + genB[1].p4).Phi(), twogenBs, EqBin(40, -3.1416, 3.1416), title=f"GenPart #phi(bb) {flag} NotFromADecay")]
                plots += [ Plot.make1D(f'deltaR_{flag}_fromGenPart_notfromA', op.deltaR(genB[0].p4, genB[1].p4), twogenBs, EqBin(40, 0., 10.), title=f"#Delta R(bb)")]
            
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
        # Leptons 
        sorted_GenDressedLepton = op.sort(t.GenDressedLepton, lambda lep : -lep.pt)
        
        genMuons     = op.select(sorted_GenDressedLepton, lambda l : op.AND( op.abs(l.pdgId) == 13, op.abs(l.eta) < 2.5, l.pt > 10.))
        genElectrons = op.select(sorted_GenDressedLepton, lambda l : op.AND(op.abs(l.pdgId) == 11, op.abs(l.eta) < 2.5, l.pt > 15.))
        genLeptons   = op.select(sorted_GenDressedLepton, lambda l : op.AND(op.OR(op.abs(l.pdgId) == 11, op.abs(l.pdgId) == 13), op.abs(l.eta) < 2.5, l.pt > 10.))
        
        OSSFLeptons = lambda lep1,lep2 : op.AND(lep1.pdgId == -lep2.pdgId)
        LowMass_cut = lambda lep1, lep2: op.invariant_mass(lep1.p4, lep2.p4)>12.
        OSSFLeptons_Zmass = lambda lep1,lep2 : op.AND(lep1.pdgId == -lep2.pdgId, op.in_range(70., op.invariant_mass(lep1.p4, lep2.p4), 120.))

        hasOSLL_cmbRng = lambda cmbRng : op.AND(op.rng_len(cmbRng) > 0, cmbRng[0][0].pt > 25.) 

        # AK4 GEN Jets
        sorted_GenJet= op.sort(t.GenJet, lambda j : -j.pt)
        genJets = op.select(sorted_GenJet, lambda j : op.AND( j.pt > 20., op.abs(j.eta) < 2.5))
        genCleanedJets = op.select(genJets, lambda j: op.AND(
                            op.NOT(op.rng_any(genElectrons, lambda el: op.deltaR(j.p4, el.p4) < 0.4 )),
                            op.NOT(op.rng_any(genMuons, lambda mu: op.deltaR(j.p4, mu.p4) < 0.4 ))
                        ))
        # AK8 GEN Jets
        sorted_GenJetAK8= op.sort(t.GenJetAK8, lambda j : -j.pt)
        genJetsAK8 = op.select(sorted_GenJetAK8, lambda j : op.AND(j.pt > 170., op.abs(j.eta) < 2.5 ))
        genCleanedJetsAK8 = op.select(genJetsAK8, lambda j: op.AND(
                            op.NOT(op.rng_any(genElectrons, lambda el: op.deltaR(j.p4, el.p4) < 0.8 )),
                            op.NOT(op.rng_any(genMuons, lambda mu: op.deltaR(j.p4, mu.p4) < 0.8 ))
                        ))
        
        # b/light GEN Jets 
        genBJets = op.select(genCleanedJets, lambda jet: jet.hadronFlavour == 5)
        genLightJets = op.select(genCleanedJets, lambda jet: jet.hadronFlavour != 5)
        
        genBJetsAK8 = op.select(genCleanedJetsAK8, lambda jet: jet.hadronFlavour == 5)
        genLightJetsAK8 = op.select(genCleanedJetsAK8, lambda jet: jet.hadronFlavour != 5)
       
        ################################################################################################
        # Catagories :
        ################################################################################################
        
        if isggH:
            jetsscenarios  = { "resolved": { 'at_least_2jets'  : op.rng_len(genCleanedJets)    >= 2  },
                               "boosted" : { 'at_least_1fatjet': op.rng_len(genCleanedJetsAK8) >= 1  }
                             }
            bjetsscenarios = { "resolved": { 'at_least_2bjets'  : op.rng_len(genBJets)        == 2  },
                               "boosted" : { 'at_least_1fatbjet': op.rng_len(genBJetsAK8)     == 1  }
                             }
        if isbbH:
            jetsscenarios = { "resolved": { 'at_least_3jets'  : op.rng_len(genCleanedJets)    >= 3  },  
                             #"boosted" : { 'at_least_1fatjet': op.rng_len(genCleanedJetsAK8) >= 1  }
                            }
            bjetsscenarios = { "resolved": { 'at_least_3bjets'  : op.rng_len(genBJets)        >= 3, 
                                             'at_least_2bjets'  : op.rng_len(genBJets)        >= 2,
                                             'at_least_1bjets'  : op.rng_len(genBJets)        >= 1,},
                              #"boosted" : { 'at_least_1fatbjet_and_2resolvedbjets': [ op.rng_len(genBJetsAK8) >= 1, 
                              #                                                        op.rng_len(genBJets)    >= 2 ] } 
                             }
        
        ################################################################################################
        ################################################################################################
        
        mkPlt("ngenBJets", op.rng_len(genBJets), noSel, EqBin(10, 0, 10), title="# AK4 genBJets")
        mkPlt("ngenBJetsAK8", op.rng_len(genBJetsAK8), noSel, EqBin(10, 0, 10), title="# AK8 genBJets")
        
        ################################################################################################
        # Matching studies 
        ################################################################################################
        if doGen_Matching: 
            resID = ( 36 if 'HToZATo2L2B' in sample else (35))
            # mother of bb~ 
            mother_of_bs = ( 'h3' if 'HToZATo2L2B' in sample else ('h2'))
            genParticles = op.select(t.GenPart, lambda p : op.AND(op.OR(p.statusFlags & 2**GEN_FLAGS["IsLastCopy"], p.statusFlags & 2**GEN_FLAGS["FromHardProcess"], p.statusFlags & 2**GEN_FLAGS["IsHardProcess"]), p.parent.idx >= 0))
            
            # b and light flavour quarks that are not from the h3 decay in the case of H > ZA and  /  not from h2 decay in the case of A > ZH
            #b_quark_forward     = op.select(genParticles, lambda jet: op.AND(op.abs(jet.pdgId) == 5, op.NOT(op.rng_any(jet.ancestors, lambda mother: mother.pdgId == resID))))
            b_quark_forward     = op.select(genParticles, lambda jet: op.AND(op.abs(jet.pdgId) == 5, op.NOT(jet.genPartMother.pdgId == resID)))
            light_quark_forward = op.select(genParticles, lambda jet: op.AND(op.NOT(op.abs(jet.pdgId) == 5), op.NOT(op.rng_any(jet.ancestors, lambda mother: mother.pdgId == resID))))
    
            #mkPlt(f"incl_has_2b_forward_notfrom_{resID}", op.AND(b_quark_forward), noSel, EqBin(2, 0, 2))
            #mkPlt(f"incl_has_2light_forward_notfrom_{resID}", op.rng_len(light_quark_forward), noSel, EqBin(5, 0, 5))

            # match genJets with quarks
            for match_q_genJet_DR in [0.4 , 0.5, 0.7 ]:
                matchedGenJets = {}
                nMatchGenJets = {}

                # match genJets with b quarks
                matchedGenJets["b0"] = op.rng_min_element_by(genCleanedJets, lambda j: op.deltaR(b_quark_forward[0].p4, j.p4))
                nMatchGenJets["b0"] = op.rng_count(genCleanedJets, lambda j: op.deltaR(b_quark_forward[0].p4, j.p4) < match_q_genJet_DR)
                matchedGenJets["b1"] = op.rng_min_element_by(genCleanedJets, lambda j: op.deltaR(b_quark_forward[1].p4, j.p4))
                nMatchGenJets["b1"] = op.rng_count(genCleanedJets, lambda j: op.deltaR(b_quark_forward[1].p4, j.p4) < match_q_genJet_DR)
        
                # match genJets with light quarks
                matchedGenJets["l0"] = op.rng_min_element_by(genCleanedJets, lambda j: op.deltaR(light_quark_forward[0].p4, j.p4))
                nMatchGenJets["l0"] = op.rng_count(genCleanedJets, lambda j: op.deltaR(light_quark_forward[0].p4, j.p4) < match_q_genJet_DR)
                matchedGenJets["l1"] = op.rng_min_element_by(genCleanedJets, lambda j: op.deltaR(light_quark_forward[1].p4, j.p4))
                nMatchGenJets["l1"] = op.rng_count(genCleanedJets, lambda j: op.deltaR(light_quark_forward[1].p4, j.p4) < match_q_genJet_DR)
    
                # all quarks are matched to at least one jet
                match_all = op.AND(*(n > 0 for n in nMatchGenJets.values()))
                # all quarks are matched to at least one jet and the closest jet has the right flavour
                match_all_flav = op.AND(match_all, matchedGenJets["b0"].hadronFlavour == 5, matchedGenJets["b1"].hadronFlavour == 5, matchedGenJets["l0"].hadronFlavour != 5, matchedGenJets["l1"].hadronFlavour != 5)
                # all quarks are matched to a unique jet
                match_all_to_a_unique = op.AND(match_all, *( j1 != j2 for i1,j1 in enumerate(matchedGenJets.values()) for i2,j2 in enumerate(matchedGenJets.values()) if i2 > i1 ))
                # all quarks are matched to a unique jet of the right flavour
                match_all_to_a_unique_flav = op.AND(match_all_to_a_unique, match_all_flav)

                unmatched_genJets = op.select(genCleanedJets, lambda j: op.NOT(op.OR(
                                                                        op.rng_any(b_quark_forward, lambda b: op.deltaR(j.p4, b.p4) < match_q_genJet_DR),
                                                                        op.rng_any(light_quark_forward, lambda l: op.deltaR(j.p4, l.p4) < match_q_genJet_DR))
                                                                    ))
            
                unmatched_genBJets = op.select(unmatched_genJets, lambda j: j.hadronFlavour == 5)
                unmatched_genLightJets = op.select(unmatched_genJets, lambda j: j.hadronFlavour != 5)
                
                
                # unmatched jets
                # match jets to genJets (themselves matched to quarks)
                match_jet_genJet_DR = match_q_genJet_DR
                matchedJetColls = {}
                matchedJets = {}
                nMatchJets = {}
    
                #for q in matchedGenJets.keys():
                #    matchedJetColls[q] = op.select(genCleanedJets, lambda j: matchJetToGenJet(j, matchedGenJets[q], nMatchGenJets[q]))
                #    nMatchJets[q] = op.rng_len(matchedJetColls[q])
                #    matchedJets[q] = matchedJetColls[q][0]

                match_q_genJet_DR_ =f"{match_q_genJet_DR}".replace(".","p")
                
                AtLeast3genBJets = noSel.refine(f"select_atleast3_genbjets_cone{match_q_genJet_DR_}", cut=op.rng_len(genBJets) >= 3)
                AtLeast2MatchedgenBJetsNotFromDecay = AtLeast3genBJets.refine(f"select_atleast3genbjets_including_atleast2matchedbassociated_notfromdecay_cone{match_q_genJet_DR_}", cut=[nMatchGenJets["b0"] > 0, nMatchGenJets["b1"] > 0])
                
                for idx, val in nMatchGenJets.items():
                    plots.append(Plot.make1D(f"nGenMatched_to_{idx}quarks_atleast3_genbjets_sel_cone{match_q_genJet_DR_}", nMatchGenJets[idx], AtLeast3genBJets, EqBin(10, 0., 10.), title=f"Nbr genjet matched to {idx} quark not from {resID} decay"))
                    
                mkPlt(f"nUnmatchedJets_cone{match_q_genJet_DR_}", op.rng_len(unmatched_genJets), AtLeast3genBJets, EqBin(10, 0, 10), title="# unmatched jets")
                mkPlt(f"nUnmatchedBJets_cone{match_q_genJet_DR_}", op.rng_len(unmatched_genBJets), AtLeast3genBJets, EqBin(6, 0, 6), title="# unmatched b jets")
                mkPlt(f"nUnmatchedLightJets_cone{match_q_genJet_DR_}", op.rng_len(unmatched_genLightJets), AtLeast3genBJets, EqBin(10, 0, 10), title="# unmatched light jets")
    
                mkPlt(f"unmatched_genLightJets_pt_cone{match_q_genJet_DR_}", op.map(unmatched_genLightJets, lambda j: j.pt), AtLeast3genBJets, EqBin(40, 20, 300), title="pt of unmatched light jets")
                mkPlt(f"unmatched_genBJets_pt_cone{match_q_genJet_DR_}", op.map(unmatched_genBJets, lambda j: j.pt), AtLeast3genBJets, EqBin(40, 20, 300), title="pt of unmatched b jets")
        
                for selNm , sel in {f"AtLeast3genBJetsSel_cone{match_q_genJet_DR_}": AtLeast3genBJets, 
                                    f"AtLeast2MatchedgenBJetsNotFromDecaySel_cone{match_q_genJet_DR_}": AtLeast2MatchedgenBJetsNotFromDecay,
                                    }.items():

                    plots.append(Plot.make1D(f"bquarks_match_all_{selNm}", match_all, sel, EqBin(10, 0., 10.), title=f"All quarks have a matching genjet"))
                    plots.append(Plot.make1D(f"bquarks_match_all_flav_{selNm}", match_all_flav, sel, EqBin(10, 0., 10.), title=f"All quarks have a matching genjet of right flavour"))
                    plots.append(Plot.make1D(f"bquarks_match_all_to_a_unique_genjet_{selNm}", match_all_to_a_unique, sel, EqBin(10, 0., 10.), title=f"All quarks have a matching genjet, matched to a single-quark"))
                    plots.append(Plot.make1D(f"bquarks_match_all_to_a_unique_genjet_ofRightflavour_{selNm}", match_all_to_a_unique_flav, sel, EqBin(10, 0., 10.), title=f"All quarks have a matching genjet of right-flavour && matched to a single-quark"))

                    plots.append(Plot.make1D(f"matched_genbjet_deltaR_{selNm}", op.deltaR(matchedGenJets["b0"].p4, matchedGenJets["b1"].p4), sel, EqBin(40, 0., 6.), title="matched forward b jet #Delta R(bb)"))
                    plots.append(Plot.make1D(f"matched_genbjet_forawrd_mbb_{selNm}", op.invariant_mass(matchedGenJets["b0"].p4, matchedGenJets["b1"].p4), sel, EqBin(40, 0., 600.), title="matched forward b jet M(bb)"))
                    plots.append(Plot.make1D(f"matched_genbjet_forawrd_pTbb_{selNm}", (matchedGenJets["b0"].p4 + matchedGenJets["b1"].p4).Pt(), sel, EqBin(40, 0., 400.), title="matched forward b jet pT(bb)"))
                    plots.append(Plot.make1D(f"matched_genbjet_forawrd_Etabb_{selNm}", (matchedGenJets["b0"].p4 + matchedGenJets["b1"].p4).Eta(), sel, EqBin(40, -2.5, 2.5), title="matched forward b jet Eta(bb)"))
                    plots.append(Plot.make1D(f"matched_genbjet_forawrd_Phibb_{selNm}", (matchedGenJets["b0"].p4 + matchedGenJets["b1"].p4).Phi(), sel, EqBin( 40, -3.1416, 3.1416), title="matched forward b jet #Phi (bb)"))
                    plots.append(Plot.make1D(f"matched_genbjet_forawrd_DpTbb_{selNm}", op.abs(matchedGenJets["b0"].pt - matchedGenJets["b1"].pt), sel, EqBin(40, 0., 400.), title="matched forward b jet |pt(b1)-pt(b2)|"))
        
                    plots.append(SummedPlot(f"matched_genbjet_notfrom_{mother_of_bs}_hFlavour_{selNm}", [
                            Plot.make1D(f"matched_genbjet_b0_notfrom_{mother_of_bs}_hFlavour_{selNm}", matchedGenJets["b0"].hadronFlavour, sel, EqBin(6, 0, 6)),
                            Plot.make1D(f"matched_genbjet_b1_notfrom_{mother_of_bs}_hFlavour_{selNm}", matchedGenJets["b1"].hadronFlavour, sel, EqBin(6, 0, 6))
                    ], title=f"Hadron flavour of jet matched to b quark not from {mother_of_bs}"))
                    
                    plots.append(SummedPlot(f"matched_light_genjet_notfrom_{mother_of_bs}_hFlavour_{selNm}", [
                            Plot.make1D(f"matched_light_genjet_l0_notfrom_{mother_of_bs}_hFlavour_{selNm}", matchedGenJets["b0"].hadronFlavour, sel, EqBin(6, 0, 6)),
                            Plot.make1D(f"matched_light_genjet_l1_notfrom_{mother_of_bs}_hFlavour_{selNm}", matchedGenJets["b1"].hadronFlavour, sel, EqBin(6, 0, 6))
                    ], title=f"Hadron flavour of genjet matched to light quark not from {mother_of_bs}"))
            
    
            # FIXME WIP
            #unmatched_genjets = op.select(genCleanedJets, lambda j: op.NOT(op.OR(*(matchJetToGenJet(j, matchedGenJets[q], nMatchGenJets[q]) for q in matchedGenJets.keys()))))
            #unmatched_genbJets = op.select(unmatched_genjets, lambda j: isTagB(j))
            #unmatched_genbJets_true = op.select(unmatched_genbJets, lambda j: isTrueBeauty(j))
            #unmatched_light_genJets = op.select(unmatched_genjets, lambda j: isTagL(j))
            #unmatched_light_genJets_true = op.select(unmatched_light_genJets, lambda j: isTrueLight(j))


            #matched_bJets_true = op.select(matched_bJets, lambda j: isTrueBeauty(j))
            #sel_2matched_bJets = noSel.refine("matched_2forwardbjets", op.rng_len(matched_bJets_true) >= 2)
            #for i, suf in zip([0,1], ["b0", "b1"]):
            #    plots += [ Plot.make1D(f"matched_forward_b{suf}jet_{nm}", jVar(matchedGenJets[suf][i]), sel, binning, 
            #                title=f"{utils.getCounter(i+1)} matched forward GenBJet {title}")
            #                for nm, (jVar, binning, title) in {
            #                    "pT" : (lambda bj : bj.pt,  EqBin(60 // binScaling, 0., 650.), "p_{T} [GeV]"),
            #                    "eta": (lambda bj : bj.eta, EqBin(50 // binScaling, -3., 3.), "eta"),
            #                    "phi": (lambda bj : bj.phi, EqBin(50 // binScaling, -3.1416, 3.1416), "#phi")
            #            }.items() ]
        
        ################################################################################################
        ################################################################################################
        
        resolved_Jets_dict = { "nGenJets": genCleanedJets, "nGenBJets" : genBJets, "nGenLightJets": genLightJets}
        boosted_Jets_dict  = { "nGenFatJets": genCleanedJetsAK8, "nGenBFatJets" : genBJetsAK8, "nGenLightFatJets": genLightJetsAK8 }
        
        for dict_ in [resolved_Jets_dict, boosted_Jets_dict]:
            for key, Obs in dict_.items():
                plots.append(Plot.make1D(f"{key}", op.rng_len(Obs), noSel, EqBin(10, 0., 10.), title=f"{key}"))
        
        ################################################################################################
        ################################################################################################
        if doPlot_ForwardBJets and isbbH:
                
            sel = noSel.refine("select_4bjets_including_2b-asscicated", cut=op.rng_len(genBJets) >= 4)
            bb_p4 = (genBJets[2].p4 + genBJets[3].p4)
            for i in range(2,4):
                plots += [ Plot.make1D(f"Forward_GenBJet{i+1}_gen{nm}", jVar(genBJets[i]), sel, binning, 
                            title=f"{utils.getCounter(i+1)} Forward GenBJet {title}")
                            for nm, (jVar, binning, title) in {
                                "pT" : (lambda bj : bj.pt,  EqBin(60 // binScaling, 0., 650.), "p_{T} [GeV]"),
                                "eta": (lambda bj : bj.eta, EqBin(50 // binScaling, -3., 3.), "eta"),
                                "phi": (lambda bj : bj.phi, EqBin(50 // binScaling, -3.1416, 3.1416), "#phi")
                        }.items() ]
            
            plots += [ Plot.make1D(f"Forward_GenBJet_gen{nm}", var, sel, binning,
                            title=f"Forward GEN {title}")
                            for nm, (var, binning, title) in {
                                "bbPT" : (bb_p4.Pt() , EqBin(60 // binScaling, 0., 450.), "bb P_{T} [GeV]"),
                                "bbPhi": (bb_p4.Phi(), EqBin(50 // binScaling, -3.1416, 3.1416), "bb #phi"),
                                "bbEta": (bb_p4.Eta(), EqBin(50 // binScaling, -3., 3.), "bb Eta"),
                                "bbMass": (bb_p4.M(), EqBin(50 // binScaling, 0., 600.), "bb Mass [GeV]"),
                                "bbDeltaR": (op.deltaR(genBJets[2].p4, genBJets[3].p4), EqBin(60 // binScaling, 0., 1.), "bb #DeltaR"),
                        }.items() ]

        ################################################################################################
        if doSelect_fromHardprocess:
            GoodGenParticles = op.select(t.GenPart, lambda p : op.OR(p.statusFlags & 2**GEN_FLAGS["IsHardProcess"], p.statusFlags & 2**GEN_FLAGS["FromHardProcess"], p.parent.idx >= 0 ))
            sorted_GoodGenParticles = op.sort(GoodGenParticles, lambda lep : -lep.pt)
            
            GoodGenElectrons = op.select(sorted_GoodGenParticles, lambda l : op.AND( op.abs(l.pdgId) == 11, op.abs(l.eta) < 2.5, l.pt > 15.))
            GoodGenMuons     = op.select(sorted_GenDressedLepton, lambda l : op.AND( op.abs(l.pdgId) == 13, op.abs(l.eta) < 2.4, l.pt > 10.))
            GoodGenLeptons   = op.select(sorted_GenDressedLepton, lambda l : op.AND( op.abs(l.pdgId) == 13, op.abs(l.eta) < 2.5, l.pt > 10., op.abs(l.pdgId) == 11)) 
            
            GoodOSLeptons = {# "mumu" : op.combine(GoodGenMuons,     N=2, pred=OSSFLeptons_Zmass),
                             # "elel" : op.combine(GoodGenElectrons, N=2, pred=OSSFLeptons_Zmass),
                             # "elmu" : op.combine((GoodGenMuons, GoodGenElectrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), mu.pdgId != -ele.pdgId)),
                               "oslep": op.combine(GoodGenLeptons,   N=2, pred=OSSFLeptons_Zmass),
                            }
            
            TwoGoodOSLeptonsSel = noSel.refine("hasGoodOSLL", cut=op.OR(*( hasOSLL_cmbRng(rng) for rng in GoodOSLeptons.values())))
            categories = dict((channel, (catLLRng[0], TwoGoodOSLeptonsSel.refine("hasGoodOs{0}".format(channel), cut=hasOSLL_cmbRng(catLLRng)))) for channel, catLLRng in GoodOSLeptons.items())
        else:
            OSLeptons = { #"mumu": op.combine(genMuons, N=2, pred= OSSFLeptons_Zmass),
                          #"elel": op.combine(genElectrons, N=2, pred=OSSFLeptons_Zmass),
                          #"elmu":op.combine((genMuons, genElectrons), pred=lambda mu,ele : op.AND(LowMass_cut(mu, ele), mu.pdgId != -ele.pdgId)), 
                          "oslep":op.combine(genLeptons, N=2, pred=OSSFLeptons_Zmass) 
                        }
            
            TwoOSLeptonsSel = noSel.refine("hasOSLL", cut=op.OR(*( hasOSLL_cmbRng(rng) for rng in OSLeptons.values())))
            categories = dict((channel, (catLLRng[0], TwoOSLeptonsSel.refine("hasOs{0}".format(channel), cut=hasOSLL_cmbRng(catLLRng)))) for channel, catLLRng in OSLeptons.items())
        
        ################################################################################################
        ################################################################################################

        for channel, (TwoLeptons, catSel) in categories.items():
        
            selections_for_cutflowreport.append(catSel)
            if doPlot_Leptonsdistributions:
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
                
                for bk,bv in bjetsscenarios[regime].items():
                    selections_for_cutflowreport.append(catSel.refine("{0}_GenBJet_{1}Sel_{2}_fromIncluSel".format(bk, channel, regime), cut=[bv]))
                    
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
                                title=f"RECO {title}", plotopts=utils.getOpts(channel))
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
                        
                    if doPlot_deltaR_CR:
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
                                    title=f"RECO {title}", plotopts=utils.getOpts(channel))
                                for nm, (var, binning, title) in {
                                "bbPT" : (bb_p4.Pt() , EqBin(60 // binScaling, 0., 450.), "bb P_{T} [GeV]"),
                                "bbPhi": (bb_p4.Phi(), EqBin(50 // binScaling, -3.1416, 3.1416), "bb #phi"),
                                "bbEta": (bb_p4.Eta(), EqBin(50 // binScaling, -3., 3.), "bb Eta"),
                                "mbb": (bb_p4.M(), EqBin(60 // binScaling, 0., 1300.), "M_{bb} [GeV]"),
                                "mllbb": (llbb_p4.M(), EqBin(60 // binScaling, 120., 1300.), "M_{llbb} [GeV]")
                            }.items() ]
                        plots += [ Plot.make2D("{0}_{1}_{2}_genmllbb_vs_genmbb".format(channel, regime, bk_scenario),
                                    (bb_p4.M(), llbb_p4.M()), lepplusbjets,
                                    (EqBin(60 // binScaling, 0., 1000.), EqBin(60 // binScaling, 0., 1000.)),
                                    title="mllbb vs mbb invariant mass [Gev]", plotopts=utils.getOpts(channel)) ]
        
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
        ################################################################################################
        ################################################################################################
                    
                    if doPlot_deltaR_SR:
                        rng = (2 if regime =="resolved" else(1))
                        idxtotitle = ["leading", "sub-leading", "3rd"]
                        plots += [ Plot.make1D(f"{channel}_{regime}_{bk_scenario}_bjet{ij+1:d}lep{il+1:d}_deltaR",
                                        op.deltaR(gen_BJets[ij].p4, TwoLeptons[il].p4), lepplusbjets,
                                        EqBin(50, 0., 8.), title=f"#Delta R ({idxtotitle[ij]} bjet, {idxtotitle[il]} lepton)",
                                        plotopts=utils.getOpts(channel, **{"log-y": False}))
                                    for ij,il in product(*repeat(range(rng), 2)) ]
                        plots += [ Plot.make1D(f"{channel}_{regime}_{bk_scenario}_{nm[:3]}1{nm[:3]}2_deltaR", 
                                        op.deltaR(objs[0].p4, objs[1].p4), lepplusbjets, 
                                        EqBin(50, 0., 8.), title=f"#Delta R (leading {nm}, sub-leading {nm})",
                                        plotopts=utils.getOpts(channel, **{"log-y": False}))
                                    for nm,objs in {"lepton": TwoLeptons, "jet": gen_BJets}.items() ]
                    
        
                    if doPlot_MET:
                        from bamboo.analysisutils import forceDefine
                        #forceDefine(getattr(t, "GenMET").calcProd, TwoOSLeptonsSel)
                        for flag, met in {"GenMET": t.GenMET }.items():
                            plots.append(Plot.make1D(f"{channel}_{regime}_{bk_scenario}_{flag}_pt", met.pt, lepplusbjets,
                                        EqBin(60 // binScaling, 0., 600.), title="MET p_{T} [GeV]",
                                        plotopts=utils.getOpts(channel, **{"log-y": False})))
                            plots.append(Plot.make1D(f"{channel}_{regime}_{suffix}_{flag}_phi", met.p4.Phi(), lepplusbjets,
                                        EqBin(60 // binScaling, -3.1416, 3.1416), title="MET #phi",
                                        plotopts=utils.getOpts(channel, **{"log-y": False})))

                            for i in range(2):
                                plots.append(Plot.make1D(f"{channel}_{regime}_{bk_scenario}_{flag}_lep{i+1}_deltaPhi",
                                        op.Phi_mpi_pi(TwoLeptons[i].phi - met.phi), lepplusbjets, EqBin(60 // binScaling, -3.1416, 3.1416),
                                        title="#Delta #phi (lepton, MET)", plotopts=utils.getOpts(channel, **{"log-y": False})))

                                MT = op.sqrt( 2. * met.pt * TwoLeptons[i].p4.Pt() * (1. - op.cos(op.Phi_mpi_pi(met.phi - TwoLeptons[i].p4.Phi()))) )
                                plots.append(Plot.make1D(f"{channel}_{regime}_{bk_scenario}_{flag}_MT_lep{i+1}", MT, lepplusbjets,
                                        EqBin(60 // binScaling, 0., 600.), title="Lepton M_{T} [GeV]",
                                        plotopts=utils.getOpts(channel, **{"log-y": False})))


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
