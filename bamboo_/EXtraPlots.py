import sys
import os
from bambooToOls import Plot
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_')
import utils

class makeYieldPlots:
    def __init__(self):
        self.calls = 0
        self.plots = []
    def addYields(self, cut, sel, name, title):
        """
            Make Yield plot and use it also in the latex yield table
            sel     = refine selection
            name    = name of the PDF to be produced
            title   = title that will be used in the LateX yield table
        """
        self.plots.append(Plot.make1D("Yield_"+name,   
                        cut,
                        sel,
                        EqB(2, 0., 2.),
                        title = title + " Yield",
                        plotopts = {"for-yields":True, "yields-title":title, 'yields-table-order':self.calls}))
        self.calls += 1
    def returnPlots(self):
        return self.plots

def MakeTriggerDecisionPlots(catSel, channel):
    """
        I should enable the cut above on the triggersPerPrimaryDataset.values() when passing maketriggerdecision func 
        noSel = noSel.refine("genWeight", weight=tree.genWeight, cut=op.OR(*chain.from_iterable(triggersPerPrimaryDataset.values())), autoSyst=self.doSysts)
    """
    plots=[]
    SingleLeptonsTriggers = {
            "SingleElectron": [ t.HLT.Ele25_eta2p1_WPTight_Gsf, t.HLT.Ele27_WPTight_Gsf, t.HLT.Ele27_eta2p1_WPLoose_Gsf, t.HLT.Ele32_eta2p1_WPTight_Gsf],
            "SingleMuon"    : [t.HLT.IsoMu20, t.HLT.IsoTkMu20, t.HLT.IsoMu22, t.HLT.IsoTkMu22, t.HLT.IsoMu24, t.HLT.IsoTkMu24]
            }
    DoubleLeptonsTriggers = {
            "mumu"  : [ t.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL, t.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ, t.HLT.Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL, t.HLT.Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ ],
            "elel"  : [ t.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ ],
            "mixed" : [t.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL, t.HLT.Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, t.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ, t.HLT.Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL]
            }

    passSingleLepton = Plot.make1D("OSll_HLTSingleLeptonDecision_{0}".format(channel), 
                                op.OR(*chain.from_iterable(SingleLeptonsTriggers.values())), 
                                catSel, EqB(2, 0., 2.), title="Single lepton trigger decision", plotopts=utils.getOpts(channel))
    passDiLepton = Plot.make1D("OSll_HLTDiLeptonDecision_{0}".format(channel), 
                                op.OR(*chain.from_iterable(DoubleLeptonsTriggers.values())), 
                                catSel, EqB(2, 0., 2.), title="Dilepton trigger decision", plotopts=utils.getOpts(channel))
    passboth = Plot.make1D("OSll_HLTDiLeptonANDSiLeptonDecision_{0}".format(channel), 
                                op.OR(*chain.from_iterable(DoubleLeptonsTriggers.values())), 
                                catSel, EqB(2, 0., 2.), title="Dilepton && Single Lepton trigger decision", plotopts=utils.getOpts(channel))
    
    optstex = ('$e^+e^-$' if channel=="ElEl" else( '$\mu^+\mu^-$' if channel =="MuMu" else( '$\mu^+e^-$' if channel=="MuEl" else('$e^+\mu^-$'))))
    
    yield_object.addYields(op.OR(*chain.from_iterable(SingleLeptonsTriggers.values())), catSel,"OS_%s_HLT_SLDesc"%channel,"Single lepton trigger decision")
    yield_object.addYields(op.OR(*chain.from_iterable(DoubleLeptonsTriggers.values())), catSel,"OS_%s_HLT_DLDesc"%channel,"Dilepton trigger decision")
    yield_object.addYields(op.OR(*chain.from_iterable(DoubleLeptonsTriggers.values())), catSel,"OS_%s_HLT_SLandDLDesc"%channel,"Dilepton && Single Lepton trigger decision")
    
    #plots.append(passSingleLepton)
    #plots.append(passDiLepton)
    #plots.append(passboth)
    return plots

