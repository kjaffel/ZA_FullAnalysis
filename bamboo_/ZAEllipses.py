from bambooToOls import Plot
from bamboo.plots import SummedPlot 
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op
import utils

def MakeEllipsesPLots(selections, bjets, lepton, wp, uname, suffix, metcut):
    plots = []
    binScaling=1
    for key, sel in selections.items():
        bjets_ = bjets[key.replace(wp, "")][wp]
        sorted_bJets= ((bjets_[0].p4+bjets_[1].p4) if suffix=="resolved" else( bjets_[0].p4))
        
        plots.append(Plot.make1D(f"jj_M_{suffix}_{uname}_hZA_lljj_{key}{metcut}",
                        op.invariant_mass(sorted_bJets), sel,
                        EqB(60 // binScaling, 0., 1000.), 
                        title= "mbb [GeV]", plotopts=utils.getOpts(uname, **{"log-y": False})))
            
        plots.append(Plot.make1D(f"lljj_M_{suffix}_{uname}_hZA_lljj_{key}{metcut}", 
                        (lepton[0].p4 + lepton[1].p4 + sorted_bJets).M(), sel,
                        EqB(60 // binScaling, 0., 1000.), 
                        title="mllbb [GeV]", plotopts=utils.getOpts(uname, **{"log-y": False})))
            
        plots.append(Plot.make2D(f"Mjj_vs_Mlljj_{suffix}_{uname}_hZA_lljj_{key}{metcut}", 
                        (op.invariant_mass(sorted_bJets),( lepton[0].p4 + lepton[1].p4 + sorted_bJets).M()), sel,
                        (EqB(60 // binScaling, 0., 1000.), EqB(60 // binScaling, 0., 1000.)), 
                        title="mllbb vs mbb [GeV]", plotopts=utils.getOpts(uname, **{"log-y": False})))
        
        plots.append(Plot.make1D(f"ll_M_{suffix}_{uname}_hZA_lljj_{key}{metcut}", 
                        op.invariant_mass(lepton[0].p4, lepton[1].p4), sel,
                        EqB(60 // binScaling, 70., 110.), 
                        title= "mll [GeV]", plotopts=utils.getOpts(uname, **{"log-y": False})))
    return plots

def MakeMETPlots(selections, corrmet, met, uname, suffix):
    plots = []
    binScaling=1
    for key, sel in selections.items():
        
        plots.append(Plot.make1D("met_pt_{0}_{1}_hZA_lljj_{2}".format(suffix, uname, key), 
                    met.pt, sel,
                    EqB(60 // binScaling, 0., 600.), title="MET p_{T} [GeV]",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D("xycorrmet_pt_{0}_{1}_hZA_lljj_{2}".format(suffix, uname, key), 
                    corrmet.pt, sel,
                    EqB(60 // binScaling, 0., 600.), title="corrMET p_{T} [GeV]",
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

def MakeExtraMETPlots(selections, lepton, met, uname, suffix):
    binScaling=1
    plots = []
    for key, sel in selections.items():

        plots.append(Plot.make1D("{0}_{1}_{2}_MET_pt".format(uname, key, suffix), met.pt, sel,
                        EqB(60 // binScaling, 0., 600.), title="MET p_{T} [GeV]",
                        plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D("{0}_{1}_{2}_MET_phi".format(uname, key, suffix), met.phi, sel,
                        EqB(60 // binScaling, -3.1416, 3.1416), title="MET #phi",
                        plotopts=utils.getOpts(uname, **{"log-y": False})))
        
        for i in range(2):
            plots.append(Plot.make1D(f"{uname}_{key}_{suffix}_MET_lep{i+1}_deltaPhi".format(uname=uname, key=key, suffix=suffix),
                            op.Phi_mpi_pi(lepton[i].phi - met.phi), sel, EqB(60 // binScaling, -3.1416, 3.1416),
                            title="#Delta #phi (lepton, MET)", plotopts=utils.getOpts(uname, **{"log-y": False})))
    
            MT = op.sqrt( 2. * met.pt * lepton[i].p4.Pt() * (1. - op.cos(op.Phi_mpi_pi(met.phi - lepton[i].p4.Phi()))) )
            plots.append(Plot.make1D(f"{uname}_{key}_{suffix}_MET_MT_lep{i+1}".format(uname=uname, key=key, suffix=suffix), MT, sel,
                            EqB(60 // binScaling, 0., 600.), title="Lepton M_{T} [GeV]",
                            plotopts=utils.getOpts(uname, **{"log-y": False})))
    return plots

def MHMAforCombinedLimits( selections, bjets, lepton, wp, uname, suffix):
    plots = []
    binScaling=1
    for key, sel in selections.items():
        bjets_ = bjets[key.replace(wp, "")][wp]
        sorted_bJets= ((bjets_[0].p4+bjets_[1].p4) if suffix=="resolved" else( bjets_[0].p4))
    
        plots.append(Plot.make1D("jj_M_{0}_{1}_hZA_lljj_{2}_mll_and_met_cut".format(suffix, uname, key),
                        op.invariant_mass(sorted_bJets), sel,
                        EqB(15 // binScaling, 0., 1000.), title= "mbb [GeV]",
                        plotopts=utils.getOpts(uname, **{"log-y": False})))
        
        plots.append(Plot.make1D("lljj_M_{0}_{1}_hZA_lljj_{2}_mll_and_met_cut".format(suffix, uname, key), 
                        (lepton[0].p4 + lepton[1].p4 + sorted_bJets).M(), sel,
                        EqB(15 // binScaling, 0., 1000.), title="mllbb [GeV]",
                        plotopts=utils.getOpts(uname, **{"log-y": False})))

    return plots 
