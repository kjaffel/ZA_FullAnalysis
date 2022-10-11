import sys
import os, os.path
import yaml
import ROOT
import json
import glob
import subprocess
import re, hashlib
import shutil

from cppyy import gbl

import Constants as Constants
logger = Constants.ZAlogger(__name__)


sys.dont_write_bytecode  = True
splitTTbarUncertBinByBin = False



def openFileAndGet(path, mode="read"):
    """Open ROOT file in a mode, check if open properly, and return TFile handle."""
    tf = ROOT.TFile.Open(path, mode)
    if not tf or not tf.IsOpen():
        raise Exception("Could not open file {}".format(path))
    return tf


def readRecursiveDirContent(content, currTDir, resetDir=True):
    """
    Fill dictionary content with the directory structure of currTDir.
    Every object is read and put in content with their name as the key.
    Sub-folders will define sub-dictionaries in content with their name as the key.
    """
    if not currTDir.InheritsFrom("TDirectory") or not isinstance(content, dict):
        return

    # Retrieve the directory structure inside the ROOT file
    currPath = currTDir.GetPath().split(':')[-1].split('/')[-1]

    if currPath == '':
        # We are in the top-level directory
        thisContent = content
    else:
        thisContent = {}
        content[currPath] = thisContent

    listKeys = currTDir.GetListOfKeys()

    for key in listKeys:
        obj = key.ReadObj()
        if obj.InheritsFrom("TDirectory"):
            print("Entering sub-directory {}".format(obj.GetPath()))
            readRecursiveDirContent(thisContent, obj)
        else:
            name = obj.GetName()
            if '__' in name:
                continue
            thisContent[name] = obj
            if resetDir:
                obj.SetDirectory(0)


def CMSNamingConvention(origName=None, era=None, process=None):
    ## see https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/HiggsCombinationConventions
    jerRegions = [ "barrel", "endcap1", "endcap2lowpt", "endcap2highpt", "forwardlowpt", "forwardhighpt" ]
    era   = era.replace('-', '')
    newEra  = '2016' if 'VFP' in era else era 

    other = {
        # uncorrelated
        #'btagSF_deepCSV_subjet_fixWP_light' : "CMS_btag_subjet_light_%s"%era,
        #'btagSF_deepCSV_subjet_fixWP_heavy' : "CMS_btag_subjet_heavy_%s"%era,
        #'btagSF_deepJet_fixWP_light'        : "CMS_btag_light_%s"%era,
        #'btagSF_deepJet_fixWP_heavy'        : "CMS_btag_heavy_%s"%era,
        'unclustEn'                         : "CMS_UnclusteredEn_%s"%era,        
        'jesHEMIssue'                       : "CMS_HEM_%s"%era, 
        'HLTZvtx'                           : "CMS_HLTZvtx_%s"%era,
        'elel_trigSF'                       : "CMS_elel_trigSF_%s"%newEra,
        'mumu_trigSF'                       : "CMS_mumu_trigSF_%s"%newEra,
        'muel_trigSF'                       : "CMS_muel_trigSF_%s"%newEra,
        'mu_trigger'                        : "CMS_mu_trigger_%s"%newEra,
        
        # correlated
        'pileup'            : "CMS_pileup",
        'L1PreFiring'       : "CMS_L1PreFiring",
        'elid_medium'       : "CMS_eff_elid",
        'lowpt_ele_reco'    : "CMS_eff_elreco_lowpt",
        'highpt_ele_reco'   : "CMS_eff_elreco_highpt",
        'muid_medium'       : "CMS_eff_muid",
        'muiso_tight'       : "CMS_eff_muiso",

        }
   
    # remove mass _MX-... duplicate in the datacards 
    if process:
        process = process.split('_')[0]
    
    # theory 
    theo_perProc = {"qcdScale": "QCDscale_%s"%process, 
                    "qcdMuF"  : "qcdMuF_%s"%process, 
                    "qcdMuR"  : "qcdMuR_%s"%process, 
                    "psISR"   : "ISR_%s"%process, 
                    "psFSR"   : "FSR_%s"%process, 
                    "pdf"     : "pdf_%s"%process}

    if origName in other:
        return other[origName]
    elif origName in theo_perProc:
        return "{}".format(theo_perProc[origName])
    
    # btag;  good names do  not overwrite
    elif 'btag' in origName:
        return 'CMS_'+origName

    # DY reweighting, correlated across year
    elif 'DYweight_' in origName:
        return origName

    # jes 
    elif origName.startswith("jes"):
        return "CMS_scale_j_{}".format(origName[3:])
    elif origName.startswith("jms"):
        return "CMS_scale_fatjet_{}".format(newEra)
    
    # jer
    elif origName.startswith("jer"):
        if len(origName) == 3:
            return "CMS_res_j_Total_{}".format(newEra)
        else:
            jerReg = jerRegions[int(origName[3:])]
            return "CMS_res_j_{}_{}".format(jerReg, newEra)
    elif origName.startswith("jmr"):
        return "CMS_res_fatjet_{}".format(newEra)
    
    # unkown 
    else:
        return origName+"_{}".format(era)


