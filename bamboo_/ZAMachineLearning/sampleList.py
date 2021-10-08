import os, os.path, sys
import glob

#samples_path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/skimmedTree/ver5/'
#samples_path = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/nanov7/skimmedTree/ver0/'
#samples_path = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/nanov7/skimmedTree/ver1/'
samples_path  = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov8/ul2016__ver2/'

samples_dict_2016 = {}
samples_dict_2017 = {} 
samples_dict_2018 = {}

for proc in ["ggH", "bbH"]:
    samples_dict_2016[proc] = {}
    samples_dict_2017[proc] = {}
    samples_dict_2018[proc] = {}
    for cat in ["ElEl", "MuMu"]:
        for reg in ["boosted", "resolved"]:
            samples_dict_2016[proc][f"{reg}_{cat}_DY"] = []
            samples_dict_2016[proc][f"{reg}_{cat}_TT"] = []
            samples_dict_2016[proc][f"{reg}_{cat}_ZA"] = []
            samples_dict_2016[proc][f"{reg}_{cat}_others"] = []
                    
            for data in ["signals21", "backgrounds"]:
                    for taggerWp in ["deepcsvM"]:#, "deepflavourM"]:
                        path ="{}/{}/2Lep2bJets_{}_{}_{}/results/".format(data, proc, reg, cat.lower(), taggerWp) 
    
                        for i_f, fn in enumerate(glob.glob(os.path.join(samples_path, path,'*.root'))):
                            smp = fn.split('/')[-1]
                            if '__skeleton__' in smp:
                                continue
                            elif smp.startswith('DY'):
                                samples_dict_2016[proc][f"{reg}_{cat}_DY"].append(f"{path}/{smp}")
                            elif smp.startswith('ST') or smp.startswith('TT'):
                                samples_dict_2016[proc][f"{reg}_{cat}_TT"].append(f"{path}/{smp}")
                            elif smp.startswith('HToZATo2L2B'):
                                samples_dict_2016[proc][f"{reg}_{cat}_ZA"].append(f"{path}/{smp}")
                            else:
                                samples_dict_2016[proc][f"{reg}_{cat}_others"].append(f"{path}/{smp}")

####################################### ERA 2016 ########################################

