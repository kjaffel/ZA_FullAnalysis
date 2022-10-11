import os, sys
sys.dont_write_bytecode = True
import yaml
import math


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

logger = ZAlogger(__name__)


def get_Nm_for_runmode(mode): 
    Nm_formode = {'ellipse':'rho_steps',
                  'dnn'    :'dnn_scores',
                  'mbb'    :'mbb_bins',
                  'mllbb'  :'mllbb_bins',
                  'mjj_vs_mlljj' : 'mjj_vs_mlljj_map',
                  'mjj_and_mlljj': 'mjj_and_mlljj_combined_bins', }
    return Nm_formode[mode]


def mass_to_str(m):
    m = '%.2f' % (float(m))
    return str(m).replace('.', 'p')


def cat_to_tuplemass(c):
    m0 = float(c.split('_')[2])
    m1 = float(c.split('_')[4]) 
    return (m0, m1)


def loadSushiInfos(len_, fileName):
    import numpy as np
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
    # depreacted !!    
    import numpy as np
    base   = "/home/ucl/cp3/kjaffel/ZAPrivateProduction/data/"
    heavy  = mode[0]
    light  = mode[-1]
    
    smpNms = {
        'ggH': {
            'lo':"GluGluTo{}To2L2B_M{}-{}_M{}-{}_tb-1p50_TuneCP5_13TeV-madgraph-pythia8".format(mode, heavy, m_Heavy, light, m_light) },
        'bbH':{
            'lo':"{}To2L2B_M{}-{}_M{}-{}_tb-20p00_TuneCP5_bbH4F_13TeV-madgraph-pythia8".format(mode, heavy, m_Heavy, light, m_light),
            'nlo':"{}To2L2B_M{}-{}_M{}-{}_tb-20p00_TuneCP5_bbH4F_13TeV-amcatnlo-pythia8".format(mode, heavy, m_Heavy, light, m_light) } 
        }
    
    smpNm_lo = smpNms[process]['lo']
    
    benchmarks_lo = loadSushiInfos(len(smpNm_lo),"{}/list_benchmarks_{}_lo_{}_datasetnames.txt".format(base, process, mode))
    fullsim_lo    = loadSushiInfos(len(smpNm_lo),"{}/list_fullsim_{}_lo_{}_datasetnames.txt".format(base, process, mode))
    all_          = loadSushiInfos(len(smpNm_lo),"{}/list_all_{}_lo_{}_datasetnames.txt".format(base, process, mode))
    
    try:
        arrs = np.concatenate((benchmarks_lo, fullsim_lo, all_))
        xsc, xsc_err, br_HeavytoZlight, br_lighttobb = get_xsc_br_fromSushi(smpNm_lo, arrs)
    except:
        logger.warning(' sushi infos not found for: {}, {}, {}, {} will look to some left-over at nlo '.format(m_Heavy, m_light, process, mode))
        benchmarks_nlo = loadSushiInfos(len(smpNms['bbH']['nlo']),"{}/list_benchmarks_bbH_nlo_{}_datasetnames.txt".format(base, mode))
        fullsim_nlo    = loadSushiInfos(len(smpNms['bbH']['nlo']),"{}/list_fullsim_bbH_nlo_{}_datasetnames.txt".format(base, mode))
        arrs = np.concatenate((fullsim_nlo, benchmarks_nlo))
        xsc, xsc_err, br_HeavytoZlight, br_lighttobb = get_xsc_br_fromSushi(smpNms['bbH']['nlo'], arrs)
    
    return xsc, xsc_err, br_HeavytoZlight, br_lighttobb


def get_SignalStatisticsUncer(m_heavy, m_light, process, mode, tb=None):
    br_Ztoll = 0.067264 
    heavy    = mode[0]
    light    = mode[-1]
    if tb is None:
        tb     = 1.5 if process.startswith('gg') else 20.

    with open('data/sushi1.7.0-xsc_tanbeta-{}_2hdm-type2.yml'.format(float(tb))) as f_:
        dict_ = yaml.safe_load(f_)

    given_mass = dict_[mode]['M{}_{}_M{}_{}'.format(heavy, float(m_heavy), light, float(m_light))]
    br_HeavytoZlight = given_mass['branching-ratio']['{}ToZ{}'.format(heavy, light)]
    br_lighttobb     = given_mass['branching-ratio']['{}Tobb'.format(light)]
    br = float(br_HeavytoZlight) * br_Ztoll* float(br_lighttobb)
    
    if process == 'gg{}'.format(heavy):
        xsc      = given_mass['cross-section'][process].split()[0]
        xsc_err  = given_mass['cross-section'][process].split()[2]
    else:
        xsc      = given_mass['cross-section'][process]['NLO'].split()[0]
        xsc_err  = given_mass['cross-section'][process]['NLO'].split()[2]
    
    return float(xsc), float(xsc_err), br


