#! /bin/env python
# files are found here : https://gitlab.cern.ch/cms-muonPOG/MuonReferenceEfficiencies?nav_source=navbar
import math
import sys
import argparse
import ROOT
import json
def extract_binning(data):
    """ Assume format of bin of 'B:[x,y]'"""
    binning = []

    for bin_ in data:
        b = eval(bin_.split(':')[1])
        binning += b

    # Binning is not always correctly ordered
    return sorted(list(set(binning)))

def format_eta_bin(eta_bin):
    return 'abseta:[%.1f,%.1f]' % (eta_bin[0], eta_bin[1])
def format_tag_bin(tag_bin):
    return 'tag:[%.1f,%.1f]' % (tag_bin[0], tag_bin[1])

def format_pt_bin(bin):
    return 'pt:[%.1f,%.1f]' % (bin[0], bin[1])

def clean_wp(wp):
    """ 
    Assume format 
        NUM_<WP>_DEN_A_PAR_B
    or
        <WP>_A_B
    """

    r = re.search(r'NUM_(.*)_DEN_(.*)_PAR', wp)
    if not r:
        r = re.search(r'([^_]*)_([^_]*)_.*', wp)
        if not r:
            raise RuntimeError('Failed to extract WP info from %r' % wp)

    return "%s_%s" % (r.group(1), r.group(2))

parser = argparse.ArgumentParser()
parser.add_argument('file', help='json format txt file containing muon scale factors')
parser.add_argument('-s', '--suffix', help='Suffix to append at the end of the output filename', required=True)

args = parser.parse_args()
with open(args.file, 'r') as f:
    d = json.load(f)

    for wp, wp_data in d.items():
        print (wp, wp_data)
        print ('')
        if 'histo_tag_nVertices_DATA'in wp_data.keys():
            wp_data = wp_data['histo_tag_nVertices_DATA']
            # Extract binning
            tag_binning = extract_binning(wp_data)

            json_content = {'dimension': 1, 'variables': ['tag'], 'binning': {'x': tag_binning}, 'data': [], 'error_type': 'absolute'}
            json_content_data = json_content['data']
            tag_data = { 'values': []}

            for tag_bin_index in range(0, len(tag_binning) - 1):
                tag_bin = format_tag_bin([tag_binning[tag_bin_index], tag_binning[tag_bin_index + 1]])
                print (tag_bin)
                if tag_bin not in wp_data:
                    print('Error: eta bin not found in input file. This should not happen!')
                    continue

                content = wp_data[tag_bin]

                value_data = { 'bin': [tag_binning[tag_bin_index], tag_binning[tag_bin_index + 1]], 'value': content['value'], 'error': content['error']}

                tag_data['values'].append(value_data)
                #print (value_data)
            json_content_data.append(tag_data)
            print (json_content_data)
            filename = '%s_%s.json' % (wp, args.suffix)
            with open(filename, 'w') as j:
                import json
                json.dump(json_content, j, indent=2)

        #if not 'pt_abseta_ratio'in wp_data.keys(): //2016
        #    continue
        if not 'abseta_pt_DATA' in wp_data.keys():
            continue

        print("Working on working point %r" % wp)

        #wp_data = wp_data['abseta_pt_ratio'] //2016
        wp_data = wp_data['abseta_pt_DATA'] 
        # Extract binning
        eta_binning = extract_binning(wp_data)

        pt_binning = None

        json_content = {'dimension': 2, 'variables': ['AbsEta', 'Pt'], 'binning': {'x': eta_binning, 'y': []}, 'data': [], 'error_type': 'absolute'}
        json_content_data = json_content['data']

        for i in range(0, len(eta_binning) - 1):
            eta_bin = format_eta_bin([eta_binning[i], eta_binning[i + 1]])

            if eta_bin not in wp_data:
                print('Error: eta bin not found in input file. This should not happen!')
                continue

            if pt_binning is None:
                pt_binning = extract_binning(wp_data[eta_bin])
                json_content['binning']['y'] = pt_binning

            eta_data = {'bin': [eta_binning[i], eta_binning[i + 1]], 'values': []}

            for pt_bin_index in range(0, len(pt_binning) - 1):
                pt_bin = format_pt_bin([pt_binning[pt_bin_index], pt_binning[pt_bin_index + 1]])
                if pt_bin not in wp_data[eta_bin]:
                    print("Error: pt bin not found in input file. This should not happpen!")
                    continue

                content = wp_data[eta_bin][pt_bin]

                pt_data = {'bin': [pt_binning[pt_bin_index], pt_binning[pt_bin_index + 1]], 'value': content['value'], 'error_low': content['error'], 'error_high': content['error']}

                eta_data['values'].append(pt_data)

            json_content_data.append(eta_data)
        # Save JSON file
        filename = '%s_%s.json' % (wp, args.suffix)
        with open(filename, 'w') as j:
            import json
            json.dump(json_content, j, indent=2)
