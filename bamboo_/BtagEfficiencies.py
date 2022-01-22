import os, os.path
import sys
import yaml

from bamboo import treefunctions as op
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqBin
from bamboo.plots import VariableBinning as VarBin
from bamboo.analysismodules import NanoAODHistoModule, HistogramsModule

zabPath = os.path.dirname(__file__)
if zabPath not in sys.path:
    sys.path.append(zabPath)

import utils as utils
logger = utils.ZAlogger(__name__)

import ControlPLots as cp
import HistogramTools as HT
from ZAtollbb import NanoHtoZABase

class  ZA_BTagEfficiencies(NanoHtoZABase, HistogramsModule):
    def __init__(self, args):
        super(ZA_BTagEfficiencies, self).__init__(args)
    
    def definePlots(self, t, noSel, sample=None, sampleCfg=None):

        from bambooToOls import Plot
        from bamboo.plots import CutFlowReport

        noSel, puWeightsFile, PUWeight, categories, isDY_reweight, WorkingPoints, BoostedTopologiesWP, legacy_btagging_wpdiscr_cuts, deepBFlavScaleFactor, deepB_AK4ScaleFactor, deepB_AK8ScaleFactor, AK4jets, AK8jets, fatjets_nosubjettinessCut, bjets_resolved, bjets_boosted, CleanJets_fromPileup, electrons, muons, MET, corrMET, PuppiMET, elRecoSF_highpt, elRecoSF_lowpt, isULegacy = super(ZA_BTagEfficiencies, self).defineObjects(t, noSel, sample, sampleCfg)
        
        year = sampleCfg.get("era") if sampleCfg else None
        isMC = self.isMC(sample)
        
        ZOOM_PT_ETA_BINS      = True
        plot_deltaR           = False
        plot_Jetsmultiplicity = False
        
        binScaling = 1
        plots = []

        
        eoy_btagging_wpdiscr_cuts = {
                "resolved": {
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
                    },
                "boosted":{
                    "DeepCSV": {
                        "2016": (0.2217, 0.6321), 
                        "2017":(0.1522, 0.4941), 
                        "2018":(0.1241, 0.4184) 
                        },
                    }
                }

        
        legacy_btagging_wpdiscr_cuts = {
                "resolved": {
                    "DeepCSV":{ # era: (loose, medium, tight)
                        "2016-preVFP" :(0.2027, 0.6001, 0.8819), 
                        "2016-postVFP":(0.1918, 0.5847, 0.8767), 
                        "2017":(0.1355, 0.4506, 0.7738), 
                        "2018":(0.1208, 0.4168,  0.7665) 
                        },
                    "DeepFlavour":{
                        "2016-preVFP" :(0.0508, 0.2598, 0.6502), 
                        "2016-postVFP":( 0.0480, 0.2489, 0.6377), 
                        "2017":(0.0532, 0.3040, 0.7476), 
                        "2018":(0.0490, 0.2783, 0.7100) 
                        }
                    },
                "boosted":{ 
                    "DeepCSV": {
                        "2016-preVFP" :(0.2217, 0.6321), 
                        "2016-postVFP":(0.1918, 0.5847), 
                        "2017":(0.1522, 0.4941), 
                        "2018":(0.1241, 0.4184) 
                        },
                    }
                }
        
        discriminatorcuts_lib = (legacy_btagging_wpdiscr_cuts if isULegacy else (eoy_btagging_wpdiscr_cuts))  
        
        processes_dic = { "gg_fusion":{ 
                                        "resolved": op.AND(op.rng_len(AK4jets) == 2, op.rng_len(AK8jets) == 0),
                                        "boosted" : op.AND(op.rng_len(AK8jets) == 1, op.rng_len(AK4jets) == 0) },
                          "bb_associatedProduction":{
                                        "resolved": op.AND(op.rng_len(AK4jets) >= 3, op.rng_len(AK8jets) == 0),
                                        "boosted" : op.AND(op.rng_len(AK4jets) >= 0, op.rng_len(AK8jets) >= 1) }
                        }

        for process, njetscut in processes_dic.items():
            
            proc = "ggH" if process=="gg_fusion" else ("bbH")

            lljj_selections_percat_resolved = { channel.lower() : catSel.refine("twolep_%s_%s_resolved_selection"%(channel.lower(), process), cut=[ njetscut["resolved"]] ) 
                                                    for channel, (dilepton, catSel) in categories.items() }
            lljj_selections_percat_boosted  = { channel.lower() : catSel.refine("twolep_%s_%s_boosted_selection"%(channel.lower(), process), cut=[ njetscut["boosted"]] ) 
                                                    for channel, (dilepton, catSel) in categories.items() }
        
            lljj_selections_perreg= {"resolved": lljj_selections_percat_resolved, "boosted": lljj_selections_percat_boosted }
        
        
            for reg, lljj_selections_percat in lljj_selections_perreg.items():
    
                # Nbr of subjettiness cut to be studied 
                jets = (AK4jets if reg=="resolved" else (AK8jets))
                
                jets_length = { "gg_fusion": {
                                        "resolved":2,
                                        "boosted" :1},
                                "bb_associatedProduction":{
                                        "resolved":3,
                                        "boosted" :1}
                                }
                if isMC:
                    bFlavJets = op.select(jets, lambda j: j.hadronFlavour == 5)
                    cFlavJets = op.select(jets, lambda j: j.hadronFlavour == 4)
                    lFlavJets = op.select(jets, lambda j: j.hadronFlavour == 0)
    
                if reg == "resolved":
                    JetPairs      = op.combine(jets, N=2)
                    bJetPairs     = op.combine(bFlavJets, N=2)
                    cJetPairs     = op.combine(cFlavJets, N=2)
                    lightJetPairs = op.combine(lFlavJets, N=2)
                

                    if plot_deltaR:
                        minJetDR      = op.rng_min(JetPairs, lambda pair: op.deltaR(pair[0].p4, pair[1].p4))
                        minBJetDR     = op.rng_min(bJetPairs, lambda pair: op.deltaR(pair[0].p4, pair[1].p4))
                        minBJetDR     = op.rng_min(cJetPairs, lambda pair: op.deltaR(pair[0].p4, pair[1].p4))
                        minLightJetDR = op.rng_min(lightJetPairs, lambda pair: op.deltaR(pair[0].p4, pair[1].p4))
                        
                        for uname, sel in lljj_selections_percat.items(): 
                            plots.append(Plot.make1D(uname + f"_2jets_minJetDR_{reg}_{process}", minJetDR, sel, EqBin(40, 0.4, 2.), plotopts=utils.getOpts(uname)))
                            plots.append(Plot.make1D(uname + f"_2bjets_minBJetDR_{reg}_{process}", minBJetDR, sel, EqBin(40, 0.4, 2.), plotopts=utils.getOpts(uname)))
                            plots.append(Plot.make1D(uname + f"_2cjets_minBJetDR_{reg}_{process}", minBJetDR, sel, EqBin(40, 0.4, 2.), plotopts=utils.getOpts(uname)))
                            plots.append(Plot.make1D(uname + f"_2lightjets_minLightJetDR_{reg}_{process}", minLightJetDR, sel, EqBin(40, 0.4, 2.), plotopts=utils.getOpts(uname)))
    
    
                for flav, flavJets in zip(['b', 'c', 'light'], [bFlavJets, cFlavJets, lFlavJets]):
                    # b tagging efficiencies as a function of flavour/pt/|eta|
                    if reg=='resolved':
                        if year=='2016':
                            binning = ( VarBin([20., 30., 50., 70., 100., 140., 200., 300.,  600., 1000.]) , VarBin([-2.5,-2.0,-1.566,-1.4442, -0.8, 0.0, 0.8, 1.4442, 1.566, 2.0, 2.5]) )
                            firstpt = 20.
                            lastpt  = 200.
                        else:
                            binning = ( VarBin([30., 50., 70., 100., 140., 200., 300.,  600., 1000.]) , VarBin([-2.5,-2.0,-1.566,-1.4442, -0.8, 0.0, 0.8, 1.4442, 1.566, 2.0, 2.5]) )
                            firstpt = 30.
                            lastpt  = 200.
                    else: 
                        binning = ( VarBin([200., 250., 300., 350., 450., 500., 600., 800., 1000.]) , VarBin([-2.5,-2.0,-1.566,-1.4442, -0.8, 0.0, 0.8, 1.4442, 1.566, 2.0, 2.5]) )
                        firstpt = 200.
                        lastpt  = 800.
    
                    pt  = op.map(flavJets, lambda j: j.pt)
                    eta = op.map(flavJets, lambda j: j.eta)
                    ZOOM_BINS = (EqBin(20//binScaling, firstpt, lastpt) , VarBin([-2.5,-2.0,-1.566,-1.4442, -0.8, 0.0, 0.8, 1.4442, 1.566, 2.0, 2.5])) 
                    
                    plots.append(Plot.make2D(f"2mu_2j_jet_pt_eta_{flav}flav_{reg}_{process}", (pt, eta), lljj_selections_percat['mumu'], binning, title=f"{proc} efficiency {flav} hadronFlavour Jet", xTitle="p_{T} [GeV]",yTitle="#eta"))
                    plots.append(Plot.make2D(f"2el_2j_jet_pt_eta_{flav}flav_{reg}_{process}", (pt, eta), lljj_selections_percat['elel'], binning, title=f"{proc} efficiency {flav} hadronFlavour Jet", xTitle="p_{T} [GeV]",yTitle="#eta"))
                    #plots.append(Plot.make2D(f"1el1mu_2j_jet_pt_eta_{flav}_{reg}", (pt, eta), lljj_selections_percat['elmu'], binning, title=f"{proc} Efficiency {flav} hadronFlavour Jet", xTitle="p_{T} [GeV]",yTitle="#eta"))
                    plots.append(Plot.make2D(f"1mu1el_2j_jet_pt_eta_{flav}flav_{reg}_{process}", (pt, eta), lljj_selections_percat['muel'], binning, title=f"{proc} efficiency {flav} hadronFlavour Jet", xTitle="p_{T} [GeV]",yTitle="#eta"))
                    plots.append(SummedPlot(f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_{process}", plots[-3:-2:1]))
        
                    if ZOOM_PT_ETA_BINS:
                        plots.append(Plot.make2D(f"2mu_2j_jet_pt_eta_{flav}flav_{reg}_ZOOM_PT_ETA_BINS_{process}", (pt, eta), lljj_selections_percat['mumu'], ZOOM_BINS, title=f"{proc} efficiency {flav} hadronFlavour Jet", xTitle="p_{T} [GeV]",yTitle="#eta"))
                        plots.append(Plot.make2D(f"2el_2j_jet_pt_eta_{flav}flav_{reg}_ZOOM_PT_ETA_BINS_{process}", (pt, eta), lljj_selections_percat['elel'], ZOOM_BINS, title=f"{proc} efficiency {flav} hadronFlavour Jet", xTitle="p_{T} [GeV]",yTitle="#eta"))
                        #plots.append(Plot.make2D(f"1el1mu_2j_jet_pt_eta_{flav}_{reg}_ZOOM_PT_ETA_BINS_{process}", (pt, eta), lljj_selections_percat['elmu'], ZOOM_BINS, title=f"{proc} efficiency {flav} hadronFlavour Jet", xTitle="p_{T} [GeV]",yTitle="#eta"))
                        plots.append(Plot.make2D(f"1mu1el_2j_jet_pt_eta_{flav}flav_{reg}_ZOOM_PT_ETA_BINS_{process}", (pt, eta), lljj_selections_percat['muel'], ZOOM_BINS, title=f"{proc} efficiency {flav} hadronFlavour Jet", xTitle="p_{T} [GeV]",yTitle="#eta"))
                        plots.append(SummedPlot(f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_ZOOM_PT_ETA_BINS_{process}", plots[-3:-2:1]))
            
                    if plot_Jetsmultiplicity:
                        plots.append(Plot.make1D(f"2mu_n{flav}jets_hadronFlav_{reg}_{process}", op.rng_len(flavJets), lljj_selections_percat['mumu'], EqBin(6, 0, 6), title=f"{flav}Jets multiplicity"))
                        plots.append(Plot.make1D(f"2el_n{flav}jets_hadronFlav_{reg}_{process}", op.rng_len(flavJets), lljj_selections_percat['elel'], EqBin(6, 0, 6), title=f"{flav}Jets multiplicity"))
                        #plots.append(Plot.make1D(f"1el1mu_n{flav}jets_hadronFlav_{reg}_{process}", op.rng_len(flavJets), lljj_selections_percat['elmu'], EqBin(6, 0, 6), title=f"{flav}jets multiplicity"))
                        plots.append(Plot.make1D(f"1mu1el_n{flav}jets_hadronFlav_{reg}_{process}", op.rng_len(flavJets), lljj_selections_percat['muel'], EqBin(6, 0, 6), title=f"{flav}Jets multiplicity"))
                        plots.append(SummedPlot(f"pair_lept_2j_jet_multiplicity_{flav}flav_{reg}_{process}", plots[-3:-2:1]))
            
                    OperatingPoints= ['L', 'M']
                    if reg == "resolved":
                        OperatingPoints.append( "T" )
                    
                    for tagger in discriminatorcuts_lib[reg].keys(): 
                        for (wp, deepThr) in zip( OperatingPoints, discriminatorcuts_lib[reg][tagger][year]):
                            
                            selJets = ( op.select(flavJets, lambda j: j.btagDeepFlavB >= deepThr) if tagger=='DeepFlavour' else (op.select(flavJets, lambda j: j.btagDeepB >= deepThr )))
        
                            pt  = op.map(selJets, lambda j: j.pt)
                            eta = op.map(selJets, lambda j: j.eta)
                            
                            discr  = f"btagDeepFlavB_{wp}" if tagger=='DeepFlavour' else f"btagDeepB_{wp}"
                            tagger = tagger.lower()

                            plots.append(Plot.make2D(f"2mu_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}_{process}", (pt, eta), lljj_selections_percat['mumu'], binning, title=f"{proc} efficiency {flav} hadronFlavour Jet {discr}", xTitle="p_{T} [GeV]",yTitle="#eta"))
                            plots.append(Plot.make2D(f"2el_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}_{process}", (pt, eta), lljj_selections_percat['elel'], binning, title=f"{proc} efficiency {flav} hadronFlavour Jet {discr}", xTitle="p_{T} [GeV]",yTitle="#eta"))
                            #plots.append(Plot.make2D(f"1el1mu_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}_{process}", (pt, eta), lljj_selections_percat['elmu'], binning, title=f"{proc} efficiency {flav} hadronFlavour Jet {discr}", xTitle="p_{T} [GeV]",yTitle="#eta"))
                            plots.append(Plot.make2D(f"1mu1el_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}_{process}", (pt, eta), lljj_selections_percat['muel'], binning, title=f"{proc} efficiency {flav} hadronFlavour Jet {discr}", xTitle="p_{T} [GeV]",yTitle="#eta"))
                            plots.append(SummedPlot(f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_{tagger}_wp{wp}_{process}", plots[-3:-2:1]))
                            
                            if ZOOM_PT_ETA_BINS:
                                plots.append(Plot.make2D(f"2mu_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}_{process}_ZOOM_PT_ETA_BINS", (pt, eta), lljj_selections_percat['mumu'], ZOOM_BINS, title=f"{proc} efficiency {flav} hadronFlavour Jet {discr}", xTitle="p_{T} [GeV]",yTitle="#eta"))
                                plots.append(Plot.make2D(f"2el_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}_{process}_ZOOM_PT_ETA_BINS", (pt, eta), lljj_selections_percat['elel'], ZOOM_BINS, title=f"{proc} efficiency {flav} hadronFlavour Jet {discr}", xTitle="p_{T} [GeV]",yTitle="#eta"))
                                #plots.append(Plot.make2D(f"1el1mu_2j_jet_pt_eta_{flav}_{reg}_{tagger}_wp{wp}_{process}_ZOOM_PT_ETA_BINS", (pt, eta), lljj_selections_percat['elmu'], ZOOM_BINS, title=f"{proc} efficiency {flav} hadronFlavour Jet {discr}", xTitle="p_{T} [GeV]",yTitle="#eta"))
                                plots.append(Plot.make2D(f"1mu1el_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}_{process}_ZOOM_PT_ETA_BINS", (pt, eta), lljj_selections_percat['muel'], ZOOM_BINS, title=f"{proc} efficiency {flav} hadronFlavour Jet {discr}", xTitle="p_{T} [GeV]",yTitle="#eta"))
                                plots.append(SummedPlot(f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_{tagger}_wp{wp}_{process}_ZOOM_PT_ETA_BINS", plots[-3:-2:1]))
    
                # look at specific slice in pt/|eta|
                if plot_deltaR:
                    jetSel = lambda j: op.AND(op.in_range(80., j.pt, 200.), op.in_range(-1., j.eta, 1.))
                    
                    selBJets     = op.select(bFlavJets, jetSel)
                    selCJets     = op.select(cFlavJets, jetSel)
                    selLightJets = op.select(lFlavJets, jetSel)
    
                    lambdadic = { "resolved":{
                                        'btagDeepFlavB': lambda j: j.btagDeepFlavB,
                                        'btagDeepB'    : lambda j: j.btagDeepB }, 
                                  "boosted":{
                                        'btagDeepB'    : lambda j: j.btagDeepB}
                                }
    
                    for channel, (dilepton, catSel) in categories.items():
                        channel = channel.lower()
                        for lambda_ , discr_cut in lambdadic[reg].items():
                            for i in range(1, jets_length[process][reg]+1):
                                
                                nJetSel = catSel.refine(f"{channel}_{i}jets_{reg}_sel_{lambda_}_{process}", cut=op.rng_len(jets)==i)
                                
                                plots.append(Plot.make1D(f"{channel}_{i}bjets_{reg}sel_{lambda_}_{process}", op.map(selBJets, discr_cut), nJetSel, EqBin(30, 0., 1.), 
                                                        title=f"{utils.getCounter(i+1)} N true bjets {lambda_}", plotopts=utils.getOpts(channel) ))
                                plots.append(Plot.make1D(f"{channel}_{i}cjets_{reg}sel_{lambda_}_{process}", op.map(selCJets, discr_cut), nJetSel, EqBin(30, 0., 1.),
                                                        title=f"{utils.getCounter(i+1)} N true cjets {lambda_}", plotopts=utils.getOpts(channel) )) 
                                plots.append(Plot.make1D(f"{channel}_{i}lightjets_{reg}sel_{lambda_}_{process}", op.map(selLightJets, discr_cut), nJetSel, EqBin(30, 0., 1.),
                                                        title=f"{utils.getCounter(i+1)} N true lightjets {lambda_}", plotopts=utils.getOpts(channel) ))

                    ## b, c and light jets which have - or not - another jet within DeltaR < 0.6
                    deltaR = { 'min': 
                              { 'b': op.select(selBJets, lambda jet: op.rng_any(jets, lambda j: op.AND(jet != j, op.deltaR(jet.p4, j.p4) < 0.6))) ,
                                'c': op.select(selCJets, lambda jet: op.rng_any(jets, lambda j: op.AND(jet != j, op.deltaR(jet.p4, j.p4) < 0.6))),
                                'light': op.select(selLightJets, lambda jet: op.rng_any(jets, lambda j: op.AND(jet != j, op.deltaR(jet.p4, j.p4) < 0.6)))  },
                                'max': 
                              { 'b': op.select(selBJets, lambda jet: op.NOT(op.rng_any(jets, lambda j: op.AND(jet != j, op.deltaR(jet.p4, j.p4) < 0.6)))) ,
                                'c': op.select(selCJets, lambda jet: op.NOT(op.rng_any(jets, lambda j: op.AND(jet != j, op.deltaR(jet.p4, j.p4) < 0.6)))) ,
                                'light':  op.select(selLightJets, lambda jet: op.NOT(op.rng_any(jets, lambda j: op.AND(jet != j, op.deltaR(jet.p4, j.p4) < 0.6)))) }
                            }
        
                    for vari, flavOpts_dic in deltaR.items():
                        for flav, deltaR_val in flavOpts_dic.items():
                            for lambda_ , discr_cut in lambdadic[reg].items():
                                plots.append(Plot.make1D(f"2mu_2j_{vari}DR_{flav}jets_{reg}_{lambda_}_{process}", op.map(deltaR_val, discr_cut ), lljj_selections_percat['mumu'], 
                                                            EqBin(30, 0., 1.), title=f' {vari} #Delta R({flav}, j)' , plotopts=utils.getOpts('mumu')))
                                plots.append(Plot.make1D(f"2el_2j_{vari}DR_{flav}jets_{reg}_{lambda_}_{process}", op.map(deltaR_val, discr_cut ), lljj_selections_percat['elel'], 
                                                            EqBin(30, 0., 1.), title=f' {vari} #Delta R({flav}, j)' , plotopts=utils.getOpts('elel')))
                                #plots.append(Plot.make1D(f"1el1mu_2j_{vari}DR_{flav}jets_{lambda_}", op.map(deltaR_val, discr_cut ), lljj_selections_percat['elmu'], 
                                                            #EqBin(30, 0., 1.),title=f' {vari} #Delta R({flav}, j)' , plotopts=utils.getOpts('elmu')))
                                plots.append(Plot.make1D(f"1mu1el_2j_{vari}DR_{flav}jets_{reg}_{lambda_}_{process}", op.map(deltaR_val, discr_cut ), lljj_selections_percat['muel'], 
                                                            EqBin(30, 0., 1.), title=f' {vari} #Delta R({flav}, j)'  , plotopts=utils.getOpts('muel')))
    
        return plots
        
    def postProcess(self, taskList, config=None, workdir=None, resultsdir=None):
        # run plotIt as defined in HistogramsModule - this will also ensure that self.plotList is present
        super(ZA_BTagEfficiencies, self).postProcess(taskList, config, workdir, resultsdir)

        from bamboo.plots import CutFlowReport, DerivedPlot, Plot
        import bambooToOls
        import json 

        # save generated-events for each samples--- > mainly needed for the DNN
        plotList_cutflowreport = [ ap for ap in self.plotList if isinstance(ap, CutFlowReport) ]
        bambooToOls.SaveCutFlowReports(config, plotList_cutflowreport, resultsdir, self.readCounters)

        plotList_2D = [ ap for ap in self.plotList if ( isinstance(ap, Plot) or isinstance(ap, DerivedPlot) ) and len(ap.binnings) == 2 ]
        logger.debug("Found {0:d} plots to save".format(len(plotList_2D)))

        from bamboo.analysisutils import loadPlotIt
        #p_config, samples, plots_2D, systematics, legend = loadPlotIt(config, plotList_2D, eras=self.args.eras, workdir=workdir, resultsdir=resultsdir, readCounters=self.readCounters, vetoFileAttributes=self.__class__.CustomSampleAttributes, plotDefaults=self.plotDefaults)
        p_config, samples, plots_2D, systematics, legend = loadPlotIt(config, plotList_2D, eras=None, workdir=workdir, resultsdir=resultsdir, readCounters=self.readCounters, vetoFileAttributes=self.__class__.CustomSampleAttributes, plotDefaults=self.plotDefaults)
        
        from plotit.plotit import Stack
        from bamboo.root import gbl
        
        import ROOT
        from ROOT import TFile, TH1, TH2, TCanvas
        ROOT.gROOT.SetBatch(True)
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #  change default ROOT style
        # https://root.cern.ch/doc/master/classTHistPainter.html#HP07
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # gbl.gStyle.SetHistLineColor(4)
        # gbl.gStyle.SetHistLineWidth(2)
        # gbl.gStyle.SetMarkerColor(4)
        # gbl.gStyle.SetMarkerStyle(8)
        gbl.gStyle.SetPalette(1)
        gbl.gStyle.SetOptStat(0) # stat box is OFF 
        for plot in plots_2D:
            if ('_2j_jet_pt_eta_') in plot.name  or plot.name.startswith('pair_lept_2j_jet_pt_vs_eta_'):
                expStack = Stack(smp.getHist(plot) for smp in samples if smp.cfg.type == "MC")
                cv = gbl.TCanvas(f"c{plot.name}")
                cv.cd(1)
                expStack.obj.Draw("COLZ0")
                expStack.obj.Draw("TEXT,SAME")
                cv.Update()
                cv.SaveAs(os.path.join(resultsdir, f"{plot.name}.png"))
            else:
                logger.debug(f"Saving plot {plot.name}")
                obsStack = Stack(smp.getHist(plot) for smp in samples if smp.cfg.type == "DATA")
                expStack = Stack(smp.getHist(plot) for smp in samples if smp.cfg.type == "MC")
                cv = gbl.TCanvas(f"c{plot.name}")
                cv.Divide(2)
                cv.cd(1)
                expStack.obj.Draw("COLZ")
                expStack.obj.Draw("TEXT,SAME")
                cv.cd(2)
                obsStack.obj.Draw("COLZ")
                expStack.obj.Draw("TEXT,SAME")
                cv.Update()
                cv.SaveAs(os.path.join(resultsdir, f"{plot.name}.png"))
        # This part is meant to produce 2D eff maps as function ( pt, eta) for mc samples so all the function have being modified accordingly ; if you want to call them from 
        # utils for other prurposes , you have to keep in mind that data will not processed ... 
        if not os.path.isdir(os.path.join(resultsdir, "summedProcessesForEffmaps")):
            os.makedirs(os.path.join(resultsdir,"summedProcessesForEffmaps"))
        utils.normalizeAndSumSamples(config['eras'], config['samples'], resultsdir, os.path.join(resultsdir, "summedProcesses"), self.readCounters) 
        
        def getRatio(f, n, d, suffix):
            num = f.Get(n)
            den = f.Get(d)
            ratio = num.Clone(num.GetName() + suffix)
            ratio.Divide(den)
            return ratio

        taggers_and_workingspoints = { "resolved": { "deepcsv": ["L","M","T"] , "deepflavour": ["L","M","T"] }, 
                                       "boosted" : { "deepcsv": ["L","M"]}
                                     } 
        
        for proc in list(config["samples"].keys()) + ["summedProcesses_" + suff for suff in ["run2"] + list(config["eras"].keys())]:
            in_tf = HT.openFileAndGet(os.path.join(resultsdir, proc + ".root"), "read")
            out_tf = HT.openFileAndGet(os.path.join(resultsdir, "summedProcessesForEffmaps", proc + "_ratios.root"), "recreate")
           
            # compute efficiencies (divide histo after cut by total histo)
            for process in ["gg_fusion","bb_associatedProduction"]:
                for reg, dict_ in taggers_and_workingspoints.items():
                    for tagger, workingpoints in dict_.items():
                        for wp in workingpoints:
                            for flav in ["b", "c", "light"]:
                                logger.info( f"smp: {proc} // ratio = pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_{tagger}_wp{wp}_{process} / pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_{process}")
                                #(btagged: b , c or light) /(total no b-tag requirement : b, c or light respetively )  --> mistag rate in mc 
                                getRatio(in_tf, f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_{tagger}_wp{wp}_{process}", f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_{process}", f"__mc_eff").Write()
            in_tf.Close()
            out_tf.Close()

        ff = gbl.TFile(os.path.join(resultsdir, "summedProcessesForEffmaps/summedProcesses_run2_ratios.root"))
        to_print2D = []
        for obj_key in ff.GetListOfKeys():
            obj = ff.Get(obj_key.GetName())
            if isinstance(obj,TH2):
                to_print2D.append(obj)
        if len(to_print2D) != 0:
            for i,obj in enumerate(to_print2D):
                cv = gbl.TCanvas()
                obj.Draw("COLZ0, TEXT")
                cv.Update()
                cv.SaveAs(os.path.join(resultsdir, f"summedProcessesForEffmaps/{obj.GetName()}.png"))

        cache = HT.FileCache()

        outDir = os.path.join(resultsdir, "..", "bTagEffs")
        os.makedirs(outDir, exist_ok=True)
        for era in config['eras']:
            for process in ["gg_fusion","bb_associatedProduction"]:
                for reg, dict_ in taggers_and_workingspoints.items():
                    for tagger, workingpoints in dict_.items():
                        for wp in workingpoints:
                            for flav in ["b", "c", "light"]:
                                name = f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_{tagger}_wp{wp}_{process}__mc_eff"
                                hist = HT.loadHisto((os.path.join(resultsdir, "summedProcessesForEffmaps", f"summedProcesses_{era}_ratios.root")), name, cache)
                                style = HT.setTDRStyle()
                                style.SetPadRightMargin(0.15)
                                style.SetLabelSize(0.03, "XYZ")
                                style.SetPaintTextFormat(".3f")
    
                                title = hist.GetTitle()
                                c = ROOT.TCanvas(HT.randomString(), title, 800, 600)
                                pad = ROOT.TPad(HT.randomString(), "", 0, 0, 1, 1)
                                pad.Draw()
                                pad.cd()
                                hist.Draw("colztexte")
                                hist.GetYaxis().SetTitleOffset(1.5)
                                hist.GetYaxis().SetTitle("Jet |#eta|")
                                hist.GetXaxis().SetTitle("Jet p_{T}")
                                pad.SetLogx()
                                c.Print(os.path.join(outDir, f"{era}_{name}.pdf"))
