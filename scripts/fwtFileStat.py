#! /bin/env python

"""
Print disk usage of a TTree
"""

from __future__ import division

import sys, array, os

import ROOT

from math import log
unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
def sizeof_fmt(num):
    """Human friendly file size"""
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'

def printTreeStat(filesize, d, t):
    print("Statistics for tree %s/%s" % (d.GetName() if d is not None else "", t.GetName()))

    s = 0
    skey = 0
    if t.GetDirectory() is not None:
        key = t.GetDirectory().GetKey(t.GetName())
        if key is not None:
            skey = key.GetKeylen()
            s = key.GetNbytes()

    total = skey
    if t.GetZipBytes() > 0:
        total += t.GetTotBytes()
           
    b = ROOT.TBufferFile(ROOT.TBuffer.kWrite, 10000)
    ROOT.TTree.Class().WriteBuffer(b, t)
    total += b.Length()
    file = t.GetZipBytes() + s
    cx = 1
    if t.GetZipBytes() > 0:
        cx = (t.GetTotBytes() + 0.00001) / t.GetZipBytes()
    
    percent = file / filesize * 100
    print("******************************************************************************")
    print("*Tree    :%-10s: %-54s *" % (t.GetName(), t.GetTitle()))
    print("*Entries : %8d : Total = %10s  File  Size = %10s  ~ %5.2f %% *" %  (t.GetEntries(), sizeof_fmt(total), sizeof_fmt(file), percent))
    print("*        :          : Tree compression factor = %6.2f                       *" % cx)
    print("******************************************************************************")


    nl = t.GetListOfLeaves().GetEntries()
    br = None
    leaf = None
    count = array.array('f', [0] * nl)
    names = []
    keep = 0
    for l in xrange(0, nl):
        leaf = t.GetListOfLeaves().At(l)
        br = leaf.GetBranch()
        if '.' in br.GetName() or br.GetMother() != br:
            count[l] = -1
            count[keep] += br.GetZipBytes()
        else:
            keep = l
            count[keep] = br.GetZipBytes()

        names.append(br.GetName())

    percent_sum = 0
    for size, name in sorted(zip(count, names), reverse=True):
        if size < 0:
            continue

        percent = size / file * 100
        percent_sum += percent
        print("branch %-60s %9s    ~%.2f %%" % (name, sizeof_fmt(size), percent))

    print("------------------")
    print("       %-60s %9s    ~%.2f %%" % (" ", " ", percent_sum))
    print("\n\n\n")

filesize = os.path.getsize(sys.argv[1])
f = ROOT.TFile.Open(sys.argv[1], "read")

for key in f.GetListOfKeys():
    d = f.Get(key.GetName())

    if isinstance(d, ROOT.TTree):
        printTreeStat(filesize, None, d) 
    elif isinstance(d, ROOT.TDirectory):
        for treeKey in d.GetListOfKeys():
            tree = d.Get(treeKey.GetName())
            printTreeStat(filesize, d, tree)