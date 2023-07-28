#!/usr/bin/env python3

import sys, os, os.path
import json
import glob 
import ROOT
import subprocess
import argparse


import Constants as Constants
logger = Constants.ZAlogger(__name__)

from numpy_hist import NumpyHist

os.path.abspath(os.path.join(os.path.dirname(__file__), '../bamboo_' ))
import HistogramTools as HT


def CopyTH1F_to_TH1D(hist):
    if (hist == None):
        return None
    copyHist = ROOT.TH1D(str(hist.GetName()), hist.GetTitle(), hist.GetNbinsX(), hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    return copyHist



def RedoPrePostfitShapesConversionForPlotIt(workdir, mode, poi_dir, tb_dir, era, submit_to_slurm=True):
    if submit_to_slurm:
        from CP3SlurmUtils.Configuration import Configuration
        from CP3SlurmUtils.SubmitWorker import SubmitWorker
        
        slurm_stageout = workdir.split('work__')[0]
        
        config = Configuration()
        config.sbatch_partition = 'Def'
        config.sbatch_qos = 'normal'
        config.cmsswDir = os.path.dirname(os.path.abspath(__file__))
        config.sbatch_chdir = os.path.join(slurm_stageout, 'work__UL%s'%era, 'slurm', 'plotit')
        config.stageoutDir = config.sbatch_chdir
        #config.sbatch_additionalOptions=['--exclude=mb-sky[002,005-014,016-018,020],mb-ivy220,mb-ivy213,mb-ivy212,mb-ivy211']
        #config.sbatch_additionalOptions=['--nodelist=mb-sky[002,005-014,016-018,020],mb-ivy220,mb-ivy213,mb-ivy212,mb-ivy211']
        config.sbatch_time  = '01:24:00'
        config.sbatch_memPerCPU = '1000'
        config.inputParamsNames = ['cmssw', 'inDir', 'outDir', 'prod', 'name']
        config.inputParams = []
        cmssw  = config.cmsswDir
        
        if os.path.exists(config.sbatch_chdir):
            logger.warning("Output directory {}/ , already exists !!".format(config.sbatch_chdir))
            exit()

    for i, fit in enumerate(['fit_s', 'fit_b']):
        for j, rf in enumerate(glob.glob(os.path.join(workdir, 'fit', mode, poi_dir, tb_dir, '*', 'plotIt_*', 'fit_shapes_*%s.root'%fit))):
            
            #if not  (i== 0 and j ==0):
            #    continue # test 
            smp    = rf.split('/')[-1]
            dir    = rf.split(smp)[0]
            params = rf.split('/')[-3].split('_')
            heavy  = params[0].split('-')[0].replace('M', '')
            light  = params[1].split('-')[0].replace('M', '')
            inDir  = '%s/%s'%(dir, smp)
            outDir = '%s/%s'%(dir, fit) 
            prod   = '%sToZ%sTo2LB'%(heavy, light)
            name   = 'dnn_scores' 

            if submit_to_slurm:
                config.inputParams.append([cmssw, inDir, outDir, prod, name])
            else:
                redoConversion = ['python', 'utils/convertPrePostfitShapesForPlotIt.py', '-i',  inDir, '-o', outDir, '--signal-process', prod, '-n', name]
                try:
                    logger.info("running {}".format(" ".join(redoConversion)))
                    subprocess.check_call(redoConversion)#, stdout=subprocess.DEVNULL)
                except subprocess.CalledProcessError:
                    logger.error("Failed to run {}".format(" ".join(redoConversion)))
    
    if submit_to_slurm :
        config.payload = \
            """
                pushd ${cmssw}
                echo "working on plotit root files :::"
                cat /etc/redhat-release
                python utils/convertPrePostfitShapesForPlotIt.py -i ${inDir} -o ${outDir} --signal-process ${prod} -n ${name}
            """
        submitWorker = SubmitWorker(config, submit=True, yes=True, debug=True, quiet=True)
        submitWorker()
    return 


def ProcessHistograms( hist):
    stat  = []
    uncer = []
    NBins = hist.GetNbinsX()
    for i in range(1, NBins + 1):
        content = hist.GetBinContent(i)
        error = hist.GetBinError(i)
        stat.append(content)
        uncer.append(error)
    return round(sum(stat), 2), round(sum(uncer),2)



def EventsYields(mH, mA, workdir, mode, unblind):
    processes= ['gg_fusion', 'bb_associatedProduction']
    regions  = ['resolved', 'boosted']
    flavours = ['ElEl', 'MuMu']
    fits     = ['prefit', 'postfit']
    
    collected_data = {}

    outdir = os.path.join(workdir, 'fit', mode, f'MH-{mH}_MA-{mA}')
    with open('%s/yields_tab.tex' % (outdir), 'w') as f:
        f.write(R'\begin{tabular}{@{}ccccc@{}} \toprule' + '\n')
        
        for flav in flavours:
            f.write(R'\hline' + '\n')
            f.write(R'\\' + '\n')
            lepflav  = '$ee$' if flav == 'ElEl' else '$\mu\mu$'
            f.write(R'{} '.format(lepflav) +R'Signal region & $nb=2$ -resolved & $nb=2$ -boosted & $nb=3$ -resolved & $nb=3$ -boosted\\ \midrule' + '\n')
            f.write(R'\\' + '\n')
            f.write(R'\hline' + '\n')
            f.write(R'\\' + '\n')

            collected_data[flav] = {}
            for process in processes:
                for reg in regions:
                    for fit in fits:
                        Total_bkg = 0.
                        Total_bkg_uncer = 0.
                        
                        collected_data[flav][f'{process}_{reg}_{fit}']= {'Total_bkg': []}
                        list_files = glob.glob(os.path.join(outdir, f'plotIt_{process}_{reg}_{flav}_fit_s', f'*_{fit}_histos.root'))
                        for rf in list_files: 
                            inFile  = HT.openFileAndGet(rf)
                            smpNm   = rf.split('/')[-1]
                            bkg     = smpNm.split(f'_{fit}')[0]
                            
                           # params     = rf.split('/')[-3].split('_')
                           # mH         = params[0].split('-')[1]
                           # mA         = params[1].split('-')[1]

                           # if not (mH =='500' and mA=='300'):
                           #     continue
                            if bkg == 'HToZATo2L2B':
                                bkg = '($m_{H}$, $m_{A}$) = (%s, %s) GeV'%(mH, mA)
                            
                            collected_data[flav][f'{process}_{reg}_{fit}'][bkg] = []
                            for hk in inFile.GetListOfKeys():
                                hist  = hk.ReadObj()
                                if '__' in hist.GetName():
                                    continue
                                print( hist.Integral() , hist.GetEntries())
                                yield_nom, yield_uncer = ProcessHistograms(hist)
                                
                                if not bkg == 'data_obs' or not bkg == 'HToZATo2L2B':
                                    Total_bkg += yield_nom
                                    Total_bkg_uncer += yield_uncer
                                
                                print( hist.GetName(), flav, bkg, f'{process}_{reg}_{fit}', yield_nom, yield_uncer)
                            collected_data[flav][f'{process}_{reg}_{fit}'][bkg] = [yield_nom, yield_uncer]
                        if list_files:
                            collected_data[flav][f'{process}_{reg}_{fit}']['Total_bkg'] = [round(Total_bkg,2), round(Total_bkg_uncer,2)]
            
            print( collected_data[flav] )
            collected_processes = collected_data[flav]['gg_fusion_resolved_prefit'].keys()
            
            for proc in ['data_obs', 'ttbar', 'SingleTop', 'DY', '($m_{H}$, $m_{A}$) = (%s, %s) GeV'%(mH, mA), 'Total_bkg']:
                if proc == 'data_obs' and not unblind: 
                    f.write(R'Data & - & - & - & - &  \\'+'\n')
                    continue
                if proc == 'Total_bkg':
                    Nm = f"Total bkg. pre-fit"
                else:
                    Nm = proc 

                tex_line  = '{} &'.format(Nm)
                tex_line2 = 'Total bkg. post-fit &'
                for cat in collected_data[flav].keys():
                    if not proc in collected_data[flav][cat].keys():
                        if 'prefit' in cat:
                            tex_line  += ' -  & '
                        else:
                            tex_line2 += ' -  & '
                        continue
                    y = collected_data[flav][cat][proc]
                    
                    if 'prefit' in cat:
                        if not y: 
                            tex_line  += ' -  & '
                            continue
                        tex_line += '{} $\pm$ {} & '.format(y[0], y[1])
                    else:
                        if not proc == 'Total_bkg': continue
                        if not y: 
                            tex_line2 += ' -  & '
                            continue
                        tex_line2 += '{} $\pm$ {} & '.format(y[0], y[1])

                f.write(R'{} \\'.format(tex_line) + '\n')
                #f.write(R'\\' + '\n')
            f.write(R'{} \\'.format(tex_line2) +'\n')
            f.write(R'\\' + '\n')
        f.write(R'\hline' + '\n')
        f.write(R'\bottomrule' + '\n')
        f.write(R'\end{tabular}' + '\n')



def WriteChannelOnPlotIt(data, channels):
    plotit_texts = {}
    for ch, cfg in data.items():
        ch_per_bin = cfg[0].split('_')[4:]
        ch_per_bin[-1] = channels[ ch_per_bin[-1]]
        plotit_texts[ch] = ch_per_bin
    print( plotit_texts)
    return plotit_texts



def runPlotIt_prepostFit(workdir, mode, era, unblind=False, reshape=False, poi_dir='2POIs_r', tb_dir='', rescale_to_za_br=None):

        base     = os.path.abspath(os.path.dirname(__file__))
        re       = 'reshaped' if reshape else ''
        dir_     = '../' if reshape else ''
        era      = era.replace('2016', '2016-') if 'VFP' in era else era
        lumi     = Constants.getLuminosity(era)
        hist_nm  = Constants.get_Nm_for_runmode(mode)
        
        # will devide bin contents by the bin width
        if options.reshape: 
            sys.path.append(f'{base}/utils')
            import convertPrePostfitShapesForPlotIt as shPlotIt 
            for fit in ['fit_s', 'fit_b']:
                output_dir = os.path.join(workdir, mode, poi_dir, tb_dir, '*', 'plotIt_*', fit)
                shPlotIt.reshapePrePostFitHistograms(output_dir)
        
        xmax_dict= {'dnn': 1.0, 'mllbb': 1400., 'mbb': 1200} 
        channels = {
                    'ElEl'      : 'ee',
                    'MuMu'      : '#mu#mu',
                    'MuEl'      : '#mu e',
                    'MuMu_ElEl' : '#mu#mu + ee',
                    'OSSF'      : '#mu#mu + ee',
                    'ElEl_MuEl' : 'ee + #mu e',
                    'MuMu_MuEl' : '#mu#mu + #mu e',
                    'OSSF_MuEl' : '#mu#mu + ee + #mu e',
                    'split_OSSF': '#mu#mu + ee',
                    'split_OSSF_MuEl': '#mu#mu + ee + #mu e',
                    'MuMu_ElEl_MuEl' : '#mu#mu + ee + #mu e',
                    }
        
        for fit in ['prefit', 'postfit']:
            for fit_what in ['fit_s', 'fit_b']:
                
                for cat_path in glob.glob(os.path.join(workdir, 'fit/', mode, poi_dir, tb_dir, '*/', 'plotIt_*', fit_what, re)):
                    
                    jsf = os.path.join(cat_path, dir_, 'channels.json')
                    f = open(jsf)
                    data  = json.load(f)
                    texts = WriteChannelOnPlotIt(data, channels)
                    
                    split_path = cat_path.split('/')
                    if '' in split_path: split_path.remove('')
                    
                    p_out  = split_path[-3]
                    output = cat_path.split()[-1]
                    os.chdir(os.path.join(base, cat_path.split(output)[0]))
                    os.getcwd()
                    
                    if '_nb2_' in p_out: nb = 'nb2'
                    elif '_nb3_' in p_out: nb = 'nb3'
                    elif 'nb2PLusnb3' in p_out: nb  = 'nb2+nb3'
                    
                    if 'resolved_boosted' in p_out: region = 'resolved_boosted'
                    elif 'resolved' in p_out: region = 'resolved'
                    elif 'boosted' in p_out : region = 'boosted'
                    
                    
                    f = p_out.split( region + '_')[-1]
                    flavor = channels[f]

                    inBlockSignal = False
                    prod       = '_'.join(p_out.split('_')[1:2])
                    params     = cat_path.split('/plotIt_')[0].split('/')[-1].split('_')
                    heavy      = params[0].split('-')[0].replace('M', '')
                    light      = params[1].split('-')[0].replace('M', '')
                    process    = 'gg%s'%heavy if 'gg_fusion' in p_out else 'bb%s'%heavy
                    m_heavy    = '%.2f'%float(params[0].split('-')[1])
                    m_light    = '%.2f'%float(params[1].split('-')[1])
                    m_heavy    = m_heavy.replace('.00', '')
                    m_light    = m_light.replace('.00', '')
                    x_axis     = f'DNN_Output Z{light}' if mode =='dnn' else f'{mode}'
                    x_max      = len(data.keys())
                    signal_smp = "#splitline{%s: (m_{%s}, m_{%s})}{= (%s, %s) GeV}"%(process, heavy, light, m_heavy, m_light)
                    tb         = float(tb_dir.split('_')[1]) if tb_dir !='' else None
                    
                    if tb is None:
                        tb = 1.5 if 'gg_fusion' in p_out else 20.
                    xsc, xsc_err, br = Constants.get_SignalStatisticsUncer(float(m_heavy), float(m_light), process, f'{heavy}ToZ{light}', tb) 
                    
                    print( p_out, flavor, nb, region, br , tb, 'unblind', unblind) 

                    with open(f"{base}/data/ZA_plotter_all_shapes_prepostfit_template.yml", 'r') as inf:
                        with open(f"{output}/{fit}_plots.yml", 'w+') as outf:
                            
                            for line in inf:
                                cs = ''
                                cb = ''
                                if 'luminosity-label' in line:
                                    if era =='fullrun2':
                                        outf.write("  luminosity-label: '%1$.0f fb^{-1} (13 TeV)'\n")
                                    else:
                                        outf.write("  luminosity-label: '%1$.2f fb^{-1} (13 TeV)'\n")
                                
                                elif '    blinded-range:' in line:
                                    outf.write("{}    blinded-range: [0.8, 1.]\n".format('#' if unblind or 'MuEl' in p_out else ''))
                                elif '    x-axis:' in line:
                                    outf.write(f"    x-axis: {x_axis}\n")
                                elif '  root: myroot_path' in line:
                                    outf.write(f"  root: {output}\n")
                                elif '  luminosity: mylumi' in line:
                                    outf.write(f"  luminosity: {lumi}\n")
                                
                                elif 'signal-prod_fit-type_histos.root:' in line:
                                    inBlockSignal = True
                                    signal = line.strip().replace('signal-prod', process).replace('fit-type', fit).replace(':','')
                                    if not os.path.exists( os.path.join(output, signal)): cs = '#'
                                    outf.write(f"{cs}  {signal}:\n")
                                    if rescale_to_za_br:
                                        outf.write(f"{cs}    branching-ratio: {br}\n")
                                
                                elif '_fit-type_histos.root:' in line:
                                    inBlockSignal = False
                                    bkg    = line.strip().replace('fit-type', fit).replace(':','')
                                    if not os.path.exists( os.path.join(output, bkg)): cb = '#'
                                    outf.write(f"{cb}  {bkg}:\n")
                                
                                elif '    type:' in line and not inBlockSignal:
                                    _Type  = line.strip().split(':')[-1]
                                    outf.write(f"{cb}    type: {_Type}\n")
                                
                                elif '    group:' in line and not inBlockSignal:
                                    _group = line.strip().split(':')[-1]
                                    outf.write(f"{cb}    group: {_group}\n")
                                elif '    legend: mysignal' in line:
                                    outf.write(f"{cs}    legend: '{signal_smp}'\n")
                                elif '    type: signal' in line:
                                    outf.write(f"{cs}    type: signal\n")
                                elif '    line-type: 8' in line and inBlockSignal:
                                    outf.write(f"{cs}    line-type: 8\n")
                                elif '    line-width: 3' in line and inBlockSignal:
                                    outf.write(f"{cs}    line-width: 3\n")

                                elif 'myLabel' in line:
                                    shift = 1/(x_max+1.)
                                    s = 12 if x_max >7 else 15 
                                    x = shift
                                    if x_max ==8:
                                        shift = 0.1
                                        x = 0.18
                                    if x_max ==5:
                                        x = 0.18
                                    for i, t in enumerate(texts.values()):
                                        outf.write(f"    - position: [{x}, 0.4]\n")
                                        outf.write("      text: '#splitline{%s, %s}{%s}'\n"%(t[0],t[1],t[2]))
                                        outf.write(f"      size: {s}\n")
                                        x += shift
                                        #outf.write(f"        - {text: '{t}', position: [[{x+1}, 10e-2]}\n")
                                elif '      text: mychannel' in line:
                                    outf.write("      text: '#splitline{%s, %s}{%s}'\n"%(nb, region.replace('_', '+'), flavor))
                                elif '  histo-name:' in line:
                                    outf.write(f"  {hist_nm}_{fit}:\n")
                                elif '    - x_max' in line:
                                    outf.write(f"    - {x_max}\n")
                                elif '  - fit-type' in line:
                                    outf.write("  - {}\n".format(fit))
                                else:
                                    outf.write(line)
                    
                    plotitCmd = ["/home/ucl/cp3/kjaffel/bamboodev/plotIt/plotIt", "-o", output, "--", f"{output}/{fit}_plots.yml"]
                    try:
                        logger.info("running {}".format(" ".join(plotitCmd)))
                        subprocess.check_call(plotitCmd)#, stdout=subprocess.DEVNULL)
                        print(f' plot saved in :: {cat_path}/{hist_nm}_{fit}.png')
                        print(f' plot saved in :: {cat_path}/{hist_nm}_{fit}_logy.png')
                    except subprocess.CalledProcessError:
                        logger.error("Failed to run {0}".format(" ".join(plotitCmd)))
                    print( "===============" *8)
                os.chdir(base)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PreFit/PostFit Producer')
    parser.add_argument('-i', '--inputs', action='store', required=True, default=None, 
                help='Path to work dir ( output given when running prepareShapesAndCards.py script with arg --method fit )')
    parser.add_argument('-m', '--mode', action='store', required=False, default='dnn', choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'mbb', 'mllbb', 'ellipse', 'dnn'], 
                help='posfit plots produced for one of these mode')
    parser.add_argument('--era', action='store', required=True, default=None, choices=['2016', '2016preVFP', '2016postVFP', '2017', '2018', 'fullrun2'], 
                help='data taking year')
    parser.add_argument('--unblind', action='store_true', default=False, 
                help='unblind data in dnn score template')
    parser.add_argument('--reshape', action='store_true', default=False, 
                help='bin histograms will be divide by the bin width')
    parser.add_argument('-r', '--rescale-to-za-br', action='store_true', dest='rescale_to_za_br',
                help='If flagged True, limits in HToZA mode will be x to BR( Z -> ll) x BR(A -> bb ) x (H -> ZA)')

    options = parser.parse_args()
   
    ## if you will redo this step on slurm, you will have to wait until jobs finish before running func below :: runPlotIt_prepostFit
    """
    RedoPrePostfitShapesConversionForPlotIt(workdir         = options.inputs, 
                                            mode            = options.mode, 
                                            poi_dir         = '2POIs_r', 
                                            tb_dir          = '', 
                                            era             = options.era,
                                            submit_to_slurm = True )
    """
    runPlotIt_prepostFit(workdir          = options.inputs, 
                         mode             = options.mode, 
                         era              = options.era, 
                         unblind          = options.unblind, 
                         reshape          = options.reshape, 
                         poi_dir          = '2POIs_r', 
                         tb_dir           = '', 
                         rescale_to_za_br = options.rescale_to_za_br)
    #EventsYields(mH=379, mA=54.59, workdir=options.inputs, mode=options.mode, unblind=options.unblind)
