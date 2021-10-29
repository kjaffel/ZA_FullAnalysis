#! /bin/env python

import math
import argparse
import ROOT
import numpy as np

#def format_eta_bin(eta_bin):
#    return 'ptabseta<%.1f' % (eta_bin[1]) if (eta_bin[0] == 0) else 'ptabseta%.1f-%.1f' % (eta_bin[0], eta_bin[1])

parser = argparse.ArgumentParser()
parser.add_argument('file', help='ROOT file containing muon tracking scale factors (eta-only)')
parser.add_argument('-s', '--suffix', help='Suffix to append at the end of the output filename', required=True)

args = parser.parse_args()


f = ROOT.TFile.Open(args.file)

for key in f.GetListOfKeys():
    wp = key.GetName()
    if 'ratio_eff_eta3_dr030e030_corr' not in wp:
        continue

    h = f.Get(wp)

    # Get binning
    eta_binning = []
    for i in range(0, h.GetN()):
        x = ROOT.Double(0.)
        y = ROOT.Double(0.)
        h.GetPoint(i, x, y)
        if len(eta_binning) == 0:
            eta_binning.append(x-h.GetErrorXlow(i))
            eta_binning.append(x+h.GetErrorXhigh(i))
        else:
            eta_binning.append(x+h.GetErrorXhigh(i))
#        print i, x, x-h.GetErrorXlow(i), x+h.GetErrorXhigh(i), y, y-h.GetErrorYlow(i), y+h.GetErrorYhigh(i)
#    print eta_binning

    pt_binning = [10., 14000.]

    eta = 'Eta' if eta_binning[0] < 0 else 'AbsEta'

    json_content = {'dimension': 2, 'variables': [eta, 'Pt'], 'binning': {'x': eta_binning, 'y': pt_binning}, 'data': [], 'error_type': 'absolute'}
    json_content_data = json_content['data']

    for i in range(0, len(eta_binning) - 1):
        x = ROOT.Double(0.)
        y = ROOT.Double(0.)
        eta_data = {'bin': [eta_binning[i], eta_binning[i + 1]], 'values': []}
        h.GetPoint(i, x, y)
        pt_data = {'bin': [pt_binning[0], pt_binning[1]], 'value': y, 'error_low': h.GetErrorYlow(i), 'error_high': h.GetErrorYhigh(i)}

        eta_data['values'].append(pt_data)

        json_content_data.append(eta_data)

    # Save JSON file
    filename = 'Muon_tracking_%s_%s.json' % (wp, args.suffix)
    with open(filename, 'w') as j:
        import json
        json.dump(json_content, j, indent=2)
