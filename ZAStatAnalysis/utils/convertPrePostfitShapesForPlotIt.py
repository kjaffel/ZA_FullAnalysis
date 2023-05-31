#!/usr/bin/env python3

import argparse
import os, sys, os.path
import glob
import json
# to prevent pyroot to hijack argparse we need to go around
tmpargv  = sys.argv[:] 
sys.argv = []
sys.argv = tmpargv

import numpy as np
import ROOT

from ROOT import gROOT, PyConfig, TFile, TCanvas, nullptr
gROOT.Reset()
gROOT.SetBatch()
PyConfig.IgnoreCommandLineOptions = True


def reshapePrePostFitHistograms(output_dir):
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../bamboo_' ))
    import HistogramTools as HT
    
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..' )))
    from numpy_hist import NumpyHist
    
    for rf in  glob.glob(os.path.join(output_dir, '*.root')):
            
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
        print( 'Divide events by the bin width for', smp)
    print( "============="*10)


def produce_empty_hist_to_allow_plotit_stack(fit, ch, output_dir, findhist):
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..' )))
    from numpy_hist import NumpyHist
    
    rF  = '%s_tt_%s_histos.root'%(ch, fit) # this file should always be there
    inF = TFile.Open(os.path.join(output_dir, rF), 'read')
    for hk in inF.GetListOfKeys():
        histNm = hk.ReadObj().GetName()
        hk.ReadObj().SetDirectory(0)
        
        if not histNm == findhist:
            continue
        
        hist   = hk.ReadObj()
        nph    = NumpyHist.getFromRoot(hist)
        edges  = nph.e 
        events = np.zeros(len(edges)-1)
        quadratic_bin_err = np.zeros(len(edges)-1)
    inF.Close()
    return edges,  events,  quadratic_bin_err


