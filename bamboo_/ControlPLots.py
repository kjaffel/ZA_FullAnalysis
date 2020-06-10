import os
import sys
zabPath = os.path.dirname(__file__)
if zabPath not in sys.path:
    sys.path.append(zabPath)

from bambooToOls import Plot
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op

import utils
from utils import *

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
        
    plots.append(Plot.make1D(f"{uname}_mll_%s_%s"%(suffix, reg), op.invariant_mass(leptons[0].p4, leptons[1].p4), sel, 
            EqB(60, 70., 110.), title= "mll [GeV]", 
            plotopts=utils.getOpts(uname)))
    return plots
        
def makeJetmultiplictyPlots(sel, jets, uname, suffix):
    binScaling=1
    plots=[]
    plots.append(Plot.make1D(f"{uname}_{suffix}_Jet_mulmtiplicity".format(suffix=suffix), op.rng_len(jets), sel,
            EqB(7, 0., 7.), title="Jet mulmtiplicity",
            plotopts=utils.getOpts(uname, **{"log-y": True})))
        
    return plots

def makePrimaryANDSecondaryVerticesPlots(t, sel, uname):
    binScaling=1
    plots=[]
    sv_mass=op.map(t.SV, lambda sv: sv.mass)
    sv_eta=op.map(t.SV, lambda sv: sv.eta)
    sv_phi=op.map(t.SV, lambda sv: sv.phi)
    sv_pt=op.map(t.SV, lambda sv: sv.pt)
    
    plots.append(Plot.make1D(f"{uname}_number_primary_reconstructed_vertices", 
                    t.PV.npvsGood, sel, 
                    EqB(50 // binScaling, 0., 100.), title="reconstructed vertices",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))
    plots.append(Plot.make1D(f"{uname}_secondary_vertices_mass", 
                    sv_mass, sel, 
                    EqB(50 // binScaling, 0., 450.), title="SV mass",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))
    plots.append(Plot.make1D(f"{uname}_secondary_vertices_eta", 
                    sv_eta, sel, 
                    EqB(50 // binScaling,-2.4, 2.4), title="SV eta",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))
    plots.append(Plot.make1D(f"{uname}_secondary_vertices_phi", 
                    sv_phi, sel, 
                    EqB(50 // binScaling, -3.1416, 3.1416), title="SV #phi",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))
    plots.append(Plot.make1D(f"{uname}_secondary_vertices_pt", 
                    sv_pt, sel, 
                    EqB(50 // binScaling, 0., 450.), title="SV p_{T} [GeV]",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))

    return plots

def makeControlPlotsForBasicSel(sel, jets, dilepton, uname, suffix):
    binScaling =1
    plots =[]
    
    if suffix== "resolved":
        plots.append(Plot.make1D("{0}_{1}_jjPT".format(uname, suffix), 
                    (jets[0].p4 + jets[1].p4).Pt(), sel, 
                    EqB(60 // binScaling, 0., 450.), 
                    title= "di-jets P_{T} [GeV]", plotopts=utils.getOpts(uname)))
    
        plots.append(Plot.make1D("{0}_{1}_jjPhi".format(uname, suffix), 
                    (jets[0].p4 + jets[1].p4).Phi(), sel, 
                    EqB(50 // binScaling, -3.1416, 3.1416),
                    title= "di-jets #phi", plotopts=utils.getOpts(uname)))
    
        plots.append(Plot.make1D("{0}_{1}_jjEta".format(uname, suffix), 
                    (jets[0].p4 + jets[1].p4).Eta(), sel, 
                    EqB(50 // binScaling, -3., 3.),
                    title= "di-jets Eta", plotopts=utils.getOpts(uname)))

    Jets_ = (jets[0].p4 if suffix=="boosted" else(jets[0].p4+jets[1].p4))
    
    # masses: mjj , mlljj, TH1D && TH2D  in boosted and resolved region:
    plots.append(Plot.make1D("{0}_{1}_mjj".format(uname, suffix),
                op.invariant_mass(Jets_), sel,
                EqB(60 // binScaling, 0., 650.), 
                title="mjj [GeV]", plotopts=utils.getOpts(uname)))
    
    EqBIns = ( EqB(60 // binScaling, 120., 1200.) if suffix == "boosted" else(EqB(60 // binScaling, 150., 1200.)))
    plots.append(Plot.make1D("{0}_{1}_mlljj".format(uname, suffix), 
                (dilepton[0].p4 +dilepton[1].p4+Jets_).M(), sel, EqBIns, 
                title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make2D("{0}_{1}_mlljj_vs_mjj".format(uname, suffix), 
                (op.invariant_mass(Jets_), (dilepton[0].p4 + dilepton[1].p4 + Jets_).M()), sel, 
                (EqB(60 // binScaling, 0., 1200.), EqB(60 // binScaling, 120., 1200.)), 
                title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
    return plots

def makeControlPlotsForFinalSel(sel, bjets, leptons, wp, uname, suffix, cut):
    plots =[]
    binScaling=1
    for key in sel.keys():

        if 'DeepDoubleBvL' in key:
            tagger= 'DeepDoubleBvL'
        else:
            tagger=key.replace(wp, "")
        
        bjets_ = safeget(bjets, tagger, wp)
        
        
        # make di-bjets Plots 
        # skip boosted catgory because plots are already called in "makeBjetsPlots"
        if suffix=="resolved":
            plots.append(Plot.make1D("{0}_{1}{2}_bbPT_{3}".format(uname, suffix, cut, key), 
                        (bjets_[0].p4+bjets_[1].p4).Pt(),
                        sel.get(key), 
                        EqB(60 // binScaling, 0., 450.),
                        title= "di-bjet P_{T} [GeV]", plotopts=utils.getOpts(uname)))
            
            plots.append(Plot.make1D("{0}_{1}{2}_bbPhi_{3}".format(uname, suffix, cut, key), 
                        (bjets_[0].p4+bjets_[1].p4).Phi(), sel.get(key), 
                        EqB(50 // binScaling, -3.1416, 3.1416),
                        title= "di-bjet #phi", plotopts=utils.getOpts(uname)))
            
            plots.append(Plot.make1D("{0}_{1}{2}_bbEta_{3}".format(uname, suffix, cut, key), 
                        (bjets_[0].p4+bjets_[1].p4).Eta(), sel.get(key), 
                        EqB(50 // binScaling, -3., 3.),
                        title= "di-bjet Eta", plotopts=utils.getOpts(uname)))
        
        sorted_bJets= ((bjets_[0].p4+bjets_[1].p4)if suffix=="resolved" else( bjets_[0].p4))
        # plots masses: mllbb, mbb, mllbb vs mbb
        plots.append(Plot.make1D("{0}_{1}{2}_mllbb_{3}".format(uname, suffix, cut, key), 
                    (leptons[0].p4 +leptons[1].p4+sorted_bJets).M(),
                    sel.get(key),
                    EqB(60 // binScaling, 120., 1000.), 
                    title="mllbb [GeV]", plotopts=utils.getOpts(uname)))
        
        plots.append(Plot.make1D("{0}_{1}{2}_mbb_{3}".format(uname, suffix, cut, key),
                    op.invariant_mass(sorted_bJets), 
                    sel.get(key),
                    EqB(60 // binScaling, 0., 850.), 
                    title= "mbb [GeV]", plotopts=utils.getOpts(uname)))

        plots.append(Plot.make2D("{0}_{1}{2}_mllbb_vs_mbb_{3}".format(uname, suffix, cut, key), 
                    (op.invariant_mass(sorted_bJets), 
                    (leptons[0].p4 +leptons[1].p4+sorted_bJets).M()),
                    sel.get(key),
                    (EqB(60 // binScaling, 0., 1000.), EqB(60 // binScaling, 120., 1000)), 
                    title="mllbb vs mbb invariant mass [GeV]", plotopts=utils.getOpts(uname)))

        
        
        
    return plots 

def makeJetPlots(sel, jets, uname, suffix, era):
    binScaling=1
    plots = []
    maxJet=( 1 if suffix=="boosted" else(2))
    for i in range(maxJet):
        if suffix=="boosted":
            EqBin= EqB(60 // binScaling, 200, 850.)
        elif suffix=="resolved":
            jet_ptcut =(30. if era!='2016' else (20.))
            EqBin= EqB(60 // binScaling, jet_ptcut, 650.)
        else:
            raise RuntimeError('ERROR: {0} Unknown suffix '.format(suffix))
        
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet{i+1}_pt".format(suffix=suffix), jets[i].pt, sel,
                    EqBin, title=f"{utils.getCounter(i+1)} jet p_{{T}} [GeV]",
                    plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet{i+1}_eta".format(suffix=suffix), jets[i].eta, sel,
                    EqB(50 // binScaling, -2.4, 2.4), title=f"{utils.getCounter(i+1)} jet eta",
                    plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet{i+1}_phi".format(suffix=suffix), jets[i].phi, sel,
                    EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} jet #phi", plotopts=utils.getOpts(uname)))
    return plots

def makedeltaRPlots(sel, jets, leptons, uname, suffix):
    plots = []
    if suffix=="resolved":
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet1jet2_deltaR".format(suffix=suffix), op.deltaR(jets[0].p4, jets[1].p4),
                    sel, EqB(50, 0., 8.), title="#Delta R (leading jet, sub-leading jet)",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet1lep1_deltaR".format(suffix=suffix), op.deltaR(jets[0].p4, leptons[0].p4),
                    sel, EqB(50, 0., 8.), title="#Delta R (leading jet, leading lepton)",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet1lep2_deltaR".format(suffix=suffix), op.deltaR(jets[0].p4, leptons[1].p4),
                    sel, EqB(50, 0., 8.), title="#Delta R (leading jet, sub-leading lepton)",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet2lep1_deltaR".format(suffix=suffix), op.deltaR(jets[1].p4, leptons[0].p4),
                    sel, EqB(50, 0., 8.), title="#Delta R (sub-leading jet, leading lepton)",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet2lep2_deltaR".format(suffix=suffix), op.deltaR(jets[1].p4, leptons[1].p4),
                    sel, EqB(50, 0., 8.), title="#Delta R (leading jet, sub-leading lepton)",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D(f"{uname}_{suffix}_lep1lep2_deltaR".format(suffix=suffix), op.deltaR(leptons[0].p4, leptons[1].p4),
                    sel, EqB(50, 0., 8.), title="#Delta R (leading lepton, sub-leading lepton)",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
    return plots

def makeBJetPlots(sel, bjets, wp, uname, suffix, cut, era):
    binScaling=1
    plots = []
    
    if suffix== "resolved":
        jet_ptcut = (30. if era != '2016' else (20.))
        EqBin= EqB(60 // binScaling, jet_ptcut, 650.)
    elif suffix=="boosted":
        EqBin= EqB(60 // binScaling, 200, 850.)
    else:
        raise RuntimeError('ERROR: {0} Unknown suffix '.format(suffix))
    
    for key in sel.keys():
        if 'DeepDoubleBvL' in key:
            tagger= 'DeepDoubleBvL'
        else:
            tagger=key.replace(wp, "")
        bjets_ = safeget(bjets, tagger, wp)
        maxJet= (1 if suffix=="boosted" else(2))
        
        plots.append(Plot.make1D(f"{uname}_{suffix}_{key}_{cut}_Jet_mulmtiplicity".format(suffix=suffix, cut=cut, key=key), op.rng_len(bjets_), sel.get(key),
                    EqB(7, 0., 7.), title="Jet mulmtiplicity",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))
        
        for i in range(maxJet):
            plots.append(Plot.make1D(f"{uname}_{suffix}{cut}_bjet{i+1}_pT_{key}".format(suffix=suffix, cut=cut, key=key), bjets_[i].pt, sel.get(key),
                        EqBin, title=f"{utils.getCounter(i+1)} bJet pT [GeV]",
                        plotopts=utils.getOpts(uname)))
            plots.append(Plot.make1D(f"{uname}_{suffix}{cut}_bjet{i+1}_eta_{key}".format(suffix=suffix, cut=cut, key=key), bjets_[i].eta, sel.get(key),
                        EqB(50 // binScaling, -2.5, 2.5), title=f"{utils.getCounter(i+1)} bJet eta",
                        plotopts=utils.getOpts(uname)))
            plots.append(Plot.make1D(f"{uname}_{suffix}{cut}_bjet{i+1}_phi_{key}".format(suffix=suffix, cut=cut, key=key), bjets_[i].phi, sel.get(key),
                        EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} bJet phi", 
                        plotopts=utils.getOpts(uname)))
    return plots

def makeExtraFatJetBOostedPlots(sel, bjets, wp, uname):
    binScaling=1
    plots = []
    """
        sel = 2lep OSSF + 2bjets 
        wp = medium 
    """
    for key in sel.keys():
        tagger=key.replace(wp, "")
        bjets_ = safeget(bjets, tagger, wp)

        plots.append(Plot.make1D("{0}_{1}_boosted_fatjet_mass".format(uname, key),
                            bjets_[0].mass, sel.get(key),
                            EqB(60 // binScaling, 0., 850.),
                            title="fatjet mass",
                            plotopts = utils.getOpts(uname)))
        # Corrected soft drop mass with PUPPI"
        plots.append(Plot.make1D("{0}_{1}_boosted_fatjet_softdropmass".format(uname, key),
                            bjets_[0].msoftdrop, sel.get(key),
                            EqB(60 // binScaling, 0., 850.),
                            title="M_{Soft Drop}(fatjet) [GeV]",
                            plotopts = utils.getOpts(uname)))

    return plots

def makeAK8JetsPLots(sel, fatjet, uname):
    
    binScaling=1
    plots = []
    plots.append(Plot.make1D("%{0}_boosted_fatjet_mass".format(uname),
                        fatjet[0].mass, sel,
                        EqB(60 // binScaling, 0., 900.),
                        title="fatjet mass",
                        plotopts = utils.getOpts(uname)))
    # Corrected soft drop mass with PUPPI"
    plots.append(Plot.make1D("{0}_boosted_fatjet_softdropmass".format(uname),
                        fatjet[0].msoftdrop, sel,
                        EqB(60 // binScaling, 0., 900.),
                        title="M_{Soft Drop}(fatjet) [GeV]",
                        plotopts = utils.getOpts(uname)))

    plots.append(Plot.make1D("{0}_boosted_subJet1_pT".format(uname),
                        fatjet[0].subJet1._idx.pt, sel,
                        EqB(60 // binScaling, 0., 650.),
                        title= " subJet1 p_{T} [GeV]",
                        plotopts = utils.getOpts(uname)))
    plots.append(Plot.make1D("{0}_boosted_subJet2_pT".format(uname),
                        fatjet[0].subJet2._idx.pt, sel,
                        EqB(60 // binScaling, 0., 650.),
                        title= " subJet2 p_{T} [GeV]",
                        plotopts = utils.getOpts(uname)))
    return plots



def makehistosforTTbarEstimation(sel, leptons, bjets, wp, uname, suffix, met):

    plots=[]
    for key in sel.keys():
        
        tagger=key.replace(wp, "")
        bjets_ = safeget(bjets, tagger, wp)

        plots.append(Plot.make1D("jj_M_{0}_hZA_{1}_lljj_{2}_btag{3}_mll_and_{4}".format(uname, suffix, tagger, wp, met),
                        op.invariant_mass(bjets_[0].p4+bjets_[1].p4), 
                        sel.get(key),
                        EqB(40, 10., 1000.),
                        title= "Mjj [GeV]",
                        plotopts = utils.getOpts(uname)))
        plots.append(Plot.make1D("lljj_M_{0}_hZA_{1}_lljj_{2}_btag{3}_mll_and_{4}".format(uname, suffix, tagger, wp, met),
                        (leptons[0].p4 +leptons[1].p4+bjets_[0].p4+bjets_[1].p4).M(),
                        sel.get(key),
                        EqB(50, 100., 1500.),
                        title= "Mlljj [GeV]",
                        plotopts = utils.getOpts(uname)))
        plots.append(Plot.make1D("ll_M_{0}_hZA_{1}_lljj_{2}_btag{3}_mll_and_{4}".format(uname, suffix, tagger, wp, met),
                        op.invariant_mass(leptons[0].p4, leptons[1].p4),
                        sel.get(key),
                        EqB(60, 70., 120.),
                        title= "Mll [GeV]",
                        plotopts = utils.getOpts(uname)))

        plots.append(Plot.make1D("jj_DR_j_j_{0}_hZA_{1}_lljj_{2}_btag{3}_mll_and_{4}".format(uname, suffix, tagger, wp, met),
                        op.deltaR(bjets_[0].p4, bjets_[1].p4),
                        sel.get(key),
                        EqB(50, 0., 6.),
                        title= "jj deltaR",
                        plotopts = utils.getOpts(uname)))
        plots.append(Plot.make1D( "jj_pt_{0}_hZA_{1}_lljj_{2}_btag{3}_mll_and_{4}".format(uname, suffix, tagger, wp, met),
                        (bjets_[0].p4 + bjets_[1].p4).Pt(),
                        sel.get(key),
                        EqB(50, 0., 450.),
                        title= "dijets p_{T} [GeV]",
                        plotopts = utils.getOpts(uname)))

        # FIXME loop later --- check the boosted EqBins range         
        plots.append(Plot.make1D("jet1_pt_{0}_hZA_{1}_lljj_{2}_btag{3}_mll_and_{4}".format(uname, suffix, tagger, wp, met),
                        bjets_[0].pt,
                        sel.get(key),
                        EqB( 50, 20., 500.),
                        title= "jet1 p_{T} [GeV]",
                        plotopts = utils.getOpts(uname)))
        plots.append(Plot.make1D( "jet2_pt_{0}_hZA_{1}_lljj_{2}_btag{3}_mll_and_{4}".format(uname, suffix, tagger, wp, met),
                        bjets_[1].pt,
                        sel.get(key),
                        EqB(50, 20., 300.),
                        title= "jet2 p_{T} [GeV]",
                        plotopts = utils.getOpts(uname)))

        plots.append(Plot.make1D("lep1_pt_{0}_hZA_{1}_lljj_{2}_btag{3}_mll_and_{4}".format(uname, suffix, tagger, wp, met),
                        leptons[0].pt,
                        sel.get(key),
                        EqB(50, 20., 400.),
                        title= "Leading Lepton p_{T} [GeV]",
                        plotopts = utils.getOpts(uname)))
        plots.append(Plot.make1D("lep2_pt_{0}_hZA_{1}_lljj_{2}_btag{3}_mll_and_{4}".format(uname, suffix, tagger, wp, met),
                        leptons[1].pt,
                        sel.get(key),
                        EqB(50, 10., 200.),
                        title= "Sub-leading Lepton p_{T} [GeV]",
                        plotopts = utils.getOpts(uname)))


    return plots 
