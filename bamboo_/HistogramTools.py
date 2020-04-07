from math import ceil
from array import array
import numpy as np

from bamboo.root import gbl as ROOT

def setTDRStyle():
  tdrStyle =  ROOT.TStyle("tdrStyle","Style for P-TDR")

   #for the canvas:
  tdrStyle.SetCanvasBorderMode(0)
  tdrStyle.SetCanvasColor(ROOT.kWhite)
  tdrStyle.SetCanvasDefH(600) #Height of canvas
  tdrStyle.SetCanvasDefW(600) #Width of canvas
  tdrStyle.SetCanvasDefX(0)   #POsition on screen
  tdrStyle.SetCanvasDefY(0)


  tdrStyle.SetPadBorderMode(0)
  #tdrStyle.SetPadBorderSize(Width_t size = 1)
  tdrStyle.SetPadColor(ROOT.kWhite)
  tdrStyle.SetPadGridX(False)
  tdrStyle.SetPadGridY(False)
  tdrStyle.SetGridColor(0)
  tdrStyle.SetGridStyle(3)
  tdrStyle.SetGridWidth(1)

#For the frame:
  tdrStyle.SetFrameBorderMode(0)
  tdrStyle.SetFrameBorderSize(1)
  tdrStyle.SetFrameFillColor(0)
  tdrStyle.SetFrameFillStyle(0)
  tdrStyle.SetFrameLineColor(1)
  tdrStyle.SetFrameLineStyle(1)
  tdrStyle.SetFrameLineWidth(1)
  
#For the histo:
  #tdrStyle.SetHistFillColor(1)
  #tdrStyle.SetHistFillStyle(0)
  tdrStyle.SetHistLineColor(1)
  tdrStyle.SetHistLineStyle(0)
  tdrStyle.SetHistLineWidth(1)
  #tdrStyle.SetLegoInnerR(Float_t rad = 0.5)
  #tdrStyle.SetNumberContours(Int_t number = 20)

  tdrStyle.SetEndErrorSize(2)
  #tdrStyle.SetErrorMarker(20)
  #tdrStyle.SetErrorX(0.)
  
  tdrStyle.SetMarkerStyle(20)
  
#For the fit/function:
  tdrStyle.SetOptFit(1)
  tdrStyle.SetFitFormat("5.4g")
  tdrStyle.SetFuncColor(2)
  tdrStyle.SetFuncStyle(1)
  tdrStyle.SetFuncWidth(1)

#For the date:
  tdrStyle.SetOptDate(0)
  # tdrStyle.SetDateX(Float_t x = 0.01)
  # tdrStyle.SetDateY(Float_t y = 0.01)

# For the statistics box:
  tdrStyle.SetOptFile(0)
  tdrStyle.SetOptStat(0) # To display the mean and RMS:   SetOptStat("mr")
  tdrStyle.SetStatColor(ROOT.kWhite)
  tdrStyle.SetStatFont(42)
  tdrStyle.SetStatFontSize(0.025)
  tdrStyle.SetStatTextColor(1)
  tdrStyle.SetStatFormat("6.4g")
  tdrStyle.SetStatBorderSize(1)
  tdrStyle.SetStatH(0.1)
  tdrStyle.SetStatW(0.15)
  # tdrStyle.SetStatStyle(Style_t style = 1001)
  # tdrStyle.SetStatX(Float_t x = 0)
  # tdrStyle.SetStatY(Float_t y = 0)

# Margins:
  tdrStyle.SetPadTopMargin(0.05)
  tdrStyle.SetPadBottomMargin(0.13)
  tdrStyle.SetPadLeftMargin(0.16)
  tdrStyle.SetPadRightMargin(0.02)

# For the Global title:

  tdrStyle.SetOptTitle(0)
  tdrStyle.SetTitleFont(42)
  tdrStyle.SetTitleColor(1)
  tdrStyle.SetTitleTextColor(1)
  tdrStyle.SetTitleFillColor(10)
  tdrStyle.SetTitleFontSize(0.05)
  # tdrStyle.SetTitleH(0) # Set the height of the title box
  # tdrStyle.SetTitleW(0) # Set the width of the title box
  # tdrStyle.SetTitleX(0) # Set the position of the title box
  # tdrStyle.SetTitleY(0.985) # Set the position of the title box
  # tdrStyle.SetTitleStyle(Style_t style = 1001)
  # tdrStyle.SetTitleBorderSize(2)

