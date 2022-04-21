import argparse, optparse
import subprocess
import utils as utils
logger = utils.ZAlogger(__name__)

def RunBambooCmd(submit=None, outputDIR= None, processes=None, sys=False, standalone=False):
    YMLs={"signal_and_bkg": "./config/mc_sig_RunIISummer20UL16_nanov9.yml",}
          #"backgrounds"  : "./config/mainUl16_bkgs_nanoAODv8.yml",}
          #"signals21"    : "./config/signales2016legacy_nanoAODv7.yml"}

    Taggers        =["DeepCSV"]#, "DeepFlavour"]
    WorkingPoints  =["M"] # "L", "T"
    llbb_selections=["2Lep2bJets"]#"noSel", "OsLeptons", "2Lep2Jets", "2Lep2bJets"
    regions        =["resolved", "boosted"]
    catgories      =["MuMu", "ElEl"]
    
    if standalone:
        for myproc in processes:
            for DATA, YML in YMLs.items():
                for mysel in llbb_selections:
                    for myreg in regions:
                        for mytag in Taggers:
                            for mywp in WorkingPoints:
                                for mycat in catgories:
                                
                                    DIR= f"{mysel}_{myreg}_{mycat.lower()}_{mytag.lower()}{mywp}"
                                    Output_Path= f"{outputDIR}/{DATA}/{myproc}/{DIR}"
                                    
                                    SkimmerCmd = ["bambooRun",  submit, "-m", "ZAtollbbSkimmer.py:Skimedtree_NanoHtoZA", YML, "-o", Output_Path, "--processes", myproc, "--selections", mysel, "--regions", myreg, "--categories", mycat, "--taggers", mytag, "--workingpoints", mywp]
                                    try:
                                        logger.debug("Running Bamboo skimmer with the given command: {}".format(" ".join(SkimmerCmd)))
                                        subprocess.check_call(SkimmerCmd)#, stdout=subprocess.DEVNULL) 
                                    except subprocess.CalledProcessError:
                                        logger.error("Failed to run {0}".format(" ".join(SkimmerCmd)))
    else:
        for yml in YMLs.values():
            SkimmerCmd = ["bambooRun",  submit, "--skim", "-m", "ZAtollbb.py:NanoHtoZA", yml, "-o", f"{outputDIR}"]
            if sys: 
                SkimmerCmd += [-s]
            try:
                logger.debug("Running Bamboo skimmer with the given command: {}".format(" ".join(SkimmerCmd)))
                subprocess.check_call(SkimmerCmd)#, stdout=subprocess.DEVNULL) 
            except subprocess.CalledProcessError:
                logger.error("Failed to run {0}".format(" ".join(SkimmerCmd)))
                    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='run ZA skimmer ', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-o', '--output', required=True, help='output directory')
    parser.add_argument('-p', '--process', required=False, nargs="+", default=['ggH', 'bbH'], help='processes: we want 1 DNN per process')
    parser.add_argument('--submit', required=True, choices=['worker', 'driver', 'onlypost', 'finalize', 'max1'], help='submit to slurm or just test locally')
    parser.add_argument('--standalone', action="store_true", default=False, help='In this mode ZAtollbbSkimmer.py will  be used : you need to pass the tagger , regions , selections for such skim. The 2nd options is the most up to date skim')
    parser.add_argument("-s", "--systematic", action="store_true", default=False, help="Produce systematic variations") 
    options = parser.parse_args()
    
    if options.submit in ["worker", "driver", "finalize"]:
        submit_opt = f"--distributed={options.submit}"
    elif options.submit =="max1":
        submit_opt = "--maxFiles=1"
    else:
        submit_opt = "--onlypost"
    
    if options.standalone:
        logger.warning('\t !! This mode is deprecated, recomended not to use !!') 
    
    RunBambooCmd(submit= submit_opt, outputDIR=options.output, processes=options.process, sys=options.systematic, standalone=options.standalone)
