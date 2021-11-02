# this script is made to keep tracks of the Number of Events when you change your selections or the nanoAOD production version 
# please make sure to run this script on your skimmed Trees before doing the training
import ROOT
import glob
import os, os.path
import logging
from cppyy import gbl
import json
import argparse

logger = logging.getLogger("ZA_Skimmer")
parser = argparse.ArgumentParser(description='Nbr Events cross check')
parser.add_argument('-i', '--inputs', action='store', dest='InputDir', type=str, help='path to ntuples (* .root files)')
parser.add_argument('-e', '--era',   action='store', dest='era',       type=str, help='you need to pass your era ')
parser.add_argument('-prod', '--prodversion',   action='store', dest='prodversion', help='you need to pass your era ')

options = parser.parse_args()

InputDir=options.InputDir
if not os.path.isdir(os.path.join('./', "events/%s"%options.era)):
    os.makedirs(os.path.join('./',"events/%s"%options.era))
version =InputDir.split('/')[-2]
taggers = ['DeepCSV', 'DeepFlavour']
channels =['ElEl', 'MuMu']
WP= 'M'
llbb_selections= []
for sel in ['boosted', 'resolved']:
    for tagger in taggers:
        for channel in channels:
            llbb_selections.append('2Lep2bJets_{0}_{1}_{2}{3}'.format(sel.lower(), channel.lower(), tagger.lower(), WP.upper()))
    
totalEvents= {}
for sel in llbb_selections: 
    for suffix in ['backgrounds', 'signals21']:
        try:
            path_toskimmer=os.path.join(InputDir,"{suffix}/{sel}/results/".format(suffix=suffix, sel=sel))
        except:
            raise RuntimeError('** given path not found !')
    
        JetType = ('AK4Jets' if 'resolved' in sel else ('AK8Jets'))
        reconstructed_Objects = ['llbb_M', 'bb_M', 'nB_%s'%JetType]
        print( 'path :' , path_toskimmer)
        root_without_events = []
        tot = 0
        for smp in glob.glob(os.path.join(path_toskimmer, '*.root')):
            sample= smp.split('/')[-1].replace('.root','')
            if '__skeleton__' in sample:
                continue
            if 'DoubleMuon' in sample or 'EGamma' in sample or 'MuonEG' in sample or 'DoubleEGamma' in sample or 'SingleElectron' in sample or 'SingleMuon' in sample:
                continue
            tot +=1
            f=gbl.TFile.Open(smp)
            if not f:
                print("Could not open file %s"%smp)
            #try:
            t = f.Get("Events")
            if t:    
                totalEvents[sample]= t.GetEntries()
                with open(os.path.join('./events/%s'%options.era,"%s_Nevents_%s_%s.json"%(sel, options.prodversion, version)), "w") as handle:
                    json.dump(totalEvents, handle, indent=4, sort_keys=True)
            else:
                logger.warning('%s found without Events, will skipp '%sample)
                root_without_events.append(smp.split('/')[-1])
        rlen= len(root_without_events)
        logger.warning('no no ... you should re-consider having {rlen}/{tot} missing *TTree: Events in your Outputs before doing any training :'.format(rlen=rlen, tot=tot))
        print(root_without_events)
        print('='*100)