def get_hist_from_key(keys=None, key=None):
    h = keys.get(key, None)
    if h:
        return h.ReadObj()
    return None


def get_listofsystematics(files, flavorCat):
    
    flavor = flavorCat.split('_')[-1]
    cat    = None
    if len( flavorCat.split('_') ) >= 2:
        cat    = flavorCat.split('_')[-2]
    
    muel  = [ 'elmu_trigSF', 'muel_trigSF', 'mu_trigger']
    mumu  = [ 'muid_medium', 'mumu_trigSF', 'muiso_tight', 'mu_trigger']
    elel  = [ 'elid_medium', 'lowpt_ele_reco', 'elel_trigSF', 'highpt_ele_reco']
    ll    = [ 'mumu_trigSF', 'elel_trigSF']

    systematics = []
    for f in files:
        open_f = ROOT.TFile(f)
        avoid  = []
        for key in open_f.GetListOfKeys():
            if not 'TH1' in key.GetClassName():
                continue
            if not '__' in key.GetName():
                continue
            if not 'down' in key.GetName():
                continue
            if 'Jet_mulmtiplicity' in key.GetName(): # nm of histogram contain __ by mistake, confused with sys ignore until i fix it again in the new vers 
                continue

            syst = key.GetName().split('__')[1].replace('up','').replace('down','')
            syst = syst.replace('pile', 'pileup')
            
            if   flavor == 'MuMu': avoid += elel + muel 
            elif flavor == 'ElEl': avoid += mumu + muel 
            elif flavor == 'OSSF': avoid += muel 
            else: avoid += ll
            
            if cat == 'boosted':
                avoid += [ 'btagSF_deepJet_fixWP', 'DYweight_resolved_'] 
            elif cat == 'resolved':
                avoid += [ 'btagSF_deepCSV_subjet_fixWP', 'DYweight_boosted_', 'jmr', 'jms'] 
            
            if syst not in systematics:
                if not any(x in syst for x in avoid):
                    systematics.append(syst)
        
        open_f.Close()
    return systematics


def zeroNegativeBins(h):
    for i in range(1, h.GetNbinsX() + 1):
        if h.GetBinContent(i) < 0.:
            h.SetBinContent(i, 0.)
            h.SetBinError(i, 0.)


def EraFromPOG(era):
    return '_UL'+era.replace('20','')


def ConfigurationEra(smp):                    
    if 'preVFP' in smp:
        newEra = '2016-preVFP'
    elif 'postVFP' in smp:
        newEra = '2016-postVFP'
    elif '_UL17' in smp:
        newEra = '2017'
    elif '_UL18' in smp:
        newEra = '2018'
    return newEra


