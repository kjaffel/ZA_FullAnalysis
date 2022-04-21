import os, os.path, sys
import subprocess
import glob
from cppyy import gbl

sys.path.append('/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/')
import utils as utils
logger = utils.ZAlogger(__name__)


def getSignalSamples(era, signal):
    dasgoCmd     = ['dasgoclient', '-query', f'/{signal}*/RunIISummer20UL{era}*AODv9*/NANOAODSIM']
    dasgoCmd_APV = ['dasgoclient', '-query', f'/{signal}*/RunIISummer20UL{era}*AODAPVv9*/NANOAODSIM']
    try:
        logger.info("running: {}".format(" ".join(dasgoCmd)))
        ls_lines = subprocess.run(dasgoCmd, stdout=subprocess.PIPE).stdout.splitlines()
        if era == 16:
            ls_linesAPV = subprocess.run(dasgoCmd_APV, stdout=subprocess.PIPE).stdout.splitlines()
    except subprocess.CalledProcessError:
        logger.error("Failed to run {0}".format(" ".join(dasgoCmd)))
    
    return (ls_lines + ls_linesAPV if era == 16 else (ls_lines))

def checklocalfiles(era, list, tot_req): 
    i = 0 
    with open(f"rucio_signalUL{era}.txt","w") as outf:
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
            print( len(files),  len(ls_files) , not files or len(files) != len(ls_files))
            if not files or len(files) != len(ls_files):
                outf.write(f"{dbLoc.decode('utf-8')}\n")
            #try:
            #    rf = gbl.TFile.Open(('/storage/data/cms/',ls_files[0]), "READ")
            #except:# subprocess.CalledProcessError:
            #    outf.write(f"{dbLoc.decode('utf-8')}\n")
    outf.close()
    logger.info( f" {i} out of {tot_req} samples are ready, you are getting there: {i/tot_req*100}%"
    logger.info( f"rucio request needed for samples saved in :: rucio_signalUL{era}.txt") 

for era in [16]:#, 17, 16]:
    all_signals = []
    request = [218, 232, 8, 13]
    for signal in['GluGluToHToZATo2L2B', 'HToZATo2L2B', 'GluGluToAToZHTo2L2B', 'AToZHTo2L2B']:
        all_signals += getSignalSamples(era, signal)
    
    checklocalfiles(era, all_signals, request= 471)
