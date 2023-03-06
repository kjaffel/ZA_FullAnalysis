#!/usr/bin/env python3

import json
import os
from argparse import ArgumentParser

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplhep
import mplhep.cms
plt.style.use(mplhep.style.CMS)


def load_impact_json(impacts_file):
    with open(impacts_file) as f:
        js = json.load(f)
    return js


def get_impacts_df(js):
    impacts = []
    for nuis in js["params"]:
        if "prop" in nuis["name"]: continue
        impacts.append(
            {
                "pull": nuis["fit"][1],
                "pull_err_down": nuis["fit"][1] - nuis["fit"][0],
                "pull_err_up": nuis["fit"][2] - nuis["fit"][1],
                "name": nuis["name"],
                "avg_impact": nuis["impact_r"],
                "impact_up":nuis["r"][1] - nuis["r"][2],
                "impact_down":nuis["r"][0] - nuis["r"][1],
            })
    return pd.DataFrame(impacts)


def plot_nuisance(nuisance, impacts, outdir):
    impacts = impacts.sort_values("category")

    # get categories
    categories = list(impacts["category"].unique())
    n_fits = len(categories)

    # get y coordinates
    y_coords = np.arange(0, n_fits, 1)
    y_low = y_coords[0]-0.4
    y_hi  = y_coords[-1]+0.4

    # for nuis in nuisances:
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(18, 8 + n_fits // 2),
                        gridspec_kw={"width_ratios": (1,1)})
    fig.subplots_adjust(hspace=0)

    # some style options
    ms = 8
    lw = 2

    # get pull values
    pulls = impacts["pull"]
    pulls_du = impacts[["pull_err_down", "pull_err_up"]].to_numpy().T

    # draw prefit pull area
    ax1.fill_between([-1, 1], y_low, y_hi, color="grey", alpha=0.2, zorder=1, label="Pre-fit")
    ax1.plot([0, 0], [y_low, y_hi], color="k", ls="dashed", marker="")
    ax2.plot([0, 0], [y_low, y_hi], color="k", ls="dashed", marker="")

    # draw pulls
    ax1.errorbar(pulls, y_coords, xerr=pulls_du, fmt="o", markersize=ms, linewidth=lw, zorder=10, label=nuis)

    # get impact values
    ax2.barh(y_coords, impacts["impact_down"], label="down")
    ax2.barh(y_coords, impacts["impact_up"], label="up")

    # set y axis label
    ax1.set_yticks(y_coords)
    ax1.set_yticklabels(categories)
    ax1.set_ylim(y_low, y_hi*1.1)
    ax1.xaxis.grid(True)
    ax2.xaxis.grid(True)
    
    # set x axis label
    ax1.set_xlabel(f"{nuis} pulls")
    ax2.set_xlabel(r"Impact on r")

    # legend
    mplhep.cms.label(ax=ax1, data=True, rlabel="", label="Preliminary")
    ax1.legend(loc="upper right", bbox_to_anchor=(1, 1), fontsize="small")
    ax2.legend(loc="upper right", bbox_to_anchor=(1, 1), fontsize="small")

    # save figure
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig_path = os.path.join(outdir, f"pulls_{nuis}.pdf")
    fig_path = os.path.join(outdir, f"pulls_{nuis}.png")
    fig.savefig(fig_path)
    plt.close()


if __name__ == '__main__':
    parser = ArgumentParser(usage="%(prog)s [options]")
    parser.add_argument('-i', '--impacts', nargs='+', help="List of category:impact, e.g. mumu:./mumu/impacts.json ee:./ee/impacts.json")
    parser.add_argument('-o', '--output', required=True, help="Output directory")
    args = parser.parse_args()

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    impacts_df = []
    print( args.impacts, type(args.impacts))
    for cat_json in args.impacts:
        cat, json_path = cat_json.split(":")
        impact_json = load_impact_json(json_path)
        impact_df = get_impacts_df(impact_json)
        impact_df["category"] = cat
        impacts_df.append(impact_df)
    impacts_df = pd.concat(impacts_df)

    for nuis, nuis_df in impacts_df.groupby(["name"]):
        plot_nuisance(nuis, nuis_df, args.output)


