import sys, os, os.path
import glob 
import subprocess
import argparse
import Constants as Constants
logger = Constants.ZAlogger(__name__)
base   = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/'

def runPlotIt_postFits(workdir=None):
    scripts = glob.glob(os.path.join(workdir, 'postfit/', '*/', '*/', '*_do_postfit.sh'))
    for script in scripts:
        scriptNm = script.split('/')[-1]
        os.chdir(os.path.join(base, script.split(scriptNm)[0]))
        cmd = ["bash", scripts]
        try:
            logger.debug("running {}".format(" ".join(cmd)))
            subprocess.check_call(cmd)#, stdout=subprocess.DEVNULL) 
        except subprocess.CalledProcessError:
            logger.error("Failed to run {0}".format(" ".join(cmd)))
        
        print(f"start working on : {os.path.join(base, script.split(scriptNm)[0])}" )
        print("==="*60)
        plotit_histos = glob.glob(os.path.join(os.getcwd(), 'plotIt_*'))
        for plotitdir in plotit_histos:
            output = plotitdir.split('/')[-1]
            with open(f"{base}/data/ZA_plotter_all_shapes_postfit_template.yml", 'r') as inf:
                with open(f"{output}/plots.yml", 'w+') as outf:
                    for line in inf:
                        if '  root: root_path' in line:
                            outf.write(f"  root: {output}\n")
                        else:
                            outf.write(line)
            
            plotitCmd = ["/home/ucl/cp3/kjaffel/bamboodev/plotIt/plotIt", "-o", output, "--", f"{output}/plots.yml"]
            try:
                logger.info("running {}".format(" ".join(plotitCmd)))
                subprocess.check_call(plotitCmd)#, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                logger.error("Failed to run {0}".format(" ".join(plotitCmd)))
        os.chdir(base)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PreFit/PostFit Producer')
    parser.add_argument('--inputs', action='store', required=True, default=None, help='')

    options = parser.parse_args()
    runPlotIt_postFits(workdir=options.inputs)
