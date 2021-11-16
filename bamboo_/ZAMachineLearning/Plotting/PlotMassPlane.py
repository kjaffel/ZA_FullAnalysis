import os
import sys
import argparse
import copy
import json
import enlighten
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

import numpy as np
import multiprocessing as mp

from root_numpy import hist2array
from IPython import embed

# Avoid tensorflow print on standard error
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

sys.path.append(os.path.abspath('..'))
import Operations
from talos import Restore
from tdrstyle import setTDRStyle

class MassPlane:
    def __init__(self,pdf_path,x_bins,x_min,x_max,y_bins,y_min,y_max,inputs_order,additional_inputs={},plot_DY=False,plot_TT=False,plot_ZA=False,projection=False):
        self.pdf_path           = pdf_path
        self.x_bins             = x_bins
        self.x_min              = x_min
        self.x_max              = x_max
        self.y_bins             = y_bins
        self.y_min              = y_min
        self.y_max              = y_max
        self.model              = None
        self.inputs_order       = inputs_order
        self.additional_inputs  = additional_inputs
        self.plot_DY            = plot_DY
        self.plot_TT            = plot_TT
        self.plot_ZA            = plot_ZA
        self.projection         = projection
        # Produce grid #
        self.produce_grid()

    def produce_grid(self):
        self.X,self.Y = np.meshgrid(np.linspace(self.x_min,self.x_max,self.x_bins),np.linspace(self.y_min,self.y_max,self.y_bins))
        bool_upper = np.greater_equal(self.Y,self.X)
        self.X = self.X[bool_upper]
        self.Y = self.Y[bool_upper]
        self.x = self.X.reshape(-1,)  # mjj
        self.y = self.Y.reshape(-1,)  # mlljj
        # X, Y are 2D arrays, x,y are vectors of points

    @staticmethod
    def load_model(path_model):
        success = False
        while not success:
            try:
                model  = Restore(path_model, custom_objects={name:getattr(Operations,name) for name in dir(Operations) if name.startswith('op')}).model
                success = True
            except:
                pass
        # When multiple threads loading the model, try again if fails 
        return model

    def prepareInputs(self,mH,mA):
        N = self.x.shape[0]
        inputs = {'mH'              : np.ones(N)*mH,
                  'mA'              : np.ones(N)*mA,
                  'bb_M'            : self.x,
                  'llbb_M'          : self.y,
                  'bb_M_squared'    : np.power(self.x,2),
                  'llbb_M_squared'  : np.power(self.y,2),
                  'bb_M_x_llbb_M'   : np.multiply(self.x,self.y), }
        inputs.update({inpName:np.ones(N)*inpVal for inpName,inpVal in self.additional_inputs.items()})

        if set(self.inputs_order) != set(inputs.keys()):
            raise RuntimeError(f'The inputs in order are {inputs_order}, while you provide {inputs.keys()}, there is a mismatch so will stop here')
        inputsArrays = []
        for inpName in self.inputs_order:
            inputsArrays.append(inputs[inpName])
        return inputsArrays

    def plotMassPoint(self,args):
        path_model = args[0]
        mH = round(args[1],3)
        mA = round(args[2],3)
        #print ("Producing plot for MH = %.2f GeV, MA = %.2f"%(mH,mA))
        model  = self.load_model(path_model)
        output = model.predict(self.prepareInputs(mH,mA),batch_size=8192)
        if output.max() > 1.0:
            raise RuntimeError(f'Output max is {output.max()}, this should not happen')
        if output.min() < 0.0:
            raise RuntimeError(f'Output min is {output.min()}, this should not happen')

        N = self.x.shape[0]
        graph_list = []

        if self.plot_DY:
            g_DY = ROOT.TGraph2D(N,np.array(self.x,dtype='double'),np.array(self.y,dtype='double'),np.array(output[:,0],dtype='double'))
            g_DY.SetNpx(self.x_bins)
            g_DY.SetNpy(self.y_bins)
            g_DY.SetName(("MassPlane_DY_mH_%s_mA_%s"%(mH,mA)).replace('.','p'))
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
            graph_list.append(g_DY)

        if self.plot_TT:
            g_TT = ROOT.TGraph2D(N,np.array(self.x,dtype='double'),np.array(self.y,dtype='double'),np.array(output[:,1],dtype='double'))
            g_TT.SetNpx(self.x_bins)
            g_TT.SetNpy(self.y_bins)
            g_TT.GetHistogram().SetTitle("P(t#bar{t}) for mass point M_{H} = %.2f GeV, M_{A} = %.2f GeV"%(mH,mA))
            g_TT.SetName(("MassPlane_TT_mH_%s_mA_%s"%(mH,mA)).replace('.','p'))
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
            graph_list.append(g_TT)

        if self.plot_ZA:
            g_ZA = ROOT.TGraph2D(N,np.array(self.x,dtype='double'),np.array(self.y,dtype='double'),np.array(output[:,2],dtype='double'))
            g_ZA.SetNpx(self.x_bins)
            g_ZA.SetNpy(self.y_bins)
            g_ZA.GetHistogram().SetTitle("P(H#rightarrowZA) for mass point M_{H} = %.2f GeV, M_{A} = %.2f GeV"%(mH,mA))
            g_ZA.SetName(("MassPlane_ZA_mH_%s_mA_%s"%(mH,mA)).replace('.','p'))
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
            graph_list.append(g_ZA)

        return graph_list

    @staticmethod
    def getProjectionX(g):
        h = g.GetHistogram()
        xAxis = h.GetXaxis()
        yAxis = h.GetYaxis()
        Nx = h.GetNbinsX()
        Ny = h.GetNbinsY()
        hx = ROOT.TH1F(h.GetName()+'_px',h.GetName()+'_px',Nx,xAxis.GetBinLowEdge(1),xAxis.GetBinUpEdge(Nx))
        for ix in range(1,Nx+1):
            x = xAxis.GetBinCenter(ix)
            n_bins = 0
            for iy in range(1,Ny+1):
                y = yAxis.GetBinCenter(iy)
                if y >= x:
                    hx.SetBinContent(ix,hx.GetBinContent(ix)+h.GetBinContent(ix,iy))
                    n_bins += 1
            if n_bins == 0:
                n_bins = 1
            hx.SetBinContent(ix,hx.GetBinContent(ix)/n_bins)
        hx.SetTitle('Projection X')
        hx.GetYaxis().SetTitle("DNN output")
        hx.GetXaxis().SetTitle("m_{jj}")
        return hx 

    @staticmethod
    def getProjectionsX(g):
        h = g.GetHistogram()
        hxs = []
        colors = [int(50+i*50/h.GetNbinsY()) for i in range(0,h.GetNbinsY())]
        for iy in range(1,h.GetNbinsY()+1):
            hx = h.ProjectionX(h.GetName()+f'_{iy}px',iy,iy)
            hx.SetLineColor(colors[iy-1])
            hx.SetTitle('Projection X')
            hx.GetYaxis().SetTitle("DNN output")
            hx.GetXaxis().SetTitle("m_{jj}")
            hxs.append(hx)
        return hxs 

    @staticmethod
    def getProjectionY(g):
        h = g.GetHistogram()
        xAxis = h.GetXaxis()
        yAxis = h.GetYaxis()
        Nx = h.GetNbinsX()
        Ny = h.GetNbinsY()
        hy = ROOT.TH1F(h.GetName()+'_py',h.GetName()+'_py',Ny,yAxis.GetBinLowEdge(1),yAxis.GetBinUpEdge(Ny))
        for iy in range(1,Ny+1):
            y = yAxis.GetBinCenter(iy)
            n_bins = 0
            for ix in range(1,Nx+1):
                x = xAxis.GetBinCenter(ix)
                if y >= x:
                    hy.SetBinContent(iy,hy.GetBinContent(iy)+h.GetBinContent(ix,iy))
                    n_bins += 1
            if n_bins == 0:
                n_bins = 1
            hy.SetBinContent(iy,hy.GetBinContent(iy)/n_bins)
        hy.SetTitle('Projection Y')
        hy.GetYaxis().SetTitle("DNN output")
        hy.GetXaxis().SetTitle("m_{lljj}")
        return hy

    @staticmethod
    def getProjectionsY(g):
        h = g.GetHistogram()
        hys = []
        colors = [int(50+i*50/h.GetNbinsY()) for i in range(0,h.GetNbinsY())]
        for ix in range(1,h.GetNbinsX()+1):
            hy = h.ProjectionY(h.GetName()+f'_{ix}py',ix,ix)
            hy.SetLineColor(colors[ix-1])
            hy.SetTitle('Projection Y')
            hy.GetYaxis().SetTitle("DNN output")
            hy.GetXaxis().SetTitle("m_{lljj}")
            hys.append(hy)
        return hys 


    def plotOnCanvas(self, graph_list):
        path_out = os.path.dirname(self.pdf_path)
        if not os.path.isdir(path_out):
            os.makedirs(path_out)
        root_path = self.pdf_path.replace('.pdf','.root')
        outFile   = ROOT.TFile(root_path,"RECREATE")
        C = ROOT.TCanvas("C","C",800,600)
        #C.SetLogz()
        C.Print(self.pdf_path+"[")
        for g in graph_list:
            print ("Plotting %s"%g.GetName())
            g.Draw("colz")
            g_copy = g.Clone()
            contours = np.array([0.90,0.95,0.99])
            g_copy.GetHistogram().SetContour(contours.shape[0],contours)
            g_copy.Draw("cont2 same")
            g.Write()
            C.Print(self.pdf_path,"Title:"+g.GetName())
            if self.projection:
                # Full projection #
                hx = self.getProjectionX(g)
                hy = self.getProjectionY(g)
                hx.Draw("hist")
                hx.Write()
                C.Print(self.pdf_path,"Title:"+g.GetName()+" X projection")
                hy.Draw("hist")
                C.Print(self.pdf_path,"Title:"+g.GetName()+" Y projection")
                hy.Write()
                # Per line projection #
                C.Clear()
                hxs = self.getProjectionsX(g)
                hxs[0].Draw("hist")
                for hx in hxs[1:]:
                    hx.Draw("hist same")
                C.Print(self.pdf_path,"Title:"+g.GetName()+" X projections")
                C.Clear()
                hys = self.getProjectionsY(g)
                hys[0].Draw("hist")
                for hy in hys[1:]:
                    hy.Draw("hist same")
                C.Print(self.pdf_path,"Title:"+g.GetName()+" Y projections")

        C.Print(self.pdf_path+"]")
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
    #=====================================================================================================
    parser.add_argument('--mA', action='store', required=False, type=int, 
                   help='Mass of A for plot')
    parser.add_argument('--mH', action='store', required=False, type=int, 
                   help='Mass of H for plot')
    parser.add_argument('-p', '--process', action='store', required=True, choices=['ggH', 'bbH'],
                   help='predict model for ggfusion or b-associated production ')
    parser.add_argument('--resolved', action='store_true', required=False,  default=False,
                   help='predict model for resolved  regions')
    parser.add_argument('--boosted', action='store_true', required=False,  default=False,
                   help=' or in the boosted region')
    parser.add_argument('--channel', action='store', required=True, default=None, choices=['elel', 'mumu'],
                   help='from the channel we will get the pdgid')
    parser.add_argument('--era', action='store', required=True, type=int, choices=[2016, 2017, 2018],
                    help='predict model for different eras')
    #=====================================================================================================
    parser.add_argument('--DY', action='store_true', required=False, default=True,
                   help='Wether to plot the DY output')
    parser.add_argument('--TT', action='store_true', required=False, default=True,
                   help='Wether to plot the TT output')
    parser.add_argument('--ZA', action='store_true', required=False, default=True,
                   help='Wether to plot the ZA output')
    #=====================================================================================================
    parser.add_argument('--projection', action='store_true', required=False, default=False,
                   help='Wether also plot the projections in MH and MA')
    parser.add_argument('--pavement', action='store', nargs='+', required=False, default=None, type=float,
                   help='Produces pavement for all points considered, need to provide a cut value (can provide several)')
    parser.add_argument('--gif', action='store_true', required=False, default=False, 
                   help='Wether to produce the gif on all mass plane (overriden by --mA and --mH)')
    parser.add_argument('-j','--jobs', action='store', required=False, default=None, type=int,
                   help='Number of jobs for multiprocessing')
    #===================================================================================================== 
    args = parser.parse_args()

    inputs_order = ['pdgid','era','bb_M','llbb_M','bb_M_squared','llbb_M_squared','bb_M_x_llbb_M','mA','mH', 'isResolved', 'isBoosted', 'isggH', 'isbbH']
    inputs = {
        'isResolved' : args.resolved,
        'isBoosted'  : args.resolved,
        'isggH'      : True if 'ggH' in args.process else (False),
        'isbbH'      : True if 'bbH' in args.process else (False),
        'era'        : float(args.era),
        'pdgid'      : int(11) if args.channel=='elel' else int(13),
        }
    
    region = 'resolved' if args.resolved else ('boosted')
    pdf_path  = os.path.join(f'{args.model.split("all_combined")[0]}','plots',f'massplane_{os.path.basename(args.model).split(".")[0]}_{args.process}_{region}_{args.channel}_{args.era}.pdf')
    inst = MassPlane(pdf_path           = pdf_path,
                     x_bins             = 500,
                     x_min              = 0.,
                     x_max              = 1500.,
                     y_bins             = 500,
                     y_min              = 0.,
                     y_max              = 1500.,
                     plot_DY            = args.DY,
                     plot_TT            = args.TT,
                     plot_ZA            = args.ZA,
                     projection         = args.projection,
                     inputs_order       = inputs_order,
                     additional_inputs  = inputs)
    graph_list = []
    if args.mA and args.mH:
        graph_list.extend(inst.plotMassPoint([args.model,args.mH,args.mA]))
    elif not args.gif:
        # To pass when needed on all mass points !!
        #with open(os.path.join('data','points_0.500000_0.500000.json')) as f:
        #    d = json.load(f)
        #    masspoints = [(mH, mA,) for mA, mH in d]
        masspoints = [(200, 100), ( 300, 50), ( 300, 100), ( 300, 200)]
        pbar = enlighten.Counter(total=len(masspoints), desc='Progress', unit='mass points')
        if not args.jobs:
            inst.load_model(args.model)
            for masspoint in masspoints:
                graph_list.extend(inst.plotMassPoint([args.model,*masspoint]))
                pbar.update()
        else:
            pool = mp.Pool(args.jobs)
            for content in pool.imap(inst.plotMassPoint,[[args.model,*masspoint] for masspoint in masspoints]):
                graph_list.extend(content)
                pbar.update()
            pool.close()
            pool.join()
    inst.plotOnCanvas(graph_list)
    if args.pavement is not None:
        inst.makePavement(args.pavement, args.model)
