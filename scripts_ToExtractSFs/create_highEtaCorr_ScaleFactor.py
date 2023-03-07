#! /bin/env python

import math
import argparse
import ROOT
import os
import numpy as np


eta_bins_array = np.linspace(-2.5, 2.5, 50)
eta_bins = eta_bins_array.tolist()
pt_bins_array = np.array([0., 5000.])
pt_bins = pt_bins_array.tolist()

json_content = {'dimension': 2, 'variables': ['Eta', 'Pt'], 'binning': {'x': eta_bins, 'y': pt_bins}, 'data': [], 'error_type': 'absolute'}
json_content_data = json_content['data']

for i in range(0, len(eta_bins) - 1):
    eta_bin = {'bin': [eta_bins[i], eta_bins[i + 1]], 'values': []}
    eta_center = (eta_bins[i+1] - eta_bins[i]) / 2 + eta_bins[i]
    eta_value = 1.01583 - 0.0190406*eta_center + 0.00696095*(math.pow(eta_center,2)) + 0.0156002*(math.pow(eta_center,3)) - 0.00658065*(math.pow(eta_center,4)) - 0.00313692*(math.pow(eta_center,5))
    eta_error_up = 1.
    eta_error_down = eta_value
    for j in range(0, len(pt_bins) - 1):
        pt_bin = {'bin': [pt_bins[j], pt_bins[j + 1]], 'value': eta_value, 'error_low': eta_value, 'error_high': 1.0}
        eta_bin['values'].append(pt_bin)
    json_content_data.append(eta_bin)

# Save JSON file
filename = 'Electrons_highEtaCorrection.json'
with open(filename, 'w') as j:
    import json
    json.dump(json_content, j, indent=2) 