# For the axis titles:

  tdrStyle.SetTitleColor(1, "XYZ")
  tdrStyle.SetTitleFont(42, "XYZ")
  tdrStyle.SetTitleSize(0.06, "XYZ")
  # tdrStyle.SetTitleXSize(Float_t size = 0.02) # Another way to set the size?
  # tdrStyle.SetTitleYSize(Float_t size = 0.02)
  tdrStyle.SetTitleXOffset(0.9)
  tdrStyle.SetTitleYOffset(1.25)
  # tdrStyle.SetTitleOffset(1.1, "Y") # Another way to set the Offset

# For the axis labels:

  tdrStyle.SetLabelColor(1, "XYZ")
  tdrStyle.SetLabelFont(42, "XYZ")
  tdrStyle.SetLabelOffset(0.007, "XYZ")
  tdrStyle.SetLabelSize(0.03, "XYZ")

# For the axis:

  tdrStyle.SetAxisColor(1, "XYZ")
  tdrStyle.SetStripDecimals(True)
  tdrStyle.SetTickLength(0.03, "XYZ")
  tdrStyle.SetNdivisions(510, "XYZ")
  tdrStyle.SetPadTickX(1)  # To get tick marks on the opposite side of the frame
  tdrStyle.SetPadTickY(1)

# Change for log plots:
  tdrStyle.SetOptLogx(0)
  tdrStyle.SetOptLogy(0)
  tdrStyle.SetOptLogz(0)

  tdrStyle.SetCanvasDefH(600) #Height of canvas
  tdrStyle.SetCanvasDefW(540) #Width of canvas
  tdrStyle.SetTitleSize(1, "XYZ")
  tdrStyle.SetLabelSize(0.1, "XYZ")
  tdrStyle.cd()


  return tdrStyle



