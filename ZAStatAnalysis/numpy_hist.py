# orignal author : Florian Bury
import sys
from copy import copy,deepcopy
import numpy as np
import logging

from hist_interface import PythonInterface, CppInterface

class NumpyHist:
    """
        Helper class to perform perform transitions between ROOT histograms and their numpy contents
        This is required for the rebinning functions that are numpy related 
    """
    #################################################################################################
    #                                           __init__                                            #
    #################################################################################################
    def __init__(self,e,w,s2,name=None):
        """
            e = bin edges [N+1]
            w = bin content [N]
            s2 = quadratic bin error [N]
                where N is the number of bins
            name = name of the histogram [str] (to keep track from ROOT)
            We keep in the self only the quadratic error 
        """
        self._e  = e     # Bin edges
        self._w  = w     # Bin content
        self._s2 = s2  # Quadratic bin error 
        self._name = name

        if self._w.shape != self._s2.shape:
            raise ValueError(f'Histogram content has shape {self._w.shape}, but histogram error has shape {self._s2.shape}')
        if self.ndim == 1:
            if self._w.shape[0] != self._e.shape[0]-1:
                raise ValueError(f'Histogram content has {self._w.shape[0]} bins, but there are {self._e.shape[0]} bin edges ')
        elif self.ndim == 2:
            if self._w.shape[0] != self._e[0].shape[0]-1:
                raise ValueError(f'Histogram x-axis content has {self._w.shape[0]} bins, but there are {self._e[0].shape[0]} bin edges ')
            if self._w.shape[1] != self._e[1].shape[0]-1:
                raise ValueError(f'Histogram y-axis content has {self._w.shape[1]} bins, but there are {self._e[1].shape[0]} bin edges ')
        else:
            raise NotImplementedError(f'Dimension {self.ndim} has not been coded')

    #################################################################################################
    #                                         properties                                            #
    #################################################################################################
    @property 
    def e(self):
        """ Return the bin edges """
        return self._e

    @property 
    def w(self):
        """ Return the bin content """
        return self._w

    @property 
    def s(self):
        """ 
            Needed so the histogram addition is defined by quadratic addition 
            But this way the bin error can be access as an attribute
        """
        return np.sqrt(self._s2)

    @property 
    def s2(self):
        """ Return the quadratic bin error """
        return self._s2

    @property 
    def ndim(self):
        """ Returns the number of dimensions of the histogram """
        return self._w.ndim

    @property 
    def name(self):
        """ Returns the name of the histogram """
        return self._name

    @property 
    def dims(self):
        """ Returns the dimensions of the histograms axes """
        return self._w.shape

    @property 
    def integral(self):
        """ Returns the histogram integral """
        return self._w.sum()

    @property 
    def widths(self):
        """ Returns the bin widths in an array following the bin content """
        if self.ndim == 1:
            widths = self._e[1:]-self._e[:-1]
        elif self.ndim == 2:
            widths = np.dot((self._e[0][1:]-self._e[0][:-1]).reshape(-1,1),
                            (self._e[1][1:]-self._e[1][:-1]).reshape(1,-1))
        else:
            raise NotImplementedError
        if (widths <= 0.).any():
            #raise RuntimeError(f"Some bins have width <= 0., this might not be wanted : {widths}")
            logging.warning(f"Some bins have width <= 0., this might not be wanted : {widths}")
        return widths
            


    #################################################################################################
    #                                       ROOT conversions                                        #
    #################################################################################################

    @classmethod
    def getFromRoot(cls,h):
        """
            From TH1/TH2 extract : 
                e : edges including lower and upper 
                w : content (GetBinContent)
                s : errors  (GetBinError)
            return class object from (e,w,s)
            Internally use the C++ helpers to speed up the data flow
        """
        # Cannot use isinstance because TH2 inherits from TH1 #
        name = h.GetName()
        if h.__class__.__name__.startswith('TH1'):
            e,w,s = CppInterface.getContent1D(h)
        elif h.__class__.__name__.startswith('TH2'):
            e,w,s = CppInterface.getContent2D(h)
        else:
            raise NotImplementedError(f'Unknown histogram type {h.__class__.__name__}')
        return cls(e,w,s**2,name)

    def fillHistogram(self,name=None):
        """
            Inputs : 
            name : name to be used in the TH* instantiation (default = '')
            return : TH1/TH2 based on the dimension
            Internally use the C++ helpers to speed up the data flow
        """
        if name is None:
            if self._name is None:
                name = ""
            else:
                name = self._name
        if self.ndim == 1:
            return CppInterface.fillHistogram1D(self.e,self.w,self.s,name)
        elif self.ndim == 2:
            return CppInterface.fillHistogram2D(self.e,self.w,self.s,name)
        else:
            raise NotImplementedError(f'Dimension {self.ndim} has not been coded')


    #################################################################################################
    #                                      Safety checks                                            #
    #################################################################################################
    def compareAxes(self,other):
        """
            Compare the axes of the self with other, that can be 
            - a NumpyHist object
            - a numpy array
            Raises an error in case something looks different 
        """
        e1 = self._e
        # Get e2 #
        if isinstance(other,np.ndarray): 
            # Other is directly the axes #
            e2 = other
        elif isinstance(other,NumpyHist):
            # Other is another numpy hist #
            e2 = other.e
        else:
            raise NotImplementedError(f'Comparison object {type(other)} not understood')

        # Compare per dimension #
        if self.ndim == 1:
            if e1.shape[0] != e2.shape[0]:
                raise RuntimeError(f'Axes have different lenghts in the two histograms : {e1.shape[0]-1} versus {e2.shape[0]-1}')
            if not np.isclose(e1,e2).all():
                raise RuntimeError(f'Different axes in the two histograms : {e1} versus {e2}')
        elif self.ndim == 2:
            if e1[0].shape[0] != e2[0].shape[0]:
                raise RuntimeError(f'X axes have different lenghts in the two histograms : {e1[0].shape[0]}-1 versus {e2[0].shape[0]-1}')
            if not np.isclose(e1[0],e2[0]).all():
                raise RuntimeError(f'Different x axes in two histograms : {e1[0]} versus {e2[0]}')
            if e1[1].shape[0] != e2[1].shape[0]:
                raise RuntimeError(f'Y axes have different lenghts in the two histograms : {e1[1].shape[0]-1} versus {e2[1].shape[0]-1}')
            if not np.isclose(e1[1],e2[1]).all():
                raise RuntimeError(f'Different x axes in two histograms : {e1[1]} versus {e2[1]}')
        else:
            raise NotImplementedError(f'Dimension {self.ndim} has not been coded')

    @staticmethod
    def compareRebinAxes(ax1,ax2):
        """
            Compares two arrays of axis edges, makes sure ax2 is contained in ax1
            Safety check for the rebinning 
        """
        if ax1.dtype != ax2.dtype:
            ax2 = ax2.astype(ax1.dtype)
        if ax1[0] != ax2[0]:
            raise RuntimeError("Axis first edge not matching : {} != {}".format(ax1[0],ax2[0]))
        if ax1[-1] != ax2[-1]:
            raise RuntimeError("Axis last edge not matching : {} != {}".format(ax1[-1],ax2[-1]))
        if np.any(ax1[:-1] > ax1[1:]):
            raise RuntimeError("Axis old edges not increasing : ["+",".join([str(ax1[i]) for i in range(ax1.shape[0])])+"]")
        if np.any(ax2[:-1] > ax2[1:]):
            raise RuntimeError("Axis new edges not increasing : ["+",".join([str(ax2[i]) for i in range(ax2.shape[0])])+"]")
        if not np.isin(ax2,ax1).all():
            wrong_edges = ax2[~np.isin(ax2,ax1)]
            raise RuntimeError("New X axis edges not contained in initial ones : ["+",".join([str(wrong_edges[i]) for i in range(wrong_edges.shape[0])])+"]")


    #################################################################################################
    #                                      Magic methods                                            #
    #################################################################################################
    def __add__(self,other):
        """
            Implements the addition with another NumpyHist
            First, check the axes, then add the content linearly, and errors quadratically
            Then returns the new results
        """
        # Check axis first #
        self.compareAxes(other)
        # Return added content #
        return NumpyHist(self._e,
                         self._w + other._w,
                         self._s2 + other._s2,
                         self._name)

    def add(self,other):
        """
            Implements the addition with another NumpyHist
            But in this case add the content to the self
        """
        # Check axis first #
        self.compareAxes(other)
        # Return added content #
        self._w += other._w
        self._s2 += other._s2

    def __copy__(self):
        return NumpyHist(deepcopy(self._e),
                         deepcopy(self._w),
                         deepcopy(self._s2),
                         self._name)

    def __deepcopy__(self):
        return self.__copy__()

    #################################################################################################
    #                                      Helper methods                                           #
    #################################################################################################
    @staticmethod
    def _checkTotal(arr1,arr2,name):
        """
            Check two arrays to make sure their integral did not change too much
        """
        if arr1.sum() != 0. and abs(arr1.sum()-arr2.sum())/arr1.sum() > 1e-4:
            logging.warning(f'Difference in {name} above threshold : original {arr1.sum():.5e}, changed {arr2.sum():.5e} -> relative difference = {abs(arr1.sum()-arr2.sum())/arr1.sum():.3e}')

    def rebin(self,ne):
        """
            Rebin based on new bin edges ne
            Checks are made to be sure that the new axis edges match some of the current ones
        """
        # 1D method #
        if self.ndim == 1:
            # Make sure the rebin can work #
            self.compareRebinAxes(self._e,ne)
            # Get indices #
            x = (self._e[1:]+self._e[:-1])/2
            idx = np.digitize(x,ne) - 1
            # Perform aggregation #
            nw = np.zeros(ne.shape[0]-1)
            ns2 = np.zeros(ne.shape[0]-1)
            for i in range(nw.shape[0]):
                nw[i] += self._w[idx == i].sum()
                ns2[i] += (self._s2[idx == i]).sum()
        # 2D method #
        elif self.ndim == 2:
            # Make sure the rebin can work #
            self.compareRebinAxes(self._e[0],ne[0])
            self.compareRebinAxes(self._e[1],ne[1])
            # Get indices #
            x = (self._e[0][1:]+self._e[0][:-1])/2
            y = (self._e[1][1:]+self._e[1][:-1])/2
            idx = np.digitize(x,ne[0]) - 1
            idy = np.digitize(y,ne[1]) - 1
            # Perform aggregation #
            nw = np.zeros((ne[0].shape[0]-1,ne[1].shape[0]-1))
            ns2 = np.zeros((ne[0].shape[0]-1,ne[1].shape[0]-1))
            for ix in range(0,nw.shape[0]):
                for iy in range(0,nw.shape[1]):
                    nw[ix,iy] += self._w[np.ix_(idx==ix,idy==iy)].sum()
                    ns2[ix,iy] += self._s2[np.ix_(idx==ix,idy==iy)].sum()
        else:
            raise NotImplementedError

        # Safety checks #
        self._checkTotal(self._w,nw,'content')
        self._checkTotal(self._s2,ns2,'quadratic error')
        # Return #
        return NumpyHist(ne,nw,ns2,self._name)

    def projectionX(self):
        """
            From a 2D histogram, return the projection in the X axis 
        """
        if self.ndim != 2:
            raise NotImplementedError(f'Projection in dimension {self.ndim} is not implemented')
        e = self._e[0]
        w = self._w.sum(axis=1)
        s2 = self._s2.sum(axis=1)
        return NumpyHist(e,w,s2,self._name)

    def projectionY(self):
        """
            From a 2D histogram, return the projection in the Y axis 
        """
        if self.ndim != 2:
            raise NotImplementedError(f'Projection in dimension {self.ndim} is not implemented')
        e = self._e[1]
        w = self._w.sum(axis=0)
        s2 = self._s2.sum(axis=0)
        return NumpyHist(e,w,s2,self._name)

    def divideByBinWidth(self):
        """
            Divide the bin content and squared errors by the bin width
            TODO : not sure about the bin error
        """
        self._w  = np.divide(self._w,self.widths)
        self._s2 = np.divide(self._s2,self.widths)

    def setUnitaryBinWidth(self):
        """
            Make the bin width to unitary    
        """
        if self.ndim == 1:
            self._e = np.arange(self._e.shape[0]) 
        elif self.ndim == 2:
            self._e = [np.arange(self._e[0].shape[0]),np.arange(self._e[1].shape[0])]
        else:
            raise NotImplementedError
            
    def split(self,x_edges=None,y_edges=None,axis='x'):
        """
            Split a 2D histogram into a series of smaller 2D histograms 
            x_edges : edges on x axis along which to split
            y_edges : edges on y axis along which to split
                If any is None, no splitting along this axis
            axis : 'x'|'y' decides in which order to return the list of new 2D hists
        """
        if self.ndim == 1:
            if axis != 'x': 
                raise ValueError('Splittign a 1D histogram can only work in x direction')
            if x_edges is None:
                x_edges = np.array([self._e[0][0],self._e[0][-1]])
            else:
                if not isinstance(x_edges,np.ndarray):
                    x_edges = np.array(x_edges)
                assert x_edges.ndim == 1
            # Get centers of bins #
            centers = (self._e[1:] + self._e[:-1]) / 2
            # Get where centers go in new binning #
            idx = np.digitize(centers,x_edges) - 1 
            # Get limits of the new bins #
            lims = np.where(idx[:-1] != idx[1:])[0] + 1 
            # Split #
            ws  = np.split(self._w,lims,axis=0)
            s2s = np.split(self._s2,lims,axis=0)
            nes = self._splitEdges(self._e,lims)
            nphs = [NumpyHist(nes[i],ws[i],s2s[i]) for i in range(len(ws))]
        elif self.ndim == 2:
            if axis not in ['x','y']:
                raise RuntimeError(f'Unknow axis {axis}')
            # Check the axes :
            if x_edges is None:
                x_edges = np.array([self._e[0][0],self._e[0][-1]])
            else:
                if not isinstance(x_edges,np.ndarray):
                    x_edges = np.array(x_edges)
                assert x_edges.ndim == 1
                self.compareRebinAxes(self._e[0],x_edges)
            if y_edges is None:
                y_edges = np.array([self._e[1][0],self._e[1][-1]])
            else:
                if not isinstance(y_edges,np.ndarray):
                    y_edges = np.array(y_edges)
                assert y_edges.ndim == 1
                self.compareRebinAxes(self._e[1],y_edges)
            # Get centers of bins #
            x_centers = (self._e[0][1:] + self._e[0][:-1]) / 2
            y_centers = (self._e[1][1:] + self._e[1][:-1]) / 2

            # Get where centers go in new binning #
            idx_x = np.digitize(x_centers,x_edges) - 1 
            idx_y = np.digitize(y_centers,y_edges) - 1

            # Get limits of the new bins #
            x_lims = np.where(idx_x[:-1] != idx_x[1:])[0] + 1 
            y_lims = np.where(idx_y[:-1] != idx_y[1:])[0] + 1
        
            # Splitting #
            ws  = self._splitArray(self._w,x_lims,y_lims,axis)
            s2s = self._splitArray(self._s2,x_lims,y_lims,axis)
                # list of split, x is major split, y is minor

            # Make edges #
            nx_edges = self._splitEdges(self._e[0],x_lims)
            ny_edges = self._splitEdges(self._e[1],y_lims)

            # Make list of NumpyHist #
            if axis == 'x':
                nphs = [NumpyHist([ex,ey],ws[ix][iy],s2s[ix][iy],self._name)
                            for ix,ex in enumerate(nx_edges)
                            for iy,ey in enumerate(ny_edges)]
            if axis == 'y':
                nphs = [NumpyHist([ex,ey],ws[iy][ix],s2s[iy][ix],self._name)
                            for iy,ey in enumerate(ny_edges)
                            for ix,ex in enumerate(nx_edges)]

        else:
            raise NotImplementedError(f'Split in dimension {self.ndim} is not implemented')

        return nphs

    @staticmethod
    def _splitArray(arr,x_lims,y_lims,axis):
        """
            Helper to split an array based on the limits in x and y axes
            axis determines what order to return the list
        """
        if axis == 'x':
            return [[splitxy for splitxy in np.split(splitx,y_lims,axis=1)]
                        for splitx in np.split(arr,x_lims,axis=0)]
        if axis == 'y':
            return [[splityx for splityx in np.split(splity,x_lims,axis=0)]
                        for splity in np.split(arr,y_lims,axis=1)]

    @staticmethod
    def _splitEdges(e,lims):
        """
            Helper to split an edge array based on the limits on the axis
        """
        ne = np.split(e,lims)
        for i in range(len(ne)-1):
            ne[i] = np.append(ne[i],ne[i+1][0]) 
        return ne 
            
    @classmethod
    def concatenate(cls,list_nphs,axis=0):
        """
            Take a list of NumpyHist and concatenate them based on the provided axis number
            Returns a single NumpyHist
        """
        if not isinstance(list_nphs,list):
            raise RuntimeError(f'First argument needs to be a list of NumpyHists, is type {type(list_nphs)}')
        ndims = np.array([nph.ndim for nph in list_nphs])
        if not (ndims == ndims[0]).all():
            raise RuntimeError(f'Not all dimensions match : {ndims}')
        ndim = ndims[0]

        w = None
        s2 = None
        e = None
        for nph in list_nphs:
            if w is None:
                w = nph._w
                s2 = nph._s2
                e = nph._e
            else:
                w = np.concatenate((w,nph._w),axis=axis)
                s2 = np.concatenate((s2,nph._s2),axis=axis)
                if ndim == 1:
                    e = np.append(e,nph._e[1:] - nph._e[0] + e[-1])
                elif ndim == 2:
                    if axis == 0:
                        if not np.array_equal(e[1],nph._e[1]):
                            raise ValueError(f'Y-axis edges do not match : {e[1]}, {nph._e[1]}')
                        e[0] = np.append(e[0],nph._e[0][1:] - nph._e[0][0] + e[0][-1])
                    elif axis == 1:
                        if not np.array_equal(e[0],nph._e[0]):
                            raise ValueError(f'X-axis edges do not match : {e[0]}, {nph._e[0]}')
                        e[1] = np.append(e[1],nph._e[1][1:] - nph._e[1][0] + e[1][-1])
                    else:
                        raise ValueError(f'2D histogram cannot be concatenated on axis {axis}')
                        
                else:
                    raise NotImplementedError

        return cls(e,w,s2,list_nphs[0].name)


if __name__ == '__main__':
    from IPython import embed
    embed()
