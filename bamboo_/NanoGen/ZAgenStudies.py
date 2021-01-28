import os
import sys
import logging
logger = logging.getLogger("ZA NanoGen")

from bamboo.analysismodules import NanoAODHistoModule
from bamboo.analysisutils import makePileupWeight

from bamboo.plots import Plot
from bamboo.plots import EquidistantBinning as EqBin
from bamboo import treefunctions as op

GENPath = os.path.dirname(__file__)
if GENPath not in sys.path:
    sys.path.append(GENPath)

def addTheorySystematics(tree, noSel, qcdScale=True, PSISR=True, PSFSR=True, PDFs=True):
    if qcdScale:
        qcdScaleVariations = { f"qcdScalevar{i}": tree.LHEScaleWeight[i] for i in [0, 1, 3, 5, 7, 8] }
        qcdScaleSyst = op.systematic(op.c_float(1.), name="qcdScale", **qcdScaleVariations)
        noSel = noSel.refine("qcdScale", weight=qcdScaleSyst)

    if PSISR :#and "PS" not in buggySyst:
        psISRSyst = op.systematic(op.c_float(1.), name="psISR", up=tree.PSWeight[2], down=tree.PSWeight[0])
        noSel = noSel.refine("psISR", weight=psISRSyst)
    
    if PSFSR :#and "PS" not in buggySyst:
        psFSRSyst = op.systematic(op.c_float(1.), name="psFSR", up=tree.PSWeight[3], down=tree.PSWeight[1])
        noSel = noSel.refine("psFSR", weight=psFSRSyst)
    
    if PDFs:
        pdfsWeight = op.systematic(tree.LHEPdfWeight[0], name="pdfWgt", up=op.rng_max(tree.LHEPdfWeight[1:]), down=op.rng_min(tree.LHEPdfWeight[1:]))

    return noSel

from bamboo.treedecorators import NanoAODDescription
nanoGenDescription = NanoAODDescription(
    groups=["HTXS_", "Generator_", "MET_", "GenMET_", "LHE_", "GenVtx_"],
    collections=["nGenPart", "nGenJet", "nGenJetAK8", "nGenVisTau", "nGenDressedLepton", "nGenIsolatedPhoton", "nLHEPart"]
)
class NanoGenHtoZAPlotter(NanoAODHistoModule):
    """ H->Z(ll)A(bb) Nano-Gen studies """
    def __init__(self, args):
        super(NanoGenHtoZAPlotter, self).__init__(args)
        self.plotDefaults = {
                            "y-axis"           : "Events",
                            "log-y"            : "both",
                            "y-axis-show-zero" : True,
                            "save-extensions"  : ["pdf", "png"],
                            "show-ratio"       : True,
                            "sort-by-yields"   : False,
                            "legend-columns"   : 2
                            }
        self.doSysts = self.args.systematic
    def addArgs(self, parser):
        super(NanoGenHtoZAPlotter, self).addArgs(parser)
        parser.add_argument("-s", "--systematic", action="store_true", help="Produce systematic variations")
        parser.add_argument("--backend", type=str, default="dataframe", help="Backend to use, 'dataframe' (default) or 'lazy'")

    def prepareTree(self, tree, sample=None, sampleCfg=None):
        tree,noSel,be,lumiArgs = super(NanoGenHtoZAPlotter, self).prepareTree(tree, sample=sample, sampleCfg=sampleCfg, description=nanoGenDescription)
        if self.isMC(sample):
            # if it's a systematics sample, turn off other systematics
            if "syst" in sampleCfg:
                self.doSysts = False
            noSel = noSel.refine("mcWeight", weight=tree.genWeight, autoSyst=self.doSysts)
            if self.doSysts:
                noSel = utils.addTheorySystematics(self, sample, sampleCfg, tree, noSel)
        return tree,noSel,be,lumiArgs

    def definePlots(self, t, noSel, sample=None, sampleCfg=None):
        plots = []

        genVetoMuons = op.select(t.GenDressedLepton, lambda l : op.AND( op.abs(l.pdgId) == 13, op.abs(l.eta) < 2.4, l.pt > 15.))
        genMuons = op.select(genVetoMuons, lambda l : l.pt > 26.)
        genMuon = genMuons[0]

        genVetoElectrons = op.select(t.GenDressedLepton, lambda l : op.AND(op.abs(l.pdgId) == 11, op.abs(l.eta) < 2.5, l.pt > 15.))
        genElectrons = op.select(genVetoElectrons, lambda l : op.AND(l.pt > 29., op.abs(l.eta) < 2.4))
        genElectron = genElectrons[0]

        genJets = op.select(t.GenJet, lambda j : op.AND( j.pt > 20., op.abs(j.eta) < 2.4))
        genCleanedJets = op.select(genJets, lambda j: op.AND(
                            op.NOT(op.rng_any(genElectrons, lambda el: op.deltaR(j.p4, el.p4) < 0.4 )),
                            op.NOT(op.rng_any(genMuons, lambda mu: op.deltaR(j.p4, mu.p4) < 0.4 ))
                        ))

        genBJets = op.select(genCleanedJets, lambda jet: jet.hadronFlavour == 5)
        genLightJets = op.select(genCleanedJets, lambda jet: jet.hadronFlavour != 5)

        muonChannel = op.AND(
                op.rng_len(genMuons) == 1,
                op.rng_len(genVetoMuons) == 1,
                op.rng_len(genVetoElectrons) == 0
                )
        electronChannel = op.AND(
                op.rng_len(genVetoMuons) == 0,
                op.rng_len(genVetoElectrons) == 1,
                op.rng_len(genElectrons) == 1
                )
        # the 2 channels are exclusive, so we can safely combine them in a single selection
        genOneLepSel = noSel.refine("lepton", cut=op.OR(muonChannel, electronChannel))

        plots.append(Plot.make1D("nBJets", op.rng_len(genBJets), noSel,
                    EqBin(7, 0., 7.), title="Number of b jets"))
        plots.append(Plot.make1D("nLightJets", op.rng_len(genBJets), noSel,
                    EqBin(7, 0., 7.), title="Number of light jets"))

        return plots
