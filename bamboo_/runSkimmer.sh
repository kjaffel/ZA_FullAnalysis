
#!/bin/bash
#Be careful this will submit all jobs in the background, assuming the local test is run succesfully
# to test locally try with --maxFiles=1 
echo "ZA-llbb skimmer !"
VER="ver1"
YMLs=("./config/fullanalysis2016_nanov7.yml"
"./config/signales2016legacy_nanoAODv7.yml")

WorkingPoints=("M")
llbb_selections=("2Lep2bJets") #"noSel", "OsLeptons", "2Lep2Jets", "2Lep2bJets"
regions=("boosted" "resolved")
catgories=("MuMu" "ElEl")
Taggers=("DeepCSV" "DeepFlavour")

count=0
for YML in ${YMLs[*]}; do
    count=$((count + 1)) 
    for mysel in ${llbb_selections[*]}; do
        for myreg in ${regions[*]}; do
            for mytag in ${Taggers[*]}; do
                for mywp in ${WorkingPoints[*]}; do
                    for mycat in ${catgories[*]}; do
                        DIR="${mysel}_${myreg,}_${mycat,,}_${mytag,,}${mywp}"
                        if [ $count -eq 1 ]
                        then 
                            eval DATA="backgrounds"
                        else
                            eval DATA="signals21"
                        fi
                        Output_Path="./nanov7/skimmedTree/${VER}/${DATA}/${DIR}"
                        echo "** bambooRun skimmer ***"
                        echo "YML : $YML"
                        echo "Output_Path : $Output_Path"
                    
                        #bambooRun --distributed=driver -s -m skimmedtree_ZAtollbb.py:Skimedtree_NanoHtoZA $YML -o $Output_Path --selections=$mysel --regions=$myreg --categories=$mycat --taggers=$mytag --workingpoints=$mywp &
                        bambooRun --distributed=finalize -s -m skimmedtree_ZAtollbb.py:Skimedtree_NanoHtoZA $YML -o $Output_Path --selections=$mysel --regions=$myreg --categories=$mycat --taggers=$mytag --workingpoints=$mywp
                        #echo "bambooRun successfully submitted for --selections=$mysel --regions=$myreg --categories=$mycat --taggers=$mytag --workingpoints=$mywp"
                        for i in {1..80}; do echo -n '*'; done
                    done
                done
            done
        done
    done
done
