#!/usr/bin/env python
import os
import re
import yaml
import logging
logger = logging.getLogger("ZAutils")

import numpy as np

from bamboo.plots import Plot, SummedPlot
from bamboo import treefunctions as op
from bamboo import scalefactors
from bamboo.root import gbl as ROOT

import HistogramTools as HT

def getOpts(name, **kwargs):
    uname=name.lower()
    if "elmu" in uname:
        label = "e^{+}#mu^{-}"+"channel"
    elif "muel" in uname:
        label = "#mu^{+}e^{-}"+ "channel"
    elif "elel" in uname:
        label = "e^{+}e^{-}"+"channel"
    elif "mumu" in uname:
        label = "#mu^{+}#mu^{-}"+"channel"
    elif "comb" in uname:
        label = "e^{#pm}#mu^{#pm}"+" combined"
    elif "lept" in uname:
        label = "1 lepton pair (e/#mu)"
    if "2j" in uname:
        label += ", #geq 2 jets"
    if "2b" in uname:
        label += ", #geq 2 b tags"
    opts = {
        "labels": [{"text": label, "position": [0.205, 0.912]}]
    }
    opts.update(kwargs)
    return opts

def getCounter(i):
    if i <= 0:
        return str(i)
    if i == 1:
        return "Leading"
    if i == 2:
        return "Sub-Leading"
    if i == 3:
        return "3rd Highest"
    if i >= 4:
        return "{}th Highest".format(i)

def getRunEra(sample):
    """Return run era (A/B/...) for data sample"""
    result = re.search(r'Run201.([A-Z]?)', sample)
    if result is None:
        raise RuntimeError("Could not find run era from sample {}".format(sample))

    return result.group(1)

def makeMergedPlots(categDef, newCat, name, binning, var=None, **kwargs):
    """ Make a series of plots which will be merged.
    - cateDef can either be e.g.:
        - `[("mu", muSelection), ("el", elSelection), ...]`, in which case the same variable `var` is used for all sub-categories
        - `[("mu", muSelection, muVar), ("el", elSelection, elVar), ...]`, for cases where the variable is different for each sub-category
    - `newCat`: name of the merged category
    - `name`: name of the merged plot (-> full plot name is newCat_name)
    - `var`: variable to plot (if it is the same for all categories)
    - `binning`: binning to be used
    Any further named args will be forwarded to the plot constructor.
    The variables can also be iterables for multi-dimensional plots.
    """
    plotsToAdd = []
    
    for cat in categDef:
        if len(cat) == 2:
            (catName, catSel), catVar = cat, var
        elif len(cat) == 3:
            catName, catSet, catVar = cat
        else:
            raise Exception(f"{cat} should have 2 or 3 entries")
        thisName = f"{catName}_{name}"
        if not hasattr(catVar, "__len__"):
            plotType = Plot.make1D
        elif len(catVar) == 2:
            plotType = Plot.make2D
        elif len(catVar) == 3:
            plotType = Plot.make3D
        plotsToAdd.append(plotType(thisName, catVar, catSel, binning, **kwargs))

    return plotsToAdd + [SummedPlot(f"{newCat}_{name}", plotsToAdd, **kwargs)]

def declareHessianPDFCalculator():
    from bamboo.root import gbl
    if not hasattr(gbl, "computeHessianPDFUncertainty"):
        gbl.gInterpreter.Declare("""
                                 float computeHessianPDFUncertainty(const ROOT::VecOps::RVec<float>& weights) {
                                 if (weights.size() < 2)
                                    return 0.;
                                 float result = 0.;
                                 for (std::size_t i = 1; i < weights.size(); i++)
                                    result += pow(weights[i] - weights[0], 2);
                                 return sqrt(result);
                            }""")

