import sys
import os
from bamboo.plots import Plot, SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_')
import utils
from utils import *


def makeControlPlotsForZpic(self, sel, leptons, uname):
    plots = []
    binScaling=1
    for i in range(2):
        if "Mu" in uname:
            flav = "Muon"
        if "El" in uname:
            flav = "Electron"

        plots.append(Plot.make1D(f"{uname}_lep{i+1}_pt", leptons[i].pt, sel,
                EqB(60 // binScaling, 30., 530.), title=f"{utils.getCounter(i+1)} %s pT [GeV]" % flav,
                plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_lep{i+1}_eta", leptons[i].eta, sel,
                EqB(50 // binScaling, -2.4, 2.4), title=f"{utils.getCounter(i+1)} %s eta" % flav,
                plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_lep{i+1}_phi", leptons[i].phi, sel,
                EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} %s phi" % flav,
                plotopts=utils.getOpts(uname))) 
    
    plots.append(Plot.make1D(f"{uname}_llpT", (leptons[0].p4 + leptons[1].p4).Pt(), sel, 
            EqB(60, 0., 450.), title= "dilepton P_{T} [GeV]", 
            plotopts=utils.getOpts(uname)))
        
    plots.append(Plot.make1D(f"{uname}_mll", op.invariant_mass(leptons[0].p4, leptons[1].p4), sel, 
            EqB(60, 70., 110.), title= "mll [GeV]", 
            plotopts=utils.getOpts(uname)))
    return plots
        
def makeJetmultiplictyPlots(self, sel, jets, uname, suffix):
    binScaling=1
    plots=[]

    plots.append(Plot.make1D(f"{uname}_{suffix}_Jet_mulmtiplicity".format(suffix=suffix), op.rng_len(jets), sel,
            EqB(10, 0., 7.), title="Jet mulmtiplicity",
            plotopts=utils.getOpts(uname, **{"log-y": True})))
        
    #plots.append(Plot.make2D("{0}_Electron_dzdxy".format(uname), 
    #            (lepton[0].dz ,lepton[0].dxy), sel, 
    #            (EqB(10, 0., 2.),
    #            EqB(10, 0., 2.)) ,
    #            title="Electron in Barrel/EndCAP region" ))
    return plots



def makePrimaryANDSecondaryVerticesPlots(self, sel, uname):
    binScaling=1
    plots=[]
    sv_mass=op.map(t.SV, lambda sv: sv.mass)
    sv_eta=op.map(t.SV, lambda sv: sv.eta)
    sv_phi=op.map(t.SV, lambda sv: sv.phi)
    sv_pt=op.map(t.SV, lambda sv: sv.pt)
    
    plots.append(Plot.make1D(f"{uname}_number_primary_reconstructed_vertices", 
                    t.PV.npvs, sel, 
                    EqBin(50 // binScaling, 0., 60.), title="reconstructed vertices",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))
    plots.append(Plot.make1D(f"{uname}_secondary_vertices_mass", 
                    sv_mass, sel, 
                    EqBin(50 // binScaling, 0., 450.), title="SV mass",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))
    plots.append(Plot.make1D(f"{uname}_secondary_vertices_eta", 
                    sv_eta, sel, 
                    EqBin(50 // binScaling,-2.4, 2.4), title="SV eta",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))
    plots.append(Plot.make1D(f"{uname}_secondary_vertices_phi", 
                    sv_phi, sel, 
                    EqBin(50 // binScaling, -3.1416, 3.1416), title="SV phi",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))
    plots.append(Plot.make1D(f"{uname}_secondary_vertices_pt", 
                    sv_pt, sel, 
                    EqBin(50 // binScaling, 0., 450.), title="SV p_{T} [GeV]",
                    plotopts=utils.getOpts(uname, **{"log-y": True})))

    return plots

def makeControlPlotsForBasicSel(self, sel, jets, dilepton, uname, suffix):
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
                    title= "di-jets Phi", plotopts=utils.getOpts(uname)))
    
        plots.append(Plot.make1D("{0}_{1}_jjEta".format(uname, suffix), 
                    (jets[0].p4 + jets[1].p4).Eta(), sel, 
                    EqB(50 // binScaling, -3., 3.),
                    title= "di-jets Eta", plotopts=utils.getOpts(uname)))

    Jets_ = (jets[0].p4 if suffix=="boosted" else(jets[0].p4+jets[1].p4))
    
    # masses: mjj , mlljj, TH1D && TH2D  in boosted and resolved region:
    plots.append(Plot.make1D("{0}_{1}_mjj".format(uname, suffix),
                op.invariant_mass(Jets_), sel,
                EqB(60 // binScaling, 20., 450.), 
                title="mjj [GeV]", plotopts=utils.getOpts(uname)))
    
    EqBIns = ( EqB(60 // binScaling, 200., 900.) if suffix == "boosted" else(EqB(60 // binScaling, 110., 900.)))
    plots.append(Plot.make1D("{0}_{1}_mlljj".format(uname, suffix), 
                (dilepton[0].p4 +dilepton[1].p4+Jets_).M(), sel, EqBIns, 
                title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make2D("{0}_{1}_mlljj_vs_mjj".format(uname, suffix), 
                (op.invariant_mass(Jets_), (dilepton[0].p4 + dilepton[1].p4 + Jets_).M()), sel, 
                (EqB(60 // binScaling, 20., 650.), EqB(60 // binScaling, 110., 650.)), 
                title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
    return plots

def makeControlPlotsForFinalSel(self, sel, bjets, leptons, wp, uname, suffix, cut):
    plots =[]
    binScaling=1
    for key in sel.keys():

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
                        title= "di-bjet Phi", plotopts=utils.getOpts(uname)))
            
            plots.append(Plot.make1D("{0}_{1}{2}_bbEta_{3}".format(uname, suffix, cut, key), 
                        (bjets_[0].p4+bjets_[1].p4).Eta(), sel.get(key), 
                        EqB(50 // binScaling, -3., 3.),
                        title= "di-bjet Eta", plotopts=utils.getOpts(uname)))
        
        sorted_bJets= ((bjets_[0].p4+bjets_[1].p4)if suffix=="resolved" else( bjets_[0].p4))
        # plots masses: mllbb, mbb, mllbb vs mbb
        plots.append(Plot.make1D("{0}_{1}{2}_mllbb_{3}".format(uname, suffix, cut, key), 
                    (leptons[0].p4 +leptons[1].p4+sorted_bJets).M(),
                    sel.get(key),
                    EqB(60 // binScaling, 110., 650.), 
                    title="mllbb [GeV]", plotopts=utils.getOpts(uname)))
        
        plots.append(Plot.make1D("{0}_{1}{2}_mbb_{3}".format(uname, suffix, cut, key),
                    op.invariant_mass(sorted_bJets), 
                    sel.get(key),
                    EqB(60 // binScaling, 20., 650.), 
                    title= "mbb [GeV]", plotopts=utils.getOpts(uname)))

        plots.append(Plot.make2D("{0}_{1}{2}_mllbb_vs_mbb_{3}".format(uname, suffix, cut, key), 
                    (op.invariant_mass(sorted_bJets), 
                    (leptons[0].p4 +leptons[1].p4+sorted_bJets).M()),
                    sel.get(key),
                    (EqB(60 // binScaling, 20., 650.), EqB(60 // binScaling, 110., 650.)), 
                    title="mllbb vs mbb invariant mass [GeV]", plotopts=utils.getOpts(uname)))
    return plots 

def makeJetPlots(self, sel, jets, uname, suffix):
    binScaling=1
    plots = []
    maxJet=( 1 if suffix=="boosted" else(2))
    for i in range(maxJet):
        if suffix=="boosted":
            EqBin= EqB(60 // binScaling, 200, 850.)
        elif suffix=="resolved":
            EqBin= EqB(60 // binScaling, 25., 650.)
        else:
            raise RuntimeError('ERROR: {0} Unknown suffix '.format(suffix))
        
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet{i+1}_pt".format(suffix=suffix), jets[i].pt, sel,
                    EqBin, title=f"{utils.getCounter(i+1)} jet p_{{T}} [GeV]",
                    plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet{i+1}_eta".format(suffix=suffix), jets[i].eta, sel,
                    EqB(50 // binScaling, -2.5, 2.5), title=f"{utils.getCounter(i+1)} jet eta",
                    plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet{i+1}_phi".format(suffix=suffix), jets[i].phi, sel,
                    EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} jet phi", plotopts=utils.getOpts(uname)))

    if suffix=="resolved":
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet_deltaR".format(suffix=suffix), op.deltaR(jets[0].p4, jets[1].p4),
                    sel, EqB(50, 0.3, 8.), title="Jets DR",
                    plotopts=utils.getOpts(uname)))
    return plots

def makeBJetPlots(self, sel, bjets, wp, uname, suffix, cut):
    binScaling=1
    plots = []
    
    if suffix== "resolved":
        EqBin= EqB(60 // binScaling, 25., 650.)
    elif suffix=="boosted":
        EqBin= EqB(60 // binScaling, 200, 850.)
    else:
        raise RuntimeError('ERROR: {0} Unknown suffix '.format(suffix))
    
    for key in sel.keys():
        tagger=key.replace(wp, "")
        bjets_ = safeget(bjets, tagger, wp)
        maxJet= (1 if suffix=="boosted" else(2))
        
        for i in range(maxJet):
            print (bjets_[i] , "**********************")
            print ("*********** maxJet", maxJet, i, suffix, wp, tagger, key, uname)
            
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

def makeExtraFatJetBOostedPlots(self, sel, bjets, wp, uname):
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

def makeAK8JetsPLots(self, sel, fatjet, uname):
    
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
