import os
import sys
import argparse
import copy
import json
import ROOT

import numpy as np
from root_numpy import hist2array
sys.path.append(os.path.abspath('..'))

import Operations
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
        self.model  = Restore(path_model, custom_objects={name:getattr(Operations,name) for name in dir(Operations) if name.startswith('op')}).model
        #self.model = Restore(path_model, custom_objects={'PreprocessLayer': PreprocessLayer}).model
        self.model_name = os.path.basename(path_model).replace(".zip","")
        print(f'Path to model : {path_model}, {self.model_name} will be used as name for plotting')

    def plotMassPoint(self,mH,mA):
        print ("Producing plot for MH = %.2f GeV, MA = %.2f"%(mH,mA))
        N = self.x.shape[0]
        params = np.c_[np.ones(N)*mA,np.ones(N)*mH]
        #'l1_pdgId@op_pdgid', '$era@op_era', 'bb_M','llbb_M','bb_M_squared','llbb_M_squared', 'bb_M_x_llbb_M','$mA', '$mH'
        pdgid = 11.
        era   = 2016. 
        bb_M_squared   = pow(self.x,2)                                                    
        llbb_M_squared = pow(self.y,2)
        bb_M_x_llbb_M  = self.x * self.y
        pdgid = pdgid*np.ones(N)
        era   = era*np.ones(N)
        #print( pdgid, type(pdgid), pdgid.shape)
        #print( era, type(era) , era.shape)
        #print( self.x , type(self.x), self.x.shape)
        #print( self.y , type(self.y), self.y.shape)
        #print( bb_M_squared , type(bb_M_squared), bb_M_squared.shape)
        #print( llbb_M_squared, type(llbb_M_squared), llbb_M_squared.shape)
        #print( bb_M_x_llbb_M, type(self.x * self.y), bb_M_x_llbb_M.shape)

        v = np.c_[pdgid, era]
        variables = [bb_M_squared, llbb_M_squared, bb_M_x_llbb_M, self.x,self.y, mA, mH]
        inputsLL  = np.c_[v, bb_M_squared, llbb_M_squared, bb_M_x_llbb_M, self.x,self.y,params]
        #print( inputsLL )
        inputs    = np.hsplit(inputsLL,inputsLL.shape[1])
        output    = self.model.predict(inputs)

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

    def plotOnCanvas(self, path_model):
        setTDRStyle()
        path_out  = path_model.split('model')[0] + "plots/MassPlane/"
        if not os.path.isdir(path_out):
            os.makedirs(path_out)
        pdf_path  = path_out + self.model_name + ".pdf"
        root_path = pdf_path.replace('.pdf','.root')
        outFile   = ROOT.TFile(root_path,"RECREATE")
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

    def makePavement(self,contours, path_model):
        path_out  = path_model.split('model')[0] + "plots/MassPlane/"
        if not os.path.isdir(path_out):
            os.makedirs(path_out)
        for contour in contours:
            print ("Producing pavement for cut %.2f"%contour)
            pdf_path  = path_out + self.model_name+("_pave%0.2f"%contour).replace('.','p')+".pdf"
            root_path = pdf_path.replace('.pdf','.root')
            outFile   = ROOT.TFile(root_path,"RECREATE")
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
    parser.add_argument('--mA', action='store', required=False, type=int, 
                   help='Mass of A for plot')
    parser.add_argument('--mH', action='store', required=False, type=int, 
                   help='Mass of H for plot')
    parser.add_argument('--DY', action='store_true', required=False, default=True,
                   help='Wether to plot the DY output')
    parser.add_argument('--TT', action='store_true', required=False, default=True,
                   help='Wether to plot the TT output')
    parser.add_argument('--ZA', action='store_true', required=False, default=True,
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
        #with open(os.path.join('data','points_0.500000_0.500000.json')) as f:
        #   d = json.load(f)
        #   masspoints = [(mH, mA,) for mA, mH in d]
        masspoints = [( 300, 50), ( 300, 100), ( 300, 200),]
        for masspoint in masspoints:
            inst.plotMassPoint(*masspoint)
    
    inst.plotOnCanvas(args.model)
    if args.pavement is not None:
        inst.makePavement(args.pavement, args.model)
