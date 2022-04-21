from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo.root import gbl
from bamboo import treefunctions as op

import utils
import corrections as corr
import ControlPLots as cp
from bambooToOls import Plot

def makerhoPlots(selections, bjets, leptons, ellipses, ellipse_params, reg, cut, WP, uname, doblinded, process):
    plots = []
    plotOptions = utils.getOpts(uname, **{"log-y": True})
    if doblinded:
        plotOptions["blinded-range"] = [0., 1.5]
    
    for key, sel in selections.items():
        tagger = key.replace(WP, "")
        bjets_ = bjets[key.replace(WP, "")][WP]
        
        bb_p4  = (bjets_[0].p4+bjets_[1].p4) if reg=="resolved" else(bjets_[0].p4)
        bb_M   = bb_p4.M()
        llbb_M = (leptons[0].p4 +leptons[1].p4+bb_p4).M()
        
        for j, line in enumerate(ellipse_params, 0): 
            MH = str(line[-1]).replace('.', 'p')
            MA = str(line[-2]).replace('.', 'p')
            plots.append(Plot.make1D(f"rho_steps_{uname}_{reg}_{tagger}{WP}_{cut}_{process}_MH_{MH}_MA_{MA}",
                            ellipses.at(op.c_int(j)).radius(bb_M, llbb_M),
                            sel, EqB(6, 0., 3.), title="rho ",
                            plotopts= plotOptions))
    return plots

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