def get_method_group(method):
    if method == 'fit':
        return 'fit'
    elif method == 'impacts':
        return 'pulls-impacts'
    elif method == 'generatetoys':
        return 'generatetoys-data'
    elif method == 'signal_strength':
        return 'signal_strength'
    elif method == 'pvalue':
        return 'pvalue-significance'
    elif method == 'goodness_of_fit':
        return 'goodness_of_fit_test'
    elif method == 'asymptotic':
        return 'asymptotic-limits'
    elif method == 'hybridnew':
        return 'hybridnew-limits'


def get_combine_method(method):
            # --rMin -50 --rMax 50 --robustFit=1' 
            # --X-rtd MINIMIZER_analytic'
            # --X-rtd MINIMIZER_no_analytic 
    if method == 'fit':
        return '-M FitDiagnostics --rMax 20'   
    elif method == 'asymptotic':
        return '-M AsymptoticLimits --rMax 20' 
    elif method == 'impacts':
        return '-M Impacts --rMin -20 --rMax 20' 
    elif method == 'hybridnew':
        return '-H Significance -M HybridNew --frequentist --testStat LHC --fork 10'
    elif method == 'signal_strength':
        return '-M MultiDimFit --rMin -3 --rMax 3'
    elif method == 'pvalue':
        return '-M Significance'


def get_Observed_HIG_18_012(m):
    obs = { 'MH_1000_MA_200': 21.4, # fb
            'MH_1000_MA_500': 8.20,
            'MH_200_MA_50'  : 157, 
            'MH_200_MA_100' : 161,
            'MH_250_MA_50'  : 89.1, 
            'MH_250_MA_100' : 82.3,
            'MH_300_MA_50'  : 43.4,
            'MH_300_MA_100' : 97.1,
            'MH_300_MA_200' : 94.9,
            'MH_500_MA_50'  : 37.9, 
            'MH_500_MA_100' : 16.2, 
            'MH_500_MA_200' : 32.0,
            'MH_500_MA_300' : 46.9,
            'MH_500_MA_400' : 74.8,
            'MH_650_MA_50'  : 71.9,
            'MH_800_MA_50'  : 95.6,
            'MH_800_MA_100' : 20.8,
            'MH_800_MA_200' : 27.5,
            'MH_800_MA_400' : 8.96,
            'MH_800_MA_700' : 27.0, }
    if m in obs.keys():
        return obs[m]/1000. # pb 
    else:
        return None


