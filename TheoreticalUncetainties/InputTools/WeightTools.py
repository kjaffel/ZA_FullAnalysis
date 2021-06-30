from collections import OrderedDict
import Utilities.scalePDFUncertainties as Uncertainty
from DataFormats.FWLite import Handle, Events, Runs
import ConfigHistFactory
import numpy
import os
import Ntuple
import ROOT
import logging

def getLHEInfoTag(holder, handle):
    check = holder.__iter__().next()
    lheLabel = "externalLHEProducer"
    check.getByLabel(lheLabel, handle)
    try:
        lheStuff = handle.product()
        return lheLabel
    except RuntimeError:
        pass
    try:
        lheLabel = "source"
        check.getByLabel(lheLabel, handle)
        lheStuff = handle.product()
        return lheLabel
    except:
        print "Error getting LHE info from file."
        print "Are you sure this file contains LHE weights?"
        raise
def getWeightsFromEDMFile(edm_file_name, cross_section=1):
    if "/store/" in edm_file_name:
        edm_file_name = "/".join(["root://cmsxrootd.fnal.gov/",
            edm_file_name])
    elif not os.path.isfile(edm_file_name):
        raise FileNotFoundException("File %s was not found." % edm_file_name)
    events = Events(edm_file_name)
    eventsHandle = Handle("LHEEventProduct")
    lheLabel = getLHEInfoTag(events, eventsHandle)
    lhe_weight_sums = []
    weight_ids = []
    for i, event in enumerate(events):
        event.getByLabel(lheLabel, eventsHandle)
        lheStuff = eventsHandle.product()
        weights = lheStuff.weights()
        #orig = lheStuff.originalXWGTUP()    
        if i == 0:
            weight_ids = [w.id for w in weights]
            lhe_weight_sums = [w.wgt for w in weights]
        else:
            for j, weight in enumerate(weights):
                lhe_weight_sums[j] += weight.wgt
    if cross_section != 0:
        norm = cross_section/lhe_weight_sums[0]
        lhe_weight_sums = [w*norm for w in lhe_weight_sums]
    return getVariations(weight_ids, lhe_weight_sums)
def getWeightsFromROOTFile(filename, analysis, cut, normalize):
    path = "/cms/kdlong" if "hep.wisc.edu" in os.environ['HOSTNAME'] else \
        "/afs/cern.ch/user/k/kelong/work"
    config_factory = ConfigHistFactory.ConfigHistFactory(
        "%s/AnalysisDatasetManager" % path,
        analysis
    )
    #config_factory.setProofAliases()
    all_files = config_factory.getFileInfo()
    mc_info = config_factory.getMonteCarloInfo()
    hist_factory = OrderedDict() 
    if filename not in all_files.keys():
        logging.warning("%s is not a valid file name (must match a definition in FileInfo/%s.json)" % \
            (filename, analysis))
    ntuple = Ntuple.Ntuple("LHEweights")
    tuple_name = "analyze%s/Ntuple" % ("WZ" if "WZ" in analysis else "ZZ")
    proof_name = "_".join([filename, "%s#/%s" % (analysis.replace("/", "_"), 
        tuple_name)])
    ntuple.setProofPath(proof_name)
    metaTree = ROOT.TChain(tuple_name.replace("Ntuple", "MetaData"))
    metaTree.Add(all_files[filename]["file_path"])
    weight_ids = []
    for row in metaTree:
        for weight_id in row.LHEweightIDs:
            weight_ids.append(weight_id)
        break
    weight_sums = ntuple.getSumWeights(config_factory.hackInAliases(cut))
    if len(weight_sums) == 1:
        return { "1000" : {"1001" : weight_sums[0]}}
    if normalize:
        proof_name = "_".join([filename, "%s#/%s" % (analysis.replace("/", "_"), 
            tuple_name.split("/")[0] + "/MetaData")])
        ntuple.setProofPath(proof_name)
        norm = mc_info[filename]["cross_section"]/ntuple.getBranchSum("initLHEweightSums[0]")
        weight_sums = [x*norm for x in weight_sums]

    return getVariations(weight_ids, weight_sums)
def getVariations(weight_ids, weight_sums):
    values = {"1000" : OrderedDict(), 
            "2000" : OrderedDict(), 
            "3000" : OrderedDict(),
            "4000" : OrderedDict()
    }
    if len(weight_ids) != len(weight_sums):
        print "Should have equal number of weights and IDs!!!"
        print "length of weight_ids: %i" % len(weight_ids) 
        print "length of weight_sums: %i" % len(weight_sums) 
        exit(1)
    if float(weight_ids[0]) > 10:
        for weight in zip(weight_ids, weight_sums):
            label = ''.join([weight[0][0], "000"]) 
            values[label][weight[0]] = weight[1]
    else:
        # Hackity hack hack for MadGraph LO samples
        for i,weight in enumerate(zip(weight_ids, weight_sums)):
            entry = 1
            weight_id = str(1000+i+1)
            if i > 8:
                entry = 2
                weight_id = str(2000+i-8)
            label = ''.join([str(entry), "000"]) 
            values[label][weight_id] = weight[1]
            if i > 109:
                break
    return values
def excludeKeysFromDict(values, exclude):
    return [x for key, x in values.iteritems()
            if key not in exclude]
def getScaleAndPDFUnc(variations):
    uncertainty = {}
    uncertainty["scales"] = Uncertainty.getScaleUncertainty(excludeKeysFromDict(
        variations["1000"], ["1001", "1006", "1008"])
    )
    uncertainty["pdf"] = Uncertainty.getFullNNPDFUncertainty(excludeKeysFromDict(
        variations["2000"], ["2101", "2102"]),
        [variations["2000"]["2101"], variations["2000"]["2102"]]
    )
    return uncertainty
