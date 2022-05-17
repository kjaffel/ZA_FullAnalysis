# orignal author : Florian Bury
import sys
import scipy
import logging
import ROOT
import numpy as np
import scipy.interpolate

from scipy.stats import chi2, norm
from copy import copy,deepcopy
from array import array

from numpy_hist import NumpyHist

"""
    How to use the rebinning classes

    The rebinning classes takes one or a list of histograms and a certain number of parameters 
    -> Based on these the new sets of bin edges is computed (`self.ne`)

    The class object, which now contains the new bin edges can be applied on any ROOT histogram 
    to return a rebinned histogram

    Available algorithms : 
    - Boundary  : New axis edges are provided directly as parameters (simplest method)
        example : 
            ```
                obj = Boundary([0,5,20,100])
                new_h = obj(h) 
            ```
            Provided the new bin edges match some of the ones from `h` 
    - Quantile  : From the CDF of the provided histogram(s), computes the bin edges
        to match the quantiles provided by the user 
        example:
            ```
                obj = Quantile(h_sig,[0.,0.5,1.])
                new_h = obj(h) 
            ```
            The bin edges are computed such that h_sig has 2 bins with 50% of h_sig content each
            Then any histogram h can be called with the class to rebin them with such edges
            
    - Threshold : Iterative method that starts from the right of the histogram and starts aggregating bins
                until a certain threshold condition is obtained. The list of thresholds are provided by the user.
                Additional constraints are : 
                    - one can pass additional histograms (extra) that are required to have at least one event in the bin
                    - one can pass a minimum relative uncertainty threshold (rsut) to avoid stats fluctuations to be below 
                        the thresholds
                This class performs a threshold scan, which means the thresholds are adapted to the total integral, starting 
                aggressively and lowers them until the required number or bins is obtained (which is the length of the threshold list)
        example:
            ```
                obj = Threshold(h_sig,[1,4,9,16,25],[h_sup1,h_sup2],rsut=0.075)
                new_h = obj(h) 
            ```
            The bin edges are computed such that :
                - the threshold follow a quadratic increase in h_sig content 
                - in this case, there should be 5 bins (number of thresholds)
                - h_sup1 and h_sup2 have at least one entry in each bin [optionnal]
                - the stats uncertainty above 0.075 [optionnal]
            Then any histogram h can be called with the class to rebin them with such edges
            
    - Threshold2 : Iterative method that starts from the left of the histogram and starts aggregating bins
                until a certain threshold condition is obtained. 
                This is an upgrade of the Threshold class which had potentially large variations of backgrounds 
                because based solely on signals. And the extra contributions could have fluctuations that impacted the binning heavily
    
                To counteract that, here the algorithm takes all the processes into account and computes the sum over them.
                The thresholds are still provided by the user but are now inverted (eg, quadratic means quadraticly decreasing bins).
                The algorithm also takes into account that the total stats variations must be above the threshold.
                When the bins are aggregated, if for a certain process the bin is empty, the error is taken from the fallback vector.
                Fallback vector is a vector with the same length as the list of histograms/processes, it is recommended that :
                    - signal samples have a np.inf fallback (to force at least one signal event in the bin)
                    - main background events have sumw2/sumw (even if empty, they should have an impact)
                    - non main backgrounds have 0 (we don't really care is they are not in every bin)

                This class performs a threshold scan, which means the thresholds are adapted to the total integral, starting 
                aggressively and lowers them until the required number or bins is obtained (which is the length of the threshold list)

        example:
            ```
                obj = Threshold2([<list-of-histogram>],[1,4,9,16,25],[<list of fallbacks>])
                new_h = obj(h) 
            ```
            The bin edges are computed such that :
                - the threshold follow a quadratic decrease in the total content (including signal) 
                - in this case, there should be 5 bins (number of thresholds)
                - fallbacks must have same length as list of histograms
            Then any histogram h can be called with the class to rebin them with such edges

    The same algorithm also work in 2D versions (Boundary2D, Quantile2D, Threshold2D)
    in exactly the same way except the parameters have to be provided for both the x and y axes
    These algorithms work independently on the x and y axis by projections

    The Linearize2D method allows to turn a 2D histogram into a linearized 1D one
    example : 
        ```
            # h is a 2D histogram 
            objx = Linearize2D('x')
            hx = Linearize2D(h)
        ```
        In this case, we ask that the major axis is x, and the minor will be y (opposite can be done with 'y' instead)
        This means that the 1D histogram hx will consist in large x bins that contain the y bins

        In case come rebinning has to be done on the major axis first, one can do 
        ```
            objx = Linearize2D('x')
            objx.nemajor = [0,5,100]
            hx = Linearize2D(h)
        ```
        In which case the x major bins will be first rebinned into the two bins [0,5,100], the the histogram linearized
        In case the rebinning also has to be done in the minor axis, one can also add 
        ```
            objx.neminor = [[0,0.5,1],[0,0.3,1.]]
        ```
        Note that since we have 2 major bins, we need to provide a list of 2 minor binnings.
        In general the neminor length must be the same as the number of bins of the major axis
        This means the minor binning in each major bin can be optimized independently

    To perform something more automatic, one cane use the LinearizeSplit, which applies the above mentionned 
    1D rebinning for both major and minor (if requested) , before linearizing.
    So the major and minor classes need to be provided with their associated parameters
        example : we want a quantile binning of the y axis, and a threshold2 binning of the x axis in each major bin of y
        ```
            obj = LinearizeSplit(h_sig,
                                 major        = 'y',
                                 major_class  = 'Quantile',
                                 major_params = [[0.,0.4,0.8,1.]],
                                 minor_class  = 'Threshold2',
                                 minor_params = [list_h,[1,4,9,16,25],fallbacks])
            # h2D = 2D histogram
            h_lin = LinearizeSplit(h2D)
        ```
        In this case we will have a linearized histogram in which :
            - there are 3 y bins with edges based on h_sig quantiles
            - for each of the 3 major y bins, the content in x axis is rebinned by the threshold2 algo
                with 5 bins and the processes fallbacks
        => 3 x 5 = 15 bins
        Note that in this particular example, we have to provide the additional histograms as parameters
        The major and minor classes are optional, but keep in mind if no rebinning is employed, the number 
        of bins in linearized histogram can be quite large.
"""

