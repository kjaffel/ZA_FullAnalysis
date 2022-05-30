import ROOT
from interpolation import Interpolation
 

class HistogramFile(object):

    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.file = ROOT.TFile.Open(self.filename, 'read')
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.file.Close()

    def get_histogram(self, name):
        """Return the histogram identified by name from the file.
        """
        # The TFile::Get() method returns a pointer to an object stored in a ROOT file.
        hist = self.file.Get(name)
        if hist:
            return hist
        else:
            raise RuntimeError('Unable to retrieve histogram named {0} from {1}'.format(name, self.filename))


#get your histograms from the root file

f = ROOT.TFile.Open('ul_run2__ver8/results/GluGluToHToZATo2L2B_MH_300p00_MA_200p00_tb_1p50_TuneCP5_13TeV_madgraph_pythia8_UL17.root', 'read')
hist_2 = f.Get('DNNOutput_ZAnode_ElEl_resolved_DeepFlavourM_METCut_gg_fusion_MH_300_MA_200')


f1 = ROOT.TFile.Open('ul_run2__ver8/results/GluGluToHToZATo2L2B_MH_300p00_MA_100p00_tb_1p50_TuneCP5_13TeV_madgraph_pythia8_UL17.root', 'read')
hist_1 = f1.Get('DNNOutput_ZAnode_ElEl_resolved_DeepFlavourM_METCut_gg_fusion_MH_300_MA_100')


#and now interpolate

interpolator = Interpolation(100,200,150)

hist_3 = interpolator(hist_1,hist_2,"int_h3")

C = ROOT.TCanvas('canvas', '', 500, 500)
hist_3.Draw()
hist_1.SetLineColor(2)
hist_1.Draw("same")
hist_2.SetLineColor(3)
hist_2.Draw("same")

C.SaveAs('plot.pdf')


