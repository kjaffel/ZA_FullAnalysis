import ROOT
import json
import os, os.path, sys
import re, hashlib
import Constants as Constants

sys.dont_write_bytecode  = True
splitPDF                 = False
splitJECBySources        = False
scaleZAToSMCrossSection  = False
splitTTbarUncertBinByBin = False

def CMSNamingConvention(origName, era=None):
    ## see https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/HiggsCombinationConventions
    jerRegions = [ "barrel", "endcap1", "endcap2lowpt", "endcap2highpt", "forwardlowpt", "forwardhighpt" ]
    other = {
        # old naming , will be removed  soon 
        'puweights2016_Moriond17': "CMS_pileup_%s"era,
        'elid':"CMS_eff_el",
        'muid':"CMS_eff_mu",
        'muiso':"CMS_iso_mu",
        'eleltrig':"CMS_eff_trigElEl_%s"%era,
        'mumutrig':"CMS_eff_trigMuMu_%s"%era,
        'elmutrig':"CMS_eff_trigElMu_%s"%era,
        'mueltrig':"CMS_eff_trigMuEl_%s"%era,
        # new names in the histograms  
        "btagSF_fixWP_subjetdeepcsvM_light":"CMS_btag_light_%s"%era,
        "btagSF_fixWP_subjetdeepcsvM_heavy":"CMS_btag_heavy_%s"%era,
        "btagSF_fixWP_deepcsvM_light":"CMS_btag_light_%s"%era,
        "btagSF_fixWP_deepcsvM_heavy":"CMS_btag_heavy_%s"%era,
        "btagSF_fixWP_deepflavourM_light":"CMS_btag_light_%s"%era,
        "btagSF_fixWP_deepflavourM_heavy":"CMS_btag_heavy_%s"%era,
        "L1Prefiring": "CMS_L1PreFiring":"CMS_btag_heavy_%s"%era,
        "unclustEn": "CMS_UnclusteredEn_%s"%era,
        'elid_medium':"CMS_eff_elid",
        'lowpt_ele_reco':"CMS_reff_elreco",
        'highpt_ele_reco':"CMS_eff_elreco",
        'muid_medium':"CMS_eff_muid",
        'muiso_tight':"CMS_eff_muiso",
        'HHMoriond17__eleltrig':"CMS_eff_trigElEl_%s"%era,
        'HHMoriond17__mumutrig':"CMS_eff_trigMuMu_%s"%era,
        'HHMoriond17__elmutrig':"CMS_eff_trigElMu_%s"%era,
        'HHMoriond17__mueltrig':"CMS_eff_trigMuEl_%s"%era,
        # not in use  
        "chMisID": "CMS_chargeMisID_%s"%era,
        "jesHEMIssue": "CMS_HEM",
        }
    theo_perProc = {"qcdScale": "QCDscale", "psISR": "ISR", "psFSR": "FSR", "pdf": "pdf"}
    if origName in other:
        return other[origName]
    elif origName in theo_perProc:
        return "{}".format(theo_perProc[origName])
    elif origName.startswith("jes"):
        return "CMS_scale_j_{}".format(origName[3:])
    elif origName.startswith("jer"):
        if len(origName) == 3:
            return "CMS_res_j_{}".format(era)
        else:
            jerReg = jerRegions[int(origName[3:])]
            return "CMS_res_j_{}_{}".format(jerReg, era)
        return "CMS_FR{}_{}".format(flav[0].lower(), vari[:3].lower())
    if origName.startswith("pileup"):
        return "CMS_pileup_%s"%era  
    else:
        return origName

def get_hist_from_key(keys, key):
    h = keys.get(key, None)
    if h:
        return h.ReadObj()
    return None

def zeroNegativeBins(h):
    for i in range(1, h.GetNbinsX() + 1):
        if h.GetBinContent(i) < 0.:
            h.SetBinContent(i, 0.)
            h.SetBinError(i, 0.)

