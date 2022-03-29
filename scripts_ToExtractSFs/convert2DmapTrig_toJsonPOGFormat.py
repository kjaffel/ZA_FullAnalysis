import os.path
import gzip
import uproot
from correctionlib.schemav2 import (
    VERSION, Binning, Category, Content, Correction, MultiBinning, Variable, CorrectionSet)
from correctionlib.JSONEncoder import write

era = "2016preVFP"
#era = "2016postVFP"
#era = "2017"
#era = "2018"

pathIN = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/data/HLTefficiencies/run2ULegacyHLT/Inputs/"
input_file = uproot.open(os.path.join(pathIN, f"TriggerSF_{era}_UL.root"))

def get_corr(corr_name, input_file):
    hist = input_file[corr_name]

    nominal = hist.values()
    errs = hist.errors()
    up = nominal + errs
    down = nominal - errs
    content = {
        "sf": list(nominal.ravel()),
        "sfup": list(up.ravel()),
        "sfdown": list(down.ravel())
    }

    axis_edges = [ list(ax.edges()) for ax in hist.axes ]
    axis_titles = [ "ele_pt", "mu_pt" ] if "emu" in corr_name else [ "lep1_pt", "lep2_pt" ]
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
    "h2D_SF_ee_lepABpt_FullError",
    "h2D_SF_emu_lepABpt_FullError",
    "h2D_SF_mumu_lepABpt_FullError"
]

corr_set = CorrectionSet.parse_obj({
    "schema_version": VERSION,
    "corrections": [ get_corr(name) for name in corr_names ]
})

write(corr_set, f"TriggerSF_{era}_UL.json.gz", sort_keys=True,indent=2,maxlistlen=25,maxdictlen=3,breakbrackets=False)
