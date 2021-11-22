import sys, os, os.path
import glob 
import subprocess
import argparse
import Constants as Constants
logger = Constants.ZAlogger(__name__)
base   = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/ZAStatAnalysis/'

def runPlotIt_postFits(workdir=None):
        
        plotit_histos = glob.glob(os.path.join(workdir, 'fit/', '*/','*/', 'plotIt_*'))
        for cat_path in plotit_histos:
            output     = cat_path.split('/')[-1]
            os.chdir(os.path.join(base, cat_path.split(output)[0]))
            process    = 'ggH' if 'gg_fusion' in output else 'bbH'
            params     = cat_path.split('/')[-2]
            signal_smp = f'{process}: params'
            flavor     =  'ee channel' if output.endswith('ElEl') else '#mu#mu channel'
            region     = 'resolved' if 'resolved' in output else 'boosted'
            with open(f"{base}/data/ZA_plotter_all_shapes_postfit_template.yml", 'r') as inf:
                with open(f"{output}/plots.yml", 'w+') as outf:
                    for line in inf:
                        if '  root: myroot_path' in line:
                            outf.write(f"  root: {output}\n")
                        elif '    label: mysignal' in line:
                            outf.write(f"    label: '{signal_smp}'\n")
                        elif '      text: mychannel' in line:
                            outf.write(f"      text: {region}, {flavor}\n")
                        else:
                            outf.write(line)
            plotitCmd = ["/home/ucl/cp3/kjaffel/bamboodev/plotIt/plotIt", "-o", output, "--", f"{output}/plots.yml"]
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
    parser.add_argument('--inputs', action='store', required=True, default=None, help='')

    options = parser.parse_args()
    runPlotIt_postFits(workdir=options.inputs)
