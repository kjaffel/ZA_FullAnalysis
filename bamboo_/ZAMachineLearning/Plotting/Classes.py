import os
import sys
import glob
import copy
import logging
import yaml
import string
import itertools
import ROOT

import numpy as np
import matplotlib.pyplot as plt

from ROOT import TFile, TH1F, TH2F, TCanvas, gROOT, TGaxis, TPad, TLegend, TImage, THStack
from array import array
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import confusion_matrix
from root_numpy import root2array, rec2array
from scipy import interp
from sklearn import metrics
from matplotlib.pyplot import cm

import tdrstyle

gROOT.LoadMacro("formulas.C")
SMALL_SIZE  = 14
MEDIUM_SIZE = 20
BIGGER_SIZE = 22

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

class Plot_TH1:
    def __init__(self,filepath,filename,tree,variable,cut,name,bins,xmin,xmax,title,xlabel,ylabel,weight=None,logx=False,logy=False,option='hist'):
        self.filepath = filepath
        self.filename = filename
        self.tree = tree
        self.variable = variable
        self.weight = weight
        self.cut = cut
        self.name = name
        self.bins = bins
        self.xmin = xmin
        self.xmax = xmax
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.logx = logx
        self.logy = logy
        self.option = option

    def MakeHisto(self):
        file_handle = TFile.Open(self.filepath)
        tree = file_handle.Get(self.tree)
        if not tree:
            logging.error("Could not open tree '%s' from file '%s'"%(self.tree,self.filename))
        first_arg = self.variable+'>>'+self.name+'('+str(self.bins)+','+str(self.xmin)+','+str(self.xmax)+')'
        if self.weight and self.weight != '' and self.cut != '':
            second_arg = self.weight + "* (" + self.cut + ")"
        elif self.weight and self.weight != '':
            second_arg = self.weight
        elif self.cut != '':
            second_arg = self.cut
        else:
            second_arg = ''
        tree.Draw(first_arg,second_arg,"goff")    
        histo = gROOT.FindObject(self.name)
        try: 
            histo.ClassName()
        except ReferenceError:
            raise RuntimeError('Could not produce histogram %s'%self.name)
        histo.SetTitle(self.title+';'+self.xlabel+';'+self.filename+' '+self.ylabel+' / %0.2f'%(histo.GetBinWidth(1)))
        self.histo = copy.deepcopy(histo)
        file_handle.Close()
        # Overflow #
        self.histo.SetBinContent(1,self.histo.GetBinContent(0)+self.histo.GetBinContent(1))
        self.histo.SetBinContent(self.histo.GetNbinsX(),self.histo.GetBinContent(self.histo.GetNbinsX())+self.histo.GetBinContent(self.histo.GetNbinsX()+1))


    def PlotOnCanvas(self,pdf_name):
        tdrstyle.setTDRStyle() 
        canvas = TCanvas("c", "c", 600, 600)
        canvas.SetTopMargin(0.15)
        canvas.SetBottomMargin(0.15)
        canvas.SetRightMargin(0.05)
        canvas.SetLeftMargin(0.15)
        if self.title == '':
            canvas.SetTopMargin(0.05)

        self.histo.GetXaxis().SetTitleOffset(1.4)
        self.histo.GetXaxis().SetLabelSize(0.03)
        self.histo.GetXaxis().SetTitleSize(0.05)
        if len(self.xlabel) > 30:
            self.histo.GetXaxis().SetTitleSize(0.035)
            
        self.histo.GetYaxis().SetTitleOffset(1.5)
        self.histo.GetYaxis().SetLabelSize(0.03)
        self.histo.GetYaxis().SetTitleSize(0.05)
        if len(self.ylabel) > 30:
            self.histo.GetYaxis().SetTitleSize(0.035)

        self.histo.SetMinimum(0)
        self.histo.SetLineWidth(2)
        self.histo.SetTitle(self.title)
        if self.logx:
            canvas.SetLogx()
        if self.logy:
            canvas.SetLogy()
            self.histo.SetMinimum(1)

        self.histo.Draw(self.option)

        return canvas,self.filename

