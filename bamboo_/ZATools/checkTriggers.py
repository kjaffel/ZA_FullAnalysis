import sys, os, os.path
import glob
from cppyy import gbl


pathNames = {
    2016: {
        "DoubleMuon": [ #"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL",
                        #"HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                        #"HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL",
                        #"HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ",
                        "HLT_TkMu17_TrkIsoVVL_TkMu8_TrkIsoVVL", 
                        "HLT_TkMu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ"
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
        "SingleMuon" : [ 
                     "HLT_IsoMu24", 
                     "HLT_IsoTkMu24",
                     "HLT_Mu50",
                     "HLT_TkMu50",
                   ],
         },
    2017 : {
        "DoubleMuon": [ 
                        "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL",
                        "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
                        "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
                        "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8"
                        ],
        "DoubleEG": [ 
                    "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", 
                    "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"
                    ],
        "MuonEG"  : [ 
                    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL",
                    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
                    "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL",
                    "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ" 
                    ]
                    },
    }


def checkTriggers(era, base_p): 
    year = 2016 if "VFP" in era else int(era)
    for data in ["SingleMuon", "SingleElectron", "MuonEG", "DoubleEG", "DoubleMuon"]:
        for f in glob.glob(os.path.join(base_p, "*.dat")):
            smp = f.split('/')[-1]
            if not smp.startswith(data):
                continue
            
            with open(f) as inF:
                lines = inF.readlines()
            print( f"working on : {smp}" )
            print( f"reading first root file : {lines[1]}")
            
            # too risky to look only for one file ! 
            #fName = lines[1].split()[0]
            for fName in lines[1].split():
                rf = gbl.TFile.Open(fName, "READ")
                if rf:
                    #print("\t---> Checking file {0}".format(fName))
                    tEvt = rf.Get("Events")
                    if tEvt:
                        lvs = set(lv.GetName() for lv in tEvt.GetListOfLeaves())
                        trig_missing = [ trig for trig in pathNames[year][data] if trig not in lvs ]
                        print( f'list of missing triggers : {trig_missing}')
                        print( ' sorry still on ToDo list : check for which run the tigger if OFF ')
                        #tEvt.GetEntry(0)
                        #for path in pathNames[year][data]:
                        #    if hasattr(tEvt, path):
                        #        print("HAS : {0}".format(path))
                        #    else:
                        #        print("NOT : {0}".format(path))
                print("===="*20)
    
if __name__ == "__main__":

    era = "2016-preVFP"
    base_p = f"../bamboo_/config/dascache/nanov9/{era}/"

    checkTriggers(era, base_p)