def get_method_group(method):
    if method == 'fit':
        return 'fit'
    else:
        return 'limits'

def get_combine_method(method):
    if method == 'fit':
        return '-M MaxLikelihoodFit'
    elif method == 'asymptotic':
        return '-M AsymptoticLimits --rMax 500'
    elif method == 'hybridnew':
        return '-H Significance -M HybridNew --frequentist --testStat LHC --fork 10'

def getScaleFactor(flavor, process):
    if flavor == 'ElEl' and 'nobtag_to_btagM' in process:
        return 0.828
    if flavor == 'MuMu' and 'nobtag_to_btagM' in process:
        return 0.879
    if scaleZAToSMCrossSection and 'ggZA' in process:
        return Constants.getZACrossSection() * Constants.getZATollbbBR()
    return 1.

def merge_histograms(flavor, process, histogram, destination, luminosity):
    """
    Merge two histograms together. If the destination histogram does not exist, it
    is created by cloning the input histogram
    Parameters:
        flavor          Flavor
        process         Name of the current process
        histogram       Pointer to TH1 to merge
        destination     Destination histogram
    Return:
    The merged histogram
    """
    if not histogram:
        raise Exception()

    if histogram.GetEntries() == 0:
        if destination:
            return destination
        else:
            d = histogram.Clone()
            d.SetDirectory(ROOT.nullptr)
            return d
    
    # Rescale histogram to luminosity, if it's not data
    scale = getScaleFactor(flavor, process)
    if not 'data' in process:
        scale *= luminosity
    histogram.Scale(scale)

    d = destination
    if not d:
        d = histogram.Clone()
        d.SetDirectory(ROOT.nullptr)
    else:
        d = destination
        d.Add(histogram)

    zeroNegativeBins(d)
    return d

def getKnownSystematics():
    known_systematics = [
            'puweights2016_Moriond17',
            'jesTotal',
            'jer',
            'elid',
            #'ele_reco',
            'muid',
            'muiso',
            #'qcdScale',
            #'psISR',
            #'psFSR',
            #'pdf',
            'eleltrig',
            'mumutrig',
            'elmutrig',
            'mueltrig',
            'L1PreFiring',
            'DeepCSVM',
            ]

    if splitTTbarUncertBinByBin:
        for i in range(1,7):
            known_systematics.append('ttbarNormBin{0}'.format(i))

    if splitPDF:
        pdf_processes = ['pdf{}'.format(x).lower() for x in ["gg","qg","qq"]]
        known_systematics.remove('pdf')
        known_systematics += pdf_processes

    if splitJECBySources:
        jec_sources = ['jec{}'.format(x).lower() for x in [
                "AbsoluteFlavMap",
                "AbsoluteMPFBias",
                "AbsoluteScale",
                "AbsoluteStat",
                "FlavorQCD",
                "Fragmentation",
                "PileUpDataMC",
                "PileUpPtBB",
                "PileUpPtEC1",
                "PileUpPtEC2",
                "PileUpPtHF",
                "PileUpPtRef",
                "RelativeBal",
                "RelativeFSR",
                "RelativeJEREC1",
                "RelativeJEREC2",
                "RelativeJERHF",
                "RelativePtBB",
                "RelativePtEC1",
                "RelativePtEC2",
                "RelativePtHF",
                "RelativeStatEC",
                "RelativeStatFSR",
                "RelativeStatHF",
                "SinglePionECAL",
                "SinglePionHCAL",
                "TimePtEta"]]
        known_systematics.remove('jec')
        known_systematics += jec_sources
    return known_systematics