# CMS_lumi
#   Initiated by: Gautier Hamel de Monchenault (Saclay)
#   Translated in Python by: Joshua Hardenbrook (Princeton)
#   Updated by:   Dinko Ferencek (Rutgers)
def CMS_lumi(pad, iPeriod, iPosX, extraText="Preliminary"):
    cmsText     = "CMS"
    cmsTextFont   = 61  

    writeExtraText = True
    # extraText   = "Preliminary"
    extraTextFont = 52 

    lumiTextSize     = 0.6
    lumiTextOffset   = 0.2

    cmsTextSize      = 1. #0.75
    cmsTextOffset    = 0.1

    relPosX    = 0.045
    relPosY    = 0.035
    relExtraDY = 1.2

    extraOverCmsTextSize  = 0.76

    lumi_13TeV = "35.9 fb^{-1}"
    lumi_8TeV  = "19.7 fb^{-1}" 
    lumi_7TeV  = "5.1 fb^{-1}"
    lumi_sqrtS = ""

    drawLogo      = False
    outOfFrame    = False
    
    if(iPosX/10==0 ): outOfFrame = True

    alignY_=3
    alignX_=2
    if( iPosX/10==0 ): alignX_=1
    if( iPosX==0    ): alignY_=1
    if( iPosX/10==1 ): alignX_=1
    if( iPosX/10==2 ): alignX_=2
    if( iPosX/10==3 ): alignX_=3
    align_ = 10*alignX_ + alignY_

    H = pad.GetWh()
    W = pad.GetWw()
    l = pad.GetLeftMargin()
    t = pad.GetTopMargin()
    r = pad.GetRightMargin()
    b = pad.GetBottomMargin()
    e = 0.025

    pad.cd()

    lumiText = ""
    if( iPeriod==1 ):
        lumiText += lumi_7TeV
        lumiText += " (7 TeV)"
    elif ( iPeriod==2 ):
        lumiText += lumi_8TeV
        lumiText += " (8 TeV)"

    elif( iPeriod==3 ):      
        lumiText = lumi_8TeV 
        lumiText += " (8 TeV)"
        lumiText += " + "
        lumiText += lumi_7TeV
        lumiText += " (7 TeV)"
    elif ( iPeriod==4 ):
        lumiText += lumi_13TeV
        lumiText += " (13 TeV)"
    elif ( iPeriod==7 ):
        if( outOfFrame ):lumiText += "#scale[0.85]{"
        lumiText += lumi_13TeV 
        lumiText += " (13 TeV)"
        lumiText += " + "
        lumiText += lumi_8TeV 
        lumiText += " (8 TeV)"
        lumiText += " + "
        lumiText += lumi_7TeV
        lumiText += " (7 TeV)"
        if( outOfFrame): lumiText += "}"
    elif ( iPeriod==12 ):
        lumiText += "8 TeV"
    elif ( iPeriod==0 ):
        lumiText += lumi_sqrtS
            
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(ROOT.kBlack)    
    
    extraTextSize = 0.8 #extraOverCmsTextSize*cmsTextSize
    
    latex.SetTextFont(42)
    latex.SetTextAlign(31) 
    latex.SetTextSize(extraTextSize*t)    
    # latex.SetTextSize(lumiTextSize*t)    

    latex.DrawLatex(1-r,1-t+lumiTextOffset*t,lumiText)

    if( outOfFrame ):
        latex.SetTextFont(cmsTextFont)
        latex.SetTextAlign(11) 
        latex.SetTextSize(cmsTextSize*t)    
        latex.DrawLatex(l,1-t+lumiTextOffset*t,cmsText)
  
    pad.cd()

    posX_ = 0
    if( iPosX%10<=1 ):
        posX_ =   l + relPosX*(1-l-r)
    elif( iPosX%10==2 ):
        posX_ =  l + 0.5*(1-l-r)
    elif( iPosX%10==3 ):
        posX_ =  1-r - relPosX*(1-l-r)

    posY_ = 1-t - relPosY*(1-t-b)

    if( not outOfFrame ):
        if( drawLogo ):
            posX_ =   l + 0.045*(1-l-r)*W/H
            posY_ = 1-t - 0.045*(1-t-b)
            xl_0 = posX_
            yl_0 = posY_ - 0.15
            xl_1 = posX_ + 0.15*H/W
            yl_1 = posY_
            CMS_logo = ROOT.TASImage("CMS-BW-label.png")
            pad_logo =  ROOT.TPad("logo","logo", xl_0, yl_0, xl_1, yl_1 )
            pad_logo.Draw()
            pad_logo.cd()
            CMS_logo.Draw("X")
            pad_logo.Modified()
            pad.cd()          
        else:
            latex.SetTextFont(cmsTextFont)
            latex.SetTextSize(cmsTextSize*t)
            latex.SetTextAlign(align_)
            latex.DrawLatex(posX_, posY_, cmsText)
            if( writeExtraText ) :
                latex.SetTextFont(extraTextFont)
                latex.SetTextAlign(align_)
                latex.SetTextSize(extraTextSize*t)
                latex.DrawLatex(posX_, posY_- relExtraDY*cmsTextSize*t, extraText)
    elif( writeExtraText ):
        if( iPosX==0):
            posX_ =   l +  relPosX*(1-l-r)
            posY_ =   1-t+lumiTextOffset*t

        latex.SetTextFont(extraTextFont)
        latex.SetTextSize(extraTextSize*t)
        latex.SetTextAlign(align_)
        latex.DrawLatex(posX_, posY_, extraText)      

    pad.Update()


def getEnvelopeHistograms(nominal, variations):
    """
    Compute envelop histograms create by all variations histograms. The envelop is simply the maximum
    and minimum deviations from nominal for each bin of the distribution
    Arguments:
    nominal: The nominal histogram
    variations: a list of histograms to compute the envelop from
    """

    if len(variations) < 2:
        raise TypeError("At least two variations histograms must be provided")

    # Use GetNcells() so that it works also for 2D histograms
    n_bins = nominal.GetNcells()
    for v in variations:
        if v.GetNcells() != n_bins:
            raise RuntimeError("Variation histograms do not have the same binning as the nominal histogram")

    up = nominal.Clone()
    up.SetDirectory(ROOT.nullptr)
    up.Reset()

    down = nominal.Clone()
    down.SetDirectory(ROOT.nullptr)
    down.Reset()

    for i in range(0, n_bins):
        minimum = float("inf")
        maximum = float("-inf")

        for v in variations:
            c = v.GetBinContent(i)
            minimum = min(minimum, c)
            maximum = max(maximum, c)

        up.SetBinContent(i, maximum)
        down.SetBinContent(i, minimum)

    return (up, down)


