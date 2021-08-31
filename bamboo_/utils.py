#!/usr/bin/env python
import os
import re

import logging
logger = logging.getLogger("H->ZA->llbb Plotter")

from bamboo.plots import Plot, SummedPlot
from bamboo import treefunctions as op
from bamboo import scalefactors
from bamboo.root import gbl as ROOT

import HistogramTools as HT

def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct

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


#### Common tasks (systematics, sample splittings...)

def addTheorySystematics(plotter, tree, noSel, qcdScale=True, PSISR=False, PSFSR=False, PDFs=False):
    plotter.qcdScaleVariations = dict() 
    import yaml
    
    # for 2017 hadronic is buggy sample 
    #with open('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/config/SamplesWithWrongPSWeight.yml') as file_:
    #    buggySamples = yaml.load(file_, Loader=yaml.FullLoader)
    #    buggySyst = buggySamples.get(sample, "")
    
    if qcdScale:
        qcdScaleVariations = { f"qcdScalevar{i}": tree.LHEScaleWeight[i] for i in [0, 1, 3, 5, 7, 8] }
        qcdScaleSyst = op.systematic(op.c_float(1.), name="qcdScale", **plotter.qcdScaleVariations)
        noSel = noSel.refine("qcdScale", weight=qcdScaleSyst)

    if PSISR :#and "PS" not in buggySyst:
        psISRSyst = op.systematic(op.c_float(1.), name="psISR", up=tree.PSWeight[2], down=tree.PSWeight[0])
        noSel = noSel.refine("psISR", weight=psISRSyst)
    
    if PSFSR :#and "PS" not in buggySyst:
        psFSRSyst = op.systematic(op.c_float(1.), name="psFSR", up=tree.PSWeight[3], down=tree.PSWeight[1])
        noSel = noSel.refine("psFSR", weight=psFSRSyst)
    
    if PDFs:
        pdfsWeight = op.systematic(op.c_float(1.), name="pdfsWgt", up=tree.LHEPdfWeight, down=tree.LHEPdfWeight)

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
    toMerge = {}
    for plot in plots:
        toMerge[plot.name] = []

    for proc, cfg in config["samples"].items():
        tf = HT.openFileAndGet(os.path.join(inDir, proc + ".root"))
        
        if cfg["group"] != "data":
            sumWgt = counterReader(tf)[cfg["generated-events"]]
            xs = cfg["cross-section"]

        for plot in plots:
            hist = tf.Get(plot.name)
            if cfg["group"] != "data":
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
