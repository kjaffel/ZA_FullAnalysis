import ROOT


era     ='2017'
region  ='boosted'
n       = '6-4' if region=='resolved' else '6' # this doesn't matter it is just for comparaison

ROOT.gROOT.ProcessLine(".L fit.C")
for flav in ['LL', 'ElEl', 'MuMu']:
    rFile   = f'results/ul{era}/{flav}/DYJetsToLL_weightcomb_polfit{n}_{region}_mjj_DataMC_ratio.root'
    wgtFile = f'dyrwt_fct_{region}_{flav}_{era}'
    
    print( 'working on ::', rFile, wgtFile)
    
    ROOT.fit(wgtFile, rFile)
