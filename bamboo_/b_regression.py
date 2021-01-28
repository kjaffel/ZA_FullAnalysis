import os, os.path
import sys

zabPath = os.path.dirname(__file__)
if zabPath not in sys.path:
        sys.path.append(zabPath)
import logging
logger = logging.getLogger("H->ZA->b-regression-studies")

import utils
from utils import * 
import HistogramTools as HT
from ZAtollbb import NanoHtoZABase, makeYieldPlots

from bamboo.analysismodules import NanoAODHistoModule, HistogramsModule
from bamboo import treefunctions as op
from bamboo.plots import Plot, SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo.plots import VariableBinning as VarBin

def bJetEnergyRegression(jets):
    return op.map(jets, lambda j : op.construct("ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>>", (j.pt*j.bRegCorr, j.eta, j.phi, j.mass*j.bRegCorr)))

#def bJetEnergyRegression(jet_withnoregression):
#    return op.map( jet_withnoregression, lambda j: op.construct("ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float> >",
#                                                            ( op.product( j.p4.pt, op.multiSwitch( (j.hadronFlavour == 5 , j.bRegCorr),
#                                                                                                (j.hadronFlavour == 4, j.cRegCorr),
#                                                                                                    op.c_float(1) ) ), 
#                                                            j.p4.eta, j.p4.phi, 
#                                                            op.product ( j.mass, op.multiSwitch( (j.hadronFlavour == 5 , j.bRegCorr),
#                                                                                                    (j.hadronFlavour == 4, j.cRegCorr),
#                                                                                                    op.c_float(1) ))  )) )
scalesfactorsLIB = {
    "DeepFlavour": {
                year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
                    {"2016": "2016_legacy_ReReco/Btag/DeepJet_2016LegacySF_V1.csv", "2017": "2017/Btag/DeepFlavour_94XSF_V4_B_F.csv", "2018": "2018/Btag/DeepJet_102XSF_V1.csv"}.items() },
    "DeepCSV" :{
        "Ak4": 
            {
                year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
                    {"2016":"2016_legacy_ReReco/Btag/DeepCSV_2016LegacySF_V1.csv" , "2017": "2017/Btag/DeepCSV_94XSF_V5_B_F.csv" , "2018": "2018/Btag/DeepCSV_102XSF_V1.csv"}.items() },
        "softdrop_subjets":
            {
                year: os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Inputs", csv) for year, csv in
                    {"2016":"2016_legacy_ReReco/Btag/subjet_DeepCSV_2016LegacySF_V1.csv" , "2017": "2017/Btag/subjet_DeepCSV_94XSF_V4_B_F_v2.csv" , "2018": "2018/Btag/subjet_DeepCSV_102XSF_V1.csv"}.items() },
        }
    }
