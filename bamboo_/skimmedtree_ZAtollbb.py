import sys
import argparse

from bamboo.analysismodules import  NanoAODSkimmerModule
from bamboo.analysisutils import makePileupWeight
from bamboo import treefunctions as op

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_')
from ZAtollbb_PreSelection import NanoHtoZABase, safeget

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
        noSel, PUWeight, corrMET, muons, electrons, AK4jets, AK8jets, bjets_resolved, bjets_boosted, categories, TwoLeptonsTwoJets_Resolved, TwoLeptonsTwoJets_Boosted, TwoLeptonsTwoBjets_Res, TwoLeptonsTwoBjets_Boo, TwoLeptonsTwoBjets_NoMETCut_Res, TwoLeptonsTwoBjets_NoMETCut_Boo, WorkingPoints = self.defineObjects(t, noSel, sample, sampleCfg)

        era = sampleCfg["era"]
        isMC = self.isMC(sample)
        
        if self.SetSel not in [ "noSel", "OsLeptons", "2Lep2Jets", "2Lep2bJets"]:
            print ('[Skimedtree_NanoHtoZA]: %s Unkown selection ' %self.SetSel)
            sys.exit(0)

        if self.SetRegion not in ["boosted", "resolved"]:
            print ( ' Region of studies should be : boosted or resolved ! ' )
            sys.exit(0)
        
        if self.SetRegion=="boosted":
            self.SetTagger = "DeepCSV" # FIXME add later DeepDoubleB 
        else:
            if self.SetTagger not in ["DeepFlavour", "DeepCSV"]:
                print ('[Skimedtree_NanoHtoZA]: %s Unknown tagger for resolved region' %self.SetTagger)
                sys.exit(0)

        if self.SetCat not in categories.keys():
            print ('[Skimedtree_NanoHtoZA] channel %s not found in categories' % self.SetCat)
            print ('Available channel are :')
            print (categories.keys())
            sys.exit(0)
        
        if self.SetWP is None:
            print ('[Skimedtree_NanoHtoZA]: WP is MANDATORY, this is the working point as defined in the ZAtollbb_PreSelection.py')
            sys.exit(0)
    
        if self.SetWP not in WorkingPoints:
            print ('[Skimedtree_NanoHtoZA] WP %s not found in working points definitions' % self.SetWP)
            print ('  --> define in settings first')
            print ('  In settings I found WPs: ')
            print (WorkingPoints)
            sys.exit(1)
        
        key = self.SetTagger + self.SetWP
        if self.SetRegion== "resolved":
            jets= AK4jets
            bjets= bjets_resolved
            suffix = "AK4Jets"
        elif self.SetRegion=="boosted":
            jets= AK8jets
            bjets= bjets_boosted
            suffix= "AK8Jets"
        else:
            raise RuntimeError('ERROR : %s Unkown args' %self.SetRegion)
        
        #variables to keep from the input tree
        varsToKeep = {"run": None, "luminosityBlock": None, "event": None}
        
        if isMC:
            varsToKeep["MC_weight"] = t.genWeight
            #varsToKeep["PU_weight"] = PUWeight
            puWeightsFile = os.path.join(os.path.dirname(__file__), "data/PileupFullRunII/", "puweights2016_Moriond17.json")
            varsToKeep["PU_weight"] = makePileupWeight(puWeightsFile, tree.Pileup_nTrueInt, variation="Nominal",
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
            RawMET = (MET if era != "2017" else METFixEE2017)
            varsToKeep["CorrMET_pt"]  = RawMET.pt
            varsToKeep["CorrMET_phi"] = RawMET.phi
                # xy corr
            varsToKeep["CorrMET_pt"]  = corrMET.pt
            varsToKeep["CorrMET_phi"] = corrMET.phi

        
        for channel, (dilepton, catSel) in categories.items():
            
            ### Opposite sign leptons , Same Flavour  selection 
            if self.SetSel=="OsLeptons":
                FinalSel= catSel
                for i in range(2):
                    varsToKeep["lep{0}_pt_{1}".format(i, self.SetCat)]  = dilepton[i].p4.pt
                    varsToKeep["lep{0}_eta_{1}".format(i, self.SetCat)] = dilepton[i].p4.eta
                    varsToKeep["lep{0}_phi_{1}".format(i, self.SetCat)] = dilepton[i].p4.phi
                ll_M   = op.invariant_mass(dilepton[0].p4, dilepton[1].p4)
                varsToKeep["ll_M_{0}".format(channel)]  = ll_M
            
            
            # boosted or resolved 
                ### Two OS SF Leptons _ Two Jets  selection
            elif self.SetSel=="2Lep2Jets":
                if self.SetRegion=="resolved": 
                    FinalSel = TwoLeptonsTwoJets_Resolved.get(key)
                elif self.SetRegion=="boosted":
                    FinalSel= TwoLeptonsTwoJets_Boosted.get(key) 
                
                lljj_M= (dilepton[0].p4 +dilepton[1].p4+jets[0].p4+jets[1].p4).M()
                jj_M=op.invariant_mass(jets[0].p4, jets[1].p4)
                # For the DNN better have variables with the same name ...
                varsToKeep["lljj_M"]= lljj_M
                varsToKeep["jj_M"]  = jj_M
                varsToKeep["nB_{0}".format( suffix)] = op.static_cast("UInt_t", op.rng_len(bJets))
                
                #varsToKeep["lljj_M_{0}_{1}{2}_{3}".format(self.SetRegion, self.SetTagger, self.SetWP, self.SetCat)]= lljj_M
                #varsToKeep["jj_M_{0}_{1}{2}_{3}".format(self.SetRegion, self.SetTagger, self.SetWP, self.SetCat)]  = jj_M
                #varsToKeep["nB_{0}_{1}{2}_{3}".format( suffix, self.SetTagger, self.SetWP, self.SetCat)] = op.static_cast("UInt_t", op.rng_len(bJets))
            
                ### Two OS SF Leptons _ Two bJets  selection +MET cut (xy corr applied too )
            elif self.SetSel=="2Lep2bJets":
                bJets = safeget(bjets, self.SetTagger, self.SetWP)
                if self.SetRegion=="resolved":
                    FinalSel = TwoLeptonsTwoBjets_Res.get(key)
                elif self.SetRegion=="boosted":
                    FinalSel = TwoLeptonsTwoBjets_Boo.get(key)
    
                llbb_M= (dilepton[0].p4 +dilepton[1].p4+bJets[0].p4+bJets[1].p4).M()
                bb_M= op.invariant_mass(bJets[0].p4+bJets[1].p4)
                
                varsToKeep["llbb_M"]= llbb_M
                varsToKeep["bb_M"]= bb_M
                varsToKeep["nB_{0}".format( suffix)] = op.static_cast("UInt_t", op.rng_len(bJets))
                
                #varsToKeep["llbb_M_{0}_{1}{2}_{3}".format(self.SetRegion, self.SetTagger, self.SetWP, self.SetCat)]= llbb_M
                #varsToKeep["bb_M_{0}_{1}{2}_{3}".format(self.SetRegion, self.SetTagger, self.SetWP, self.SetCat)]= bb_M
                #varsToKeep["nB_{0}_{1}{2}_{3}".format( suffix, self.SetTagger, self.SetWP, self.SetCat)] = op.static_cast("UInt_t", op.rng_len(bJets))
            else:
                raise RuntimeError('ERROR : %s  in selection args' %self.SetSel)
            
            #sample_weight=
            #event_weight=
            #total_weight=
            #cross_section=

        return FinalSel, varsToKeep
