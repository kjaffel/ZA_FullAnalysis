#!/bin/env python

import argparse
import difflib

def get_options():
    """
    Parse and return the arguments provided by the user
    """
    parser = argparse.ArgumentParser(description='merge two efficiency files into one for later conversion in framework-format')
    parser.add_argument('datafile', type=str, metavar='DATAFILE',
        help='file containing the efficiencies on data')
    parser.add_argument('mcfile', type=str, metavar='MCFILE',
        help='file containing the efficiencies on MC')
    parser.add_argument('-p', '--prefix', help='Prefix to prepend to the output filename', default='', type=str)
    parser.add_argument('-s', '--suffix', help='Suffix to append at the end of the output filename', default='', type=str)
    options = parser.parse_args()
    return options


#etamin  etamax  ptmin   ptmax   eff deff_high   deff_low
#-2.4    -2.1    10  13  0.773807    0.00991219   0.0147608

def main(options):
    alldatabins = []
    allbins = []
    s = difflib.SequenceMatcher(None, options.datafile, options.mcfile)
    matching_sequence = ''.join([options.datafile[x:x+l] for x,y,l in s.get_matching_blocks()])
    matching_sequence = matching_sequence.strip('.txt')
    outputname = options.prefix + 'data_mc_' + matching_sequence + options.suffix + '.txt'
    print 'output filename: %s' % outputname
    with open(outputname, 'w') as outputfile:
        with open(options.datafile) as inputfile:
            for line in inputfile:
                if 'eff' in line:
                    continue
                content = line.split()
                alldatabins.append(content)
        with open(options.mcfile) as inputfile:
            for line in inputfile:
                if 'eff' in line:
                    continue
                content = line.split()
                etamin, etamax, ptmin, ptmax, eff, deff_high, deff_low = content
                for bin in alldatabins:
                    if ((etamin in bin)
                        and (etamax in bin)
                        and (ptmin in bin)
                        and (ptmax in bin)):
                        allbins.append(bin + [eff, deff_high, deff_low, '\n'])
                        alldatabins.remove(bin)
            for bin in allbins:
                outputfile.write(' '.join(bin))
        
    

#            etamin, etamax, ptmin, ptmax, eff, deff_high, deff_low = content
#            print content
    return

if __name__ == '__main__':
    options = get_options()
    main(options)
