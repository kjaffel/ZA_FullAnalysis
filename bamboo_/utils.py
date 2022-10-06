#!/usr/bin/env python
import os
import re
import yaml
import shutil
import collections
import subprocess
import numpy as np
import HistogramTools as HT

from bamboo.plots import Plot, SummedPlot
from bamboo.root import gbl
from bamboo.root import gbl as ROOT
from bamboo import treefunctions as op
from bamboo import scalefactors

def ZAlogger(name):
    import logging
    #numba_logger = logging.getLogger('numba')
    #numba_logger.setLevel(logging.WARNING)
    LOG_LEVEL = logging.DEBUG
    stream = logging.StreamHandler()
    stream.setLevel(LOG_LEVEL)
    logger = logging.getLogger(f'{name}')
    try:
        import colorlog
        from colorlog import ColoredFormatter
        formatter = ColoredFormatter(
                        "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
                        datefmt=None,
                        reset=True,
                        log_colors={
                                'DEBUG':    'green',
                                'INFO':     'cyan',
                                'WARNING':  'blue',
                                'ERROR':    'red',
                                'CRITICAL': 'red',
                            },
                        secondary_log_colors={},
                        style='%' )
        stream.setFormatter(formatter)
    except ImportError:
        print(" You can add colours to the output of Python logging module via : https://pypi.org/project/colorlog/")
        pass
    if not logger.hasHandlers():
        logger.setLevel(LOG_LEVEL)
        logger.addHandler(stream)
    return logger


logger   = ZAlogger(__name__)

def getYearFromEra(era):
    if   '2016' in era: return '16'
    elif '2017' in era: return '17'
    elif '2018' in era: return '18'


def get_tagger_wp(key, btv):
    if not 'DeepDoubleBvLV2' in key: s= -1 
    elif not btv: s=-6
    else: s= -2
    tagger  = key[:s]
    wp      = key.split(tagger)[-1]
    return tagger, wp


def run_Plotit(workdir, inDir, outDir, counterReader, config):
    
    to_hadd  = collections.defaultdict(list)
    hadd_cfg = collections.defaultdict(dict)
    keep_cfg = collections.defaultdict(dict)

    _gp =  list(config["plotIt"]["groups"].keys())
    if 'signal' in _gp:
        _gp.remove('signal')

    lumiCFG = {}
    for smp, smpCfg in config["samples"].items():
        
        era   = smpCfg["era"]
        lumi  = config["eras"][smpCfg["era"]]["luminosity"]
        lumiCFG[era] = lumi
        
        smpNm = smp.split('_UL'+getYearFromEra(era))[0]
        mergedHists = {}
        
        if smpCfg.get("group") in _gp:
            #copy results file to outDir
            shutil.copyfile( os.path.join(inDir, f"{smp}.root"), os.path.join(outDir,f"{smp}.root"))
            keep_cfg[smp] = smpCfg
        else:
            resultsFile    = HT.openFileAndGet(os.path.join(inDir, f"{smp}.root"), mode="READ")
            
            print( smp)
            xsc  = smpCfg["cross-section"]
            gevt = counterReader(resultsFile)[smpCfg["generated-events"]]
            br   = smpCfg["branching-ratio"]
            
            print( smp , lumi, xsc, gevt , br)
            smpScale = (lumi * xsc* br) / gevt
            
            for hk in resultsFile.GetListOfKeys():
                hist  = hk.ReadObj()
                if not hist.InheritsFrom("TH1"): 
                    continue
                hist.Scale(smpScale)
                name = hist.GetName()
                if name not in mergedHists.keys():
                    mergedHists[name] = hist.Clone()
                    mergedHists[name].SetDirectory(0)
                else:
                    mergedHists[name].Add(hist)
            
            resultsFile.Close()
        
            normalizedFile = HT.openFileAndGet(os.path.join(outDir, f"{smp}.root"), "recreate")
            for hist in mergedHists.values():
                hist.Write()
            normalizedFile.Close()
        
            to_hadd[smpNm].append(os.path.join(outDir, f"{smp}.root"))
            hadd_cfg[smpNm].update(smpCfg)
            
    for smp, val in to_hadd.items():
        sum_f   = f"{smp}_ULfull.root"
        haddCmd = ["hadd", "-f", os.path.join(outDir, sum_f)]+val
        try:
            logger.info("running {}".format(" ".join(haddCmd)))
            subprocess.check_call(haddCmd)#, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            logger.error("Failed to run {0}".format(" ".join(haddCmd)))
    
    with open(os.path.join(workdir, 'plots.yml'), 'r') as inf:
        with open(os.path.join(workdir, 'plots_full.yml'), 'w+') as outf:
            outf.write('configuration:\n')
            outf.write("  blinded-range-fill-color: '#FDFBFB'\n")
            outf.write('  blinded-range-fill-style: 4050\n')
            outf.write('  eras:\n')
            for era in lumiCFG.keys():
                outf.write(f'  - {era}\n')
            outf.write('  experiment: CMS\n')
            outf.write('  extra-label: Preliminary\n')
            outf.write('  height: 800\n')
            outf.write('  luminosity:\n')
            for era, lumi in lumiCFG.items():
                outf.write(f'    {era}: {lumi}\n')
            outf.write("  luminosity-label: '%1$.2f fb^{-1} (13 TeV)'\n")
            outf.write(f'  root: {workdir}/results/normalizedSummedSignal\n')
            outf.write('  show-overflow: true\n')
            outf.write('  width: 800\n')
            outf.write("  y-axis-format: '%1% / %2$.2f'\n")
            outf.write('files:\n')
            line_found = False
            
            for smp, cfg in hadd_cfg.items():
                outf.write(f'  {smp}_ULfull.root:\n')
                for k, v in cfg.items():
                    if k in ['type', 'group', 'line-width', 'line-type', 'legend', 'line-color']:
                        outf.write(f"    {k}: {v}\n")
            
            for smp, cfg in keep_cfg.items():
                outf.write(f'  {smp}.root:\n')
                for k, v in cfg.items():
                    outf.write(f"    {k}: {v}\n")
            
            for line in inf:
                if 'groups:' in line:
                    line_found = True
                if line_found:
                    outf.write(line)
                
    if not os.path.isdir(os.path.join(workdir, "plots_full")):
        os.makedirs(os.path.join(workdir,"plots_full"))

    plotitCmd = ["/home/ucl/cp3/kjaffel/bamboodev/plotIt/plotIt", "-o", f'{workdir}/plots_full', "--", f"{workdir}/plots_full.yml"]
    try:
        logger.info("running {}".format(" ".join(plotitCmd)))
        subprocess.check_call(plotitCmd)#, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        logger.error("Failed to run {0}".format(" ".join(plotitCmd)))


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
    elif "ossf" in uname:
        label = "e^{+}e^{-} + #mu^{+}#mu^{-}"+"channel"
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


