import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('analysis')
options.parseArguments()
process = cms.Process('genPrint')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 100

secFiles = cms.untracked.vstring() 
process.source = cms.Source ("PoolSource",
    fileNames = cms.untracked.vstring(options.inputFiles), 
    secondaryFileNames = secFiles
)
process.printTree = cms.EDAnalyzer("ParticleListDrawer",
  printVertex = cms.untracked.bool(False),
  printOnlyHardInteraction = cms.untracked.bool(False), # Print only status=3 particles. This will not work for Pythia8, which does not have any such particles.
  src = cms.InputTag("genParticles")
)

process.genPrint = cms.Path(process.printTree)
process.schedule = cms.Schedule(process.genPrint)
