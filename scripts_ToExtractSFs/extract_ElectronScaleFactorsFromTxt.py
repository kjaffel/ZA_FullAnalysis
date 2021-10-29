#! /bin/env python

import math
import argparse
import ROOT
import os

def format_eta_bin(eta_bin):
    return 'ptabseta<%.1f' % (eta_bin[1]) if (eta_bin[0] == 0) else 'ptabseta%.1f-%.1f' % (eta_bin[0], eta_bin[1])

parser = argparse.ArgumentParser()
parser.add_argument('file', help='Txt file containing electron scale factors')
parser.add_argument('-s', '--suffix', help='Suffix to append at the end of the output filename', required=True)

args = parser.parse_args()

# file name of the format /blahblah/electrons_mva_80p_Iso2016.txt
f = os.path.basename(args.file)
wp = f.strip('.txt').strip('electrons_')

# define sublist finder
# https://stackoverflow.com/questions/10106901/elegant-find-sub-list-in-list
def subfinder(mylist, pattern):
    matches = []
    for i in range(len(mylist)):
        if mylist[i] == pattern[0] and mylist[i:i+len(pattern)] == pattern:
            matches.append(pattern)
    return matches

# Moriond17: last pt bin is the same as the previous one, but with 100% error and should be ignored
IGNORE_LAST_PT_BIN = False

eta_binning = []
pt_binning = []
full_file_data = []
with open(args.file) as f:
    # Get binning
    for line in f:
        values = map(float, line.split())
        eta_low, eta_hig, pt_low, pt_hig, data, sigma_data, mc, sigma_mc, unc_1, unc_2, unc_3, unc_4 = values
        if eta_low not in eta_binning:
            eta_binning.append(eta_low)
        if eta_hig not in eta_binning:
            eta_binning.append(eta_hig)
        if pt_low not in pt_binning:
            pt_binning.append(pt_low)
        if pt_hig not in pt_binning:
            pt_binning.append(pt_hig)
        # computations taken from https://github.com/latinos/LatinoAnalysis/blob/eb0ce13d05c0c64e99467922e3ef1bd4ceae2a11/Gardener/python/variables/multiIdisoScaleFactors.py#L306
        scaleFactor = data / mc
        error_scaleFactor = math.sqrt((sigma_data / mc) * (sigma_data / mc) + (data / mc / mc * sigma_mc)*(data / mc / mc * sigma_mc))
        error_syst_scaleFactor = math.sqrt( pow(unc_1, 2) + pow(unc_2, 2) + pow(unc_3, 2) + pow(unc_4, 2))
        error_syst_scaleFactor = error_syst_scaleFactor / mc
        full_file_data.append([eta_low, eta_hig, pt_low, pt_hig, scaleFactor, error_scaleFactor, error_syst_scaleFactor])
    if IGNORE_LAST_PT_BIN and len(pt_binning) > 2:
        pt_binning.pop()


with open(args.file) as f:
    eta = 'Eta' if eta_binning[0] < 0 else 'AbsEta'
    json_content = {'dimension': 2, 'variables': [eta, 'Pt'], 'binning': {'x': eta_binning, 'y': pt_binning}, 'data': [], 'error_type': 'absolute'}
    # Get content
    json_content_data = json_content['data']

    for i in range(0, len(eta_binning) - 1):
        eta_data = {'bin': [eta_binning[i], eta_binning[i + 1]], 'values': []}
        mean_eta = (eta_binning[i] + eta_binning[i + 1]) / 2.
        for j in range(0, len(pt_binning) - 1):
            mean_pt = (pt_binning[j] + pt_binning[j + 1]) / 2.
            sf = None
            d_sf = None
            # pattern finding to find the correct data instead of parsing the file a second time
            # note: we're assuming that the file is correctly formed: there is no two lines with the same pt-eta bin...
            pattern = [eta_binning[i], eta_binning[i + 1], pt_binning[j], pt_binning[j + 1]]
            for d in full_file_data:
                matches = subfinder(d, pattern)
                if len(matches) > 0:
                    sf = d[4]
                    d_sf = math.sqrt(pow(d[5], 2) + pow(d[6], 2))
                    pt_data = {'bin': [pt_binning[j], pt_binning[j + 1]], 'value': sf, 'error_low': d_sf, 'error_high': d_sf}
                    eta_data['values'].append(pt_data)
        json_content_data.append(eta_data)

    # Save JSON file
    filename = 'Electron_%s_%s.json' % (wp, args.suffix)
    with open(filename, 'w') as j:
        import json
        json.dump(json_content, j, indent=2)            


