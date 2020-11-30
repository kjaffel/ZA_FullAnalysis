import os
import sys
import glob
import copy
import logging
import yaml
import string
import itertools
from array import array
import numpy as np
from sklearn.preprocessing import LabelBinarizer
from root_numpy import root2array, rec2array
from scipy import interp

from ROOT import TFile, TH1F, TH2F, TCanvas, gROOT, TGaxis, TPad, TLegend, TImage, THStack
import ROOT

from sklearn import metrics
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm

# ROOT STYLE #
import tdrstyle

# FORMULAS #
gROOT.LoadMacro("formulas.C")

 # PYPLOT STYLE #
SMALL_SIZE = 16
MEDIUM_SIZE = 20
BIGGER_SIZE = 22

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE) # fontsize of the figure title

#################################################################################################
##################################     Class definitions     ####################################
#################################################################################################

#####################################     Plot_TH1      #########################################
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
        if self.weight and self.weight != '':
            tree.Draw(self.variable+'>>'+self.name+'('+str(self.bins)+','+str(self.xmin)+','+str(self.xmax)+')',self.weight+'*('+self.cut+')',"goff")    
        else:
            tree.Draw(self.variable+'>>'+self.name+'('+str(self.bins)+','+str(self.xmin)+','+str(self.xmax)+')',self.cut,"goff")    
        histo = gROOT.FindObject(self.name)
        histo.SetTitle(self.title+' (%s sample)'%self.filename+';'+self.xlabel+';'+self.ylabel+' / %0.2f'%(histo.GetBinWidth(1)))
        self.histo = copy.deepcopy(histo)
        file_handle.Close()
        # Overflow #
        self.histo.SetBinContent(1,self.histo.GetBinContent(0)+self.histo.GetBinContent(1))
        self.histo.SetBinContent(self.histo.GetNbinsX(),self.histo.GetBinContent(self.histo.GetNbinsX())+self.histo.GetBinContent(self.histo.GetNbinsX()+1))


    def PlotOnCanvas(self,pdf_name):
        tdrstyle.setTDRStyle() 
        canvas = TCanvas("c1", "c1", 600, 600)
        self.histo.SetTitleOffset(1.6,'xyz')
        self.histo.SetMinimum(0)
        self.histo.SetLineWidth(2)
        self.histo.SetTitle(self.title)
        if self.logx:
            canvas.SetLogx()
        if self.logy:
            canvas.SetLogy()
            self.histo.SetMinimum(1)

        self.histo.Draw(self.option)

        canvas.Print(pdf_name,'Title:' + self.title + " (sample : %s)"%self.filename)
        canvas.Close()



####################################      Plot_TH2       ########################################
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
        file_handle = TFile.Open(self.filename)
        tree = file_handle.Get(self.tree)
        if not tree:
            logging.error("Could not open tree '%s' from file '%s'"%(self.tree,self.filename))
        if self.weight and self.weight != '':
            tree.Draw(self.variabley+':'+self.variablex+'>>'+self.name+'('+str(self.binsx)+','+str(self.xmin)+','+str(self.xmax)+','+str(self.binsy)+','+str(self.ymin)+','+str(self.ymax)+')',self.weight+'*('+self.cut+')',"goff "+self.option)    
        else:
            tree.Draw(self.variabley+':'+self.variablex+'>>'+self.name+'('+str(self.binsx)+','+str(self.xmin)+','+str(self.xmax)+','+str(self.binsy)+','+str(self.ymin)+','+str(self.ymax)+')',self.cut,"goff "+self.option)    
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
        self.histo.SetTitle(self.title+';'+self.xlabel+';'+self.ylabel+';'+self.zlabel)
        self.histo.SetMinimum(0)
        file_handle.Close()

    def PlotOnCanvas(self,pdf_name):
        tdrstyle.setTDRStyle() 
        canvas = TCanvas("c1", "c1", 600, 600)
        self.histo.SetTitleOffset(1.6,'xyz')
        if self.option == "colz":
            canvas.SetRightMargin(0.2)
            self.histo.SetContour(100)
        self.histo.Draw(self.option)

        if self.logx:
            canvas.SetLogx()
        if self.logy:
            canvas.SetLogy()
        if self.logz:
            canvas.SetLogz()

        canvas.Print(pdf_name,'Title:'+self.title)
        canvas.Close()

