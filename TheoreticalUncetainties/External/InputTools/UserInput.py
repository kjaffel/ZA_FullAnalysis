import json
import glob
import argparse

def readAllJson(json_file_path):
    json_info = {}
    for json_file in glob.glob(json_file_path):
        json_info.update(readJson(json_file))
    return json_info
def readJson(json_file_name):
    json_info = {}
    with open(json_file_name) as json_file:
        try:
            json_info = json.load(json_file)
        except ValueError as err:
            print "Error reading JSON file %s. The error message was:" % json_file_name 
            print(err)
    return json_info

def getDefaultParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_file", type=str, default="",
                        help="Name of file to be created (type pdf/png etc.) " \
                        "Note: Leave unspecified for auto naming")
    parser.add_argument("--legend_left", action="store_true",
                        help="Put legend left or right")
    parser.add_argument("--no_errors", action="store_true",
                        help="Include error bands")
    parser.add_argument("-l", "--luminosity", type=float, default=1340,
                        help="Luminsoity in pb-1. Default 1340")
    parser.add_argument("--nostack", action='store_true',
                        help="Don't stack hists")
    parser.add_argument("-r", "--no_ratio", action="store_true",
                        help="Do not add ratio comparison")
    parser.add_argument("--no_html", action='store_true',
                        help="Don't copy plot pdfs to website")
    parser.add_argument("--no_data", action='store_true',
                        help="Plot only Monte Carlo")
    parser.add_argument("--no_decorations", action='store_true',
                        help="Don't add CMS plot decorations")
    parser.add_argument("--logy", action='store_true',
                        help="Use logaritmic scale on Y-axis")
    parser.add_argument("-c","--channel", type=str, default="",
                        choices=['eee', 'eem', 'emm', 'mmm'],
                        help="Select only one channel")
    parser.add_argument("-f", "--files_to_plot", type=str, required=False,
                        default="all", help="Files to make plots from, "
                        "separated by a comma (match name in file_info.json)")
    return parser 
