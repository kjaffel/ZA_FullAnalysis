#!/usr/bin/env python
import ROOT
import json
import numpy as np


def matrix2array(matrix):
    return np.frombuffer(
        matrix.GetMatrixArray(),
        dtype={
            "TMatrixTSym<double>": np.float64,
            "TMatrixTSym<float>": np.float32,
        }[matrix.ClassName()],
        count=matrix.GetNoElements(),
    ).reshape((matrix.GetNrows(), matrix.GetNcols()))


def fit_result2cov_json(fit_result):
    pars = fit_result.floatParsFinal()
    return dict(
        qual=int(fit_result.covQual()),
        labels=[pars[i].GetName() for i in range(len(pars))],
        cov=matrix2array(fit_result.covarianceMatrix()).tolist(),
        cor=matrix2array(fit_result.correlationMatrix()).tolist(),
    )


def extract_cov_json(filename, skip="prefit"):
    """Produces a .cov.json for every `RooFitResult` within the ROOT file given by `filename`.

    This includes covariance and correlation Matrix, column/row labels, and covariance quality.
    These files can be explored via the `view_cov_json.html` viewer.

    The output filenames are automatically produced by joining `filename` without extension
    (i.e. ".root"), the name of the `RooFitResult`, and the "cov.json" extension using the ".".
    Example: folder/input_file.root -> folder/input_file.result_name.cov.json

    If `skip` (default "prefit") is given and not empty, all `RooFitResult`s with their name
    containing `skip`are  skipped.
    """
    file_obj = ROOT.TFile(filename)
    for key in file_obj.GetListOfKeys():
        if key.GetClassName() != "RooFitResult":
            continue
        name = key.GetName()
        if skip and skip in name:
            continue

        info = fit_result2cov_json(file_obj.Get(name))

        parts = [filename.rsplit(".", 1)[0], name, "cov.json"]
        with open(".".join(parts), "w") as json_file:
            json.dump(info, json_file)
    file_obj.Close()


if __name__ == "__main__":
    from argparse import ArgumentParser

    ROOT.PyConfig.IgnoreCommandLineOptions = True
    ROOT.gROOT.SetBatch(ROOT.kTRUE)

    ap = ArgumentParser(
        description=extract_cov_json.__doc__ + " Multiple `filename`s can be given simultaneously."
    )
    ap.add_argument(
        "-s",
        "--skip",
        default="prefit",
        help="skip results containing this non-empty string, default: prefit",
    )
    ap.add_argument(
        "filename",
        nargs="+",
    )

    args = ap.parse_args()

    for filename in args.filename:
        extract_cov_json(filename, skip=args.skip)
