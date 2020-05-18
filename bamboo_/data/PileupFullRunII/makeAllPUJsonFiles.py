import os
import sys
import yaml
import traceback
import shutil
import argparse

parser = argparse.ArgumentParser(description='Produces all Json files containign PU weights for MC sample on "per-sample auto" procedure')
parser.add_argument('--yaml', action='store', required=True, type=str,
                    help = 'Analysis YAML file (for sample name and DAS path)')
parser.add_argument('--era', action='store', required=True, type=str,
                    help = 'Era')
parser.add_argument('--nominal', action='store', required=True, type=str,
                    help = 'Nominal PU data values root file')
parser.add_argument('--up', action='store', required=False, type=str,
                    help = 'Up variation of PU data values root file (optional)')
parser.add_argument('--down', action='store', required=False, type=str, 
                    help = 'Down variation of PU data values root file (optional)')
args = parser.parse_args()

print ("WARNING : do not forget to load grid module and your voms ;)")

with open(args.yaml, 'r') as stream:
    try:
        data = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

if not os.path.exists('./data/PileupFullRunII/mcprofile'):
    os.makedirs('./data/PileupFullRunII/mcprofile')

baseCommand =  r"makePUReWeightJSON -o %s_%s.json"
baseCommand += r" --nominal "+args.nominal
if args.up is not None:
    baseCommand += r" --up "+args.up
if args.down is not None:
    baseCommand += r" --down "+args.down
baseCommand += r" $(dasgoclient -query 'file dataset=%s' | sed 's=^\(.*\)$=/storage/data/cms\1=g')"

for sample, dico in data['samples'].items():
    if 'group' in dico: # Signal samples do not have group
        if dico['group'] == "data":
            continue
    daspath = dico['db'].replace('das:','')
    try:
        os.system(baseCommand%(sample,args.era,daspath))
    except Exception as err:
        traceback.print_tb(err.__traceback__)

    try: 
        shutil.move("%s_%s.json"%(sample, args.era),'./data/PileupFullRunII/mcprofile/%s_%s.json'%(sample, args.era))
    except Exception as err:
        print ("Could not move file %s_%s.json to dir pileup_json due to '%s'"%(sample, args.era, err))

