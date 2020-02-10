
from bamboo.plots import Plot, SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op

def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

def MakeControlPlotsForZpic(self, catSel, dilepton, channel):
    
    plots = []
    
    plots.append(Plot.make1D("{0}_leadleptonPT".format(channel), 
                dilepton[0].p4.Pt(), catSel, 
                EqB(100, 0., 450.), 
                title="Transverse momentum of the leading lepton", 
                xTitle= "P_{T} (leading lepton) [GeV]"))

    plots.append(Plot.make1D("{0}_SubleadleptonPT".format(channel), 
                dilepton[1].p4.Pt(), catSel, 
                EqB(100, 0., 450.), 
                title="Transverse momentum of the Subleading lepton", 
                xTitle= "P_{T} (sub-leading lepton) [GeV]"))

    plots.append(Plot.make1D("{0}_leadleptonETA".format(channel), 
                dilepton[0].p4.eta(), catSel, 
                EqB(10, -3, 3), 
                title="Pseudo-rapidity of the leading lepton", 
                xTitle= "Eta(leading lepton)"))
    
    plots.append(Plot.make1D("{0}_subleadleptonETA".format(channel), 
                dilepton[1].p4.eta(), catSel, 
                EqB(10, -3, 3), 
                title="Pseudo-rapidity of the sub-leading lepton", 
                xTitle= "Eta(Sub-leading lepton)"))
    
    plots.append(Plot.make1D("{0}_mll".format(channel), 
                op.invariant_mass(dilepton[0].p4, dilepton[1].p4), catSel, 
                EqB(100, 70., 110.), 
                title=" dilepton invariant mass", 
                xTitle= "mll [GeV]"))
    
    plots.append(Plot.make1D("{0}_llpT".format(channel), 
                (dilepton[0].p4 + dilepton[1].p4).Pt(), catSel, 
                EqB(100,0.,450.),
                title= "dilepton transverse momentum" , 
                xTitle= "dilepton P_{T} [GeV]"))
    
    #plots.append(Plot.make1D("{0}_nVX".format(channel), 
    #            t.PV.npvs, catSel, 
    #            EqB(10, 0., 60.), 
    #            title="Distrubtion of the number of the reconstructed vertices", 
    #            xTitle="number of reconstructed vertices "))
        
    #plots.append(Plot.make2D("{0}_Electron_dzdxy".format(channel), 
    #            (dilepton[0].dz ,dilepton[0].dxy), catSel, 
    #            (EqB(10, 0., 2.),
    #            EqB(10, 0., 2.)) ,
    #            title="Electron in Barrel/EndCAP region" ))
    
    return plots

##########

def MakeControlPlotsForBasicSel(self, TwoLeptonsTwoJets, jets, dilepton, channel):
    
    plots =[]
    
    plots.append(Plot.make1D("{0}_leadJetPT".format(channel), 
                jets[0].p4.Pt(), 
                TwoLeptonsTwoJets, 
                EqB(100, 0., 450.), 
                title="Transverse momentum of the leading jet P_{T}", 
                xTitle= "P_{T} (leading Jet) [GeV]"))
        
    plots.append(Plot.make1D("{0}_subleadJetPT".format(channel), 
                jets[1].p4.Pt(), 
                TwoLeptonsTwoJets,
                EqB(100, 0., 450.), 
                title="Transverse momentum of the sub-leading jet PT", 
                xTitle= "P_{T} (sub-leading Jet) [GeV]"))
        
    plots.append(Plot.make1D("{0}_leadJetETA".format(channel), 
                jets[0].p4.eta(), 
                TwoLeptonsTwoJets,
                EqB(10, -3, 3), 
                title="Pseudo-rapidity of the leading jet", 
                xTitle="Eta(leading Jet)"))
        
    plots.append(Plot.make1D("{0}_subleadJetETA".format(channel), 
                jets[1].p4.eta(), 
                TwoLeptonsTwoJets, 
                EqB(10, -3, 3), 
                title="Pseudo-rapidity of the sub-leading jet", 
                xTitle="Eta (sub-leading Jet)"))
        
    plots.append(Plot.make1D("{0}_jjpT".format(channel), 
                (jets[0].p4 + jets[1].p4).Pt(), 
                TwoLeptonsTwoJets, 
                EqB(100,0.,450.),
                title= "dijet transverse momentum" , 
                xTitle= "dijet P_{T} [GeV]"))
            
    plots.append(Plot.make1D("{0}_mjj".format(channel),
                op.invariant_mass(jets[0].p4, jets[1].p4) , 
                TwoLeptonsTwoJets, 
                EqB(100, 0., 800.), title="mjj", 
                xTitle= "mjj [GeV]"))
        
    plots.append(Plot.make1D("{0}_mlljj".format(channel), 
                (dilepton[0].p4 +dilepton[1].p4+jets[0].p4+jets[1].p4).M(), 
                TwoLeptonsTwoJets, 
                EqB(100, 0., 1000.), 
                title="mlljj", 
                xTitle="mlljj [GeV]"))
    
    plots.append(Plot.make2D("{0}_mlljjvsmjj".format(channel), 
                (op.invariant_mass(jets[0].p4, jets[1].p4),
                (dilepton[0].p4 + dilepton[1].p4 + jets[0].p4 + jets[1].p4).M()), 
                TwoLeptonsTwoJets, 
                (EqB(1000, 0., 1000.), 
                EqB(1000, 0., 1000.)), 
                title="mlljj vs mjj invariant mass"))
    return plots
            