class Plot_TH2:
    def __init__(self,filepath,filename,tree,variablex,variabley,cut,name,binsx,binsy,xmin,xmax,ymin,ymax,title,xlabel,ylabel,weight=None,zlabel='',option='colz',normalizeX=False,normalizeY=False,logx=False,logy=False,logz=False):
        self.filepath = filepath
        self.filename = filename
        self.tree = tree
        self.variablex = variablex
        self.variabley = variabley
        self.weight = weight
        self.cut = cut
        self.name = name
        self.binsx = binsx
        self.binsy = binsy
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.zlabel = zlabel
        self.option = option
        self.normalizeX = normalizeX
        self.normalizeY = normalizeY
        self.logx = logx
        self.logy = logy
        self.logz = logz

    def MakeHisto(self):
        file_handle = TFile.Open(self.filepath)
        tree = file_handle.Get(self.tree)
        if not tree:
            logging.error("Could not open tree '%s' from file '%s'"%(self.tree,self.filename))
        first_arg = self.variabley+':'+self.variablex+'>>'+self.name+'('+str(self.binsx)+','+str(self.xmin)+','+str(self.xmax)+','+str(self.binsy)+','+str(self.ymin)+','+str(self.ymax)+')'
        if self.weight and self.weight != '' and self.cut != '':
            second_arg = self.weight + "* (" + self.cut + ")"
        elif self.weight and self.weight != '':
            second_arg = self.weight
        elif self.cut != '':
            second_arg = self.cut
        else:
            second_arg = ''
        tree.Draw(first_arg,second_arg,"goff "+self.option)    
        self.histo = copy.deepcopy(gROOT.FindObject(self.name))
        if self.normalizeX:
            for x in range(0,self.histo.GetNbinsX()+1):
                sum_y = 0
                for y in range(0,self.histo.GetNbinsY()+1):
                    sum_y += self.histo.GetBinContent(x,y)
                if sum_y == 0:
                    continue
                for y in range(0,self.histo.GetNbinsY()+1):
                    self.histo.SetBinContent(x,y,self.histo.GetBinContent(x,y)/sum_y)
            self.title += ' [Normalized]'

        if self.normalizeY:
            for y in range(0,self.histo.GetNbinsY()+1):
                sum_x = 0
                for x in range(0,self.histo.GetNbinsX()+1):
                    sum_x += self.histo.GetBinContent(x,y)
                if sum_x == 0:
                    continue
                for x in range(0,self.histo.GetNbinsX()+1):
                    self.histo.SetBinContent(x,y,self.histo.GetBinContent(x,y)/sum_x)
            self.title += ' [Normalized]'
        self.histo.SetTitle(self.title+';'+self.xlabel+';'+self.ylabel+';'+self.zlabel+' / %0.2f / %0.2f'%(self.histo.GetXaxis().GetBinWidth(1),self.histo.GetYaxis().GetBinWidth(1)))
        self.histo.SetMinimum(0)
        file_handle.Close()

    def PlotOnCanvas(self,pdf_name):
        tdrstyle.setTDRStyle() 
        canvas = TCanvas("c", "c", 600, 600)
        canvas.SetTopMargin(0.15)
        canvas.SetBottomMargin(0.13)
        canvas.SetRightMargin(0.12)
        canvas.SetLeftMargin(0.12)
        if self.title == '':
            canvas.SetTopMargin(0.08)
        if self.option == "colz":
            canvas.SetRightMargin(0.2)
            self.histo.SetContour(100)
            if self.logz:
                canvas.SetRightMargin(0.18)

        self.histo.GetXaxis().SetTitleOffset(1.1)
        self.histo.GetXaxis().SetLabelSize(0.03)
        self.histo.GetXaxis().SetTitleSize(0.05)
        if len(self.xlabel) > 30:
            self.histo.GetXaxis().SetTitleSize(0.025)
            self.histo.GetXaxis().SetTitleOffset(1.8)

        self.histo.GetYaxis().SetTitleOffset(1.2)
        self.histo.GetYaxis().SetLabelSize(0.03)
        self.histo.GetYaxis().SetTitleSize(0.05)
        if len(self.ylabel) > 30:
            self.histo.GetYaxis().SetTitleSize(0.025)
            self.histo.GetYaxis().SetTitleOffset(1.8)

        if "prof" in self.option:
            self.histo.GetXaxis().SetRangeUser(self.xmin,self.xmax)
            self.histo.GetYaxis().SetRangeUser(self.ymin,self.ymax)

        self.histo.GetZaxis().SetTitleOffset(1.2)
        self.histo.GetZaxis().SetLabelSize(0.03)
        self.histo.GetZaxis().SetTitleSize(0.05)

        self.histo.Draw(self.option)

        if self.logx:
            canvas.SetLogx()
        if self.logy:
            canvas.SetLogy()
        if self.logz:
            canvas.SetLogz()

        return canvas,self.filename

