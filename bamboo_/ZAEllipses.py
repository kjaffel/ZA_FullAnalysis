from bamboo.plots import Plot, SummedPlot 
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op

def MakeEllipsesPlots(self, TwoLeptonsTwoBjets, bestJetPairs, dilepton, channel, wp):
    plots = []
    
    for tagger in TwoLeptonsTwoBjets.keys():
    
        tagger = key.replace(wp, "")     

        plots.append(Plot.make1D("jj_M_{0}_hZA_lljj_{1}_btag{2}_mll_and_met_cut".format(channel, tagger, wp),
                    op.invariant_mass(bestJetPairs[tagger][0].p4, bestJetPairs[tagger][1].p4) , 
                    TwoLeptonsTwoBjets.get(tagger), 
                    EqB(100, 0., 1000.), 
                    title="invariant mass of two b-tagged jets wrt {0} Discriminator".format(key), 
                    xTitle= "mjj wrt {0} Discriminator [GeV]".format(key)))
        
        plots.append(Plot.make1D("lljj_M_{0}_hZA_lljj_{1}_btag{2}_mll_and_met_cut".format(channel, tagger, wp), 
                    (dilepton[0].p4 +dilepton[1].p4+bestJetPairs[tagger][0].p4+bestJetPairs[tagger][1].p4).M(),
                    TwoLeptonsTwoBjets.get(tagger), 
                    EqB(100, 0., 1000.), 
                    title="invariant mass of 2 leptons two b-tagged jets wrt {0} Discriminator".format(key), 
                    xTitle="mlljj wrt {0} Discriminator [GeV]".format(key)))
        
        plots.append(Plot.make2D("Mjj_vs_Mlljj_{0}_hZA_lljj_{1}_btag{2}_mll_and_met_cut".format(channel, tagger, wp), 
                    (op.invariant_mass(bestJetPairs[tagger][0].p4, bestJetPairs[tagger][1].p4),(
                    dilepton[0].p4 +dilepton[1].p4+bestJetPairs[tagger][0].p4+bestJetPairs[tagger][1].p4).M()),
                    TwoLeptonsTwoBjets.get(tagger), 
                    (EqB(100, 0., 1000.), 
                    EqB(100, 0., 1000.)), 
                    title="mlljj vs mjj invariant mass wrt {0} Discriminator".format(key)))
                
        plots.append(Plot.make1D("ll_M_{0}_hZA_lljj_{1}_btag{2}_mll_and_met_cut".format(channel, tagger, wp), 
                    op.invariant_mass(dilepton[0].p4, dilepton[1].p4), 
                    TwoLeptonsTwoBjets.get(tagger), 
                    EqB(100, 70., 110.), 
                    title=" dilepton invariant mass wrt {0} Discriminator".format(key), 
                    xTitle= "mll wrt {0} Discriminator [GeV]".format(key)))
    return plots

def MakeMETPlots(self, TwoLeptonsTwoBjets_NoMETCut, corrMET, MET, channel):
    plots = []

    for tagger in TwoLeptonsTwoBjets_NoMETCut.keys():

        plots.append(Plot.make1D("met_pt_{0}_hZA_lljj_btag_{1}".format(channel, tagger), 
                    MET.pt, 
                    TwoLeptonsTwoBjets_NoMETCut.get(tagger), 
                    EqB(50, 0., 400.), 
                    title=" Missing Transverse Energy", 
                    xTitle= "MET p_{T} [GeV]"))
                
        plots.append(Plot.make1D("xycorrmet_pt_{0}_hZA_lljj_btag_{1}".format(channel, tagger), 
                    corrMET.pt, 
                    TwoLeptonsTwoBjets_NoMETCut.get(tagger), 
                    EqB(50, 0., 400.), 
                    title=" x-y correction on Missing Transverse Energy", 
                    xTitle= "corrMET p_{T} [GeV]"))
    return plots