def get_normalisationScale(inDir=None, method=None, era=None):
    dict_ = {}
    wEra  = EraFromPOG(era)
    plotit_yml= True
    
    bamboo_p    = inDir.replace('results', '')
    plotter_p   = inDir.split('work__UL')[0]
    yaml_file   = os.path.join(bamboo_p, 'plots.yml')
    
    # just make things faster reading an yml file, rather than opening hundred of root files
    # plotit cmd get killed when there are lots of files to read and does not give the plots.yml
    # this is just a workaround !
    if not os.path.exists(yaml_file):
        yaml_file = os.path.join(plotter_p, 'work_{}/plots.yml'.format(wEra))
    else:
        shutil.copyfile( os.path.join(bamboo_p, yaml_file), os.path.join(plotter_p, yaml_file))
    
    if not os.path.exists(yaml_file):
        yaml_file = os.path.join(plotter_p, 'config_fullrun2.yml')
    
    if not os.path.exists(yaml_file):
        yaml_file = os.path.join(plotter_p, 'config_{}.yml'.format(era))
    
    if not os.path.exists(yaml_file):
        yaml_file = os.path.join(plotter_p, 'plots.yml')
    
    if os.path.exists(yaml_file):
        print( 'reading root files configuration from : ', yaml_file)
        with open(yaml_file) as file:
            scalefactors = yaml.safe_load(file)
        return scalefactors
    else:
        yaml_file  = 'data/fullanalysisRunIISummer20UL_18_17_16_nanov9.yml'
        plotit_yml = False
     
    try:
        with open(yaml_file, 'r') as inf:
            config = yaml.safe_load(inf)
    except yaml.YAMLError as exc:
        logger.error('failed reading file : %s '%exc)
    
    for i, inPath in enumerate(glob.glob(os.path.join(inDir, "*.root"))): 
        smp   = inPath.split('/')[-1]
        smpNm = smp.split('.root')[0]
        if smp.startswith('__skeleton__'):
            continue

        if era != "fullrun2":
            if not wEra in smp:
                continue
        
        if i == 0: dict_['files'] = {}
        
        print( "working on scale factors:: ", smp)
        smpScale = None
        sumW     = None
        do_SumW  = True

        if plotit_yml:
            smpCfg   = config['files'][smp]
            sumW     = smpCfg["generated-events"]
            lumi     = config["configuration"]["luminosity"][smpCfg["era"]]
            dict_["configuration"] = config["configuration"]["luminosity"]
        else:
            smpCfg   = config['samples'][smpNm]
            lumi     = config["eras"][smpCfg["era"]]["luminosity"]
            dict_["configuration"] = {"luminosity": {    
                    '2016-postVFP': 16977.701784453,
                    '2016-preVFP': 19667.812849099,
                    '2017': 41529.152060112,
                    '2018': 59740.565201546}}

            if smpCfg.get("type")== "mc" or smpCfg.get("type")=="signal":
                if do_SumW:
                    inFile = openFileAndGet(inPath)
                    hists  = dict()
                    readRecursiveDirContent(hists, inFile, resetDir=False)
                    runsTree = hists['Runs']
                    sumW     = sum([entry.genEventSumw for entry in runsTree])
                    inFile.Close()
        
        if smpCfg.get("type") == "mc":
            smpScale = lumi * smpCfg["cross-section"]/ sumW
            
            dict_['files'][smp] = { 'era'  : smpCfg["era"], 
                                    'lumi' : lumi, 
                                    'type' : 'mc', 
                                    'group': smpCfg["group"],
                                    'scale': smpScale, 
                                    'cross-section': smpCfg["cross-section"], 
                                    'generated-events': sumW, 
                                    'branching-ratio': None 
                                    }
             
        elif smpCfg.get("type") == "signal":
            if not do_SumW:
                sumW = None
                smpScale = None
            else:
                smpScale  = lumi / sumW
                smpScale *= smpCfg["cross-section"] * smpCfg["branching-ratio"]
            
            dict_['files'][smp] = { 'era'  : smpCfg["era"], 
                                    'lumi' : lumi, 
                                    'type' : 'signal', 
                                    'group': 'signal',
                                    'scale': smpScale, 
                                    'cross-section': smpCfg["cross-section"], 
                                    'generated-events': sumW, 
                                    'branching-ratio': smpCfg["branching-ratio"], 
                                    }
        
        elif smpCfg.get("type") == "data":
            
            dict_['files'][smp] = { 'era'  : smpCfg["era"], 
                                    'lumi' : None, 
                                    'type' : 'data',
                                    'group': smpCfg["group"],
                                    'scale': 1, 
                                    'cross-section': None, 
                                    'generated-events': None, 
                                    'branching-ratio' : None 
                                }

    with open(os.path.join(plotter_p, "config_{}.yml".format(era)), 'w+') as _f:
        yaml.dump(dict_, _f, default_flow_style=False)

    return dict_ 


def ignoreSystematic(smp=None, flavor=None, process=None, s=None):
    """
        If some systematics cause problems, 
        return True and they will be ignored in the statistic test
        please give them in the using the CMS naming convention
    """
    if not s:
        return False
    
    if smp:
        # do not propagate DYrewigthing to non DY samples !
        if not smp.startswith('DYJetsToLL') and s.startswith('DYweight_'):
            return True 
    
        if 'postVFP' in smp and 'preVFP' in s: 
            return True 
        if 'preVFP' in smp and 'postVFP' in s: 
            return True
    
    # this is my first attempt, applying tth dy weights
    if 'DYReWeight' in s:
        return True
    if 'cEff' in s:
        return True
    if 'bEff' in s:
        return True
    if 'lightEff' in s:
        return True
    if 'UnclusteredEn' in s: ## this vars is very small and causes problem in the fit
        return True
    if 'scale_j_Total' in s: # FIXME just for now 
        return True
    if 'CMS_btagSF_deepCSV_fixWP_' in s: # btag scale facors will be applied on subjets
        return True


