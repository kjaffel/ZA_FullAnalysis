import math

def getZATollbbBR():
    # FIXME
    # Not implemented yet for interpretation
    return 1.

def getZACrossSection():
    # FIXME
    # Not implemented yet for interpretation
    return 1.

def getZACrossSectionUncertainties():
    # FIXME
    # Not implemented yet for interpretation
    """
    return up, down
    """
    return 0.01, 0.01

def getLuminosity(era):
    if era == '2016':
        lumi = 35921.875594646
    elif era == '2017':
        lumi = 41529.152060112
    elif era == "2018":
        lumi = 59740.565201546
    return lumi

def getLuminosityUncertainty(era):
    if era == '2016':
        uncer = 1.025 
    elif era == '2017':
        uncer = 1.023
    elif era == '2018':
        uncer=  1.025
    return uncer