class Plot_Ratio_TH1:
    def __init__(self,filepath,filename,tree,variable1,variable2,cut,name,bins,xmin,xmax,title,xlabel,ylabel,legend1,legend2,weight=None,logx=False,logy=False,option='hist'):
        self.filepath = filepath
        self.filename = filename
        self.tree = tree
        self.variable1 = variable1
        self.variable2 = variable2
        self.cut = cut
        self.weight = weight
        self.name = name
        self.bins = bins
        self.xmin = xmin
        self.xmax = xmax
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend1 = legend1
        self.legend2 = legend2
        self.logx = logx
        self.logy = logy
        self.option = option

    def MakeHisto(self):
        instance1 = Plot_TH1(self.filepath,self.filename,self.tree,self.variable1,self.cut,self.name,self.bins,self.xmin,self.xmax,self.title,self.xlabel,self.ylabel,self.weight,self.logx,self.logy,self.option)
        instance2 = Plot_TH1(self.filepath,self.filename,self.tree,self.variable2,self.cut,self.name,self.bins,self.xmin,self.xmax,self.title,self.xlabel,self.ylabel,self.weight,self.logx,self.logy,self.option)
        instance1.MakeHisto()
        instance2.MakeHisto()

        self.histo1 = copy.deepcopy(instance1.histo)
        self.histo2 = copy.deepcopy(instance2.histo)
        self.histo1.Sumw2()
        self.histo2.Sumw2()

        ratio = self.histo1.Clone(self.name)
        ratio.Divide(self.histo2)

        self.ratio = copy.deepcopy(ratio)

    def PlotOnCanvas(self,pdf_name):
        tdrstyle.setTDRStyle() 
        canvas = TCanvas("c", "c", 600, 600)

        pad1 = TPad("pad1", "pad1", 0, 0.0, 1, 1.0)
        pad1.SetTopMargin(0.15)
        pad1.SetBottomMargin(0.32)
        pad1.SetRightMargin(0.05)
        pad1.SetLeftMargin(0.15)
        if self.title == '':
            pad1.SetTopMargin(0.05)
        pad1.SetGridx()
        pad1.Draw()
        pad1.cd()
        self.histo1.SetStats(0)
        self.histo1.Draw(self.option)
        self.histo2.Draw(self.option+" same")

        if self.logx:
            pad1.SetLogx()
        if self.logy:
            pad1.SetLogy()

        # Redraw axis to avoid clipping 0
        self.histo1.GetXaxis().SetLabelSize(0.)
        self.histo1.GetXaxis().SetTitle('')
        axis = TGaxis(-9,-2.8,-9,2.8,0,10000,50510,"")
        axis.SetLabelFont(43)
        axis.SetLabelSize(15)
        axis.Draw("same")

        pad2 = TPad("pad2", "pad2", 0, 0.0, 1, 0.3)
        pad2.SetTopMargin(0)
        pad2.SetBottomMargin(0.4)
        pad2.SetRightMargin(0.05)
        pad2.SetLeftMargin(0.15)
        pad2.SetGridx()
        pad2.Draw()
        pad2.cd() 

        if self.logx:
            pad2.SetLogx()

        self.ratio.SetLineColor(ROOT.kBlack)
        self.ratio.SetMinimum(0.5)
        self.ratio.SetMaximum(1.5)
        self.ratio.SetStats(0)
        self.ratio.SetMarkerStyle(21)
        self.ratio.Draw("ep")

        self.histo1.SetLineColor(ROOT.kBlue+1)
        self.histo1.SetLineWidth(2)
        max_y = max(self.histo1.GetMaximum(),self.histo2.GetMaximum())
        self.histo1.SetMaximum(max_y*1.1)

        self.histo1.GetXaxis().SetTitleOffset(1.5)
        self.histo1.GetXaxis().SetLabelSize(0.)
        self.histo1.GetXaxis().SetTitleSize(0.)

        self.histo1.GetYaxis().SetTitleOffset(1.5)
        self.histo1.GetYaxis().SetLabelSize(0.03)
        self.histo1.GetYaxis().SetTitleSize(0.05)
        self.histo1.GetYaxis().SetNdivisions(505)

        self.histo2.SetLineColor(ROOT.kRed)
        self.histo2.SetLineWidth(2)

        self.ratio.SetTitle("")

        self.ratio.GetXaxis().SetNdivisions(510)
        self.ratio.GetXaxis().SetTitleOffset(1.1)
        self.ratio.GetXaxis().SetLabelSize(0.10)
        self.ratio.GetXaxis().SetTitleSize(0.15)
        if len(self.xlabel) > 30:
            self.ratio.GetXaxis().SetTitleSize(0.13)
        if len(self.xlabel) > 60:
            self.ratio.GetXaxis().SetTitleSize(0.11)

        self.ratio.GetYaxis().SetTitle("Ratio")
        self.ratio.GetYaxis().SetNdivisions(505)
        self.ratio.GetYaxis().SetTitleOffset(0.5)
        self.ratio.GetYaxis().SetLabelSize(0.10)
        self.ratio.GetYaxis().SetTitleSize(0.15)
        if len(self.ylabel) > 30:
            self.ratio.GetYaxis().SetTitleSize(0.13)
        if len(self.ylabel) > 60:
            self.ratio.GetYaxis().SetTitleSize(0.11)

        # Legend #
        canvas.cd()
        if self.title == '':
            self.legend = TLegend(0.60,0.80,0.93,0.93)
        else:
            self.legend = TLegend(0.60,0.70,0.93,0.83)
        self.legend.SetTextSize(0.05)
        self.legend.SetBorderSize(0)
        self.legend.SetFillColor(0)
        self.legend.AddEntry(self.histo1,self.legend1,"l")
        self.legend.AddEntry(self.histo2,self.legend2,"l")
        self.legend.Draw()

        ROOT.SetOwnership(canvas, False)
        ROOT.SetOwnership(pad1, False)
        ROOT.SetOwnership(pad2, False)

        return canvas,self.filename

