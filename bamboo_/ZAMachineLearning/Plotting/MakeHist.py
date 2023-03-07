import os
import sys
import argparse
import glob
import logging
import copy
import yaml
import pprint
import traceback

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = 2000 #[ROOT.kPrint, ROOT.kInfo , kWarning, kError, kBreak, kSysError, kFatal]

import Classes
from Classes import ProcessYAML, Plot_TH1, Plot_TH2, Plot_Ratio_TH1, Plot_Multi_TH1, Plot_ROC, Plot_Multi_ROC
from Classes import LoopPlotOnCanvas, MakeROCPlot, MakeMultiROCPlot  # functions


def writeyaml(proc, reg, heavy, light, m0, m1, cut, isResolved, isBoosted, isggH, isbbH):
    outdir= f"tpl-tempalte/rocs_for_masses/{proc}_{reg}" 
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    
    with open(f"tpl-tempalte/rocs_for_masses/ROCMulti_mH_xxx_mA_xxx.yml.tpl", 'r') as inf:
        with open(f"{outdir}/ROCMulti_m{heavy}_{m0}_m{light}_{m1}.yml.tpl", 'w+') as outf:
            for line in inf:
                if 'ROC_mH_xxx_mA_xxx:' in line:
                    outf.write(f'ROC_m{heavy}_{m0}_m{light}_{m1}:\n')
                elif '  title : Mass points $M_{H}=xxx \ GeV$ and $M_{A}=xxx \ GeV$' in line:
                    p0 = str(m0).replace('.00', '').replace('.0', '')
                    p1 = str(m1).replace('.00', '').replace('.0', '')
                    outf.write(f'  title : ( $M_{{}}$, $M_{{}}$)= ( {{}}, {{}}) GeV\n'.format(heavy, light, p0, p1))
                elif '    - P($H\rightarrow ZA$ | x,$\theta$)' in line:
                    outf.write(f'    - P(${heavy}\rightarrow Z{light}$ | x,$\theta$)\n')
                elif "  cut : 'mH==xxx & mA==xxx'" in line:
                    outf.write(f"  cut : 'm{heavy}=={int(m0)} & m{light}=={int(m1)} & {cut}'\n")
                else:
                    outf.write(line)


def createYmlTemplate(ROC, plotter_p):
    plotter_p = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/skims_nanov9/ul_fullrun2___nanov9__ver4/'

    with open(os.path.join(plotter_p, 'plots.yml')) as _f:
            plotConfig = yaml.load(_f, Loader=yaml.FullLoader)

    allmasses = {'gg_fusion':{ 'HToZA': [], 'AToZH': [] },
                 'bb_associatedProduction': {'HToZA': [], 'AToZH': [] } }
    allROC = []
    for f in plotConfig["files"]:
        key   = 'HToZA'
        heavy = 'H'
        light = 'A'
        isResolved = False
        isBoosted  = False
        if not (f.startswith('GluGluTo') or f.startswith('HToZATo2L2B') or f.startswith('AToZHTo2L2B')):
            continue
        split_f = f.split('_')

        if split_f[1] == 'MA': 
            key   = 'AToZH'
            heavy = 'A'
            light = 'H'

        m0 = float(split_f[2].replace('p', '.'))
        m1 = float(split_f[4].replace('p', '.'))
        
        if 'GluGluTo' in f:
            if (m0, m1) not in  allmasses['gg_fusion'][key]:
                allmasses['gg_fusion'][key].append( (m0, m1))
        else:
            if (m0, m1) not in allmasses['gg_fusion'][key]:
                allmasses['bb_associatedProduction'][key].append( (m0, m1))
    
    for proc, dfm in allmasses.items():
        isggH = False
        isbbH = False
        if proc == 'gg_fusion': isggH = True
        else: isbbH = True
        for k, lfm in dfm.items():
            heavy = k[0]
            light = k[-1]
            for (m0,m1) in lfm:
                isBoosted  = False
                isResolved = False
                
                if isggH: cut = 'isggH'
                elif isbbH: cut = 'isbbH'
                if m0 > 4*m1: 
                    isBoosted = True
                    reg  = 'boosted'
                    cut += ' & isBoosted'
                else: 
                    isResolved =True
                    reg = 'resolved'
                    cut += ' & isResolved'
                writeyaml(proc, reg, heavy, light, m0, m1, cut, isResolved, isBoosted, isggH, isbbH)
                outdir= f"tpl-tempalte/rocs_for_masses/{proc}_{reg}"
                allROC.append(
                    ROC(tpl        = f"{outdir}/ROCMulti_m{heavy}_{m0}_m{light}_{m1}.yml.tpl",
                        class_name = 'Plot_Multi_ROC',
                        def_name   = 'MakeMultiROCPlot',
                        plot_name  = f'ROC_{k}_{proc}_{reg}_m{heavy}_{m0}_m{light}_{m1}') 
                    )
    return allROC