class Rebin:
    """
        Base rebin method
        includes common methods to rebin, extract and fill histograms
    """
    def __call__(self,h):
        """
            input : initial histogram TH1
            return : rebinned TH1
        """
        nph = NumpyHist.getFromRoot(h)
        if np.isnan(nph.w).any():
            logging.warning('Warning : nan found in hist %s'%h.GetName())
            return None
        if not hasattr(self,'ne'):
            raise RuntimeError('New bin edges have not been computed, is the rebin_method() not implemented ?')

        return nph.rebin(self.ne).fillHistogram(h.GetName()+'rebin')

    @staticmethod
    def _processHist(h):
        """
            Input : h, can be 
                - ROOT.TH1X
                - NumpyHist already
                - list of ROOT.TH1X or NumpyHist
            return : NumpyHist object
        """
        nph = None
        if isinstance(h,list):
            # List, need to add them #
            for i,hi in enumerate(h):
                if isinstance(hi,ROOT.TH1):
                    nphi = NumpyHist.getFromRoot(hi)
                elif isinstance(hi,NumpyHist):
                    nphi = hi
                else:
                    raise ValueError(f'Histogram type {type(h)} of entry {i} not understood')
                if nph is None:
                    nph = copy(nphi)
                else:
                    nph.add(nphi)
        elif isinstance(h,ROOT.TH1):
            nph = NumpyHist.getFromRoot(h)
        elif isinstance(h,NumpyHist):
            nph = h
        else:
            raise ValueError(f'Histogram type {type(h)} not understood')

        if np.isnan(nph.w).any():
            raise RuntimeError(f'Warning : nan found in hist content {h.GetName()}')
        if np.isnan(nph.s).any():
            raise RuntimeError(f'Warning : nan found in hist error {h.GetName()}')

        return nph 