class Plot_Multi_TH1:
    def __init__(self,filepath,filename,tree,list_variable,weight,list_cut,list_legend,list_color,name,bins,xmin,xmax,title,xlabel,ylabel,option='hist',logx=False,logy=False,legend_pos=[0.5,0.5,0.9,0.85],stack=False,norm=False):
        self.filepath = filepath
        self.filename = filename
        self.tree = tree
        self.weight = weight
        self.name = name
        self.bins = bins
        self.xmin = xmin
        self.xmax = xmax
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend_pos = legend_pos
        self.logx = logx
        self.logy = logy
        self.option = option
        self.stack = stack
        self.norm = norm

        if not isinstance(list_cut,list):
            list_cut = [list_cut]
        if not isinstance(list_variable,list):
            list_variable = [list_variable]
        if not isinstance(list_legend,list):
            list_legend = [list_legend]


        if len(list_variable) == 1 and len(list_cut) > 1:
            logging.debug('\tOnly one variable but several cuts')
            self.list_variable = list_variable*len(list_cut)
            self.list_cut = list_cut
        elif len(list_variable) > 1 and len(list_cut) == 1:
            logging.debug('\tOnly one cut but several variables')
            self.list_cut = list_cut*len(list_variable)
            self.list_variable = list_variable
        elif len(list_variable) == 1 and len(list_cut) == 1:
            logging.warning('\tWhy do you even need to stack ?')
        elif len(list_variable) != len(list_cut):
            raise RuntimeError('Inconsistent number of variables and cuts')
            print (len(list_variable))
            print (len(list_cut))
        else:
            self.list_variable = list_variable
            self.list_cut = list_cut
        if len(list_legend) != max(len(list_variable),len(list_cut)):
            raise RuntimeError('Inconsistent number of legends compared to variables and cuts')
        else:
            self.list_legend = list_legend
        if len(list_color) != len(list_legend):
            raise RuntimeError('Inconsistent number of colors compared to legends')
        else:
            self.list_color = list_color

        for i in range(len(self.list_color)):
            if isinstance(self.list_color[i],str):
                self.list_color[i] = ROOT.TColor.GetColor(self.list_color[i])
        
    def MakeHisto(self):
        self.list_obj = []
        for i in range(0,len(self.list_variable)):
            instance = Plot_TH1(filepath = self.filepath,
                                filename = self.filename,
                                tree     = self.tree,
                                variable = self.list_variable[i],
                                weight   = self.weight,
                                cut      = self.list_cut[i],
                                name     = self.name,
                                bins     = self.bins,
                                xmin     = self.xmin,
                                xmax     = self.xmax,
                                title    = self.title,
                                xlabel   = self.xlabel,
                                ylabel   = self.ylabel,
                                logx     = self.logx,
                                logy     = self.logy)
            instance.MakeHisto()
            self.list_obj.append(copy.deepcopy(instance.histo))

    def PlotOnCanvas(self,pdf_name):
        tdrstyle.setTDRStyle() 

        # Canvas #
        canvas = TCanvas("c", "c", 600, 600)
        canvas.SetTopMargin(0.15)
        canvas.SetBottomMargin(0.15)
        canvas.SetRightMargin(0.05)
        canvas.SetLeftMargin(0.15)
        if self.title == '':
            canvas.SetTopMargin(0.05)

        if self.logx:
            canvas.SetLogx()
        if self.logy:
            canvas.SetLogy()
            self.list_obj[0].SetMinimum(10)

        # Norm #
        if self.norm:
            for obj in self.list_obj:
                if obj.Integral() != 0:
                    obj.Scale(1./obj.Integral())

        # Axes #
        maxY = max([h.GetMaximum() for h in self.list_obj])
        if self.logy:
            maxY *= 2
        else:
            maxY *= 1.1
            
        self.list_obj[0].SetMaximum(maxY)

        self.list_obj[0].GetXaxis().SetLabelSize(0.03)
        self.list_obj[0].GetXaxis().SetTitleSize(0.05)
        if len(self.xlabel) > 30:
            self.list_obj[0].GetXaxis().SetTitleSize(0.035)
        if len(self.xlabel) > 60:
            self.list_obj[0].GetXaxis().SetTitleSize(0.03)
        if "frac" in self.xlabel:
            self.list_obj[0].GetXaxis().SetTitleSize(0.03)
            self.list_obj[0].GetXaxis().SetTitleOffset(1.9)
        else:
            self.list_obj[0].GetXaxis().SetTitleOffset(1.6)
            
            
        self.list_obj[0].GetYaxis().SetTitleOffset(1.5)
        self.list_obj[0].GetYaxis().SetLabelSize(0.03)
        self.list_obj[0].GetYaxis().SetTitleSize(0.05)
        self.list_obj[0].GetYaxis().SetNdivisions(10)
        if len(self.ylabel) > 30:
            self.list_obj[0].GetYaxis().SetTitleSize(0.035)
        if len(self.ylabel) > 60:
            self.list_obj[0].GetYaxis().SetTitleSize(0.03)

        # Stacking #
        if self.stack:
            self.stack_hist = THStack("hs","") # Needs to be in self, otherwise destroyed at end of function
            opt = self.option
            for col,obj in zip(self.list_color,self.list_obj):
                obj.SetFillColor(col)
                obj.SetLineColor(col)
                self.stack_hist.Add(obj)
                obj.Draw(opt)
                if not "same" in opt :  
                    opt += " same"
            self.stack_hist.Draw(self.option+" same")
            maxY = self.stack_hist.GetMaximum()
            if self.logy:
                maxY *= 10
            else:
                maxY *= 1.1
            self.list_obj[0].SetMaximum(maxY)
        # Regular plotting
        else:
            opt = self.option
            for col,obj in zip(self.list_color,self.list_obj):
                obj.SetLineColor(col)
                obj.SetLineWidth(2)
                obj.Draw(opt)
                if not "same" in opt :  
                    opt += " same"
        # Legend #
        legend = TLegend(*self.legend_pos)
        for leg,obj in zip(self.list_legend,self.list_obj):
            legend.AddEntry(obj,leg,"f" if self.stack else "l")
        legend.SetBorderSize(0)
        legend.SetFillColor(0)
        legend.Draw()
        ROOT.SetOwnership(legend,0) # Otherwise goes out of scope and not printed

        return canvas,self.filename
            