def addTheorySystematics(plotter, sample, sampleCfg, tree, noSel, qcdScale=True, PSISR=False, PSFSR=False, PDFs=False, pdf_mode="simple"):
    plotter.qcdScaleVariations = dict()
    if qcdScale:
        if plotter.qcdScaleVarMode == "separate":
            noSel = noSel.refine("qcdMuF", weight=op.systematic(op.c_float(1.), name="qcdMuF", up=tree.LHEScaleWeight[3], down=tree.LHEScaleWeight[5]))
            noSel = noSel.refine("qcdMuR", weight=op.systematic(op.c_float(1.), name="qcdMuR", up=tree.LHEScaleWeight[1], down=tree.LHEScaleWeight[7]))
        elif plotter.qcdScaleVarMode == "combined":
            qcdScaleVariations = { f"qcdScalevar{i}": tree.LHEScaleWeight[i] for i in [0, 1, 3, 5, 7, 8] }
            qcdScaleSyst = op.systematic(op.c_float(1.), name="qcdScale", **plotter.qcdScaleVariations)
            noSel = noSel.refine("qcdScale", weight=qcdScaleSyst)
    
    if PSISR:
        psISRSyst = op.systematic(op.c_float(1.), name="psISR", up=tree.PSWeight[2], down=tree.PSWeight[0])
        noSel = noSel.refine("psISR", weight=psISRSyst)
    
    if PSFSR:
        psFSRSyst = op.systematic(op.c_float(1.), name="psFSR", up=tree.PSWeight[3], down=tree.PSWeight[1])
        noSel = noSel.refine("psFSR", weight=psFSRSyst)
    
    if PDFs:
        pdf_mc = sampleCfg.get("pdf_mc", False)
        nPdfVars = (0, 101) if pdf_mc else (1, 103)
        if pdf_mode == "full" and sampleCfg.get("pdf_full", False):
            logger.info("Adding full PDF systematics")
            pdfVars = { f"pdf{i}": tree.LHEPdfWeight[i] for i in range(*nPdfVars) }
        elif pdf_mode == "simple":
            logger.info("Adding simplified PDF systematics")
            if pdf_mc:
                pdfSigma = op.rng_stddev(tree.LHEPdfWeight)
            else:
                declareHessianPDFCalculator()
                sigmaCalc = op.extMethod("computeHessianPDFUncertainty", returnType="float")
                pdfSigma = sigmaCalc(tree.LHEPdfWeight)
            pdfVars = { "pdfup": tree.LHEPdfWeight[0] + pdfSigma, "pdfdown": tree.LHEPdfWeight[0] - pdfSigma }
        if pdf_mc:
            logger.info("This sample has MC PDF variations")
        else:
            logger.info("This sample has Hessian PDF variations")
        noSel = noSel.refine("PDF", weight=op.systematic(op.c_float(1.), **pdfVars))

    return noSel

def splitTTjetFlavours(cfg, tree, noSel):
    subProc = cfg["subprocess"]
    if subProc == "ttbb":
        noSel = noSel.refine(subProc, cut=(tree.genTtbarId % 100) >= 52)
    elif subProc == "ttbj":
        noSel = noSel.refine(subProc, cut=(tree.genTtbarId % 100) == 51)
    elif subProc == "ttcc":
        noSel = noSel.refine(subProc, cut=op.in_range(40, tree.genTtbarId % 100, 46))
    elif subProc == "ttjj":
        noSel = noSel.refine(subProc, cut=(tree.genTtbarId % 100) < 41)

    return noSel

