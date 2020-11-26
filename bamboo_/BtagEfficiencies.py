import os, os.path
import sys

zabPath = os.path.dirname(__file__)
if zabPath not in sys.path:
    sys.path.append(zabPath)
import logging
logger = logging.getLogger("H->ZA->BTagEfficiencies_MAPS")

import utils
import ControlPLots as cp
import HistogramTools as HT
from ZAtollbb import NanoHtoZABase

from bamboo.analysismodules import NanoAODHistoModule, HistogramsModule
from bamboo import treefunctions as op
from bamboo.plots import Plot, SummedPlot
from bamboo.plots import EquidistantBinning as EqBin
from bamboo.plots import VariableBinning as VarBin

class  MC_BTagEfficiencies(NanoHtoZABase, HistogramsModule):
    def __init__(self, args):
        super(MC_BTagEfficiencies, self).__init__(args)
    def definePlots(self, t, noSel, sample=None, sampleCfg=None):
        #from bamboo.plots import Plot
        from bambooToOls import Plot
        from bamboo.plots import CutFlowReport

        noSel, PUWeight, categories, isDY_reweight, WorkingPoints, btagging, deepBFlavScaleFactor, deepB_AK4ScaleFactor, deepB_AK8ScaleFactor, AK4jets, AK8jets, fatjets_nosubjettinessCut, bjets_resolved, bjets_boosted, CleanJets_fromPileup, electrons, muons, MET, corrMET, PuppiMET, elRecoSF_highpt, elRecoSF_lowpt = super(MC_BTagEfficiencies, self).defineObjects(t, noSel, sample, sampleCfg)
        year = sampleCfg.get("era") if sampleCfg else None
        isMC = self.isMC(sample)
        binScaling = 1
        plots = []
        ZoOm_Onpteta = True

        lljj_selections_percat_resolved = { channel.lower() : catSel.refine("twolep_%s_twojets_resolved_selection"%channel.lower(), cut=[ op.rng_len(AK4jets) > 1 ] ) 
                                                    for channel, (dilepton, catSel) in categories.items() }
        lljj_selections_percat_boosted = { channel.lower() : catSel.refine("twolep_%s_onejet_boosted_selection"%channel.lower(), cut=[ op.rng_len(AK8jets) > 0 ] ) 
                                                    for channel, (dilepton, catSel) in categories.items() }
         
        lljj_selections_perreg= {"resolved": lljj_selections_percat_resolved,
                                 "boosted": lljj_selections_percat_boosted }
        
        discrCut_PerYearLIB= {
                "resolved": {
                            "DeepCSV": {
                                "2016": (0.2217, 0.6321, 0.8953), "2017":(0.1522, 0.4941, 0.8001), "2018":(0.1241, 0.4184, 0.7527) },
                            "DeepFlavour": {
                                "2016": (0.0614, 0.3093, 0.7221), "2017":(0.0521, 0.3033, 0.7489), "2018":(0.0494, 0.2770, 0.7264) }    
                    },
                "boosted":{ "DeepCSV": {
                                "2016": (0.2217, 0.6321), "2017":(0.1522, 0.4941), "2018":(0.1241, 0.4184) },
                    }
                }
        for reg, lljj_selections_percat in lljj_selections_perreg.items():
    
            jets = (AK4jets if reg=="resolved" else (fatjets_nosubjettinessCut ) )
            jlen= (2 if reg=="resolved" else (1))

            if isMC:
                bFlavJets = op.select(jets, lambda j: j.hadronFlavour == 5)
                cFlavJets = op.select(jets, lambda j: j.hadronFlavour == 4)
                lFlavJets = op.select(jets, lambda j: j.hadronFlavour == 0)

            if reg == "resolved":
                jetPairs = op.combine(jets, N=2)
                bJetPairs = op.combine(bFlavJets, N=2)
                cJetPairs = op.combine(cFlavJets, N=2)
                lightJetPairs = op.combine(lFlavJets, N=2)
                
                minJetDR = op.rng_min(jetPairs, lambda pair: op.deltaR(pair[0].p4, pair[1].p4))
                minBJetDR = op.rng_min(bJetPairs, lambda pair: op.deltaR(pair[0].p4, pair[1].p4))
                minBJetDR = op.rng_min(cJetPairs, lambda pair: op.deltaR(pair[0].p4, pair[1].p4))
                minLightJetDR = op.rng_min(lightJetPairs, lambda pair: op.deltaR(pair[0].p4, pair[1].p4))

                for uname, sel in lljj_selections_percat.items(): 
                    plots.append(Plot.make1D(uname + f"_2jets_minJetDR_{reg}", minJetDR, sel, EqBin(40, 0.4, 2.), plotopts=utils.getOpts(uname)))
                    plots.append(Plot.make1D(uname + f"_2bjets_minBJetDR_{reg}", minBJetDR, sel, EqBin(40, 0.4, 2.), plotopts=utils.getOpts(uname)))
                    plots.append(Plot.make1D(uname + f"_2cjets_minBJetDR_{reg}", minBJetDR, sel, EqBin(40, 0.4, 2.), plotopts=utils.getOpts(uname)))
                    plots.append(Plot.make1D(uname + f"_2lightjets_minLightJetDR_{reg}", minLightJetDR, sel, EqBin(40, 0.4, 2.), plotopts=utils.getOpts(uname)))
    
    
            for flav, flavJets in zip(['b', 'c', 'light'], [bFlavJets, cFlavJets, lFlavJets]):
                # b tagging efficiencies as a function of flavour/pt/|eta|
                if reg=='resolved':
                    if year=='2016':
                        binning = ( VarBin([20., 30., 50., 70., 100., 140., 200., 300.,  600., 1000.]) , EqBin(5, -2.5, 2.5) )
                        firstpt = 20.
                        lastpt = 200.
                    else:
                        binning = ( VarBin([30., 50., 70., 100., 140., 200., 300.,  600., 1000.]) , EqBin(5, -2.5, 2.5) )
                        firstpt= 30.
                        lastpt= 200.
                else: 
                    binning = ( VarBin([200., 300.,  450., 600., 1000.]) , EqBin(5, -2.5, 2.5) )
                    firstpt= 200.
                    lastpt= 800.

                pt = op.map(flavJets, lambda j: j.pt)
                eta = op.map(flavJets, lambda j: j.eta)
                zoOmbins = (EqBin(20//binScaling, firstpt, lastpt) , EqBin(5, -2.5, 2.5)) 
                
                plots.append(Plot.make2D(f"2mu_2j_jet_pt_eta_{flav}flav_{reg}", (pt, eta), lljj_selections_percat['mumu'], binning, title=f"{flav}jets pt vs eta ", plotopts=utils.getOpts('mumu')))
                plots.append(Plot.make2D(f"2el_2j_jet_pt_eta_{flav}flav_{reg}", (pt, eta), lljj_selections_percat['elel'], binning, title=f"{flav}jets pt vs eta", plotopts=utils.getOpts('elel')))
                #plots.append(Plot.make2D(f"1el1mu_2j_jet_pt_eta_{flav}_{reg}", (pt, eta), lljj_selections_percat['elmu'], binning, title=f"{flav}jets pt vs eta", plotopts=utils.getOpts('elmu')))
                plots.append(Plot.make2D(f"1mu1el_2j_jet_pt_eta_{flav}flav_{reg}", (pt, eta), lljj_selections_percat['muel'], binning, title=f"{flav}jets pt vs eta", plotopts=utils.getOpts('muel')))
                plots.append(SummedPlot(f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}", plots[-3:-2:1]))
       
                if ZoOm_Onpteta:
                    plots.append(Plot.make2D(f"2mu_2j_jet_pt_eta_{flav}flav_{reg}_ZoOm_Onpteta", (pt, eta), lljj_selections_percat['mumu'], zoOmbins, title=f"{flav}jets pt vs eta ", plotopts=utils.getOpts('mumu')))
                    plots.append(Plot.make2D(f"2el_2j_jet_pt_eta_{flav}flav_{reg}_ZoOm_Onpteta", (pt, eta), lljj_selections_percat['elel'], zoOmbins, title=f"{flav}jets pt vs eta", plotopts=utils.getOpts('elel')))
                    #plots.append(Plot.make2D(f"1el1mu_2j_jet_pt_eta_{flav}_{reg}_ZoOm_Onpteta", (pt, eta), lljj_selections_percat['elmu'], zoOmbins, title=f"{flav}jets pt vs eta", plotopts=utils.getOpts('elmu')))
                    plots.append(Plot.make2D(f"1mu1el_2j_jet_pt_eta_{flav}flav_{reg}_ZoOm_Onpteta", (pt, eta), lljj_selections_percat['muel'], zoOmbins, title=f"{flav}jets pt vs eta", plotopts=utils.getOpts('muel')))
                    plots.append(SummedPlot(f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_ZoOm_Onpteta", plots[-3:-2:1]))
        
                plots.append(Plot.make1D(f"2mu_n{flav}jets_hadronFlav_{reg}", op.rng_len(flavJets), lljj_selections_percat['mumu'], EqBin(6, 0, 6), title=f"{flav}jets multiplicity", plotopts=utils.getOpts('mumu')))
                plots.append(Plot.make1D(f"2el_n{flav}jets_hadronFlav_{reg}", op.rng_len(flavJets), lljj_selections_percat['elel'], EqBin(6, 0, 6), title=f"{flav}jets multiplicity", plotopts=utils.getOpts('elel')))
                #plots.append(Plot.make1D(f"1el1mu_n{flav}jets_hadronFlav_{reg}", op.rng_len(flavJets), lljj_selections_percat['elmu'], EqBin(6, 0, 6), title=f"{flav}jets multiplicity", plotopts=utils.getOpts('elmu')))
                plots.append(Plot.make1D(f"1mu1el_n{flav}jets_hadronFlav_{reg}", op.rng_len(flavJets), lljj_selections_percat['muel'], EqBin(6, 0, 6), title=f"{flav}jets multiplicity", plotopts=utils.getOpts('muel')))
                plots.append(SummedPlot(f"pair_lept_2j_jet_multiplicity_{flav}flav_{reg}", plots[-3:-2:1]))
        
                OperatingPoints= ['L', 'M']
                if reg == "resolved":
                    OperatingPoints.append( "T" )
                for tagger in discrCut_PerYearLIB[reg].keys(): 
                    for (wp, deepThr) in zip( OperatingPoints, discrCut_PerYearLIB[reg][tagger][year]):
                        selJets = ( op.select(flavJets, lambda j: j.btagDeepFlavB >= deepThr) if tagger=='DeepFlavour' else (op.select(flavJets, lambda j: j.btagDeepB >= deepThr )))
        
                        pt = op.map(selJets, lambda j: j.pt)
                        eta = op.map(selJets, lambda j: j.eta)
                    
                        tagger = tagger.lower()
                        plots.append(Plot.make2D(f"2mu_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}", (pt, eta), lljj_selections_percat['mumu'], binning))
                        plots.append(Plot.make2D(f"2el_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}", (pt, eta), lljj_selections_percat['elel'], binning))
                        #plots.append(Plot.make2D(f"1el1mu_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}", (pt, eta), lljj_selections_percat['elmu'], binning))
                        plots.append(Plot.make2D(f"1mu1el_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}", (pt, eta), lljj_selections_percat['muel'], binning))
                        plots.append(SummedPlot(f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_{tagger}_wp{wp}", plots[-3:-2:1]))
                        
                        if ZoOm_Onpteta:
                            plots.append(Plot.make2D(f"2mu_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}_ZoOm_Onpteta", (pt, eta), lljj_selections_percat['mumu'], zoOmbins))
                            plots.append(Plot.make2D(f"2el_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}_ZoOm_Onpteta", (pt, eta), lljj_selections_percat['elel'], zoOmbins))
                            #plots.append(Plot.make2D(f"1el1mu_2j_jet_pt_eta_{flav}_{reg}_{tagger}_wp{wp}_ZoOm_Onpteta", (pt, eta), lljj_selections_percat['elmu'], zoOmbins))
                            plots.append(Plot.make2D(f"1mu1el_2j_jet_pt_eta_{flav}flav_{reg}_{tagger}_wp{wp}_ZoOm_Onpteta", (pt, eta), lljj_selections_percat['muel'], zoOmbins))
                            plots.append(SummedPlot(f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_{tagger}_wp{wp}_ZoOm_Onpteta", plots[-3:-2:1]))
    
            # look at specific slice in pt/|eta|
            jetSel = lambda j: op.AND(op.in_range(80., j.pt, 200.), op.in_range(-1., j.eta, 1.))
            selBJets = op.select(bFlavJets, jetSel)
            selCJets = op.select(cFlavJets, jetSel)
            selLightJets = op.select(lFlavJets, jetSel)

            lambdadic = { 
                    "resolved":
                            {'btagDeepFlavB': lambda j: j.btagDeepFlavB,
                             'btagDeepB' :lambda j: j.btagDeepB }, 
                    "boosted":
                            {'btagDeepB' :lambda j: j.btagDeepB}
                    }

            for channel, (dilepton, catSel) in categories.items():
                channel = channel.lower()
                for lambda_ , discr_cut in lambdadic[reg].items():
                    for i in range(0, jlen):
                        nJetSel = catSel.refine(f"{channel}_{i}jets_{reg}_sel_{lambda_}", cut=op.rng_len(jets)==i)
                        plots.append(Plot.make1D(f"{channel}_{i}bjets_{reg}sel_{lambda_}", op.map(selBJets, discr_cut), nJetSel, EqBin(30, 0., 1.), 
                                                title=f"{utils.getCounter(i+1)} N true bjets {lambda_}", plotopts=utils.getOpts(channel) ))
                        plots.append(Plot.make1D(f"{channel}_{i}cjets_{reg}sel_{lambda_}", op.map(selCJets, discr_cut), nJetSel, EqBin(30, 0., 1.),
                                                title=f"{utils.getCounter(i+1)} N true cjets {lambda_}", plotopts=utils.getOpts(channel) )) 
                        plots.append(Plot.make1D(f"{channel}_{i}lightjets_{reg}sel_{lambda_}", op.map(selLightJets, discr_cut), nJetSel, EqBin(30, 0., 1.),
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
                        plots.append(Plot.make1D(f"2mu_2j_{vari}DR_{flav}jets_{reg}_{lambda_}", op.map(deltaR_val, discr_cut ), lljj_selections_percat['mumu'], 
                                                    EqBin(30, 0., 1.), title=f' {vari} #delta R({flav}, j)' , plotopts=utils.getOpts('mumu')))
                        plots.append(Plot.make1D(f"2el_2j_{vari}DR_{flav}jets_{reg}_{lambda_}", op.map(deltaR_val, discr_cut ), lljj_selections_percat['elel'], 
                                                    EqBin(30, 0., 1.), title=f' {vari} #delta R({flav}, j)' , plotopts=utils.getOpts('elel')))
                        #plots.append(Plot.make1D(f"1el1mu_2j_{vari}DR_{flav}jets_{lambda_}", op.map(deltaR_val, discr_cut ), lljj_selections_percat['elmu'], 
                                                    #EqBin(30, 0., 1.),title=f' {vari} #delta R({flav}, j)' , plotopts=utils.getOpts('elmu')))
                        plots.append(Plot.make1D(f"1mu1el_2j_{vari}DR_{flav}jets_{reg}_{lambda_}", op.map(deltaR_val, discr_cut ), lljj_selections_percat['muel'], 
                                                    EqBin(30, 0., 1.), title=f' {vari} #delta R({flav}, j)'  , plotopts=utils.getOpts('muel')))

        return plots
    def postProcess(self, taskList, config=None, workdir=None, resultsdir=None):
        # run plotIt as defined in HistogramsModule - this will also ensure that self.plotList is present
        super(MC_BTagEfficiencies, self).postProcess(taskList, config, workdir, resultsdir)

        from bamboo.plots import CutFlowReport, DerivedPlot
        import bambooToOls
        import json 

        # save generated-events for each samples--- > mainly needed for the DNN
        plotList_cutflowreport = [ ap for ap in self.plotList if isinstance(ap, CutFlowReport) ]
        bambooToOls.SaveCutFlowReports(config, plotList_cutflowreport, resultsdir, self.readCounters)

        plotList_2D = [ ap for ap in self.plotList if ( isinstance(ap, Plot) or isinstance(ap, DerivedPlot) ) and len(ap.binnings) == 2 ]
        logger.debug("Found {0:d} plots to save".format(len(plotList_2D)))

        from bamboo.analysisutils import loadPlotIt
        p_config, samples, plots_2D, systematics, legend = loadPlotIt(config, plotList_2D, eras=self.args.eras, workdir=workdir, resultsdir=resultsdir, readCounters=self.readCounters, vetoFileAttributes=self.__class__.CustomSampleAttributes, plotDefaults=self.plotDefaults)
        from plotit.plotit import Stack
        from bamboo.root import gbl
        for plot in plots_2D:
            if ('_2j_jet_pt_eta_') in plot.name  or plot.name.startswith('pair_lept_2j_jet_pt_vs_eta_'):
                expStack = Stack(smp.getHist(plot) for smp in samples if smp.cfg.type == "MC")
                cv = gbl.TCanvas(f"c{plot.name}")
                cv.cd(1)
                expStack.obj.Draw("COLZ0")
                cv.Update()
                cv.SaveAs(os.path.join(resultsdir, f"{plot.name}.png"))
            else:
                logger.debug(f"Saving plot {plot.name}")
                obsStack = Stack(smp.getHist(plot) for smp in samples if smp.cfg.type == "DATA")
                expStack = Stack(smp.getHist(plot) for smp in samples if smp.cfg.type == "MC")
                cv = gbl.TCanvas(f"c{plot.name}")
                cv.Divide(2)
                cv.cd(1)
                expStack.obj.Draw("COLZ0")
                cv.cd(2)
                obsStack.obj.Draw("COLZ0")
                cv.Update()
                cv.SaveAs(os.path.join(resultsdir, f"{plot.name}.png"))
        # This part is meant to to produce 2D eff maps ad funct ( pt, eta) in mc so all the function have being modified accordingly ; if you want to call them from 
        # utils for other prurposes , you have to keep in mind that data will not processed ... 
        if not os.path.isdir(os.path.join(resultsdir, "summedProcessesForEffmaps")):
            os.makedirs(os.path.join(resultsdir,"summedProcessesForEffmaps"))
        utils.normalizeAndSumSamples(self.readCounters, config["eras"], config["samples"], resultsdir, os.path.join(resultsdir, "summedProcesses"))

        def getRatio(f, n, d, suffix):
            num = f.Get(n)
            den = f.Get(d)
            ratio = num.Clone(num.GetName() + suffix)
            ratio.Divide(den)
            return ratio

        for proc in list(config["samples"].keys()) + ["summedProcesses_" + suff for suff in ["run2"] + list(config["eras"].keys())]:
            if proc.startswith('DoubleMuon_') or proc.startswith('DoubleEGamma_') or proc.startswith('MuonEG_') or proc.startswith('SingleMuon_') or proc.startswith('SingleElectron_'):continue 
            in_tf = HT.openFileAndGet(os.path.join(resultsdir, proc + ".root"), "read")
            out_tf = HT.openFileAndGet(os.path.join(resultsdir, "summedProcessesForEffmaps", proc + "_ratios.root"), "recreate")
            
            # compute efficiencies (divide histo after cut by total histo)
            taggers = ["deepcsv"]
            for reg in ["resolved", "boosted"]:
                if reg == "boosted":
                    taggers.append( "deepflavour")
                for tagger in taggers:
                    for flav in ["b", "c", "light"]:
                        for wp in ["L", "M", "T"]:
                            print( 'smp:', proc , f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_{tagger}_wp{wp}" , f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}" )
                            #(btagged: b , c or light) /(total no b-tag requirement : b, c or light respetively )  --> mistag rate in mc 
                            getRatio(in_tf, f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}_{tagger}_wp{wp}", f"pair_lept_2j_jet_pt_vs_eta_{flav}flav_{reg}", f"__mc_eff").Write()
            in_tf.Close()
            out_tf.Close()