class Plot_ROC:
    def __init__(self,tree,variable,title,selector,weight=None,cut=''):
        self.tree        = tree                         # Name of the tree to be taken from root file
        self.variable    = variable                     # Discriminative variable (typically between 0 and 1)
        self.weight_name = weight                       # Weight branch name
        self.weight      = None                         # Weight to be used in the ROC curve
        self.cut         = cut                          # Potential cut before applying the ROC
        self.title       = title                        # Title of the ROC (to be included in legend !)
       #self.xlabel      = xlabel                       # Title of x axis
       #self.ylabel      = ylabel                       # Title of y axis
        self.selector    = selector                     # Dict to give the target (=value) as a function of string inside filename (=key)
        self.output      = np.empty((0,1))              # Will contain the outputs (aka the variable from files)
        self.target      = np.empty((0,1))              # Will contin the targets

    def AddToROC(self,filename):
        # Check that correct target and records #
        valid_file = False
        for key,value in self.selector.items():
            if key in os.path.basename(filename): 
                target = value
                valid_file = True
        if not valid_file: return False# If file not to be taken into account
        # recover output #
        if self.weight_name and self.weight_name!='':
            out = root2array(filename,self.tree,branches=[self.variable+self.weight_name],selection=self.cut)
        else:
            out = root2array(filename,self.tree,branches=self.variable,selection=self.cut)
        try:
            out = rec2array(out) # If not a vector, need to remove dtype
        except:
            pass
        if out.ndim==1: 
            out = out.reshape(-1,1) # vector -> array
        if out.shape[1]>1: # contains [dicriminant,weight]
            weight = out[:,1]
            out = out[:,0]

        # Add to container #
        tar = np.ones((out.shape[0],1))*target
        self.output = np.concatenate((self.output,out),axis=0)
        self.target = np.concatenate((self.target,tar),axis=0)
        if self.weight_name and self.weight_name!='':
            self.weight = weight
        return True

    def ProcessROC(self):
        self.fpr, self.tpr, threshold = metrics.roc_curve(self.target, self.output, sample_weight=self.weight)
        self.roc_auc = metrics.auc(self.fpr, self.tpr)

