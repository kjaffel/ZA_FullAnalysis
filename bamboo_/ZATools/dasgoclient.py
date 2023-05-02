# VOMS is needed here
#source /cvmfs/cms.cern.ch/cmsset_default.sh
#voms-proxy-init -voms cms -rfc -valid 192:00

import os, os.path, sys
import subprocess
import glob
from cppyy import gbl

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
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
   
    if dataType == 'mc':
        for ls in [ls_linesAPV, ls_lines]:
            if len(ls) !=2: continue
            
            ext_f = None
            for f in ls:
                if 'ext' in f.decode('utf-8'):
                    ext_ver = f.decode('utf-8').split('_ext')[-1].split('-')[-1]
                    ext_f   = f
            
            if ext_f:
                for f in ls:
                    if not f.decode('utf-8').endswith(ext_ver):
                        print( f'droping {ext_f} this extension does not belong here !')
                        ls.remove(ext_f)
    
    all_smp = (ls_lines + ls_linesAPV if era == 16 else (ls_lines))
    
    if dataType == 'mc':
        all_smp = [ smpNm for smpNm in all_smp if not any(str.encode(x) in smpNm for x in ['PUForTRKv2_TRKv2_', 'PU35ForTRKv2_TRKv2_', 'PUForTRK_TRK_106X', '-PU35ForTRK_TRK_106X_', 'JMENano', 'PUForMUOVal', 'FSUL18_FSUL18_'])] 
        return all_smp
    
    elif dataType == 'signal':
        if rm_nlo: 
            filter_nlosmp = [ smpNm for smpNm in all_smp if not str.encode('_tb-20p00_TuneCP5_bbH4F_13TeV-amcatnlo-pythia8') in smpNm]
            return filter_nlosmp
        else:
            return all_smp
    
    else:
        if era == 17: all_smp = [ smpNm for smpNm in all_smp if not (str.encode('2017G') in smpNm or str.encode('2017H') in smpNm)]
        return all_smp


def writeToFile(fNm, list):
    with open(fNm,"w") as outf:
        for smp in list:
            outf.write(f"{smp.decode('utf-8')}\n")
    outf.close()
    return 


def writeBambooYml(txtF, doSplitTT=False, doSplitDY=False):
    ymlF = txtF.replace('.txt', '.yml')
    Cmd  = ['python', 'writeconfig.py', '--das', txtF, '-o', ymlF]
    if doSplitTT:
        Cmd += ['--doSplitTT']
    if doSplitDY:
        Cmd += ['--doSplitDY']
    try:
        logger.info("running: {}".format(" ".join(Cmd)))
        subprocess.run(Cmd, stdout=subprocess.PIPE).stdout.splitlines()
    except subprocess.CalledProcessError:
        logger.error("Failed to run {0}".format(" ".join(Cmd)))
    return

def checklocalfiles(era, list, s): 
    with open(f"rucio_signalUL{era}__ext2.txt","w") as outf:
        for dbLoc in list:
            dasQuery   = f"'file dataset={dbLoc.decode('utf-8')}'"
            localgoCmd = ["dasgoclient", "-query", dasQuery]
            try:
                print(f"Querying DAS: {' '.join(localgoCmd)}")
                ls_files = [ln.strip() for ln in subprocess.check_output(localgoCmd, stderr=subprocess.STDOUT).decode().split()]
            except subprocess.CalledProcessError:
                logger.error("Failed to run {0}".format(" ".join(localgoCmd)))
            
            files = glob.glob(os.path.join(f'/storage/data/cms/store/{s}/'+ os.path.dirname(ls_files[0]), '*.root'))
            print( os.path.join(f'/storage/data/cms/store/{s}/'+ os.path.dirname(ls_files[0]), '*.root') )
            print( glob.glob(os.path.join('/storage/data/cms/'+ os.path.dirname(ls_files[0]), '*.root')) )
            print( len(files),  len(ls_files) )
            if not files or len(files) != len(ls_files):
                outf.write(f"{dbLoc.decode('utf-8')}\n")
            #try:
            #    rf = gbl.TFile.Open(('/storage/data/cms/',ls_files[0]), "READ")
            #except:# subprocess.CalledProcessError:
            #    outf.write(f"{dbLoc.decode('utf-8')}\n")
    outf.close()
    logger.info( f"rucio request needed for samples saved in :: rucio_signalUL{era}__ext2.txt") 


