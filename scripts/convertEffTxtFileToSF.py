#! /bin/env python

import math
import argparse
import ROOT

# define indexes in the 'systs' array
# Taken from https://twiki.cern.ch/twiki/pub/CMS/ElectronScaleFactorsRun2/efficiencyUtils.py.txt

iAltBkgModel = 0
iAltSigModel = 1
iAltMCSignal = 2
iAltTagSelec = 3

def format_eta_bin(eta_bin):
    return 'ptabseta<%.1f' % (eta_bin[1]) if (eta_bin[0] == 0) else 'ptabseta%.1f-%.1f' % (eta_bin[0], eta_bin[1])

parser = argparse.ArgumentParser()
parser.add_argument('file', help='Txt file containing electron scale factors')
parser.add_argument('-a', '--asymm-errors', action='store_true', dest='asymm', help='If True, expect to find in the text fields two fields for the errors instead of one, first high error and them down error')
parser.add_argument('-p', '--prefix', help='Prefix to prepend to the output filename')
parser.add_argument('-s', '--suffix', help='Suffix to append at the end of the output filename')
parser.add_argument('--no-systs', action='store_true', dest='no_systs', help='If True, do not consider the systematics errors from the input file')
parser.add_argument('--variated-systematics', action='store_true', dest='variated_systs', help='Use this flag if the systematics uncertainties are stored like "eff_mc + syst" instead of just "syst')
parser.add_argument('--indent', help='Identation of the JSON file', dest="indent", type=int, default=None)

args = parser.parse_args()


# Parse input files
# Structure is
# eta_low eta_up pt_low pt_up eff_data eff_data_err eff_mc eff_mc_err bkg_mod_err sig_mod_err range_err mc_err pu_err tag_sel_err

efficiencies = {}

with open(args.file, 'r') as f:
    eta_binning = []
    pt_binning = []

    for line in f:
        data = line.strip().split()
        if len(data) == 0:
            continue

        # Skip line if there's no number
        try:
            float(data[0])
        except ValueError:
            continue

        eta_bin = (float(data[0]), float(data[1]))
        pt_bin = (float(data[2]), float(data[3]))

        if len(eta_binning) == 0:
            eta_binning.extend(eta_bin)
        else:
            eta_binning.append(eta_bin[1])

        if len(pt_binning) == 0:
            pt_binning.extend(pt_bin)
        else:
            pt_binning.append(pt_bin[1])

        data_err_indexes = (5, 5)
        mc_index = 6
        mc_err_indexes = (7, 7)

        if args.asymm:
            data_err_indexes = (5, 6)
            mc_index = 7
            mc_err_indexes = (8, 9)

        eff = {
                'data': float(data[4]),
                'data_err': (float(data[data_err_indexes[0]]), float(data[data_err_indexes[1]])),
                'mc': float(data[mc_index]),
                'mc_err': (float(data[mc_err_indexes[0]]), float(data[mc_err_indexes[1]])),
                'systs': []
                }

        first_syst_index = mc_err_indexes[1] + 1
        for i in range(first_syst_index, len(data)):
            eff['systs'].append(float(data[i]))

        if len(eff['systs']) > 4:
            eff['systs'] = eff['systs'][:4]

        for n in range(len(eff['systs']), 4):
            eff['systs'].append(-1)

        if not eta_bin in efficiencies:
            efficiencies[eta_bin] = {}

        efficiencies[eta_bin][pt_bin] = eff

eta_binning = sorted(list(set(eta_binning)))
pt_binning = sorted(list(set(pt_binning)))

json_content = {'dimension': 2, 'variables': ['Eta', 'Pt'], 'binning': {'x': eta_binning, 'y': pt_binning}, 'data': [], 'error_type': 'absolute'}
json_content_data = json_content['data']


for i in range(0, len(eta_binning) - 1):
    eta_data = {'bin': [eta_binning[i], eta_binning[i + 1]], 'values': []}
    eta_bin = (eta_binning[i], eta_binning[i + 1])
    for j in range(0, len(pt_binning) - 1):
        pt_bin = (pt_binning[j], pt_binning[j + 1])
        eff = efficiencies[eta_bin][pt_bin]

        scale_factor = eff['data'] / eff['mc']

        mc_error_up_squared = eff['mc_err'][0]**2
        mc_error_down_squared = eff['mc_err'][1]**2

        data_error_up_squared = eff['data_err'][0]**2
        data_error_down_squared = eff['data_err'][1]**2

        if not args.no_systs:
            if args.variated_systs:
                eff['systs'][iAltBkgModel] -= eff['data']
                eff['systs'][iAltSigModel] -= eff['data']
                eff['systs'][iAltMCSignal] -= eff['mc']
                eff['systs'][iAltTagSelec] -= eff['data']

            for (i, syst) in enumerate(eff['systs']):
                if syst < 0:
                    continue

                if i == iAltMCSignal:
                    mc_error_up_squared += syst**2
                    mc_error_down_squared += syst**2
                else:
                    data_error_up_squared += syst**2
                    data_error_down_squared += syst**2

        scale_factor_error_up = math.sqrt(data_error_up_squared / eff['data']**2 + mc_error_up_squared / eff['mc']**2)
        scale_factor_error_down = math.sqrt(data_error_down_squared / eff['data']**2 + mc_error_down_squared / eff['mc']**2)

        pt_data = {'bin': [pt_binning[j], pt_binning[j + 1]], 'value': scale_factor, 'error_low': scale_factor_error_down, 'error_high': scale_factor_error_up}

        eta_data['values'].append(pt_data)

    json_content_data.append(eta_data)

# Save JSON file
import os
wp = os.path.splitext(os.path.basename(args.file))[0]
if args.prefix and args.suffix:
    filename = '%s_%s_%s.json' % (args.prefix, wp, args.suffix)
elif args.prefix and not args.suffix:
    filename = '%s_%s.json' % (args.prefix, wp)
elif not args.prefix and args.suffix:
    filename = '%s_%s.json' % (wp, args.suffix)
else :
    filename = '%s.json' % (wp)
with open(filename, 'w') as j:
    import json
    json.dump(json_content, j, indent=args.indent)
    print("JSON file saved as %r" % filename)