#############

def DiscriminatorPlots(self, TwoLeptonsTwoBjets, bestJetPairs, channel, wp, isMC):

    plots =[]
    for key in TwoLeptonsTwoBjets.keys():
        
        tagger=key.replace(wp,"")

        if tagger == 'DeepCSV':
            discr_1stbest = bestJetPairs[tagger][0].btagDeepB
            discr_2ndbest = bestJetPairs[tagger][1].btagDeepB
            discr = 'btagDeepB'
        
        elif tagger=='DeepFlavour':
            discr_1stbest = bestJetPairs[tagger][0].btagDeepFlavB
            discr_2ndbest = bestJetPairs[tagger][1].btagDeepFlavB
            discr = 'btagDeepFlavB'
        else:
            raise RuntimeError("ERROR in getting TwoLeptonsTwoBjets keys !!" )
        
        
        plots.append(Plot.make1D("{0}_{1}{2}_Discriminator_leadingBJet".format(channel, discr, wp), 
                    discr_1stbest, 
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100, 0., 1.), 
                    title="{0} Discriminator ".format(key), 
                    xTitle="{0}{1} discriminant(leading bjet)".format(discr, wp)))
    
        plots.append(Plot.make1D("{0}_{1}{2}_Discriminator_subleadingBJet".format(channel, discr, wp), 
                    discr_2ndbest, 
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100, 0., 1.), 
                    title="{0} Discriminator".format(key), 
                    xTitle="{0}{1} discriminant (sub-leading bjet)".format(discr, wp)))
            
        plots.append(Plot.make2D("{0}_1st_vs_2nd_leadingBJet_discriminant_{1}{2}".format(channel, discr, wp),
                    (discr_1stbest, discr_2ndbest),
                    TwoLeptonsTwoBjets.get(key), 
                    (EqB(100, 0., 1.), EqB(100, 0., 1.)),
                    title="{0}{1} discriminant 1st vs 2nd leading bjets".format(discr, wp)))
        
        if isMC:

            sel_leadingB = TwoLeptonsTwoBjets.get(key).refine(..., cut=(bestJetPairs[tagger][0].hadronFlavour == 5))
            sel_leadingC = TwoLeptonsTwoBjets.get(key).refine(..., cut=(bestJetPairs[tagger][0].hadronFlavour == 4))
            sel_leadingLight = TwoLeptonsTwoBjets.get(key).refine(..., cut=(bestJetPairs[tagger][0].hadronFlavour == 0))


            hadronFlavour_leading = bestJetPairs[tagger][0].hadronFlavour if isMC else op.c_int(9)


            bFlav_LeadingJets= op.select(bestJetPairs[tagger][0], lambda j: j.hadronFlavour == 5)
            cFlav_LeadingJets = op.select(bestJetPairs[tagger][0], lambda j: j.hadronFlavour == 4)
            lFlav_LeadingJets = op.select(bestJetPairs[tagger][0], lambda j: j.hadronFlavour == 0)
            
            Pass_bFlav0 = (Plot.make1D("{0}_{1}_{2}_bFlav_taggedb_0".format(channel, discr, wp),
                                    bFlav_LeadingJets,
                                    TwoLeptonsTwoBjets.get(key),
                                    EqB(100, 0., 1.),
                                    title="Pass bFlav",
                                    xTitle="Pass bFlav"))
            
            Pass_cFlav0 = (Plot.make1D("{0}_{1}_{2}_cFlav_mistagged_bFlav_0".format(channel, discr, wp),
                                    cFlav_LeadingJets,
                                    TwoLeptonsTwoBjets.get(key),
                                    EqB(100, 0., 1.),
                                    title="Pass cFlav",
                                    xTitle="Pass cFlav"))
            
            Pass_lFlav0 = (Plot.make1D("{0}_{1}_{2}_lFlav_mistagged_bFlav_0".format(channel, discr, wp),
                                    lFlav_LeadingJets,
                                    TwoLeptonsTwoBjets.get(key),
                                    EqB(100, 0., 1.),
                                    title="Pass lFlav",
                                    xTitle="Pass lFlav"))
            
            plots.append(SummedPlot("{0}_Discriminator_splitbyJetsFlavour_leadingBJets{1}".format(channel, key),
                        [Pass_bFlav0, Pass_cFlav0, Pass_lFlav0],
                        xTitle="Discriminator {0}".format(key)))
            
            bFlav_SubLeadingJets= op.select(bestJetPairs[tagger][1], lambda j: j.hadronFlavour == 5)   # b
            cFlav_SubLeadingJets = op.select(bestJetPairs[tagger][1], lambda j: j.hadronFlavour == 4)  # c
            lFlav_SubLeadingJets = op.select(bestJetPairs[tagger][1], lambda j: j.hadronFlavour == 0)  # udsg
            
            Pass_bFlav1 = (Plot.make1D("{0}_{1}_{2}_bFlav_taggedb_1".format(channel, discr, wp),
                                    bFlav_SubLeadingJets,
                                    TwoLeptonsTwoBjets.get(key),
                                    EqB(100, 0., 1.),
                                    title="Pass bFlav",
                                    xTitle="Pass bFlav"))
            
            Pass_cFlav1 = (Plot.make1D("{0}_{1}_{2}_cFlav_mistagged_bFlav_1".format(channel, discr, wp),
                                    cFlav_SubLeadingJets,
                                    TwoLeptonsTwoBjets.get(key),
                                    EqB(100, 0., 1.),
                                    title="Pass cFlav",
                                    xTitle="Pass cFlav"))
            
            Pass_lFlav1 = (Plot.make1D("{0}_{1}_{2}_lFlav_mistagged_bFlav_1".format(channel, discr, wp),
                                    lFlav_SubLeadingJets,
                                    TwoLeptonsTwoBjets.get(key),
                                    EqB(100, 0., 1.),
                                    title="Pass lFlav",
                                    xTitle="Pass lFlav"))
        
            plots.append(SummedPlot("{0}_Discriminator_splitbyJetsFlavour_subleadingBJets{1}".format(channel, key),
                        [Pass_bFlav1, Pass_cFlav1, Pass_lFlav1],
                        xTitle="Discriminator {0}".format(key)))
        
    return plots