def merge_histograms(smp=None, smpScale=None, process=None, histogram=None, destination=None, luminosity=None, normalize=False):
    """
    Merge two histograms together. If the destination histogram does not exist, it
    is created by cloning the input histogram
    Parameters:
        production      gg-fusion , bb-assocaited production 
        flavor          elel , mumu, muel 
        process         MH-{}_MA-{}
        histogram       Pointer to TH1 to merge
        destination     Destination histogram
    Return:
    The merged histogram
    """
    
    if not histogram:
        raise Exception('Histogram can not be found')
    if histogram.GetEntries() == 0:
        if destination:
            return destination
        else:
            d = histogram.Clone()
            d.SetDirectory(ROOT.nullptr)
            return d

    if normalize and not 'data' in process and smpScale is not None:
        # In case is needed , but this already should be done 
        # in the post-processing step in bamboo
        #logger.info('I am scaling here process %s by %s '%(process, smpScale))
        histogram.Scale(smpScale)
    
    d = destination
    if not d:
        d = histogram.Clone()
        d.SetDirectory(ROOT.nullptr)
    else:
        d = destination
        d.Add(histogram)
    zeroNegativeBins(d)
    return d


def add_decorPrePosVFPSytstematics(listFiles):
    otherFiles= []
    for f in listFiles:
        if f.endswith('postVFP.root'):
            otherFiles.append(f.replace('UL16postVFP.root', 'UL16preVFP.root'))
        elif f.endswith('preVFP.root'):
            otherFiles.append(f.replace('UL16preVFP.root', 'UL16postVFP.root'))
    return otherFiles


def call_python_version(Version, Module, Function, ArgumentList):
    import execnet
    """
    scalefactors = call_python_version("3", "Harvester.py", "get_normalisationScale",  [input, method, era]) 
    """
    gw      = execnet.makegateway("popen//python=python%s" % Version)
    channel = gw.remote_exec("""
                from %s import %s as the_function
                channel.send(the_function(*channel.receive()))
            """ % (Module, Function))
    channel.send(ArgumentList)
    return channel.receive()


def get_massParameters(smp):
    m_heavy = float(smp.split('_')[2].replace('p', '.'))
    m_light = float(smp.split('_')[4].replace('p', '.'))
    
    if '_tb_20p00_' in smp: 
        process = 'bb{}'.format(smp[0])
    elif '_tb_1p50_' in smp:
        process = 'gg{}'.format(smp[8])
    
    return m_heavy, m_light, process


