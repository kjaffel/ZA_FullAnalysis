#! /usr/bin/env python
import argparse
import math
import os, sys
# to prevent pyroot to hijack argparse we need to go around
tmpargv  = sys.argv[:] 
sys.argv = []
sys.argv = tmpargv

from ROOT import gROOT, PyConfig, TFile, nullptr
gROOT.Reset()
gROOT.SetBatch()

PyConfig.IgnoreCommandLineOptions = True

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

def create_postfit_prefit_error_shapes(fit, fit_shape_with_errors, reference):
    fit_up = reference.Clone()
    fit_up.SetName(reference.GetName() + "__%sup"%fit)
    fit_up.SetDirectory(nullptr)
    fit_down = reference.Clone()
    fit_down.SetName(reference.GetName() + "__%sdown"%fit)
    fit_down.SetDirectory(nullptr)
    for b in range(1, reference.GetNbinsX() + 1):
        error = fit_shape_with_errors.GetBinError(b)
        fit_up.SetBinContent(b, reference.GetBinContent(b) + error)
        fit_down.SetBinContent(b, reference.GetBinContent(b) - error)
    return fit_up, fit_down

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Combine harvester pre/post-fit output to a format suitable for plotIt')
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
    channels = filter(lambda x: x != '', channels)
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
    
    for fit in ['prefit', 'postfit']:
        # Prepare shapes for plotIt
        for channel in channels:
            data_driven_dy_histogram = None
            for background in backgrounds[channel]:
        
                output_filename = "%s_%s_histos.root" % (background, fit)
                if ignore_background(background):
                    continue
                # Nominal post/pre-fit shape
                nominal_fit = file.Get('%s_%s/%s' % (channel, fit, background))
                if not nominal_fit:
                    print("[{}, {}] Shape not found, skipping".format(background, channel))
                    continue
                nominal_fit.SetName('{}'.format(options.name+ '_%s'%fit))
                remove_errors(nominal_fit)
        
                plot_file = TFile.Open(os.path.join(output_dir, output_filename), 'recreate')
                nominal_fit.Write()
                if background == 'ttbar':
                    # Special treatment for ttbar. Apply errors from the TotalBkgs shapes to ttbar
                    total_bkgs_fit = file.Get("{}_{}/TotalBkg".format(channel, fit))
                    if not total_bkgs_fit:
                        raise Exception("TotalBkg %s shape not found"%fit)
                    nominal_fit_up, nominal_fit_down = create_postfit_prefit_error_shapes(fit, total_bkgs_fit, nominal_fit)
                    nominal_fit_up.Write()
                    nominal_fit_down.Write()
                plot_file.Close()

                # if background != 'data_obs' and not background.startswith(options.signal_process):
                    # nominal_fit_up = nominal_fit.Clone()
                    # nominal_fit_up.SetName(options.name+ '_%s'%fit + '_' + channel + '__%sup'%fit)
                    # shift_hist(nominal_fit_up, 1)
                    # nominal_fit_down = nominal_fit.Clone()
                    # nominal_fit_down.SetName(options.name+ '_%s'%fit + '_' + channel + '__%sdown'%fit)
                    # shift_hist(nominal_fit_down, -1)
                    # remove_errors(nominal_fit)
                    # nominal_fit_up.Write()
                    # nominal_fit_down.Write()
            
            if data_driven_dy_histogram:
                output_filename = "DY_%s_histos.root"%fit
                plot_file = TFile.Open(os.path.join(output_dir, output_filename), 'recreate')
                data_driven_dy_histogram.Write()
                plot_file.Close()
                data_driven_dy_histogram = None
        
            # if options.signals:
            # f = TFile.Open(options.signals)
            # output_filename = "%s_%s_histos.root" % (options.signal_process, fit)
            # plot_file = TFile.Open(os.path.join(output_dir, output_filename), 'recreate')
            # for channel in channels:
                # # signals = [k.GetName() for k in f.Get(options.name+ '_%s'%fit).GetListOfKeys() if not '__' in k.GetName() and options.signal_process in k.GetName()]
                # # print 'Detected signals: %s' % (', '.join(signals))
                # shape = f.Get('%s/%s' % (options.name+ '_%s'%fit, options.signal_process + '_' + channel))
                # shape.SetName(options.name+ '_%s'%fit+ '_' + channel)
                # shape.Write()
            # plot_file.Close()
        # f.Close()
    print("All done. Files saved in %r" % output_dir)