def zoomplots(oslepsel, oslep_plus2jet_sel, leptons, jets, suffix, uname):
    plots = []
    binScaling=1
    Jets_ = (jets[0].p4 if suffix=="boosted" else(jets[0].p4+jets[1].p4))
    for i in range(2):
        leptonptCut = (25. if i == 0 else( 10. if uname[-1]=='u' else( 15.)))
        plots.append(Plot.make1D(f"{uname}_lep{i+1}_zoom_pt", leptons[i].pt, oslepsel,
                EqB(60 // binScaling, leptonptCut, 60.), title=f"{utils.getCounter(i+1)} Lepton pT [GeV]" ,
                plotopts=utils.getOpts(uname, **{"log-y": False})))
    
    plots.append(Plot.make1D(f"{uname}_zoom_llpT", (leptons[0].p4 + leptons[1].p4).Pt(), oslepsel, 
            EqB(60, 0., 60.), title= "dilepton P_{T} [GeV]", 
            plotopts=utils.getOpts(uname, **{"log-y": False})))
        
    plots.append(Plot.make1D("{0}_{1}_zoom_mjj".format(uname, suffix),
                op.invariant_mass(Jets_), oslep_plus2jet_sel,
                EqB(60 // binScaling, 0., 60.), 
                title="mjj [GeV]", plotopts=utils.getOpts(uname, **{"log-y": False})))
    
    EqBIns = EqB(60 // binScaling, 120., 200.)
    plots.append(Plot.make1D("{0}_{1}_zoom_mlljj".format(uname, suffix), 
                (leptons[0].p4 +leptons[1].p4+Jets_).M(), oslep_plus2jet_sel, EqBIns, 
                title="mlljj [GeV]", plotopts=utils.getOpts(uname, **{"log-y": False})))
    
    return plots

def ptcuteffectOnJetsmultiplicty(TwoLepsel, leptons, jets_noptcut, jet_ptcut, corrMET, era, uname):
    plots = []
    binScaling=1
    for i in range(2):
        
        leptonptCut = (25. if i == 0 else( 10. if uname[-1]=='u' else( 15. if uname[-1]=='l' else(0.)))) 
        
        for idx, jets in enumerate([jets_noptcut, jet_ptcut]):
            
            j= ('noptcut' if idx ==0 else('ptcut'))
            jetcut =(0. if idx ==0 else (30.))
            EqBin= EqB(60 // binScaling, jetcut, 200.)
            
            sel_noMETcut = TwoLepsel.refine( '2lep_%s_jets_%s_noMETcut_plus_cut_on_jets_length_sup_%s'%(uname.lower(), j, i), cut = [op.rng_len(jets) > i ])
            sel_METcut = sel_noMETcut.refine( '2lep_%s_jets_%s_METcut_plus_cut_on_jets_length_sup_%s'%(uname.lower(), j, i), cut = [corrMET.pt < 80.])
            
            for sel, suffix in zip( [sel_noMETcut, sel_METcut ],['%s_noMETcut'%(j),'%s_METcut'%(j)]):
            
                plots.append(Plot.make1D(f"{uname}_resolved_jet{i+1}_{suffix}_pT".format(suffix=suffix), jets[i].pt, sel,
                            EqBin, title=f"{utils.getCounter(i+1)} jet p_{{T}} [GeV]",
                            plotopts=utils.getOpts(uname, **{"log-y": True})))
                plots.append(Plot.make1D(f"{uname}_resolved_jet{i+1}_{suffix}_eta".format(suffix=suffix), jets[i].eta, sel,
                            EqB(50 // binScaling, -2.5, 2.5), title=f"{utils.getCounter(i+1)} jet eta",
                            plotopts=utils.getOpts(uname)))
                plots.append(Plot.make1D(f"{uname}_resolved_jet{i+1}_{suffix}_phi".format(suffix=suffix), jets[i].phi, sel,
                            EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} jet #phi", plotopts=utils.getOpts(uname)))
                plots.append(Plot.make1D(f"{uname}_resolved_{suffix}_lenOnjets_sup{i}_Jet_mulmtiplicity".format(suffix=suffix, i=i), op.rng_len(jets), sel,
                            EqB(7, 0., 7.), title="Jet mulmtiplicity",
                            plotopts=utils.getOpts(uname, **{"log-y": True})))

            
                plots.append(Plot.make1D(f"{uname}_%s_lep{i+1}_pt"%suffix, leptons[i].pt, sel,
                        EqB(60 // binScaling, leptonptCut, 200.), title=f"{utils.getCounter(i+1)} Lepton pT [GeV]" ,
                        plotopts=utils.getOpts(uname, **{"log-y": True})))
                plots.append(Plot.make1D(f"{uname}_%s_lep{i+1}_eta"%suffix, leptons[i].eta, sel,
                        EqB(50 // binScaling, -2.5, 2.5), title=f"{utils.getCounter(i+1)} Lepton eta",
                        plotopts=utils.getOpts(uname, **{"log-y": True})))
                plots.append(Plot.make1D(f"{uname}_%s_lep{i+1}_phi"%suffix, leptons[i].phi, sel,
                        EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} Lepton #phi",
                        plotopts=utils.getOpts(uname, **{"log-y": True}))) 
            
                #plots.append(Plot.make1D(f"{uname}_%s_llpT"%suffix, (leptons[0].p4 + leptons[1].p4).Pt(), sel, 
                #        EqB(60, 0., 200.), title= "dilepton P_{T} [GeV]", 
                #        plotopts=utils.getOpts(uname, **{"log-y": True})))
                    
                #plots.append(Plot.make1D(f"{uname}_%s_mll"%suffix, op.invariant_mass(leptons[0].p4, leptons[1].p4), sel, 
                #        EqB(60, 70., 120.), title= "mll [GeV]", 
                #        plotopts=utils.getOpts(uname, **{"log-y": True})))
            
    return plots


def perCatPlots_sameVar(uName, categories, variable, binning, saveSeparate=True, combPrefix=None, nDim=1, **kwargs):
    plotFun = getattr(Plot, "make{0:d}D".format(nDim))
    catPlots = [ plotFun("_".join((catSel.name, uName)), variable, catSel, binning, **kwargs) for catSel in categories.values() ]
    combPlot = SummedPlot(("_".join((combPrefix, uName)) if combPrefix is not None else uName), catPlots)
    if saveSeparate:
        return catPlots + [ combPlot ]
    else:
        return [ combPlot ]


def leptonPlots_candVar(flavour, uName, categories, varFun, binning, saveSeparate=False, saveIntermediate=True, saveTotal=False, combPrefix=None, **kwargs):
    allPlots = []
    intCombPlots = []
    for i in range(2):
        catPlots = [ Plot.make1D("_".join((catSel.name, flavour, str(i), uName)), varFun(cand[i]), catSel, binning, **kwargs) for catName, (catSel, cand) in categories.items() if catName[2*i:2*(i+1)] == flavour ]
        intCombPlots.append(SummedPlot(("_".join((combPrefix, flavour, str(i), uName)) if combPrefix is not None else "_".join((uName, str(i), flavour))), catPlots))
        allPlots += catPlots
        toSave = []
    if saveSeparate:
        toSave += allPlots
    if saveIntermediate:
        toSave += intCombPlots
    if saveTotal:
        toSave.append(SummedPlot(("_".join((combPrefix, flavour, uName)) if combPrefix is not None else "_".join((uName, flavour))), allPlots))
    return toSave


def choosebest_jetid_puid(t, muons, electrons, osllSelCand, year, sample, isMC):
    plots = []
    binScaling = 1
    # look at PUID for 2017
    sorted_AK4jets=op.sort(t.Jet, lambda j : -j.pt)
    all_clean_jets = op.select(sorted_AK4jets, lambda j : op.AND(
        op.NOT(op.rng_any(muons, lambda l : op.deltaR(l.p4, j.p4) < 0.4)),
        op.NOT(op.rng_any(electrons, lambda l : op.deltaR(l.p4, j.p4) < 0.4))
        ))
    jet_sel_kin = {
        #"PT20"      : lambda j : j.pt > 20.,
        #"PT30"      : lambda j : j.pt > 30.,
        #"CentrPT20" : lambda j : op.AND(op.abs(j.eta) < 2.4, j.pt > 20.),
        "CentrPT30" : lambda j : op.AND(op.abs(j.eta) < 2.4, j.pt > 30.)
        }
    jet_collections_id2017_beforeClean = {
        "T"        : op.select(all_clean_jets, lambda j : j.jetId & 0x2),
        "TLepVeto" : op.select(all_clean_jets, lambda j : j.jetId & 0x4),
        }
    jet_puID_wp = {
        "L"   : lambda j : j.puId & 0x4,
        "M"   : lambda j : j.puId & 0x2,
        "T"   : lambda j : j.puId & 0x1
        }
    for jet_id, jets_noKin in jet_collections_id2017_beforeClean.items():
        jets_kin = { kinNm : op.select(jets_noKin, kinSel) for kinNm, kinSel in jet_sel_kin.items() }
        for puWP, puSel in jet_puID_wp.items():
            w_noKin = None
            if isMC:
                w_noKin = corr.makePUIDSF(jets_noKin, year=year, wp=puWP, wpToCut=jet_puID_wp)
            
            OsLepplus_allJets_noKinematics = dict((catName, catSel.refine(f"OsLeptonsPlusJets_withonly_jId{jet_id}_puId{puWP}_cuts_{catName}", weight=w_noKin))
                for catName, (cand, catSel) in osllSelCand.items())
            
            for kinNm, kinSel in jet_sel_kin.items():
                w_pu = None
                ak4jets_corr = op.select(jets_kin[kinNm], lambda j :  op.switch(j.pt < 50, puSel(j), op.c_bool(True)))
                #ak4jets_corr = op.select(jets_kin[kinNm], lambda j : op.OR(j.pt < 50, puSel(j)))
                
                if isMC:
                    w_pu = corr.makePUIDSF(ak4jets_corr, year=year, wp=puWP, wpToCut=jet_puID_wp)
                
                ## selections
                OsLepplus_allJets = dict((catName, catSel.refine(f"OsLepplus_allJets_jId{jet_id}_puId{puWP}_{kinNm}_Eta2p4_{catName}", weight=w_pu))
                    for catName, (cand, catSel) in osllSelCand.items())
                OsLepplus_atleast2Jets = dict((catName, catSel.refine(f"OsLepplus_atleast2_jId{jet_id}_puId{puWP}_{kinNm}_Eta2p4_{catName}", cut=[op.rng_len(ak4jets_corr) > 1], weight=w_pu))
                    for catName, (cand, catSel) in osllSelCand.items())
                OsLepplus_exactly2Jets = dict((catName, catSel.refine(f"OsLepplus_Only2_jId{jet_id}_puId{puWP}_{kinNm}_Eta2p4_{catName}", cut=[op.rng_len(ak4jets_corr) ==2], weight=w_pu))
                    for catName, (cand, catSel) in osllSelCand.items())
                
                plots += perCatPlots_sameVar("jetETAPHI", OsLepplus_allJets,
                        (op.map(ak4jets_corr, lambda j : j.eta), op.map(ak4jets_corr, lambda j : j.phi)),
                        (EqB(50, -2.5, 2.5), EqB(50,  -3.1416, 3.1416)), combPrefix="OsLepplus_allJets", nDim=2)
                #plots += perCatPlots_sameVar(f"nJet{kinNm}", OsLepplus_allJets_noKinematics, op.rng_len(ak4jets_corr),
                #        EqB(12, 0., 12.), saveSeparate=True, combPrefix="OsLepplus_allJets_noKinematics")
                
                sv_mass=op.map(t.SV, lambda sv: sv.mass)
                sv_eta=op.map(t.SV, lambda sv: sv.eta)
                sv_phi=op.map(t.SV, lambda sv: sv.phi)
                sv_pt=op.map(t.SV, lambda sv: sv.pt)
                
                for sel , suffix in zip([OsLepplus_atleast2Jets],['_atleast2_']):
                #for sel , suffix in zip([OsLepplus_atleast2Jets, OsLepplus_exactly2Jets],['_atleast2_', '_Only2_']):
                    plots += perCatPlots_sameVar("jetETAPHI", sel,
                            (op.map(ak4jets_corr, lambda j : j.eta), op.map(ak4jets_corr, lambda j : j.phi)),
                            (EqB(50, -2.5, 2.5), EqB(50,  -3.1416, 3.1416)), combPrefix="OsLepplus_%s_aka4Jets"%suffix, nDim=2)
                
                    plots += perCatPlots_sameVar("nJet", sel, op.rng_len(ak4jets_corr),
                            EqB(7, 0., 7.), saveSeparate=True, combPrefix="OsLepplus_%s_aka4Jets"%suffix)

                    plots += perCatPlots_sameVar("vtx", sel, t.PV.npvsGood,
                            EqB(60 // binScaling, 0., 80.), saveSeparate=True, combPrefix="OsLepplus_%s_aka4Jets"%suffix)
                    plots += perCatPlots_sameVar("sv_mass", sel, sv_mass,
                            EqB(50 // binScaling, 0., 80.), saveSeparate=True, combPrefix="OsLepplus_%s_aka4Jets"%suffix)
                    plots += perCatPlots_sameVar("sv_eta", sel, sv_eta,
                            EqB(50 // binScaling,-2.4, 2.4), saveSeparate=True, combPrefix="OsLepplus_%s_aka4Jets"%suffix)
                    plots += perCatPlots_sameVar("sv_phi", sel, sv_phi,
                            EqB(50 // binScaling, -3.1416, 3.1416), saveSeparate=True, combPrefix="OsLepplus_%s_aka4Jets"%suffix)
                    plots += perCatPlots_sameVar("sv_pt", sel, sv_pt,
                            EqB(50 // binScaling, 0., 450.), saveSeparate=True, combPrefix="OsLepplus_%s_aka4Jets"%suffix)
                    kinematic_cuts = suffix + 'jId_'+ jet_id+'_puId'+puWP+'_'+kinNm+ '_Eta2p4'
                    for catName, lepjSel in sel.items(): 
                        plots += cp.makeJetPlots(lepjSel, ak4jets_corr, catName, 'resolved', year, kinematic_cuts)
    return plots


def varsCutsPlotsforLeptons(lepton, sel, uname):
   plots = []
   # TODO this not going to work for mixed cat, no time to do this  now , fix it later 
   Flav = ('Electron' if uname[-1]=='l' else('Muon' if uname[-1]=='u' else('comb')))
   for i in range(2):
       plots.append(Plot.make1D(f"%s{i+1}_sip3d_%s"%(Flav,uname), lepton[i].sip3d, sel,
                            EqB(100, -8., 8.), title=f"{utils.getCounter(i+1)} sip3d",
                            plotopts=utils.getOpts(uname)))
       plots.append(Plot.make1D(f"%s{i+1}_miniPFRelIso_all_%s"%(Flav,uname), lepton[i].miniPFRelIso_all, sel,
                            EqB(100, 0., .4), title=f"{utils.getCounter(i+1)} miniPFRelIso_all",
                            plotopts=utils.getOpts(uname)))
       if Flav == 'Electron':
           plots.append(Plot.make1D(f"%s{i+1}_dxy_%s"%(Flav,uname), lepton[i].dxy, sel,
                                EqB(100, -.05, .05), title=f"{utils.getCounter(i+1)} dxy",
                                plotopts=utils.getOpts(uname)))
           plots.append(Plot.make1D(f"%s{i+1}_dz_%s"%(Flav, uname), lepton[i].dz, sel,
                                EqB(100, -.1, .1), title=f"{utils.getCounter(i+1)} dz",
                                plotopts=utils.getOpts(uname)))
   return plots


def LeptonsInsideJets(jets, sel, uname):
    plots=[]
    binScaling=1

    plots.append(Plot.make1D(f"%s_Jet_nElectrons"%uname, op.rng_len(jets.nElectrons), sel,
            EqB(7, 0., 7.), title="Jet_nElectrons",
            plotopts=utils.getOpts(uname, **{"log-y": True})))
    plots.append(Plot.make1D(f"%s_Jet_nMuons"%uname, op.rng_len(jets.nMuons), sel,
            EqB(7, 0., 7.), title="Jet_nMuons",
            plotopts=utils.getOpts(uname, **{"log-y": True})))
        
    return plots


def NegativeWeightsFractions( self, tree, leptons, jets, sel, uname, isMC):

    # sel : 2leptons os
    plots = []
    binScaling=1
    Njets = op.rng_len(jets)
    HT = op.rng_sum(Njets, lambda j : j.pt)
    
#    plots.append(Plot.make1D(f"NJets_%s"%uname, op.rng_len(jets), sel.weight/op.switch(tree.genWeight < 0 , tree.genWeight, op.c_bool(isMC)),
#            EqB(10, 0., 10.), title="Reco. Njets",
#            plotopts=utils.getOpts(uname, **{"log-y": True})))
#
#    plots.append(Plot.make1D(f"HT_%s"%uname, HT, sel.weight/op.switch(tree.genWeight < 0 , tree.genWeight, op.c_bool(isMC)),
#            EqB(100//binScaling, 0., 2500.), title="GEN. HT",
#            plotopts=utils.getOpts(uname, **{"log-y": True})))
#   
#    plots.append(Plot.make1D(f"pt_ll_%s"%uname, (leptons[0].p4 + leptons[1].p4).Pt(), sel.weight/op.switch(tree.genWeight < 0 , tree.genWeight, op.c_bool(isMC)),
#            EqB(60//binScaling, 0., 1000.), title="GEN. pT(ll)",
#            plotopts=utils.getOpts(uname, **{"log-y": True})))

    plots.append(Plot.make1D(f"genWeight_%s"%uname, tree.genWeight, sel,
            EqB(60//binScaling, 0., 1000.), title="GEN. Weight",
            plotopts=utils.getOpts(uname, **{"log-y": True})))
    plots.append(Plot.make1D(f"TotalWeight_%s"%uname, sel.weight, sel,
            EqB(60//binScaling, 0., 1000.), title="Total. Weight",
            plotopts=utils.getOpts(uname, **{"log-y": True})))
    
    return plots



def DYgenLevelPlots(t, noSel, sample):
    # it will crash if evaluated when there are no two leptons in the matrix element
    plots = []
    if sample in ["DYJetsToLL_0J", "DYJetsToLL_1J", "DYJetsToLL_2J"]:
        genLeptons_hard = op.select(t.GenPart, lambda gp : op.AND((gp.statusFlags & (0x1<<7)), op.in_range(10, op.abs(gp.pdgId), 17)))
        gen_ptll_nlo    = (genLeptons_hard[0].p4+genLeptons_hard[1].p4).Pt()
        
        forceDefine(gen_ptll_nlo, noSel)
        
        plots.append(Plots_gen(gen_ptll_nlo, noSel, "noSel"))
        plots.append(Plot.make1D("nGenLeptons_hard", op.rng_len(genLeptons_hard), noSel, EqB(5, 0., 5.),  title="nbr genLeptons_hard [GeV]")) 
    return plots
