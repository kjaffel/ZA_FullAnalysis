from bamboo.root import gbl
import os
import sys
import logging
logger = logging.getLogger("ZAInfos Plotter")

import bamboo.plots
class Plot(bamboo.plots.Plot):
    def produceQCDEnvelopes(self, bareResults, fbe):
        if any("__qcdScale" in h.GetName() for h in bareResults):
            hNom = next(h for h in bareResults if "__" not in h.GetName())
            prefix = f"{hNom.GetName()}__qcdScale"
            hVar_qcdScale = [ h for h in bareResults if h.GetName().startswith(prefix) ]
            if not all(hv.GetNcells() == hNom.GetNcells() for hv in hVar_qcdScale):
                logger.error("Variation histograms do not have the same binning as the nominal histogram")
            elif len(hVar_qcdScale) < 2:
                logger.error("At least two variations histograms must be provided")
            else: ## make an envelope from maximum deviations
                import numpy as np
                vars_cont = np.array([ [ hv.GetBinContent(i) for i in range(hv.GetNcells()) ] for hv in hVar_qcdScale ])
                hVar_up = hNom.Clone(f"{prefix}up")
                hVar_down = hNom.Clone(f"{prefix}down")
                from itertools import count
                for i,vl,vh in zip(count(), np.amin(vars_cont, axis=0), np.amax(vars_cont, axis=0)):
                    hVar_down.SetBinContent(i, vl)
                    hVar_up.SetBinContent(i, vh)
                return bareResults + [ hVar_up, hVar_down ]
        return bareResults

def SaveCutFlowReports(config, reportList, resultsdir=".", readCounters=lambda f : -1., eras=("all", None), verbose=False):
    eraMode, eras = eras
    f= open( os.path.join(resultsdir, "ZAInfos.txt"),"a")
    if not eras: ## from config if not specified
        eras = list(config["eras"].keys())
    ## helper: print one bamboo.plots.CutFlowReport.Entry
    def saveEntry(entry, printFun=logger.info, recursive=True):
        effMsg = ""
        if entry.parent:
            sumPass = entry.nominal.GetBinContent(1)
            sumTotal = entry.parent.nominal.GetBinContent(1)
            if sumTotal != 0.:
                effMsg = f", Eff={sumPass/sumTotal:.2%}"
        printFun(f"Selection {entry.name}: N={entry.nominal.GetEntries()}, SumW={entry.nominal.GetBinContent(1)}{effMsg}")
        f.write((f"- Selection {entry.name}: N={entry.nominal.GetEntries()}, SumW={entry.nominal.GetBinContent(1)}{effMsg}\n"))
        if recursive:
            for c in entry.children:
                saveEntry(c, printFun=printFun, recursive=recursive)
    ## retrieve results files
    resultsFiles = dict((smp, gbl.TFile.Open(os.path.join(resultsdir, f"{smp}.root"))) for smp, smpCfg in config["samples"].items() if smpCfg.get("era") in eras)
    for report in reportList:
        for smp, resultsFile in resultsFiles.items():
            smpCfg = config["samples"][smp]
            logger.info(f"Cutflow report {report.name} for sample {smp}")
            f.write('\n')
            f.write(f"Cutflow report for sample {smp}:\n")
            if "generated-events" in smpCfg:
                if isinstance(smpCfg["generated-events"], str):
                    generated_events = readCounters(resultsFile)[smpCfg["generated-events"]]
                else:
                    generated_events = smpCfg["generated-events"]
                logger.info(f"Sum of event weights for processed files: {generated_events:e}")
                f.write(f"Sum of event weights for processed files: {generated_events:e}\n")
            smpReport = report.readFromResults(resultsFile)
            for root in smpReport.rootEntries():
                saveEntry(root)
    f.close()
