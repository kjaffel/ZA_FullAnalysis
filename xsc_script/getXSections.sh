#! /bin/bash
# Author: Izaak Neutelings (August 2018)
# 1) Install genXsecAnalyzer: https://twiki.cern.ch/twiki/bin/view/CMS/HowToGenXSecAnalyzer
# 2) Make a text file "samples.txt" with a list of DAS paths of samples you want the cross sections for
#    to find the complete paths, use e.g.
#    $ dasgoclient --limit=0 --query="dataset=/DY*JetsToLL_M-50_TuneCP5*/*94X*/MINIAODSIM"

START=`date +%s`
SAMPLEFILE="samples.txt"
MAXFILES=-1



function main {
  
  ensureDir "log"
  
  LOGFILES=""
  DASPATHS=`cat $SAMPLEFILE | sed 's/\#.*//g'`
  for daspath in $DASPATHS; do
    [[ $daspath == "#"* ]] && continue
    header "$(echo $daspath | cut -d '/' -f2)"
    echo ">>> getting $MAXFILES root files for \"$daspath\"..."
    
    #dasgoclient --limit=0 --query="dataset=/DYJetsToLL_M-50_TuneCP5_13TeV-*/RunIIFall17MiniAODv2-*/MINIAODSIM"
    #dasgoclient --limit=0 --query="dataset=$DASPATH" | sort -n
    #dasgoclient -query="summary dataset=$daspath" | grep -Po '(?<=events":)\d+'
    
    # CREATE LOG FILE
    LOG=`formatLogName $daspath`
    LOGFILES+="$LOG "
    echo `date` > $LOG
    echo ">>> DASPATH=$daspath" >> $LOG
    echo ">>> log file \"${LOG}\""
    
    # GET SOME ROOT FILES
    ROOTFILES=`dasgoclient -query="file dataset=$daspath" | head -n $MAXFILES`
    printf "\n>>> $MAXFILES input files:\n${ROOTFILES}\n" >> $LOG
    ROOTFILES=`echo "$ROOTFILES" | awk -vORS=, '{ print $1 }' | sed 's/,$/\n/'` # comma-separated
    
    # CALCULATE CROSS SECTION
    echo ">>> calculate cross section:" | tee -a $LOG
    peval "cmsRun ana.py inputFiles=\"${ROOTFILES}\"" 2>&1 | tee -a $LOG || exit 1
    
  done
  
  # SUMMARIZE
  header "cross sections summary"
  for logfile in $LOGFILES; do
    DASPATH=`grep -m1 -oP "DASPATH=\K.*" $logfile`
    XSEC=`grep -m1 -oP "After filter: final cross section = \K.*" $logfile`
    [[ $DASPATH = *"amcatnlo"* ]] && ORDER="(NLO)" || ORDER=""
    echo ">>> $(tput setab 0)$(tput setaf 7)${DASPATH}:$(tput sgr0)"
    echo ">>>   $(tput setab 0)$(tput setaf 7)${XSEC}$(tput sgr0) $ORDER"
    echo ">>> "
  done
  
}



function peval { # print and evaluate given command
  echo -e ">>> $(tput setab 0)$(tput setaf 7)$@$(tput sgr0)"
  eval "$@";
}

function header { # print box around given string
  local HDR="$@"
  local BAR=`printf '#%.0s' $(seq 1 ${#HDR})`
  printf "\n\n\n"
  echo ">>>     $A####${BAR}####$E"
  echo ">>>     $A#   ${HDR}   #$E"
  echo ">>>     $A####${BAR}####$E"
  echo ">>> ";
}

function formatLogName { # make log filename
  BASE="$(echo $1 | cut -d '/' -f2)"
  CAMPAIGN="$(echo $1 | cut -d '/' -f3)"
  LOG="log/${BASE}.log"
  printf "$LOG"
}

function ensureDir { # check if directory exists, else create it
  [ -e "$1" ] || { echo ">>> making $1 directory..."; mkdir "$1"; }
}

function runtime { # print out runtime
  END=`date +%s`; RUNTIME=$((END-START))
  printf "%d minutes %d seconds" "$(( $RUNTIME / 60 ))" "$(( $RUNTIME % 60 ))"
}

echo
main
echo ">>> "
echo ">>> ${A}done in $(runtime)$E"
echo

exit 0
