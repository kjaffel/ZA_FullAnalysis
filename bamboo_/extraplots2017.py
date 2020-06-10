import os.path
import sys
zabPath = os.path.dirname(__file__)
if zabPath not in sys.path:
    sys.path.append(zabPath)

from bambooToOls import Plot
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op

import utils
from utils import *


def zoomplots(oslepsel, oslep_plus2jet_sel, leptons, jets, suffix, uname):
    plots = []
    binScaling=1
    Jets_ = (jets[0].p4 if suffix=="boosted" else(jets[0].p4+jets[1].p4))
    for i in range(2):
        leptonptCut = (25. if i == 0 else( 10. if uname[-1]=='u' else( 15.)))
        plots.append(Plot.make1D(f"{uname}_lep{i+1}_zoom_pt", leptons[i].pt, oslepsel,
                EqB(60 // binScaling, leptonptCut, 60.), title=f"{utils.getCounter(i+1)} Lepton pT [GeV]" ,
                plotopts=utils.getOpts(uname, **{"log-y": False})))
    
    plots.append(Plot.make1D(f"{uname}_zoom_llpT", (leptons[0].p4 + leptons[1].p4).Pt(), oslepsel, 
            EqB(60, 0., 60.), title= "dilepton P_{T} [GeV]", 
            plotopts=utils.getOpts(uname, **{"log-y": False})))
        
    plots.append(Plot.make1D("{0}_{1}_zoom_mjj".format(uname, suffix),
                op.invariant_mass(Jets_), oslep_plus2jet_sel,
                EqB(60 // binScaling, 0., 60.), 
                title="mjj [GeV]", plotopts=utils.getOpts(uname, **{"log-y": False})))
    
    EqBIns = EqB(60 // binScaling, 120., 200.)
    plots.append(Plot.make1D("{0}_{1}_zoom_mlljj".format(uname, suffix), 
                (leptons[0].p4 +leptons[1].p4+Jets_).M(), oslep_plus2jet_sel, EqBIns, 
                title="mlljj [GeV]", plotopts=utils.getOpts(uname, **{"log-y": False})))
    
    return plots

def ptcuteffectOnJetsmultiplicty(TwoLepsel, leptons, jets_noptcut, jet_ptcut, corrMET, era, uname):
    plots = []
    binScaling=1
    for i in range(2):
        
        leptonptCut = (25. if i == 0 else( 10. if uname[-1]=='u' else( 15. if uname[-1]=='l' else(0.)))) 
        
        for idx, jets in enumerate([jets_noptcut, jet_ptcut]):
            
            j= ('noptcut' if idx ==0 else('ptcut'))
            jetcut =(0. if idx ==0 else (30.))
            EqBin= EqB(60 // binScaling, jetcut, 200.)
            
            sel_noMETcut = TwoLepsel.refine( '2lep_%s_jets_%s_noMETcut_plus_cut_on_jets_length_sup_%s'%(uname.lower(), j, i), cut = [op.rng_len(jets) > i ])
            sel_METcut = sel_noMETcut.refine( '2lep_%s_jets_%s_METcut_plus_cut_on_jets_length_sup_%s'%(uname.lower(), j, i), cut = [corrMET.pt < 80.])
            
            for sel, suffix in zip( [sel_noMETcut, sel_METcut ],['%s_noMETcut'%(j),'%s_METcut'%(j)]):
            
                plots.append(Plot.make1D(f"{uname}_resolved_jet{i+1}_{suffix}_pT".format(suffix=suffix), jets[i].pt, sel,
                            EqBin, title=f"{utils.getCounter(i+1)} jet p_{{T}} [GeV]",
                            plotopts=utils.getOpts(uname, **{"log-y": True})))
                plots.append(Plot.make1D(f"{uname}_resolved_jet{i+1}_{suffix}_eta".format(suffix=suffix), jets[i].eta, sel,
                            EqB(50 // binScaling, -2.5, 2.5), title=f"{utils.getCounter(i+1)} jet eta",
                            plotopts=utils.getOpts(uname)))
                plots.append(Plot.make1D(f"{uname}_resolved_jet{i+1}_{suffix}_phi".format(suffix=suffix), jets[i].phi, sel,
                            EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} jet #phi", plotopts=utils.getOpts(uname)))
                plots.append(Plot.make1D(f"{uname}_resolved_{suffix}_lenOnjets_sup{i}_Jet_mulmtiplicity".format(suffix=suffix, i=i), op.rng_len(jets), sel,
                            EqB(7, 0., 7.), title="Jet mulmtiplicity",
                            plotopts=utils.getOpts(uname, **{"log-y": True})))

            
                plots.append(Plot.make1D(f"{uname}_%s_lep{i+1}_pt"%suffix, leptons[i].pt, sel,
                        EqB(60 // binScaling, leptonptCut, 200.), title=f"{utils.getCounter(i+1)} Lepton pT [GeV]" ,
                        plotopts=utils.getOpts(uname, **{"log-y": True})))
                plots.append(Plot.make1D(f"{uname}_%s_lep{i+1}_eta"%suffix, leptons[i].eta, sel,
                        EqB(50 // binScaling, -2.5, 2.5), title=f"{utils.getCounter(i+1)} Lepton eta",
                        plotopts=utils.getOpts(uname, **{"log-y": True})))
                plots.append(Plot.make1D(f"{uname}_%s_lep{i+1}_phi"%suffix, leptons[i].phi, sel,
                        EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} Lepton #phi",
                        plotopts=utils.getOpts(uname, **{"log-y": True}))) 
            
                #plots.append(Plot.make1D(f"{uname}_%s_llpT"%suffix, (leptons[0].p4 + leptons[1].p4).Pt(), sel, 
                #        EqB(60, 0., 200.), title= "dilepton P_{T} [GeV]", 
                #        plotopts=utils.getOpts(uname, **{"log-y": True})))
                    
                #plots.append(Plot.make1D(f"{uname}_%s_mll"%suffix, op.invariant_mass(leptons[0].p4, leptons[1].p4), sel, 
                #        EqB(60, 70., 120.), title= "mll [GeV]", 
                #        plotopts=utils.getOpts(uname, **{"log-y": True})))
            
    return plots

def makeJetPlots(sel, jets, uname, suffix, era, cuts):
    binScaling=1
    plots = []
    maxJet=( 1 if suffix=="boosted" else(2))
    for i in range(maxJet):
        if suffix=="boosted":
            EqBin= EqB(60 // binScaling, 200, 850.)
        elif suffix=="resolved":
            jet_ptcut =(30. if era!='2016' else (20.))
            EqBin= EqB(60 // binScaling, jet_ptcut, 650.)
        else:
            raise RuntimeError('ERROR: {0} Unknown suffix '.format(suffix))
        
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet{i+1}_pt_{cuts}".format(suffix=suffix, cuts=cuts), jets[i].pt, sel,
                    EqBin, title=f"{utils.getCounter(i+1)} jet p_{{T}} [GeV]",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet{i+1}_eta_{cuts}".format(suffix=suffix, cuts=cuts), jets[i].eta, sel,
                    EqB(50 // binScaling, -2.4, 2.4), title=f"{utils.getCounter(i+1)} jet eta",
                    plotopts=utils.getOpts(uname, **{"log-y": False})))
        plots.append(Plot.make1D(f"{uname}_{suffix}_jet{i+1}_phi_{cuts}".format(suffix=suffix, cuts=cuts), jets[i].phi, sel,
                    EqB(50 // binScaling, -3.1416, 3.1416), title=f"{utils.getCounter(i+1)} jet #phi", plotopts=utils.getOpts(uname, **{"log-y": False})))
    return plots

puScenarios = {
    "2016" : "Moriond17",
    "2017" : "Fall17",
    "2018" : "Autumn18"
    }

puIDSFLib = {
        f"{year}_{wp}" : {
            f"{eom}_{mcsf}" : os.path.join('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_',
                "PileupJetID", "fromPieter", f"PUID_80X_{eom}_{mcsf}_{year}_{wp}.json")
            for eom in ("eff", "mistag") for mcsf in ("mc", "sf")
        }
    for year in ("2016", "2017", "2018") for wp in "LMT"
    }

import bamboo.scalefactors

def makePUIDSF(jets, year=None, wp=None, wpToCut=None):
    sfwpyr = puIDSFLib[f"{year}_{wp}"]
    sf_eff = bamboo.scalefactors.get_scalefactor("lepton", "eff_sf"   , sfLib=sfwpyr, paramDefs=bamboo.scalefactors.binningVariables_nano)
    sf_mis = bamboo.scalefactors.get_scalefactor("lepton", "mistag_sf", sfLib=sfwpyr, paramDefs=bamboo.scalefactors.binningVariables_nano)
    eff_mc = bamboo.scalefactors.get_scalefactor("lepton", "eff_mc"   , sfLib=sfwpyr, paramDefs=bamboo.scalefactors.binningVariables_nano)
    mis_mc = bamboo.scalefactors.get_scalefactor("lepton", "mistag_mc", sfLib=sfwpyr, paramDefs=bamboo.scalefactors.binningVariables_nano)
    jets_m50 = op.select(jets, lambda j : j.pt < 50.)
    wFail = op.extMethod("scalefactorWeightForFailingObject", returnType="double")
    return op.rng_product(jets_m50, lambda j : op.switch(j.genJet.isValid,
        op.switch(wpToCut[wp](j), sf_eff(j), wFail(sf_eff(j), eff_mc(j))),
        op.switch(wpToCut[wp](j), sf_mis(j), wFail(sf_mis(j), mis_mc(j)))
        ))

def perCatPlots_sameVar(uName, categories, variable, binning, saveSeparate=True, combPrefix=None, nDim=1, **kwargs):
    plotFun = getattr(Plot, "make{0:d}D".format(nDim))
    catPlots = [ plotFun("_".join((catSel.name, uName)), variable, catSel, binning, **kwargs) for catSel in categories.values() ]
    combPlot = SummedPlot(("_".join((combPrefix, uName)) if combPrefix is not None else uName), catPlots)
    if saveSeparate:
        return catPlots + [ combPlot ]
    else:
        return [ combPlot ]

def leptonPlots_candVar(flavour, uName, categories, varFun, binning, saveSeparate=False, saveIntermediate=True, saveTotal=False, combPrefix=None, **kwargs):
    allPlots = []
    intCombPlots = []
    for i in range(2):
        catPlots = [ Plot.make1D("_".join((catSel.name, flavour, str(i), uName)), varFun(cand[i]), catSel, binning, **kwargs) for catName, (catSel, cand) in categories.items() if catName[2*i:2*(i+1)] == flavour ]
        intCombPlots.append(SummedPlot(("_".join((combPrefix, flavour, str(i), uName)) if combPrefix is not None else "_".join((uName, str(i), flavour))), catPlots))
        allPlots += catPlots
        toSave = []
    if saveSeparate:
        toSave += allPlots
    if saveIntermediate:
        toSave += intCombPlots
    if saveTotal:
        toSave.append(SummedPlot(("_".join((combPrefix, flavour, uName)) if combPrefix is not None else "_".join((uName, flavour))), allPlots))
    return toSave

def choosebest_jetid_puid(t, muons, electrons, osllSelCand, year, sample, isMC):
    plots = []
    binScaling = 1
    # look at PUID for 2017
    sorted_AK4jets=op.sort(t.Jet, lambda j : -j.pt)
    all_clean_jets = op.select(sorted_AK4jets, lambda j : op.AND(
        op.NOT(op.rng_any(muons, lambda l : op.deltaR(l.p4, j.p4) < 0.4)),
        op.NOT(op.rng_any(electrons, lambda l : op.deltaR(l.p4, j.p4) < 0.4))
        ))
    jet_sel_kin = {
        #"PT20"      : lambda j : j.pt > 20.,
        #"PT30"      : lambda j : j.pt > 30.,
        #"CentrPT20" : lambda j : op.AND(op.abs(j.eta) < 2.4, j.pt > 20.),
        "CentrPT30" : lambda j : op.AND(op.abs(j.eta) < 2.4, j.pt > 30.)
        }
    jet_collections_id2017_beforeClean = {
        "T"        : op.select(all_clean_jets, lambda j : j.jetId & 0x2),
        "TLepVeto" : op.select(all_clean_jets, lambda j : j.jetId & 0x4),
        }
    jet_puID_wp = {
        "L"   : lambda j : j.puId & 0x4,
        "M"   : lambda j : j.puId & 0x2,
        "T"   : lambda j : j.puId & 0x1
        }
    for jet_id, jets_noKin in jet_collections_id2017_beforeClean.items():
        jets_kin = { kinNm : op.select(jets_noKin, kinSel) for kinNm, kinSel in jet_sel_kin.items() }
        for puWP, puSel in jet_puID_wp.items():
            w_noKin = None
            if isMC:
                w_noKin = makePUIDSF(jets_noKin, year=year, wp=puWP, wpToCut=jet_puID_wp)
            
            OsLepplusJets_noKinematics = dict((catName, catSel.refine(f"OsLeptonsPlusJets_withonly_jId{jet_id}_puId{puWP}_cuts_{catName}", weight=w_noKin))
                for catName, (cand, catSel) in osllSelCand.items())
            
            for kinNm, kinSel in jet_sel_kin.items():
                w_pu = None
                ak4jets_corr = op.select(jets_kin[kinNm], lambda j :  op.switch(j.pt < 50, puSel(j), op.c_bool(True)))
                #ak4jets_corr = op.select(jets_kin[kinNm], lambda j : op.OR(j.pt < 50, puSel(j)))
                if isMC:
                    w_pu = makePUIDSF(ak4jets_corr, year=year, wp=puWP, wpToCut=jet_puID_wp)
                
                ## selections
                OsLepplusJets = dict((catName, catSel.refine(f"OsLepplusJets_jId{jet_id}_puId{puWP}_{kinNm}_Eta2p4_{catName}", weight=w_pu))
                    for catName, (cand, catSel) in osllSelCand.items())
                OsLepplus_atleast2Jets = dict((catName, catSel.refine(f"OsLepplus_atleast2_jId{jet_id}_puId{puWP}_{kinNm}_Eta2p4_{catName}", cut=[op.rng_len(ak4jets_corr) > 1], weight=w_pu))
                    for catName, (cand, catSel) in osllSelCand.items())
                OsLepplus_exactly2Jets = dict((catName, catSel.refine(f"OsLepplus_Only2_jId{jet_id}_puId{puWP}_{kinNm}_Eta2p4_{catName}", cut=[op.rng_len(ak4jets_corr) ==2], weight=w_pu))
                    for catName, (cand, catSel) in osllSelCand.items())
                
                plots += perCatPlots_sameVar("jetETAPHI", OsLepplusJets,
                        (op.map(ak4jets_corr, lambda j : j.eta), op.map(ak4jets_corr, lambda j : j.phi)),
                        (EqB(50, -2.5, 2.5), EqB(50,  -3.1416, 3.1416)), combPrefix="OsLepplusJets", nDim=2)
                #plots += perCatPlots_sameVar(f"nJet{kinNm}", OsLepplusJets_noKinematics, op.rng_len(ak4jets_corr),
                #        EqB(12, 0., 12.), saveSeparate=True, combPrefix="OsLepplusJets_noKinematics")
                
                sv_mass=op.map(t.SV, lambda sv: sv.mass)
                sv_eta=op.map(t.SV, lambda sv: sv.eta)
                sv_phi=op.map(t.SV, lambda sv: sv.phi)
                sv_pt=op.map(t.SV, lambda sv: sv.pt)
                for sel , suffix in zip([OsLepplus_atleast2Jets, OsLepplus_exactly2Jets],['_atleast2_', '_Only2_']):
                
                    plots += perCatPlots_sameVar("nJet", sel, op.rng_len(ak4jets_corr),
                            EqB(12, 0., 12.), saveSeparate=True, combPrefix="OsLepplusJets_%s"%suffix)
                    plots += perCatPlots_sameVar("vtx", sel, t.PV.npvsGood,
                            EqB(60 // binScaling, 0., 80.), saveSeparate=True, combPrefix="OsLepplus_%s_aka4Jets"%suffix)
                    plots += perCatPlots_sameVar("sv_mass", sel, sv_mass,
                            EqB(50 // binScaling, 0., 450.), saveSeparate=True, combPrefix="OsLepplus_%s_aka4Jets"%suffix)
                    plots += perCatPlots_sameVar("sv_eta", sel, sv_eta,
                            EqB(50 // binScaling,-2.4, 2.4), saveSeparate=True, combPrefix="OsLepplus_%s_aka4Jets"%suffix)
                    plots += perCatPlots_sameVar("sv_phi", sel, sv_phi,
                            EqB(50 // binScaling, -3.1416, 3.1416), saveSeparate=True, combPrefix="OsLepplus_%s_aka4Jets"%suffix)
                    plots += perCatPlots_sameVar("sv_pt", sel, sv_pt,
                            EqB(50 // binScaling, 0., 450.), saveSeparate=True, combPrefix="OsLepplus_%s_aka4Jets"%suffix)
                    kinematic_cuts = suffix + 'jId_'+ jet_id+'_puId'+puWP+'_'+kinNm+ '_Eta2p4'
                    for catName, lepjSel in sel.items(): 
                        plots +=makeJetPlots(lepjSel, ak4jets_corr, catName, 'resolved', year, kinematic_cuts)
    return plots

def varsCutsPlotsforLeptons(lepton, sel, uname):
   plots = []
   # TODO this not going to work for mixed cat, no time to do this  now , fix it later 
   Flav = ('Electron' if uname[-1]=='l' else('Muon' if uname[-1]=='u' else('comb')))
   for i in range(2):
       plots.append(Plot.make1D(f"%s{i+1}_sip3d_%s"%(Flav,uname), lepton[i].sip3d, sel,
                            EqB(100, -8., 8.), title=f"{utils.getCounter(i+1)} sip3d",
                            plotopts=utils.getOpts(uname)))
       plots.append(Plot.make1D(f"%s{i+1}_miniPFRelIso_all_%s"%(Flav,uname), lepton[i].miniPFRelIso_all, sel,
                            EqB(100, 0., .4), title=f"{utils.getCounter(i+1)} miniPFRelIso_all",
                            plotopts=utils.getOpts(uname)))
       if Flav == 'Electron':
           plots.append(Plot.make1D(f"%s{i+1}_dxy_%s"%(Flav,uname), lepton[i].dxy, sel,
                                EqB(100, -.05, .05), title=f"{utils.getCounter(i+1)} dxy",
                                plotopts=utils.getOpts(uname)))
           plots.append(Plot.make1D(f"%s{i+1}_dz_%s"%(Flav, uname), lepton[i].dz, sel,
                                EqB(100, -.1, .1), title=f"{utils.getCounter(i+1)} dz",
                                plotopts=utils.getOpts(uname)))
   return plots


def LeptonsInsideJets(jets, sel, uname):
    plots=[]
    binScaling=1

    plots.append(Plot.make1D(f"%s_Jet_nElectrons"%uname, op.rng_len(jets.nElectrons), sel,
            EqB(7, 0., 7.), title="Jet_nElectrons",
            plotopts=utils.getOpts(uname, **{"log-y": True})))
    plots.append(Plot.make1D(f"%s_Jet_nMuons"%uname, op.rng_len(jets.nMuons), sel,
            EqB(7, 0., 7.), title="Jet_nMuons",
            plotopts=utils.getOpts(uname, **{"log-y": True})))
        
    return plots 
