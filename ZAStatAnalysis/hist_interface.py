# orignal author: Florain Bury
import os
import sys
import ROOT
import numpy as np

from array import array

ROOT.gInterpreter.ProcessLine('#include "header.h"')


class PythonInterface:
    @classmethod
    def getContent1D(self,h):
        assert isinstance(h,ROOT.TH1)
        e = [h.GetXaxis().GetBinUpEdge(0)]
        w = []
        s = []
        for i in range(1,h.GetNbinsX()+1):
            e.append(h.GetXaxis().GetBinUpEdge(i))
            w.append(h.GetBinContent(i))
            s.append(h.GetBinError(i))
        return np.array(e).round(5),np.array(w),np.array(s)

    @classmethod
    def getContent2D(self,h):
        assert isinstance(h,ROOT.TH2)
        xAxis = h.GetXaxis()
        yAxis = h.GetYaxis()
        Nx = xAxis.GetNbins() 
        Ny = yAxis.GetNbins()
        w = np.zeros((Nx,Ny))
        s = np.zeros((Nx,Ny))
        for ix in range(0,Nx):
            for iy in range(0,Ny):
                w[ix,iy] = h.GetBinContent(ix+1,iy+1)
                s[ix,iy] = h.GetBinError(ix+1,iy+1)
        e = [np.array([xAxis.GetBinLowEdge(i) for i in range(1,Nx+2)]).round(5),
             np.array([yAxis.GetBinLowEdge(i) for i in range(1,Ny+2)]).round(5)]
        return e,w,s

    @classmethod
    def fillHistogram1D(self,e,w,s,name=""):
        h = ROOT.TH1F(name,name,e.shape[0]-1,array('d',e))
        for i in range(w.shape[0]):
            h.SetBinContent(i+1,w[i])
            h.SetBinError(i+1,s[i])
        return h

    @classmethod
    def fillHistogram2D(self,e,w,s,name=""):
        assert len(e) == 2
        h = ROOT.TH2F(name,name,e[0].shape[0]-1,array('d',e[0]),e[1].shape[0]-1,array('d',e[1]))
        for ix in range(w.shape[0]):
            for iy in range(0,w.shape[1]):
                h.SetBinContent(ix+1,iy+1,w[ix,iy])
                h.SetBinError(ix+1,iy+1,s[ix,iy])

        return h


class CppInterface:
    @classmethod
    def getContent1D(self,h):
        assert isinstance(h,ROOT.TH1)
        Nx = h.GetNbinsX() 
        content = ROOT.getContentFromTH1(h)
        content.reshape((3*Nx+1,))
        arr = np.frombuffer(content, dtype=np.float32, count=3*Nx+1)
        w = arr[:Nx]
        s = arr[Nx:2*Nx]
        e = arr[2*Nx:].round(5)
        return e,w,s

    @classmethod
    def getContent2D(self,h):
        assert isinstance(h,ROOT.TH2)
        content = ROOT.getContentFromTH2(h)
        Nx = h.GetNbinsX()
        Ny = h.GetNbinsY()
        content.reshape((2*Nx*Ny+Nx+Ny+2,)) 
        arr = np.frombuffer(content, dtype=np.float32, count=2*Nx*Ny+Nx+Ny+2)
        w = arr[:Nx*Ny].reshape(Nx,Ny)
        s = arr[Nx*Ny:2*Nx*Ny].reshape(Nx,Ny)
        e = arr[2*Nx*Ny:]
        e = [e[:Nx+1],e[Nx+1:]]
        return e,w,s

    @classmethod
    def fillHistogram1D(self,e,w,s,name=""):
        e = e.astype(w.dtype)
        s = s.astype(w.dtype)
        return ROOT.fillTH1(e,w,s,w.shape[0],name)

    @classmethod
    def fillHistogram2D(self,e,w,s,name=""):
        e[0] = e[0].astype(w.dtype)
        e[1] = e[1].astype(w.dtype)
        s = s.astype(w.dtype)
        return ROOT.fillTH2(e[0],e[1],w.flatten(),s.flatten(),w.shape[0],w.shape[1],name)