def equaliseBins(hist, title='BLR bins'):
    """Change bin boundaries along X axis of hist to 1, 2, ..., nBins+1.
    Does not affect actual bin contents or errors.
    Return a cloned histogram, no side-effect on hist."""

    newHist = hist.Clone()
    newHist.SetDirectory(ROOT.nullptr)
    xAxis = newHist.GetXaxis()
    xAxis.SetTitle(title)
    nBins = xAxis.GetNbins()
    newBins = array('f', range(1, nBins + 2))
    xAxis.Set(nBins, newBins)
    return newHist


def openFileAndGet(path, mode="read"):
    """Open ROOT file in a mode, check if open properly, and return TFile handle."""

    _tf = ROOT.TFile.Open(path, mode)
    if not _tf or not _tf.IsOpen():
        raise Exception("Could not open file {}".format(path))
    return _tf


def readRecursiveDirContent(content, currTDir, resetDir=True):
    """Fill dictionary content with the directory structure of currTDir.
    Every object is read and put in content with their name as the key.
    Sub-folders will define sub-dictionaries in content with their name as the key.
    """

    if not currTDir.InheritsFrom("TDirectory") or not isinstance(content, dict):
        return

    # Retrieve the directory structure inside the ROOT file
    currPath = currTDir.GetPath().split(':')[-1].split('/')[-1]

    if currPath == '':
        # We are in the top-level directory
        thisContent = content
    else:
        thisContent = {}
        content[currPath] = thisContent

    listKeys = currTDir.GetListOfKeys()

    for key in listKeys:
        obj = key.ReadObj()
        if obj.InheritsFrom("TDirectory"):
            print("Entering sub-directory {}".format(obj.GetPath()))
            readRecursiveDirContent(thisContent, obj)
        else:
            name = obj.GetName()
            thisContent[name] = obj
            if resetDir:
                obj.SetDirectory(0)


def writeRecursiveDirContent(content, currTDir):
    """Write the items in dictionary content to currTDir, respecting the sub-directory structure."""

    if not currTDir.IsWritable() or not isinstance(content, dict):
        return

    for key, obj in content.items():
        if isinstance(obj, dict):
            print("Creating new sub-directory {}".format(key))
            subDir = currTDir.mkdir(key)
            writeRecursiveDirContent(obj, subDir)
        elif isinstance(obj, ROOT.TObject):
            currTDir.WriteTObject(obj, key)


def randomiseHistMCStats(hist):
    """Randomise the yields in each bin according to the statistical uncertainty in the bin"""

    newHist = hist.Clone()

    rng = ROOT.TRandom2()
    rng.SetSeed(0)
    sumw2Arr = hist.GetSumw2()
    assert(sumw2Arr.GetSize() == hist.GetNcells())

    for i in range(hist.GetNcells()):
        orig = hist.GetBinContent(i)
        sumw2 = sumw2Arr[i]
        if sumw2 == 0 or orig == 0:
            continue
        effN = ceil(orig ** 2 / sumw2)
        ran = rng.Poisson(effN)
        new = ran * orig / effN
        # print("Rel. uncertainty: {}, effective: {}, old: {}, new: {}".format(sqrt(sumw2)/orig, effN, orig, new))
        newHist.SetBinContent(i, new)

    return newHist


def addHists(histList, newName):
    myIt = iter(histList)
    newHist = next(myIt).Clone(newName)
    for hist in myIt:
        newHist.Add(hist)
    return newHist