class Quantile(Rebin):
    """
        Applies quantile binning
        -> provide quantile boundaries and bin histogram accordingly
        list of quantile values need to be optimized
    """
    def __init__(self,h,q):
        """
            h : either TH1 or list of TH1
            q : quantiles list [0 , ... 1]
        """
        # Process and check quantiles #
        if not isinstance(q,np.ndarray):
            q = np.array(q)
        if q[0] != 0. or q[-1] != 1.:
            raise RuntimeError("Invalid quantiles boundaries ["+",".join([str(q[i]) for i in range(q.shape[0])])+"]")
        if np.any(q[:-1] > q[1:]):
            raise RuntimeError("Quantile edges not increasing ["+",".join([str(q[i]) for i in range(q.shape[0])])+"]")
        # Process histograms #
        nph = self._processHist(h)
        nbins = q.shape[0] - 1 
        if nph.w[nph.w>0].shape[0] >= q.shape[0]:
            self.ne = nph.e[0]
            if nph.w[0] > q[1] * nph.w.sum(): # First bin has already more than first quantile bin
                logging.warning(f'First bin content higher than first quantile : {nph.w[0]} > {q[1] * nph.w.sum()} [quantile = {q[1]}], will use its edge and rescale the quantiles for the rest of the histogram')
                # Add first bin as new edge #
                self.ne = np.r_[self.ne,nph.e[1]]
                # Remove the first bin for the rest #
                nph = nph.split(np.r_[nph.e[0],nph.e[1],nph.e[-1]])[1]
                # Rescale the quantiles #
                q = np.r_[0,np.cumsum(np.diff(q[1:])*1/(1-q[1]))]

            x = (nph.e[:-1]+nph.e[1:])/2
            nx = self.rebin_method(x[nph.w>0],nph.w[nph.w>0],q)
            idx = np.digitize(nx, nph.e) - 1
            self.ne = np.r_[self.ne,nph.e[idx],nph.e[-1]]
            self.ne,counts = np.unique(self.ne,return_counts=True)
            if (counts>1).any():
                logging.warning(f'There were repetitions in the new binning : {ne}')
        elif nph.w[w>0].shape[0] == 0:   
            self.ne = np.array([e[0],e[-1]])
        else:
            idx = np.digitize(x[nph.w>0], e) - 1
            self.ne = np.r_[nph.e[0], nph.e[idx], nph.e[-1]]
        # Make sure there are no zero-width bins #
        if self.ne.shape[0] != nbins + 1:
            raise RuntimeError(f'Error in quantile, hist will have {self.ne.shape[0]-1} bins, but you asked for {nbins} : bins = {self.ne}')
            # Because can be a problem for combination
        logging.debug(f'Found binning : {self.ne}')

    @staticmethod
    def rebin_method(x, w, q):
        """
        x: bin centers
        w: bin heights (bin content)
        q: quantiles
        """
        assert x.shape == w.shape
        assert x.ndim == 1
        assert q.ndim == 1
        assert np.all((0 <= q) & (q <= 1))
        i = np.argsort(x)
        x = x[i]
        w = w[i]
        c = np.cumsum(w)
        inter = scipy.interpolate.interp1d(c, x, kind="nearest",fill_value="extrapolate")
        return inter(q[1:-1] * c[-1])


