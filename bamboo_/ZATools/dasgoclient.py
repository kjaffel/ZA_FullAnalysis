# VOMS is needed here
#source /cvmfs/cms.cern.ch/cmsset_default.sh
#voms-proxy-init -voms cms -rfc -valid 192:00

import os, os.path, sys
import subprocess
import glob
from cppyy import gbl

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/')
import utils as utils
logger = utils.ZAlogger(__name__)


def getSamplesFromDAS(era, smp, dataType= None, rm_nlo= False):
        
    if dataType != 'data':
        dasgoCmd     = ['dasgoclient', '-query', f'/{smp}*/RunIISummer20UL{era}*AODv9*/NANOAODSIM']
        dasgoCmd_APV = ['dasgoclient', '-query', f'/{smp}*/RunIISummer20UL{era}*AODAPVv9*/NANOAODSIM']
    else:
        dasgoCmd     = ['dasgoclient', '-query', f'/{smp}/Run20{era}*UL20{era}_MiniAODv2_NanoAODv9-v*/NANOAOD']
    
    ls_linesAPV = []
    
    try:
        logger.info("running: {}".format(" ".join(dasgoCmd)))
        ls_lines = subprocess.run(dasgoCmd, stdout=subprocess.PIPE).stdout.splitlines()
        if dataType != 'data':
            if era == 16:
                ls_linesAPV = subprocess.run(dasgoCmd_APV, stdout=subprocess.PIPE).stdout.splitlines()
    except subprocess.CalledProcessError:
        logger.error("Failed to run {0}".format(" ".join(dasgoCmd)))
   
    all_smp = (ls_lines + ls_linesAPV if era == 16 else (ls_lines))
    
    if era == 17:
        filter_smp1 = [ smpNm for smpNm in all_smp if not (str.encode('2017G') in smpNm or str.encode('2017H') in smpNm)]
    
    if dataType == 'mc':
        filter_smp1 = [ smpNm for smpNm in all_smp if not str.encode('JMENano') in smpNm]
        filter_smp2 = [ smpNm for smpNm in filter_smp1 if not str.encode('PUForMUOVal') in smpNm]
        filter_smp3 = [ smpNm for smpNm in filter_smp2 if not str.encode('FSUL18_FSUL18_') in smpNm]
        return filter_smp3
    elif dataType == 'signal':
        if rm_nlo: 
            filter_smp1 = [ smpNm for smpNm in all_smp if not str.encode('_tb-20p00_TuneCP5_bbH4F_13TeV-amcatnlo-pythia8') in smpNm]
            return filter_smp1
        else:
            return all_smp
    else:
        return filter_smp1 if era ==17 else all_smp

def writeToFile(fNm, list):
    with open(fNm,"w") as outf:
        for smp in list:
            outf.write(f"{smp.decode('utf-8')}\n")
    outf.close()


def checklocalfiles(era, list, tot_req): 
    i = 0 
    with open(f"rucio_signalUL{era}__ext2.txt","w") as outf:
        for dbLoc in list:
            dasQuery = f"file dataset={dbLoc.decode('utf-8')}"
            localgoCmd = ["dasgoclient", "-query", dasQuery]
            try:
                print(f"Querying DAS: '{dasQuery}'")
                ls_files = [ln.strip() for ln in subprocess.check_output(localgoCmd, stderr=subprocess.STDOUT).decode().split()]
                i += 1
            except subprocess.CalledProcessError:
                logger.error("Failed to run {0}".format(" ".join(localgoCmd)))
            
            files = glob.glob(os.path.join('/storage/data/cms/'+ os.path.dirname(ls_files[0]), '*.root'))
            #print( len(files),  len(ls_files) , not files or len(files) != len(ls_files))
            if not files or len(files) != len(ls_files):
                outf.write(f"{dbLoc.decode('utf-8')}\n")
            #try:
            #    rf = gbl.TFile.Open(('/storage/data/cms/',ls_files[0]), "READ")
            #except:# subprocess.CalledProcessError:
            #    outf.write(f"{dbLoc.decode('utf-8')}\n")
    outf.close()
    logger.info( f"{i} out of {tot_req} samples are ready, you are getting there: {i/tot_req*100}%")
    logger.info( f"rucio request needed for samples saved in :: rucio_signalUL{era}__ext2.txt") 

if __name__ == "__main__":
    
    look_for = {
        'signal' : ['GluGluToHToZATo2L2B', 'HToZATo2L2B', 'GluGluToAToZHTo2L2B', 'AToZHTo2L2B'],
        'mc'     : [ 
               # dy
               'DYJetsToLL_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8', 
               'DYJetsToLL_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8', 
               'DYJetsToLL_2J_TuneCP5_13TeV-amcatnloFXFX-pythia8', 
               # ttbar
               'TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8', 
               'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
               'TTToHadronic_TuneCP5_13TeV-powheg-pythia8',
               # single top 
               #'ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8',
               #'ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8',
               'ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8',
               'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8',
               'ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8',
               'ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8',
               'ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8',
               # ZZ
               'ZZTo2L2Nu_TuneCP5_13TeV_powheg_pythia8',
               'ZZTo4L_TuneCP5_13TeV_powheg_pythia8', 
               # others 
               'WWTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
               'WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8', 
               'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8', 
               'WZZ_TuneCP5_13TeV-amcatnlo-pythia8', 
               'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8', 
               'WJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-pythia8', 
               'TTWJetsToQQ_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8',
               'TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8',
               'TTZToQQ_TuneCP5_13TeV-amcatnlo-pythia8',
               'TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8',
               # Zh
               'HZJ_HToWW_M-125', 
               'ggZH_HToBB_ZToLL_M-125_TuneCP5_13TeV-powheg-pythia8', 
               'ggZH_HToBB_ZToNuNu_M-125_TuneCP5_13TeV-powheg-pythia8',
               # ggh, h ->(ll)Z(qq),
               'GluGluHToZZTo2L2Q_M125_TuneCP5_13TeV_powheg2_JHUGenV7011_pythia8', 
               # tth
               'ttHTobb_M125_', 
               'ttHToNonbb_M125_'], 
        'data': [
                'DoubleEG',
                'DoubleMuon',
                'MuonEG',
                'EGamma',
                'SingleElectron',
                'SingleMuon',
            ],
        }
    
    suffix   = ''
    request  = [218, 232, 8, 13]
    all_processes = []
    
    for era in [17]:#18, 17, 16]:
        suffix += f'_{era}'
        
        for dtype, listsmp in look_for.items():
            #if dtype != 'signal':
            #    continue
            if era ==17 and dtype=='data':
                listsmp.remove('SingleElectron')
                listsmp.remove('SingleMuon')
            
            for smp in listsmp:
                all_processes += getSamplesFromDAS(era, smp, dataType=dtype, rm_nlo=True)
        
        #checklocalfiles(era, all_processes, tot_req= 471)
    
    fNm = f'fullanalysisRunIISummer20UL{suffix}_nanov9.txt'
    writeToFile(fNm, all_processes)
    print(f'All das path are saved in: {fNm}')