##################
# No discriminator requirement for the jets 
def MakeControlPlotsForBjetsSel(self, TwoLeptonsTwoBjets, bjets, dilepton, channel, wp):

    plots =[]
    for key in TwoLeptonsTwoBjets.keys():
        
        tagger=key.replace(wp, "")
        bjets_ = safeget(bjets, tagger, wp) 
        # b-jets pT 
        plots.append(Plot.make1D("{0}_lead_BJetPT_{1}".format(channel,key), 
                    bjets_[0].p4.Pt(),
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100, 0., 450.), 
                    title="Transverse momentum of the leading bjet P_{T}", 
                    xTitle= "P_{T} (leading b-Jet) [GeV]"))

        plots.append(Plot.make1D("{0}_sublead_BJetPT_{1}".format(channel, key), 
                    bjets_[1].p4.Pt(),
                    TwoLeptonsTwoBjets.get(key),
                    EqB(100, 0., 450.), 
                    title="Transverse momentum of the sub-leading bjet P_{T}", 
                    xTitle= "P_{T}(Sub-leading b-Jet) [GeV]"))
        
        # pseudo-rapidity 
        plots.append(Plot.make1D("{0}_lead_BJetETA_{1}".format(channel, key), 
                    bjets_[0].p4.eta(),
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(10, -3, 3), 
                    title="Pseudo-rapidity of the leading b-Jet", 
                    xTitle="Eta (Leading b-Jet"))

        plots.append(Plot.make1D("{0}_sublead_BJetETA_{1}".format(channel, key), 
                    bjets_[1].p4.eta(),
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(10, -3, 3), 
                    title="Pseudo-rapidity of the sub-leading b-Jet", 
                    xTitle="Eta (Sub-Leading b-Jet)"))
        # dijet pT     
        plots.append(Plot.make1D("{0}_twoBtaggedjetspT_{1}".format(channel, key), 
                    (bjets_[0].p4+bjets_[1].p4).Pt(),
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100,0.,450.),
                    title= "di-bjet transverse momentum" , 
                    xTitle= "di-bjet P_{T} [GeV]"))
        
        # number of bjets passing my selection: just for debugging should be >=2
        plots.append(Plot.make1D("{0}_nBJets_{1}".format(channel, key), 
                    op.rng_len(bjets_),
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(5, 2., 6.), 
                    title="Number of bjets", 
                    xTitle= "nbr b-Jets"))

        # llbb invariant mass distribution 
        plots.append(Plot.make1D("{0}_mlljj_btagged_{1}".format(channel, key), 
                    (dilepton[0].p4 +dilepton[1].p4+bjets_[0].p4+bjets_[1].p4).M(),
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100, 0., 1000.), 
                    title="Invariant mass of two leptons two b-tagged jets", 
                    xTitle="mlljj [GeV]"))
        
        # di-bjet invariant mass 
        plots.append(Plot.make1D("{0}_mjj_btagged_{1}".format(channel, key),
                    op.invariant_mass(bjets_[0].p4+bjets_[1].p4) , 
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100, 0., 800.), 
                    title="Invariant mass distribution of two b-tagged jets", 
                    xTitle= "mjj [GeV]"))

        # mllbb vs mbb distribution in 2D plane 
        plots.append(Plot.make2D("{0}_mlljjvsmjj_btagged_{1}".format(channel, key), 
                    (op.invariant_mass(bjets_[0].p4+bjets_[1].p4) , 
                    (dilepton[0].p4 +dilepton[1].p4+bjets_[0].p4+bjets_[1].p4).M()),
                    TwoLeptonsTwoBjets.get(key), 
                    (EqB(1000, 0., 1000.), 
                    EqB(1000, 0., 1000.)), 
                    title="mlljj vs mjj invariant mass"))
    return plots