def getSignalMassPoints(outdir, all_=True):
    with open(os.path.join(outdir, 'signals_fullanalysisRunIISummer20UL_18_17_16_nanov9.yml')) as _f:
        plotConfig = yaml.load(_f, Loader=yaml.FullLoader)
    
    points = {'gg_fusion': 
                { 'resolved': { 'HToZA': [], 'AToZH': [] },
                  'boosted' : { 'HToZA': [], 'AToZH': [] } },
              'bb_associatedProduction':
                { 'resolved': {'HToZA': [], 'AToZH': [] },
                  'boosted' : {'HToZA': [], 'AToZH': [] } },
            }

    all_points = { 'HToZA': [], 
                   'AToZH': [] }
    
    for f in plotConfig['samples']:
        key = 'HToZA'
        region = 'resolved'
        if not (f.startswith('GluGluTo') or f.startswith('HToZATo2L2B') or f.startswith('AToZHTo2L2B')):
            continue
        split_f = f.split('_')
        
        if split_f[1] == 'MA': key = 'AToZH'
        
        m0 = float(split_f[2].replace('p', '.'))
        m1 = float(split_f[4].replace('p', '.'))
        
        if all_:
            if not (m0, m1) in all_points[key]:
                all_points[key].append((m0, m1))
        else:
            if m0 > 4*m1:
                region = 'boosted'
    
            if 'GluGluTo' in f: 
                if not (m0, m1) in points['gg_fusion'][region][key]:
                    points['gg_fusion'][region][key].append( (m0, m1))
            else:
                if not (m0, m1) in points['bb_associatedProduction'][region][key]:
                    points['bb_associatedProduction'][region][key].append( (m0, m1))
    if all_:
        return all_points
    else:
        return points 


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


@ROOT.Numba.Declare(['RVec<float>'], 'float')
def computeHessianPDFUncertainty(weights):
    if len(weights) < 2:
        return 0.
    weights = np.asarray(weights)
    return np.sqrt(np.sum((weights[1:] - weights[0])**2))


