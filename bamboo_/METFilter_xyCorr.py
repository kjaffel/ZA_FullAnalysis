import math 
from bamboo import treefunctions as op

def METFilter(flags, era, isMC):
    # from https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
    # to be applied on data and mc
    cuts=[
            flags.goodVertices,
            flags.globalSuperTightHalo2016Filter,
            flags.HBHENoiseFilter,
            flags.HBHENoiseIsoFilter,
            flags.EcalDeadCellTriggerPrimitiveFilter,
            flags.BadPFMuonFilter,
            flags.BadPFMuonDzFilter]
    if era == '2017' or era =='2018':
        cuts.append(flags.ecalBadCalibFilter)
    else:
        cuts.append(flags.eeBadScFilter)

    return cuts

class METcorrection(object):
    # https://lathomas.web.cern.ch/lathomas/METStuff/XYCorrections/XYMETCorrection.h
    def __init__(self,rawMET,pv,sample,era,isMC):
        if(era=='2016'):
            if isMC:
                xcorr = (0.195191,   0.170948)
                ycorr = (0.0311891, -0.787627)
            else:
                if '2016B' in sample:
                    xcorr = (0.0478335,  0.108032)
                    ycorr = (-0.125148, -0.355672)
                elif '2016C' in sample: 
                    xcorr = ( 0.0916985, -0.393247)
                    ycorr = (-0.151445,  -0.114491)
                elif '2016D' in sample:
                    xcorr = ( 0.0581169, -0.567316)
                    ycorr = (-0.147549,  -0.403088)
                elif '2016E' in sample:
                    xcorr = ( 0.065622, -0.536856)
                    ycorr = (-0.188532, -0.495346)
                elif '2016F' in sample:
                    xcorr = ( 0.0313322, -0.39866)
                    ycorr = (-0.16081,   -0.960177)
                elif '2016G' in sample:
                    xcorr = (-0.040803,   0.290384)
                    ycorr = (-0.0961935, -0.666096)
                else:
                    xcorr = (-0.0330868, 0.209534)
                    ycorr = (-0.141513, -0.816732)


        elif(era=='2017'):
            #these are the corrections for v2 MET recipe (currently recommended for 2017)
            if isMC:
                xcorr = (0.217714, -0.493361)
                ycorr = (-0.177058, 0.336648)
            else: 
                if '2017B' in sample:
                    xcorr = ( 0.19563, -1.51859)
                    ycorr = (-0.306987, 1.84713)
                elif '2017C' in sample:
                    xcorr = ( 0.161661, -0.589933)
                    ycorr = (-0.233569,  0.995546)
                elif '2017D' in sample:
                    xcorr = ( 0.180911, -1.23553)
                    ycorr = (-0.240155,  1.27449)
                elif '2017E' in sample:
                    xcorr = ( 0.149494, -0.901305)
                    ycorr = (-0.178212,  0.535537)
                else:
                    xcorr = ( 0.165154, -1.02018)
                    ycorr = (-0.253794, -0.75776)
        else:
            if isMC:
                xcorr = (-0.296713,  0.141506)
                ycorr = (-0.115685, -0.0128193)
            else:
                if '2018A' in sample:
                    xcorr= (-0.362865,  1.94505)
                    ycorr= (-0.0709085, 0.307365)
                elif'2018B' in sample:
                    xcorr = (-0.492083, 2.93552)
                    ycorr = (-0.17874,  0.786844)
                elif '2018C' in sample:
                    xcorr = (-0.521349, 1.44544)
                    ycorr = (-0.118956, 1.96434)
                else:
                    xcorr = (-0.531151,  1.37568)
                    ycorr = (-0.0884639, 1.57089)
                
        METxcorr=xcorr[0] *pv.npvs+xcorr[1]
        METycorr=ycorr[0] *pv.npvs+ycorr[1]
            
        corrMETx=rawMET.pt*op.cos(rawMET.phi) +METxcorr
        corrMETy=rawMET.pt*op.sin(rawMET.phi) +METycorr
        
        self.pt=op.sqrt(corrMETx**2 +corrMETy**2)
        atan=op.atan(corrMETy/corrMETx)
        self.phi=op.multiSwitch((corrMETx> 0,atan),(corrMETy> 0,atan+math.pi),atan-math.pi)

