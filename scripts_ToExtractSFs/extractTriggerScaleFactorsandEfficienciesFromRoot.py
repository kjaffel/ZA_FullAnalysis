#! /bin/env python

import math
import argparse
import ROOT
import sys


def format_eta_bin(eta_bin):
    return 'ptabseta<%.1f' % (eta_bin[1]) if (eta_bin[0] == 0) else 'ptabseta%.1f-%.1f' % (eta_bin[0], eta_bin[1])

parser = argparse.ArgumentParser()
parser.add_argument('file', help='ROOT file containing Trigger  scale factors and efficiencies ')
parser.add_argument('-s', '--suffix', help='Suffix to append at the end of the output filename', required=True)

args = parser.parse_args()

IGNORE_LAST_PT_BIN = True

f = ROOT.TFile.Open(args.file)


for dirKey in f.GetListOfKeys():
    dirName = dirKey.GetName()
    directory = f.Get(dirName)
    for subDirKey in directory.GetListOfKeys():
        subDirName = subDirKey.GetName()
        subDir = directory.Get(subDirName)
        try:
            for entryKey in subDir.GetListOfKeys():
                print("%s/%s/%s"%(dirName,subDirName,entryKey.GetName()))
                wp =entryKey.GetName()
                h = f.GetDirectory(wp)
                #print ("wp", wp)
                eta_binning = []
                for i in range(1, h.GetXaxis().GetNbins() + 1):
                    if len(eta_binning) == 0:
                        print("pass1")
                        eta_binning.append(h.GetXaxis().GetBinLowEdge(i))
                        eta_binning.append(h.GetXaxis().GetBinUpEdge(i))
                    else:
                        print("pass2")
                        eta_binning.append(h.GetXaxis().GetBinUpEdge(i))
                    
                pt_binning = []
                for i in range(1, h.GetYaxis().GetNbins() + 1):
                    if len(pt_binning) == 0:
                        print("pass3")
                        pt_binning.append(h.GetYaxis().GetBinLowEdge(i))
                        pt_binning.append(h.GetYaxis().GetBinUpEdge(i))
                    else:
                        print("pass4")
                        pt_binning.append(h.GetYaxis().GetBinUpEdge(i))

                if IGNORE_LAST_PT_BIN and len(pt_binning) > 2:
                    pt_binning.pop()

                eta = 'Eta' if eta_binning[0] < 0 else 'AbsEta'
                json_content = {'dimension': 2, 'variables': [eta, 'Pt'], 'binning': {'x': eta_binning, 'y': pt_binning}, 'data': [], 'error_type': 'absolute'}
                json_content_data = json_content['data']

                for i in range(0, len(eta_binning) - 1):
                    eta_data = {'bin': [eta_binning[i], eta_binning[i + 1]], 'values': []}
                    mean_eta = (eta_binning[i] + eta_binning[i + 1]) / 2.
                    print(mean_eta)
                    for j in range(0, len(pt_binning) - 1):
                        mean_pt = (pt_binning[j] + pt_binning[j + 1]) / 2.
                        bin = h.FindBin(mean_eta, mean_pt)
                        error = h.GetBinError(bin)
                        pt_data = {'bin': [pt_binning[j], pt_binning[j + 1]], 'value': h.GetBinContent(bin), 'error_low': error, 'error_high': error}
                        eta_data['values'].append(pt_data)

                json_content_data.append(eta_data)
                filename = 'Muon_HLT_%s_%s.json' % (wp, args.suffix)
                with open(filename, 'w') as j:
                    import json
                    json.dump(json_content, j, indent=2)
        except:
            print("couldnt do this one!")
#sys.exit()