class Threshold(Rebin):
    """
        Applied threshold binning 
        -> content is scanned from the right of the histogram 
           until enough stats are accumulated so that 
                 bincontent - unc > threshold
           then move to next threshold
        list of threshold values need to be optimized
    """
    def __init__(self, h, thresh, extra=None, rsut=None):
        """
            thresh : thresholds to remain above
            h : either TH1 or list of TH1
            extra : list of hists to remain above 0
            rsut : relative stat. unc. threshold
        """
        nph = self._processHist(h)
        if extra is not None:
            extra_nphs = [self._processHist(ex) for ex in extra]
            # Check axes are correct #
            for extra_nph in extra_nphs:
                nph.compareAxes(extra_nph)
            extra_ws = np.c_[tuple(extra_nph.w for extra_nph in extra_nphs)]
            assert extra_ws.shape[0] == nph.w.shape[0]
        if not isinstance(thresh,np.ndarray):
            thresh = np.array(thresh)
        if nph.w.shape[0] < thresh.shape[0]:
            raise RuntimeError("Fewer bins than thresholds")

        # Threshold scan #
        logging.debug("Starting scan for Threshold")
        nbins = thresh.shape[0]
        rsut_trials = 1
        rsut_trials_max = 10
        while rsut_trials <= rsut_trials_max: # Rsut loop 
            factor = 1.
            epsilon = 0.01
            epsilon_min = epsilon * 1e-9
            self.ne = None
            while factor > 0.: # factor loop #
                thresh_test = thresh * factor * nph.w.sum() / thresh.max() 
                # Get idx #
                idx = self.rebin_method(thresh  = thresh_test,
                                        val     = nph.w, 
                                        var     = nph.s2,
                                        extra   = extra_ws,
                                        rsut    = rsut)
                if len(idx) > 0 and nph.w[0 : idx[0]].sum() < nph.w[idx[0] : (idx[1] if len(idx) > 1 else None)].sum(): # merge two first bins in case rising in content
                    idx = idx[1:]     
                # Get bin edges #
                ne = np.unique(np.r_[nph.e[0], nph.e[idx] , nph.e[-1]])
                logging.debug(f'\tTrying factor {factor} (epsilon = {epsilon}), number of bins = {len(ne)}')
                if ne.shape[0] <= nbins + 1: # Not too far
                    # if perfect number -> record it #
                    if ne.shape[0] == nbins + 1:
                        self.ne = ne
                    # Iteration #
                    if factor - epsilon > 0 or epsilon < epsilon_min:
                        factor -= epsilon
                    else:
                        epsilon /= 10
                    # Even if we found the correct number of bins, we want to continue, 
                    # maybe first bin is not populated as much as it could be 
                else: #self.ne.shape[0] > nbins + 1 ->  # Too far
                    if self.ne is None:
                        # Not converged, maybe we passed over the good threshold
                        # Go back one step, and divide epsilon 
                        factor += epsilon
                        epsilon /= 10
                        # Can't find the perfect point between too many and two few bins, just merge the first bins until it matches #
                        if epsilon < epsilon_min:
                            excess_bins = ne.shape[0]-(nbins+1)
                            assert excess_bins > 0
                            self.ne = copy(ne[excess_bins:])
                            self.ne[0] = ne[0]
                            logging.debug(f"Cannot find the sweet spot, will merge the first bins : {ne} [{ne.shape[0]} bins]  -> {self.ne} [{self.ne.shape[0]} bins]")
                            break
                    else:
                        # self.ne has been found, will not get better
                        break
            if self.ne is None: # Still not found 
                self.ne = ne
            if self.ne.shape[0] != nbins +1:
                logging.warning(f'{self.ne.shape[0]-1} bins were produced, but you asked for {nbins}, will modify the rsut from {rsut} to {rsut * 2} [Attempt {rsut_trials}/{rsut_trials_max}]')
                rsut *= 2
                rsut_trials += 1
            else:
                break
        if self.ne.shape[0] != nbins +1:
            raise RuntimeError(f'Error in threshold, hist will have {self.ne.shape[0]-1} bins, but you asked for {nbins} : bins = {self.ne}')
            # Because can be a problem for combination
        logging.debug(f'Found binning : {self.ne}')
                

    @staticmethod
    def rebin_method(thresh,val,var,extra,rsut=np.inf):
        """
            thresh : array of threshold values from right to left
            val    : array of bin height
            var    : variance of each bin
            extra  : additional contributions to be kept above threshold
            rsut   : relative stat. unc. threshold
        """
        assert thresh.shape[0] < val.shape[0]     
        assert np.all(thresh >= 0)     
        assert rsut >= 0.0 

        sum_val = 0
        sum_var = 0
        sum_extra = np.zeros_like(extra[0])

        val = val[::-1]
        var = var[::-1]
        extra = extra[::-1]

        la = len(val)
        lt = len(thresh)
        idx = np.zeros(lt, dtype=np.intp)
        tidx = -1
        for i in range(la):
            if tidx < -lt:
                break
            sum_val += val[i]
            sum_var += var[i]
            sum_extra += extra[i]
            unc = np.sqrt(sum_var)

            if (sum_val - unc) >= thresh[tidx] and np.all(sum_extra) and np.abs((unc / sum_val)) <= rsut:
                idx[tidx] = la - 1 - i
                sum_val = 0.0
                sum_var = 0.0
                sum_extra[:] = 0.0
                tidx -= 1

        return idx[1 + tidx :]     