#---------------------------------------------------------------------------------------#
#                                       Resolved                                        #      
#---------------------------------------------------------------------------------------#
#samples_dict_2016["resolved_ElEl_DY"] = [
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/DYJetsToLL_M-10to50.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/DYToLL_0J.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/DYToLL_1J.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/DYToLL_2J.root",
#                     ]
#samples_dict_2016["resolved_MuMu_DY"] = [
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/DYJetsToLL_M-10to50.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/DYToLL_0J.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/DYToLL_1J.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/DYToLL_2J.root",
#                     ]
#
#samples_dict_2016["resolved_ElEl_TT"] = [
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/TT.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/TTTo2L2Nu.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ST_schannel_4f.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ST_tchannel_antitop_4f.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ST_tchannel_top_4f.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ST_tW_antitop_5f.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ST_tW_top_5f.root",
#                     ]
#samples_dict_2016["resolved_MuMu_TT"] = [
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/TT.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/TTTo2L2Nu.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ST_schannel_4f.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ST_tchannel_antitop_4f.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ST_tchannel_top_4f.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ST_tW_antitop_5f.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ST_tW_top_5f.root",
#                     ]
#
#samples_dict_2016["resolved_ElEl_Other"] = [
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ggZH_HToBB_ZToLL.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ggZH_HToBB_ZToNuNu.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/HZJ_HToWW.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ttHTobb.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ttHToNonbb.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/TTWJetsToLNu.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/TTWJetsToQQ.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/TTZToLLNuNu.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/TTZToQQ.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/WJetsToLNu.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/WWTo2L2Nu.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/WWToLNuQQ.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/WWW.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/WWZ.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/WZ1L1Nu2Q.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/WZTo1L3Nu.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/WZTo2L2Q.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/WZTo3LNu.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/WZZ.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ZH_HToBB_ZToLL.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ZZTo2L2Nu.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ZZTo2L2Q.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ZZTo4L.root",
#"backgrounds/2Lep2bJets_resolved_elel_deepcsvM/results/ZZZ.root",
#                                ]
#samples_dict_2016["resolved_MuMu_Other"] = [
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ggZH_HToBB_ZToLL.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ggZH_HToBB_ZToNuNu.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/HZJ_HToWW.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ttHTobb.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ttHToNonbb.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/TTWJetsToLNu.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/TTWJetsToQQ.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/TTZToLLNuNu.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/TTZToQQ.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/WJetsToLNu.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/WWTo2L2Nu.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/WWToLNuQQ.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/WWW.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/WWZ.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/WZ1L1Nu2Q.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/WZTo1L3Nu.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/WZTo2L2Q.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/WZTo3LNu.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/WZZ.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ZH_HToBB_ZToLL.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ZZTo2L2Nu.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ZZTo2L2Q.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ZZTo4L.root",
#"backgrounds/2Lep2bJets_resolved_mumu_deepcsvM/results/ZZZ.root",
#                    ]
#
#samples_dict_2016["resolved_ElEl_ZA"] = [
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-1000_MA-200.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-1000_MA-500.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-1000_MA-50.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-2000_MA-1000.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-200_MA-100.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-200_MA-50.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-250_MA-100.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-250_MA-50.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-3000_MA-2000.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-300_MA-100.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-300_MA-200.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-300_MA-50.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-500_MA-200.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-500_MA-300.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-500_MA-400.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-500_MA-50.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-650_MA-50.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-800_MA-200.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-800_MA-400.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-800_MA-50.root",
#"signals21/2Lep2bJets_resolved_elel_deepcsvM/results/HToZATo2L2B_MH-800_MA-700.root",
#                                ]
#samples_dict_2016["resolved_MuMu_ZA"] = [
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-1000_MA-200.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-1000_MA-500.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-1000_MA-50.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-2000_MA-1000.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-200_MA-100.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-200_MA-50.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-250_MA-100.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-250_MA-50.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-3000_MA-2000.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-300_MA-100.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-300_MA-200.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-300_MA-50.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-500_MA-200.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-500_MA-300.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-500_MA-400.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-500_MA-50.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-650_MA-50.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-800_MA-200.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-800_MA-400.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-800_MA-50.root",
#"signals21/2Lep2bJets_resolved_mumu_deepcsvM/results/HToZATo2L2B_MH-800_MA-700.root",
#                          ]
#
#
##---------------------------------------------------------------------------------------#
##                                      Boosted                                          #      
##---------------------------------------------------------------------------------------#
#
#samples_dict_2016["boosted_ElEl_DY"] = [
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/DYJetsToLL_M-10to50.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/DYToLL_0J.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/DYToLL_1J.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/DYToLL_2J.root",
#                                ]
#samples_dict_2016["boosted_MuMu_DY"] = [
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/DYJetsToLL_M-10to50.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/DYToLL_0J.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/DYToLL_1J.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/DYToLL_2J.root",
#                    ]
#
#samples_dict_2016["boosted_ElEl_TT"] = [
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/TT.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/TTTo2L2Nu.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ST_schannel_4f.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ST_tchannel_antitop_4f.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ST_tchannel_top_4f.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ST_tW_antitop_5f.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ST_tW_top_5f.root",
#                    ]
#
#samples_dict_2016["boosted_MuMu_TT"] = [
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/TT.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/TTTo2L2Nu.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ST_schannel_4f.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ST_tchannel_antitop_4f.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ST_tchannel_top_4f.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ST_tW_antitop_5f.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ST_tW_top_5f.root",
#                    ]
#
#samples_dict_2016["boosted_ElEl_Other"] = [
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ggZH_HToBB_ZToLL.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ggZH_HToBB_ZToNuNu.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/HZJ_HToWW.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ttHTobb.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ttHToNonbb.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/TTWJetsToLNu.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/TTWJetsToQQ.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/TTZToLLNuNu.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/TTZToQQ.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/WJetsToLNu.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/WWTo2L2Nu.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/WWToLNuQQ.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/WWW.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/WWZ.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/WZ1L1Nu2Q.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/WZTo1L3Nu.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/WZTo2L2Q.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/WZTo3LNu.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/WZZ.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ZH_HToBB_ZToLL.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ZZTo2L2Nu.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ZZTo2L2Q.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ZZTo4L.root",
#"backgrounds/2Lep2bJets_boosted_elel_deepcsvM/results/ZZZ.root",
#                    ]
#samples_dict_2016["boosted_MuMu_Other"] = [
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ggZH_HToBB_ZToLL.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ggZH_HToBB_ZToNuNu.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/HZJ_HToWW.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ttHTobb.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ttHToNonbb.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/TTWJetsToLNu.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/TTWJetsToQQ.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/TTZToLLNuNu.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/TTZToQQ.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/WJetsToLNu.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/WWTo2L2Nu.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/WWToLNuQQ.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/WWW.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/WWZ.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/WZ1L1Nu2Q.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/WZTo1L3Nu.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/WZTo2L2Q.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/WZTo3LNu.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/WZZ.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ZH_HToBB_ZToLL.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ZZTo2L2Nu.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ZZTo2L2Q.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ZZTo4L.root",
#"backgrounds/2Lep2bJets_boosted_mumu_deepcsvM/results/ZZZ.root",
#                    ]
#
#samples_dict_2016["boosted_ElEl_ZA"] = [
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-1000_MA-200.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-1000_MA-500.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-1000_MA-50.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-2000_MA-1000.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-200_MA-100.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-200_MA-50.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-250_MA-100.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-250_MA-50.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-3000_MA-2000.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-300_MA-100.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-300_MA-200.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-300_MA-50.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-500_MA-200.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-500_MA-300.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-500_MA-400.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-500_MA-50.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-650_MA-50.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-800_MA-200.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-800_MA-400.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-800_MA-50.root",
#"signals21/2Lep2bJets_boosted_elel_deepcsvM/results/HToZATo2L2B_MH-800_MA-700.root",
#                                ]
#
#samples_dict_2016["boosted_MuMu_ZA"] = [
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-1000_MA-200.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-1000_MA-500.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-1000_MA-50.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-2000_MA-1000.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-200_MA-100.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-200_MA-50.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-250_MA-100.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-250_MA-50.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-3000_MA-2000.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-300_MA-100.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-300_MA-200.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-300_MA-50.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-500_MA-200.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-500_MA-300.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-500_MA-400.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-500_MA-50.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-650_MA-50.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-800_MA-200.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-800_MA-400.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-800_MA-50.root",
#"signals21/2Lep2bJets_boosted_mumu_deepcsvM/results/HToZATo2L2B_MH-800_MA-700.root",
#                          ]
