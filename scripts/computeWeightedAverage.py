#!/usr/bin/env python

from __future__ import division

import argparse
import json
import copy
import sys
import pprint
import numpy as np

def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    """

    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)

    m = int(n / arrays[0].size)
    out[:,0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out

parser = argparse.ArgumentParser(description='Compute weighted average of a set of efficiencies / scale-factors.')

parser.add_argument('-i', '--input', metavar='JSON', type=str, action='append',
                    help='JSON input files', required=True)

parser.add_argument('-w', '--weight', metavar='W', type=float, action='append',
                    help='Weight', required=True)

parser.add_argument('-o', '--output', metavar='JSON', type=str, action='store',
                    help='JSON output file', required=True)

args = parser.parse_args()

if len(args.input) != len(args.weight):
    parser.error('The number of inputs and weights is different')

inputs = []
weights = []

for i, input in enumerate(args.input):
    print("Using input %r with weight %.4f" % (input, args.weight[i]))
    with open(input) as f:
        inputs.append(json.load(f))

    weights.append(args.weight[i] / sum(args.weight))

result = copy.deepcopy(inputs[0])

# Clear all bin content
def clearValues(data):
    if 'values' in data:
        for d in data['values']:
            clearValues(d)
    else:
        data['value'] = 0
        data['error_low'] = 0
        data['error_high'] = 0

for d in result['data']:
    clearValues(d)

# Sanity check. Ensure all inputs are compatible
all_binnings = [result['binning']]
for i in range(1, len(inputs)):
    v = inputs[i]
    keys = ['variables', 'error_type', 'dimension']
    for key in keys:
        if result[key] != v[key]:
            raise Exception("Inputs are not compatible: key %r is different\n%s != %s" % (key, result[key], v[key]))
    all_binnings.append(v['binning'])

# Find common binning
common_binning = copy.deepcopy(all_binnings[0])
for i in range(1, len(all_binnings)):
    for key, binning in all_binnings[i].items():
        common_binning[key].extend(binning)

for key, binning in common_binning.items():
    common_binning[key] = sorted(list(set(binning)))

dimensions = ['x']
if result['dimension'] > 1:
    dimensions += ['y']
if result['dimension'] > 2:
    dimensions += ['z']

if common_binning != result['binning']:
    print("Warning: binnings in input files are different. Using new binning for result:")
    pprint.pprint(common_binning)

    # Recreate binning in result dict
    new_data = []
    first = True
    def buildData(binning, to_append=None):
        result = []
        list_binning = []
        for i in range(len(binning) - 1):
            list_binning.append([binning[i], binning[i + 1]])

        for bin in list_binning:
            if to_append:
                data = {'bin': bin, 'values': copy.deepcopy(to_append)}
            else:
                data = {'bin': bin, 'value': 0, 'error_low': 0, 'error_high': 0}
            result += [data]

        return result

    result['data'] = None
    for dimension in reversed(dimensions):
        binning = common_binning[dimension]
        result['data'] = buildData(binning, result['data'])

    result['binning'] = common_binning

# Compute centers of bin in all dimensions
bin_centers = {}
for dimension in dimensions:
    bin_center = np.asarray(common_binning[dimension])
    bin_center = (bin_center[1:] + bin_center[:-1]) / 2
    bin_centers[dimension] = bin_center

# Get a flatten list of bins. Each entry of the array is a bin, where first dimension is
# the center of the bin in X, second in Y, and possibly third in Z
bins = []
for dimension in dimensions:
    bins.append(bin_centers[dimension])

bins = cartesian(bins)

def findBinData(from_, bin):
    result = from_['data']

    # Exclude latest bin
    for b in bin[:-1]:
        found = False
        for data in result:
            if b > data['bin'][0] and b <= data['bin'][1]:
                result = data['values']
                found = True
                break
        if not found:
            raise Exception("No bin found containing %s in input file" % b)

    b = bin[-1]
    for data in result:
        if b > data['bin'][0] and b <= data['bin'][1]:
            return data

    raise Exception("No bin found containing %s in input file" % b)

# Compute weighted average for each bin
for bin in bins:
    # Loop over all inputs
    for input, weight in zip(inputs, weights):
        result_data = findBinData(result, bin)
        input_data = findBinData(input, bin)
        
        result_data['value'] += weight * input_data['value']
        result_data['error_low'] += weight * input_data['error_low']
        result_data['error_high'] += weight * input_data['error_high']

# Create comment
comment = 'JSON created running %s' % (' '.join(sys.argv))
result['comment'] = comment

with open(args.output, 'w') as f:
    json.dump(result, f)
    print("Output saved as %r" % args.output)
