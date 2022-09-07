import math
import yaml
import os, os.path

mass        = (609.21, 253.68)
r           = 'ggH'
region      = 'boosted'
taggerWP    = 'DeepDoubleBvLV2custom' 
taggerWP    = 'DeepCSVM'
era         = '2017'
year        = era.replace('20', '')
channel     = '$\mu^{+}\mu^{-}$'
process     = '$\splitline{%s: (m_{H}, m_{A})}{= %s GeV}$'%(r, str(mass))
#process    = f'{r}: (m_{{H}}, m_{{A}})= {mass}GeV'
nomet       = 'no $p_{T}^{miss}$ cut' # will be ignored 
cols        = ['DY', 'SM', 'others', 'ST', 'VV', 'ttbar', 'Data/MC', 'Tot. MC'] + [process]    
inDir       = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/forHIG/ul_2017_ver45'
plotit_yml  = os.path.join(inDir, 'plots.yml')


mH = "{:.2f}".format(mass[0])
mA = "{:.2f}".format(mass[1])

mH = str(mH).replace('.', 'p')
mA = str(mA).replace('.', 'p')

if r =='ggH':
    smp  = f'GluGluToHToZATo2L2B_MH_{mH}_MA_{mA}_tb_1p50_TuneCP5_13TeV_madgraph_pythia8_UL{year}.root'
elif r == 'bbH':
    smp = f'HToZATo2L2B_MH_{mH}_MA_{mA}_tb_20p00_TuneCP5_bbH4F_13TeV_madgraph_pythia8_UL{year}.root'

def get_cfg(plotit_yml):
    with open(plotit_yml) as file:
        cfg= yaml.safe_load(file)
    return cfg


def get_process(process):
    with open(f"{inDir}/yields_{era}.tex", 'r') as inf:
        for l in inf: 
            if 'Cat.' in l:
                catl = l.split('&')
            if process in l :
                procl = l.split('&')
        return catl, procl


def get_significance(y):
    S = y[-1].split('\pm')[0].replace('$', '') 
    B = y[-2].split('\pm')[0].replace('$', '')
    if '---' in S or '---' in B:
        return '---'
    else:
        S = float(S)
        B = float(B)
        signif = math.sqrt(2*( (S+B)*math.log(1+S/B) -S ))
        return '%.4f'%signif


def get_SignalCatEff(dict_yields):
    cfg = get_cfg(plotit_yml)
    print( f"Cat. & eff \\\\" )
    for i, (cat, y) in enumerate(dict_yields.items()):
        if not channel in cat:
            continue
        if nomet in cat:
            continue
        if '---' in y:
            continue
        signal_cat = cat.split(':')[0]
        Tot_pass      = y[-1].split('\pm')[0].replace('$', '')
        Tot_generated = cfg['files'][smp]["generated-events"]
        eff = float(Tot_pass)/float(Tot_generated)
        print( f"{signal_cat}")
        print( f'**pass: {Tot_pass}, generated: {Tot_generated}, Eff: {eff}')


dict_yields = {}
for i, process in enumerate(cols):
    catl, procl = get_process(process)
    for cat, y_proc in zip(catl, procl):
        y_proc = y_proc.strip()
        cat    = cat.strip()
        if cat !='Cat.':
            if not region in cat: 
                continue
            if not taggerWP in cat:
                continue
        if i == 0:
            dict_yields[cat] = [y_proc]
        else:
            dict_yields[cat].append(y_proc)


get_SignalCatEff(dict_yields)
print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")


cols +=['Significance \\\\'] 
print('Cat. & ' + ' & '.join(cols))
for i, (cat, y) in enumerate(dict_yields.items()):
    if not channel in cat:
        continue
    if nomet in cat:
        continue
    sigma = get_significance(y)
    y += [sigma]
    all_y = ' & '.join(y)
    cat = cat.replace('_', '\_')
    print(f"{cat} & {all_y} \\\\")



with open(f"{inDir}/yields_{era}.tex", 'r') as inf:
    with open(f"{inDir}/yields_{era}_formatted.tex", 'w+') as outf:
        for line in inf:
            
            if any( x in line for x in ['DY', 'SM', 'others', 'ST', 'VV', 'ttbar']):
                continue

            if '&' in line:
                newl = line.split('&')
                for col in newl:
                    outf.write(f'& {col.strip()}\n')
            else:
                outf.write(line)
