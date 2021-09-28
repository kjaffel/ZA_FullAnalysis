import os
import sys

zabPath = os.path.dirname(__file__)
if zabPath not in sys.path:
    sys.path.append(zabPath)

import utils
from utils import *
from bambooToOls import Plot
from bamboo import treefunctions as op
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB


def makeControlPlotsForZpic(sel, leptons, suffix, uname, reg ):
    plots = []
    binScaling=1
    for i in range(2):
        lepptcut_forcomb = ( 25. if i == 0 else ( 10. if leptons[1].pt > 10 else( 15. if leptons[1].pt > 15. else (0.))))
        leptonptCut = (25. if i == 0 else( 10. if uname[-1]=='u' else( 15. if uname[-1]=='l' else(lepptcut_forcomb)))) 
        plots.append(Plot.make1D(f"{uname}_lep{i+1}_pt_%s_%s"%(suffix, reg), leptons[i].pt, sel,
                EqB(60 // binScaling, leptonptCut, 530.), title=f"{utils.getCounter(i+1)} Lepton pT [GeV]" ,
                plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_lep{i+1}_eta_%s_%s"%(suffix, reg), leptons[i].eta, sel,
                EqB(50 // binScaling, -2.5, 2.5), title=f"{utils.getCounter(i+1)} Lepton eta",
                plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_lep{i+1}_phi_%s_%s"%(suffix, reg), leptons[i].phi, sel,
                EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} Lepton #phi",
                plotopts=utils.getOpts(uname))) 
    
    plots.append(Plot.make1D(f"{uname}_llpT_%s_%s"%(suffix, reg), (leptons[0].p4 + leptons[1].p4).Pt(), sel, 
            EqB(60, 0., 450.), title= "dilepton P_{T} [GeV]", 
            plotopts=utils.getOpts(uname)))
    plots.append(Plot.make1D(f"{uname}_llphi_%s_%s"%(suffix, reg), (leptons[0].p4 + leptons[1].p4).Phi(), sel, 
            EqB(50 // binScaling, -3.1416, 3.1416), title= "dilepton #phi ", 
            plotopts=utils.getOpts(uname)))
    plots.append(Plot.make1D(f"{uname}_lleta_%s_%s"%(suffix, reg), (leptons[0].p4 + leptons[1].p4).Eta(), sel, 
            EqB(50 // binScaling, -2.5, 2.5), title= "dilepton eta", 
            plotopts=utils.getOpts(uname)))
    if uname not in ["MuEl", "ElMu"]:    
        plots.append(Plot.make1D(f"{uname}_mll_%s_%s"%(suffix, reg), op.invariant_mass(leptons[0].p4, leptons[1].p4), sel, 
                EqB(60, 70., 110.), title= "mll [GeV]", 
                plotopts=utils.getOpts(uname)))
    return plots
        
def makeJetmultiplictyPlots(sel, jets, uname, suffix):
    binScaling=1
    plots=[]
    plots.append(Plot.make1D(f"{uname}_{suffix}_Jet_multiplicity".format(suffix=suffix), op.rng_len(jets), sel,
            EqB(7, 0., 7.), title="Jet multiplicity",
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

def makeControlPlotsForBasicSel(sel, jets, dilepton, uname, suffix):
    binScaling =1
    plots =[]
    
    jj_p4 = (jets[0].p4 if suffix=="boosted" else(jets[0].p4+jets[1].p4))

    if suffix== "resolved":
        plots += [ Plot.make1D("{0}_{1}_jj{nm}".format(uname, suffix, nm=nm), var, sel, binning,
            title=f"di-jets {title}", plotopts=utils.getOpts(uname))
            for nm, (var, binning, title) in {
                "PT" : (jj_p4.Pt() , EqB(60 // binScaling, 0., 450.), "P_{T} [GeV]"),
                "Phi": (jj_p4.Phi(), EqB(50 // binScaling, -3.1416, 3.1416), "#phi"),
                "Eta": (jj_p4.Eta(), EqB(50 // binScaling, -3., 3.), "Eta")
                }.items()
            ]

    
    # masses: mjj , mlljj, TH1D && TH2D  in boosted and resolved region:
    plots.append(Plot.make1D("{0}_{1}_mjj".format(uname, suffix),
                jj_p4.M(), sel,
                EqB(60 // binScaling, 0., 650.), 
                title="mjj [GeV]", plotopts=utils.getOpts(uname)))
    
    eqBIns_M = ( EqB(60 // binScaling, 120., 1200.) if suffix == "boosted" else(EqB(60 // binScaling, 150., 1200.)))
    plots.append(Plot.make1D("{0}_{1}_mlljj".format(uname, suffix), 
                (dilepton[0].p4 +dilepton[1].p4+jj_p4).M(), sel, eqBIns_M,
                title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make2D("{0}_{1}_mlljj_vs_mjj".format(uname, suffix),
                (jj_p4.M(), (dilepton[0].p4 + dilepton[1].p4 + jj_p4).M()), sel, 
                (EqB(60 // binScaling, 0., 1200.), EqB(60 // binScaling, 120., 1200.)), 
                title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
    return plots

def makeControlPlotsForFinalSel(selections, bjets, leptons, wp, uname, suffix, cut, process):
    plots =[]
    binScaling=1
    for key, sel in selections.items():

        if 'DeepDoubleBvL' in key:
            tagger= 'DeepDoubleBvL'
        else:
            tagger=key.replace(wp, "")
        
        bjets_ = safeget(bjets, tagger, wp)
        
        jj_p4 = ((bjets_[0].p4+bjets_[1].p4)if suffix=="resolved" else( bjets_[0].p4))

        # make di-bjets Plots 
        # skip boosted catgory because plots are already called in "makeBjetsPlots"
        if suffix=="resolved":
            plots += [ Plot.make1D(f"{uname}_{suffix}{cut}_bb{nm}_{key}_{process}",
                var, sel, binning, title=f"di-bjet {title}", plotopts=utils.getOpts(uname))
                for nm, (var, binning, title) in {
                    "PT" : (jj_p4.Pt() , EqB(60 // binScaling, 0., 450.), "P_{T} [GeV]"),
                    "Phi": (jj_p4.Phi(), EqB(50 // binScaling, -3.1416, 3.1416), "#phi"),
                    "Eta": (jj_p4.Eta(), EqB(50 // binScaling, -3., 3.), "Eta")
                    }.items()
                ]
        
        llbb_p4 = (leptons[0].p4 +leptons[1].p4+jj_p4)
        # plots masses: mllbb, mbb, mllbb vs mbb
        plots.append(Plot.make1D(f"{uname}_{suffix}{cut}_mllbb_{key}_{process}", 
                    llbb_p4.M(), sel,
                    EqB(60 // binScaling, 120., 1000.), 
                    title="mllbb [GeV]", plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_{suffix}{cut}_mbb_{key}_{process}",
                    jj_p4.M(), sel,
                    EqB(60 // binScaling, 0., 850.), 
                    title= "mbb [GeV]", plotopts=utils.getOpts(uname)))
        plots.append(Plot.make2D(f"{uname}_{suffix}{cut}_mllbb_vs_mbb_{key}_{process}", 
                    (jj_p4.M(), llbb_p4.M()), sel,
                    (EqB(60 // binScaling, 0., 1000.), EqB(60 // binScaling, 120., 1000)), 
                    title="mllbb vs mbb invariant mass [GeV]", plotopts=utils.getOpts(uname)))
    return plots 

def makeJetPlots(sel, jets, uname, suffix, era):
    binScaling=1
    plots = []
    maxJet=( 1 if suffix=="boosted" else(2))
    for i in range(maxJet):
        if suffix=="boosted":
            eqBin_pt = EqB(60 // binScaling, 200, 850.)
        elif suffix=="resolved":
            jet_ptcut =(30. if "2016" in era else (20.))
            eqBin_pt = EqB(60 // binScaling, jet_ptcut, 650.)
        else:
            raise RuntimeError('ERROR: {0} Unknown suffix '.format(suffix))
        
        plots += [ Plot.make1D(f"{uname}_{suffix}_jet{i+1}_{nm}",
                jVar(jets[i]), sel, binning, title=f"{utils.getCounter(i+1)} jet {title}",
                plotopts=utils.getOpts(uname))
            for nm, (jVar, binning, title) in {
                "pT" : (lambda j : j.pt, eqBin_pt, "p_{T} [GeV]"),
                "eta": (lambda j : j.eta, EqB(50 // binScaling, -2.4, 2.4), "eta"),
                "phi": (lambda j : j.phi, EqB(50 // binScaling, -3.1416, 3.1416), "#phi")
                }.items() ]
    return plots

def makedeltaRPlots(sel, jets, leptons, uname, suffix):
    plots = []
    if suffix=="resolved":
        idxtotitle = ["leading", "sub-leading"]
        from itertools import product, repeat
        plots += [ Plot.make1D(f"{uname}_{suffix}_jet{ij+1:d}lep{il+1:d}_deltaR",
                    op.deltaR(jets[ij].p4, leptons[il].p4), sel,
                    EqB(50, 0., 8.), title=f"#Delta R ({idxtotitle[ij]} jet, {idxtotitle[il]} lepton)",
                    plotopts=utils.getOpts(uname, **{"log-y": False}))
                for ij,il in product(*repeat(range(2), 2)) ]
        plots += [ Plot.make1D(f"{uname}_{suffix}_{nm[:3]}1{nm[:3]}2_deltaR", op.deltaR(objs[0].p4, objs[1].p4),
                    sel, EqB(50, 0., 8.), title=f"#Delta R (leading {nm}, sub-leading {nm})",
                    plotopts=utils.getOpts(uname, **{"log-y": False}))
                for nm,objs in {"lepton": leptons, "jet": jets}.items() ]
    return plots

def makeBJetPlots(selections, bjets, wp, uname, suffix, cut, era, process):
    binScaling=1
    plots = []
    
    if suffix== "resolved":
        jet_ptcut = (30. if "2016" in era else (20.))
        eqBin_pt = EqB(60 // binScaling, jet_ptcut, 650.)
    elif suffix=="boosted":
        eqBin_pt = EqB(60 // binScaling, 200, 850.)
    else:
        raise RuntimeError('ERROR: {0} Unknown suffix '.format(suffix))
    
    for key, sel in selections.items():
        if 'DeepDoubleBvL' in key:
            tagger= 'DeepDoubleBvL'
        else:
            tagger=key.replace(wp, "")
        bjets_ = safeget(bjets, tagger, wp)
        maxJet= (1 if suffix=="boosted" else(2))
        
        plots.append(Plot.make1D(f"{uname}_{suffix}_{key}_{cut}_{process}_Jet_mulmtiplicity", op.rng_len(bjets_), sel,
                    EqB(7, 0., 7.), title="Jet mulmtiplicity",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))
        
        for i in range(maxJet):
            plots += [ Plot.make1D(f"{uname}_{suffix}{cut}_bjet{i+1}_{nm}_{key}_{process}",
                        jVar(bjets_[i]), sel, binning, title=f"{utils.getCounter(i+1)} bJet {title}",
                        plotopts=utils.getOpts(uname))
                for nm, (jVar, binning, title) in {
                    "pT" : (lambda j : j.pt, eqBin_pt, "pt [GeV]"),
                    "eta": (lambda j : j.eta, EqB(50 // binScaling, -2.5, 2.5), "eta"),
                    "phi": (lambda j : j.phi, EqB(50 // binScaling, -3.1416, 3.1416), "phi")
                    }.items() ]
    return plots

def makeExtraFatJetBOostedPlots(selections, bjets, wp, uname, suffix, process):
    binScaling=1
    plots = []
    """
        sel = 2lep OSSF + 2bjets 
        wp  = medium 
    """
    for key, sel in selections.items():
        tagger=key.replace(wp, "")
        bjets_ = safeget(bjets, tagger, wp)
        plots.append(Plot.make1D(f"{uname}_{key}_{suffix}_{process}_boosted_fatjet_mass",
                            bjets_[0].mass, sel,
                            EqB(60 // binScaling, 0., 850.),
                            title="fatjet mass",
                            plotopts = utils.getOpts(uname)))
        # Corrected soft drop mass with PUPPI"
        plots.append(Plot.make1D(f"{uname}_{key}_{suffix}_{process}_boosted_fatjet_softdropmass",
                            bjets_[0].msoftdrop, sel,
                            EqB(60 // binScaling, 0., 850.),
                            title="M_{Soft Drop}(fatjet) [GeV]",
                            plotopts = utils.getOpts(uname)))
    return plots

def makeBoOstedInvariantMass( uname, fatjet, lepPlusJetssel, suffix):
    binScaling=1
    plots = []
    plots.append(Plot.make1D("{}_boosted_fatjet_mass{}".format(uname, suffix),
                        fatjet[0].mass, lepPlusJetssel,
                        EqB(60 // binScaling, 0., 450.),
                        title="fatjet mass",
                        plotopts = utils.getOpts(uname)))
    # Corrected soft drop mass with PUPPI"
    plots.append(Plot.make1D("{}_boosted_fatjet_softdropmass{}".format(uname, suffix),
                        fatjet[0].msoftdrop, lepPlusJetssel,
                        EqB(60 // binScaling, 0., 450.),
                        title="M_{Soft Drop}(fatjet) [GeV]",
                        plotopts = utils.getOpts(uname)))
    return plots


def makeNsubjettinessPLots(lepPlusJetssel, fatjet, lepSel, fatjet_Nosubjettinesscut, uname):
    
    binScaling=1
    plots = []
   # plots.extend(makeBoOstedInvariantMass( uname, fatjet, lepPlusJetssel, "0p75"))
   # 
   # plots.append(Plot.make1D("{0}_boosted_subJet1_pT".format(uname),
   #                     fatjet[0].subJet1.pt, lepPlusJetssel,
   #                     EqB(60 // binScaling, 0., 650.),
   #                     title= " subJet1 p_{T} [GeV]",
   #                     plotopts = utils.getOpts(uname)))
   # plots.append(Plot.make1D("{0}_boosted_subJet2_pT".format(uname),
   #                     fatjet[0].subJet2.pt, lepPlusJetssel,
   #                     EqB(60 // binScaling, 0., 650.),
   #                     title= " subJet2 p_{T} [GeV]",
   #                     plotopts = utils.getOpts(uname)))
   # https://arxiv.org/pdf/1011.2268.pdf
    TwoLep_AtLeast1FatJetBoosted_notau21cut = lepSel.refine("OnboOstedeJet_{}Sel_NosubjettinessCut".format(uname), cut=[ op.rng_len(fatjet_Nosubjettinesscut) > 0 ])    
    plots.extend(makeBoOstedInvariantMass( uname, fatjet_Nosubjettinesscut, TwoLep_AtLeast1FatJetBoosted_notau21cut, "NosubjettinessCut"))
    
    plots.append(Plot.make1D("{}_boosted_ratio_tau2tau1".format(uname),
                            fatjet_Nosubjettinesscut[0].tau2/fatjet_Nosubjettinesscut[0].tau1, TwoLep_AtLeast1FatJetBoosted_notau21cut,
                            EqB(60 // binScaling, 0., 1.),
                            title= " N-subjettiness #tau2/#tau1 [GeV]",
                            plotopts = utils.getOpts(uname)))
    
    plots.append(Plot.make1D("{}_boostedfatjet_tau1".format(uname),
                            fatjet_Nosubjettinesscut[0].tau1, TwoLep_AtLeast1FatJetBoosted_notau21cut,
                            EqB(60 // binScaling, 0., 1.),
                            title= " #tau1",
                            plotopts = utils.getOpts(uname)))
    plots.append(Plot.make1D("{}_boostedfatjet_tau2".format(uname),
                            fatjet_Nosubjettinesscut[0].tau2, TwoLep_AtLeast1FatJetBoosted_notau21cut,
                            EqB(60 // binScaling, 0., 1.),
                            title= " #tau2",
                            plotopts = utils.getOpts(uname)))
    plots.append(Plot.make2D("{}_tau1_vs_tau2".format(uname),
                            (fatjet_Nosubjettinesscut[0].tau1, fatjet_Nosubjettinesscut[0].tau2), TwoLep_AtLeast1FatJetBoosted_notau21cut,
                            (EqB(60 // binScaling, 0., 1.), EqB(60 // binScaling, 0., 1.)),
                            title=" #tau1 vs #tau2 ", plotopts=utils.getOpts(uname)))
    
    for r in [0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9] :
        fatjet_withsubjettinesscut = op.select(fatjet_Nosubjettinesscut, lambda j : op.AND(j.tau2/j.tau1 < r ))
        TwoLep_AtLeast1FatBoostedJet = lepSel.refine("OneBoostedFatJet_{}Sel_WithNsubjettinessCut{}".format(uname, str(r).replace('.','p')), cut=[ op.rng_len(fatjet_withsubjettinesscut) > 0 ])
        plots.extend(makeBoOstedInvariantMass( uname, fatjet_Nosubjettinesscut, TwoLep_AtLeast1FatBoostedJet, "ratio_tau2tau1_{0}".format( str(r).replace('.','p')) ))

    return plots

def makeHistosForTTbarEstimation(selections, ll, bjets, wp, uname, suffix, met):
    plots=[]
    for key, sel in selections.items():
        tagger = key.replace(wp, "")
        bjets_ = safeget(bjets, tagger, wp)
        bb = bjets[key.replace(wp, "")][wp]
        plots += [ Plot.make1D(f"{nm}_{uname}_hZA_{suffix}_lljj_{tagger}_btag{wp}_mll_and_{met}",
            llbbVar, sel, binning, title=title, plotopts=utils.getOpts(uname))
            for nm, (llbbVar, binning, title) in {
                "jj_M"   : (op.invariant_mass(bb[0].p4+bb[1].p4), EqB(40, 10., 1000.), "Mjj [GeV]"),
                "lljj_M" : ((ll[0].p4+ll[1].p4+bb[0].p4+bb[1].p4).M(), EqB(50, 100., 1500.), "Mlljj [GeV]"),
                "ll_M"   : (op.invariant_mass(ll[0].p4+ll[1].p4), EqB(60, 70., 120.), "Mll [GeV]"),
                "jj_DR"  : (op.deltaR(bb[0].p4, bb[1].p4), EqB(50, 0., 6.), "jj deltaR"),
                "jj_pt"  : ((bjets_[0].p4 + bjets_[1].p4).Pt(), EqB(50, 0., 450.), "dijets p_{T} [GeV]"),
                "jet1_pt": (bb[0].pt, EqB( 50, 20., 500.), "jet1 p_{T} [GeV]"),
                "jet2_pt": (bb[1].pt, EqB( 50, 20., 300.), "jet2 p_{T} [GeV]"),
                "lep1_pt": (ll[0].pt, EqB( 50, 20., 400.), "Leading Lepton p_{T} [GeV]"),
                "lep2_pt": (ll[1].pt, EqB(50, 10., 200.), "Sub-leading Lepton p_{T} [GeV]"),
                }.items()
            ]
    return plots 