class RatioPalette:
    """ Create color palette by assembling several "beautiful" (possibly inverted) ROOT palettes"""

    colors = {
        "deepsea": (np.array([0./255.,  9./255., 13./255., 17./255., 24./255.,  32./255.,  27./255.,  25./255.,  29./255.]),
                    np.array([0./255.,  0./255.,  0./255.,  2./255., 37./255.,  74./255., 113./255., 160./255., 221./255.]),
                    np.array([28./255., 42./255., 59./255., 78./255., 98./255., 129./255., 154./255., 184./255., 221./255.])),
        "bird": (np.array([0.2082, 0.0592, 0.0780, 0.0232, 0.1802, 0.5301, 0.8186, 0.9956, 0.9764]),
                 np.array([0.1664, 0.3599, 0.5041, 0.6419, 0.7178, 0.7492, 0.7328, 0.7862, 0.9832]),
                 np.array([0.5293, 0.8684, 0.8385, 0.7914, 0.6425, 0.4662, 0.3499, 0.1968, 0.0539])),
        "invDarkBody": (np.array([242./255., 234./255., 237./255., 230./255., 212./255., 156./255., 99./255., 45./255., 0./255.]),
                        np.array([243./255., 238./255., 238./255., 168./255., 101./255.,  45./255.,  0./255.,  0./255., 0./255.]),
                        np.array([230./255.,  95./255.,  11./255.,   8./255.,   9./255.,   3./255.,  1./255.,  1./255., 0./255.])),
        "greyScale": (np.array([0./255., 32./255., 64./255., 96./255., 128./255., 160./255., 192./255., 224./255., 255./255.]),
                      np.array([0./255., 32./255., 64./255., 96./255., 128./255., 160./255., 192./255., 224./255., 255./255.]),
                      np.array([0./255., 32./255., 64./255., 96./255., 128./255., 160./255., 192./255., 224./255., 255./255.])),
        "blueYellow": (np.array([0./255.,  22./255., 44./255., 68./255., 93./255., 124./255., 160./255., 192./255., 237./255.]),
                       np.array([0./255.,  16./255., 41./255., 67./255., 93./255., 125./255., 162./255., 194./255., 241./255.]),
                       np.array([97./255., 100./255., 99./255., 99./255., 93./255.,  68./255.,  44./255.,  26./255.,  74./255.])),
        # "middle" is at 0.5
        "temperatureMap": (np.array([34./255.,  70./255., 129./255., 187./255., 225./255., 226./255., 216./255., 193./255., 179./255.]),
                           np.array([48./255.,  91./255., 147./255., 194./255., 226./255., 229./255., 196./255., 110./255.,  12./255.]),
                           np.array([234./255., 212./255., 216./255., 224./255., 206./255., 110./255.,  53./255.,  40./255.,  29./255.])),
        # "middle" is at 0.36/0.64
        "blackBody": (np.array([243./255., 243./255., 240./255., 240./255., 241./255., 239./255., 186./255., 151./255., 129./255.]),
                      np.array([0./255.,  46./255.,  99./255., 149./255., 194./255., 220./255., 183./255., 166./255., 147./255.]),
                      np.array([6./255.,   8./255.,  36./255.,  91./255., 169./255., 235./255., 246./255., 240./255., 233./255.])),
        # "blueYellow": (np.array([]),
        #                np.array([]),
        #                np.array([])),
    }

    def __init__(self, paletteList, nColors=250):
        red = np.concatenate([np.flip(self.colors[colSet][0]) if doFlip else self.colors[colSet][0] for colSet, doFlip in paletteList])
        green = np.concatenate([np.flip(self.colors[colSet][1]) if doFlip else self.colors[colSet][1] for colSet, doFlip in paletteList])
        blue = np.concatenate([np.flip(self.colors[colSet][2]) if doFlip else self.colors[colSet][2] for colSet, doFlip in paletteList])
        number = len(red)
        self.nColors = nColors
        stops = np.linspace(0., 1., number)
        index = ROOT.TColor.CreateGradientColorTable(number, stops, red, green, blue, self.nColors, 1.)
        ROOT.gStyle.SetPalette(ROOT.kBird)
        assert(index >= 0)
        self.palette = np.arange(index + 1, index + self.nColors + 2, dtype=np.int32)

    def set(self, hist, logLower=True, powerLower=10., logUpper=True, powerUpper=10., middle=0.5):
        """ Apply palette to ratio histogram, so that the color at "middle" lies at the level of z=1 """

        ROOT.gStyle.SetPalette(self.nColors, self.palette)
        nContours = 100
        middleContour = int(middle * nContours)
        if logLower:
            lower = np.log10(np.linspace(np.power(powerLower, hist.GetMinimum()), 10., middleContour, endpoint=False)) / np.log10(powerLower)
        else:
            lower = np.linspace(hist.GetMinimum(), 1., middleContour, endpoint=False)
        if logUpper:
            upper = np.power(powerUpper, np.linspace(0., np.log10(hist.GetMaximum()) / np.log10(powerUpper), nContours - middleContour))
        else:
            upper = np.linspace(1., hist.GetMaximum(), nContours - middleContour)
        contours = np.concatenate((lower, upper))
        hist.SetContour(nContours, contours)

    def reset(self):
        ROOT.gStyle.SetPalette(ROOT.kBird)
