import sys
sys.dont_write_bytecode = True
import math
import numpy as np

def ZAlogger(nm):
    import logging
    LOG_LEVEL = logging.DEBUG
    stream = logging.StreamHandler()
    stream.setLevel(LOG_LEVEL)
    logger = logging.getLogger('{}'.format(nm))
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(stream)
    try:
        import colorlog
        from colorlog import ColoredFormatter
        formatter = ColoredFormatter(
                    "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
                    datefmt=None,
                    reset=True,
                    log_colors={
                            'DEBUG':    'green',
                            'INFO':     'cyan',
                            'WARNING':  'blue',
                            'ERROR':    'red',
                            'CRITICAL': 'red',
                            },
                    secondary_log_colors={},
                    style='%')
        stream.setFormatter(formatter)
    except ImportError:
        print(' try https://pypi.org/project/colorlog/  for colorlog')
        pass
    return logger

def getZATollbbBR(H, A, tb ):
    return 1.

def mass_to_str(m):
    m = '%.2f' % (float(m))
    return str(m).replace('.', 'p')

def loadSushiInfos(len_, fileName):
    in_dtypes = [
            ("DatasetName",  'U%s'%len_),
            ("Sushi_xsc@NLO[pb]", float),
            ("Sushi_xsc_err[pb]", float),
            ("BR(H -> ZA )", float),
            ("BR(A  -> bb)", float),
            ("Ymb,H[GeV]", float),
            ("Ymb,A[GeV]", float),
            ("Partialwidth(H ->bb)[GeV]", float),
            ("Partial_width(A ->bb)[GeV]", float),
            ("Totalwidth,H[GeV]", float),
            ("Totalwidth,A[GeV]", float),
            ("WHMHPercent", float),
            ("WAMAPercent", float)
            ]
    with open(fileName) as inF:
        arr = np.genfromtxt(inF, skip_header=1, dtype=in_dtypes)
    #print( arr.dtype.type )#names) 
    pars = np.array([ [ float(tk.replace("p", ".").split('-')[-1]) for tk in dsNm.split("_")[1:4] ] for dsNm in arr["DatasetName"] ])
    return np.hstack((
        arr["DatasetName"][:,None],
        pars[:,:3], ## mH,mA,tb 
        arr["Sushi_xscNLOpb"][:,None],
        arr["Sushi_xsc_errpb"][:,None],
        arr["BRH__ZA_"][:,None],
        arr["BRA___bb"][:,None]
        ))

def get_xsc_br_fromSushi(smpNm, arr):
    for lis in arr:
        if not smpNm == lis[0]: continue
        xsc     = lis[4]
        xsc_err = lis[5]
        br_HeavytoZlight  = lis[6]
        br_lighttobb      = lis[7]
        return xsc, xsc_err, float(br_HeavytoZlight), float(br_lighttobb)

def get_2hdm_xsc_br_unc_fromSushi(m_Heavy, m_light, process, mode):
    br = 1.
    heavy = 'H' if mode == 'HToZA' else 'A'
    light = 'A' if mode == 'HToZA' else 'H'
    tanb  = '1p50' if process == 'ggH' else '20p00' 
    smpNms = {'ggH':
                {'lo':"GluGluTo{}To2L2B_M{}-{}_M{}-{}_tb-{}_TuneCP5_13TeV-madgraph-pythia8".format(mode, heavy, m_Heavy, light, m_light, tanb) },
              'bbH':
                {'lo':"{}To2L2B_M{}-{}_M{}-{}_tb-{}_TuneCP5_bbH4F_13TeV-madgraph-pythia8".format(mode, heavy, m_Heavy, light, m_light, tanb),
                 'nlo':"{}To2L2B_M{}-{}_M{}-{}_tb-{}_TuneCP5_bbH4F_13TeV-amcatnlo-pythia8".format(mode, heavy, m_Heavy, light, m_light, tanb) } 
            }

    smpNm_lo = smpNms[process]['lo']
    base = "/home/ucl/cp3/kjaffel/ZAPrivateProduction/data/"
    
    benchmarks_lo = loadSushiInfos(len(smpNm_lo),"{}/list_benchmarks_{}_lo_{}_datasetnames.txt".format(base, process, mode))
    fullsim_lo    = loadSushiInfos(len(smpNm_lo),"{}/list_fullsim_{}_lo_{}_datasetnames.txt".format(base, process, mode))
    all_          = loadSushiInfos(len(smpNm_lo),"{}/list_all_{}_lo_{}_datasetnames.txt".format(base, process, mode))
    
    try:
        arrs = np.concatenate((benchmarks_lo, fullsim_lo, all_))
        xsc, xsc_err, br_HeavytoZlight, br_lighttobb = get_xsc_br_fromSushi(smpNm_lo, arrs)
    except:
        logger.warning(' sushi infos not found for: {}, {}, {}, {} will the left-over of nlo '.format(m_Heavy, m_light, process, mode))
        benchmarks_nlo = loadSushiInfos(len(smpNms['bbH']['nlo']),"{}/list_benchmarks_bbH_nlo_{}_datasetnames.txt".format(base, mode))
        fullsim_nlo    = loadSushiInfos(len(smpNms['bbH']['nlo']),"{}/list_fullsim_bbH_nlo_{}_datasetnames.txt".format(base, mode))
        arrs = np.concatenate((fullsim_nlo, benchmarks_nlo))
        xsc, xsc_err, br_HeavytoZlight, br_lighttobb = get_xsc_br_fromSushi(smpNms['bbH']['nlo'], arrs)
    br      = br_HeavytoZlight *  br_lighttobb
    return br

def getZACrossSectionUncertainties():
    # FIXME
    # Not implemented yet for interpretation
    """
    return up, down
    """
    return 0.01, 0.01

def getLuminosity(era):
    if era == '2016-preVFP':
        lumi = 19667.812849099  #pb
    elif era == '2016-postVFP':
        lumi = 16977.701784453  #pb
    elif era == '2016':
        lumi = 35921.875594646  #pb
    elif era == '2017':
        lumi = 41529.152060112  #pb
    elif era == "2018":
        lumi = 59740.565201546  #pb
    return lumi

def getLuminosityUncertainty(era):
    if era == '2016':
        uncer = 1.025 
    elif era == '2017':
        uncer = 1.023
    elif era == '2018':
        uncer= 1.025
    return uncer

