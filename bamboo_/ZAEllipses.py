from bamboo.plots import Plot, SummedPlot 
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op
import utils
from utils import safeget

def MakeEllipsesPLots(self, sel, bjets, lepton, wp, uname, suffix):
    plots = []
    binScaling=1
    for key in sel.keys():
        
        tagger = key.replace(wp, "")
        bjets_ = safeget(bjets, tagger, wp)
        
        plots.append(Plot.make1D("jj_M_{0}_{1}_hZA_lljj_{2}_mll_and_met_cut".format(suffix, uname, key),
                    op.invariant_mass(bjets_[0].p4, bjets_[1].p4), 
                    sel.get(key), 
                    EqB(60 // binScaling, 0., 1000.), 
                    title="invariant mass of two b-tagged jets wrt {0} Discriminator".format(suffix, key), 
                    xTitle= "mjj {0} {1} [GeV]".format(suffix, key),
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        
        plots.append(Plot.make1D("lljj_M_{0}_{1}_hZA_lljj_{2}_mll_and_met_cut".format(suffix, uname, key), 
                    (lepton[0].p4 + lepton[1].p4 + bjets_[0].p4 + bjets_[1].p4).M(),
                    sel.get(key), 
                    EqB(60 // binScaling, 0., 1000.), 
                    title="invariant mass of 2 leptons two b-tagged jets wrt {0} Discriminator".format(suffix, key), 
                    xTitle="mlljj {0} {1} [GeV]".format(suffix, key),
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        
        plots.append(Plot.make2D("Mjj_vs_Mlljj_{0}_{1}_hZA_lljj_{2}_mll_and_met_cut".format(suffix, uname, key), 
                    (op.invariant_mass(bjets_[0].p4, bjets_[1].p4),(
                    lepton[0].p4 + lepton[1].p4 + bjets_[0].p4 + bjets_[1].p4).M()),
                    sel.get(key), 
                    (EqB(60 // binScaling, 0., 1000.), EqB(60 // binScaling, 0., 1000.)), 
                    title="mlljj vs mjj invariant mass {0} wrt {1} Discriminator".format(suffix, key),
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        
        plots.append(Plot.make1D("ll_M_{0}_{1}_hZA_lljj_{2}_mll_and_met_cut".format(suffix, uname, key), 
                    op.invariant_mass(lepton[0].p4, lepton[1].p4), 
                    sel.get(key), 
                    EqB(60 // binScaling, 70., 110.), 
                    title=" dilepton invariant mass {0} wrt {1} Discriminator".format(suffix, key), 
                    xTitle= "mll {0} {1} [GeV]".format(suffix, key),
                    plotopts=utils.getOpts(uname)))
    return plots

def MakeMETPlots(self, sel, corrmet, met, uname, suffix):    
    plots = []
    binScaling=1
    for key in sel.keys():
        
        plots.append(Plot.make1D("met_pt_{0}_{1}_hZA_lljj_{2}".format(suffix, uname, key), 
                    met.pt, sel.get(key), 
                    EqB(60 // binScaling, 0., 600.), title="MET p_{T} [GeV]",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D("xycorrmet_pt_{0}_{1}_hZA_lljj_{2}".format(suffix, uname, key), 
                    corrmet.pt, sel.get(key), 
                    EqB(60 // binScaling, 0., 600.), title="corrMET p_{T} [GeV]",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
    return plots

def MakeExtraMETPlots(self, sel, lepton, met, uname, suffix):
    binScaling=1
    plots = []
    for key in sel.keys():

        plots.append(Plot.make1D("{0}_{1}_{2}_MET_pt".format(uname, key, suffix), met.pt, sel.get(key),
                        EqB(60 // binScaling, 0., 600.), title="MET p_{T} [GeV]",
                        plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D("{0}_{1}_{2}_MET_phi".format(uname, key, suffix), met.phi, sel.get(key),
                        EqB(60 // binScaling, -3.1416, 3.1416), title="MET #phi",
                        plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D("{0}_{1}_{2}_MET_eta".format(uname, key, suffix), met.phi, sel.get(key),
                        EqB(60 // binScaling, -2.4, 2.4), title="MET #eta",
                        plotopts=utils.getOpts(uname, **{"log-y": False})))
        
        for i in range(2):
            plots.append(Plot.make1D(f"{uname}_{key}_{suffix}_MET_lep{i+1}_deltaPhi".format(uname=uname, key=key, suffix=suffix),
                            op.Phi_mpi_pi(lepton[i].phi - met.phi), sel.get(key), EqB(60 // binScaling, -3.1416, 3.1416),
                            title="#Delta #phi (lepton, MET)", plotopts=utils.getOpts(uname, **{"log-y": False})))
    
            MT = op.sqrt( 2. * met.pt * lepton[i].p4.Pt() * (1. - op.cos(op.Phi_mpi_pi(met.phi - lepton[i].p4.Phi()))) )
            plots.append(Plot.make1D(f"{uname}_{key}_{suffix}_MET_MT_lep{i+1}".format(uname=uname, key=key, suffix=suffix), MT, sel.get(key),
                            EqB(60 // binScaling, 0., 600.), title="Lepton M_{T} [GeV]",
                            plotopts=utils.getOpts(uname, **{"log-y": False})))
    return plots
