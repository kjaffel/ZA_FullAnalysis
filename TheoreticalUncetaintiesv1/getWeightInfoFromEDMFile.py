#!/usr/bin/env python
import argparse
import re
import sys
tmparg = sys.argv[:]
sys.argv = []
import xml.etree.ElementTree as ET
from InputTools import EDMWeightInfo
from Utilities import LHAPDFInfo
from OutputTools import prettytable
sys.argv = tmparg
# Because pyROOT hijackes the command line args
def getComLineArgs():
    parser = argparse.ArgumentParser()


    parser.add_argument("-f", "--file_name", required=True,
            help="EDM file name (should be full path, starting"
                "with '/store' for file on DAS"
    )
    parser.add_argument("--print_header", action="store_true",
            help="Print the raw header containing weight information. " 
            "Useful for cases where the weight parsing does not work "
            "properly, including MadGraph LO samples"
    )
    return parser.parse_args()
def getPDFSetInfo(entry, lhapdf_info):
    weight_set = re.findall(r'\d+', entry)
    if len(weight_set) == 0:
        return ""
    weight_set = int(weight_set[0])
    for i in range(0,3):
        central_id = str(weight_set - (weight_set % 10**i))
        if central_id in lhapdf_info.keys():
            return lhapdf_info[central_id]
    # For pdfas sets entry central + 101 should be associated with central set
    central_id = str(weight_set - (weight_set % 10**i) - 100)
    if central_id in lhapdf_info.keys():
        return lhapdf_info[central_id]
    return ""
def main():
    args = getComLineArgs()
    lhapdf_info = LHAPDFInfo.getPDFIds()
    weight_info = EDMWeightInfo.getWeightIDs(args.file_name)
    print (weight_info)
    print_header = args.print_header
    if print_header:
        print (weight_info)
        return
    root = ET.fromstring("<header>" + weight_info + "</header>")
    other_weights_table = prettytable.PrettyTable(["Index", "LHE Weight ID", "LHE Weight Name"])
    pdf_weights_table = prettytable.PrettyTable(["Index", "LHE weight ID", "LHE Weight Name", "PDF set name", "LHAPDF set path"])
    i = 0
    for block in root:
        for entry in block:
            pdf_info = getPDFSetInfo(entry.text, lhapdf_info) 
            if pdf_info == "":
                other_weights_table.add_row([i, entry.attrib["id"], entry.text])
            else:
                pdf_weights_table.add_row([i, entry.attrib["id"], entry.text, pdf_info["name"],
                    pdf_info["path"]])
            i += 1
    print (other_weights_table)
    print (pdf_weights_table)

if __name__ == "__main__":
        main()
