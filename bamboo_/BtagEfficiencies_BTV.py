import os
import sys

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_')
import utils
from ControlPLots import safeget
import ControlPLots as cp
import HistogramTools as HT
import logging
logger = logging.getLogger("H->ZA->llbb : BtagEfficiencies Plotter")
from bamboo.analysismodules import NanoAODHistoModule
from bamboo import treefunctions as op
from bamboo.plots import Plot, SummedPlot
from bamboo.plots import EquidistantBinning as EqBin
from bamboo.plots import VariableBinning as VarBin
from utils import *
import utils 
def MakeBtagEfficienciesPlots(self, jets, bjets, categories, era):

    if isMC:
        bFlavJets = op.select(jets, lambda j: j.hadronFlavour == 5)
        cFlavJets = op.select(jets, lambda j: j.hadronFlavour == 4)
        lFlavJets = op.select(jets, lambda j: j.hadronFlavour == 0)
    #else:
    #    bFlavJets = cFlavJets = lFlavJets = jets
    for channel, (dilepton, catSel) in categories.items():
        if channel=="ElMu":
            muelJetsSel = catSel.refine("twoJet{0}Sel_".format(channel), cut=[ op.rng_len(jets) > 1 ])
        elif channel=="MuEl":
            elmuTwoJetsSel = catSel.refine("twoJet{0}Sel_".format(channel), cut=[ op.rng_len(jets) > 1 ])
        elif channel=="MuMu":
            mumuTwoJetsSel = catSel.refine("twoJet{0}Sel_".format(channel), cut=[ op.rng_len(jets) > 1 ])
        elif channel=="ElEl":
            elelTwoJetsSel = catSel.refine("twoJet{0}Sel_".format(channel), cut=[ op.rng_len(jets) > 1 ])

    plots = []
    for flav, flavJets in zip(['b', 'c', 'light'], [bFlavJets, cFlavJets, lFlavJets]):
    # b tagging efficiencies as a function of flavour/pt/|eta|
        binning = (VarBin([30, 40, 60, 80, 100, 200, 350, 1000]), EqBin(5, 0, 2.5))

        pt = op.map(flavJets, lambda j: j.pt)
        eta = op.map(flavJets, lambda j: op.abs(j.eta))
        plots.append(Plot.make2D(f"1el1mu_atleast2j_jet_pt_eta_{flav}flav", (pt, eta), elmuTwoJetsSel, binning))
        plots.append(Plot.make2D(f"1mu1el_atleast2j_jet_pt_eta_{flav}flav", (pt, eta), muelJetsSel, binning))
        plots.append(SummedPlot(f"pair_lept_OSOF_atleast2j_jet_pt_eta_{flav}flav", plots[-2:-1]))
        
        plots.append(Plot.make2D(f"1mu1mu_atleast2j_jet_pt_eta_{flav}flav", (pt, eta), mumuTwoJetsSel, binning))
        plots.append(Plot.make2D(f"1el1el_atleast2j_jet_pt_eta_{flav}flav", (pt, eta), elelTwoJetsSel, binning))
        plots.append(SummedPlot(f"pair_lept_OSSF_atleast2j_jet_pt_eta_{flav}flav", plots[-2:-1]))

    jetPairs = op.combine(jets, N=2)
    minJetDR = op.rng_min(jetPairs, lambda pair: op.deltaR(pair[0].p4, pair[1].p4))
    bJetPairs = op.combine(bFlavJets, N=2)
    minBJetDR = op.rng_min(bJetPairs, lambda pair: op.deltaR(pair[0].p4, pair[1].p4))
    lightJetPairs = op.combine(lFlavJets, N=2)
    minLightJetDR = op.rng_min(lightJetPairs, lambda pair: op.deltaR(pair[0].p4, pair[1].p4))

    for vari, sel in zip(["1el1mu", "1mu1el"], [elmuTwoJetsSel, muelJetsSel]):
        plots.append(Plot.make1D(vari +"_minJetDR", minJetDR, sel, EqBin(40, 0.4, 2.), plotopts=utils.getOpts(vari.replace("1",""))))
        plots.append(Plot.make1D(vari + "_minBJetDR", minBJetDR, sel, EqBin(40, 0.4, 2.), plotopts=utils.getOpts(vari.replace("1", ""))))
        plots.append(Plot.make1D(vari + "_minLightJetDR", minLightJetDR, sel, EqBin(40, 0.4, 2.), plotopts=utils.getOpts(vari.replace("1",""))))

        #plots += cp.makeJetPlots(sel, jets, vari, maxJet=2, binScaling=2)
    btagging = {
            "DeepCSV":{ # era: (loose, medium, tight)
                        "2016":(0.2217, 0.6321, 0.8953), 
                        "2017":(0.1522, 0.4941, 0.8001), 
                        "2018":(0.1241, 0.4184, 0.7527) 
                        },
            "DeepFlavour":{
                        "2016":(0.0614, 0.3093, 0.7221), 
                        "2017":(0.0521, 0.3033, 0.7489), 
                        "2018":(0.0494, 0.2770, 0.7264) 
                        }
                }
    # look at specific slice in pt/|eta|
    jetSel = lambda j: op.AND(op.in_range(30., j.pt, 1000.), op.in_range(-2.5, j.eta, 2.5))
    selBJets = op.select(bFlavJets, jetSel)
    selLightJets = op.select(lFlavJets, jetSel)
    
    # b and light jets which have - or not - another jet within DeltaR < 0.4
    selBJetsMaxDR = op.select(selBJets, lambda jet: op.NOT(op.rng_any(jets, lambda j: op.AND(jet != j, op.deltaR(jet.p4, j.p4) < 0.4))))
    selBJetsMinDR = op.select(selBJets, lambda jet: op.rng_any(jets, lambda j: op.AND(jet != j, op.deltaR(jet.p4, j.p4) < 0.4)))
    selLightJetsMaxDR = op.select(selLightJets, lambda jet: op.NOT(op.rng_any(jets, lambda j: op.AND(jet != j, op.deltaR(jet.p4, j.p4) < 0.4))))
    selLightJetsMinDR = op.select(selLightJets, lambda jet: op.rng_any(jets, lambda j: op.AND(jet != j, op.deltaR(jet.p4, j.p4) < 0.4)))

    def returnselforchannel(self, categories, jets, nbJets, channel, ext):
        for cat, (dilepton, catSel) in categories.items():
            if cat not in channel:
                continue
            if nbJets in range(3) :
                OSOFlep_JetsSel = catSel.refine("%s_%sjets_ext%s"%(channel, nbJets, ext), cut=op.rng_len(jets)==nbJets)
            else:
                OSOFlep_JetsSel = catSel.refine("%s_atleast2jets_ext%s"%(channel, ext), cut=op.rng_len(jets)>1)
        return OSOFlep_JetsSel
    for ext, tagger in enumerate(btagging.keys()):
        for wp, discr in zip(["L", "M", "T"], btagging[tagger][era]):
            print ( tagger, wp)
            print(  btagging[tagger][era])
            print( discr )
            bJets_ = safeget(bjets, tagger, wp)
            print( bJets_)             
            if bJets_ is None:
                #raise RuntimeError("era: {0}, {1} WorkingPoint not passed in --module NanoHtoZA".format(era, wp))
                logger.info("era: {0}, {1} WorkingPoint not passed in --module NanoHtoZA ".format(era, wp))
            if tagger == "DeepFlavour":
                selJets = op.select(flavJets, lambda j: j.btagDeepFlavB >= discr)
                lambda_ = lambda j: j.btagDeepFlavB
                suffix = "deepFlav"
            elif tagger =="DeepCSV":
                selJets = op.select(flavJets, lambda j: j.btagDeepB >= discr)
                lambda_ = lambda j: j.btagDeepB
                suffix = "deepB"

            pt = op.map(selJets, lambda j: j.pt)
            eta = op.map(selJets, lambda j: op.abs(j.eta))
            plots.append(Plot.make2D(f"1el1mu_atleast2j_jet_pt_eta_{flav}_{tagger}{wp}", (pt, eta), elmuTwoJetsSel, binning))
            plots.append(Plot.make2D(f"1mu1el_atleast2j_jet_pt_eta_{flav}_{tagger}{wp}", (pt, eta), muelJetsSel, binning))
            plots.append(SummedPlot(f"pair_lept_OSSF_atleast2j_jet_pt_eta_{flav}_{tagger}{wp}", plots[-2:-1]))

            for vari, sel in zip(["1el1mu", "1mu1el"], [elmuTwoJetsSel, muelJetsSel]):
                #plots += cp.makeBJetPlots(sel, bJets_, vari)
                plots.append(Plot.make1D(vari + "_nbJets_%s%s"%(tagger, wp), op.rng_len(bJets_), sel, EqBin(7, 0., 7.), title="Number of %s%s b jets"%(tagger, wp), plotopts=utils.getOpts(vari.replace("1",""))))
        
        # b-tagger shape for specific jet multiplicities
        for vari, channel in zip(["1el1mu", "1mu1el"], ["ElMu", "MuEl"]):
            zeroJetsSel= returnselforchannel(self, categories, jets, 0, channel, ext) 
            oneJetsSel = returnselforchannel(self, categories, jets, 1, channel, ext)
            twoJetsSel = returnselforchannel(self, categories, jets, 2, channel, ext)
            atleast2JetsSel = returnselforchannel(self, categories, jets, "atlest2", channel, ext)
            for i, nJetSel in zip (["0", "1", "2", "atleast2"], [ zeroJetsSel, oneJetsSel, twoJetsSel, atleast2JetsSel]):
            
                plots.append(Plot.make1D("%s_%sj_bJet_%s"%(vari, i, suffix), op.map(selBJets, lambda_), nJetSel, EqBin(30, 0., 1.)))
                plots.append(Plot.make1D("%s_%sj_lightJet_%s"%(vari, i, suffix), op.map(selLightJets, lambda_), nJetSel, EqBin(30, 0., 1.)))
    
                plots.append(Plot.make1D(f"%s_%sj_minDR_bJet_%s"%(vari, i, suffix), op.map(selBJetsMinDR, lambda_), nJetSel, EqBin(30, 0., 1.)))
                plots.append(Plot.make1D(f"%s_%sj_minDR_lightJet_%s"%(vari, i, suffix), op.map(selLightJetsMinDR, lambda_), nJetSel, EqBin(30, 0., 1.)))
                plots.append(Plot.make1D(f"%s_%sj_maxDR_bJet_%s"%(vari, i, suffix), op.map(selBJetsMaxDR, lambda_), nJetSel, EqBin(30, 0., 1.)))
                plots.append(Plot.make1D(f"%s_%sj_maxDR_lightJet_%s"%(vari, i, suffix), op.map(selLightJetsMaxDR, lambda_), nJetSel, EqBin(30, 0., 1.)))
    
    return plots
    
    def postProcess(self, taskList, config=None, workdir=None, resultsdir=None):
    ## Get list of plots (taken from bamboo.HistogramsModule)
        if not self.plotList:
            tup, smpName, smpCfg = self.getATree()
            tree, noSel, backend, runAndLS = self.prepareTree(tup, sample=smpName, sampleCfg=smpCfg)
            self.plotList = self.definePlots(tree, noSel, sample=smpName, sampleCfg=smpCfg)

        # merge processes using their cross sections
        utils.normalizeAndMergeSamples(self.plotList, self.readCounters, config, resultsdir, os.path.join(resultsdir, "mergedProcesses.root"))
        def getRatio(f, n, d, suffix):
            num = f.Get(n)
            den = f.Get(d)
            ratio = num.Clone(num.GetName() + suffix)
            ratio.Divide(den)
            return ratio

        for proc in list(config["samples"].keys()) + ["mergedProcesses"]:
            tf = HT.openFileAndGet(os.path.join(resultsdir, proc +".root"), "update")

            # compute ratio histogram needed to correct the jet multiplicity
            getRatio(tf, "1lep_nJets", "1lep_shape_nJets", "_sfCorr").Write()

            # compute efficiencies (divide histo after cut by total histo)
            for flav in ["b", "c", "light"]:
                for wp in ["L", "M", "T"]:
                    getRatio(tf, f"pair_lept_OSSF_atleast2j_jet_pt_eta_{flav}_wp{wp}", f"pair_lept_OSSF_atleast2j_jet_pt_eta_{flav}", "_eff").Write()         
            
            tf.Close()
