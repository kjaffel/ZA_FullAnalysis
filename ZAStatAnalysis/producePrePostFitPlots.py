import sys, os, os.path
import glob 
import subprocess
import argparse
import Constants as Constants
logger = Constants.ZAlogger(__name__)
base   = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/'

def runPlotIt_prepostFit(workdir=None, mode=None):
        
        plotit_histos = glob.glob(os.path.join(workdir, 'fit/', mode,'*/', 'plotIt_*'))
        print( plotit_histos)
        for fit in ['prefit', 'postfit']:
            for cat_path in plotit_histos:
                output     = cat_path.split('/')[-1]
                os.chdir(os.path.join(base, cat_path.split(output)[0]))
                os.getcwd()

                process    = 'ggH' if 'gg_fusion' in output else 'bbH'
                params     = cat_path.split('/')[-2]
                signal_smp = f'{process}: {params}'
                flavor     = 'ee channel' if 'ElEl' in output else r'$\mu^+\mu^-$ channel'
                region     = 'resolved' if 'resolved' in output else 'boosted'
                with open(f"{base}/data/ZA_plotter_all_shapes_prepostfit_template.yml", 'r') as inf:
                    with open(f"{output}/{fit}_plots.yml", 'w+') as outf:
                        for line in inf:
                            if '  root: myroot_path' in line:
                                outf.write(f"  root: {output}\n")
                            elif 'fit-type' in line:
                                outf.write("{}\n".format(line.replace('fit-type', fit)))
                            elif '    legend: mysignal' in line:
                                outf.write(f"    legend: '{signal_smp}'\n")
                            elif '      text: mychannel' in line:
                                outf.write(f"      text: {region}, {flavor}\n")
                            else:
                                outf.write(line)
                
                plotitCmd = ["/home/ucl/cp3/kjaffel/bamboodev/plotIt/plotIt", "-o", output, "--", f"{output}/{fit}_plots.yml"]
                try:
                    logger.info("running {}".format(" ".join(plotitCmd)))
                    subprocess.check_call(plotitCmd)#, stdout=subprocess.DEVNULL)
                except subprocess.CalledProcessError:
                    logger.error("Failed to run {0}".format(" ".join(plotitCmd)))
                print(f' plot saved in :: {cat_path}/dnn_scores.png')
                print(f' plot saved in :: {cat_path}/dnn_scores_logy.png')
            os.chdir(base)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PreFit/PostFit Producer')
    parser.add_argument('-i', '--inputs', action='store', required=True, default=None, 
                help='Path to work dir ( output given when running prepareShapesAndCards.py script with arg --method fit )')
    parser.add_argument('-m', '--mode', action='store', required=True, default=None, choices=['mjj_vs_mlljj', 'mjj_and_mlljj', 'mjj', 'mlljj', 'ellipse', 'dnn'], 
                help='posfit plots produced for one of these mode')

    options = parser.parse_args()
    runPlotIt_prepostFit(workdir=options.inputs, mode=options.mode)
