import os.path
import gzip
import uproot
import numpy as np
from correctionlib.schemav2 import (
    VERSION, Binning, Category, Content, Correction, MultiBinning, Variable, CorrectionSet)
from correctionlib.JSONEncoder import write

def get_corr(corr_name):
    hist = input_file[corr_name]

    nominal = np.absolute(hist.values())
    errs = hist.errors()
    up = nominal + errs
    down = nominal - errs
    content = {
        "sf": list(nominal.ravel()),
        "sfup": list(up.ravel()),
        "sfdown": list(down.ravel())
    }
    
    axis_edges = [ list(ax.edges()) for ax in hist.axes ]
    axis_titles = [ "pt", "eta" ]
    axis_vars = [ Variable.parse_obj({"type": "real", "name": title, "description": ""}) for title in axis_titles ]
    categ_var = Variable.parse_obj({"type": "string", "name": "ValType", "description": "sf/sfup/sfdown"})
    content_mbs = {
        typ: MultiBinning.parse_obj({
            "nodetype": "multibinning",
            "inputs": axis_titles,
            "edges": axis_edges,
            "content": cont,
            "flow": "clamp"
        }) for typ,cont in content.items()
    }
    categ_data = Category.parse_obj({
        "nodetype": "category",
        "input": "ValType",
        "content": [{"key": key, "value": cont} for key,cont in content_mbs.items()],
    })
    
    corr = Correction.parse_obj({
        "version": 1,
        "name": corr_name,
        "description": "",
        "inputs": [ categ_var ] + axis_vars,
        "output": {"name": "weight", "type": "real"},
        "data": categ_data
    })

    return corr

corr_names = [
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepcsv_wpL_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepcsv_wpL_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepcsv_wpM_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepcsv_wpM_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepcsv_wpL_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepcsv_wpL_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepcsv_wpM_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepcsv_wpM_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepcsv_wpT_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepcsv_wpT_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepflavour_wpL_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepflavour_wpL_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepflavour_wpM_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepflavour_wpM_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepflavour_wpT_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepflavour_wpT_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepcsv_wpL_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepcsv_wpL_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepcsv_wpM_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepcsv_wpM_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepcsv_wpL_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepcsv_wpL_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepcsv_wpM_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepcsv_wpM_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepcsv_wpT_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepcsv_wpT_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepflavour_wpL_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepflavour_wpL_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepflavour_wpM_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepflavour_wpM_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepflavour_wpT_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepflavour_wpT_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepcsv_wpL_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepcsv_wpL_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepcsv_wpM_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepcsv_wpM_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepcsv_wpL_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepcsv_wpL_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepcsv_wpM_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepcsv_wpM_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepcsv_wpT_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepcsv_wpT_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepflavour_wpL_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepflavour_wpL_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepflavour_wpM_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepflavour_wpM_gg_fusion__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepflavour_wpT_bb_associatedProduction__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepflavour_wpT_gg_fusion__mc_eff",
]



