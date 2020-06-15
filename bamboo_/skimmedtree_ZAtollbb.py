import os
import sys
import argparse

from bamboo.analysismodules import  NanoAODSkimmerModule
from bamboo.analysisutils import makePileupWeight
from bamboo import treefunctions as op

zabPath = os.path.dirname(__file__)
if zabPath not in sys.path:
    sys.path.append(zabPath)
from ObjectsReco import NanoHtoZABase, safeget

import logging
logger = logging.getLogger("SKIMMER")

def value_for_channel(d, channel, return_dilepton):
    """Return a value in neseted dic `d` having a key == channel ."""
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

        noSel, PUWeight, corrMET, muons, electrons, AK4jets, AK8jets, bjets_resolved, bjets_boosted, categories, WorkingPoints, selections_2lep2bjets_METCut, selections_2lep2bjets_NoMET, selections_2lep2jets = self.defineObjects(t, noSel, sample, sampleCfg)

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
    
            if self.SetWP not in WorkingPoints:
                print ('[Skimedtree_NanoHtoZA]: %s not found in WorkingPoints ' % self.SetWP)
                print ('[Skimedtree_NanoHtoZA]: I could only find in ObjectsReco ** ')
                print (WorkingPoints)
                sys.exit(1)
        
        logger.info("Start filling the Tree ...")
        print ("GIVING INFOS TO ZA SKIMMER :", 'Region=', self.SetRegion, ', Catgorie=', self.SetCat, ', Tagger=', self.SetTagger, ', WP=', self.SetWP)

        if self.SetRegion== "resolved":
            jets= AK4jets
            bjets= bjets_resolved
            suffix = "AK4Jets"
            maxJets = 2
        
        elif self.SetRegion=="boosted":
            jets= AK8jets
            bjets= bjets_boosted
            suffix= "AK8Jets"
            maxJets = 1
        
        else:
            raise RuntimeError('ERROR : %s Unkown args' %self.SetRegion)
        
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
    
        
        # boosted or resolved 
        ### Two OS SF Leptons _ Two Jets  selection
        if self.SetSel=="2Lep2Jets":
            
            if self.SetRegion=="resolved":
                FinalSel = selections_2lep2jets[self.SetCat][0]
                lljj_M= (dilepton[0].p4 +dilepton[1].p4+jets[0].p4+jets[1].p4).M()
                jj_M=op.invariant_mass(jets[0].p4, jets[1].p4)
        
            elif self.SetRegion=="boosted":
                FinalSel = selections_2lep2jets[self.SetCat][1]
                lljj_M= (dilepton[0].p4 +dilepton[1].p4+jets[0].p4).M()
                jj_M=op.invariant_mass(jets[0].p4)
            
            #for i in range(maxJets):
            #    varsToKeep["{0}_{1}_pt".format(suffix, i)]  = jets[i].p4.pt
            #    varsToKeep["{0}_{1}_eta".format(suffix, i)] = jets[i].p4.eta
            #    varsToKeep["{0}_{1}_phi".format(suffix, i)] = jets[i].p4.phi
            
            # For the DNN better have variables with the same name ...
            varsToKeep["lljj_M"]= lljj_M
            varsToKeep["jj_M"]  = jj_M
            varsToKeep["nB_{0}".format( suffix)] = op.static_cast("UInt_t", op.rng_len(jets))
            
            #varsToKeep["lljj_M_{0}_{1}{2}_{3}".format(self.SetRegion, self.SetTagger, self.SetWP, self.SetCat)]= lljj_M
            #varsToKeep["jj_M_{0}_{1}{2}_{3}".format(self.SetRegion, self.SetTagger, self.SetWP, self.SetCat)]  = jj_M
            #varsToKeep["nB_{0}_{1}{2}_{3}".format( suffix, self.SetTagger, self.SetWP, self.SetCat)] = op.static_cast("UInt_t", op.rng_len(bJets))
        
            ### Two OS SF Leptons _ Two bJets  selection +MET cut (xy corr applied too )
        elif self.SetSel=="2Lep2bJets":
            key = self.SetTagger + self.SetWP
            bJets = safeget(bjets, self.SetTagger, self.SetWP)
        
            if self.SetRegion=="resolved":
                FinalSel = safeget( selections_2lep2bjets_METCut [self.SetCat][0], self.SetWP, key)
                llbb_M= (dilepton[0].p4 +dilepton[1].p4+bJets[0].p4+bJets[1].p4).M()
                bb_M= op.invariant_mass(bJets[0].p4+bJets[1].p4)
            
            elif self.SetRegion=="boosted":
                FinalSel = safeget( selections_2lep2bjets_METCut [self.SetCat][1], self.SetWP, key)
                llbb_M= (dilepton[0].p4 +dilepton[1].p4+bJets[0].p4).M()
                bb_M= op.invariant_mass(bJets[0].p4)

            #for i in range(maxJets):
            #    varsToKeep["{0}_{1}_pt".format(suffix, i)]  = bJets[i].p4.pt
            #    varsToKeep["{0}_{1}_eta".format(suffix, i)] = bJets[i].p4.eta
            #    varsToKeep["{0}_{1}_phi".format(suffix, i)] = bJets[i].p4.phi
            
            varsToKeep["llbb_M"]= llbb_M
            varsToKeep["bb_M"]= bb_M
            varsToKeep["nB_{0}".format( suffix)] = op.static_cast("UInt_t", op.rng_len(bJets))
            
            #varsToKeep["llbb_M_{0}_{1}{2}_{3}".format(self.SetRegion, self.SetTagger, self.SetWP, self.SetCat)]= llbb_M
            #varsToKeep["bb_M_{0}_{1}{2}_{3}".format(self.SetRegion, self.SetTagger, self.SetWP, self.SetCat)]= bb_M
            #varsToKeep["nB_{0}_{1}{2}_{3}".format( suffix, self.SetTagger, self.SetWP, self.SetCat)] = op.static_cast("UInt_t", op.rng_len(bJets))
        else:
            raise RuntimeError('ERROR : %s  in selection args' %self.SetSel)

        varsToKeep['total_weight'] = FinalSel.weight            
    
        return FinalSel, varsToKeep