####################################    Plot_Ratio_TH1    ########################################
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
        instance1 = Plot_TH1(self.filepath,self.filename,self.tree,self.variable1,self.weight,self.cut,self.name,self.bins,self.xmin,self.xmax,self.title,self.xlabel,self.ylabel)
        instance2 = Plot_TH1(self.filepath,self.filename,self.tree,self.variable2,self.weight,self.cut,self.name,self.bins,self.xmin,self.xmax,self.title,self.xlabel,self.ylabel)
        instance1.MakeHisto()
        instance2.MakeHisto()

        self.histo1 = copy.deepcopy(instance1.histo)
        self.histo2 = copy.deepcopy(instance2.histo)

        ratio = self.histo1.Clone(self.name)
        ratio.Sumw2()
        ratio.Divide(self.histo2)

        self.ratio = copy.deepcopy(ratio)

    def PlotOnCanvas(self,pdf_name):
        #gROOT.SetBatch(False)
        tdrstyle.setTDRStyle() 
        canvas = TCanvas("c1", "c1", 600, 600)
        pad1 = TPad("pad1", "pad1", 0, 0.0, 1, 1.0)
        pad1.SetBottomMargin(0.32)
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

        legend = TLegend(0.65,0.7,0.85,0.83)
        legend.SetHeader("Legend","C")
        legend.AddEntry(self.histo1,self.legend1,"l")
        legend.AddEntry(self.histo2,self.legend2,"l")
        legend.Draw()

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
        self.histo1.GetYaxis().SetNdivisions(505)
        self.histo1.GetYaxis().SetTitleSize(20)
        self.histo1.GetYaxis().SetTitleFont(43)
        self.histo1.GetYaxis().SetTitleOffset(1.8)

        self.histo2.SetLineColor(ROOT.kRed)
        self.histo2.SetLineWidth(2)

        self.ratio.SetTitle("")

        self.ratio.GetYaxis().SetTitle("Ratio")
        self.ratio.GetYaxis().SetNdivisions(505)
        self.ratio.GetYaxis().SetTitleSize(20)
        self.ratio.GetYaxis().SetTitleFont(43)
        self.ratio.GetYaxis().SetTitleOffset(1.8)
        self.ratio.GetYaxis().SetLabelFont(43)
        self.ratio.GetYaxis().SetLabelSize(15)

        self.ratio.GetXaxis().SetNdivisions(510)
        self.ratio.GetXaxis().SetTitleSize(20)
        self.ratio.GetXaxis().SetTitleFont(43)
        self.ratio.GetXaxis().SetTitleOffset(4.)
        self.ratio.GetXaxis().SetLabelFont(43)
        self.ratio.GetXaxis().SetLabelSize(15)

        ROOT.SetOwnership(canvas, False)
        ROOT.SetOwnership(pad1, False)
        ROOT.SetOwnership(pad2, False)

        canvas.Print(pdf_name,'Title:'+self.title)
        canvas.Close()

####################################    Plot_Multi_TH1    #######################################
class Plot_Multi_TH1:
    def __init__(self,filepath,filename,tree,list_variable,weight,list_cut,list_legend,list_color,name,bins,xmin,xmax,title,xlabel,ylabel,option='hist',logx=False,logy=False,legend_pos=[0.5,0.5,0.9,0.85]):
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
            logging.critical('Inconsistent number of variables and cuts')
            sys.exit(1)
        else:
            self.list_variable = list_variable
            self.list_cut = list_cut
        if len(list_legend) != max(len(list_variable),len(list_cut)):
            logging.critical('Inconsistent number of legends compared to variables and cuts')
            sys.exit(1)
        else:
            self.list_legend = list_legend
        if len(list_color) != len(list_legend):
            logging.critical('Inconsistent number of colors compared to legends')
            sys.exit(1)
        else:
            self.list_color = list_color

        
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

        # Plot the histograms on over the other #
        c1 = TCanvas("c1", "c1", 600, 600)
        c1.SetLeftMargin(0.16)

        legend = TLegend(self.legend_pos[0],self.legend_pos[1],self.legend_pos[2],self.legend_pos[3])
        legend.SetHeader("Legend","C")
        maxY = 0
        for leg,obj in zip(self.list_legend,self.list_obj):
            legend.AddEntry(obj,leg,"l")
            obj_max = obj.GetMaximum()
            if obj_max>maxY:
                maxY = obj_max
        maxY *= 1.1
 
        for col,obj in zip(self.list_color,self.list_obj):
            obj.SetLineColor(col)
            obj.SetLineWidth(3)
            obj.SetMaximum(maxY)
            obj.SetTitleOffset(1.8,'x')
            obj.SetTitleOffset(2,'y')
            obj.Draw(self.option+" same")
            
        if self.logx:
            c1.SetLogx()
        if self.logy:
            c1.SetLogy()
            self.list_obj[0].SetMinimum(10)

        legend.Draw()
        c1.Print(pdf_name,'Title:'+self.list_obj[0].GetTitle()+' Same')
        c1.Close()
            
        # Plot the stacked histograms #
        self.stack_hist = THStack("hs","")

        for col,obj in zip(self.list_color,self.list_obj):
            obj.SetFillColor(col)
            self.stack_hist.Add(obj)

        c2 = TCanvas("c2", "c2", 600, 600)
        c2.SetLeftMargin(0.16)

        legend.Clear()
        legend.SetHeader("Legend","C")
        for leg,obj in zip(self.list_legend,self.list_obj):
            legend.AddEntry(obj,leg,"f")
            obj.SetMaximum(self.stack_hist.GetMaximum()*1.1)
            obj.SetTitleOffset(1.8,'x')
            obj.SetTitleOffset(2,'y')
            obj.Draw()

        self.stack_hist.Draw(self.option+" same")

        if self.logx:
            c2.SetLogx()
        if self.logy:
            c2.SetLogy()

        legend.Draw()

        c2.Print(pdf_name,'Title:'+self.list_obj[0].GetTitle()+' Stack')
        c2.Close()
        