# https://en.wikipedia.org/wiki/Poisson_distribution#Confidence_interval 
# poisson confidence interval (1-sigma, upper) for lambda if oberservation was 0 
LAMBDA0 = chi2.ppf(1 - (1 - (norm.cdf(1) * 2 - 1)) / 2, 2) / 2
class Threshold2(Rebin):
    """
        Applied threshold binning 
        -> content is scanned from the right of the histogram 
           until enough stats are accumulated so that 
                 bincontent - unc > threshold
           then move to next threshold
        list of threshold values need to be optimized
    """
    def __init__(self, h_list, thresh, fallback,  allowUnderEstimationFix=True):
        """
            h_list : list of ROOT.TH1X or NumpyHist from all the processes
            thresh : thresholds to remain above
            fallback : default values for variance when 0 in the bin 
                - signal : should be np.inf (enforce at least an event in the bin)
                - main backgrounds : should be sumw2/sumw
                - other backgrounds : 0
        """
        if not isinstance(thresh,np.ndarray):
            thresh = np.array(thresh)
        if not isinstance(fallback,np.ndarray):
            fallback = np.array(fallback)
        fallback *= LAMBDA0 ** 0.5 # mathematical correction
        if not isinstance(h_list,list):
            raise RuntimeError('`h_list` must be a list')
        nphs = [self._processHist(h) for h in h_list]
        # Check axes #
        for i in range(1,len(nphs)):
            nphs[0].compareAxes(nphs[i])
        e = nphs[0].e
        # Get content #
        ws = np.array([nph.w for nph in nphs])
        ss = np.array([nph.s for nph in nphs])
        if ws.shape[1] < thresh.shape[0]:
            raise RuntimeError(f"Fewer bins than thresholds hist.shape : {ws.shape[1]}, thresold.shape :  {thresh.shape[0]}")
        # Make data array #
        data = np.empty(ws.shape,dtype=np.dtype([('value',ws.dtype),('variance',ss.dtype)]))
        data['value'] = ws
        data['variance'] = ss
        # Cut out empty processes #
        valid_processes = data['value'].any(axis=1) # Non zero processes
        data = data[valid_processes]
        fallback = fallback[valid_processes]
        # Get total of content #
        totval = np.sum(data['value'],axis=0) # Sum over bin of all processes
        # Need to inverse because rebin_method goes from left to right
        data = data[:,::-1]

        # Threshold scan #
        logging.debug("Starting scan for Threshold2")
        nbins = thresh.shape[0]
        variance_trials = 1
        variance_trials_max = 10
        while variance_trials < variance_trials_max:
            factor = 1.
            epsilon = 0.01
            epsilon_min = epsilon * 1e-9
            self.ne = None
            while factor > 0.:
                thresh_test = thresh * factor * ws.sum() / thresh.max() 
                idx = self.rebin_method(thresh  = thresh_test,
                                        data    = data,
                                        fallback=fallback)
                # Invert back the bin indexes #
                idx = data.shape[1] - 1 - idx[::-1]
                # fuse left-most two bins if they are rising in content #
                if len(idx) > 0 and totval[0 : idx[0]].sum() < totval[idx[0] : (idx[1] if len(idx) > 1 else None)].sum():
                    idx = idx[1:]
                # Make binning #
                ne = np.unique(np.r_[e[0], e[idx] , e[-1]])
                logging.debug(f'\tTrying factor {factor} (epsilon = {epsilon}), number of bins = {len(ne)}')
                if ne.shape[0] <= nbins + 1: # Not too far
                    # if perfect number -> record it #
                    if ne.shape[0] == nbins + 1:
                        self.ne = ne
                    # Iteration #
                    if factor - epsilon > 0 or epsilon < epsilon_min:
                        factor -= epsilon 
                    else:
                        epsilon /= 10
                    # Even if we found the correct number of bins, we want to continue, 
                    # maybe first bin is not populated as much as it could be 
                else: #self.ne.shape[0] > nbins + 1 ->  # Too far
                    if self.ne is None and epsilon > epsilon_min:
                        # Not converged, maybe we passed over the good threshold
                        # Go back one step, and divide epsilon 
                        factor += epsilon
                        epsilon /= 10
                        # Can't find the perfect point between too many and two few bins, just merge the first bins until it matches #
                        if epsilon < epsilon_min:
                            excess_bins = ne.shape[0]-(nbins+1)
                            assert excess_bins > 0
                            self.ne = copy(ne[excess_bins:])
                            self.ne[0] = ne[0]
                            logging.debug(f"Cannot find the sweet spot, will merge the first bins : {ne} [{ne.shape[0]} bins]  -> {self.ne} [{self.ne.shape[0]} bins]")
                            break
                    else:
                        # self.ne has been found, will not get better
                        break
            if self.ne is None: # Still not found 
                self.ne = ne
            if self.ne.shape[0] != nbins +1:
                logging.warning(f'{self.ne.shape[0]-1} bins were produced, but you asked for {nbins}, will artificially divide the variance by 2 to help convergence [Attempt {variance_trials}/{variance_trials_max}]')
                data['variance'] /= 2
                variance_trials += 1
                if variance_trials == 5:
                    if  allowUnderEstimationFix:
                        logging.warning('You allow to fix under-estimation!')
                        break
                    else:
                        logging.warning('Does not seem to converge ... Will cancel all fallbacks')
                        fallback = np.zeros(data.shape[0])
            else:
                break

        if self.ne.shape[0] != nbins + 1:
            logging.warning(f'Error in threshold, hist will have {self.ne.shape[0]-1} bins, but you asked for {nbins} : bins = {self.ne}')
            # Because can be a problem for combination
        logging.debug(f'Found binning : {self.ne}')
                
    @staticmethod
    def rebin_method(thresh, data, fallback):
        """
        thresh: floaty[T] >= 0
        data: (value: floaty, variance: floaty)[P, N]
        fallback: floaty[P]

        note: bins are built "from left to right"
        """
        assert thresh.ndim == 1
        assert data.ndim == 2
        assert fallback.ndim == 1
        assert thresh.shape[0] > 0
        assert data.shape[0] == fallback.shape[0]

        acc_val = np.zeros(data.shape[:1])
        acc_var = np.zeros(data.shape[:1])
        idx = np.zeros(thresh.shape, dtype=np.intp)
        idx_num = 0
        for bin_curr in range(data.shape[1]):
            acc_val += data["value"][:, bin_curr]
            acc_var += data["variance"][:, bin_curr]
            tot_val = np.sum(acc_val)
            tot_var = np.sum(np.where(acc_var, acc_var, fallback))
            if tot_val - np.sqrt(tot_var) > thresh[idx_num]:
                idx[idx_num] = bin_curr
                idx_num += 1
                if len(thresh) > idx_num:
                    acc_val[:] = 0
                    acc_var[:] = 0
                else:
                    break
        return idx[:idx_num]