# FIXME also merge systematic variations
def normalizeAndMergeSamplesForCombined(plots, counterReader, config, inDir, outPath):
    """
    Produce file containing the sum of all the histograms over the processes, 
    after normalizing the processes by their cross section, sum of weights and luminosity.
    Note: The systematics are handled but are expected to be SAME for all processes and eras.
    """
    toMerge = {}
    for plot in plots:
        toMerge[plot.name] = []

    for proc, cfg in config["samples"].items():
        if proc.startswith('HToZATo2L2B_'):
            continue
        tf = HT.openFileAndGet(os.path.join(inDir, proc + ".root"))
        
        if "group" not in cfg.keys():
            sumWgt = counterReader(tf)[cfg["generated-events"]]
            xs = cfg["cross-section"]

        for plot in plots:
            hist = tf.Get(plot.name)
            if "group" not in cfg.keys():
                hist.Scale(xs / sumWgt)
                hist.SetDirectory(0)
            toMerge[plot.name].append(hist)

        tf.Close()
    eras = list(config["eras"].keys())
    for era in eras:
        mergedFile = HT.openFileAndGet(f"{outPath}_{era}.root", "recreate")
        for name, mergeList in toMerge.items():
            merged = HT.addHists(mergeList, name)
            merged.Write()
        mergedFile.Close()

    os.system("hadd -f " + outPath + "_run2.root " + " ".join([ f"{outPath}_{era}.root" for era in eras ]))

def produceMEScaleEnvelopes(plots, scaleVariations, path):
    _tf = HT.openFileAndGet(path, "update")
    listOfKeys = [ k.GetName() for k in _tf.GetListOfKeys() ]

    for plot in plots:
        # Compute envelope histograms for QCD scale variations
        nominal = _tf.Get(plot.name)
        variations = []
        for var in scaleVariations:
            varName = "{}__{}".format(plot.name, var)
            if varName in listOfKeys:
                variations.append(_tf.Get(varName))
        if len(variations) != len(scaleVariations):
            logger.warning("Did not find {} variations for plot {} in file {}".format(len(scaleVariations), plot.name, path))
            continue
        up, down = HT.getEnvelopeHistograms(nominal, variations)
        up.Write(f"{plot.name}__qcdScaleup", ROOT.TObject.kOverwrite)
        down.Write(f"{plot.name}__qcdScaledown", ROOT.TObject.kOverwrite)

    _tf.Close()

def producePDFEnvelopes(plots, task, resultsdir):
    sample = task.name
    smpCfg = task.config
    path   = os.path.join(resultsdir, task.outputFile)

    logger.info(f"Producing PDF uncertainty envelopes for sample {sample}")

    def sigmaFromReplicasMC(replicas):
        return np.std(replicas, axis=0, ddof=1)

    def sigmaFromReplicasHessian(residuals):
        sq = residuals**2
        return np.sqrt(sq.sum(axis=0))

    def buildTHFromNP(nom_th, values, name):
        new_th = nom_th.Clone(name)
        assert(nom_th.GetNcells() == len(values))
        for i in range(len(values)):
            new_th.SetBinContent(i, values[i])
        return new_th

    tf = HT.openFileAndGet(path, "update")
    listOfKeys = [ k.GetName() for k in tf.GetListOfKeys() ]
    nVar = 0

    for plot in plots:
        if isinstance(plot, CutFlowReport):
            continue
        # Compute envelope histograms for PDF variations
        nominal = tf.Get(plot.name)
        def isPDFVar(name):
            return name.startswith(f"{plot.name}__pdf") and not (
                name.endswith("up") or name.endswith("down"))
        variations = [ tf.Get(varName) for varName in listOfKeys if isPDFVar(varName) ]

        if not variations:
            logger.warning(f"Did not find PDF variations for plot {plot.name} in file {path}")
            continue
        nVar = len(variations)

        replica_values = np.vstack([ np.array(h) for h in variations ])
        nom_values = np.array(nominal)
        if smpCfg.get("pdf_mc", False):
            # PDF MC set
            sigma = sigmaFromReplicasMC(replica_values)
        else:
            # Hessian MC set
            sigma = sigmaFromReplicasHessian(replica_values - nom_values)
        up = buildTHFromNP(nominal, nom_values + sigma, f"{plot.name}__pdfup")
        down = buildTHFromNP(nominal, np.clip(nom_values - sigma, 0., None), f"{plot.name}__pdfdown")
        up.Write("", ROOT.TObject.kOverwrite)
        down.Write("", ROOT.TObject.kOverwrite)

    logger.info(f"Found {nVar} PDF variations for sample {sample}")

    tf.Close()