class Plot_Multi_ROC:
    def __init__(self,tree,classes,labels,prob_branches,colors,title,selector,weight=None,cut=''):
        self.tree           = tree                                  # Name of the tree
        self.classes        = classes                               # eg [0,1,2], just numbering
        self.labels         = labels                                # Labels to display on plot
        self.colors         = colors                                # Pyplot colors for each element
        self.selector       = selector                              # Depending on string name, gives target
        self.prob_branches  = prob_branches                         # Branche contain the probabilities
        self.n_classes      = len(classes)                          # number of classes
        self.weight_name    = weight                                # Weight name
        self.weight         = np.empty((0,1))                       # Weight vector 
        self.title          = title                                 # title of plot
        self.prob_per_class = np.empty((0,self.n_classes))          # output of network
        self.scores         = np.empty((0,self.n_classes))          # Correct classes
        self.cut            = cut                                   # Potential cut
        self.lb             = LabelBinarizer()                      # eg ['A','B','C']-> labels [0,1,0]...
        self.lb.fit(self.classes)                                   # Carefull ! Alphabetic order !
        
        # classes in lb -> lb.classes_
        if self.classes != sorted(self.classes):
            raise RuntimeError('The classes need to be sorted alphabetically otherwise LabelBinarizer will give wrong results')

    def AddToROC(self,filename):
        """ 
        Info of the root file, the name of the probability branches and the target (0 or 1 or ...)
        """
        valid_file = False
        for key,value in self.selector.items():
            if key in os.path.basename(filename): 
                target = value
                valid_file = True
        if not valid_file: return False# If file not to be taken into account
 
        # Get the output prob #
        if self.weight_name and self.weight_name!='':
            probs = rec2array(root2array(filename,self.tree,branches=self.prob_branches+[self.weight_name],selection=self.cut))
            self.prob_per_class = np.concatenate((self.prob_per_class,probs[:,:-1]),axis=0)
            self.weight = np.concatenate((self.weight,probs[:,-1].reshape(-1,1)),axis=0)
        else:
            probs = rec2array(root2array(filename,self.tree,branches=self.prob_branches,selection=self.cut))
            self.prob_per_class = np.concatenate((self.prob_per_class,probs),axis=0)
            self.weight = None

        # Make the targets labelized #
        target_arr = self.lb.transform([target]*probs.shape[0])
        
        # eg target = 1 and classes = [0,1,2] => scores = [0,1,0],...
        self.scores = np.concatenate((self.scores,target_arr),axis=0)

        return True

    def ProcessROC(self):
        self.tpr = {}
        self.fpr = {}
        self.roc_auc = {}
        # Process class by class #
        for i,n in enumerate(self.lb.classes_):
            # https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html
            self.fpr[n], self.tpr[n], _ = metrics.roc_curve(self.scores[:, i], self.prob_per_class[:, i], sample_weight=self.weight)
            try:
                self.roc_auc[n] = metrics.auc(self.fpr[n], self.tpr[n]) 
            except ValueError: # Due to weights the fpr might not be increasing due float errors, tries to sort it   
                logging.warning("FPR not increasing for auc computation, might be weights ... will sort and try again")
                fpr = np.sort(self.fpr[n])
                self.roc_auc[n] = metrics.auc(fpr, self.tpr[n]) 
            