####################################      Plot_ROC       ########################################
class Plot_ROC:
    def __init__(self,tree,variable,title,selector,xlabel,ylabel,weight=None,cut=''):
        self.tree = tree                                # Name of the tree to be taken from root file
        self.variable = variable                        # Discriminative variable (typically between 0 and 1)
        self.weight_name = weight                       # Weight to be used in the ROC curve 
        self.cut = cut                                  # Potential cut before applying the ROC
        self.title = title                              # Title of the ROC (to be included in legend !)
        self.xlabel = xlabel                            # TItle of x axis
        self.ylabel = ylabel                            # Title of y axis
        self.selector = selector                        # Dict to give the target (=value) as a function of string inside filename (=key)
        self.output = np.empty((0,1))                   # Will contain the outputs (aka the variable from files)
        self.target = np.empty((0,1))                   # Will contin the targets

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
        self.weight = weight if self.weight_name and self.weight_name!='' else None
        return True

    def ProcessROC(self):
        self.fpr, self.tpr, threshold = metrics.roc_curve(self.target, self.output, sample_weight=self.weight)
        self.roc_auc = metrics.auc(self.fpr, self.tpr)


def MakeROCPlot(list_obj,name,title):
    # Generate figure #
    fig, ax = plt.subplots(1,figsize=(8,6))

    # Loop over plot objects #
    for i,obj in enumerate(list_obj):
        ax.plot(obj.tpr, obj.fpr, label = '%s (AUC = %0.5f)' % (obj.title,obj.roc_auc))
        ax.grid(True)
        #plt.title('ROC : %s'%obj.title)
    plt.legend(loc = 'upper left')
    #plt.yscale('symlog',linthreshy=0.0001)
    plt.plot([0, 1], [0, 1],'k--')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.xlabel("Signal efficiency")
    plt.ylabel("Background efficiency")
    plt.suptitle(title)

    fig.savefig(name+'.png')
    logging.info('ROC curved saved as %s.png'%name)
    plt.close(fig)