# for better selection of b jets 
# and to remove fakes b from my selection I should take into account only the jet with the highest discriminator !

def MakeControlPlotsForBestBJetsPair(self, TwoLeptonsTwoBjets, bestJetPairs, dilepton, channel, wp):

    plots =[]
    for key in TwoLeptonsTwoBjets.keys():
        tagger= key.replace(wp, "")
        
        plots.append(Plot.make1D("{0}_Jet_leading_pT_wrt_{1}_Discriminator".format(channel, key), 
                    bestJetPairs[tagger][0].p4.Pt(), 
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100, 0., 450.), 
                    title="pT(leading Jet) wrt {0} discriminator [GeV]".format(key), 
                    xTitle= "pT(leading Jet) wrt {0} discriminator [GeV]".format(key)))
                
        plots.append(Plot.make1D("{0}_Jet_Sub_leading_pT_wrt_{1}_Discriminator".format(channel, key), 
                    bestJetPairs[tagger][1].p4.Pt(), 
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100, 0., 450.), 
                    title=" pT(sub-leading Jet) wrt {0} discriminator [GeV]".format(key), 
                    xTitle= "pT(Sub-leading Jet) wrt {0} discriminator [GeV]".format(key)))

        plots.append(Plot.make1D("{0}_Jet_leading_Eta_wrt_{1}_Discriminator".format(channel, key), 
                    bestJetPairs[tagger][0].p4.eta(), 
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(10, -3., 3), 
                    title="Pseudo-rapidity (Leading Jet) wrt {0} discriminator".format(key), 
                    xTitle= "Eta (Leading Jet) wrt {0} discriminator".format(key)))
        
        plots.append(Plot.make1D("{0}_Jet_Sub_leading_Eta_wrt_{1}_Discriminator".format(channel, key), 
                    bestJetPairs[tagger][1].p4.eta(), 
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(10, -3., 3.), 
                    title="Pseudo-rapidity (sub-eading Jet) wrt {0} discriminator".format(key), 
                    xTitle= "Eta (Sub-Leading Jet) wrt {0} discriminator".format(key)))
        
        plots.append(Plot.make1D("{0}_twoBtaggedjetspT_wrt_{1}_Discriminator".format(channel, key), 
                    (bestJetPairs[tagger][0].p4+bestJetPairs[tagger][1].p4).Pt(),
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100,0.,450.),
                    title= "di-bjet transverse momentum wrt {0} Discriminator".format(key) , 
                    xTitle= "di-bjet pT wrt {0} Discriminator [GeV]".format(key)))
        
        plots.append(Plot.make1D("{0}_llpT_{1}".format(channel, key), 
                    (dilepton[0].p4 + dilepton[1].p4).Pt(), 
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100,0.,450.),
                    title= "dilepton transverse momentum in btagging selection" , 
                    xTitle= "dilepton P_{T} [GeV]"))

        plots.append(Plot.make1D("{0}_mll_btagged_{1}".format(channel, key), 
                    op.invariant_mass(dilepton[0].p4, dilepton[1].p4), 
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100, 70., 110.), 
                    title=" Dilepton invariant mass distribution", 
                    xTitle= "mll [GeV]"))

        plots.append(Plot.make1D("{0}_mjj_btagged_wrt_{1}_Discriminator".format(channel, key),
                    op.invariant_mass(bestJetPairs[tagger][0].p4 + bestJetPairs[tagger][1].p4) , 
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100, 0., 800.), 
                    title="Invariant mass distribution of two b-tagged jets wrt {0} Discriminator".format(key), 
                    xTitle= "mjj wrt {0} Discriminator [GeV]".format(key)))

        plots.append(Plot.make1D("{0}_mlljj_btagged_wrt_{1}_Discriminator".format(channel, key), 
                    (dilepton[0].p4 + dilepton[1].p4 + bestJetPairs[tagger][0].p4 + bestJetPairs[tagger][1].p4).M(),
                    TwoLeptonsTwoBjets.get(key), 
                    EqB(100, 0., 1000.), 
                    title="Invariant mass of 2 leptons two b-tagged jets  wrt {0} Discriminator".format(key), 
                    xTitle="mlljj wrt {0} Discriminator [GeV]".format(key)))

        plots.append(Plot.make2D("{0}_mlljjvsmjj_btagged_wrt_{1}_Discriminator".format(channel, key), 
                    (op.invariant_mass(bestJetPairs[tagger][0].p4 + bestJetPairs[tagger][1].p4) , 
                    (dilepton[0].p4 + dilepton[1].p4 + bestJetPairs[tagger][0].p4 + bestJetPairs[tagger][1].p4).M()),
                    TwoLeptonsTwoBjets.get(key), 
                    (EqB(1000, 0., 1000.), 
                    EqB(1000, 0., 1000.)), 
                    title="mlljj vs mjj invariant mass wrt {0} Discriminator".format(key)))
                
        return plots
