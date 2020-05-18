import math
import numpy
import ROOT
from collections import OrderedDict

# The largest and smallest values for variations of uR and uF 0.5, 1, 2
# times their central values are as the scale uncertainty.
# Assymetric variations (e.g. uF = 0.5, uR = 2) are excluded
def getScaleUncertainty(values):
    scales = {}
    scales['down'] = 1- min(values)
    scales['up'] = max(values) - 1 
    return scales
# Compute alpha_s variation uncertainties, using alpha_s = 0.116 and 0.120, which
# are stored as weight 2101 and 2102 in CMS samples, according to equation 27 in
# PDF4LHC paper: http://arxiv.org/pdf/1510.03865v1.pdf
def getAlphaSUncertainty(values):
    return abs(values[0] - values[1])/2
# Copied from MG code. To modify
def getHessianUncertainty(values):        
    lhaid=int(self.run_card['lhaid'])
    pdf_upp=0.0
    pdf_low=0.0
    if lhaid <= 90000:
        # use Hessian method (CTEQ & MSTW)
        if numofpdf>1:
            for i in range(int(numofpdf/2)):
                pdf_upp=pdf_upp+math.pow(max(0.0,pdfs[2*i+1]-cntrl_val,pdfs[2*i+2]-cntrl_val),2)
                pdf_low=pdf_low+math.pow(max(0.0,cntrl_val-pdfs[2*i+1],cntrl_val-pdfs[2*i+2]),2)
            if cntrl_val != 0.0:
                scale_pdf_info['pdf_upp'] = math.sqrt(pdf_upp)/cntrl_val*100
                scale_pdf_info['pdf_low'] = math.sqrt(pdf_low)/cntrl_val*100
            else:
                scale_pdf_info['pdf_upp'] = 0.0
                scale_pdf_info['pdf_low'] = 0.0
# Compute Gaussian PDF uncertainties, appropriate for NNPDF
def getNNPDFUncertainty(values):
    pdf_unc = {}
    pdf_unc["up"] = numpy.std(values, ddof=1)
    pdf_unc["down"] = pdf_unc["up"]
    return pdf_unc

#def getNNPDFUncertainty(values):
#    pdf_unc = {}
#    central = values["1000"]["1001"]
#    # These are alpha_s variations
#    exclude = ["2001", "2002"]
#    variations = [value for key, value in values["2000"].iteritems() if key not in exclude]
#    variance = 0
#    for xsec in variations:
#        variance += (xsec - central)*(xsec - central)
#        num = len(variations) - 1
#    return math.sqrt(variance/(num))
# Combine PDF fit and alpha_s uncertainties according to PDF4LHC recommendation.
# Equation 30 in http://arxiv.org/pdf/1510.03865v1.pdf, with r = 1.5
# (alpha_s uncertainty is +- 0.0015, and we use 0.119 and 0.117 PDF sets)
def getFullNNPDFUncertainty(pdf_values, alphas_values):
    pdf_unc = getNNPDFUncertainty(pdf_values)
    alpha_s_unc = getAlphaSUncertainty(alphas_values)
    # Taken to give the +- 0.00015 variation
    r = 1.5
    tot_pdf_unc = {}
    tot_pdf_unc["up"] = math.sqrt(pdf_unc["up"]*pdf_unc["up"] + r*r*alpha_s_unc*alpha_s_unc) 
    tot_pdf_unc["down"] = math.sqrt(pdf_unc["down"]*pdf_unc["down"] + r*r*alpha_s_unc*alpha_s_unc) 
    return tot_pdf_unc
