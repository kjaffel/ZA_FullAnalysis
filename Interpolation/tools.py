import yaml
import os

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


def mass_to_str(m, _p2f=False):
    if _p2f: m = "%.2f"%m
    return str(m).replace('.','p')


class YMLparser:
    def get_masspoints(path, thdm):
        with open(os.path.join(path,'plots.yml')) as _f:
            plotConfig = yaml.load(_f, Loader=yaml.FullLoader)

        ggfusion= { 'HToZA': [], 'AToZH': [] }
        bb_associatedProduction = {'HToZA': [], 'AToZH': [] }

        for f in plotConfig["files"]:
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