class ProcessYAML():
    def __init__(self, yaml_path, template):
        self.template    = template
        self.OUTPUT_YAML = os.path.join(yaml_path,'yaml')
        
        if not os.path.exists(self.OUTPUT_YAML):
            os.makedirs(self.OUTPUT_YAML)
        logging.debug('Instantiation of template %s'%template)

    def Particularize(self,filename=''):
        self.part_template = os.path.join(self.OUTPUT_YAML, self.template.replace('tpl-tempalte/','').replace('.yml.tpl','_') + filename + '.yml')
        
        rocs_dir = self.part_template.split('ROCMulti_')[0]
        if not os.path.exists(rocs_dir):
            os.makedirs(rocs_dir)
        
        with open(self.template) as tpl_handle:
            tpl = tpl_handle.read()

        with open(self.part_template, 'w') as out_yml:
            out_yml.write(tpl)
        logging.debug('\tParticularized template saved as %s'%self.part_template)
        
        self._loadYAML()
        logging.debug('\tLoaded the template saved as %s'%self.part_template)

    def _loadYAML(self): 
        with open(self.part_template, 'r') as stream:
            self.config = yaml.safe_load(stream) # Dict of dicts 
            # config is a dict : keys = names of hist
            #                    values = dict of parameters  
    def Override(self,changes):
        for name,conf in self.config.items(): # name is a string, conf is the dict of params
            # Loop over kwargs #
            for key,value in changes.items():
                # Check if the changes keys are in the config keys
                if not key in conf.keys():
                    logging.debug('Overriden key "%s" not found, will add it'%key)
                    self.config[name][key] = value
                    continue
                # If string, depends if empty or not
                if isinstance(self.config[name][key],str):
                    if len(self.config[name][key]) == 0:
                        self.config[name][key] = value
                    else: # check if contains format
                        form = [tup[1] for tup in string.Formatter().parse(self.config[name][key]) if tup[1] is not None]# List of format arguments
                        if len(form)==0: # no format, replace value
                            self.config[name][key] = value
                        else:   # format present, will replace corresponding keys
                            for f in form:
                                self.config[name][key] = self.config[name][key].format(value)
                else: # Not a string -> replace
                    self.config[name][key] = value

def LoopPlotOnCanvas(pdf_name,list_histo):
    #c = TCanvas('c','c')
    canvas = TCanvas('c','c',600,600)
    canvas.Print(pdf_name+'.pdf[')
    canvas.Close()

    for idx,inst in enumerate(list_histo,1):
        canvas,title = inst.PlotOnCanvas(pdf_name=pdf_name+'.pdf')
#        if isinstance(canvas,list):
#            for c in canvas:
#                c.Print(pdf_name+'.pdf')
#            if idx == len(list_histo):
#                canvas[-1].Print(pdf_name+'.pdf]')
#            for c in canvas:
#                c.Close()
        canvas.Print(pdf_name+'.pdf','Title:'+title)
        if idx == len(list_histo):
            canvas.Print(pdf_name+'.pdf]')
        canvas.Close()
    logging.info('Plots saved at %s'%(pdf_name+'.pdf'))

    # Save to root file #
    #f_root = TFile(pdf_name+".root", "recreate")
    #inst.histo.Write()

def MakeROCPlot(list_obj,name,title=None):
    # Generate figure #
    fig, ax = plt.subplots(1,figsize=(8,6))
    fig.subplots_adjust(left=0.12, bottom=0.12, right=0.95, top=0.95 if title is None else 0.90)

    # Loop over plot objects #
    for i,obj in enumerate(list_obj):
        ax.plot(obj.fpr, obj.tpr, label = '%s (AUC = %0.5f)' % (obj.title,obj.roc_auc))
        ax.grid(True)
    plt.legend(loc = 'lower right')
    plt.yscale('symlog',linthreshy=0.001)
    #plt.plot([0, 1], [0, 1],'k--')
    plt.xlim([0, 1])
    plt.ylim([0.001, 1])
    plt.xlabel("Misidentification rate")
    plt.ylabel("Correct identification rate")
    if title is not None:
        plt.suptitle(title)

    fig.savefig(name+'.png')
    logging.info('ROC curved saved as %s.png'%name)
    plt.close(fig)


