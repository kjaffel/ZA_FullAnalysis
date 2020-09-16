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
import utils
from utils import safeget

import logging
logger = logging.getLogger("ZA SKIMMER")

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

        noSel, PUWeight, categories, isDY_reweight, WorkingPoints, deepBFlavScaleFactor, deepB_AK4ScaleFactor, AK4jets, AK8jets, bjets_resolved, bjets_boosted, CleanJets_fromPileup, electrons, muons, MET, corrMET, PuppiMET, elRecoSF_highpt, elRecoSF_lowpt = self.defineObjects(t, noSel, sample, sampleCfg)

        era = sampleCfg["era"]
        isMC = self.isMC(sample)
        
        if self.SetSel not in [ "noSel", "OsLeptons", "2Lep2Jets", "2Lep2bJets"]:
            print ('[Skimedtree_NanoHtoZA]: %s Unkown selection ' %self.SetSel)
            sys.exit(0)

        if self.SetRegion not in ["boosted", "resolved"]:
            print ( '[Skimedtree_NanoHtoZA]: Region of studies should be : boosted or resolved ! ' )
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
            jets= AK4jets
            bjets= bjets_resolved
            suffix = "AK4Jets"
        
        elif self.SetRegion=="boosted":
            jets= AK8jets
            bjets= bjets_boosted
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
                # xy corr
            varsToKeep["CorrMET_pt"]  = corrMET.pt
            varsToKeep["CorrMET_phi"] = corrMET.phi
    
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
        for wp in WorkingPoints:
            bJets_resolved_PassdeepflavourWP=safeget(bjets_resolved, "DeepFlavour", wp)
            bJets_resolved_PassdeepcsvWP=safeget(bjets_resolved, "DeepCSV", wp)
            bJets_boosted_PassdeepcsvWP=safeget(bjets_boosted, "DeepCSV", wp)
            
            print ( bJets_resolved_PassdeepflavourWP, bjets_resolved, '**********************')
            TwoLeptonsTwoBjets_NoMETCut_Res = {
                "DeepFlavour{0}".format(wp) :  lljjSelections["resolved"].refine("TwoLeptonsTwoBjets_NoMETcut_DeepFlavour{0}_{1}_Resolved".format(wp, self.SetCat),
                                                                        cut=[ op.rng_len(bJets_resolved_PassdeepflavourWP) > 1 ],
                                                                        weight=([ deepBFlavScaleFactor(bJets_resolved_PassdeepflavourWP[0]), 
                                                                                  deepBFlavScaleFactor(bJets_resolved_PassdeepflavourWP[1])
                                                                                ] if isMC else None
                                                                                )),

                "DeepCSV{0}".format(wp)     :  lljjSelections["resolved"].refine("TwoLeptonsTwoBjets_NoMETcut_DeepCSV{0}_{1}_Resolved".format(wp, self.SetCat),
                                                                        # here where the selection become exclusive 
                                                                        cut=[ op.rng_len(bJets_resolved_PassdeepcsvWP) > 1, op.rng_len(bJets_boosted_PassdeepcsvWP) ==0],
                                                                        weight=([ deepB_AK4ScaleFactor(bJets_resolved_PassdeepcsvWP[0]), 
                                                                                  deepB_AK4ScaleFactor(bJets_resolved_PassdeepcsvWP[1])
                                                                                ] if isMC else None
                                                                                ))
                                            }


            TwoLeptonsOneBjets_NoMETCut_Boo = {
                "DeepCSV{0}".format(wp)     :  lljjSelections["boosted"].refine("TwoLeptonsOneBjets_NoMETcut_DeepCSV{0}_{1}_Boosted".format(wp, self.SetCat),
                                                                        cut=[ op.rng_len(bJets_boosted_PassdeepcsvWP) > 0 ])
                                                }
        llbbSelections_noMETCut = {
                "resolved": TwoLeptonsTwoBjets_NoMETCut_Res,
                "boosted" : TwoLeptonsOneBjets_NoMETCut_Boo
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
            bJets = safeget(bjets, self.SetTagger, self.SetWP)
            FinalSel = safeget( llbbSelections_noMETCut [self.SetRegion], key)
            
            if self.SetRegion=="resolved":
                llbb_M= (dilepton[0].p4 +dilepton[1].p4+bJets[0].p4+bJets[1].p4).M()
                bb_M= op.invariant_mass(bJets[0].p4+bJets[1].p4)
            
            elif self.SetRegion=="boosted":
                llbb_M= (dilepton[0].p4 +dilepton[1].p4+bJets[0].p4).M()
                bb_M= op.invariant_mass(bJets[0].p4)

            
            varsToKeep["llbb_M"]= llbb_M
            varsToKeep["bb_M"]= bb_M
            varsToKeep["nB_{0}".format( suffix)] = op.static_cast("UInt_t", op.rng_len(bJets))
            
        else:
            raise RuntimeError('ERROR : %s  in selection args' %self.SetSel)

        varsToKeep['total_weight'] = FinalSel.weight            
        print ( '*** ALL DONE ***' )    
        return FinalSel, varsToKeep
