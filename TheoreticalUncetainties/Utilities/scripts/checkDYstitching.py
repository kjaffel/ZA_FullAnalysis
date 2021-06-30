#!/usr/bin/env python

# Modified from N. Smith, U. Wisconsin

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True
from DataFormats.FWLite import Handle, Runs, Lumis, Events
import sys
import math

eventsInclusive = Events([
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/00312D7A-FEBD-E611-A713-002590DB923E.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/00355459-F4BD-E611-B5E8-D4AE526A11F3.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/00BCC036-F6BD-E611-92F5-0025905A6118.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/028EE230-F7BD-E611-BCDB-0CC47AA9906E.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/02C57965-0DBE-E611-91EF-70106F4A9254.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/0632A87F-0DBE-E611-8948-F04DA275BF11.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/063CB919-03BE-E611-B04B-70106F4D68D4.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/0668344A-FEBD-E611-9FD3-0025905A48D0.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/0854F2BE-0FBE-E611-8864-E41D2D08DE00.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/0881F329-F4BD-E611-88F0-FA163E4A37A7.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/089C4B33-FFBD-E611-BEE7-70106F48BA5E.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/0A6C3F97-FDBD-E611-8E50-842B2B758AD8.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/0A900466-F0BD-E611-8E89-001C23C105CF.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/0AC8C964-F9BD-E611-A796-0025905A60CA.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_HCALDebug_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/50000/0C255783-F3BD-E611-BE80-7845C4FC39C8.root',
])

events0to50 = Events([
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/002E07B8-0F24-E711-91B4-5065F381B211.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/00A0E2D3-9F25-E711-A77B-A0369F83628A.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/00F511F3-DE24-E711-A6C4-0025904C66E6.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/0212D22B-E524-E711-AF1B-D067E5F914D3.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/02664488-0924-E711-85AB-0025905C5432.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/027530B0-1824-E711-821C-002590D60036.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/0402660A-2D23-E711-A774-5065F3817221.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/043F5A47-BD29-E711-BFD1-02163E01A2E5.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/0440FDFE-0724-E711-9D1D-0242AC130002.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/047486A5-0527-E711-85DC-FA163EDAC6C2.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/0480133D-2324-E711-90B4-008CFA198258.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/0611613D-1A24-E711-8756-0242AC130002.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Zpt-0To50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/70000/066F7083-F224-E711-B393-00266CFBE29C.root',
])

events50to100 = Events([
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-50To100_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/100000/00E3D7B3-9DCE-E611-A42D-0025905A609A.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-50To100_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/100000/0462F883-C0CE-E611-8CEE-0CC47A4D764A.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-50To100_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/100000/0E1E6882-A0CE-E611-BB4A-0CC47A7452D0.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-50To100_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/100000/0EC51971-9FCE-E611-A1FE-0025905B85FC.root',
])

events100to250 = Events([
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/120000/104AF025-6DCB-E611-BFB4-0025904B8708.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/120000/2029BD2C-7DCB-E611-8E08-0025904A87E2.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/120000/20E39922-6ECB-E611-8C93-0025904C7F80.root',
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/120000/28BA2C57-7CCB-E611-BECC-0025901D4894.root',
])

lorentz = ROOT.Math.LorentzVector('ROOT::Math::PxPyPzE4D<double>')

lheHandle = Handle('LHEEventProduct')

hInclusive = ROOT.TH1D("Inclusive", "Inclusive;Z p_{T};Counts / fb", 400, 0, 400)
hInclusive.SetLineColor(ROOT.kBlack)
h0to50 = ROOT.TH1D("0to50", "0 #leq p_{T} #leq 50;Z p_{T};Counts / fb", 400, 0, 400)
h0to50.SetLineColor(ROOT.kOrange)
h50to100 = ROOT.TH1D("50to100", "50 #leq p_{T} #leq 100;Z p_{T};Counts / fb", 400, 0, 400)
h50to100.SetLineColor(ROOT.kRed)
h100to250 = ROOT.TH1D("100to250", "100 #leq p_{T} #leq 250;Z p_{T};Counts / fb", 400, 0, 400)
h100to250.SetLineColor(ROOT.kGreen)
h250to400 = ROOT.TH1D("250to400", "250 #leq p_{T} #leq 400;Z p_{T};Counts / fb", 400, 0, 400)
h250to400.SetLineColor(ROOT.kBlue)

def fillhist(hist, events, xs):
    sumW = 0
    for iev, event in enumerate(events):
        event.getByLabel('externalLHEProducer', lheHandle)
        lhe = lheHandle.product()
        weight = 1 if lhe.originalXWGTUP() > 0 else -1
        sumW += weight

        lheParticles = lhe.hepeup()
        def lhep4(i):
            px = lheParticles.PUP.at(i)[0]
            py = lheParticles.PUP.at(i)[1]
            pz = lheParticles.PUP.at(i)[2]
            pE = lheParticles.PUP.at(i)[3]
            return lorentz(px, py, pz, pE)

        nZlep = 0
        p4 = lorentz()
        for i in range(lheParticles.NUP):
            if abs(lheParticles.IDUP[i]) in [11, 13, 15]:
                nZlep += 1
                p4 += lhep4(i)
        if nZlep == 2:
            hist.Fill(p4.pt(), weight)
        else:
            print "bad event"
            for i in range(lheParticles.NUP):
                print "part %d id %d pt %f" % (i, lheParticles.IDUP[i], lhep4(i).pt())
    hist.Scale(xs/sumW)


fillhist(hInclusive, eventsInclusive, 5938. * 1e3)

fillhist(h0to50, events0to50, 5.379e+03 * 1e3)

fillhist(h50to100, events50to100, 354.6 * 1e3)

fillhist(h100to250, events100to250, 83.05 * 1e3)

events250to400 = Events([
    'root://cmsxrootd.fnal.gov//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_Pt-250To400_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/120000/0A953D30-0BCD-E611-B4CB-0CC47AD99112.root',
])
fillhist(h250to400, events250to400, 3.043 * 1e3)

hInclusive.Draw('histex0')
h50to100.Draw('histex0same')
h0to50.Draw('histex0same')
h100to250.Draw('histex0same')
h250to400.Draw('histex0same')
hstitched = h50to100.Clone("stitched")
hstitched.Add(h0to50)
hstitched.Add(h100to250)
hstitched.Add(h250to400)
hstitched.SetTitle("Stitched")
hstitched.SetLineColor(ROOT.kBlack)
hstitched.SetLineStyle(ROOT.kDashed)
hstitched.Draw('histex0same')
ROOT.gPad.Print("ptStitch.root")
