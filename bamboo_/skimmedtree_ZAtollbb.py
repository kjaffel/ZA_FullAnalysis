import os
import sys
import argparse

from bamboo.analysismodules import  NanoAODSkimmerModule
from bamboo.analysisutils import makePileupWeight
from bamboo import treefunctions as op

zabPath = os.path.dirname(__file__)
if zabPath not in sys.path:
    sys.path.append(zabPath)

from ZAtollbb import NanoHtoZABase
from b_regression import scalesfactorsLIB
import utils
from utils import safeget

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
    
    def addArgs(self, parser):
        super(Skimedtree_NanoHtoZA, self).addArgs(parser)
        parser.add_argument("-sel", "--selections",    default=None, help="set Final Selection")
        parser.add_argument("-reg", "--regions",       default=None, help="Produce ntuples in Boosted or resolved region")
        parser.add_argument("-cat", "--categories",    default=None, help="Produce ntuples in ElEl or MuMu channel")
        parser.add_argument("-Tag", "--taggers",       default=None, help="Set tagger for b-jet identification")
        parser.add_argument("-wp",  "--workingpoints", default=None, help="Setting Working point is mandatory")
    
    def defineSkimSelection(self, t, noSel, sample=None, sampleCfg=None):
        from bamboo.root import addIncludePath, loadHeader
        from bamboo.scalefactors import BtagSF

        noSel, PUWeight, categories, isDY_reweight, WorkingPoints, btagging, deepBFlavScaleFactor, deepB_AK4ScaleFactor, deepB_AK8ScaleFactor, AK4jets, AK8jets, fatjets_nosubjettinessCut, bjets_resolved, bjets_boosted, CleanJets_fromPileup, electrons, muons, MET, corrMET, PuppiMET, elRecoSF_highpt, elRecoSF_lowpt = self.defineObjects(t, noSel, sample, sampleCfg)
        
        era = sampleCfg["era"]
        isMC = self.isMC(sample)
        
        if self.SetSel not in [ "noSel", "OsLeptons", "2Lep2Jets", "2Lep2bJets"]:
            print ('[Skimedtree_NanoHtoZA]: %s Unkown selection ' %self.SetSel)
            sys.exit(0)

        if self.SetRegion not in ["boosted", "resolved"]:
            print ('[Skimedtree_NanoHtoZA]: Region of studies should be : boosted or resolved ! ' )
            sys.exit(0)
        

        if self.SetCat not in categories.keys():
            print ('[Skimedtree_NanoHtoZA]: channel %s not found in categories' % self.SetCat)
            print ('[Skimedtree_NanoHtoZA]: I could only find ** ')
            print (categories.keys())
            sys.exit(0)
        
        if self.SetSel=="2Lep2bJets":
            
            if self.SetRegion=="boosted":
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
        
        if self.SetRegion== "resolved":
            jets= bJetEnergyRegression (AK4jets)
            suffix = "AK4Jets"
        
        elif self.SetRegion=="boosted":
            jets= AK8jets
            suffix= "AK8Jets"
        
        else:
            raise RuntimeError('[Skimedtree_NanoHtoZA]: %s Unkown args' %self.SetRegion)
        
        logger.info("Start filling the Tree ...")
        logger.info(f"[Skimedtree_NanoHtoZA]: Region= {self.SetRegion}, Channel= {self.SetCat}, Tagger= {self.SetTagger}, WP={self.SetWP}")
        #variables to keep from the input tree
        varsToKeep = {"run": None, "luminosityBlock": None, "event": None}
        
        if isMC:
            varsToKeep["MC_weight"] = t.genWeight
            jsonfile = ('puweights2016_Moriond17.json' if era == '2016' else( 'puweights2017_Fall17.json' if era == '2017' else ('puweights2018_Autumn18.json')))
            puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/", jsonfile)
            varsToKeep["PU_weight"] = makePileupWeight(puWeightsFile, t.Pileup_nTrueInt, variation="Nominal",
                                                        nameHint="puWeight{0}".format("".join(c for c in sample if c.isalnum())))

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
    
        ### Opposite sign leptons , Same Flavour  selection 
        dilepton = value_for_channel(categories, self.SetCat, True)
    
        if self.SetSel=="OsLeptons":
            FinalSel= value_for_channel(categories, self.SetCat, False)
            for i in range(2):
                varsToKeep["lep{0}_pt".format(i)]  = dilepton[i].p4.pt
                varsToKeep["lep{0}_eta".format(i)] = dilepton[i].p4.eta
                varsToKeep["lep{0}_phi".format(i)] = dilepton[i].p4.phi
        
            ll_M   = op.invariant_mass(dilepton[0].p4, dilepton[1].p4)
            varsToKeep["ll_M"]  = ll_M
    
        TwoLeptonsTwoJets_Resolved= value_for_channel(categories, self.SetCat, False).refine("TwoJet_{0}Sel_resolved".format(self.SetCat), cut=[ op.rng_len(AK4jets) > 1])
        TwoLeptonsOneJet_Boosted = value_for_channel(categories, self.SetCat, False).refine("OneJet_{0}Sel_boosted".format(self.SetCat), cut=[ op.rng_len(AK8jets) > 0 ])

        lljjSelections = {
                "resolved": TwoLeptonsTwoJets_Resolved,
                "boosted" : TwoLeptonsOneJet_Boosted
                }
        
        pathtoRoOtmaps = { '2016': "/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/ver.20_10_08/results/summedProcessesForEffmaps/summedProcesses_2016_ratios.root",
                            '2017': "/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2017Results/ver.20_10_06/fix_bug_cause_missing_histograms/results/summedProcessesForEffmaps/summedProcesses_2017_ratios.root",
                            '2018': "/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2018Results/ver.20_10_06/fix_bug_causing_missingHistograms/results/summedProcessesForEffmaps/summedProcesses_2018_ratios.root"
                        }
        
        cleaned_AK4JetsByDeepFlav = op.sort(AK4jets, lambda j: -j.btagDeepFlavB)
        cleaned_AK4JetsByDeepB = op.sort(AK4jets, lambda j: -j.btagDeepB)
        cleaned_AK8JetsByDeepB = op.sort(AK8jets, lambda j: -j.btagDeepB)

        for wp in WorkingPoints:
            idx = ( 0 if wp=="L" else ( 1 if wp=="M" else 2))
            if os.path.exists(pathtoRoOtmaps[era]):
                bTagEff_deepcsvAk4 = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "resolved", "deepcsv", {%s});'%(pathtoRoOtmaps[era], wp, btagging['DeepCSV'][era][idx]))
                bTagEff_deepflavour = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "resolved", "deepflavour", {%s});'%(pathtoRoOtmaps[era], wp, btagging['DeepFlavour'][era][idx]))
                if 'T' not in wp:
                    bTagEff_deepcsvAk8 = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "boosted", "deepcsv", {%s});'%(pathtoRoOtmaps[era], wp, btagging['DeepCSV'][era][idx]))
            else:
                raise RuntimeError(f"{era} efficiencies maps not found !")
                
            csv_deepcsvAk4 = scalesfactorsLIB['DeepCSV']['Ak4'][era]
            csv_deepcsvSubjets = scalesfactorsLIB['DeepCSV']['softdrop_subjets'][era]
            csv_deepflavour = scalesfactorsLIB['DeepFlavour'][era]
            OP= ("Loose" if wp=='L' else ("Medium" if wp=='M' else "Tight"))
    
            btagSF_deepcsv= BtagSF('deepcsv', csv_deepcsvAk4, wp=OP, sysType="central", otherSysTypes=["up", "down"],
                                                    systName= f'mc_eff_deepcsv{wp}', measurementType={"B": "comb", "C": "comb", "UDSG": "incl"}, sel= noSel,
                                                    uName=f'sf_eff_{self.SetCat}_On{sample}_deepcsv{wp}')
            btagSF_deepflavour= BtagSF('deepflavour', csv_deepflavour, wp=OP, sysType="central", otherSysTypes=["up", "down"],
                                                    systName= f'mc_eff_deepflavour{wp}', measurementType={"B": "comb", "C": "comb", "UDSG": "incl"}, sel= noSel,
                                                    uName=f'sf_eff_{self.SetCat}_On{sample}_deepflavour{wp}')
            if 'Tight' not in OP : 
                btagSF_subjets= BtagSF('deepcsv', csv_deepcsvSubjets, wp=OP, sysType="central", otherSysTypes=["up", "down"],
                                                    systName= f'mc_eff_subjets_deepcsv{wp}', measurementType={"B": "lt", "C": "lt", "UDSG": "incl"}, sel= noSel,
                                                    uName=f'sf_eff_{self.SetCat}_On{sample}_subjets_deepcsv{wp}')
    
            deepcsv_bTagWeight = None
            deepflavour_bTagWeight = None
            deepcsvAk8_bTagWeight = None

            # resolved 
            bJets_resolved_PassdeepflavourWP=safeget(bjets_resolved, "DeepFlavour", wp)
            bJets_resolved_PassdeepcsvWP=safeget(bjets_resolved, "DeepCSV", wp)
            # boosted
            bJets_boosted_PassdeepcsvWP=safeget(bjets_boosted, "DeepCSV", wp)
    
            if isMC:
                bTagSF_DeepCSVPerJet = op.map(cleaned_AK4JetsByDeepB, 
                                                lambda j: bTagEff_deepcsvAk4.evaluate( j.hadronFlavour, j.btagDeepB, j.pt*j.bRegCorr, op.abs(j.eta), btagSF_deepcsv(j)))
                bTagSF_DeepFlavourPerJet = op.map(cleaned_AK4JetsByDeepFlav, 
                                                    lambda j: bTagEff_deepflavour.evaluate(j.hadronFlavour, j.btagDeepFlavB, j.pt*j.bRegCorr, op.abs(j.eta), btagSF_deepflavour(j)))
                bTagSF_DeepCSVPerSubJet = op.map(cleaned_AK8JetsByDeepB, 
                                                lambda j: op.product(
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
                deepcsv_bTagWeight = op.rng_product(bTagSF_DeepCSVPerJet)
                deepflavour_bTagWeight = op.rng_product(bTagSF_DeepFlavourPerJet)
                deepcsvAk8_bTagWeight = op.rng_product(bTagSF_DeepCSVPerSubJet)
    
            run2_bTagEventWeight_PerWP = { 'resolved': { 
                                                'DeepCSV{0}'.format(wp): deepcsv_bTagWeight,
                                                'DeepFlavour{0}'.format(wp): deepflavour_bTagWeight },
                                            'boosted' :  {'DeepCSV{0}'.format(wp): deepcsvAk8_bTagWeight }
                                    }
            
            
            TwoLeptonsTwoBjets_NoMETCut_bTagEventWeight_Res = {
                "DeepFlavour{0}".format(wp) :  lljjSelections["resolved"].refine("TwoLeptonsTwoBjets_NoMETcut_bTagEventWeight_DeepFlavour{0}_{1}_Resolved".format(wp, self.SetCat),
                                                                cut=[ op.rng_len(bJets_resolved_PassdeepflavourWP) > 1 ], 
                                                                    weight=run2_bTagEventWeight_PerWP['resolved']["DeepFlavour{0}".format(wp)]),
    
                "DeepCSV{0}".format(wp)     :  lljjSelections["resolved"].refine("TwoLeptonsTwoBjets_NoMETcut_bTagEventWeight_DeepCSV{0}_{1}_Resolved".format(wp, self.SetCat),
                                                                cut=[ op.rng_len(bJets_resolved_PassdeepcsvWP) > 1, op.rng_len(bJets_boosted_PassdeepcsvWP) ==0], 
                                                                    weight=run2_bTagEventWeight_PerWP['resolved']["DeepCSV{0}".format(wp)])
                                        }
    
            TwoLeptonsOneBjets_NoMETCut_bTagEventWeight_Boo = {
                "DeepCSV{0}".format(wp)     :  lljjSelections["boosted"].refine("TwoLeptonsOneBjets_NoMETcut_bTagEventWeight_DeepCSV{0}_{1}_Boosted".format(wp, self.SetCat),
                                                                    cut=[ op.rng_len(bJets_boosted_PassdeepcsvWP) > 0 ], 
                                                                weight=run2_bTagEventWeight_PerWP['boosted']["DeepCSV{0}".format(wp)])
                                        }
                        
            llbbSelections_NoMETCut_bTagEventWeight = { "resolved": TwoLeptonsTwoBjets_NoMETCut_bTagEventWeight_Res,
                                                    "boosted" : TwoLeptonsOneBjets_NoMETCut_bTagEventWeight_Boo }
                
            llbbSelections_METCut_bTagEventWeight = { reg:
                                                        { key: selbTag.refine(f"TwoLeptonsTwoBjets_METCut_bTagEventWeight_{key}_{self.SetCat}_{reg}", cut=[corrMET.pt <80. ])
                                                        for key, selbTag in bTagEventWeight_selections.items() }
                                                                for reg, bTagEventWeight_selections in llbbSelections_NoMETCut_bTagEventWeight.items()
                                                                } 
            
        # boosted or resolved 
        ### Two OS SF Leptons _ Two Jets  selection inclusive 
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
            
            ### Two OS SF Leptons _ Two bJets  selection + no MET cut
        elif self.SetSel=="2Lep2bJets":
            key = self.SetTagger + self.SetWP
            FinalSel = safeget( llbbSelections_METCut_bTagEventWeight [self.SetRegion], key)
            
            if self.SetRegion=="resolved":
                
                bjets = safeget(bjets_resolved, self.SetTagger, self.SetWP)
                bJets= bJetEnergyRegression (bjets)
                
                llbb_M= (dilepton[0].p4 +dilepton[1].p4+bJets[0]+bJets[1]).M()
                bb_M= op.invariant_mass(bJets[0]+bJets[1])
            
            elif self.SetRegion=="boosted":

                bJets = safeget(bjets_boosted, self.SetTagger, self.SetWP)
                llbb_M= (dilepton[0].p4 +dilepton[1].p4+bJets[0].p4).M()
                bb_M= bJets[0].mass
                bb_softDropM= bJets[0].msoftdrop
    
                varsToKeep["bb_softDropM"]= bb_softDropM
            
            varsToKeep["llbb_M"]= llbb_M
            varsToKeep["bb_M"]= bb_M
            varsToKeep["nB_{0}".format( suffix)] = op.static_cast("UInt_t", op.rng_len(bJets))
            
        else:
            raise RuntimeError('ERROR : %s  in selection args' %self.SetSel)

        varsToKeep['total_weight'] = FinalSel.weight            
        print ( '*** ALL DONE ***' )    
        return FinalSel, varsToKeep