class Boundary(Rebin):
    """
        Applied boundary binning 
        Rebin with the given boundaries for the bin edges
        h not used (kept for compatibility)
    """
    def __init__(self, h=None, boundaries=None):
        """
            boundaries : list of bin edges
        """
        if boundaries is None:
            raise RuntimeError("Boundary method requires to set the boundaries")
        if not isinstance(boundaries,np.ndarray):
            boundaries = np.array(boundaries)
        self.ne = boundaries

class Boundary2D(Rebin):
    """
        Applied boundary binning 
        Rebin with the given boundaries for the bin edges
    """
    def __init__(self,h=None,bx=None,by=None):
        """
            bx : list of edges for the x axis
            by : list of edges for the y axis
        """
        if not isinstance(bx,np.ndarray):
            bx = np.array(bx)
        if not isinstance(by,np.ndarray):
            by = np.array(by)
        self.ne = [bx,by]

class Quantile2D(Rebin):
    """
        Applies quantile binning
        -> provide quantile boundaries and bin histogram accordingly
        list of quantile values need to be optimized
    """
    def __init__(self,h,qx,qy):
        """
            h : either TH1 or list of TH1
            qx : quantiles list [0 , ... 1]
            qy : quantiles list [0 , ... 1]
        """
        nph = self._processHist(h)
        nphx = nph.projectionX()
        nphy = nph.projectionY()

        qObjx = Quantile(nphx,qx)
        qObjy = Quantile(nphy,qy)

        self.ne = [qObjx.ne,qObjy.ne]



