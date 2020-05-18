#!/usr/bin/env python
import argparse
import ROOT
import json
import array

class ConfigObject:
    def __init__(self, data):
        self.data = data   
    def getObject(self, object_name, title=""):
        initialize = self.data[object_name]['Initialize']
        if "TH1" in initialize['type']:
            if "varbins" not in initialize:
                tObject = ROOT.TH1F(object_name, title, 
                    initialize['nbins'], initialize['xmin'], 
                    initialize['xmax'])
            else:
                tObject = ROOT.TH1F(object_name, object_name, 
                    initialize['nbins'], 
                    array.array('d', initialize['varbins'])) 
            tObject.SetDirectory(ROOT.gROOT)
        elif initialize['type'] == "TCanvas":
            tObject = ROOT.TCanvas(object_name, object_name, 
                                initialize['ww'], initialize['wh'])
        else:
            tObject = ""
        return tObject
    def deepGetattr(self, obj, attr):
        """Recurses through an attribute chain to get the ultimate value.
            via http://pingfive.typepad.com/blog/2010/04/deep-getattr-python-function.html"""
        try:
            return float(attr)
        except ValueError:
            return self.evaluateNested(getattr, attr.split('.'), obj)
    def evaluateNested(self, func, iterable, start=None):
        it = iter(iterable)
        if start is None:
            try:
                start = next(it)
            except StopIteration:
                raise TypeError('reduce() of empty sequence with no initial value')
        accum_value = start
        for x in iterable:
            split = str(x).strip(")").split("(")
            function_call = split[0]
            accum_value = func(accum_value, function_call)
            if len(split) != 1:
                if len(split[1]) == 0:
                    accum_value = accum_value()
                else:
                    func_args = split[1].split(",")
                    accum_value = accum_value(*func_args)
        return accum_value

    def setAttributes(self, tObject, attributes):
        functions = []
        for function_call, params in attributes.iteritems():
            if not isinstance(params, list): 
                params = [params]
            parsed_params = []
            for param in params:
                param_str = str(param)
                if "ROOT" in param_str:
                    expr = param_str.replace("ROOT.", "")
                    if "+" in param_str:
                        values = [x.strip() for x in expr.split("+")]
                        root_val = self.deepGetattr(ROOT, values[0])
                        root_val += int(values[1]) 
                    elif "-" in param_str:
                        values = [x.strip() for x in expr.split("-")]
                        root_val =self.deepGetattr(ROOT, values[0])
                        root_val -= int(values[1]) 
                    else:
                        root_val = self.deepGetattr(ROOT, expr)
                    param = root_val
                parsed_params.append(param)
            self.deepGetattr(tObject, function_call)(*parsed_params)
    def getHistCanvas(self, hist_name):
        canvas = getCanvas(self)
        hist = self.getObject(hist_name) 
        hist.Draw()
        self.setAtrributes(hist)
        hist.Draw()
        return canvas
    def getCanvas(self):
        canvas = self.getObject("Canvas") 
        self.setAttributes(canvas, "Canvas")
        canvas.cd()
        return canvas
    def getListOfHists(self):
        list_of_hists = []
        for key in self.data:
            if key != "Canvas":
                list_of_hists.append(key)
        return list_of_hists
