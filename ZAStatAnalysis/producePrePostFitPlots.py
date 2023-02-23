import sys, os, os.path
import glob 
import ROOT
import subprocess
import argparse


import Constants as Constants
logger = Constants.ZAlogger(__name__)

from numpy_hist import NumpyHist

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/')
import HistogramTools as HT


def CopyTH1F_to_TH1D(hist):
    if (hist == None):
        return None
    copyHist = ROOT.TH1D(str(hist.GetName()), hist.GetTitle(), hist.GetNbinsX(), hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
    return copyHist


def RedoPrePostfitShapesConversionForPlotIt(workdir, mode, poi_dir, tb_dir):
   
    for fit in ['fit_s', 'fit_b']:
        for rf in glob.glob(os.path.join(workdir, 'fit', mode, poi_dir, tb_dir, '*', 'plotIt_*', 'fit_shapes_*%s.root'%fit)):
            smp    = rf.split('/')[-1]
            dir    = rf.split(smp)[0]
            params = rf.split('/')[-3].split('_')
            heavy  = params[0].split('-')[0].replace('M', '')
            light  = params[1].split('-')[0].replace('M', '')
            prod   = '%sToZ%sTo2LB'%(heavy, light)
    
            redoConversion = ['python', 'utils/convertPrePostfitShapesForPlotIt.py', '-i',  '%s/%s'%(dir, smp), '-o', '%s/%s'%(dir, fit), '--signal-process', prod, '-n', 'dnn_scores']
            try:
                logger.info("running {}".format(" ".join(redoConversion)))
                subprocess.check_call(redoConversion)#, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                logger.error("Failed to run {}".format(" ".join(redoConversion)))



def reshapePrePostFitHistograms(workdir, mode, poi_dir, tb_dir):
    
    for fit in ['fit_s', 'fit_b']:
        for rf in  glob.glob(os.path.join(workdir, 'fit', mode, poi_dir, tb_dir, '*', 'plotIt_*', fit, '*.root')):
            cat    = rf.split('/')[-2]
            smp    = rf.split('/')[-1]
            p_out  = rf.split(smp)[0]
            
            outdir = os.path.join(p_out, 'reshaped')
            if not os.path.isdir(outdir):
                os.makedirs(outdir)

            if smp == 'plots.root':
                continue
            if smp.startswith('fit_shapes_'):
                continue
            #print( 'working on:', rf)
            inFile  = HT.openFileAndGet(rf)
            outFile = HT.openFileAndGet(f'{p_out}/reshaped/{smp}', "recreate")
            for hk in inFile.GetListOfKeys():
                
                cl = ROOT.gROOT.GetClass(hk.GetClassName())
                if not cl.InheritsFrom("TH1"):
                    continue
                histNm = hk.ReadObj().GetName()
                hk.ReadObj().SetDirectory(0)
                
                hist  = hk.ReadObj()
                #hist = CopyTH1F_to_TH1D(hk.ReadObj())
                
                nph = NumpyHist.getFromRoot(hist)
                #nph.setUnitaryBinWidth()
                nph.divideByBinWidth()
                newHist = nph.fillHistogram(hist.GetName())
                newHist.SetDirectory(0) 
                
                outFile.cd()
                newHist.Write()
            inFile.Close()
            outFile.Close()
            #print( 'Divide events by the bin width for', fit, smp)
        #print( "============="*10)


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


def runPlotIt_prepostFit(workdir, mode, era, unblind=False, reshape=False, poi_dir='2POIs_r', tb_dir='', rescale_to_za_br=None):

        base     = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/'
        re       = 'reshaped' if reshape else ''
        era      = era.replace('2016', '2016-') if 'VFP' in era else era
        lumi     = Constants.getLuminosity(era)
        hist_nm  = Constants.get_Nm_for_runmode( mode)
        
        xmax_dict= {'dnn': 1.0, 'mllbb': 1400., 'mbb': 1200} 
        channels = {
                    'ElEl'     : 'ee',
                    'MuMu'     : r'$\mu\mu$',
                    'MuEl'     : r'$\mu e$',
                    'MuMu_ElEl': r'$\mu\mu$ + ee',
                    'OSSF'     : r'$\mu\mu$ + ee',
                    'ElEl_MuEl':  'ee + r$\mu e$',
                    'MuMu_MuEl': r'$\mu\mu$ + $\mu e$',
                    'OSSF_MuEl': r'$\mu\mu$ + ee + $\mu e$',
                    'MuMu_ElEl_MuEl': r'($\mu\mu$ + ee) + $\mu e$',
                    }
        
        for fit in ['prefit', 'postfit']:
            for fit_what in ['fit_s', 'fit_b']:
                
                plotit_histos = glob.glob(os.path.join(workdir, 'fit/', mode, poi_dir, tb_dir, '*/', 'plotIt_*', fit_what, re))
                
                for cat_path in plotit_histos:
                    
                    split_path = cat_path.split('/')
                    if '' in split_path: split_path.remove('')
                    
                    if any(x in split_path for x in ['MuMu_ElEl', 'MuMu_MuEl', 'ElEl_MuEl', 'OSSF_MuEl', 'MuMu_ElEl_MuEl']):
                        print('sorry, merged categories are not supported...')
                        continue # this is need to be taken care in :: convertPrePostfitShapesForPlotIt.py TODO
                    
                    if reshape: p_out = split_path[-3]
                    else: p_out = split_path[-2]
                   
                    output = cat_path.split()[-1]
                    os.chdir(os.path.join(base, cat_path.split(output)[0]))
                    os.getcwd()
                    
                    inBlockSignal = False
                    prod       = p_out.split('_')[1] +'_'+p_out.split('_')[2]
                    flavor     = channels[p_out.split('_')[-1]]
                    region     = p_out.split('_')[-2]
                    reco       = p_out.split('_')[-3]
                    params     = cat_path.split('/plotIt_')[0].split('/')[-1].split('_')
                    heavy      = params[0].split('-')[0].replace('M', '')
                    light      = params[1].split('-')[0].replace('M', '')
                    process    = 'gg%s'%heavy if 'gg_fusion' in p_out else 'bb%s'%heavy
                    m_heavy    = '%.2f'%float(params[0].split('-')[1])
                    m_light    = '%.2f'%float(params[1].split('-')[1])
                    m_heavy    = m_heavy.replace('.00', '')
                    m_light    = m_light.replace('.00', '')
                    x_axis     = f'DNN_Output Z{light}' if mode =='dnn' else f'{mode}'
                    x_max      = xmax_dict[mode]
                    signal_smp = "#splitline{%s: (m_{%s}, m_{%s})}{= (%s, %s) GeV}"%(process, heavy, light, m_heavy, m_light)
                    tb         = float(tb_dir.split('_')[1]) if tb_dir !='' else None

                    if tb is None:
                        tb = 1.5 if 'gg_fusion' in p_out else 20.
                    xsc, xsc_err, br = Constants.get_SignalStatisticsUncer(float(m_heavy), float(m_light), process, f'{heavy}ToZ{light}', tb) 
                    
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
                                    outf.write("{}    blinded-range: [0.8, 1.0]\n".format('#' if unblind or 'MuEl' in p_out else ''))
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
                                elif '    Branching-ratio: ' in line:
                                    outf.write(f"{cs}    Branching-ratio: {br}\n")
                                elif '    type: signal' in line:
                                    outf.write(f"{cs}    type: signal\n")
                                elif '    line-type: 8' in line and inBlockSignal:
                                    outf.write(f"{cs}    line-type: 8\n")
                                elif '    line-width: 3' in line and inBlockSignal:
                                    outf.write(f"{cs}    line-width: 3\n")

                                elif '      text: mychannel' in line:
                                    outf.write(f"      text: {reco}-{region}, {flavor}\n")
                                elif '  histo-name:' in line:
                                    outf.write(f"  {hist_nm}_{fit}:\n")
                                elif '    - x_max' in line:
                                    outf.write(f"    - {x_max}\n")
                                #elif 'Label1' in line:
                                #    outf.write("        - {text: '%s -%s', position: [0.22, 0.895], size: 20}\n"%(reco, region))
                                #elif 'Lable2' in line:
                                #    outf.write("        - {text: '%s', position: [0.3, 0.7], size: 20}\n"%flavor)
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
    
    #RedoPrePostfitShapesConversionForPlotIt(workdir=options.inputs, mode=options.mode, poi_dir='2POIs_r', tb_dir='')
    
    if options.reshape: # will devide bin contents by the bin width
        reshapePrePostFitHistograms(workdir=options.inputs, mode=options.mode, poi_dir='2POIs_r', tb_dir='')
    
    runPlotIt_prepostFit(workdir          = options.inputs, 
                         mode             = options.mode, 
                         era              = options.era, 
                         unblind          = options.unblind, 
                         reshape          = options.reshape, 
                         poi_dir          = '2POIs_r', 
                         tb_dir           = '', 
                         rescale_to_za_br = options.rescale_to_za_br)

    #EventsYields(mH=500, mA=300, workdir=options.inputs, mode=options.mode, unblind=options.unblind)