class Threshold2D(Rebin):
    """
        Applied threshold binning 
        -> content is scanned from the right of the histogram 
           until enough stats are accumulated so that 
                 bincontent - unc > threshold
           then move to next threshold
        list of threshold values need to be optimized
    """
    def __init__(self, h, threshx, threshy, extra=None, rsut=None):
        """
            h : either TH2 or list of TH2
            threshx : thresholds to remain above in the x direction
            threshy : thresholds to remain above in the y direction
            extra : list of hists to remain above 0
            rsut : relative stat. unc. threshold
        """
        nph = self._processHist(h)
        nphx = nph.projectionX()
        nphy = nph.projectionY()

        extra_nphs = [self._processHist(ex) for ex in extra]
        extra_nphxs = [extra_nph.projectionX() for extra_nph in extra_nphs]
        extra_nphys = [extra_nph.projectionY() for extra_nph in extra_nphs]

        qObjx = Threshold(nphx,threshx,extra_nphxs,rsut)
        qObjy = Threshold(nphy,threshy,eytra_nphys,rsut)

        self.ne = [qObjx.ne,qObjy.ne]


class Linearize2D(Rebin):
    def __init__(self,major='y'):
        if major != 'x' and major != 'y':
            raise RuntimeError(f'Major {major} not understood')
        self.major = major

        self.nemajor = None
        self.neminor = None
        self.plotData = None

    def __call__(self,h):
        """
            input : initial histogram TH2
            return : linearized TH1
        """
        # Get histograms into a single NumpyHist #
        nph = self._processHist(h)

        # Split along the major axis #
        if self.major == 'x':
            if self.nemajor is None:
                # If binning on major axis is not provided -> split per bin #
                self.nemajor = nph._e[0]
            nph_splits = [nph_split.projectionY() for nph_split in nph.split(self.nemajor,None,'x')]
        else:
            if self.nemajor is None:
                # If binning on major axis is not provided -> split per bin #
                self.nemajor = nph._e[1]
            nph_splits = [nph_split.projectionX() for nph_split in nph.split(None,self.nemajor,'y')]

        # If rebinning in the minor axis has been defined, do it #
        if self.neminor is not None:
            if not isinstance(self.neminor,list):
                raise RuntimeError('`self.neminor` must be a list of bin edges')
            if len(self.neminor) != len(nph_splits):
                raise RuntimeError(f'You request rebinning on eminor for {len(self.neminor)} major bins, but only {len(nph_splits)} histograms have been produced in the split')
            nph_tmp = []
            for nph_split,eminor in zip(nph_splits,self.neminor):
                nph_tmp.append(nph_split.rebin(eminor))
            nph_splits = nph_tmp
            # Save plot data (lines and positions) #
            self.savePlotData(self.neminor,self.nemajor)

        # Concatenate the linearized splits # 
        comb_nph = NumpyHist.concatenate(nph_splits)
        # Return the concatenated linearized hist #
        if isinstance(h,ROOT.TH1):
            name = h.GetName()
        if isinstance(h,NumpyHist):
            name = h.name
        return comb_nph.fillHistogram(name+'rebin')

    def savePlotData(self,eminor,emajor):
        labels = []
        ylabel = 'HME'
        xpos = [0.] + [float(eminor[i][-1] + i * eminor[i-1][-1]) for i in range(len(eminor))]
        lines = xpos[1:-1]
        for i in range(len(xpos)-1):
            label = f"{emajor[i]} < {ylabel} < {emajor[i+1]}"
            poslabel = [(xpos[i] + 0.1 * (xpos[i+1]-xpos[i]))/xpos[-1],0.75]
            labels.append({'text':label,'position':poslabel,'size':22-2*len(eminor)})
        self.plotData = {'labels':labels,'lines':lines}

    def getPlotData(self):
        return self.plotData