def prepareFile(processes_map=None, categories_map=None, input=None, output_filename=None, signal_process=None, method=None, luminosity=None, flavors=['All'], era=None, blind=False):
    """
    Prepare a ROOT file suitable for Combine Harvester.
    The structure is the following:
      1) Each observable is mapped to a subfolder. The name of the folder is the name of the observable
      2) Inside each folder, there's a bunch of histogram, one per background and signal hypothesis. The name of the histogram is the name of the background.
    """

    known_systematics = getKnownSystematics()
    print("Preparing ROOT file for combine...")
    print("="*60)
    systematics = {f: known_systematics[:] for f in flavors}

    if not os.path.exists(os.path.dirname(output_filename)):
        os.makedirs(os.path.dirname(output_filename))

    hash = hashlib.sha512()
    hash.update(input)
    hash.update(output_filename)
    hash.update(str(luminosity))

    files = [os.path.join(input, f) for f in os.listdir(input) if f.endswith('.root')]

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
                print("Warning: regular expression {} do not match any file".format(path))
            process_files += local_process_files
        processes_files[process] = process_files
        if type(process) is tuple:
            hash.update(process[0])
        else:
            hash.update(process)

        map(hash.update, process_files)

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
    histogram_names_per_flavor = {}
    for flavor in flavors:
        hash.update(flavor)
        histogram_names = {}
        for category, histogram_name in categories_map.items():
            histogram_name = histogram_name.format(flavor=flavor)
            if type(category) is tuple:
                hash.update(category[0])
            else:
                hash.update(category)
            hash.update(histogram_name)
            r = re.compile(histogram_name, re.IGNORECASE)
            histogram_names[category] = [n for n in keys if r.search(n)]
            if len(histogram_names[category]) == 0:
                print("[{}, {}] Warning: no histogram found matching {}".format(flavor, category, histogram_name))
        histogram_names_per_flavor[flavor] = histogram_names

    # Extract list of expand histogram name
    systematics_regex = re.compile('__(.*)(up|down)$', re.IGNORECASE)
    histograms_per_flavor = {}
    for flavor in flavors:
        histograms = {}
        for category, histogram_names in histogram_names_per_flavor[flavor].items():
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

        histograms_per_flavor[flavor] = histograms

    cms_systematics = {f: [CMSNamingConvention(s, era) for s in v] for f, v in systematics.items()}
    for f in flavors:
        hash.update(f)
        for systematic in cms_systematics[f]:
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
            return output_filename, json.loads(systematics.GetTitle())
        else:
            print("File %r already exists but is no longer up-to-date. It'll be regenerated." % output_filename)

    # [flavor][category][process] -> set()
    final_systematics = {}
    # [category][process_with_flavor] = {}
    shapes = {}

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

        # final_systematics[systematic_process] = {}
        # shapes[process] = {}

        for process_file in process_files:
            f = ROOT.TFile.Open(process_file)

            if process_file.split('/')[-1].startswith('__skeleton__'):
                continue
            # Build a dict key name -> key for faster access
            keys = {}
            for key in f.GetListOfKeys():
                # Only keep the highest cycle
                if not key.GetName() in keys:
                    keys[key.GetName()] = key

            for flavor in flavors:
                if not flavor in final_systematics:
                    final_systematics[flavor] = {}

                process_with_flavor = process + "_" + flavor

                # Loop over all categories and load the histograms
                for category, original_histogram_name in histograms_per_flavor[flavor].items():

                    category_specific_to_signal_hypo = None
                    if type(category) is tuple:
                        category_specific_to_signal_hypo = category[1]
                        category = category[0]

                    if category_specific_to_signal_hypo and process_specific_to_signal_hypo:
                        # Keep the category only if the signal hypothesis is the same
                        if category_specific_to_signal_hypo != process_specific_to_signal_hypo:
                            print("  ignoring category {} for {}".format(category, process))
                            continue

                    final_systematics_category = final_systematics[flavor].setdefault(category, {})
                    final_systematics_category_process = final_systematics_category.setdefault(systematic_process, set())

                    shapes_category = shapes.setdefault(category, {})
                    shapes_category_process = shapes_category.setdefault(process_with_flavor, {})

                    # Load nominal shape
                    try:
                        hist = get_hist_from_key(keys, original_histogram_name)
                        shapes_category_process['nominal'] = merge_histograms(flavor, process, hist, shapes_category_process.get('nominal', None), luminosity)
                    except:
                        raise Exception('Missing histogram %r in %r for %r. This should not happen.' % (original_histogram_name, process_file, process_with_flavor))

                    # Load systematics shapes
                    for systematic in systematics[flavor]:
                        cms_systematic = CMSNamingConvention(systematic, era)

                        has_both = True
                        for variation in ['up', 'down']:
                            key = cms_systematic + variation.capitalize()

                            h = get_hist_from_key(keys, original_histogram_name + '__' + systematic + variation)
                            if h:
                                try:
                                    shapes_category_process[key] = merge_histograms(flavor, process, h, shapes_category_process.get(key, None), luminosity)
                                except:
                                    raise Exception('Missing histogram %r in %r for %r. This should not happen.' % (original_histogram_name + '__' + systematic + variation, process_file, process_with_flavor))
                            else:
                                has_both = False

                        if has_both:
                            final_systematics_category_process.add(cms_systematic)

            f.Close()
        print("Done.")

    for flavor in flavors:
        for category, d in final_systematics[flavor].items():
            for key, value in d.items():
                d[key] = list(value)

    # In 'fit' mode, scale the signal to 1 pb instead of 1 fb
    if method == 'fit':
        for category, processes in shapes.items():
            for process, systematics_dict in processes.items():
                if not process.startswith(signal_process):
                    continue

                for name, shape in systematics_dict.items():
                    shape.Scale(1000)

    output_file = ROOT.TFile.Open(output_filename, 'recreate')

    # Store hash
    file_hash = ROOT.TNamed('hash', hash)
    file_hash.Write()

    systematics_object = ROOT.TNamed('systematics', json.dumps(final_systematics))
    systematics_object.Write()

    if blind:
        for flavor in flavors:
            for category, processes in shapes.items():
                category = category
                fake_data = None
                for process, systematics_dict in processes.items():
                    if process.startswith(signal_process):
                        continue

                    if not process.endswith(flavor):
                        continue

                    scale = 1
                    if 'nobtag_to_btagM' in process and not 'data' in process:
                        scale = -1

                    if not fake_data:
                        fake_data = systematics_dict['nominal'].Clone()
                        fake_data.Scale(scale)
                        fake_data.SetDirectory(ROOT.nullptr)
                    else:
                        fake_data.Add(systematics_dict['nominal'], scale)
                #create fake excess
                #if fake_data.GetName() == "rho_steps_histo_ElEl_hZA_lljj_deepCSV_btagM_mll_and_met_cut_3":
                #    fake_data.SetBinContent(2, fake_data.GetBinContent(2)*1.4)
                #if fake_data.GetName() == "rho_steps_histo_MuMu_hZA_lljj_deepCSV_btagM_mll_and_met_cut_6":
                #    fake_data.SetBinContent(2, fake_data.GetBinContent(2)*1.4)
                #if fake_data.GetName() == "rho_steps_histo_ElEl_hZA_lljj_deepCSV_btagM_mll_and_met_cut_9":
                #    fake_data.SetBinContent(3, fake_data.GetBinContent(3)*1.4)
                #if fake_data.GetName() == "rho_steps_histo_ElEl_hZA_lljj_deepCSV_btagM_mll_and_met_cut_10":
                #    fake_data.SetBinContent(1, fake_data.GetBinContent(1)*1.4)
                #if fake_data.GetName() == "rho_steps_histo_MuMu_hZA_lljj_deepCSV_btagM_mll_and_met_cut_12":
                #    fake_data.SetBinContent(1, fake_data.GetBinContent(1)*1.4)
                #if fake_data.GetName() == "rho_steps_histo_MuMu_hZA_lljj_deepCSV_btagM_mll_and_met_cut_19":
                #    fake_data.SetBinContent(1, fake_data.GetBinContent(1)*1.4)

                processes['data_obs_%s' % flavor] = {'nominal': fake_data}

    for category, processes in shapes.items():
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
    return output_filename, final_systematics