class EnergyRegression(NanoHtoZABase, HistogramsModule):
    def __init__(self, args):
        super(EnergyRegression, self).__init__(args)
    
        self.Energyregression_OnAlljets = self.args.Onjets
        self.Energyegression_Onbtaggedjets = self.args.Onbjets
    def addArgs(self, parser):
        super(EnergyRegression, self).addArgs(parser)
        parser.add_argument("-Onjets", "--Onjets", action="store_true", help="Bjets Energy Regression will be applied on all Jets ")
        parser.add_argument("-Onbjets", "--Onbjets", action="store_true", help="Bjets Energy Regression will be applied Only on those that pass the b-tag discr score for specific tagger and for specif wp ")

    def definePlots(self, t, noSel, sample=None, sampleCfg=None):
        from bambooToOls import Plot
        from bamboo.plots import CutFlowReport
        from bamboo.root import addIncludePath, loadHeader
        from bamboo.scalefactors import BtagSF

        noSel, PUWeight, categories, isDY_reweight, WorkingPoints, btagging, deepBFlavScaleFactor, deepB_AK4ScaleFactor, deepB_AK8ScaleFactor, AK4jets, AK8jets, fatjets_nosubjettinessCut, bjets_resolved, bjets_boosted, CleanJets_fromPileup, electrons, muons, MET, corrMET, PuppiMET, elRecoSF_highpt, elRecoSF_lowpt = super(EnergyRegression, self).defineObjects(t, noSel, sample, sampleCfg)

        year = sampleCfg.get("era") if sampleCfg else None
        isMC = self.isMC(sample)
        binScaling = 1
        plots = []
        yield_object = makeYieldPlots()
        scenario1_Bjetsregression_OnAlljets = True
        scenario2_Bjetsregression_Onbtaggedjets = True

        addIncludePath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "include"))
        loadHeader("BTagEffEvaluator.h")

        Jets_dic = { 'with_bjetEnergyRegression': bJetEnergyRegression(AK4jets),
                    'without_bjetEnergyRegression': AK4jets }
       
        pathtoRoOtmaps = { '2016': "/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/ver.20_10_08/results/summedProcessesForEffmaps/summedProcesses_2016_ratios.root",
                           '2017': "/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2017Results/ver.20_10_06/fix_bug_cause_missing_histograms/results/summedProcessesForEffmaps/summedProcesses_2017_ratios.root",
                           '2018': "/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2018Results/ver.20_10_06/fix_bug_causing_missingHistograms/results/summedProcessesForEffmaps/summedProcesses_2018_ratios.root"
                        }

        
        for uname, (dilepton, catSel) in categories.items():
            optstex = ('$e^+e^-$' if uname=="ElEl" else( '$\mu^+\mu^-$' if uname =="MuMu" else( '$\mu^+e^-$' if uname=="MuEl" else('$e^+\mu^-$'))))
            jet_ptcut =(30. if year!='2016' else (20.))
            eqBin_pt = EqB(60 // binScaling, jet_ptcut, 650.)
            
            
            if self.Energyregression_OnAlljets :
                for cond, jets in Jets_dic.items():
                    jj_p4 = (( jets[0].p4 + jets[1].p4 ) if 'without_' in cond else ( jets[0] + jets[1] ) )
                    
                    sel = catSel.refine(f"twolep_{uname}_atleast_twojets_resolved_selection_{cond}", cut=[ op.rng_len(jets) > 1])
                    yield_object.addYields(sel,f"hasOslep_{uname}_{cond}_correctionOnjets",f"OS leptons + 2 AK4Jets + {cond} (channel : {uname})")
                    plots.append(Plot.make1D(f"{uname}_resolved_mjj_{cond}",
                                    jj_p4.M(), sel,
                                    EqB(60 // binScaling, 0., 650.),
                                    title="mjj [GeV]", plotopts=utils.getOpts(uname)))
                    plots.append(Plot.make1D(f"{uname}_resolved_jj_PT_{cond}",
                                    jj_p4.Pt(), sel,
                                    EqB(60 // binScaling, 0., 450.),
                                    title="di-jets P_{T} [GeV]", plotopts=utils.getOpts(uname)))
                    
            
                    for i in range(2):
                        j_pt = (jets[i].pt if 'without_' in cond else (jets[i].Pt()))
                        j_mass = (jets[i].mass if 'without_' in cond else (jets[i].M()))
                        
                        plots.append(Plot.make1D(f"{uname}_resolved_jet{i+1}_pT_{cond}",
                                j_pt, sel,
                                EqB(60 // binScaling, 0., 450.),
                                title=f"{utils.getCounter(i+1)} Jet pT [GeV]", plotopts=utils.getOpts(uname)))
                        plots.append(Plot.make1D(f"{uname}_resolved_jet{i+1}_mass_{cond}",
                                j_mass, sel,
                                EqB(60 // binScaling, 0., 650.),
                                title=f"{utils.getCounter(i+1)} Jet mass [GeV]", plotopts=utils.getOpts(uname)))
                # FIXME # This's won't work : AttributeError: Type ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<float>> has no member btagDeepFlavB
                #cleaned_AK4JetsByDeepFlav = op.sort(bJetEnergyRegression(AK4jets), lambda j: -j.btagDeepFlavB)
                #cleaned_AK4JetsByDeepB = op.sort(bJetEnergyRegression(AK4jets), lambda j: -j.btagDeepB)
                #
                #bjets_resolved_regressed = {}
                #WorkingPoints = ["M"]
                #for tagger  in btagging.keys():
                #    bJets_regressed_AK4_deepflavour ={}
                #    bJets_regressed_AK4_deepcsv ={}
                #    for wp in sorted(WorkingPoints):

                #        suffix = ("loose" if wp=='L' else ("medium" if wp=='M' else "tight"))
                #        idx = ( 0 if wp=="L" else ( 1 if wp=="M" else 2))
                #        if tagger=="DeepFlavour":
                #            bJets_regressed_AK4_deepflavour[wp] = op.select(cleaned_AK4JetsByDeepFlav, lambda j : j.btagDeepFlavB >= btagging[tagger][year][idx] )
                #            bjets_resolved_regressed[tagger]=bJets_regressed_AK4_deepflavour
                #        elif tagger == "DeepCSV":
                #            bJets_regressed_AK4_deepcsv[wp] = op.select(cleaned_AK4JetsByDeepB, lambda j : j.btagDeepB >= btagging[tagger][year][idx] )
                #            bjets_resolved_regressed[tagger]=bJets_regressed_AK4_deepcsv
                #
                #bJets_regressed_resolved_PassdeepcsvWP=safeget(bjets_resolved_regressed, "DeepCSV", 'M')
                #bJets_regressed_resolved_PassdeepflavourWP=safeget(bjets_resolved_regressed, "DeepFlavour", 'M')
                #
                #TwoLep2Jets = catSel.refine(f"twolep_{uname}_atleast_twojets_resolved_selection", cut=[ op.rng_len(bJetEnergyRegression(AK4jets)) > 1])
                #regsel = TwoLep2Jets.refine(f"twolep_{uname}_Alljets_MappedWithBRegCorr_beforeCutOnbtagScore_atleast_twobjets_DeepCSVM_resolved_selection", cut=[ corrMET.pt < 80., op.rng_len(bJets_regressed_resolved_PassdeepcsvWP) > 1], weight=deepcsv_bTagWeight)
                #regbb_p4 = ( bJets_regressed_resolved_PassdeepcsvWP[0].p4 + bJets_regressed_resolved_PassdeepcsvWP[1].p4 ) 
                #plots.append(Plot.make1D(f"{uname}_Alljets_MappedWithBRegCorr_resolved_mbb_DeepCSVM_METcut_bTagWeight",
                #            regbb_p4.M(), regsel,
                #            EqB(60 // binScaling, 0., 650.),
                #            title="mbb [GeV]", plotopts=utils.getOpts(uname)))
                #plots.append(Plot.make1D(f"{uname}_Alljets_MappedWithBRegCorr_resolved_bb_PT_DeepCSVM_METcut_bTagWeight",
                #            regbb_p4.Pt(), regsel,
                #            EqB(60 // binScaling, 0., 450.),
                #            title="di-bjets P_{T} [GeV]", plotopts=utils.getOpts(uname)))
                #        
            if self.Energyegression_Onbtaggedjets :
                
                run2_bTagEventWeight_PerWP = {}
                BJets_dic = {}
                
                TwoLep2Jets = catSel.refine(f"twolep_{uname}_atleast_twojets_resolved_selection", cut=[ op.rng_len(AK4jets) > 1]) 
                for wp in WorkingPoints :

                    idx = ( 0 if wp=="L" else ( 1 if wp=="M" else 2)) 
                    if os.path.exists(pathtoRoOtmaps[year]):
                        bTagEff_deepcsvAk4 = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "resolved", "deepcsv", {%s});'%(pathtoRoOtmaps[year], wp, btagging['DeepCSV'][year][idx]))
                        bTagEff_deepflavour = op.define("BTagEffEvaluator", 'const auto <<name>> = BTagEffEvaluator("%s", "%s", "resolved", "deepflavour", {%s});'%(pathtoRoOtmaps[year], wp, btagging['DeepFlavour'][year][idx]))
                    else:
                        raise RuntimeError(f"{year} efficiencies maps not found !")

                    bJets_resolved_PassdeepcsvWP=safeget(bjets_resolved, "DeepCSV", wp)
                    bJets_resolved_PassdeepflavourWP=safeget(bjets_resolved, "DeepFlavour", wp)
                   
                    csv_deepcsv = scalesfactorsLIB['DeepCSV']['Ak4'][year]
                    csv_deepflavour = scalesfactorsLIB['DeepFlavour'][year]
                    OP= ("Loose" if wp=='L' else ("Medium" if wp=='M' else "Tight"))

                    btagSF_deepcsv= BtagSF('deepcsv', csv_deepcsv, 
                                                      wp=OP, 
                                                      sysType="central", 
                                                      otherSysTypes=["up", "down"],
                                                      systName= f'mc_eff_deepcsv{wp}', 
                                                      measurementType={"B": "comb", "C": "comb", "UDSG": "incl"}, 
                                                      sel= noSel,
                                                      uName=f'sf_eff_{uname}_On{sample}_deepcsv{wp}')
                    btagSF_deepflavour= BtagSF('deepflavour', csv_deepflavour, 
                                                              wp=OP, 
                                                              sysType="central", 
                                                              otherSysTypes=["up", "down"],
                                                              systName= f'mc_eff_deepflavour{wp}', 
                                                              measurementType={"B": "comb", "C": "comb", "UDSG": "incl"}, 
                                                              sel= noSel,
                                                              uName=f'sf_eff_{uname}_On{sample}_deepflavour{wp}')

                    deepcsv_bTagWeight = None
                    deepflavour_bTagWeight = None
                    deepcsv_bTagWeightReg = None
                    deepflavour_bTagWeightReg = None
                    
                    cleaned_AK4JetsByDeepFlav = op.sort(AK4jets, lambda j: -j.btagDeepFlavB)
                    cleaned_AK4JetsByDeepB = op.sort(AK4jets, lambda j: -j.btagDeepB)

                    if isMC:
                        bTagSF_DeepCSVPerJet = op.map(cleaned_AK4JetsByDeepB, lambda j: bTagEff_deepcsvAk4.evaluate(j.hadronFlavour, j.btagDeepB, j.pt, op.abs(j.eta), btagSF_deepcsv(j)))
                        bTagSF_DeepCSVPerJetReg = op.map(cleaned_AK4JetsByDeepB, lambda j: bTagEff_deepcsvAk4.evaluate(j.hadronFlavour, j.btagDeepB, j.pt*j.bRegCorr, op.abs(j.eta), btagSF_deepcsv(j)))
                        
                        bTagSF_DeepFlavourPerJetReg = op.map(cleaned_AK4JetsByDeepFlav, lambda j: bTagEff_deepflavour.evaluate(j.hadronFlavour, j.btagDeepFlavB, j.pt*j.bRegCorr, op.abs(j.eta), btagSF_deepflavour(j)))
                        bTagSF_DeepFlavourPerJet = op.map(cleaned_AK4JetsByDeepFlav, lambda j: bTagEff_deepflavour.evaluate(j.hadronFlavour, j.btagDeepFlavB, j.pt, op.abs(j.eta), btagSF_deepflavour(j)))
                        
                        deepcsv_bTagWeight = op.rng_product(bTagSF_DeepCSVPerJet)
                        deepcsv_bTagWeightReg = op.rng_product(bTagSF_DeepCSVPerJetReg)
                        
                        deepflavour_bTagWeight = op.rng_product(bTagSF_DeepFlavourPerJet)
                        deepflavour_bTagWeightReg = op.rng_product(bTagSF_DeepFlavourPerJetReg)
                        
    
                        run2_bTagEventWeight_PerWP = {  
                                    'DeepCSV{0}'.format(wp): 
                                                { 'with_bjetEnergyRegression': deepcsv_bTagWeightReg,
                                                    'without_bjetEnergyRegression': deepcsv_bTagWeight }, 
                                    'DeepFlavour{0}'.format(wp): 
                                                { 'with_bjetEnergyRegression': deepflavour_bTagWeightReg,
                                                    'without_bjetEnergyRegression': deepflavour_bTagWeight } 
                                        }


                        BJets_dic = {  
                                "DeepCSV{0}".format(wp): {
                                            'with_bjetEnergyRegression': bJetEnergyRegression(bJets_resolved_PassdeepcsvWP),
                                                'without_bjetEnergyRegression': bJets_resolved_PassdeepcsvWP },
                                "DeepFlavour{0}".format(wp): {
                                            'with_bjetEnergyRegression': bJetEnergyRegression(bJets_resolved_PassdeepflavourWP),
                                                'without_bjetEnergyRegression': bJets_resolved_PassdeepflavourWP }
                                    }
                    
                    for taggerWP, bEnergyRegONOF in BJets_dic.items():
                        for cond, bjets in bEnergyRegONOF.items():

                            bb_p4 = (( bjets[0].p4 + bjets[1].p4 ) if 'without_' in cond else ( bjets[0] + bjets[1] ) )
                            llbb_p4 = ( dilepton[0].p4 +dilepton[1].p4 + bb_p4)
                            
                            sel = TwoLep2Jets.refine(f"twolep_{uname}_atleast_twobjets_{taggerWP}_resolved_selection_{cond}", cut=[ corrMET.pt < 80., op.rng_len(bjets) > 1], weight=run2_bTagEventWeight_PerWP[taggerWP][cond])
                            yield_object.addYields(sel,f"hasOslep_{uname}_{cond}_{taggerWP}_correctionOnbtaggedjets",f"OS leptons + 2 AK4BJets {taggerWP} + METcut + {cond} (channel : {optstex})")
                                
                            plots.append(Plot.make1D(f"{uname}_OnlyjetsPassBtagDiscrScore_MappedWithBRegCorr_resolved_mbb_{taggerWP}_METcut_bTagWeight_{cond}",
                                        bb_p4.M(), sel,
                                        EqB(60 // binScaling, 0., 650.),
                                        title="mbb [GeV]", plotopts=utils.getOpts(uname)))
                            plots.append(Plot.make1D(f"{uname}_OnlyjetsPassBtagDiscrScore_MappedWithBRegCorr_resolved_mllbb_{taggerWP}_METcut_bTagWeight_{cond}",
                                        llbb_p4.M(), sel,
                                        EqB(60 // binScaling, 0., 650.),
                                        title="mllbb [GeV]", plotopts=utils.getOpts(uname)))
                            plots.append(Plot.make1D(f"{uname}_OnlyjetsPassBtagDiscrScore_MappedWithBRegCorr_bb_PT_{taggerWP}_METcut_bTagWeight_{cond}",
                                        bb_p4.Pt(), sel,
                                        EqB(60 // binScaling, 0., 450.),
                                        title="di-bjets P_{T} [GeV]", plotopts=utils.getOpts(uname)))
            
                            for i in range(2):
                                bj_pt = (bjets[i].pt if 'without_' in cond else (bjets[i].Pt()))
                                bj_mass = (bjets[i].mass if 'without_' in cond else (bjets[i].M()))
                            
                                plots.append(Plot.make1D(f"{uname}_OnlyjetsPassBtagDiscrScore_MappedWithBRegCorr_resolved_bjet{i+1}_pT_{taggerWP}_METcut_bTagWeight_{cond}",
                                        bj_pt, sel,
                                        EqB(60 // binScaling, 0., 450.),
                                        title=f"{utils.getCounter(i+1)} bJet pT [GeV]", plotopts=utils.getOpts(uname)))
                                plots.append(Plot.make1D(f"{uname}_OnlyjetsPassBtagDiscrScore_MappedWithBRegCorr_resolved_bjet{i+1}_mass_{taggerWP}_METcut_bTagWeight_{cond}",
                                        bj_mass, sel,
                                        EqB(60 // binScaling, 0., 650.),
                                        title=f"{utils.getCounter(i+1)} bJet mass [GeV]", plotopts=utils.getOpts(uname)))
                                
        plots.extend(yield_object.returnPlots())
        return plots