corr_names__ver2 = [
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepcsv_wpL_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepcsv_wpL_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepcsv_wpM_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepcsv_wpM_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepcsv_wpT_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepcsv_wpT_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepflavour_wpL_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepflavour_wpL_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepflavour_wpM_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepflavour_wpM_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepflavour_wpT_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_resolved_deepflavour_wpT_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepcsv_wpL_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepcsv_wpL_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepcsv_wpM_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepcsv_wpM_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepcsv_wpT_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepcsv_wpT_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepflavour_wpL_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepflavour_wpL_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepflavour_wpM_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepflavour_wpM_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepflavour_wpT_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_resolved_deepflavour_wpT_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepcsv_wpL_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepcsv_wpL_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepcsv_wpM_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepcsv_wpM_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepcsv_wpT_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepcsv_wpT_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepflavour_wpL_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepflavour_wpL_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepflavour_wpM_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepflavour_wpM_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepflavour_wpT_bb_associatedProduction_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_resolved_deepflavour_wpT_gg_fusion_AK4__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepcsv_wpL_bb_associatedProduction_AK8__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepcsv_wpL_gg_fusion_AK8__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepcsv_wpM_bb_associatedProduction_AK8__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepcsv_wpM_gg_fusion_AK8__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepcsv_wpL_bb_associatedProduction_AK8__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepcsv_wpL_gg_fusion_AK8__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepcsv_wpM_bb_associatedProduction_AK8__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepcsv_wpM_gg_fusion_AK8__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepcsv_wpL_bb_associatedProduction_AK8__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepcsv_wpL_gg_fusion_AK8__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepcsv_wpM_bb_associatedProduction_AK8__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepcsv_wpM_gg_fusion_AK8__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepcsv_wpL_bb_associatedProduction_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepcsv_wpL_gg_fusion_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepcsv_wpM_bb_associatedProduction_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepcsv_wpM_gg_fusion_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepflavour_wpL_bb_associatedProduction_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepflavour_wpL_gg_fusion_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepflavour_wpM_bb_associatedProduction_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_bflav_boosted_deepflavour_wpM_gg_fusion_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepcsv_wpL_bb_associatedProduction_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepcsv_wpL_gg_fusion_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepcsv_wpM_bb_associatedProduction_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepcsv_wpM_gg_fusion_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepflavour_wpL_bb_associatedProduction_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepflavour_wpL_gg_fusion_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepflavour_wpM_bb_associatedProduction_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_cflav_boosted_deepflavour_wpM_gg_fusion_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepcsv_wpL_bb_associatedProduction_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepcsv_wpL_gg_fusion_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepcsv_wpM_bb_associatedProduction_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepcsv_wpM_gg_fusion_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepflavour_wpL_bb_associatedProduction_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepflavour_wpL_gg_fusion_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepflavour_wpM_bb_associatedProduction_AK4_cleaned__mc_eff",
"pair_lept_2j_jet_pt_vs_eta_lightflav_boosted_deepflavour_wpM_gg_fusion_AK4_cleaned__mc_eff",

]

#pathIN="/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/ul_btv_effmaps/"
#pathIN="/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext5/sanitycheck__4/"
pathIN ="/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/run2Ulegay_results/unblind_stage1_full_per_chunk_fullrun2/ext6/sanitycheck__10/btagEffmaps/"

for era in [ '2018', '2017', '2016-preVFP', '2016-postVFP']:
    
    #input_file = uproot.open(os.path.join(pathIN, f"ul2016__btv_effmaps__ver8/results/summedProcessesForEffmaps/summedProcesses_{era}_ratios.root"))
    #input_file = uproot.open(os.path.join(pathIN, f"ul_full_run2__ver2/results/summedProcessesForEffmaps/summedProcesses_{era}_ratios.root"))
    #input_file = uproot.open(os.path.join(pathIN, f"ul_full_run2__ver3/results/summedProcessesForEffmaps/summedProcesses_{era}_ratios.root"))
    #input_file = uproot.open(os.path.join(pathIN, f"ul_full_run2__ver4/results/summedProcessesForEffmaps/summedProcesses_{era}_ratios.root"))
    #input_file = uproot.open(os.path.join(pathIN, f"ul_full_run2__ver5/results/summedProcessesForEffmaps/summedProcesses_{era}_ratios.root"))
    input_file = uproot.open(os.path.join(pathIN, f"results/summedProcessesForEffmaps/summedProcesses_{era}_ratios.root"))
    
    corr_set = CorrectionSet.parse_obj({
        "schema_version": VERSION,
        "corrections": [ get_corr(name) for name in corr_names__ver2 ]
    })
    
    write(corr_set, f"BTagEff_maps_UL{era.replace('-','').replace('20','')}.json.gz", sort_keys=True,indent=2,maxlistlen=25,maxdictlen=3,breakbrackets=False)
