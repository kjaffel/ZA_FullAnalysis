import collections
from bamboo import treefunctions as op
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB

import utils as utils
from bambooToOls import Plot



def makeControlPlotsForZpic(sel, leptons, region, uname, reg ):
    plots = []
    binScaling=1
    
    ptcut = {'ElEl': {'l1': 25., 'l2': 15. },
             'MuMu': {'l1': 25., 'l2': 10. },
             'ElMu': {'l1': 25., 'l2': 10. },
             'MuEl': {'l1': 25., 'l2': 15. }
            }
    
    ll_p4 = leptons[0].p4 + leptons[1].p4
    for i in range(2):
        plots += [ Plot.make1D(f"{uname}_{region}_lep{i+1}_{nm}_{reg}", var, sel, binning, 
            title=f"{utils.getCounter(i+1)} lepton {title}", plotopts=utils.getOpts(uname))
            for nm, (var, binning, title) in {
                "pt" : (leptons[i].pt,  EqB(60 // binScaling, ptcut[uname][f'l{i+1}'], 650.), "P_{T} (GeV)"),
                "eta": (leptons[i].eta, EqB(50 // binScaling, -2.5, 2.5), "#eta"),
                "phi": (leptons[i].phi, EqB(50 // binScaling, -3.1416, 3.1416), "#phi")
                }.items() 
            ]
        
    plots += [ Plot.make1D(f"{uname}_{region}_ll_{nm}_{reg}", var, sel, binning,
        title=f"dilepton {title}", plotopts=utils.getOpts(uname))
        for nm, (var, binning, title) in {
            "pt" : (ll_p4.Pt() , EqB(60 // binScaling, 0., 650.), "P_{T} (GeV)"),
            "eta": (ll_p4.Eta(), EqB(50 // binScaling, -3., 3.), "#eta"),
            "phi": (ll_p4.Phi(), EqB(50 // binScaling, -3.1416, 3.1416), "#phi"),
            }.items()
        ]
    
    if not uname in ["MuEl", "ElMu"]:    
        plots += [ Plot.make1D(f"{uname}_{region}_ll_{nm}_{reg}", var, sel, binning,
            title=f"dilepton {title}", plotopts=utils.getOpts(uname))
            for nm, (var, binning, title) in {
                "mass" : (ll_p4.M() , EqB(60 // binScaling, 70., 120.), "m_{ll} (GeV)"),
            }.items()
        ]
    return plots
        

def makeJetmultiplictyPlots(sel, jets, jtype, uname, region):
    binScaling=1
    plots=[]
    plots.append(Plot.make1D(f"{uname}_{region}_Jet_multiplicity", op.rng_len(jets), sel,
            EqB(7, 0., 7.), title=f"{jtype}Jet multiplicity",
            plotopts=utils.getOpts(uname, **{"log-y": True})))
        
    return plots


def makePrimaryANDSecondaryVerticesPlots(t, sel, uname):
    binScaling=1
    return ([ Plot.make1D(f"{uname}_number_primary_reconstructed_vertices",
                t.PV.npvsGood, sel,
                EqB(50 // binScaling, 0., 100.), title="reconstructed vertices",
                plotopts=utils.getOpts(uname, **{"log-y": True}))
        ] + [ Plot.make1D(f"{uname}_secondary_vertices_{nm}",
            op.map(t.SV, vVar), sel, binning,
            title=f"SV {nm}", plotopts=utils.getOpts(uname, **{"log-y": True}))
            for nm, (vVar, binning, title) in {
                "mass" : (lambda sv : sv.mass, EqB(50 // binScaling, 0., 450.)),
                "eta"  : (lambda sv : sv.eta , EqB(50 // binScaling,-2.4, 2.4)),
                "phi"  : (lambda sv : sv.phi , EqB(50 // binScaling, -3.1416, 3.1416)),
                "pt"   : (lambda sv : sv.pt  , EqB(50 // binScaling, 0., 450.))
                }.items()
        ])


def makeControlPlotsForBasicSel(sel, jets, dilepton, uname, region, note=''):
    binScaling =1
    plots =[]
    
    if region == "resolved":
        jj_p4 = (jets[0].p4+jets[1].p4)
    elif region == "boosted":
        jj_p4 = jets[0].p4
    elif region == "inclusive": 
        jj_p4 = op.switch(op.AND(op.rng_len(jets['boosted']) >= 1, jets['boosted'][0].p4.M() < 50.), jets['boosted'][0].p4, (jets['resolved'][0].p4+jets['resolved'][1].p4) )
    
    lljj_p4 = dilepton[0].p4 +dilepton[1].p4+jj_p4
    eqBIns_M = ( EqB(60 // binScaling, 120., 1200.) if region == "boosted" else(EqB(60 // binScaling, 150., 1200.)))

    if region in ["resolved"]:#, "inclusive"]:
        plots += [ Plot.make1D(f"{uname}_{region}_jj{nm}{note}", var, sel, binning,
            title=f"di-jets {title}", plotopts=utils.getOpts(uname))
            for nm, (var, binning, title) in {
                "PT" : (jj_p4.Pt(),  EqB(60 // binScaling, 0., 450.), "P_{T} [GeV]"),
                "Phi": (jj_p4.Phi(), EqB(50 // binScaling, -3.1416, 3.1416), "#phi"),
                "Eta": (jj_p4.Eta(), EqB(50 // binScaling, -3., 3.), "Eta")
                }.items()
            ]

    plots.append(Plot.make1D(f"{uname}_{region}_mjj{note}",
                jj_p4.M(), sel,
                EqB(60 // binScaling, 0., 1200.), 
                title="mjj (GeV)", plotopts=utils.getOpts(uname)))
    plots.append(Plot.make1D(f"{uname}_{region}_mlljj{note}", 
                lljj_p4.M(), sel,
                EqB(60 // binScaling, 0., 1200.), 
                title="mlljj (GeV)", plotopts=utils.getOpts(uname)))
    # no need for these anymore!
    # if region == 'boosted':
    #     plots.append(Plot.make1D(f"{uname}_{region}_mjj_fatjet_softdropmass",
    #                 jets[0].msoftdrop, sel,
    #                 EqB(60 // binScaling, 0., 850.),
    #                 title="mjj Soft Drop(fatjet) (GeV)",
    #                 plotopts = utils.getOpts(uname)))
    #     plots.append(Plot.make1D(f"{uname}_{region}_mlljj_fatjet_softdropmass",
    #                 (jets[0].msoftdrop+ (dilepton[0].p4 +dilepton[1].p4).M()), sel,
    #                 eqBIns_M,
    #                 title="mlljj Soft Drop(fatjet) (GeV)",
    #                 plotopts = utils.getOpts(uname)))
    #plots.append(Plot.make2D("{0}_{1}_mlljj_vs_mjj".format(uname, region),
    #            (jj_p4.M(), (dilepton[0].p4 + dilepton[1].p4 + jj_p4).M()), sel, 
    #            (EqB(60 // binScaling, 0., 1200.), EqB(60 // binScaling, 120., 1200.)), 
    #            title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
    return plots


def makeControlPlotsForFinalSel(selections, bjets, leptons, uname, region, cut, reco_sig, doSum, btv):
    plots =[]
    bb_plots = {}
    binScaling = 1
    plots_ToSum2 = collections.defaultdict(list)
    
    for key, sel in selections.items():
        
        tagger, wp = utils.get_tagger_wp(key, btv)
        bjets_     = bjets[tagger][wp]
        
        bb_p4   = ((bjets_[0].p4+bjets_[1].p4)if region=="resolved" else( bjets_[0].p4))
        llbb_p4 = (leptons[0].p4 +leptons[1].p4+bb_p4)

        # make di-bjets Plots 
        # skip boosted catgory because plots are already called in "makeBjetsPlots"
        if region=="resolved":
            bb_plots = { f'plt_bb_{nm}': Plot.make1D(f"{uname}_{reco_sig}_{region}_{cut}_bb{nm}_{key}",
                var, sel, binning, title=f"di-bjet {title}", plotopts=utils.getOpts(uname))
                for nm, (var, binning, title) in {
                    "PT" : (bb_p4.Pt() , EqB(50 // binScaling, 0., 650.), "P_{T} (GeV)"),
                    "Phi": (bb_p4.Phi(), EqB(50 // binScaling, -3.1416, 3.1416), "#phi"),
                    "Eta": (bb_p4.Eta(), EqB(50 // binScaling, -3., 3.), "#eta")
                    }.items()
                }
            plots += [ bb_plots[f'plt_bb_{nm}'] for nm in ["PT", "Phi", "Eta"] ]
       
        if region=="boosted":
            # Corrected soft drop mass with PUPPI"
            plots.append(Plot.make1D(f"{uname}_{reco_sig}_boosted_{cut}_fatjet_softdropmass_mbb_{key}",
                                bjets_[0].msoftdrop, sel,
                                EqB(60 // binScaling, 0., 850.),
                                title="mbb (Soft Drop fatjet) (GeV)",
                                plotopts = utils.getOpts(uname)))
            plots.append(Plot.make1D(f"{uname}_{reco_sig}_boosted_{cut}_fatjet_softdropmass_mllbb_{key}",
                                (bjets_[0].msoftdrop + (leptons[0].p4 +leptons[1].p4).M()), sel,
                                EqB(60 // binScaling, 120., 1200.),
                                title="mllbb (Soft Drop fatjet) (GeV)",
                                plotopts = utils.getOpts(uname)))
        
        #plots.append(Plot.make2D(f"{uname}_{reco_sig}_{region}_{cut}_mllbb_vs_mbb_{key}", 
        #            (bb_p4.M(), llbb_p4.M()), sel,
        #            (EqB(60 // binScaling, 0., 1000.), EqB(60 // binScaling, 120., 1000)), 
        #            title="mllbb vs mbb invariant mass [GeV]", plotopts=utils.getOpts(uname)))
        plt_mllbb = Plot.make1D(f"{uname}_{reco_sig}_{region}_{cut}_mllbb_{key}", 
                    llbb_p4.M(), sel,
                    EqB(60 // binScaling, 120., 1400.), 
                    title="mllbb (GeV)", plotopts=utils.getOpts(uname))
        plt_mbb = Plot.make1D(f"{uname}_{reco_sig}_{region}_{cut}_mbb_{key}",
                    bb_p4.M(), sel,
                    EqB(60 // binScaling, 0., 1200.), 
                    title= "mbb (GeV)", plotopts=utils.getOpts(uname))

        
        plots += [plt_mbb, plt_mllbb]
        if doSum:
            if not uname in ['ElMu', 'MuEl']:
                plots_ToSum2[(f"OSSF_{reco_sig}_{region}_{cut}_mbb_{key}")].append(plt_mbb)
                plots_ToSum2[(f"OSSF_{reco_sig}_{region}_{cut}_mllbb_{key}")].append(plt_mllbb)
                for nm, plt in bb_plots.items():
                    plots_ToSum2[(f"OSSF_{reco_sig}_{region}_{cut}_bb{nm}_{key}")].append(plt)

    return plots, plots_ToSum2 


def makeJetPlots(sel, jets, uname, region, era, note=''):
    binScaling = 1
    plots  = []
    maxJet = ( 1 if region=="boosted" else(2))
    for i in range(maxJet):
        
        eqBin = {'resolved': EqB(60 // binScaling, 20., 650.),
                 'boosted' : EqB(60 // binScaling, 200, 850.) }
        
        plots += [ Plot.make1D(f"{uname}_{region}_jet{i+1}_{nm}{note}",
                jVar(jets[i]), sel, binning, title=f"{utils.getCounter(i+1)} jet {title}",
                plotopts=utils.getOpts(uname))
            for nm, (jVar, binning, title) in {
                "pT" : (lambda j : j.pt, eqBin[region], "p_{T} [GeV]"),
                "eta": (lambda j : j.eta, EqB(50 // binScaling, -2.4, 2.4), "#eta"),
                "phi": (lambda j : j.phi, EqB(50 // binScaling, -3.1416, 3.1416), "#phi")
                }.items() ]
    return plots


def makedeltaRPlots(sel, jets, leptons, uname, region):
    plots = []
    if region=="resolved":
        idxtotitle = ["leading", "sub-leading"]
        from itertools import product, repeat
        plots += [ Plot.make1D(f"{uname}_{region}_jet{ij+1:d}lep{il+1:d}_deltaR",
                    op.deltaR(jets[ij].p4, leptons[il].p4), sel,
                    EqB(50, 0., 8.), title=f"#Delta R ({idxtotitle[ij]} jet, {idxtotitle[il]} lepton)",
                    plotopts=utils.getOpts(uname, **{"log-y": False}))
                for ij,il in product(*repeat(range(2), 2)) ]
        plots += [ Plot.make1D(f"{uname}_{region}_{nm[:3]}1{nm[:3]}2_deltaR", op.deltaR(objs[0].p4, objs[1].p4),
                    sel, EqB(50, 0., 8.), title=f"#Delta R (leading {nm}, sub-leading {nm})",
                    plotopts=utils.getOpts(uname, **{"log-y": False}))
                for nm,objs in {"lepton": leptons, "jet": jets}.items() ]
    return plots


def makeBJetPlots(selections, bjets, uname, region, cut, era, reco_sig, doSum, btv):
    binScaling = 1
    plots  = []
    bb_plots = {}
    plots_ToSum2 = collections.defaultdict(list)

    maxJet = 1 if region=="boosted" else 2
    
    jet_ptcut = {'resolved': 20.,
                 'boosted' : 200.}
    
    for key, sel in selections.items():
        
        tagger, wp = utils.get_tagger_wp(key, btv)
        bjets_ = bjets[tagger][wp]
        
        plots.append(Plot.make1D(f"{uname}_{reco_sig}_{region}_{key}_{cut}_Jet_mulmtiplicity", op.rng_len(bjets_), sel,
                    EqB(7, 0., 7.), title="Jet mulmtiplicity",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))
        
        for i in range(maxJet):
            bb_plots = { f'plt_bb_{nm}': Plot.make1D(f"{uname}_{reco_sig}_{region}_{cut}_bjet{i+1}_{nm}_{key}",
                        jVar(bjets_[i]), sel, binning, title=f"{utils.getCounter(i+1)} b-tagged Jet {title}",
                        plotopts=utils.getOpts(uname))
                for nm, (jVar, binning, title) in {
                    "pT"   : (lambda j : j.pt,  EqB(60 // binScaling, jet_ptcut[region], 850.), "p_{T} (GeV)"),
                    "mass" : (lambda j : j.mass,EqB(50 // binScaling, 0., 300.), "Mass (GeV)"),
                    "eta"  : (lambda j : j.eta, EqB(50 // binScaling, -2.5, 2.5), "#eta"),
                    "phi"  : (lambda j : j.phi, EqB(50 // binScaling, -3.1416, 3.1416), "#phi")
                    }.items() }

            plots += [ bb_plots[f'plt_bb_{nm}'] for nm in ["pT", "mass", "eta", "phi"] ]
            if region == 'boosted' and doSum and not uname in ['ElMu', 'MuEl']:
                for var, plt in bb_plots.items():
                    nm = var.split('plt_bb_')[1]
                    plots_ToSum2[(f'OSSFLep_{reco_sig}_{region}_{cut}_bjet{i+1}_{nm}_{var}_{key}')].append(plt)

    return plots, plots_ToSum2


def makeBoOstedInvariantMass( uname, fatjet, lepPlusJetssel, region):
    binScaling=1
    plots = []
    plots.append(Plot.make1D("{}_boosted_fatjet_mass{}".format(uname, region),
                        fatjet[0].mass, lepPlusJetssel,
                        EqB(60 // binScaling, 0., 450.),
                        title="fatjet mass",
                        plotopts = utils.getOpts(uname)))
    plots.append(Plot.make1D("{}_boosted_fatjet_softdropmass{}".format(uname, region),
                        fatjet[0].msoftdrop, lepPlusJetssel,
                        EqB(60 // binScaling, 0., 450.),
                        title="M_{Soft Drop}(fatjet) [GeV]",
                        plotopts = utils.getOpts(uname)))
    return plots


def makeNsubjettinessPLots(lepPlusJetssel, fatjet, lepSel, uname):
   # https://arxiv.org/pdf/1011.2268.pdf
    binScaling=1
    plots = []
   
    sel_notau21cut = lepSel.refine(f"{uname}_OneBoostedFatJet_NosubjettinessCut", cut=[ op.rng_len(fatjet) >= 1 ])    
    
    plots.extend(makeBoOstedInvariantMass( uname, fatjet, sel_notau21cut, "notau21cut"))
    
    plots.append(Plot.make1D("{}_boostedfatjet_ratio_tau2tau1_notau21cut".format(uname),
                            fatjet[0].tau2/fatjet[0].tau1, sel_notau21cut,
                            EqB(60 // binScaling, 0., 1.),
                            title= " N-subjettiness #tau2/#tau1 [GeV]",
                            plotopts = utils.getOpts(uname)))
    plots.append(Plot.make1D("{}_boostedfatjet_tau1_notau21cut".format(uname),
                            fatjet[0].tau1, sel_notau21cut,
                            EqB(60 // binScaling, 0., 1.),
                            title= " #tau1",
                            plotopts = utils.getOpts(uname)))
    plots.append(Plot.make1D("{}_boostedfatjet_tau2_notau21cut".format(uname),
                            fatjet[0].tau2, sel_notau21cut,
                            EqB(60 // binScaling, 0., 1.),
                            title= " #tau2",
                            plotopts = utils.getOpts(uname)))
    #plots.append(Plot.make2D("{}_tau1_vs_tau2_notau21cut".format(uname),
    #                        (fatjet[0].tau1, fatjet[0].tau2), sel_notau21cut,
    #                        (EqB(60 // binScaling, 0., 1.), EqB(60 // binScaling, 0., 1.)),
    #                        title=" #tau1 vs #tau2 ", plotopts=utils.getOpts(uname)))
    
    for r in [0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9] :
        fatjet_withsubjettinesscut = op.select(fatjet, lambda j : op.AND(j.tau2/j.tau1 < r ))
        sel_withtau21cut = lepSel.refine("OneBoostedFatJet_{}Sel_WithNsubjettinessCut{}".format(uname, str(r).replace('.','p')), 
                cut=[ op.rng_len(fatjet_withsubjettinesscut) > 0 ])
        
        plots.extend(makeBoOstedInvariantMass( uname, fatjet, sel_withtau21cut, 
            "_tau21cut{0}".format( str(r).replace('.','p')) ))

    return plots


def makeHistosForTTbarEstimation(selections, ll, bjets, corrmet, met, wp, uname, region, suffix, reco_sig, btv):
    plots=[]
    binScaling = 1
    for key, sel in selections.items():
        
        tagger, wp = utils.get_tagger_wp(key, btv)
        
        bb      = bjets[tagger][wp]
        bb_p4   = bb[0].p4 + bb[1].p4
        ll_p4   = ll[0].p4 + ll[1].p4
        llbb_p4 = ll_p4 + bb_p4
        
        plots += [ Plot.make1D(f"{uname}_{nm}_{reco_sig}_{region}_{tagger}{wp}_{suffix}",
            llbbVar, sel, binning, title=title, plotopts=utils.getOpts(uname))
            for nm, (llbbVar, binning, title) in {
                "bb_M"     : (bb_p4.M(),   EqB(50, 10., 1000.), "m_{bb} (GeV)"),
                "llbb_M"   : (llbb_p4.M(), EqB(50, 100., 1500.), "m_{llbb} (GeV)"),
                "ll_M"     : (ll_p4.M(),   EqB(50, 70., 120.), "m_{ll} (GeV)"),
                "bb_DR"    : (op.deltaR(bb[0].p4, bb[1].p4), EqB(50, 0., 6.), "#delta R(bjet1, bjet2)"),
                "bb_pt"    : (bb_p4.Pt(), EqB(50, 0., 650.), "di-bjets p_{T} (GeV)"),
                "bjet1_pt" : (bb[0].pt, EqB(50, 20., 650.), "Leading bjet p_{T} (GeV)"),
                "bjet2_pt" : (bb[1].pt, EqB(50, 20., 650.), "Sub-leading bjet p_{T} (GeV)"),
                "bjet1_eta": (bb[0].eta, EqB(50 // binScaling, -2.4, 2.4), "Leading bjet #eta (GeV)"),
                "bjet2_eta": (bb[1].eta, EqB(50 // binScaling, -2.4, 2.4), "Sub-leading bjet #eta (GeV)"),
                "lep1_pt"  : (ll[0].pt, EqB( 50, 0., 650.), "Leading lepton p_{T} (GeV)"),
                "lep2_pt"  : (ll[0].pt, EqB( 50, 0., 650.), "Leading lepton p_{T} (GeV)"),
                "met_pt"   : (met.pt, EqB(50, 0., 650), "MET p_{T} (GeV)"),
                "corrmet_pt": (corrmet.pt, EqB(50, 0., 650), "xy-corrMET p_{T} (GeV)"),
                }.items()
            ]
    return plots 


def MakeMETPlots(selections, lepton, corrmet, met, uname, region, reco_sig):
    plots = []
    binScaling = 1
    
    for key, sel in selections.items():
        
        plots.append(Plot.make1D(f"met_pt_{reco_sig}_{region}_{uname}_hZA_lljj_{key}", 
                    met.pt, sel,
                    EqB(60 // binScaling, 0., 600.), title="MET p_{T} [GeV]",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D("xycorrmet_pt_{reco_sig}_{region}_{uname}_hZA_lljj_{key}", 
                    corrmet.pt, sel,
                    EqB(60 // binScaling, 0., 600.), title="corrMET p_{T} [GeV]",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D(f"{uname}_{key}_{region}_{reco_sig}_MET_pt", met.pt, sel,
                    EqB(60 // binScaling, 0., 600.), title="MET p_{T} [GeV]",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D(f"{uname}_{key}_{region}_{reco_sig}_MET_phi", met.phi, sel,
                    EqB(60 // binScaling, -3.1416, 3.1416), title="MET #phi",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        for i in range(2):
            plots.append(Plot.make1D(f"{uname}_{key}_{reco_sig}_{region}_MET_lep{i+1}_deltaPhi",
                            op.Phi_mpi_pi(lepton[i].phi - met.phi), sel, EqB(60 // binScaling, -3.1416, 3.1416),
                            title="#Delta #phi (lepton, MET)", plotopts=utils.getOpts(uname, **{"log-y": False})))
    
            MT = op.sqrt( 2. * met.pt * lepton[i].p4.Pt() * (1. - op.cos(op.Phi_mpi_pi(met.phi - lepton[i].p4.Phi()))) )
            plots.append(Plot.make1D(f"{uname}_{key}_{reco_sig}_{region}_MET_MT_lep{i+1}", MT, sel,
                            EqB(60 // binScaling, 0., 600.), title="Lepton M_{T} [GeV]",
                            plotopts=utils.getOpts(uname, **{"log-y": False})))
    return plots


def MakePuppiMETPlots(PuppiMET, sel, uname):
    plots = []
    binScaling=1
    plots.append(Plot.make1D("PuppiMET_sumEt_%s"%uname,
                        PuppiMET.sumEt, sel,
                        EqB(60 // binScaling, 0., 600.), title="PuppiMET sumEt [GeV]",
                        plotopts=utils.getOpts(uname, **{"log-y": False})))

    plots.append(Plot.make1D("PuppiMET_pt_%s"%uname,
                        PuppiMET.pt, sel,
                        EqB(60 // binScaling, 0., 600.), title=" PuppiMET p_{T} [GeV]",
                        plotopts=utils.getOpts(uname, **{"log-y": False})))

    plots.append(Plot.make1D("PuppiMET_phi_%s"%uname, 
                        PuppiMET.phi, sel,
                        EqB(60 // binScaling, -3.1416, 3.1416), title="PuppiMET #phi",
                        plotopts=utils.getOpts(uname, **{"log-y": False})))
    return plots


def MakeBJERcorrComparaisonPlots(selections, bjets, leptons, uname, region, cut, reco_sig, btv):
    plots = []
    binScaling=1
    
    for key, sel in selections.items():
    
        tagger, wp = utils.get_tagger_wp(key, btv)
        bjets_  = bjets[tagger][wp]
        bb_p4 = ((bjets_[0].p4 + bjets_[1].p4) if region =="resolved" else( bjets_[0].p4))

        for i in range(2): 
            plots += [ Plot.make1D(f"{uname}_{reco_sig}_{region}_{cut}_{nm}{i+1}_{key}",
                llbbVar, sel, binning, title=f"{utils.getCounter(i+1)} b-Jet {title}", plotopts=utils.getOpts(uname))
                for nm, (llbbVar, binning, title) in {
                    "pT"   : (bjets_[i].pt, EqB(60, 20., 650.), "pt (GeV)"),
                    "mass" : (bjets_[i].mass, EqB(60, 0., 1000.), "mass (GeV)"),
                }.items()
            ]
        plots += [ Plot.make1D(f"{uname}_{reco_sig}_{region}_{cut}_{nm}_{key}",
            llbbVar, sel, binning, title=title, plotopts=utils.getOpts(uname))
            for nm, (llbbVar, binning, title) in {
                "mbb"   : (bb_p4.M(), EqB(60, 0., 1000.), "m_{bb} (GeV)"),
                "mllbb" : ((leptons[0].p4 + leptons[1].p4 + bb_p4).M(), EqB(60, 0., 1000.), "m_{llbb} (GeV)"),
                "ptbb"  : (bb_p4.Pt(), EqB(60, 0., 450.), "pt_{bb} (GeV)"),
                }.items()
            ]
    return plots


def MakeBtagDiscriminatorPlots(tagger, list_j_sel, uname):
    plots = []
    binScaling=1
    plots_ToSum2 = collections.defaultdict(list)

    jet = list_j_sel[0]
    sel = list_j_sel[1]

    if tagger == 'DeepDoubleBvLV2':
        discr = 'btagDDBvLV2'
        discrToPlot = op.map(jet, lambda j: j.btagDDBvLV2)
    elif tagger == 'DeepFlavour':
        discr = 'btagDeepFlavB'
        discrToPlot = op.map(jet, lambda j: j.btagDeepFlavB)
    elif tagger == 'DeepCSV':
        discr = 'btagDeepB'
        discrToPlot = op.map(jet, lambda j: j.btagDeepB)
    else:
        raise RuntimeError(f'sorry {tagger} is unkown so the discriminator !')

    plt_discr = Plot.make1D(f"{uname}_{discr}_discriminator_{tagger}",
                        discrToPlot, sel,
                        EqB(60 // binScaling, 0., 1.), title=f"{discr} discriminator",
                        plotopts=utils.getOpts(uname))
    
    plots +=[plt_discr]
    if not uname in ['ElMu', 'MuEl']:
        plots_ToSum2[(f"OSSF_{discr}_discriminator_{tagger}")].append(plt_discr)
    
    return plots, plots_ToSum2