def ZA_DASGOCILENT(n='', choosen_points=None, _runOn=None):
    all_processes  = []
    AToZH_points = []
    suffix   = ''
    for era in [18, 17, 16]:
        suffix += f'{era}_'
        
        dtype_processes =[]
        for dtype, listsmp in look_for.items():
           
            if not dtype in _runOn:
                continue

            for smp in listsmp:
                
                if era ==17:
                    if smp in ['SingleElectron', 'SingleMuon']:
                        continue
                
                processes = getSamplesFromDAS(era, smp, dataType=dtype, rm_nlo=rm_nlo)
                # take few for quick test !
                if dtype == 'signal':
                    if do in ['chunk', 'HvsA', 'custom']:
                        for p in processes:
                            m = p.decode('utf-8').split('_tb')[0].split('To2L2B_')[-1]
                            m_heavy  = float(m.split('_')[0].split('-')[1].replace('p','.'))
                            m_light  = float(m.split('_')[1].split('-')[1].replace('p','.'))
                        
                            if any(x==(m_heavy, m_light) for x in choosen_points):
                                dtype_processes.append(p)
                            if 'AToZH' in p.decode('utf-8'):
                                AToZH_points.append((m_heavy, m_light))

                    elif do=='full':
                        dtype_processes += processes
                else:
                    dtype_processes += processes
            #s = 'data' if dtype=='data' else 'mc'
            #checklocalfiles(era, dtype_processes, s=s)
        all_processes += dtype_processes
    
    if n !='':
        suffix += f'chunk{n}_'

    #fNm = f'fullanalysisRunIISummer20UL_{suffix}nanov9_AtoZHvsHToZA.txt'
    #fNm = f'fullanalysisRunIISummer20UL_{suffix}nanov9_few_for_fast_unblind.txt'
    #fNm = f'mc_fullanalysisRunIISummer20UL_{suffix}nanov9_for_btagEffMaps.txt'
    #fNm = f'fullanalysisRunIISummer20UL_{suffix}nanov9_noSignal.txt'
    #fNm = f'fullanalysisRunIISummer20UL_{suffix}nanov9_for_skim.txt'
    fNm  = f'fullanalysisRunIISummer20UL_{suffix}nanov9.txt' 
    
    writeToFile(fNm, all_processes)
    print('Available A -> ZH signal points ::', list(set(AToZH_points)))
    print(f'All das path are saved in: {fNm}')
    return fNm


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
               'WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8', 
               'WZZ_TuneCP5_13TeV-amcatnlo-pythia8', 
               'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8', 
               'WJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-pythia8', 
               'TTWJetsToQQ_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8',
               'TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8',
               'TTZToQQ_TuneCP5_13TeV-amcatnlo-pythia8',
               'TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8',
               # Zh
               'HZJ_HToWW_M-125_TuneCP5_13TeV-powheg', 
               'ZH_HToBB_ZToLL_M-125_TuneCP5_13TeV-powheg-pythia8',
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
    
    
    _runOn  = ['signal', 'data', 'mc']
    do = 'chunk' # choices: 'full', 'chunk', 'HvsA', custom
    chunk_of = 20
    
    rm_nlo          = False
    print_bambooCfg = True
    doSplitTT       = True
    doSplitDY       = True

    if do == 'chunk':
        for n in range(chunk_of):
            chunk_of_points = utils.getSignalMassPoints_ver2(chunk=n, do=do, chunk_of=chunk_of)
            choosen_points  = chunk_of_points['HToZA']+chunk_of_points['AToZH']
            logger.info( f'working on batch {n} :: {choosen_points}, len: {len(choosen_points)}')
            outF = ZA_DASGOCILENT(n, choosen_points, _runOn=_runOn)
            if print_bambooCfg:
                writeBambooYml(outF, doSplitTT=doSplitTT, doSplitDY=doSplitDY) 
    
    elif do == 'custom':
        custom_list = [(500.,300.), (500., 250.), (650., 50.), (379.00, 54.59), (510., 130.), (800., 140.), (516.94, 78.52), (800., 200.), (300., 200.), (717.96, 577.65)]
        outF = ZA_DASGOCILENT(n='', choosen_points=custom_list, _runOn=_runOn)
        if print_bambooCfg:
            writeBambooYml(outF, doSplitTT=doSplitTT, doSplitDY=doSplitDY)
    
    elif do == 'full':
        outF = ZA_DASGOCILENT(n='', choosen_points=None, _runOn=_runOn)
        if print_bambooCfg:
            writeBambooYml(outF, doSplitTT=doSplitTT, doSplitDY=doSplitDY) 
        

    elif do == 'HvsA': 
        AToZH_points = [(240.0, 130.0), (300.0, 135.0), (700.0, 200.0), (250.0, 125.0), (750.0, 610.0), (500.0, 250.0), (800.0, 140.0), (200.0, 125.0), (510.0, 130.0), (780.0, 680.0), (220.0, 127.0), (670.0, 500.0), (550.0, 300.0)]
        outF = ZA_DASGOCILENT(n='', choosen_points=AToZH_points, _runOn=_runOn)
        if print_bambooCfg:
            writeBambooYml(outF, doSplitTT=doSplitTT, doSplitDY=doSplitDY)


