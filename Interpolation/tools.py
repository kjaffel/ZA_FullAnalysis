import yaml
import os
import sys
import glob 

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/')
import Constants as Constants


def get_idx_topave(do_fix, thdm):
    if thdm == 'HToZA':
        if do_fix == 'mH':
            return 1
        else:
            return 0
    elif thdm == 'AToZH':
        if do_fix == 'mA':
            return 0
        else:
            return 1

def get_keys_from_value(d, val):
        return [k for k, v in d.items() if v == val]

def mass_to_str(m, _p2f=True):
    if _p2f: m = "%.2f"%m
    return str(m).replace('.','p')

def get_lumi(year):
    era = '20'+year.replace('UL','')
    return Constants.getLuminosity(era)

def EraFromPOG(era):
    return '_UL'+era.replace('20','')

def get_signal_parameters(f):
    split_filename = f.replace('.root','').split('To2L2B_')[-1]
    m_heavy = split_filename.split('_')[1].replace('p', '.')
    m_light = split_filename.split('_')[3].replace('p', '.')
    return float(m_heavy), float(m_light)

def no_plotsYML(input, thdm, year):
    signal_grid = Constants.get_SignalMassPoints('fullrun2', returnKeyMode=False, split_sig_reso_boo=False)
    # more filter in case we can't find these points
    all_parameters = {}
    for prefix, prod in {'GluGluTo': 'gg_fusion', '': 'bb_associatedProduction'}.items():
        
        all_parameters[prod] = { 'resolved': [] , 'boosted': [] }
        for f in glob.glob(os.path.join(input, '*.root')):
            
            split_filename = f.split('/')[-1]
            if not split_filename.startswith('{}{}To2L2B_'.format(prefix, thdm)): 
                continue
            
            if year != "fullrun2":
                if not year in split_filename:
                    continue
            
            for reg in ['resolved', 'boosted']:
                m_heavy, m_light = get_signal_parameters(split_filename)
                
                if (m_heavy, m_light) in signal_grid[prod][reg][thdm] and not (m_heavy, m_light) in all_parameters[prod][reg]:
                    all_parameters[prod][reg].append( (m_heavy, m_light) )
    # resolved and boosted are the same points, no problem 
    return {'gg_fusion': all_parameters['gg_fusion']['resolved'], 
            'bb_associatedProduction': all_parameters['bb_associatedProduction']['resolved']}


def haddSignalFiles(inDir, outDir):
    SignalToHadd = {}
    for f in glob.glob(os.path.join(input, '*.root')):

        smp = f.split('/')[-1]
        if not smp.startswith('{}{}To2L2B_'.format(prefix, thdm)):
            continue
        
        resultsFile    = HT.openFileAndGet(os.path.join(inDir, smp), mode="READ")
        normalizedFile = HT.openFileAndGet(os.path.join(outDir, smp), "recreate")
        for hk in resultsFile.GetListOfKeys():
            hist  = hk.ReadObj()
            if not hist.InheritsFrom("TH1"):
                continue
            hist.Scale(smpScale)
            hist.Write()
            normalizedFile.Write()
        normalizedFile.Close()
        resultsFile.Close()

        key = smp.replace(f'_{year}.root')
        if not key in SignalToHadd.keys():
            SignalToHadd[key] = []
        SignalToHadd[key].append(split_filename)

    return 


class YMLparser:
    def get_masspoints(path, thdm):
        with open(os.path.join(path,'plots_ggH.yml')) as _f:
            plotConfig_ggH = yaml.load(_f, Loader=yaml.FullLoader)
        with open(os.path.join(path,'plots_bbH.yml')) as _f:
            plotConfig_bbH = yaml.load(_f, Loader=yaml.FullLoader)

        ggfusion= { 'HToZA': [], 'AToZH': [] }
        bb_associatedProduction = {'HToZA': [], 'AToZH': [] }
        
        files = plotConfig_ggH["files"]+ plotConfig_bbH["files"]
        for f in files:
            key = 'HToZA'
            if not f.startswith('GluGluTo') or f.startswith('HToZATo2L2B') or f.startswith('AToZHTo2L2B'):
                continue
            split_f = f.split('_')

            if split_f[1] == 'MA': key = 'AToZH'

            m0 = float(split_f[2].replace('p', '.'))
            m1 = float(split_f[4].replace('p', '.'))
            
            if 'GluGluTo' in f:
                if not (m0, m1) in ggfusion[key]:
                    ggfusion[key].append((m0, m1))
            else:
                if not (m0, m1) in bb_associatedProduction[key]:
                    bb_associatedProduction[key].append((m0, m1))
        # print( ggfusion )
        # print( bb_associatedProduction)
        return {'gg_fusion': ggfusion.get(thdm), 'bb_associatedProduction': bb_associatedProduction.get(thdm)}