def prepareFile(processes_map, categories_map, input, output_filename, signal_process, method, luminosity, mode, thdm, flav_categories, era, scalefactors, tanbeta, _2POIs_r=False, unblind=False, normalize=False):
    """
    Prepare a ROOT file suitable for Combine Harvester.
    The structure is the following:
      1) Each observable is mapped to a subfolder. The name of the folder is the name of the observable
      2) Inside each folder, there's a bunch of histogram, one per background and signal hypothesis. 
      The name of the histogram is the name of the background.
    """
    ToFIX = [] 
    logger.info("Categories                                 : %s"%flav_categories )
    logger.info("Preparing ROOT file for combine...")
    logger.info("="*60)
    
    if not os.path.exists(os.path.dirname(output_filename)):
        os.makedirs(os.path.dirname(output_filename))

    hash = hashlib.sha512()
    hash.update(input)
    hash.update(output_filename)
    hash.update(str(luminosity))

    all_files = [os.path.join(input, f) for f in os.listdir(input) if f.endswith('.root')]
    if not era == "fullrun2":
        files = [ f for f in all_files if EraFromPOG(era) in f.split('/')[-1]]
    else:
        files = all_files
    
    # Gather a list of inputs files for each process.
    # The key is the process identifier, the value is a list of files
    # If more than one file exist for a given process, the histograms of each file will
    # be merged together later

    processes_files = {}
    for process, paths in processes_map.items():
        process_files = []
        for path in paths:
            r = re.compile(path, re.IGNORECASE)
            local_process_files = [f for f in files if r.search(os.path.basename(f))]
            if len(local_process_files) == 0:
                logger.warning("Warning: regular expression {} do not match any file".format(path))
                #continue
            process_files += local_process_files
        processes_files[process] = process_files
        if type(process) is tuple:
            hash.update(process[0])
        else:
            hash.update(process)
        map(hash.update, process_files)
    
    # I am assuming you will be able to get full list of sys from these 2 
    files_tolistsysts  = [ processes_files['ttbar'][0], processes_files['DY'][0] ]
    if era == '2016':
        otherFiles = add_decorPrePosVFPSytstematics(files_tolistsysts)
        files_tolistsysts += otherFiles
    systematics = {f: get_listofsystematics(files_tolistsysts, f)[:] for f in flav_categories}
    print("Systematics are taken from main backgrounds files:: {}".format(files_tolistsysts))
    print(systematics)
    
    # Use a TT file as reference to extract the list of histograms
    ref_file = processes_files['ttbar'][0]
    print("Extract histogram names from {}".format(ref_file))

    f = ROOT.TFile.Open(ref_file)
    keys = [n.GetName() for n in f.GetListOfKeys()]
    if len(keys) == 0:
        raise Exception('There are no histograms in file %s, aborting now' % ref_file)
    f.Close()
    print("Done.")

    # Create the list of histograms (nominal + systematics) for each category
    # we are interested in.
    # The key is the category name and the value is a list of histogram. The list will always
    # contains at least one histogram (the nominal histogram), and possibly more, two per systematic (up & down variation)
    histogram_names_per_cat = {}
    for cat in flav_categories:
        flavor   = cat.split('_')[4]
        reg      = cat.split('_')[3]
        reco     = cat.split('_')[2]
        prod     = cat.split('_')[0] +'_' + cat.split('_')[1]
        
        taggerWP = 'DeepFlavourM' if reg == 'resolved' else 'DeepCSVM'
        #FIXME in next iteration of plots in Bamboo
        fix_reco_format = 'gg_fusion' if reco =='nb2' else 'bb_associatedProduction'

        hash.update(cat)
        histogram_names = {}
        for category, histogram_name in categories_map.items():
            #histogram_name = histogram_name.format(flavor=flavor, reg=reg, taggerWP=taggerWP, fix_reco_format=fix_reco_format)
            histogram_name = histogram_name.format(flavor=flavor, reco=reco, reg=reg, taggerWP=taggerWP)
            if type(category) is tuple:
                hash.update(category[0])
            else:
                hash.update(category)
            hash.update(histogram_name)
            r = re.compile(histogram_name, re.IGNORECASE)
            histogram_names[category] = [n for n in keys if r.search(n)]
            if len(histogram_names[category]) == 0:
                print("[{}, {}] Warning: no histogram found matching {}".format(flavor, category, histogram_name))
                ToFIX.append(category[1])
        histogram_names_per_cat[cat] = histogram_names
    
    ToFIX = list( set(ToFIX))

    # Extract list of expand histogram name
    systematics_regex = re.compile('__(.*)(up|down)$', re.IGNORECASE)
    histograms_per_cat = {}
    for cat in flav_categories:
        histograms = {}
        for category, histogram_names in histogram_names_per_cat[cat].items():
            for histogram_name in histogram_names:
                m = systematics_regex.search(histogram_name)
                if m:
                    # It's a systematic histogram
                    pass
                else:
                    nominal_name = histogram_name
                    if category in histograms:
                        # Check that the regex used by the user only match 1 histogram
                        if histograms[category] != nominal_name:
                            raise Exception("The regular expression used for category %r matches more than one histogram: %r and %r" % (category, nominal_name, histograms[category]))
                    histograms[category] = nominal_name
        histograms_per_cat[cat] = histograms

    cms_systematics = {f: [CMSNamingConvention(s, era) for s in v] for f, v in systematics.items()}
    
    for cat in flav_categories:
        hash.update(cat)
        for systematic in cms_systematics[cat]:
            hash.update(systematic)
    hash.update(get_method_group(method))
    hash = hash.hexdigest()

    if os.path.exists(output_filename):
        # File exists. Check is stored hash is the same as the computed one. If yes, skip the file create
        f = ROOT.TFile.Open(output_filename)
        stored_hash = f.Get('hash')
        if stored_hash and stored_hash.GetTitle() == hash:
            print("File %r already exists and contains all the needed shapes. Skipping file generation." % output_filename)
            systematics = f.Get('systematics')
            return output_filename, json.loads(systematics.GetTitle()), ToFIX
        else:
            print("File %r already exists but is no longer up-to-date. It'll be regenerated." % output_filename)

    final_systematics = {}
    shapes = {}
    smpScale = None
    
    # Try to open each file once
    for process, process_files in processes_files.items():
        process_specific_to_signal_hypo = None
        if type(process) is tuple:
            process_specific_to_signal_hypo = process[1]
            process = process[0]

        print("Loading histograms for process {}".format(process))
        # Process name used in datacard for the signal is different from
        # the one used here (no mass or parameters in the name)
        systematic_process = process
        if signal_process in systematic_process:
            systematic_process = signal_process

        for process_file in process_files:
            f = ROOT.TFile.Open(process_file)
            
            smp  = process_file.split('/')[-1]
            smpNm= smp.replace('.root', '') 
            if smp.startswith('__skeleton__'):
                continue

            smpScale =None
            if normalize:
                newEra  = ConfigurationEra(smp)
                _t      = scalefactors['files'][smp]['type'] 
                try:
                    lumi= scalefactors['files'][smp]['lumi']
                except:
                    era = scalefactors['files'][smp]['era']
                    lumi= scalefactors["configuration"]["luminosity"][era]
                
                if _t =='signal':
                    # make sure that you are using 1 single tb with the corresponding xsc and BR
                    #xsc = scalefactors['files'][smp]['cross-section']
                    #br  = scalefactors['files'][smp]['branching-ratio']
                    sumW = scalefactors['files'][smp]['generated-events']
                    m_heavy, m_light, proc1 = get_massParameters(smpNm)
                    
                    if tanbeta is None:
                        tanbeta = 1.5 if proc1.startswith('gg') else 20.
                    
                    xsc, xsc_err, BR = Constants.get_SignalStatisticsUncer(m_heavy, m_light, proc1, thdm, tanbeta)
                    smpScale = (lumi)/sumW
                    if _2POIs_r:
                        smpScale *= BR
                        if method !='asymptotic':
                            smpScale *= xsc
                    else:
                        heavy = thdm[0]
                        proc2 = 'gg%s'%heavy if proc1 =='bb%s'%heavy else 'bb%s'%heavy
                        xsc2, xsc2_err, BR = Constants.get_SignalStatisticsUncer(m_heavy, m_light, proc2, thdm, tanbeta)
                        factor = xsc/(xsc + xsc2)
                        smpScale *= factor
                
                elif _t == 'mc':
                    sumW = scalefactors['files'][smp]['generated-events']
                    xsc  = scalefactors['files'][smp]['cross-section']
                    smpScale = (xsc*lumi)/sumW

            # Build a dict key name -> key for faster access
            keys = {}
            for key in f.GetListOfKeys():
                # Only keep the highest cycle
                if not key.GetName() in keys:
                    keys[key.GetName()] = key

            for cat in flav_categories:
                if not cat in final_systematics:
                    final_systematics[cat] = {}
                
                process_with_flavor = process + "_" + cat
                
                # Loop over all categories and load the histograms
                for category, original_histogram_name in histograms_per_cat[cat].items():
                    
                    category_specific_to_signal_hypo = None
                    if type(category) is tuple:
                        category_specific_to_signal_hypo = category[1]
                        category = category[0]
                    
                    # Keep the category only if the signal hypothesis is the same
                    #masspoint = category.split(mode)[-1]
                    #if not original_histogram_name.endswith(masspoint):
                    #    continue
                    
                    if category_specific_to_signal_hypo and process_specific_to_signal_hypo:
                        if category_specific_to_signal_hypo != process_specific_to_signal_hypo:
                            continue
                    #logger.info("Keeping only category {} with the following parameters ::  {} for {}".format(category, cat, process))

                    final_systematics_category         = final_systematics[cat].setdefault(category, {})
                    final_systematics_category_process = final_systematics_category.setdefault(systematic_process, set())
                    
                    shapes_category         = shapes.setdefault(category, {})
                    shapes_category_process = shapes_category.setdefault(process_with_flavor, {})
                
                    # Load nominal shape
                    try:
                        hist = get_hist_from_key(keys, original_histogram_name)
                        shapes_category_process['nominal'] = merge_histograms(smp, smpScale, process, hist, shapes_category_process.get('nominal', None), lumi, normalize)
                    except:
                        raise Exception('Missing histogram %r in %r for %r. This should not happen.' % (original_histogram_name, process_file, process_with_flavor))

                    # Load systematics shapes
                    for systematic in systematics[cat]:
                        
                        cms_systematic = CMSNamingConvention(systematic, newEra, process)
                        if ignoreSystematic(smp=smp, flavor=None, process=None, s=cms_systematic):
                            continue
                        
                        has_both = True
                        for variation in ['up', 'down']:
                            key = cms_systematic + variation.capitalize()
                            h   = get_hist_from_key(keys, original_histogram_name + '__' + systematic + variation)
                            if h:
                                try:
                                    shapes_category_process[key] = merge_histograms(smp, smpScale, process, h, shapes_category_process.get(key, None), lumi, normalize)
                                except:
                                    raise Exception('Missing histogram %r in %r for %r. This should not happen.' % (original_histogram_name + '__' + systematic + variation, process_file, process_with_flavor))
                            else:
                                has_both = False
                        if has_both:
                            final_systematics_category_process.add(cms_systematic)

            f.Close()
        print("Done.")

    for cat in flav_categories:
        for category, d in final_systematics[cat].items():
            for key, value in d.items():
                d[key] = list(value)

    # Store hash
    output_file = ROOT.TFile.Open(output_filename, 'recreate')
    file_hash = ROOT.TNamed('hash', hash)
    file_hash.Write()

    systematics_object = ROOT.TNamed('systematics', json.dumps(final_systematics))
    systematics_object.Write()

    if not unblind:
        for cat in flav_categories:
            for category, processes in shapes.items():
                category  = category
                fake_data = None
                for process, systematics_dict in processes.items():
                    if process.startswith(signal_process):
                        continue
                    if not process.endswith("_" + cat):
                        continue
                    scale = 1
                    if not fake_data:
                        fake_data = systematics_dict['nominal'].Clone()
                        fake_data.Scale(scale)
                        fake_data.SetDirectory(ROOT.nullptr)
                    else:
                        fake_data.Add(systematics_dict['nominal'], scale)
                    print( 'data_obs (fake):: ', fake_data.Integral(), cat, category, process)
                
                processes['data_obs_{}'.format(cat)] = {'nominal': fake_data}

    for category, processes in shapes.items():
        if Constants.cat_to_tuplemass(category) in ToFIX:
            continue
        output_file.mkdir(category).cd()
        for process, systematics_ in processes.items():
            for systematic, histogram in systematics_.items():
                if process == 'data_obs' and systematic != 'nominal':
                    continue
                histogram.SetName(process if systematic == 'nominal' else process + '__' + systematic)
                histogram.Write()
        
        output_file.cd()
    output_file.Close()
    
    print("Done. File saved as %r" % output_filename)
    return output_filename, final_systematics, ToFIX