#################################      Plot_Multi_ROC       #####################################
class Plot_Multi_ROC:
    def __init__(self,tree,classes,labels,prob_branches,colors,title,selector,weight=None,cut=''):
        self.tree = tree                                # Name of the tree
        self.classes = classes                          # eg [0,1,2], just numbering
        self.labels = labels                            # Labels to display on plot
        self.colors= colors                             # Pyplot colors for each element
        self.selector = selector                        # Depending on string name, gives target
        self.prob_branches = prob_branches              # Branches containign the probabilities
        self.n_classes = len(classes)                   # number of classes
        self.weight_name = weight                       # Weight name
        self.weight = np.empty((0,1))                   # Weight vector 
        self.title = title                              # title of plot
        self.prob_per_class = np.empty((0,self.n_classes))# output of network
        self.scores = np.empty((0,self.n_classes))      # Correct classes
        self.cut = cut                                  # Potential cut
        self.lb = LabelBinarizer()                      # eg ['A','B','C']-> labels [0,1,0]...
        self.lb.fit(self.classes)                       # Carefull ! Alphabetic order !
            # classes in lb -> lb.classes_

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
            self.fpr[n], self.tpr[n], _ = metrics.roc_curve(self.scores[:, i], self.prob_per_class[:, i], sample_weight=self.weight)
            try:
                self.roc_auc[n] = metrics.auc(self.fpr[n], self.tpr[n]) 
            except ValueError: # Due to weights the fpr might not be increasing due float errors, tries to sort it   
                logging.warning("FPR not increasing for auc computation, might be weights ... will sort and try again")
                fpr = np.sort(self.fpr[n])
                self.roc_auc[n] = metrics.auc(fpr, self.tpr[n]) 
            
        ## Micro-average #
        #self.fpr["micro"], self.tpr["micro"], _ = metrics.roc_curve(self.scores.ravel(), self.prob_per_class.ravel())
        #self.roc_auc["micro"] = metrics.auc(self.fpr["micro"], self.tpr["micro"]) 

        ## Macro-average #
        ## First aggregate all false positive rates
        #all_fpr = np.unique(np.concatenate([self.fpr[i] for i in self.lb.classes_]))
        ## Then interpolate all ROC curves at this points
        #mean_tpr = np.zeros_like(all_fpr)
        #for i in self.classes:
        #    mean_tpr += interp(all_fpr, self.fpr[i], self.tpr[i])
        ## Finally average it and compute AUC
        #mean_tpr /= self.n_classes

        #self.fpr["macro"] = all_fpr
        #self.tpr["macro"] = mean_tpr
        #self.roc_auc["macro"] = metrics.auc(self.fpr["macro"], self.tpr["macro"])

def MakeMultiROCPlot(list_obj,name):
    # Generate figure #
    fig, ax = plt.subplots(1,figsize=(10,8))
    line_cycle = itertools.cycle(["-","--",":","-.",])
    # Loop over plot objects #
    for i,obj in enumerate(list_obj):
        n_obj = len(list(obj.tpr.keys()))
        linestyle = next(line_cycle)
        for key,lab,col in zip(obj.tpr.keys(),obj.labels,obj.colors):
            # Label #
            #label = (obj.title+' '+lab)
            label = lab
            label += ('\n AUC = %0.5f'%obj.roc_auc[key])
            # Plot #
            ax.plot(obj.tpr[key], obj.fpr[key], color=col, label=label, linestyle=linestyle)
            ax.grid(True)

    plt.legend(loc = 'upper left')#,prop={'family': 'monospace'})
    #plt.yscale('symlog',linthreshy=0.0001)
    plt.plot([0, 1], [0, 1],'k--')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.xlabel(r'Correct identification')
    plt.ylabel(r'Misidentification')
    plt.suptitle(list_obj[0].title)

    fig.savefig(name+'.png')#,bbox_inches='tight')
    logging.info('ROC curved saved as %s.png'%name)
    plt.close(fig)


#####################################   ProcessYAML   ############################################
class ProcessYAML():
    def __init__(self,template):
        self.template = template
        self.OUTPUT_YAML = os.path.join(os.getcwd(),'YAML')
        if not os.path.exists(self.OUTPUT_YAML):
            os.makedirs(self.OUTPUT_YAML)
        logging.debug('Instantiation of template %s'%template)

    def Particularize(self,filename=''):
        self.part_template = os.path.join(self.OUTPUT_YAML,self.template.replace('.yml.tpl','_')+filename+'.yml')
        with open(self.template) as tpl_handle:
            tpl = tpl_handle.read()
        with open(self.part_template, 'w') as out_yml:
            out_yml.write(tpl)
        logging.debug('\tParticularized template saved as %s'%self.part_template)
        self._loadYAML()
        logging.debug('\tLoaded the template saved as %s'%self.part_template)

    def _loadYAML(self): 
        with open(self.part_template, 'r') as stream:
            self.config = yaml.load(stream) # Dict of dicts 
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

#################################################################################################
###############################      Function definitions      ################################## 
#################################################################################################
def LoopPlotOnCanvas(pdf_name,list_histo):
    for idx,inst in enumerate(list_histo,1):
        # inst is a class object -> inst.histo = TH1/TH2
        # Open file #
        if idx==1:
            c2 = TCanvas()
            c2.Print(pdf_name+'.pdf[')
            c2.Close()
        # Print each plot #
        inst.PlotOnCanvas(pdf_name=pdf_name+'.pdf')
        # Close file #
        if idx==len(list_histo):
            c2 = TCanvas()
            c2.Print(pdf_name+'.pdf') # Otherwise last plot does not have title
            c2.Print(pdf_name+'.pdf]')
            c2.Close()
    logging.info('Plots saved at %s'%(pdf_name+'.pdf'))

    # Save to root file #
    #f_root = TFile(pdf_name+".root", "recreate")
            #inst.histo.Write()
