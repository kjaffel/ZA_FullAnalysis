from bambooToOls import Plot
from bamboo.plots import SummedPlot
from bamboo.plots import EquidistantBinning as EqB
from bamboo import treefunctions as op
import sys, os

ZAtollbbPath = os.path.dirname(__file__)
if ZAtollbbPath not in sys.path:
    sys.path.append(ZAtollbbPath)

import utils
import json
from bamboo.root import gbl

def makerhoPlots(selections, bjets, leptons, ellipses, ellipse_params, suffix, cut, WP, uname):
    plots = []

    for key, sel in selections.items():
        tagger = key.replace(WP, "")
        bjets_ = bjets[key.replace(WP, "")][WP]
        
        bb_p4= ((bjets_[0].p4+bjets_[1].p4) if suffix=="resolved" else( bjets_[0].p4))
        bb_M = bb_p4.M()
        llbb_M = (leptons[0].p4 +leptons[1].p4+bb_p4).M()
        for j, line in enumerate(ellipse_params, 0): 
            MH = str(line[-1]).replace('.', 'p')
            MA = str(line[-2]).replace('.', 'p')
            plots.append(Plot.make1D(f"rho_steps_{suffix}_histo_{uname}_hZA_lljj_{tagger}_btag{WP}_{cut}_MH_{MH}_MA_{MA}", 
                            ellipses.at(op.c_int(j)).radius(bb_M, llbb_M),
                            sel, EqB(6, 0., 3.), title="rho ",
                            plotopts=utils.getOpts(uname, **{"log-y": True})))
    return plots