def main():
    parser = argparse.ArgumentParser(description='From given set of root files, make different histograms in a root file')
    parser.add_argument('-m','--model', action='store', required=True, type=str, default='',
                    help='NN model to be used')
    parser.add_argument('-v','--verbose', action='store_true', required=False, default=False,
                    help='Show DEGUG logging')
    opt = parser.parse_args() 
    
    if opt.verbose:
        logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s') 
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    subdir = glob.glob(os.path.join(opt.model, '*_isbest_model'))
    subdir_nm = subdir[0].split('/')[-1]
    
    logging.info('Taking inputs from %s'%opt.model)
    
    # For each directory, put the path in dict the value is the list of histograms #
    class Plots():
        def __init__(self,name,override_params):
            self.name = name                            # Name of the subdir
            self.path = os.path.join(opt.model,name)    # Full path to files
            self.override_params = override_params      # Parameters to override in the configs
            self.list_histo = []                        # List of histograms to be filled

    # Select template #
    class Template:
        def __init__(self,tpl,class_name):
            self.tpl = tpl                          # Template ".yml.tpl" to be used
            self.class_name = class_name            # Name of one of the class to use (TH1,TH2,...)

    # Select template #
    class ROC:
        def __init__(self,tpl,class_name,def_name,plot_name):
            self.tpl = tpl                          # Template ".yml.tpl" to be used containing all the ROC curves parameters (they will all be plotted in the same figure)
            self.class_name = class_name            # Name of one of the class to use (ROC or multiROC)
            self.def_name   = def_name              # Name of of the processing function 
            self.plot_name  = plot_name             # Name of the plot -> .png
            self.list_instance = []
        def AddInstance(self,instance):
            self.list_instance.append(instance) # Contains the ROC configs listed in the tpl file
        def clearInstance(self):
            self.list_instance = []

    plotter_p = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/skims_nanov9/ul_fullrun2___nanov9__ver4/'
    allROC = createYmlTemplate(ROC, plotter_p)
    
    #///////////////      TO BE MODIFIED BY USER       ////////////////
    list_plots = [
                    Plots(name = f'{subdir_nm}',override_params = {}), ]
    templates  = [
                    Template(tpl = 'tpl-tempalte/TH1_ZA_template.yml.tpl',class_name = 'Plot_TH1'),
                    Template(tpl = 'tpl-tempalte/TH2_ZA_template.yml.tpl',class_name = 'Plot_TH2'),
                    Template(tpl = 'tpl-tempalte/TH1Multi_ZA_template.yml.tpl',class_name = 'Plot_Multi_TH1'),
                    Template(tpl = 'tpl-tempalte/TH1Ratio_ZA_template.yml.tpl',class_name = 'Plot_Ratio_TH1'), ]

    rocs       = [  ROC(tpl        = 'tpl-tempalte/ROCMulti_class_learning_weight.yml.tpl',
                        class_name = 'Plot_Multi_ROC',
                        def_name   = 'MakeMultiROCPlot',
                        plot_name  = 'Multiclass_learning'),
                    ROC(tpl        = 'tpl-tempalte/ROCMulti_all_masses.yml.tpl',
                        class_name = 'Plot_Multi_ROC',
                        def_name   = 'MakeMultiROCPlot',
                        plot_name  = 'ROC_ZA_all_masses'), 
                    #ROC(tpl        = f"tpl-tempalte/rocs_for_masses/gg_fusion_resolved/ROCMulti_mH_500.0_mA_300.0.yml.tpl",
                    #    class_name = 'Plot_Multi_ROC',
                    #    def_name   = 'MakeMultiROCPlot',
                    #    plot_name  = f'ROC_HToZA_gg_fusion_resolved_mH_500.0_mA_300.0')
                    ] #+ allROC
                    
    #///////////////      TO BE MODIFIED BY USER       ////////////////
    # Make the output dir #
    OUTPUT_PATH = os.path.join(opt.model,'plots')
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    yaml_path = opt.model.replace('/model', '')
    # Loop over the plots #
    for obj in list_plots:
        logging.info('Starting Plotting from %s subdir'%obj.name)
        files = sorted(glob.glob(obj.path+'/*.root'))
        if len(files) == 0:
            logging.error('Could not find %s at %s'%(obj.name,obj.path))
       # Instantiate all the ROCs #
        for roc in rocs:
            logging.debug('ROC template "%s" -> Class "%s" and process function %s '%(roc.tpl, roc.class_name, roc.def_name))
            roc.clearInstance()
            YAML = ProcessYAML(yaml_path, roc.tpl) # Contain the ProcessYAML objects
            YAML.Particularize(obj.name)
            for name,config in YAML.config.items():
                class_ = getattr(Classes, roc.class_name)
                logging.info('\tInitializing ROC %s'%(name))
                logging.debug('\t ... Containing')
                logging.debug(pprint.pformat(config))
                instance = class_(**config)
                roc.AddInstance(instance)
        # Loop over files #
        for f in files:
            fullname = os.path.basename(f).replace('.root','')
            logging.info('Processing weights from %s'%(fullname+'.root'))
            if fullname.startswith('DY'):
                filename = 'Drell-Yan'
            elif fullname.startswith('TT'):
                filename = 't#bar{t}'
            elif fullname.startswith('HToZA'):
                filename = 'Signal'
            else:
                filename = fullname
            ##############  ROC  section ################ 
            for roc in rocs:
                for inst_roc in roc.list_instance:
                    try:
                        valid = inst_roc.AddToROC(f)
                        if valid:
                            logging.info('\tAdded to ROC %s'%(inst_roc.title))
                    except Exception as e:
                        logging.warning('Could not add to ROC due to "%s"'%(e))
                        traceback.print_exc()
            ##############  HIST section ################ 
            # Loop over the templates #
            for template in templates: 
                logging.debug('Hist template "%s" -> Class "%s"'%(template.tpl, template.class_name))
                list_config = [] # Will contain the dictionaries of parameters
                YAML   = ProcessYAML(yaml_path, template.tpl) # Contain the ProcessYAML objects
                params = {**{'filepath':f,'filename':filename},**obj.override_params}
                # Get the list of configs #
                YAML.Particularize(fullname)
                YAML.Override(params)
                # loop over the configs #
                for name,config in YAML.config.items():
                    try:
                        class_ = getattr(Classes, template.class_name)
                        logging.info('\tPlot %s'%(name))
                        instance = class_(**config)
                        instance.MakeHisto()
                        obj.list_histo.append(instance)
                    except Exception as e:
                        logging.warning('Could not plot %s due to "%s"'%(name,e))
                        traceback.print_exc()
        # Process ROCs #
        for roc in rocs:
            for inst_roc in roc.list_instance:
                try:
                    logging.info('\tProcessed ROC %s'%(inst_roc.title))
                    inst_roc.ProcessROC() 
                except Exception as e:
                    logging.warning('Could not process ROC due to "%s"'%(e))
                    traceback.print_exc()
        # Make ROCs graphs #
        for roc in rocs:
            try:
                def_ = getattr(Classes, roc.def_name)
                def_(roc.list_instance,name=os.path.join(OUTPUT_PATH,roc.plot_name+'_'+obj.name))
            except Exception as e:
                logging.warning('Could not plot ROC due to "%s"'%(e))
                traceback.print_exc()
    # Save histograms #
    for obj in list_plots:
        PDF_name = os.path.join(OUTPUT_PATH,obj.name) 
        if len(obj.list_histo) != 0:
            LoopPlotOnCanvas(PDF_name,obj.list_histo)
    logging.info("All Canvas have been printed")

if __name__ == "__main__":
    main()
