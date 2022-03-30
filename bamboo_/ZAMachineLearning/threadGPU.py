import os 
import sys
import logging
import subprocess
import traceback

from pynvml import *
from pynvml.smi import nvidia_smi
#import nvidia_smi
from time import sleep
from threading import Thread

class utilizationGPU(Thread):
    """
    Class generaring a parallel thread to monitor the GPU usage
    Initialize with : 
        thread = utilizationGPU(print_time = int      # Frequency of printing the average and current GPU usage
                                print_current = bool  # In addition to average, print current usage
                                time_step = float)    # Time step for sampline
    Start thread with: 
        thread.start()
    Will print usage and memory average over the last "print_time" seconds

    Stop the thread with 
        thread.stopLoop() # Important ! : Otherwise the loop will not be stopped properly 
        thread.join()     # Classic
    """
    def __init__(self,print_time=60,print_current=False,time_step=0.01):
        # Call the Thread class's init function
        super(utilizationGPU,self).__init__()
        self.print_time = print_time
        self.print_current = print_current 
        self.time_step = time_step
        self.GPUs = []
        self.occAvgTot  = []
        self.occAvgStep = []
        self.memAvgTot  = []
        self.memAvgStep = []
        self.running = True

        try:
            nvmlInit()
            self.deviceCount = nvmlDeviceGetCount()
            # Get list of handles #
            logging.info("[GPU] Detected devices are :")
            for i in range(self.deviceCount):
                handle = nvidia_smi.nvmlDeviceGetHandleByIndex(i)
                self.GPUs.append(handle)
                logging.info("[GPU] ..... Device %d : %s"%(i, nvmlDeviceGetName(handle)))
                # Records #
                self.occAvgTot.append(0)
                self.occAvgStep.append(0)
                self.memAvgTot.append(0)
                self.memAvgStep.append(0)
            logging.info("[GPU] Will print usage every %d seconds"%self.print_time)
        except Exception as e:
            logging.error("[GPU] *** Caught exception: %s : %s"%(str(e.__class__),str(e)))
            traceback.print_exc()
          
   # Override the run function of Thread class
    def run(self):
        import random
        self.time_step = 0.01
        counter = 0
        print_counter = 0
        while(self.running):
            res = []
            for i in range(self.deviceCount):
                res.append(nvidia_smi.nvmlDeviceGetUtilizationRates(self.GPUs[i]))

            # Print every self.print_time #
            if print_counter == int(self.print_time/self.time_step):
                # Print current #
                if self.print_current:
                    s = "\t[GPU] "
                    for i in range(self.deviceCount):
                        s += "Device %d %s : utilization : %d%%, memory : %d%%\t"%(i, nvmlDeviceGetName(self.GPUs[i]),res[i].gpu,res[i].memory)
                    logging.info(s)
                # Print avg #
                if self.print_time<60:
                    logging.info("\n[GPU] Occupation over the last %d seconds"%self.print_time)
                else:
                    minutes = self.print_time//60
                    seconds = self.print_time%60
                    logging.info("\n[GPU] Occupation over the last %d minutes, %d seconds"%(minutes,seconds))
                    
                s = "[GPU] "
                for i in range(self.deviceCount):
                    self.occAvgStep[i] /= (print_counter*self.time_step)
                    self.memAvgStep[i] /= (print_counter*self.time_step)
                    s += "Device %d %s : utilization : %d%%, memory : %d%%\t"%(i, nvmlDeviceGetName(self.GPUs[i]),self.occAvgStep[i],self.memAvgStep[i])
                    # Reinitialize average #
                    self.occAvgStep[i] = 0
                    self.memAvgStep[i] = 0
                logging.info(s)
                # reset printing counter #
                print_counter = 0
                
            # Add to total and step #
            for i in range(self.deviceCount):
                self.occAvgTot[i] += res[i].gpu*self.time_step
                self.occAvgStep[i] += res[i].gpu*self.time_step
                self.memAvgTot[i] += res[i].memory*self.time_step
                self.memAvgStep[i] += res[i].memory*self.time_step

            # Sleep and counters #
            print_counter += 1
            counter += 1
            sleep(self.time_step)
        
        # Print total #
        logging.info("[GPU] Average occupation over whole period")
        s = "[GPU] "
        for i in range(self.deviceCount):
            self.occAvgTot[i] /= (counter*self.time_step)
            self.memAvgTot[i] /= (counter*self.time_step)
            s += "Device %d %s : utilization : %d%%, memory : %d%%\t"%(i, nvmlDeviceGetName(self.GPUs[i]),self.occAvgTot[i],self.memAvgTot[i])
        logging.info(s)
    
    def stopLoop(self):
        self.running = False    
