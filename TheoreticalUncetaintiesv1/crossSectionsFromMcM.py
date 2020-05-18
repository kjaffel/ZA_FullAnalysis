#!/usr/bin/env python

# Usage ./crossSectionsFromMcM -d "datasetname"
# Before using, run bash getCookie.sh to get the private cookie file
#
# Wildcards are supported. Note that it's always best to put them
# in quotes so they aren't expanded by bash
#
# Kenneth Long U. Wisconsin -- Madison
# 2016-05-12
#
import requests, cookielib
import subprocess
import argparse
import os

requests.packages.urllib3.disable_warnings()

parser = argparse.ArgumentParser()
parser.add_argument("--dataset_name", "-d", type=str, required=True)
args = parser.parse_args()

cookie_file = os.path.expanduser("~/private/prod-cookie.txt")
mcm_address = "https://cms-pdmv.cern.ch/mcm"
if not os.path.isfile(cookie_file):
    print "Cookie file not found in ~/private"
    print "You either forgot to run the getCookie.sh script or it failed"
    exit(1)
c = cookielib.MozillaCookieJar(cookie_file)
c.load()
search_options = {"db_name" : "requests", 
    "page" : -1,
    "dataset_name" : args.dataset_name}
r = requests.get("/".join([mcm_address, "search"]), params=search_options, cookies=c, verify=False)
for sample in r.json()["results"]:
    gen_params = sample["generator_parameters"]
    if len(gen_params) and "GS" in sample["prepid"]:
            # Sometimes generator_parameters has empty lists in it
            values = [i for i in gen_params if type(i) is dict]
            print "\nCross section for dataset %s" \
                  " from request %s" % (sample["dataset_name"], sample["prepid"])
            print "---->  sigma = %s pb" % values[-1]["cross_section"]
