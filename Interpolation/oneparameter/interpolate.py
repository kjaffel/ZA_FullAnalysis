import os
import math
import ctypes
import logging
import ROOT

path = os.path.abspath(os.path.dirname(__file__))
ROOT.gInterpreter.ProcessLine(f'#include "{os.path.join(path,"th1fmorph.cc")}"')

class Interpolation:
    def __init__(self,p1,p2,p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        # self.p1_ = p1_
        # self.p2_ = p2_
        # self.p3_ = p3_
        if self.p3 > self.p2 or self.p3 < self.p1:
            #raise RuntimeError(f'Extrapolation dangerous : p1 = {self.p1}, p2 = {self.p2}, p3 = {self.p3}')
            print(f'Extrapolation dangerous : p1 = {self.p1}, p2 = {self.p2}, p3 = {self.p3}')
        self.w1 = 1-(self.p3-self.p1)/(self.p2-self.p1) 
       # self.w1_ = 1-(self.p3_-self.p1_)/(self.p2_-self.p1_)
        self.w2 = 1-(self.p2-self.p3)/(self.p2-self.p1)
       # self.w2_ = 1-(self.p2_-self.p3_)/(self.p2_-self.p1_)

    def _getNorm(self,norm1,norm2):
        return self.w1*norm1 + self.w2*norm2 
        
    def __call__(self,h1,h2,name):
        if h1.__class__.__name__.startswith('TH1') and h2.__class__.__name__.startswith('TH1'):
            # Compute the norm #
            norm = self._getNorm(h1.Integral(),h2.Integral())
            # Interpolate 1D #
            h3 = ROOT.th1fmorph(name,name, h1, h2, self.p1, self.p2, self.p3, norm) 
            # #print("h3", h3.Integral())           
            # # Unweight #  WHYYYYYYYYY??
            # h3_unwgt = h3.__class__(h3.GetName()+'_unweighted',
            #                         h3.GetTitle()+'_unweighted',
            #                         h3.GetNbinsX(),
            #                         h3.GetXaxis().GetBinLowEdge(1),
            #                         h3.GetXaxis().GetBinUpEdge(h3.GetNbinsX()))
            # count_sum = 0.
            # for i in range(1,h3.GetNbinsX()+1):
            #     count = int(round(h3.GetBinContent(i)))
            #     count_sum += count
            #     h3_unwgt.SetBinContent(i,count)
            # h3_unwgt.SetEntries(count_sum)
            # Return #
            return h3   
        else:
            raise RuntimeError(f"Could not find interpolation method for h1 of class {h1.__class__.__name__} and h2 of class {h2.__class__.__name__}")
