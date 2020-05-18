#!/usr/bin/env python
import sys
import argparse
tmparg = sys.argv[:]
sys.argv = []
import InputTools.WeightTools as weight_tools
import subprocess
import re
import os
sys.argv = tmparg

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file_name", required=True,
            help="EDM file name (should be full path, starting"
                "with '/store' for file on DAS"
    )
    return parser.parse_args()

def main():
    current_path = os.getcwd()
    os.chdir(sys.path[0])
    args  = getComLineArgs()
    command = ["cmsRun", "External/genXsec_cfg.py", "inputFiles=%s" % ",".join([args.file_name])]
    proc = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    for line in proc.stderr:
        if "After filter: final cross section" in line:
            values = re.findall("[0-9]+\.?[0-9]*(?:[Ee]\ *[-+]?\ *[0-9]+)?", line) 
            units = line.split()[-1]
            break
    print "Cross section from file is %s \pm %s %s (stat)" % (values[0], values[1], units) 
    print "\nComputing scale and PDF uncertainties" 
    variations = weight_tools.getWeightsFromEDMFile(args.file_name)
    unc = weight_tools.getScaleAndPDFUnc(variations)
    print "\nFinal values:"
    print "%s" % values[0] + \
        "^{%0.1f%%}_{%0.1f%%} (scale) \pm %0.1f (pdf+alpha_s) " % tuple(round(x*100, 1) for x in 
                [unc["scales"]["up"], unc["scales"]["down"], unc["pdf"]["up"]]) + \
        "%s" % units
    print "%s" % values[0] + \
        "^{%0.2e}_{%0.2e} (scale) \pm %0.2e (pdf+alpha_s) " % tuple(x*float(values[0]) for x in 
                [unc["scales"]["up"], unc["scales"]["down"], unc["pdf"]["up"]]) + \
        "\pm %s (stat) %s" % (values[1], units)
    print "\nNote that PDF+alpha_s uncertainty is taken only from NNPDF"
    os.chdir(current_path)
if __name__ == "__main__":
    main()
