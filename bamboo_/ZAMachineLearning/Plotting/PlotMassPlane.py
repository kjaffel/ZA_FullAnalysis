import os
import sys
import argparse
import copy
import numpy as np
from root_numpy import hist2array
import ROOT

sys.path.append(os.path.abspath('..'))
from talos import Restore
from preprocessing import PreprocessLayer
from tdrstyle import setTDRStyle

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

class MassPlane:
    def __init__(self,x_bins,x_min,x_max,y_bins,y_min,y_max,plot_DY=False,plot_TT=False,plot_ZA=False,profile=False):
        self.x_bins     = x_bins
        self.x_min      = x_min
        self.x_max      = x_max
        self.y_bins     = y_bins
        self.y_min      = y_min
        self.y_max      = y_max
        self.model      = None
        self.plot_DY    = plot_DY
        self.plot_TT    = plot_TT
        self.plot_ZA    = plot_ZA
        self.profile    = profile
        self.graph_list = []

        # Produce grid #
        self.produce_grid()


    def produce_grid(self):
        self.X,self.Y = np.meshgrid(np.linspace(self.x_min,self.x_max,self.x_bins),np.linspace(self.y_min,self.y_max,self.y_bins))
        bool_upper = np.greater_equal(self.Y,self.X)
        self.X = self.X[bool_upper]
        self.Y = self.Y[bool_upper]
        self.x = self.X.reshape(-1,1)
        self.y = self.Y.reshape(-1,1)
        # X, Y are 2D arrays, x,y are vectors of points

    def load_model(self,path_model):
        print(path_model)
        self.model = Restore(path_model, custom_objects={'PreprocessLayer': PreprocessLayer}).model
        self.model_name = os.path.basename(path_model).replace(".zip","")


    def plotMassPoint(self,mH,mA):
        print ("Producing plot for MH = %.2f GeV, MA = %.2f"%(mH,mA))
        N = self.x.shape[0]
        params = np.c_[np.ones(N)*mA,np.ones(N)*mH]
        inputs = np.c_[self.x,self.y,params]
        output = self.model.predict(inputs)

        g_DY = ROOT.TGraph2D(N)
        g_DY.SetNpx(500)
        g_DY.SetNpy(500)
        g_TT = ROOT.TGraph2D(N)
        g_TT.SetNpx(500)
        g_TT.SetNpy(500)
        g_ZA = ROOT.TGraph2D(N)
        g_ZA.SetNpx(500)
        g_ZA.SetNpy(500)

        g_DY.SetName(("MassPlane_DY_mH_%s_mA_%s"%(mH,mA)).replace('.','p'))
        g_TT.SetName(("MassPlane_TT_mH_%s_mA_%s"%(mH,mA)).replace('.','p'))
        g_ZA.SetName(("MassPlane_ZA_mH_%s_mA_%s"%(mH,mA)).replace('.','p'))

        for i in range(N):
            if self.plot_DY:
                g_DY.SetPoint(i,self.x[i],self.y[i],output[i,0])
            if self.plot_TT:
                g_TT.SetPoint(i,self.x[i],self.y[i],output[i,1])
            if self.plot_ZA:
                g_ZA.SetPoint(i,self.x[i],self.y[i],output[i,2])

        if self.plot_DY:
            self.graph_list.append(g_DY)
            g_DY.GetHistogram().SetTitle("P(DY) for mass point M_{H} = %.2f GeV, M_{A} = %.2f GeV"%(mH,mA))
            g_DY.GetHistogram().GetXaxis().SetTitle("M_{jj} [GeV]")
            g_DY.GetHistogram().GetYaxis().SetTitle("M_{lljj} [GeV]")
            g_DY.GetHistogram().GetZaxis().SetTitle("DNN output")
            g_DY.GetHistogram().GetZaxis().SetRangeUser(0.,1.)
            g_DY.GetHistogram().SetContour(100)
            g_DY.GetXaxis().SetTitleOffset(1.2)
            g_DY.GetYaxis().SetTitleOffset(1.2)
            g_DY.GetZaxis().SetTitleOffset(1.2)
            g_DY.GetXaxis().SetTitleSize(0.045)
            g_DY.GetYaxis().SetTitleSize(0.045)
            g_DY.GetZaxis().SetTitleSize(0.045)

        if self.plot_TT:
            g_TT.GetHistogram().SetTitle("P(t#bar{t}) for mass point M_{H} = %.2f GeV, M_{A} = %.2f GeV"%(mH,mA))
            g_TT.GetHistogram().GetXaxis().SetTitle("M_{jj} [GeV]")
            g_TT.GetHistogram().GetYaxis().SetTitle("M_{lljj} [GeV]")
            g_TT.GetHistogram().GetZaxis().SetTitle("DNN output")
            g_TT.GetHistogram().GetZaxis().SetRangeUser(0.,1.)
            g_TT.GetHistogram().SetContour(100)
            g_TT.GetXaxis().SetTitleOffset(1.2)
            g_TT.GetYaxis().SetTitleOffset(1.2)
            g_TT.GetZaxis().SetTitleOffset(1.2)
            g_TT.GetXaxis().SetTitleSize(0.045)
            g_TT.GetYaxis().SetTitleSize(0.045)
            g_TT.GetZaxis().SetTitleSize(0.045)
            self.graph_list.append(g_TT)

        if self.plot_ZA:
            g_ZA.GetHistogram().SetTitle("P(H#rightarrowZA) for mass point M_{H} = %.2f GeV, M_{A} = %.2f GeV"%(mH,mA))
            g_ZA.GetHistogram().GetXaxis().SetTitle("M_{jj} [GeV]")
            g_ZA.GetHistogram().GetYaxis().SetTitle("M_{lljj} [GeV]")
            g_ZA.GetHistogram().GetZaxis().SetTitle("DNN output")
            g_ZA.GetHistogram().GetZaxis().SetRangeUser(0.,1.)
            g_ZA.GetHistogram().SetContour(100)
            g_ZA.GetXaxis().SetTitleOffset(1.2)
            g_ZA.GetYaxis().SetTitleOffset(1.2)
            g_ZA.GetZaxis().SetTitleOffset(1.2)
            g_ZA.GetXaxis().SetTitleSize(0.045)
            g_ZA.GetYaxis().SetTitleSize(0.045)
            g_ZA.GetZaxis().SetTitleSize(0.045)
            self.graph_list.append(g_ZA)

    @staticmethod
    def getProfiles(g):
        h = g.GetHistogram()
        xproj = h.ProjectionX()
        yproj = h.ProjectionY()
        array = hist2array(h)
        # Need to compensate the triangular binning
        nonzeroXbins = h.GetNbinsY()/np.count_nonzero(array,axis=1)
        nonzeroYbins = h.GetNbinsX()/np.count_nonzero(array,axis=0)
        for x in range(1,h.GetNbinsX()):
            xproj.SetBinContent(x,xproj.GetBinContent(x)*nonzeroXbins[x-1])
        for y in range(1,h.GetNbinsY()):
            yproj.SetBinContent(y,yproj.GetBinContent(y)*nonzeroYbins[y-1])
        xproj.GetYaxis().SetTitle("DNN output")
        yproj.GetYaxis().SetTitle("DNN output")

        return xproj, yproj


    def plotOnCanvas(self):
        setTDRStyle()
        pdf_path = "MassPlane/"+self.model_name+".pdf"
        root_path = pdf_path.replace('.pdf','.root')
        outFile = ROOT.TFile(root_path,"RECREATE")
        C = ROOT.TCanvas("C","C",800,600)
        #C.SetLogz()
        C.Print(pdf_path+"[")
        for g in self.graph_list:
            print ("Plotting %s"%g.GetName())
            g.Draw("colz")
            g_copy = g.Clone()
            contours = np.array([0.90,0.95,0.99])
            g_copy.GetHistogram().SetContour(contours.shape[0],contours)
            g_copy.Draw("cont2 same")
            g.Write()
            C.Print(pdf_path,"Title:"+g.GetName())
            if self.profile:
                xproj,yproj = self.getProfiles(g)
                xproj.Draw("hist")
                xproj.Write()
                C.Print(pdf_path,"Title:"+g.GetName()+" X profile")
                yproj.Draw("hist")
                C.Print(pdf_path,"Title:"+g.GetName()+" Y profile")
                yproj.Write()

        C.Print(pdf_path+"]")
        outFile.Close()
        print ("Root file saved as %s"%root_path)

    def makePavement(self,contours):
        for contour in contours:
            print ("Producing pavement for cut %.2f"%contour)
            pdf_path = "MassPlane/"+self.model_name+("_pave%0.2f"%contour).replace('.','p')+".pdf"
            root_path = pdf_path.replace('.pdf','.root')
            outFile = ROOT.TFile(root_path,"RECREATE")
            C = ROOT.TCanvas("C","C",800,600)
            opt = 'cont2'
            new_graph_list = [g.Clone() for g in self.graph_list]
            # Need them saved in a list otherwise they are deleted and canvas is blank
            for g in new_graph_list:
                print ('Adding to contour plot',g.GetName())
                g.SetTitle("Pavement for cut %0.2f"%contour)
                g.GetHistogram().SetContour(1,np.array([contour]))
                g.Draw(opt)
                if 'same' not in opt : opt += " same"
                g.Write()
            
            C.Print(pdf_path)
            outFile.Close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to plot mass plane with Neural Net')
    parser.add_argument('--model', action='store', required=True, type=str, 
                   help='Path to model (in zip file)')
    parser.add_argument('-mA', action='store', required=False, type=int, 
                   help='Mass of A for plot')
    parser.add_argument('-mH', action='store', required=False, type=int, 
                   help='Mass of H for plot')
    parser.add_argument('-DY', action='store_true', required=False, default=False,
                   help='Wether to plot the DY output')
    parser.add_argument('-TT', action='store_true', required=False, default=False,
                   help='Wether to plot the TT output')
    parser.add_argument('-ZA', action='store_true', required=False, default=False,
                   help='Wether to plot the ZA output')
    parser.add_argument('--profile', action='store_true', required=False, default=False,
                   help='Wether also plot the profiles in MH and MA')
    parser.add_argument('--pavement', action='store', nargs='+', required=False, default=None, type=float,
                   help='Produces pavement for all points considered, need to provide a cut value (can provide several)')
    parser.add_argument('--gif', action='store_true', required=False, default=False, 
                   help='Wether to produce the gif on all mass plane (overriden by --mA and --mH)')
    args = parser.parse_args()

    inst = MassPlane(500,0,1500,500,0,1500,args.DY,args.TT,args.ZA,args.profile)
    inst.load_model(args.model)

    if args.mA and args.mH:
        inst.plotMassPoint(args.mH,args.mA)
    elif not args.gif:
        masspoints = [(132.0, 30.0),
                      (132.0, 37.34),
                      (143.44, 30.0),
                      (143.44, 37.34),
                      (143.44, 46.48),
                      (157.77, 30.0),
                      (157.77, 37.34),
                      (157.77, 46.48),
                      (157.77, 57.85),
                      (173.52, 30.0),
                      (173.52, 37.34),
                      (173.52, 46.48),
                      (173.52, 57.85),
                      (173.52, 72.01),
                      (190.85, 30.0),
                      (190.85, 37.34),
                      (190.85, 46.48),
                      (190.85, 57.85),
                      (190.85, 71.28),
                      (190.85, 86.78),
                      (200.0, 50.0),
                      (200.0, 100.0),
                      (209.9, 30.0),
                      (209.9, 37.34),
                      (209.9, 46.48),
                      (209.9, 57.71),
                      (209.9, 71.15),
                      (209.9, 86.79),
                      (209.9, 104.53),
                      (230.77, 30.0),
                      (230.77, 37.1),
                      (230.77, 45.88),
                      (230.77, 56.73),
                      (230.77, 69.78),
                      (230.77, 85.09),
                      (230.77, 102.72),
                      (230.77, 123.89),
                      (250.0, 50.0),
                      (250.0, 100.0),
                      (261.4, 37.1),
                      (261.4, 45.88),
                      (261.4, 56.73),
                      (261.4, 69.66),
                      (261.4, 85.1),
                      (261.4, 102.99),
                      (261.4, 124.53),
                      (261.4, 150.5),
                      (296.1, 30.0),
                      (296.1, 36.79),
                      (296.1, 45.12),
                      (296.1, 55.33),
                      (296.1, 67.65),
                      (296.1, 82.4),
                      (296.1, 99.9),
                      (296.1, 120.82),
                      (296.1, 145.93),
                      (296.1, 176.02),
                      (300.0, 50.0),
                      (300.0, 100.0),
                      (300.0, 200.0),
                      (335.4, 30.0),
                      (335.4, 36.79),
                      (335.4, 45.12),
                      (335.4, 55.33),
                      (335.4, 67.54),
                      (335.4, 82.14),
                      (335.4, 99.61),
                      (335.4, 120.39),
                      (335.4, 145.06),
                      (335.4, 174.55),
                      (335.4, 209.73),
                      (379.0, 30.0),
                      (379.0, 36.63),
                      (379.0, 44.72),
                      (379.0, 54.59),
                      (379.0, 66.57),
                      (379.0, 80.99),
                      (379.0, 98.26),
                      (379.0, 118.81),
                      (379.0, 143.08),
                      (379.0, 171.71),
                      (379.0, 205.76),
                      (379.0, 246.3),
                      (442.63, 30.0),
                      (442.63, 36.64),
                      (442.63, 44.76),
                      (442.63, 54.67),
                      (442.63, 66.49),
                      (442.63, 80.03),
                      (442.63, 95.27),
                      (442.63, 113.53),
                      (442.63, 135.44),
                      (442.63, 161.81),
                      (442.63, 193.26),
                      (442.63, 230.49),
                      (442.63, 274.57),
                      (442.63, 327.94),
                      (500.0, 50.0),
                      (500.0, 100.0),
                      (500.0, 200.0),
                      (500.0, 300.0),
                      (500.0, 400.0),
                      (516.94, 30.0),
                      (516.94, 36.47),
                      (516.94, 44.34),
                      (516.94, 53.9),
                      (516.94, 65.52),
                      (516.94, 78.52),
                      (516.94, 93.12),
                      (516.94, 109.3),
                      (516.94, 128.58),
                      (516.94, 151.69),
                      (516.94, 179.35),
                      (516.94, 212.14),
                      (516.94, 250.63),
                      (516.94, 296.65),
                      (516.94, 352.61),
                      (516.94, 423.96),
                      (609.21, 30.0),
                      (609.21, 34.86),
                      (609.21, 40.51),
                      (609.21, 47.08),
                      (609.21, 54.71),
                      (609.21, 63.58),
                      (609.21, 85.86),
                      (609.21, 99.78),
                      (609.21, 116.29),
                      (609.21, 135.66),
                      (609.21, 158.41),
                      (609.21, 185.18),
                      (609.21, 216.52),
                      (609.21, 253.68),
                      (609.21, 298.01),
                      (609.21, 351.22),
                      (609.21, 417.76),
                      (609.21, 505.93),
                      (650.0, 50.0),
                      (717.96, 30.0),
                      (717.96, 34.86),
                      (717.96, 40.51),
                      (717.96, 47.08),
                      (717.96, 54.71),
                      (717.96, 63.58),
                      (717.96, 73.89),
                      (717.96, 85.86),
                      (717.96, 99.78),
                      (717.96, 116.19),
                      (717.96, 157.56),
                      (717.96, 183.48),
                      (717.96, 213.73),
                      (717.96, 249.34),
                      (717.96, 291.34),
                      (717.96, 341.02),
                      (717.96, 400.03),
                      (717.96, 475.8),
                      (717.96, 577.65),
                      (800.0, 50.0),
                      (800.0, 100.0),
                      (800.0, 200.0),
                      (800.0, 400.0),
                      (800.0, 700.0),
                      (846.11, 30.0),
                      (846.11, 34.93),
                      (846.11, 40.68),
                      (846.11, 47.37),
                      (846.11, 55.16),
                      (846.11, 64.24),
                      (846.11, 74.8),
                      (846.11, 87.1),
                      (846.11, 101.43),
                      (846.11, 118.11),
                      (846.11, 137.54),
                      (846.11, 160.17),
                      (846.11, 186.51),
                      (846.11, 217.19),
                      (846.11, 252.91),
                      (846.11, 294.51),
                      (846.11, 345.53),
                      (846.11, 405.4),
                      (846.11, 475.64),
                      (846.11, 558.06),
                      (846.11, 654.75),
                      (997.14, 30.0),
                      (997.14, 34.93),
                      (997.14, 40.68),
                      (997.14, 47.37),
                      (997.14, 55.16),
                      (997.14, 64.24),
                      (997.14, 74.8),
                      (997.14, 87.1),
                      (997.14, 101.43),
                      (997.14, 118.11),
                      (997.14, 137.54),
                      (997.14, 160.17),
                      (997.14, 186.51),
                      (997.14, 217.19),
                      (997.14, 254.82),
                      (997.14, 298.97),
                      (997.14, 350.77),
                      (997.14, 411.54),
                      (997.14, 482.85),
                      (997.14, 566.51),
                      (997.14, 664.66),
                      (997.14, 779.83),
                      (1000.0, 50.0),
                      (1000.0, 200.0),
                      (1000.0, 500.0)]
        for masspoint in masspoints:
            inst.plotMassPoint(*masspoint)
        #inst.plotMassPoint(200,50)
        #inst.plotMassPoint(200,100)
        #inst.plotMassPoint(250,50)
        #inst.plotMassPoint(250,100)
        #inst.plotMassPoint(300,50)
        #inst.plotMassPoint(300,100)
        #inst.plotMassPoint(300,200)
        #inst.plotMassPoint(500,50)
        #inst.plotMassPoint(500,100)
        #inst.plotMassPoint(500,200)
        #inst.plotMassPoint(500,300)
        #inst.plotMassPoint(500,400)
        #inst.plotMassPoint(650,50)
        #inst.plotMassPoint(800,50)
        #inst.plotMassPoint(800,100)
        #inst.plotMassPoint(800,200)
        #inst.plotMassPoint(800,400)
        #inst.plotMassPoint(800,700)
        #inst.plotMassPoint(1000,50)
        #inst.plotMassPoint(1000,100)
        #inst.plotMassPoint(1000,200)
        #inst.plotMassPoint(1000,500)

    inst.plotOnCanvas()
    if args.pavement is not None:
        inst.makePavement(args.pavement)
