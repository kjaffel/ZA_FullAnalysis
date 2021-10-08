import os
import sys
import argparse
import collections

from bamboo.analysismodules import  NanoAODSkimmerModule
from bamboo.analysisutils import makePileupWeight
from bamboo import treefunctions as op

zabPath = os.path.dirname(__file__)
if zabPath not in sys.path:
    sys.path.append(zabPath)

import utils
from ZAtollbb import NanoHtoZABase, scalesfactorsULegacyLIB

import logging
logger = logging.getLogger("ZA SKIMMER")

from bamboo.root import addIncludePath, loadHeader
addIncludePath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "include"))
loadHeader("BTagEffEvaluator.h")

def value_for_channel(d, channel, return_dilepton):
    """Return a value in neseted dic `d` having a key == channel ."""
    if channel not in d.keys():
        return logger.error(" AhAh ... somthing  went wrong with  your selection !!")
    for key, (leptons, sel) in d.items():
        if key == channel:
            if return_dilepton ==True:
                return leptons
            else:
                return sel

def bJetEnergyRegression(jets):
    return op.map(jets, lambda j : op.construct("ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>", (j.pt*j.bRegCorr, j.eta, j.phi, j.mass*j.bRegCorr)))

class Skimedtree_NanoHtoZA(NanoHtoZABase, NanoAODSkimmerModule):
    def __init__(self, args):
        super(Skimedtree_NanoHtoZA, self).__init__(args)

        self.SetSel = self.args.selections
        self.SetRegion = self.args.regions
        self.SetCat = self.args.categories
        self.SetTagger = self.args.taggers
        self.SetWP = self.args.workingpoints
        self.Setproc = self.args.processes
    
    def addArgs(self, parser):
        super(Skimedtree_NanoHtoZA, self).addArgs(parser)
        parser.add_argument("-sel", "--selections", choices=["noSel", "OsLeptons", "2Lep2Jets", "2Lep2bJets"], default=None, help="set Final Selection")
        parser.add_argument("-reg", "--regions", choices=["boosted", "resolved"], default=None, help="Produce ntuples in Boosted or resolved region")
        parser.add_argument("-cat", "--categories", choices=["ElEl", "MuMu", "ElMu", "MuEl"], default=None, help="Produce ntuples in ElEl or MuMu channel")
        parser.add_argument("-Tag", "--taggers", choices= ["DeepCSV", "DeepFlavour"], default=None, help="Set tagger for b-jet identification")
        parser.add_argument("-wp",  "--workingpoints", default=None, help="Setting Working point is mandatory")
        parser.add_argument("-proc","--processes", choices= ["ggH", "bbH"], default=None, help="processes ggH or bbH")
    
    def defineSkimSelection(self, t, noSel, sample=None, sampleCfg=None):
        from bamboo.root import addIncludePath, loadHeader
        from bamboo.scalefactors import BtagSF

        noSel, puWeightsFile, PUWeight, categories, isDY_reweight, WorkingPoints, BoostedTopologiesWP, legacy_btagging_wpdiscr_cuts, deepBFlavScaleFactor, deepB_AK4ScaleFactor, deepB_AK8ScaleFactor, AK4jets, AK8jets, fatjets_nosubjettinessCut, bjets_resolved, bjets_boosted, CleanJets_fromPileup, electrons, muons, MET, corrMET, PuppiMET, elRecoSF_highpt, elRecoSF_lowpt, isULegacy = self.defineObjects(t, noSel, sample, sampleCfg)
        
        def getIDX(wp = None):
            return (0 if wp=="L" else ( 1 if wp=="M" else 2))
        def getOperatingPoint(wp = None):
            return ("Loose" if wp == 'L' else ("Medium" if wp == 'M' else "Tight"))
        
        
        era = sampleCfg["era"]
        isMC = self.isMC(sample)
        process = "gg_fusion" if self.Setproc =="ggH" else "bb_associatedProduction"
        pass_bTagEventWeight = False

        idx = getIDX(self.SetWP)
        OP  = getOperatingPoint(self.SetWP)
        wp  = self.SetWP
        run2_bTagEventWeight_PerWP = collections.defaultdict(dict)

        if self.SetCat not in categories.keys():
            print ('[Skimedtree_NanoHtoZA]: channel %s not found in categories' % self.SetCat)
            print ('[Skimedtree_NanoHtoZA]: I could only find ** ')
            print (categories.keys())
            sys.exit(0)
        
        if self.SetSel == "2Lep2bJets":
            
            if self.SetRegion == "boosted":
                self.SetTagger = "DeepCSV" # FIXME add later DeepDoubleB 
            else:
                if self.SetTagger not in ["DeepFlavour", "DeepCSV"]:
                    print ('[Skimedtree_NanoHtoZA]: %s Unknown tagger for resolved region' %self.SetTagger)
                    print ('[Skimedtree_NanoHtoZA]:  I could only find **  DeepFlavour, DeepCSV')
                    sys.exit(0)

            if self.SetWP is None:
                print ('[Skimedtree_NanoHtoZA]: WP is MANDATORY ***  ')
                sys.exit(0)
    
            if self.SetWP not in ['L', 'M', 'T']:
                print ('[Skimedtree_NanoHtoZA]: %s not found in WorkingPoints ' % self.SetWP)
                sys.exit(1)
        
        if self.SetRegion == "resolved":
            jets = AK4jets
            suffix = "AK4Jets"
        
        elif self.SetRegion == "boosted":
            jets = AK8jets
            suffix = "AK8Jets"
        
        else:
            raise RuntimeError('[Skimedtree_NanoHtoZA]: %s Unkown args' %self.SetRegion)
        
        logger.info("Start filling the Tree ...")
        logger.info(f"[Skimedtree_NanoHtoZA]: Region= {self.SetRegion}, Channel= {self.SetCat}, Tagger= {self.SetTagger}, WP={self.SetWP}")
        #variables to keep from the input tree
        varsToKeep = {"run": None, "luminosityBlock": None, "event": None}
        
        if isMC: # variation is gone !
            varsToKeep["PU_weight"] = makePileupWeight(puWeightsFile, t.Pileup_nTrueInt, nameHint="puWeight{0}".format("".join(c for c in sample if c.isalnum())))

        #===================================================================================
        #===================================================================================
        if self.SetSel=="noSel":
            FinalSel= noSel
            # Muons && Electrons selections
            for obj, flav in zip ([muons, electrons], ["Muons", "Electrons"]):
                varsToKeep["n%s"    %flav] = op.static_cast("UInt_t",op.rng_len(obj))
                varsToKeep["%s_pt"  %flav] = op.map(obj, lambda lep: lep.pt)
                varsToKeep["%s_eta" %flav] = op.map(obj, lambda lep: lep.eta)
                varsToKeep["%s_phi" %flav] = op.map(obj, lambda lep: lep.phi)
        
            # resolved or boosted 
                ### Jets selections
            varsToKeep["%s_pt"  %suffix] = op.map(jets, lambda j: j.pt)
            varsToKeep["%s_eta" %suffix] = op.map(jets, lambda j: j.eta)
            varsToKeep["%s_phi" %suffix] = op.map(jets, lambda j: j.phi)
            varsToKeep["n%s"    %suffix] = op.static_cast("UInt_t",op.rng_len(jets))    
        
            # MET selections
                # Raw MET 
            RawMET = t.MET if era != "2017" else t.METFixEE2017
            varsToKeep["RawMET_pt"]  = RawMET.pt
            varsToKeep["RawMET_phi"] = RawMET.phi
            varsToKeep["RawMET_eta"] = RawMET.eta
                # xy corr
            varsToKeep["CorrMET_pt"]  = corrMET.pt
            varsToKeep["CorrMET_phi"] = CorrMET.phi
            varsToKeep["CorrMET_eta"] = corrMET.eta
    
        #===================================================================================
        ### Opposite sign leptons , Same Flavour  selection 
        #===================================================================================
        dilepton = value_for_channel(categories, self.SetCat, return_dilepton= True)
    
        leptons_charge = {"l1": dilepton[0].charge, "l2":dilepton[1].charge}
        leptons_pdgId  = {"l1": dilepton[0].pdgId, "l2":dilepton[1].pdgId}
        
        if self.SetSel=="OsLeptons":
            FinalSel= value_for_channel(categories, self.SetCat, return_dilepton= False)
            for i in range(2):
                varsToKeep["lep{0}_pt".format(i)]  = dilepton[i].p4.pt
                varsToKeep["lep{0}_eta".format(i)] = dilepton[i].p4.eta
                varsToKeep["lep{0}_phi".format(i)] = dilepton[i].p4.phi
        
            ll_M   = op.invariant_mass(dilepton[0].p4, dilepton[1].p4)
            varsToKeep["ll_M"]  = ll_M
        
        #===================================================================================
        #===================================================================================
        TwoLeptonsTwoJets_Resolved= value_for_channel(categories, self.SetCat, return_dilepton= False).refine("TwoJet_{0}Sel_resolved".format(self.SetCat), cut=[ op.rng_len(AK4jets) > 1])
        TwoLeptonsOneJet_Boosted = value_for_channel(categories, self.SetCat, return_dilepton= False).refine("OneJet_{0}Sel_boosted".format(self.SetCat), cut=[ op.rng_len(AK8jets) > 0 ])

        lljjSelections = {
                "resolved": TwoLeptonsTwoJets_Resolved,
                "boosted" : TwoLeptonsOneJet_Boosted
                }
        
       # ROOTEffMapsPath = { '2016': "/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/ver.20_10_08/results/summedProcessesForEffmaps/summedProcesses_2016_ratios.root",
       #                     '2017': "/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2017Results/ver.20_10_06/fix_bug_cause_missing_histograms/results/summedProcessesForEffmaps/summedProcesses_2017_ratios.root",
       #                     '2018': "/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2018Results/ver.20_10_06/fix_bug_causing_missingHistograms/results/summedProcessesForEffmaps/summedProcesses_2018_ratios.root"
       #                 }
        ROOTEffMapsPath = { '2016-preVFP' : "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ul2016__btv_effmaps/results/summedProcessesForEffmaps/summedProcesses_2016_ratios.root",     
                            '2016-postVFP': "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ul2016__btv_effmaps/results/summedProcessesForEffmaps/summedProcesses_2016_ratios.root",
                            '2016': "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ul2016__btv_effmaps/results/summedProcessesForEffmaps/summedProcesses_2016_ratios.root",
                            '2017': "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ul2017__btv_effmaps__ext2/results/summedProcessesForEffmaps/summedProcesses_2017_ratios.root",
                            '2018': "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ul2018__btv_effmaps/results/summedProcessesForEffmaps/summedProcesses_2018_ratios.root"
                        }

        cleaned_AK4JetsByDeepFlav = op.sort(AK4jets, lambda j: -j.btagDeepFlavB)
        cleaned_AK4JetsByDeepB    = op.sort(AK4jets, lambda j: -j.btagDeepB)
        cleaned_AK8JetsByDeepB    = op.sort(AK8jets, lambda j: -j.btagDeepB)

        csv_deepcsvAk4     = scalesfactorsULegacyLIB['DeepCSV']['Ak4'][era]
        csv_deepcsvSubjets = scalesfactorsULegacyLIB['DeepCSV']['softdrop_subjets'][era]
        csv_deepflavour    = scalesfactorsULegacyLIB['DeepFlavour'][era]

        btagSF_deepcsv    = BtagSF('deepcsv', csv_deepcsvAk4, wp=OP, sysType="central", otherSysTypes=["up", "down"],
                                                measurementType={"B": "comb", "C": "comb", "UDSG": "incl"}, sel= noSel, uName=f'sf_eff_{self.SetCat}_On{sample}_deepcsv{wp}')
        btagSF_deepflavour= BtagSF('deepflavour', csv_deepflavour, wp=OP, sysType="central", otherSysTypes=["up", "down"],
                                                    measurementType={"B": "comb", "C": "comb", "UDSG": "incl"}, sel= noSel, uName=f'sf_eff_{self.SetCat}_On{sample}_deepflavour{wp}')
        if 'Tight' not in OP : 
            btagSF_subjets= BtagSF('deepcsv', csv_deepcsvSubjets, wp=OP, sysType="central", otherSysTypes=["up", "down"],
                                                measurementType={"B": "lt", "C": "lt", "UDSG": "incl"}, sel= noSel, uName=f'sf_eff_{self.SetCat}_On{sample}_subjets_deepcsv{wp}')

        # resolved 
        bJets_resolved_PassdeepflavourWP  = bjets_resolved["DeepFlavour"][wp]
        bJets_resolved_PassdeepcsvWP      = bjets_resolved["DeepCSV"][wp]
        # boosted
        bJets_boosted_PassdeepcsvWP       = bjets_boosted["DeepCSV"][wp]

        for process in ['gg_fusion', 'bb_associatedProduction']:
            
            if os.path.exists(ROOTEffMapsPath[era]):
                bTagEff_deepcsvAk4  = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "resolved", "deepcsv", {%s}, "%s");'%(ROOTEffMapsPath[era], wp, legacy_btagging_wpdiscr_cuts['DeepCSV'][era][idx], process))
                bTagEff_deepflavour = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "resolved", "deepflavour", {%s}, "%s");'%(ROOTEffMapsPath[era], wp, legacy_btagging_wpdiscr_cuts['DeepFlavour'][era][idx], process))
                if 'T' not in wp:
                    bTagEff_deepcsvAk8 = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "boosted", "deepcsv", {%s}, "%s");'%(ROOTEffMapsPath[era], wp, legacy_btagging_wpdiscr_cuts['DeepCSV'][era][idx], process))
                else:
                    raise RuntimeError(f"{era} efficiencies maps not found !")
            
            if isMC:
                bTagSF_DeepCSVPerJet     = op.map(cleaned_AK4JetsByDeepB, lambda j: bTagEff_deepcsvAk4.evaluate( j.hadronFlavour, j.btagDeepB, j.pt*j.bRegCorr, op.abs(j.eta), btagSF_deepcsv(j)))
                bTagSF_DeepFlavourPerJet = op.map(cleaned_AK4JetsByDeepFlav, lambda j: bTagEff_deepflavour.evaluate(j.hadronFlavour, j.btagDeepFlavB, j.pt*j.bRegCorr, op.abs(j.eta), btagSF_deepflavour(j)))
                bTagSF_DeepCSVPerSubJet  = op.map(cleaned_AK8JetsByDeepB, lambda j: op.product(
                                                                                        bTagEff_deepcsvAk8.evaluate( 
                                                                                                op.static_cast("BTagEntry::JetFlavor", 
                                                                                                            op.multiSwitch((j.nBHadrons >0, op.c_int(5)), 
                                                                                                                            (j.nCHadrons >0, op.c_int(4)), 
                                                                                                                            op.c_int(0)) ), 
                                                                                                    j.subJet1.btagDeepB, 
                                                                                                    j.subJet1.pt, 
                                                                                                    op.abs(j.subJet1.eta), 
                                                                                                    btagSF_subjets(j)) , 
                                                                                        bTagEff_deepcsvAk8.evaluate( 
                                                                                                op.static_cast("BTagEntry::JetFlavor",
                                                                                                            op.multiSwitch((j.nBHadrons >0, op.c_int(5)), 
                                                                                                                (j.nCHadrons >0, op.c_int(4)), 
                                                                                                                op.c_int(0)) ), 
                                                                                                    j.subJet2.btagDeepB, 
                                                                                                    j.subJet2.pt, 
                                                                                                    op.abs(j.subJet2.eta), 
                                                                                                    btagSF_subjets(j))  )
                                                                                        )
                
                run2_bTagEventWeight_PerWP[process]['resolved'] = { 'DeepCSV{0}'.format(wp): op.rng_product(bTagSF_DeepCSVPerJet), 'DeepFlavour{0}'.format(wp): op.rng_product(bTagSF_DeepFlavourPerJet) }
                run2_bTagEventWeight_PerWP[process]['boosted']  = { 'DeepCSV{0}'.format(wp): op.rng_product(bTagSF_DeepCSVPerSubJet) }


        LeptonsPlusBjets_NoMETCut_NobTagEventWeight_Res = {
                    "gg_fusion": {
                                "DeepFlavour{0}".format(wp) :  lljjSelections["resolved"].refine("TwoLeptonsExactlyTwoBjets_NoMETcut_NobTagEventWeight_DeepFlavour{0}_{1}_Resolved".format(wp, self.SetCat),
                                                                    cut=[ op.rng_len(bJets_resolved_PassdeepflavourWP) == 2 ] ),
                                "DeepCSV{0}".format(wp)     :  lljjSelections["resolved"].refine("TwoLeptonsExactlyTwoBjets_NoMETcut_NobTagEventWeight_DeepCSV{0}_{1}_Resolved".format(wp, self.SetCat),
                                                                    cut=[ op.rng_len(bJets_resolved_PassdeepcsvWP) == 2, op.rng_len(bJets_boosted_PassdeepcsvWP) == 0]) },
                    "bb_associatedProduction": {
                                "DeepFlavour{0}".format(wp) :  lljjSelections["resolved"].refine("TwoLeptonsAtLeast3Bjets_NoMETcut_NobTagEventWeight_DeepFlavour{0}_{1}_Resolved".format(wp, self.SetCat),
                                                                    cut=[ op.rng_len(bJets_resolved_PassdeepflavourWP) >= 3] ),
                                "DeepCSV{0}".format(wp)     :  lljjSelections["resolved"].refine("TwoLeptonsAtLeast3Bjets_NoMETcut_NobTagEventWeight_DeepCSV{0}_{1}_Resolved".format(wp, self.SetCat),
                                                                    cut=[ op.rng_len(bJets_resolved_PassdeepcsvWP) >= 3, op.rng_len(bJets_boosted_PassdeepcsvWP) == 0]) },
                        }

        LeptonsPlusBjets_NoMETCut_NobTagEventWeight_Boo = {
                    "gg_fusion": {
                                "DeepCSV{0}".format(wp)     :  lljjSelections["boosted"].refine("TwoLeptonsAtLeast1FatBjets_NoMETcut_NobTagEventWeight_DeepCSV{0}_{1}_Boosted".format(wp, self.SetCat),
                                                                    cut=[ op.rng_len(bJets_boosted_PassdeepcsvWP) == 1, op.rng_len(bJets_resolved_PassdeepcsvWP) == 0] ) },
                    "bb_associatedProduction": {
                                "DeepCSV{0}".format(wp)     :  lljjSelections["boosted"].refine("TwoLeptonsAtLeast1FatBjets_with_AtLeast1AK4_NoMETcut_NobTagEventWeight_DeepCSV{0}_{1}_Boosted".format(wp, self.SetCat),
                                                                    cut=[ op.OR( op.AND(op.rng_len(bJets_boosted_PassdeepcsvWP) >= 2 , op.rng_len(bJets_resolved_PassdeepcsvWP) == 0),
                                                                                    op.AND(op.rng_len(bJets_boosted_PassdeepcsvWP) >= 1 , op.rng_len(bJets_resolved_PassdeepcsvWP) >= 1)
                                                                                    )] )},
                        }
            
            
        llbbSelections_NoMETCut_NobTagEventWeight = { "gg_fusion":{ "resolved": LeptonsPlusBjets_NoMETCut_NobTagEventWeight_Res["gg_fusion"],
                                                                    "boosted" : LeptonsPlusBjets_NoMETCut_NobTagEventWeight_Boo["gg_fusion"] },
                                                       "bb_associatedProduction":{ "resolved": LeptonsPlusBjets_NoMETCut_NobTagEventWeight_Res["bb_associatedProduction"], 
                                                                                   "boosted" : LeptonsPlusBjets_NoMETCut_NobTagEventWeight_Boo["bb_associatedProduction"] }
                                                    }
        
        llbbSelections_NoMETCut_bTagEventWeight = { process: 
                                                        { reg: 
                                                            { key: selNobTagWeight.refine(f"TwoLeptonsTwoBjets_NoMETCut_bTagEventWeight_{key}_{self.SetCat}_{reg}_{process}", weight = (run2_bTagEventWeight_PerWP[process][reg][key] if isMC else None))
                                                            for key, selNobTagWeight in NobTagEventWeight_selections_per_taggerWP.items() }
                                                        for reg, NobTagEventWeight_selections_per_taggerWP in NobTagEventWeight_selections_per_process.items() }
                                                    for process, NobTagEventWeight_selections_per_process in llbbSelections_NoMETCut_NobTagEventWeight.items() 
                                                }
    

        if pass_bTagEventWeight:
            llbbSelections_noMETCut = llbbSelections_NoMETCut_bTagEventWeight
        else:
            llbbSelections_noMETCut = llbbSelections_NoMETCut_NobTagEventWeight

        llbbSelections = { process: 
                                { reg:
                                    { key: selNoMET.refine(f"TwoLeptonsTwoBjets_METCut_bTagEventWeight_{key}_{self.SetCat}_{reg}_{process}", cut=[ corrMET.pt < 80. ])
                                    for key, selNoMET in noMETSels.items() }
                                for reg, noMETSels in llbbSelections_noMETCut_per_process.items() }
                            for process, llbbSelections_noMETCut_per_process in llbbSelections_noMETCut.items() 
                        }
                 
        #===================================================================================
            # boosted or resolved 
            ### Two OS SF Leptons _ Two Jets  selection inclusive 
        #===================================================================================
        if self.SetSel=="2Lep2Jets":
            FinalSel = lljjSelections[self.SetRegion]
            if self.SetRegion=="resolved":
                lljj_M= (dilepton[0].p4 +dilepton[1].p4+jets[0].p4+jets[1].p4).M()
                jj_M=op.invariant_mass(jets[0].p4, jets[1].p4)
        
            elif self.SetRegion=="boosted":
                lljj_M= (dilepton[0].p4 +dilepton[1].p4+jets[0].p4).M()
                jj_M=op.invariant_mass(jets[0].p4)
            
            # For the DNN better have variables with the same name ...
            varsToKeep["lljj_M"]= lljj_M
            varsToKeep["jj_M"]  = jj_M
            varsToKeep["nB_{0}".format( suffix)] = op.static_cast("UInt_t", op.rng_len(jets))
            
        #===================================================================================
            ### Two OS SF Leptons _ Two bJets  selection + MET cut
        #===================================================================================
        elif self.SetSel=="2Lep2bJets":
            FinalSel = llbbSelections[process][self.SetRegion][self.SetTagger + self.SetWP]
            

            if self.SetRegion=="resolved":
                
                bjets_ = bjets_resolved[self.SetTagger][self.SetWP]
                bJets = bJetEnergyRegression (bjets_)
                
                llbb_M= (dilepton[0].p4 +dilepton[1].p4+bJets[0]+bJets[1]).M()
                bb_M= op.invariant_mass(bJets[0]+bJets[1])
            
            elif self.SetRegion=="boosted":

                bJets = bjets_boosted[self.SetTagger][self.SetWP]
                llbb_M= (dilepton[0].p4 +dilepton[1].p4+bJets[0].p4).M()
                bb_M  = bJets[0].mass
                bb_softDropM = bJets[0].msoftdrop
    
                varsToKeep["bb_softDropM"]= bb_softDropM
            
            varsToKeep["llbb_M"]= llbb_M
            varsToKeep["bb_M"]= bb_M

            varsToKeep["nB_{0}".format( suffix)] = op.static_cast("UInt_t", op.rng_len(bJets))
            
        else:
            raise RuntimeError('ERROR : %s  in selection args' %self.SetSel)
        
        varsToKeep["l1_charge"] = leptons_charge["l1"]
        varsToKeep["l2_charge"] = leptons_charge["l2"]
        varsToKeep["l1_pdgId"]  = leptons_pdgId["l1"]
        varsToKeep["l2_pdgId"]  = leptons_pdgId["l2"]
        varsToKeep['total_weight'] = FinalSel.weight            
        print ( '*** ALL DONE ***' )    
        return FinalSel, varsToKeep