def not_in_use_declareHessianPDFCalculator():
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
        if sampleCfg['type']== 'mc':
            pdf_mc = True
            logger.info("This sample has MC PDF variations")
        else:
            pdf_mc = False  ## signal sample produced with hessian pdf
            logger.info("This sample has Hessian PDF variations")
        
        nPdfVars = (0, 101) if pdf_mc else (1, 103)
        if hasattr(tree, "LHEPdfWeight"):
            if pdf_mode == "full" and sampleCfg['type']== 'mc':
                logger.info("Adding full PDF systematics")
                pdfVars = { f"pdf{i}": tree.LHEPdfWeight[i] for i in range(*nPdfVars) }
            
            elif pdf_mode == "simple":
                logger.info("Adding simplified PDF systematics")
                if sampleCfg['type']== 'mc':
                    pdfSigma = op.rng_stddev(tree.LHEPdfWeight)
                else:
                    logger.info("Signal sample has Hessian PDF variations: NNPDF31_nnlo_as_0118_mc_hessian_pdfas")
                    sigmaCalc = op.extMethod("Numba::computeHessianPDFUncertainty", returnType="float")
                    pdfSigma = sigmaCalc(tree.LHEPdfWeight)
                
                pdfVars = { "pdfup": tree.LHEPdfWeight[0] + pdfSigma, "pdfdown": tree.LHEPdfWeight[0] - pdfSigma }
            noSel = noSel.refine("PDF", weight=op.systematic(op.c_float(1.), **pdfVars))
        else:
            logger.warning("LHEPdfWeight not present in tree, PDF systematics will not be added")
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


def normalizeAndMergeSamplesForCombined(plots, counterReader, config, inDir, outPath):
    for smp, smpCfg in config["samples"].items():
        if smpCfg.get("group") == "data":
            #copy results file to outPath
            shutil.copyfile( os.path.join(inDir, f"{smp}.root"), os.path.join(outPath,f"{smp}.root"))
        else:
            resultsFile    = HT.openFileAndGet(os.path.join(inDir, f"{smp}.root"), mode="READ")
            normalizedFile = HT.openFileAndGet(os.path.join(outPath, f"{smp}.root"), "recreate")
            
            lumi = config["eras"][smpCfg["era"]]["luminosity"]
            smpScale = lumi / counterReader(resultsFile)[smpCfg["generated-events"]]
            
            if smpCfg.get("type") == "signal":
                smpScale *= smpCfg["cross-section"] * smpCfg["Branching-ratio"]
            elif smpCfg.get("type") == "mc":
                smpScale *= smpCfg["cross-section"]
            
            if plots is None: # do all 
                for k in resultsFile.GetListOfKeys():
                    h = resultsFile.Get(k.GetName())
                    h.Scale(smpScale)
                    h.Write()
                normalizedFile.Write()
                resultsFile.Close()
            else:
                for plot in plots:
                    hNom = resultsFile.Get(plot.name)
                    hNom.Scale(smpScale)
                    hNom.Write()
                    prefix = f"{plot.name}__"
                    for hk in resultsFile.GetListOfKeys():
                        if hk.GetName().startswith(prefix):
                            hV = resultsFile.Get(hk.GetName())
                            hV.Scale(smpScale)
                            hV.Write()
                normalizedFile.Write()
                resultsFile.Close()


def getSumw(resultsFile, smpCfg, readCounters=None):
    if "generated-events" in smpCfg:
        if isinstance(smpCfg["generated-events"], str):
            genEvts = readCounters(resultsFile)[smpCfg["generated-events"]]
        else:
            genEvts = smpCfg["generated-events"]
    else:
        genEvts = None
    return genEvts


def normalizeAndSumSamples(eras, samples, inDir, outPath, readCounters=lambda f: -1.):
    """
    Produce file containing the sum of all the histograms over the processes, 
    after normalizing the processes by their cross section, sum of weights and luminosity.
    Note: The systematics are handled but are expected to be SAME for all processes and eras.
    A separate output file is produced for each era (`outPath_era.root`), as well as a total one (`outPath_run2.root`).
    """
    for era in eras:
        lumi = eras[era]["luminosity"]
        mergedHists = {}
        for proc, cfg in samples.items():
            if cfg["era"] != era: continue
            if "syst" in cfg: continue
            xs = cfg["cross-section"]
            tf = HT.openFileAndGet(os.path.join(inDir, proc + ".root"))
            sumWgt = getSumw(tf, cfg, readCounters)
            keyList = tf.GetListOfKeys()
            for key in keyList:
                hist = key.ReadObj()
                if not hist.InheritsFrom("TH1"): continue
                hist.Scale(lumi * xs / sumWgt)
                name = hist.GetName()
                if name not in mergedHists:
                    mergedHists[name] = hist.Clone()
                    mergedHists[name].SetDirectory(0)
                else:
                    mergedHists[name].Add(hist)
            tf.Close()
        mergedFile = HT.openFileAndGet(outPath + "_" + era + ".root", "recreate")
        for hist in mergedHists.values():
            hist.Write()
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