def overwrite_path(f):
    with open(f, 'r') as file :
        filedata = file.read()
    filedata = filedata.replace('UL16', 'ULfullrun2')
    with open(f, 'w') as file:
        file.write(filedata)
    return f


def getLuminosity(era):
    era = str(era)
    if era == '2016-preVFP':
        lumi = 19667.812849099
    elif era == '2016-postVFP':
        lumi = 16977.701784453
    elif era == '2016':
        lumi = 35921.875594646  
    elif era == '2017':
        lumi = 41529.152060112  
    elif era == '2018':
        lumi = 59740.565201546  
    elif era == 'fullrun2':
        lumi = 138000.
    return lumi # pb


def getLuminosityForEraForRun(era, run):
    lumis = {#'2016': {},
             '2017': {'B':4.823, 'C':9.664, 'D':4.252, 'E':9.278, 'F':13.540},
             #'2018': {} 
             }
    return lumis[era][run]*1000 # pb 


def getLuminosityUncertainty():
    uncer =  {'uncorrelated'  : { 
                        '2016': 1.01,
                        '2017': 1.02,
                        '2018': 1.015
                        },
              'correlated_16_17_18': {
                        '2016': 1.006, '2017': 1.009, '2018': 1.020}, 
              'correlated_17_18': {
                        '2017': 1.006, '2018': 1.002 }
                  }
    return uncer


def get_SignalMassPoints(era, returnKeyMode= False, split_sig_reso_boo= False):
    
    points = {'gg_fusion': 
                { 'resolved': { 'HToZA': [], 'AToZH': [] },
                  'boosted' : { 'HToZA': [], 'AToZH': [] } 
                  },
              'bb_associatedProduction':
                { 'resolved': {'HToZA': [], 'AToZH': [] },
                  'boosted' : {'HToZA': [], 'AToZH': [] } 
                  },
            }

    base = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis'    
    with open(os.path.join(base, 'data/fullanalysisRunIISummer20UL_18_17_16_nanov9.yml')) as _f:
        plotConfig = yaml.safe_load(_f) 
    
    for f, cfg in plotConfig['samples'].items():
        
        thdm    = 'HToZA'
        split_f = f.split('_')
        
        if not (f.startswith('GluGluTo') or f.startswith('HToZATo2L2B') or f.startswith('AToZHTo2L2B')):
            continue
        if era !='fullrun2':
            if not era in cfg['era']:
                continue

        if split_f[1] == 'MA': thdm = 'AToZH'
        
        m0 = float(split_f[2].replace('p', '.'))
        m1 = float(split_f[4].replace('p', '.'))
        
        if split_sig_reso_boo:
            if m0 > 4*m1: regions = ['boosted']
            else: regions = ['resolved']
        else:
            regions = ['resolved', 'boosted']

        for region in regions:
            if 'GluGluTo' in f: 
                if not (m0, m1) in points['gg_fusion'][region][thdm]:
                    points['gg_fusion'][region][thdm].append( (m0, m1))
            else:
                if not (m0, m1) in points['bb_associatedProduction'][region][thdm]:
                    points['bb_associatedProduction'][region][thdm].append( (m0, m1))
    
    if returnKeyMode:
        otherFormatPoints = {}
        for mode in [ 'HToZA', 'AToZH']:
            otherFormatPoints[mode] = []
            for proc in [ 'gg_fusion', 'bb_associatedProduction']:
                for reg in ['resolved', 'boosted']:
                    otherFormatPoints[mode] += points[proc][reg][mode]
        return otherFormatPoints
    else:
        return points


def add_autoMCStats(datacard, threshold=0, include_signal=0, hist_mode=1):
    openFile=open(datacard, 'r')
    datacard_content = openFile.read()
    openFile.seek(0)
    
    for line in openFile.readlines():
        if 'bin ' in line:
            channels = line.split()
            break
    channels.remove( 'bin')
    
    add_autoMCStats = ""
    for channel in channels:
        add_autoMCStats +="{} autoMCStats {} {} {}\n".format(channel, threshold, include_signal, hist_mode)
    
    openFile=open(datacard, 'w')
    openFile.write(datacard_content + add_autoMCStats)
    openFile.close()
    return


def add_Correlation(datacard):
    openFile=open(datacard, 'r')
    
    datacard_content2 = ""
    for line in openFile.readlines():
        if 'lumi_uncorrelated_13TeV' in line:
            era = line.split()[0].split('_')[-1]
            lumi_uncorrelated = getLuminosityUncertainty(era)
            lumi_correlated   = getLuminosityUncertainty('fullrun2')['correlated_16_17_18'][era]
            line = line.replace(str(lumi_uncorrelated), str(lumi_correlated))
            line = line.replace('lumi_correlated_13TeV', 'lumi_uncorrelated_13TeV')
        datacard_content2 +=line +"\n"

    openFile=open(datacard, 'w')
    openFile.write(datacard_content2)
    openFile.close()
    return
