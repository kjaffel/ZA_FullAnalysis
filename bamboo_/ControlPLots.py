import sys
import os
from bamboo.plots import Plot, SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_')
import utils


def makeControlPlotsForZpic(self, sel, lepton, uname):
    plots = []
    for i in range(2):
        if "mu" in uname:
            flav = "Muon"
        if "el" in uname:
            flav = "Electron"

        plots.append(Plot.make1D(f"{uname}_lep{i+1}_pt", lepton[i].pt, sel,
                EqB(60 // binScaling, 30., 530.), title="%s p_{T} [GeV]" % flav,
                plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_lep{i+1}_eta", lepton[i].eta, sel,
                EqB(50 // binScaling, -2.4, 2.4), title="%s eta" % flav,
                plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D(f"{uname}_lep{i+1}_phi", lepton[i].phi, sel,
                EqB(50 // binScaling, -3.1416, 3.1416), title="%s phi" % flav,
                plotopts=utils.getOpts(uname, **{"log-y": False}))) 
        
        plots.append(Plot.make1D("{0}_mll".format(uname), 
                op.invariant_mass(lepton[0].p4, lepton[1].p4), sel, 
                EqB(60, 70., 110.), 
                title= "mll [GeV]", plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D("{0}_llpT".format(uname), 
                (dilepton[0].p4 + dilepton[1].p4).Pt(), sel, 
                EqB(60,0.,450.),
                title= "dilepton P_{T} [GeV]", plotopts=utils.getOpts(uname)))
    # FIXME
    #plots.append(Plot.make1D("{0}_nVX".format(uname), 
    #            t.PV.npvs, sel, 
    #            EqB(10, 0., 60.), 
    #            title="Distrubtion of the number of the reconstructed vertices", 
    #            xTitle="number of reconstructed vertices "))
    #plots.append(Plot.make2D("{0}_Electron_dzdxy".format(uname), 
    #            (lepton[0].dz ,lepton[0].dxy), sel, 
    #            (EqB(10, 0., 2.),
    #            EqB(10, 0., 2.)) ,
    #            title="Electron in Barrel/EndCAP region" ))
    return plots


def makeControlPlotsForBasicSel(self, sel, jets, dilepton, uname):
    binScaling =1
    plots =[]
    plots.append(Plot.make1D("{0}_leadJetPT".format(uname), 
                jets[0].pt, sel, 
                EqB(60, 0., 450.), 
                title= "P_{T} (leading Jet) [GeV]", plotopts=utils.getOpts(uname)))
    plots.append(Plot.make1D("{0}_subleadJetPT".format(uname), 
                jets[1].pt, sel,
                EqB(60, 0., 450.), 
                title= "P_{T} (sub-leading Jet) [GeV]", plotopts=utils.getOpts(uname)))
        
    plots.append(Plot.make1D("{0}_leadJetETA".format(uname), 
                jets[0].eta, sel,
                EqB(10, -2.4, 2.4), 
                title="Eta (leading Jet)", plotopts=utils.getOpts(uname)))
    plots.append(Plot.make1D("{0}_subleadJetETA".format(uname), 
                jets[1].eta, sel, 
                EqB(10, -2.4, 2.4), 
                title="Eta (sub-leading Jet)", plotopts=utils.getOpts(uname)))
    
    for i in range(2):        
        plots.append(Plot.make1D(f"{uname}_jet{i+1}_phi", jets[i].phi, sel,
                    EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} jet phi", plotopts=utils.getOpts(uname, **{"log-y": False})))


    plots.append(Plot.make1D("{0}_jjpT".format(uname), 
                (jets[0].p4 + jets[1].p4).pt, sel, 
                EqB(100, 0., 450.),
                title= "dijet P_{T} [GeV]", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make1D("{0}_jjPhi".format(uname), 
                (jets[0].p4 + jets[1].p4).phi, sel, 
                EqB(50 // binScaling, -3.1416, 3.1416),
                title= "dijet phi", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make1D("{0}_jjEta".format(uname), 
                (jets[0].p4 + jets[1].p4).eta, sel, 
                EqB(50 // binScaling, -2.4, 2.4),
                title= "dijet eta", plotopts=utils.getOpts(uname)))
    
    plots.append(Plot.make1D("{0}_mjj".format(uname),
                op.invariant_mass(jets[0].p4, jets[1].p4), sel, 
                EqB(100, 0., 800.), 
                title="mjj [GeV]", plotopts=utils.getOpts(uname)))
    
    
    plots.append(Plot.make1D("{0}_mlljj".format(uname), 
                (dilepton[0].p4 +dilepton[1].p4+jets[0].p4+jets[1].p4).M(), sel, 
                EqB(100, 0., 1000.), 
                title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
    plots.append(Plot.make2D("{0}_mlljjvsmjj".format(uname), 
                (op.invariant_mass(jets[0].p4, jets[1].p4),
                (dilepton[0].p4 + dilepton[1].p4 + jets[0].p4 + jets[1].p4).M()), sel, 
                (EqB(1000, 0., 1000.), EqB(1000, 0., 1000.)), 
                title="mlljj vs mjj invariant mass [Gev]", plotopts=utils.getOpts(uname)))
    return plots
            
def makeControlPlotsForFinalSel(self, sel, bjets, dilepton, uname):
    plots =[]
    binScaling=1
    for key in sel.keys():

        tagger=key.replace(wp, "")
        bjets_ = safeget(bjets, tagger, wp)
    
        plots.append(Plot.make1D("{0}_TwoBtaggedJets_pT_{1}".format(uname, key), 
                    (bjets_[0].p4+bjets_[1].p4).Pt(),
                    sel.get(key), 
                    EqB(60,170.,800.),
                    title= "di-bjet P_{T} [GeV]", plotopts=utils.getOpts(uname)))
        
        plots.append(Plot.make1D("{0}_mlljj_btagged_{1}".format(uname, key), 
                    (lepton[0].p4 +lepton[1].p4+bjets_[0].p4+bjets_[1].p4).M(),
                    sel.get(key),
                    EqB(60, 170., 1000.), 
                    title="mlljj [GeV]", plotopts=utils.getOpts(uname)))
        
        plots.append(Plot.make1D("{0}_mjj_btagged_{1}".format(uname, key),
                    op.invariant_mass(bjets_[0].p4+bjets_[1].p4) , 
                    sel.get(key),
                    EqB(60, 170., 800.), 
                    title= "mjj [GeV]", plotopts=utils.getOpts(uname)))

        plots.append(Plot.make2D("{0}_mlljjvsmjj_btagged_{1}".format(uname, key), 
                    (op.invariant_mass(bjets_[0].p4+bjets_[1].p4) , 
                    (lepton[0].p4 +lepton[1].p4+bjets_[0].p4+bjets_[1].p4).M()),
                    sel.get(key),
                    (EqB(60, 170., 1000.), 
                    EqB(60, 170., 1000.)), 
                    title="mlljj vs mjj invariant mass [GeV]", plotopts=utils.getOpts(uname)))
    return plots 

def makeResolvedJetPlots(self, sel, jets, uname):
    maxJet=2
    binScaling=1
    plots = []
    for i in range(maxJet):
        plots.append(Plot.make1D(f"{uname}_jet{i+1}_pt", jets[i].pt, sel,
                    EqB(60 // binScaling, 30., 730. - max(4, i) * 100), title=f"{utils.getCounter(i+1)} jet p_{{T}} [GeV]",
                    plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_jet{i+1}_eta", jets[i].eta, sel,
                    EqB(50 // binScaling, -2.4, 2.4), title=f"{utils.getCounter(i+1)} jet eta",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D(f"{uname}_jet{i+1}_phi", jets[i].phi, sel,
                    EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} jet phi", plotopts=utils.getOpts(uname, **{"log-y": False})))

        
    plots.append(Plot.make1D(f"{uname}_jet_DR", op.deltaR(jets[0].p4, jets[1].p4),
                sel, EqB(50, 0.3, 3.), title="Jets DR",
                plotopts=utils.getOpts(uname, **{"log-y": False})))
    plots.append(Plot.make1D(f"{uname}_jet_M", op.invariant_mass(jets[0].p4, jets[1].p4),
                sel, EqB(60, 0., 400.),
                title="dijets invariant mass [GeV]", plotopts=utils.getOpts(uname)))
    plots.append(Plot.make1D(f"{uname}_jet_pT", (jets[0].p4 + jets[1].p4).Pt(),
                sel, EqB(60, 0., 600.), title=" dijets p_{T} [GeV]",
                plotopts=utils.getOpts(uname)))
    return plots

def makeBoostedJetPLots(self, sel, jets, uname):
    maxJet=1
    binScaling=1
    plots = []
    for i in range(maxJet):
        plots.append(Plot.make1D(f"{uname}_boostedjet{i+1}_pt", jets[i].pt, sel,
            EqB(60 , 170., 800.), title=f"{utils.getCounter(i+1)} jet p_{{T}} [GeV]",
                    plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_boostedjet{i+1}_eta", jets[i].eta, sel,
                    EqB(50 // binScaling, -2.4, 2.4), title=f"{utils.getCounter(i+1)} jet eta",
                    plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_boostedjet{i+1}_phi", jets[i].phi, sel,
                    EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} jet phi", plotopts=utils.getOpts(uname)))
        plots.append(Plot.make1D(f"{uname}_boostedjet{i+1}_mass", jets[i].phi, sel,
                    EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} jet mass [GeV]", plotopts=utils.getOpts(uname)))

    return plots

def makeResolvedBJetPlots(self, sel, bjets, wp, uname):
    plots =[]
    binScaling=1
    for key in sel.keys():
        
        tagger=key.replace(wp, "")
        bjets_ = safeget(bjets, tagger, wp) 
        
        plots.append(Plot.make1D("{0}_nBJets_{1}".format(uname, key), 
                    op.rng_len(bjets_), sel.get(key), 
                    EqB(5, 2., 6.), 
                    xTitle= "Jets multiplicty {0}".format(key),  plotopts=utils.getOpts(uname)))
        for i in range(1):
            plots.append(Plot.make1D(f"{uname}_bjet{i+1}_pT_{key}", 
                        bjets_[i].pt, sel.get(key), 
                        EqB(60, 0., 800.),
                        title=f"{utils.getCounter(i+1)}-highest bjet pT {key} [GeV]", plotopts=utils.getOpts(uname)))
        
            plots.append(Plot.make1D(f"{uname}_bjet{i+1}_eta_{key}", 
                        bjets_[i].eta, sel.get(key),
                        EqB(50 // binScaling, -2.4, 2.4), 
                        title=f"{utils.getCounter(i+1)}-highest bjet eta {key}", plotopts=utils.getOpts(uname)))
            
            plots.append(Plot.make1D(f"{uname}_bjet{i+1}_eta_{key}", 
                        bjets_[i].phi, sel.get(key),
                        EqB(50 // binScaling, -3.1416, 3.1416), 
                        title=f"{utils.getCounter(i+1)}-highest bjet phi {key}", plotopts=utils.getOpts(uname)))
    return plots

def makeBoostedJetPLots(self, sel, bjets, wp, uname):
    maxJet=1
    binScaling=1
    plots =[]

    for key in sel.keys():
        tagger=key.replace(wp, "")
        bjets_ = safeget(bjets, tagger, wp)
        
        for i in range(maxJet):
            plots.append(Plot.make1D(f"{uname}_boostedjet{i+1}_pt", bjets_[i].pt, sel,
                        EqB(60 , 170., 800.), title=f"{utils.getCounter(i+1)} jet p_{{T}} [GeV]",
                        plotopts=utils.getOpts(uname)))
            plots.append(Plot.make1D(f"{uname}_boostedjet{i+1}_eta", bjets_[i].eta, sel,
                        EqB(50 // binScaling, -2.4, 2.4), title=f"{utils.getCounter(i+1)} jet eta",
                        plotopts=utils.getOpts(uname)))
            plots.append(Plot.make1D(f"{uname}_boostedjet{i+1}_phi", bjets_[i].phi, sel,
                        EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} jet phi", plotopts=utils.getOpts(uname)))
            plots.append(Plot.make1D(f"{uname}_boostedjet{i+1}_mass", bjets_[i].phi, sel,
                        EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} jet mass [GeV]", plotopts=utils.getOpts(uname)))

    return plots 