class ULMETXYCorrection(object):
    # https://lathomas.web.cern.ch/lathomas/METStuff/XYCorrections/XYMETCorrection_withUL17andUL18andUL16.h
    def __init__(self,rawMET,pv,sample,runera,isMC):
        if runera=="UL2017":
            if isMC:
                METxcorr = -(-0.300155*npv +1.90608)
                METycorr = -(0.300213*npv +-2.02232)
            else:
                if "UL2017B" in sample:
                    METxcorr = -(-0.211161*npv +0.419333)
                    METycorr = -(0.251789*npv +-1.28089)
                elif "UL2017C" in sample: 
                    METxcorr = -(-0.185184*npv +-0.164009)
                    METycorr = -(0.200941*npv +-0.56853)
                elif "UL2017D" in sample:
                    METxcorr = -(-0.201606*npv +0.426502)
                    METycorr = -(0.188208*npv +-0.58313)
                elif "UL2017E" in sample:
                    METxcorr = -(-0.162472*npv +0.176329)
                    METycorr = -(0.138076*npv +-0.250239)
                elif "UL2017F" in sample:
                    METxcorr = -(-0.210639*npv +0.72934)
                    METycorr = -(0.198626*npv +1.028)

        if runera =="UL2018":
            if isMC:
                METxcorr = -(0.183518*npv +0.546754)
                METycorr = -(0.192263*npv +-0.42121)
            else:
                if "UL2018A" in sample :
                    METxcorr = -(0.263733*npv +-1.91115)
                    METycorr = -(0.0431304*npv +-0.112043)
                elif "UL2018B" in sample:
                    METxcorr = -(0.400466*npv +-3.05914)
                    METycorr = -(0.146125*npv +-0.533233)
                elif "UL2018C" in sample:
                    METxcorr = -(0.430911*npv +-1.42865)
                    METycorr = -(0.0620083*npv +-1.46021)
                elif "UL2018D" in sample: 
                    METxcorr = -(0.457327*npv +-1.56856)
                    METycorr = -(0.0684071*npv +-0.928372)

        if runera =="UL2016":
            if isMC:
                if "preVFP" in sample or "HIPM" in sample or "APV" in sample:
                    METxcorr = -(-0.188743*npv +0.136539)
                    METycorr = -(0.0127927*npv +0.117747)
                else:
                    METxcorr = -(-0.153497*npv +-0.231751)
                    METycorr = -(0.00731978*npv +0.243323)
            else:
                if "UL2016B" in sample:
                    METxcorr = -(-0.0214894*npv +-0.188255)
                    METycorr = -(0.0876624*npv +0.812885)
                if "UL2016C" in sample:
                    METxcorr = -(-0.032209*npv +0.067288)
                    METycorr = -(0.113917*npv +0.743906)
                if "UL2016D" in sample:
                    METxcorr = -(-0.0293663*npv +0.21106)
                    METycorr = -(0.11331*npv +0.815787)
                if "UL2016E" in sample:
                    METxcorr = -(-0.0132046*npv +0.20073)
                    METycorr = -(0.134809*npv +0.679068)
                if "UL2016F" in sample:
                    METxcorr = -(-0.0543566*npv +0.816597)
                    METycorr = -(0.114225*npv +1.17266)
                if "UL2016G" in sample:
                    METxcorr = -(0.121809*npv +-0.584893)
                    METycorr = -(0.0558974*npv +0.891234)
                if "UL2016H" in sample:
                    METxcorr = -(0.0868828*npv +-0.703489)
                    METycorr = -(0.0888774*npv +0.902632)
                #if(runera==yUL2016Flate) METxcorr = -(0.134616*npv +-0.89965)
                #if(runera==yUL2016Flate) METycorr = -(0.0397736*npv +1.0385)
    
        METxcorr_=METxcorr[0] *pv.npvs+METxcorr[1]
        METycorr_=METycorr[0] *pv.npvs+METycorr[1]
            
        corrMETx=rawMET.pt*op.cos(rawMET.phi) +METxcorr_
        corrMETy=rawMET.pt*op.sin(rawMET.phi) +METycorr_
        
        self.pt=op.sqrt(corrMETx**2 +corrMETy**2)
        atan=op.atan(corrMETy/corrMETx)
        self.phi=op.multiSwitch((corrMETx> 0,atan),(corrMETy> 0,atan+math.pi),atan-math.pi)