def merge_histos(fit, tot_histos, output_dir, ch_exp):
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..' )))
    from numpy_hist import NumpyHist
    from hist_interface import CppInterface
    
    print( tot_histos )
    for bkg, rF_chs in tot_histos.items():
        mergedHists = {}
        for rF in sorted(rF_chs):
            inF = TFile.Open(os.path.join(output_dir, rF), 'read')
            ch  = rF.split('_')[0]
            for hk in inF.GetListOfKeys():
                histNm = hk.ReadObj().GetName()
                hk.ReadObj().SetDirectory(0)
                hist  = hk.ReadObj()
                nph = NumpyHist.getFromRoot(hist)
                if '__%sup'%fit in  histNm: var = 'up'
                elif '__%sdown'%fit in histNm: var = 'down'
                else: var = 'nom'
                #print( hist, nph)     
                #print( histNm, rF, var ) 
                if not histNm in mergedHists.keys():
                    mergedHists[histNm] = {}
                    for i in range(ch_exp): 
                        mergedHists[histNm]['ch%s'%(i+1)]= [] 
                
                mergedHists[histNm][ch].append(nph)
            inF.Close()
    
        outNm = "%s_%s_histos.root" % (bkg, fit)
        outF  = TFile.Open(os.path.join(output_dir, outNm), 'recreate')
        
        print( bkg, mergedHists )
        for histNm, ch_histos in mergedHists.items():
            
            edges  = []
            events = []
            quadraticErr = []
            for i, (ch, histos)  in enumerate(ch_histos.items()):
                if not histos:
                    edg, eve, err = produce_empty_hist_to_allow_plotit_stack(fit, ch, output_dir, findhist=histNm)
                    events.append(eve)
                    edges.append(np.array( list(map(lambda x: x + i, edg.tolist() )) ))
                    quadraticErr.append(err)
                else:
                    #print (histos)
                    nph = histos[0]
                    events.append(nph.w)
                    edges.append( np.array( list(map(lambda x: x + i, nph.e.tolist() )) ) )
                    quadraticErr.append(nph.s)
            
            outF.cd()    
            tot_edges        = np.unique(np.concatenate(edges,axis=0))
            tot_events       = np.concatenate(events,axis=0)
            tot_quadraticErr = np.concatenate(quadraticErr,axis=0)
            
            print( bkg, '::', histNm, 'tot edges:', tot_edges, 'tot_events:', tot_events, 'merged bins:', ch_exp)
            newHist = CppInterface.fillHistogram1D(tot_edges, tot_events, tot_quadraticErr, histNm)
            newHist.SetDirectory(0)
            newHist.Write()
        outF.Close()
        print( 'File saved in ::', os.path.join(output_dir, outNm) )
        print( "============================"*3)
    return 


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
    parser.add_argument('-o', '--output', action='store', type=str, dest='output', help='Name of the output directory')
    parser.add_argument('-n', '--name', action='store', type=str, dest='name', help='Shape name')
    parser.add_argument('--signal-process', action='store', type=str, dest='signal_process', help='The process name identifying the signal (ggH or bbH for example)')

    options  = parser.parse_args()
    file     = TFile.Open(options.input)
    
    output_dir = options.output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    channels = set()
    for k in file.GetListOfKeys():
        cat = k.GetName().split('_')
        cat.pop()
        channels.add('_'.join(cat))
    channels = list(channels)
    channels = filter(lambda x: x != '', channels)
    print ("Detected channels: ", channels )
   
    combined_channels ={}
    for ch in sorted(channels):
        if not '_ch' in ch:
            continue
        comb = ch.split('_')[1]
        if not comb in combined_channels.keys():
            combined_channels[comb] =[]
        combined_channels[comb].append(ch)
    print("Detected channels from combined datacards:", combined_channels )
    
    with open(os.path.join(output_dir, 'channels.json'), 'w+') as outf:
        json.dump(combined_channels, outf)
    
    # Prepare shapes for plotIt
    if combined_channels:
        # Construct the list of backgrounds
        # Naming is 'category/bkg_name'
        backgrounds = {}
        bkgsInChannel = {}
        for ch, ch_per_year in combined_channels.items():
            bkgsInChannel[ch] = {}
            for channel in ch_per_year:
                backgrounds[channel] = set()
                for bkg in file.Get('%s_prefit' % channel).GetListOfKeys():
                    backgrounds[channel].add(bkg.GetName())
                    if not bkg.GetName() in bkgsInChannel[ch].keys():
                        bkgsInChannel[ch][bkg.GetName()] = []
                    bkgsInChannel[ch][bkg.GetName()].append(channel)
                print('[{}] Detected backgrounds: {}'.format(channel, (', '.join(backgrounds[channel]))))
        
        print("")
        print("Creating ROOT files suitable for plotIt...")
        print( bkgsInChannel )

        for fit in ['prefit', 'postfit']:
            tot_histos = {}
            for ch, bkg_per_chs in bkgsInChannel.items():
                for background, channels in bkg_per_chs.items():
                    
                    if ignore_background(background):
                        continue

                    if not background in tot_histos.keys():
                        tot_histos[background] = []
                    
                    output_filename = "%s_%s_%s_histos.root" % (ch, background, fit)
                    plot_file = TFile.Open(os.path.join(output_dir, output_filename), 'recreate')
                    for i, channel in enumerate(channels):
                        # Nominal post/pre-fit shape
                        nominal_fit = file.Get('%s_%s/%s' % (channel, fit, background))
                        if not nominal_fit:
                            print("[{}, {}] Shape not found, skipping".format(background, channel))
                            continue
                        nominal_fit.SetName('{}'.format(options.name+ '_%s'%fit))
                        remove_errors(nominal_fit)

                        plot_file.cd()
                        if i ==0: 
                            nominal_fit.Write()
                            nom = nominal_fit
                        else:
                            nom.Add(nominal_fit)

                        if background =='tt' or background =='ttbar': 
                            total_bkgs_fit = file.Get("{}_{}/TotalBkg".format(channel, fit))
                            if not total_bkgs_fit:
                                raise Exception("TotalBkg %s shape not found"%fit)
                            nominal_fit_up, nominal_fit_down = create_postfit_prefit_error_shapes(fit, total_bkgs_fit, nominal_fit)
                            if i ==0:
                                nominal_fit_up.Write()
                                nominal_fit_down.Write()
                                up  =nominal_fit_up
                                down=nominal_fit_down
                            else:
                                up.Add(nominal_fit_up)
                                down.Add(nominal_fit_down)

                    plot_file.Close()
                    tot_histos[background].append(output_filename)

            print("All done. Files saved in %r" % output_dir)
            merge_histos(fit, tot_histos, output_dir, ch_exp=len(bkgsInChannel.keys()))
            reshapePrePostFitHistograms(output_dir) 
    
    # Prepare shapes for plotIt for single lepton flavour / no combination of datacards
    else:
        # Construct the list of backgrounds
        # Naming is 'category/bkg_name'
        backgrounds = {}
        bkgsInChannel = {}
        for channel in channels:
            backgrounds[channel] = set()
            for bkg in file.Get('%s_prefit' % channel).GetListOfKeys():
                backgrounds[channel].add(bkg.GetName())
                if not bkg.GetName() in bkgsInChannel.keys():
                    bkgsInChannel[bkg.GetName()] = []
                bkgsInChannel[bkg.GetName()].append(channel)
            print('[{}] Detected backgrounds: {}'.format(channel, (', '.join(backgrounds[channel]))))
            
        print("")
        print("Creating ROOT files suitable for plotIt...")
        print( bkgsInChannel )
        for fit in ['prefit', 'postfit']:
            for background, channels in bkgsInChannel.items():
                
                if ignore_background(background):
                    continue
                
                output_filename = "%s_%s_histos.root" % (background, fit)
                plot_file = TFile.Open(os.path.join(output_dir, output_filename), 'recreate')
                print( output_dir ) 
                for i, channel in enumerate(channels):
                    # Nominal post/pre-fit shape
                    nominal_fit = file.Get('%s_%s/%s' % (channel, fit, background))
                    if not nominal_fit:
                        print("[{}, {}] Shape not found, skipping".format(background, channel))
                        continue
                    nominal_fit.SetName('{}'.format(options.name+ '_%s'%fit))
                    remove_errors(nominal_fit)
                    
                    plot_file.cd()
                    if i ==0: 
                        nominal_fit.Write()
                        h0 = nominal_fit
                    else:
                        h0.Add(nominal_fit)

                    if background =='tt' or background =='ttbar': 
                        total_bkgs_fit = file.Get("{}_{}/TotalBkg".format(channel, fit))
                        if not total_bkgs_fit:
                            raise Exception("TotalBkg %s shape not found"%fit)
                        nominal_fit_up, nominal_fit_down = create_postfit_prefit_error_shapes(fit, total_bkgs_fit, nominal_fit)
                        if i ==0:
                            nominal_fit_up.Write()
                            nominal_fit_down.Write()
                            up  =nominal_fit_up
                            down=nominal_fit_down
                        else:
                            up.Add(nominal_fit_up)
                            down.Add(nominal_fit_down)
                    
                plot_file.Close()

        print("All done. Files saved in %r" % output_dir)
