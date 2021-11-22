#! /usr/bin/env python
import os, sys, argparse, math
# to prevent pyroot to hijack argparse we need to go around
tmpargv = sys.argv[:] 
sys.argv = []
from ROOT import gROOT, PyConfig, TFile, nullptr
gROOT.Reset()
gROOT.SetBatch()
PyConfig.IgnoreCommandLineOptions = True
sys.argv = tmpargv

def ignore_background(bkg):
    return bkg in ['TotalProcs', 'TotalBkg', 'TotalSig']

def shift_hist(hist, by):
    if hist.Integral() < 0:
        by = -1 * by
    for b in range(1, hist.GetNbinsX() + 1):
        hist.SetBinContent(b, hist.GetBinContent(b) + by * hist.GetBinError(b))
        hist.SetBinError(b, 0)

def remove_errors(hist):
    for b in range(1, hist.GetNbinsX() + 1):
        hist.SetBinError(b, 0)

def create_postfit_error_shapes(postfit_shape_with_errors, reference):
    postfit_up = reference.Clone()
    postfit_up.SetName(reference.GetName() + "__postfitup")
    postfit_up.SetDirectory(nullptr)
    postfit_down = reference.Clone()
    postfit_down.SetName(reference.GetName() + "__postfitdown")
    postfit_down.SetDirectory(nullptr)
    for b in range(1, reference.GetNbinsX() + 1):
        error = postfit_shape_with_errors.GetBinError(b)
        postfit_up.SetBinContent(b, reference.GetBinContent(b) + error)
        postfit_down.SetBinContent(b, reference.GetBinContent(b) - error)
    return postfit_up, postfit_down

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Combine harvester post-fit output to a format suitable for plotIt')
    parser.add_argument('-i', '--input', action='store', type=str, dest='input', help='Path to the ROOT file created by combine harvester', required=True)
    #parser.add_argument('-s', '--signals', action='store', type=str, dest='signals', help='Path to the ROOT file containing all the signal shapes')
    parser.add_argument('-o', '--output', action='store', type=str, dest='output', help='Name of the output directory')
    parser.add_argument('-n', '--name', action='store', type=str, dest='name', help='Shape name')
    parser.add_argument('--signal-process', action='store', type=str, dest='signal_process', help='The process name identifying the signal (ggHH or ggX0HH for example)')

    options  = parser.parse_args()
    file     = TFile.Open(options.input)
    channels = set()
    for k in file.GetListOfKeys():
        cat = k.GetName().split('_')
        cat.pop()
        channels.add('_'.join(cat))
    channels = list(channels)
    print ("Detected channels: ", channels )
    
    # Construct the list of backgrounds
    # Naming is 'category/bkg_name'
    backgrounds = {}
    for channel in channels:
        backgrounds[channel] = set()
        for bkg in file.Get('%s_prefit' % channel).GetListOfKeys():
            backgrounds[channel].add(bkg.GetName())
        print('[{}] Detected backgrounds: {}'.format(channel, (', '.join(backgrounds[channel]))))
    
    output_dir = options.output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("")
    print("Creating ROOT files suitable for plotIt...")
    
    # Prepare shapes for plotIt
    for channel in channels:
        data_driven_dy_histogram = None
        for background in backgrounds[channel]:
    
            output_filename = "%s_postfit_histos.root" % (background)
            if options.signal_process in background:
                continue
            if ignore_background(background):
                continue
            # Nominal post-fit shape
            nominal_postfit = file.Get('%s_postfit/%s' % (channel, background))
            if not nominal_postfit:
                print("[{}, {}] Shape not found, skipping".format(background, channel))
                continue
            #nominal_postfit.SetName('{}_{}'.format(options.name, channel))
            nominal_postfit.SetName('{}'.format(options.name))
            remove_errors(nominal_postfit)
    
            if 'nobtag_to_btagM' in background:
                if data_driven_dy_histogram:
                    data_driven_dy_histogram.Add(nominal_postfit)
                else:
                    data_driven_dy_histogram = nominal_postfit.Clone()
                    data_driven_dy_histogram.SetDirectory(nullptr)
            else:
                plot_file = TFile.Open(os.path.join(output_dir, output_filename), 'update')
                nominal_postfit.Write()
                if background == 'ttbar':
                    # Special treatment for ttbar. Apply errors from the TotalBkgs shapes to ttbar
                    total_bkgs_postfit = file.Get("{}_postfit/TotalBkg".format(channel))
                    if not total_bkgs_postfit:
                        raise Exception("TotalBkg postfit shape not found")
                    nominal_postfit_up, nominal_postfit_down = create_postfit_error_shapes(total_bkgs_postfit, nominal_postfit)
                    nominal_postfit_up.Write()
                    nominal_postfit_down.Write()
                plot_file.Close()

            # if background != 'data_obs' and not background.startswith(options.signal_process):
                # nominal_postfit_up = nominal_postfit.Clone()
                # nominal_postfit_up.SetName(options.name + '_' + channel + '__postfitup')
                # shift_hist(nominal_postfit_up, 1)
                # nominal_postfit_down = nominal_postfit.Clone()
                # nominal_postfit_down.SetName(options.name + '_' + channel + '__postfitdown')
                # shift_hist(nominal_postfit_down, -1)
                # remove_errors(nominal_postfit)
                # nominal_postfit_up.Write()
                # nominal_postfit_down.Write()
        
        if data_driven_dy_histogram:
            output_filename = "dy_mc_postfit_histos.root"
            plot_file = TFile.Open(os.path.join(output_dir, output_filename), 'update')
            data_driven_dy_histogram.Write()
            plot_file.Close()
            data_driven_dy_histogram = None
    
    # if options.signals:
        # f = TFile.Open(options.signals)
        # output_filename = "%s_postfit_histos.root" % (options.signal_process)
        # plot_file = TFile.Open(os.path.join(output_dir, output_filename), 'update')
        # for channel in channels:
            # # signals = [k.GetName() for k in f.Get(options.name).GetListOfKeys() if not '__' in k.GetName() and options.signal_process in k.GetName()]
            # # print 'Detected signals: %s' % (', '.join(signals))
            # shape = f.Get('%s/%s' % (options.name, options.signal_process + '_' + channel))
            # shape.SetName(options.name + '_' + channel)
            # shape.Write()
        # plot_file.Close()
    # f.Close()
    print("All done. Files saved in %r" % output_dir)