class LinearizeSplit(Linearize2D):
    def __init__(self,h,major='y',major_class=None,major_params=None,minor_class=None,minor_params=None):
        # Get histogram #
        nph = self._processHist(h)
        # Initialize Linearize #
        super(LinearizeSplit,self).__init__(major)
        # Project on the major axis #
        if major == 'x':
            hmajor = nph.projectionX()
        if major == 'y':
            hmajor = nph.projectionY()

        # For threshold algo, need to perform same adjustments #
        if major_class in ['Threshold','Threshold2']:
            major_params[1] = [self._processHist(h) for h in major_params[1]]
            if major == 'x':
                major_params[1] = [h.projectionX() for h in major_params[1]]
            if major == 'y':
                major_params[1] = [h.projectionY() for h in major_params[1]]

        
        # Use the major class method to obtain the major axis rebinning #
        majorObj = getattr(sys.modules[__name__], major_class)(hmajor,*major_params)
        self.nemajor = majorObj.ne
        logging.debug(f"Rebinning with class {major_class} yielded following major {self.major} axis bins : {self.nemajor}")

        # Split the 2D histogram along major axis #
        # (projection now done on the other axis, because we want to get the minor binning #
        if self.major == 'x':
            nph_splits = [nph_split.projectionY() for nph_split in nph.split(self.nemajor,None,'x')]
        if self.major == 'y':
            nph_splits = [nph_split.projectionX() for nph_split in nph.split(None,self.nemajor,'y')]
    
        # Same for extras in threshold algo #
        if minor_class in ['Threshold','Threshold2']:
            extra_nphs = [self._processHist(h) for h in minor_params[1]]
            if self.major == 'x':
                extra_nphs = [[h_split.projectionY() for h_split in h.split(self.nemajor,None,'x')]
                                            for h in extra_nphs]
            if self.major == 'y':
                extra_nphs = [[h_split.projectionX() for h_split in h.split(None,self.nemajor,'y')]
                                            for h in extra_nphs]
            if minor_class == 'Threshold':
                minor_params[1] = extra_nphs
            if minor_class == 'Threshold2':
                minor_params = [minor_params[0],minor_params[2]]

        self.neminor = []
        # Loop through all major bins #
        for i,nph_split in enumerate(nph_splits):
            # Threshold2 algo, need to replace just the signal by all processes # 
            if minor_class == 'Threshold2':
                nph_split = [extra_nph[i] for extra_nph in extra_nphs]
            # Apply the minor rebinning class on the histogram and parameters #
            minorObj = getattr(sys.modules[__name__], minor_class)(nph_split,*minor_params)
            # Record the new binning #
            self.neminor.append(minorObj.ne)
            logging.debug(f'Rebinning of the minor axis in major bin {i} [{self.nemajor[i]},{self.nemajor[i+1]}] yielded following binning : {minorObj.ne}')

