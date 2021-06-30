import ROOT
import array
import glob
import argparse

ROOT.gROOT.SetBatch(True)

def makeMATRIXHist(hist_file_name):
    data = readMATRIXHistData(hist_file_name)

    central_hist_name = hist_file_name.split("/")[-1].replace(".dat", "")
    nbins = len(data)-1
    varbins = array.array('f', [x[0] for x in data])
    central_hist = ROOT.TH1D(central_hist_name, central_hist_name, nbins, varbins)
    scale_up_hist = central_hist.Clone(central_hist_name + "__scaleUp")
    scale_up_hist.SetTitle(central_hist_name + "__scaleUp")
    scale_down_hist = central_hist.Clone(central_hist_name + "__scaleDown")
    scale_down_hist.SetTitle(central_hist_name + "__scaleDown")

    for i, entry in enumerate(data[:-1]):
        central_hist.SetBinContent(i+1, entry[1])
        central_hist.SetBinError(i+1, entry[2])
        scale_up_hist.SetBinContent(i+1, entry[3])
        scale_up_hist.SetBinError(i+1, entry[4])
        scale_down_hist.SetBinContent(i+1, entry[5])
        scale_down_hist.SetBinError(i+1, entry[6])
    
    return (central_hist, scale_up_hist, scale_down_hist)

def readMATRIXHistData(hist_file_name):
    data = []
    with open(hist_file_name) as hist_file:
        for line in hist_file:
            entry = line.split("#")[0]
            entry_data = [float(i) for i in entry.split()]
            if not entry_data:
                continue
            data.append(entry_data)
    if len(data[0]) != 7:
        raise(ValueError, "Invalid MATRIX output. Output should have 7 values per entry")
    return data

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file_path', type=str, required=True, help='folder with .dat files')
parser.add_argument('-o', '--output_path', type=str, required=True, help='output folder')
args = parser.parse_args()

canvas = ROOT.TCanvas("canvas", "canvas")

#hist_file_path = "result/run_07/NNLO-run/distributions/*.dat"
hist_file_path = '/'.join([args.file_path, "*.dat"])
output_path = args.output_path

for hist_file in glob.glob(hist_file_path):
    central, scale_up, scale_down = makeMATRIXHist(hist_file)
    central.SetMarkerSize(0)
    central.SetMinimum(central.GetMinimum()*.9)
    central.SetMaximum(central.GetMaximum()*1.1)
    central.Draw("hist e1")
    scale_up.SetLineColor(ROOT.kGray)
    scale_up.SetMarkerSize(0)
    scale_up.Draw("hist same e1")
    scale_down.SetLineColor(ROOT.kGray)
    scale_down.SetMarkerSize(0)
    scale_down.Draw("hist same e1")
    output_name = hist_file.split("/")[-1].replace(".dat","")
    canvas.Print(output_path + "/%s.pdf" % output_name)
    canvas.Print(output_path + "/%s.root" % output_name)
