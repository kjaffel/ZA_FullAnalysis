#!/usr/bin/env python
import logging
logger = logging.getLogger(__name__)
import json
import subprocess
import requests
import warnings

def getAODSIMName(dasName):
    if dasName.endswith("/AODSIM") or dasName.endswith("/GEN-SIM"):
        return dasName
    elif dasName.endswith("AODSIM"): ## nano->mini or mini->aod
        try:
            parent_resp = subprocess.check_output(["dasgoclient", "-json", "-query", f"parent dataset={dasName}"])
            parentName = json.loads(parent_resp)[0]["parent"][0]["parent_dataset"]
            logger.debug(f"    {dasName} --> {parentName}")
        except Exception as ex:
            logger.error(f"Problem getting parent dataset for {dasName}")
            return
        return getAODSIMName(parentName)
    else:
        raise ValueError("Cannot find ancestor AODSIM for dataset of tier {0}".format(dasName.split("/")[-1]))

def getPUDatasetName(aodSimName):
    prepid_resp = subprocess.check_output(["dasgoclient", "-json", "-query", f"dataset dataset={aodSimName} | grep dataset.prepid"])
    prepid = next(itm for itm in json.loads(prepid_resp) if "dbs3:dataset_info" in itm["das"]["services"])["dataset"][0]["prep_id"]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        req_mcm = requests.get(f"https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get/{prepid}", verify=False)
    return req_mcm.json()["results"]['pileup_dataset_name']

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find the premixing library used to produce a MC sample (from the MCM request of the ancestor AODSIM)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output")
    parser.add_argument("--aodsimIdentifier", help="String to search for in AODSIM name")
    parser.add_argument("dataset", nargs="+", help="Dataset names in DAS (MINI/NANO/)AODSIM")
    args = parser.parse_args()

    logging.basicConfig(level=(logging.DEBUG if args.verbose else logging.INFO))

    from collections import defaultdict
    id_good_datasets, id_bad_datasets = [], []
    datasets_per_PU = defaultdict(list)
    for dataset in args.dataset:
        aodSim = getAODSIMName(dataset)
        if args.aodsimIdentifier:
            if aodSim is not None and args.aodsimIdentifier in aodSim:
                id_good_datasets.append(dataset)
            else:
                id_bad_datasets.append(dataset)
        puLib = "NoneFound"
        if aodSim is not None and aodSim.endswith("/AODSIM"):
            puLib = getPUDatasetName(aodSim)
            logger.debug(f"PU dataset for {dataset}: {puLib}")
        datasets_per_PU[puLib].append(dataset)

    logger.info("Datasets by PU dataset")
    for puLib, datasets in datasets_per_PU.items():
        logger.info(f"Datasets made with PU dataset {puLib}")
        for dataset in datasets:
            logger.info(f"  - {dataset}")

    if args.aodsimIdentifier:
        logger.info("="*160)
        logger.info(f"Datasets with {args.aodsimIdentifier} in the AODSIM name:")
        for dataset in id_good_datasets:
            logger.info(f"  - {dataset}")
        logger.info(f"Datasets without {args.aodsimIdentifier} in the AODSIM name:")
        for dataset in id_bad_datasets:
            logger.info(f"  - {dataset}")
