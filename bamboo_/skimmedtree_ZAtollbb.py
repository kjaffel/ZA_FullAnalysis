import looging

from bamboo.analysismodules import
from bamboo import treefunctions as op

import definitions as defs

class Skimedtree_NanoHtoZA(NanoAODSkimmerModule):
    def __init__(self, args):
        super(SkimNanoZMuMu, self).__init__(args)
    
    def defineSkimSelection(self, tree, noSel, sample=None, sampleCfg=None):
        era = sampleCfg["era"]
        
        #variables to keep from the input tree
        varsToKeep = {"run": None, "luminosityBlock": None, "event": None}

        ## Muons selection 
        sorted_muons=op.sort(t.Muon, lambda mu : -mu.p4.Pt())
        muons = op.select(sorted_muons, lambda mu : op.AND(mu.p4.Pt() > 10., op.abs(mu.p4.Eta()) < 2.4, mu.mediumId, mu.pfRelIso04_all<0.15))
        
        ## Electrons selection
        sorted_electrons=op.sort(t.Electron, lambda ele : -ele.p4.Pt())
        electrons = op.select(sorted_electrons, lambda ele : op.AND(ele.p4.Pt() > 15., op.abs(ele.p4.Eta()) < 2.5 , ele.cutBased>=3 )) 
            
        ## Opposite sign dilepton selection 
        osdilep_Z = lambda l1,l2 : op.AND(l1.charge != l2.charge, op.in_range(70., op.invariant_mass(l1.p4, l2.p4), 120.))
        leptonchannels = {
                "MuMu" : op.combine(muons, N=2, pred=osdilep_Z),
                "ElEl" : op.combine(electrons, N=2, pred=osdilep_Z),
                "ElMu" : op.combine((electrons, muons), pred=lambda ele,mu : op.AND(osdilep_Z(ele,mu), ele.p4.Pt() > mu.p4.Pt() )),
                "MuEl" : op.combine((muons, electrons), pred=lambda mu,ele : op.AND(osdilep_Z(mu,ele), mu.p4.Pt() > ele.p4.Pt()))
                }

        TwocombinedOSlepton = lambda combine_rng : op.AND(op.rng_len(combine_rng) > 0, combine_rng[0][0].p4.Pt() > 25.)  # lepton: pT[0]> 25 GeV , pT[1]>10 GeV
        hasOSdilepton = noSel.refine("hasOSLL", cut=op.OR(*( TwocombinedOSlepton(rng) for rng in leptonchannels.values())))


        ## Jets selection
        sorted_jets=op.sort(t.Jet, lambda j : -j.p4.Pt())
        jets = op.select(sorted_jets, lambda j : op.AND(j.p4.Pt() > 20., op.abs(j.p4.Eta())< 2.4, (j.jetId &2)))
        hastwojets= op.select(jets, lambda j : op.AND(op.NOT(op.rng_any(electrons, lambda ele : op.deltaR(j.p4, ele.p4) < 0.3 )), op.NOT(op.rng_any(muons, lambda mu : op.deltaR(j.p4, mu.p4) < 0.3 ))))

        
        
        hasTwoMuons = noSel.refine("hasTwoMu", cut=( op.AND( muons[0].p4.Pt() >20. , op.rng_len(muons) >= 2)))
        hasTwoElectrons = noSel.refine("hasTwoEl", cut=( op.AND( electrons[0].p4.Pt()> 25., op.rng_len(electrons) >= 2)))
        
        jet1_p4= jets[0].p4
        jet2_p4= jets[1].p4
        lep1_p4= 
        lep2_p4=
        lep1_charge=
        lep2_charge=

        ## Two OS Leptons _ Two Jets  selection
        lljj_M= (dilepton[0].p4 +dilepton[1].p4+jets[0].p4+jets[1].p4).M()
        jj_M=op.invariant_mass(jets[0].p4, jets[1].p4)

        ll_M=op.invariant_mass(dilepton[0].p4, dilepton[1].p4)

        llbb_M= (dilepton[0].p4 +dilepton[1].p4+bjets[tagger][0].p4+bjets[tagger][1].p4).M()
        bb_M=op.invariant_mass(bjets[tagger][0].p4+bjets[tagger][1].p4)

        met_pt=
        met_phi=
        
        sample_weight=
        event_weight=
        total_weight=
        cross_section=
    
        varsToKeep["nMuons"] = op.static_cast("UInt_t", op.rng_len(muons)) ## TBranch doesn't accept size_t
        varsToKeep["nElectrons"]= op.static_cast("UInt_t", op.rng_len(electrons)) 
        
        varsToKeep["nJets"] = op.static_cast("UInt_t", op.rng_len(jets)) 
        varsToKeep["jets_pt"] = op.map(jets, lambda j: j.pt)
        varsToKeep["jets_eta"] = op.map(jets, lambda j: j.eta)
        varsToKeep["nBJets_deepFlavM"] = op.static_cast("UInt_t", op.rng_len(bJets))
        varsToKeep["nBJets_deepCSVM"] = op.static_cast("UInt_t", op.rng_len(bJets))
                                  

        
        
        
        varsToKeep["lljj_M"] =


        varsToKeep["selMu_miniPFRelIsoNeu"] = op.map(muons, lambda mu : mu.miniPFRelIso_all - mu.miniPFRelIso_chg)
        return hasTwoMu, varsToKeep