# for better selection of b jets 
# and to remove fakes b from my selection I should take into account only the jet with the highest discriminator !
def MakeBestBJetsPairPlots(self, sel, bestJetPairs, dilepton, suffix, wp):
    plots =[]
    for key in sel.keys():
        tagger= key.replace(wp, "")
        
        plots.append(Plot.make1D("{0}_Jet_leading_pT_wrt_{1}_Discriminator".format(suffix, key), 
                    bestJetPairs[tagger][0].pt, 
                    sel.get(key), 
                    EqB(100, 0., 450.), 
                    title="pT(leading Jet) wrt {0} discriminator [GeV]".format(key), 
                    xTitle= "pT(leading Jet) wrt {0} discriminator [GeV]".format(key)))
                
        plots.append(Plot.make1D("{0}_Jet_Sub_leading_pT_wrt_{1}_Discriminator".format(suffix, key), 
                    bestJetPairs[tagger][1].pt, 
                    sel.get(key), 
                    EqB(100, 0., 450.), 
                    title=" pT(sub-leading Jet) wrt {0} discriminator [GeV]".format(key), 
                    xTitle= "pT(sub-leading Jet) wrt {0} discriminator [GeV]".format(key)))

        plots.append(Plot.make1D("{0}_Jet_leading_Eta_wrt_{1}_Discriminator".format(suffix, key), 
                    bestJetPairs[tagger][0].eta, 
                    sel.get(key), 
                    EqB(10, -3., 3), 
                    title="Pseudo-rapidity (Leading Jet) wrt {0} discriminator".format(key), 
                    xTitle= "Eta (leading Jet) wrt {0} discriminator".format(key)))
        
        plots.append(Plot.make1D("{0}_Jet_Sub_leading_Eta_wrt_{1}_Discriminator".format(suffix, key), 
                    bestJetPairs[tagger][1].eta, 
                    sel.get(key), 
                    EqB(10, -3., 3.), 
                    title="Pseudo-rapidity (sub-eading Jet) wrt {0} discriminator".format(key), 
                    xTitle= "Eta (sub-leading Jet) wrt {0} discriminator".format(key)))
        
        plots.append(Plot.make1D("{0}_twoBtaggedjetspT_wrt_{1}_Discriminator".format(suffix, key), 
                    (bestJetPairs[tagger][0].p4+bestJetPairs[tagger][1].p4).Pt(),
                    sel.get(key), 
                    EqB(100,0.,450.),
                    title= "di-bjet transverse momentum wrt {0} Discriminator".format(key) , 
                    xTitle= "di-bjet pT wrt {0} Discriminator [GeV]".format(key)))
        
        plots.append(Plot.make1D("{0}_llpT_{1}".format(suffix, key), 
                    (dilepton[0].p4 + dilepton[1].p4).Pt(), 
                    sel.get(key), 
                    EqB(100,0.,450.),
                    title= "dilepton transverse momentum in btagging selection" , 
                    xTitle= "dilepton P_{T} [GeV]"))
    return plots

def MakeHadronFlavourPLots(self, sel, bestJetPairs, uname, wp, isMC):
    plots =[]
    # FIXME
    for key in sel.keys():
        tagger=key.replace(wp,"")
        hadronFlavour_leading = bestJetPairs[tagger][0].hadronFlavour if isMC else op.c_int(6)
        hadronFlavour_subleading = bestJetPairs[tagger][1].hadronFlavour if isMC else op.c_int(6)

        Pass_bFlav0 = Plot.make1D("{0}_{1}_{2}_bFlav_tagged_bFlav".format(uname, discr, wp),
                                hadronFlavour_leading,
                                sel.get(key).refine("{0}_{1}_{2}_bFlav_tagged_bFlav".format(uname, discr, wp), cut=((bestJetPairs[tagger][0].hadronFlavour == 5) if isMC else None)),
                                EqB(10, 0., 10.),
                                title="mistagged heavy flavour jets pass {0}".format(key))
        
        Pass_cFlav0 = Plot.make1D("{0}_{1}_{2}_cFlav_tagged_bFlav".format(uname, discr, wp),
                                hadronFlavour_leading,
                                sel.get(key).refine("{0}_{1}_{2}_cFlav_mistagged_bFlav".format(uname, discr, wp), cut=((bestJetPairs[tagger][0].hadronFlavour == 4)if isMC else None)),
                                EqB(10, 0., 10.),
                                title="mistagged heavy flavour jets pass {0}".format(key))
        
        Pass_lFlav0 = Plot.make1D("{0}_{1}_{2}_lFlav_mistagged_bFlav".format(uname, discr, wp),
                                hadronFlavour_leading,
                                sel.get(key).refine("{0}_{1}_{2}_lFlav_mistagged_bFlav".format(uname, discr, wp), cut=((bestJetPairs[tagger][0].hadronFlavour == 0)if isMC else None)),
                                EqB(10, 0., 10.),
                                title="mistagged heavy flavour jets pass {0}".format(key))
        
            
        plots.append(SummedPlot("{0}_Discriminator_splitbyJetsFlavour_leadingBJets{1}".format(uname, key),
                    [Pass_bFlav0, Pass_cFlav0, Pass_lFlav0],
                    title="{0}".format(key), plotopts=utils.getOpts(uname)))
        return plots
