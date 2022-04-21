import sys, os, os.path
import glob
from cppyy import gbl

era = "2016-preVFP"

pathNames = {
2016: {
    "DoubleMuon": [ "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL",
                    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                    "HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL",
                    "HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ", 
                    ],
    "DoubleEG": [ "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
                  "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", 
                  ],
    "MuonEG"  : [ "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
                  "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                  "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL",
                  "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                  "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
                  "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL",
                  "HLT_IsoMu24",
                  ],
        },
2017 : {
    "DoubleMuon": [ "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL",
                    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
                    "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8"],
    "DoubleEG": [ "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", 
                  "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"],
    "MuonEG"  : [ "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
                  "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                  "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL",
                  "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ" ]
                    },
}

base_p = f"/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/config/dascache/nanov9/{era}/"
year = 2016 if "VFP" in era else int(era)

#for data in ["MuonEG", "DoubleEG", "DoubleMuon"]:
for data in ["DoubleEG"]:
    for f in glob.glob(os.path.join(base_p, "*.dat")):
        smp = f.split('/')[-1]
        if not smp.startswith(data):
            continue
        
        with open(f) as inF:
            lines = inF.readlines()
        print( f"working on : {smp}" )
        print( f"reading first root file : {lines[1]}")
        
        fName = lines[1].split()[0]
        rf = gbl.TFile.Open(fName, "READ")
        if rf:
            #print("\t---> Checking file {0}".format(fName))
            tEvt = rf.Get("Events")
            if tEvt:
                lvs = set(lv.GetName() for lv in tEvt.GetListOfLeaves())
                trig_missing = [ trig for trig in pathNames[year][data] if trig not in lvs ]
                print( f'list of missing triggers : {trig_missing}')
                #tEvt.GetEntry(0)
                #for path in pathNames[year][data]:
                #    if hasattr(tEvt, path):
                #        print("HAS : {0}".format(path))
                #    else:
                #        print("NOT : {0}".format(path))
        print("===="*20)