def MakeMultiROCPlot(list_obj,name,title=None):
    #----- ROC -----#
    # Generate figure #
    fig, ax = plt.subplots(1,figsize=(8,6))
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.95, top=0.95 if title is None else 0.90)
    line_cycle = itertools.cycle(["-","--",":","-.",])
    # Loop over plot objects #
    for i,obj in enumerate(list_obj):
        n_obj = len(list(obj.tpr.keys()))
        linestyle = next(line_cycle)
        for key,lab,col in zip(obj.tpr.keys(),obj.labels,obj.colors):
            # Label #
            label = (obj.title+' '+lab)
            #label = lab
            label += ('\n AUC = %0.5f'%obj.roc_auc[key])
            # Plot #
            ax.plot(obj.fpr[key], obj.tpr[key], color=col, label=label, linestyle=linestyle)
            ax.grid(True)

    plt.legend(loc = 'lower right')#,prop={'family': 'monospace'})
    #plt.yscale('symlog',linthreshy=0.0001)
    plt.plot([0, 1], [0, 1],'k--')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.xlabel(r'Misidentification rate')
    plt.ylabel(r'Correct identification rate')

    fig.savefig(name+'_ROC.png')#,bbox_inches='tight')
    logging.info('ROC curved saved as %s_ROC.png'%name)
    plt.close(fig)

    #----- Confusion matrix -----#
    y_true = None
    y_pred = None
    sample_weight = None
    for i,obj in enumerate(list_obj):
        if y_pred is None and y_true is None:
            y_true = obj.scores
            y_pred = obj.prob_per_class
            sample_weight = obj.weight
        else:   
            y_true.append(obj.scores,axis=0)
            y_pred.append(obj.prob_per_class,axis=0)
            if sample_weight is not None:
                sample_weight.append(obj.weight,axis=0)
        
    # From multi class to one hot #
    y_true = y_true.argmax(axis=1)
    y_pred = y_pred.argmax(axis=1)
    if sample_weight is not None:
        sample_weight = sample_weight.reshape(-1)
    cm = confusion_matrix(y_true,y_pred,sample_weight=sample_weight).T
    accuracy = np.trace(cm) / float(np.sum(cm))                                                      
    misclass = 1 - accuracy

    # Normalize #
    # print( cm )
    cmx = cm/np.tile(cm.sum(axis=0),cm[0].shape[0]).reshape(*cm.shape)
    cmy = cm/np.repeat(cm.sum(axis=1),cm[0].shape[0]).reshape(*cm.shape)

    # Cmap #
    cmapx = plt.get_cmap('Blues')
    cmapy = plt.get_cmap('Reds')
    cmap  = plt.get_cmap('Greens')

    for cmi,cmap,label in zip([cm,cmx,cmy],[cmap,cmapx,cmapy],['plain','normedx','normedy']):
        # Plot CM #
        fig = plt.figure(figsize=(10, 9))
        plt.subplots_adjust(left=0.10, right=0.99, top=0.90, bottom=0.10)
        plt.imshow(cmi, interpolation='nearest', cmap=cmap)
        fig.suptitle('Confusion matrix')
        plt.colorbar()

        target_names = list_obj[0].lb.classes_

        tick_marks = np.arange(len(target_names))
        plt.xticks(tick_marks, target_names, rotation=45)
        plt.yticks(tick_marks, target_names)

        # Labels and numbers #
        thresh = cmi.max() / 1.5
        for i, j in itertools.product(range(cmi.shape[0]), range(cmi.shape[1])):
            plt.text(j, i, "{:0.2f}".format(cmi[i, j]),
                     horizontalalignment="center",
                     color="white" if cmi[i, j] > thresh else "black")

        xlabel = 'Predicted label'
        ylabel = 'True label'
        if label == 'normedx':
            xlabel += ' (normed)'
        if label == 'normedy':
            ylabel += ' (normed)'
        plt.ylabel(xlabel)
        plt.xlabel(ylabel)
        namefig = '%s_%s.png'%(name,label)
        fig.savefig(namefig)#,bbox_inches='tight')
        logging.info('Confusion matrix curved saved as %s'%namefig)
        plt.close(fig)
