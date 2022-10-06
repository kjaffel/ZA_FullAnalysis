# HIG-22-010: Search for 2HDM neutral Higgs bosons through the H/A → Z (→ ℓℓ ) A/H (→ bb ) processes
The most up-to-date original repository can be found [here](https://github.com/kjaffel/ZA_FullAnalysis/blob/master/ZAStatAnalysis).

## CombinedLimit: CC7 release CMSSW_10_2_X - recommended version
- Setting up the environment (once):
```bash
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
```
- Update to a reccomended tag - currently the reccomended tag is v8.2.0: see [release notes](https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/releases/tag/v8.2.0)

```bash
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.2.0
scramv1 b clean; scramv1 b # always make a clean build
```
- Now the repository contains a certain amount of analysis-specific code, the following scripts can be used to clone it with a sparse checkout for just the core [CombineHarvester/CombineTools](https://github.com/cms-analysis/CombineHarvester/tree/master/CombineTools) subpackage, speeding up the checkout and compile times:
- Read more about [CombineHarvester](http://cms-analysis.github.io/CombineHarvester/) framework for the production and analysis of datacards for use with the CMS combine tool.

## Combine Tools:
This repository is a "top-level" CMSSW package, so it should be located at [$CMSSW_BASE/src/CombineHarvester](https://cms-analysis.github.io/CombineHarvester/index.html#getting-started).
- git clone via ssh:
```bash
bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-ssh.sh)
```
- git clone via https:
```bash
bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-https.sh)
```
- make sure to run [scram]() to compile the [CombineTools]() package.

## How to run? 
```bash
cd ${CMSSW_BASE}/src
cmsenv
run_combine.sh
```
``run_combine.sh`` can be used to run different command of combine

```bash
#=============== YOUR INPUTS ==============================
#==========================================================
mode='dnn'
#choices: 'mbb', 'mllbb'

era='2016'
#choices: '2016' , '2017' , '2018', 'fullrun2'  

scenario='bayesian_rebin_on_S'
#choices: 'bayesian_rebin_on_S', 'bayesian_rebin_on_B' , 'bayesian_rebin_on_hybride', 'uniform'

do_what='fit'
#choices: 'goodness_of_fit', 'hybridnew', 'generate_toys', 'asymptotic', 'pvalue', 'impacts', 'signal_strength', 

_2POIs_r=true
# 2 POIs: r_ggH and r_bbH 
# if this flagged false, r_ggH +r_bbH will be combined ( i.e. in one histogram), so you need to give a tanbeta value

tanbeta=1.5
#choices: any value you want
# Just make sure you already run Sushi and 2HDMC, so you have the results saved in 
# data/sushi1.7.0-xsc_tanbeta-1.50_2hdm-type2.yml

bambooDir='ul_run2__ver19/results/' # inputs root files before BB rebinning
stageOut='hig-22-010/datacards/'    # output dir

#================ PLEASE DO NOT CHANGE =============================
#===================================================================
workDir='work__UL'${era/20/""}'/'
inDir=$stageOut$workDir
outDir=$inDir

```
- ``run_combine.sh`` will call ``./prepareShapesAndCards.py``. With the given inputs above ( ``fit == pre-/post-fit``) 
, Combine commands will be written to ``*.sh`` and the datacards to ``*.dat``. Both will be saved in the directory :``${stageOut}/${workDir}$/${scenario}/fit/${mode}/2POIs_r/MH-xxx_MA-xxx``. 
Then the script will automatically launch these commands from ``./run_combined_${mode}_preposfit.sh``

## Running Combine Tools:
To briefly summarize the commands used for each Combine task;
```bash

#==================================  H → ZA =================================
#============================================================================
do_what='fit'

combine -M FitDiagnostics --rMax 20 -m 125 -t -1 --saveWithUncertainties --ignoreCovWarning -n HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_500.0_MA_50.0 HToZATo2L2B_bb_associatedProduction_nb2_resolved_OSSF_dnn_MH_500.0_MA_50.0_combine_workspace.root --plots

CAT=dnn_MH_${mH}_MA_${mA}

#fit_b   RooFitResult object containing the outcome of the fit of the data with signal strength set to zero
#fit_s   RooFitResult object containing the outcome of the fit of the data with floating signal strength

# Create pre/post-fit shapes 
fit_what=fit_s
PostFitShapesFromWorkspace -w HToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA}_combine_workspace.root -d HToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA}.dat -o fit_shapes_${CAT}_${fit_what}.root -f fitDiagnosticsHToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA}.root:${fit_what} -m 125 --postfit --sampling --covariance --total-shapes --print
$CMSSW_BASE/../utils/convertPrePostfitShapesForPlotIt.py -i fit_shapes_${CAT}_${fit_what}.root -o plotIt_${process}_${cat}_${region}_${flavor}_${fit_what} --signal-process HToZATo2L2B -n dnn_scores

fit_what=fit_b
PostFitShapesFromWorkspace -w HToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA}_combine_workspace.root -d HToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA}.dat -o fit_shapes_${CAT}_${fit_what}.root -f fitDiagnosticsHToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA}.root:${fit_what} -m 125 --postfit --sampling --covariance --total-shapes --print
$CMSSW_BASE/../utils/convertPrePostfitShapesForPlotIt.py -i fit_shapes_${CAT}_${fit_what}.root -o plotIt_${process}_${cat}_${region}_${flavor}_${fit_what} --signal-process HToZATo2L2B -n dnn_scores

#============================================================================
do_what='asymptotic'

combine -M AsymptoticLimits --rMax 20 -m 125 -n HToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA} HToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA}_combine_workspace.root --noFitAsimov --rule CLsplusb --run blind

#============================================================================
do_what='impacts'

combineTool.py -M Impacts --rMin -20 --rMax 20 -d HToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA} HToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA}_combine_workspace.root -m 125 -t -1 --expectSignal 0 --doInitialFit --robustFit 1 
combineTool.py -M Impacts --rMin -20 --rMax 20 -d HToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA} HToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA}_combine_workspace.root -m 125 -t -1 --expectSignal 0 --robustFit 1 --doFits --parallel 30 
combineTool.py -M Impacts --rMin -20 --rMax 20 -d HToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA} HToZATo2L2B_${process}_${cat}_${region}_${flavor}_dnn_MH_${mH}_MA_${mA}_combine_workspace.root -m 125 -t -1 --expectSignal 0 -o impacts__${process}_${cat}_${region}_${flavor}_expectSignal0_asimovdataset.json
plotImpacts.py -i impacts__${process}_${cat}_${region}_${flavor}_expectSignal0_asimovdataset.json -o impacts__${process}_${cat}_${region}_${flavor}_expectSignal0_asimovdataset

#============================================================================
```
## Systematic uncertainties naming conventions for full run2:

1. **Experimental uncertainties:**
`` _<era>`` means nuissance parameters are uncorrelated per year; 2016-preVFP, 2016-postVFP, 2017, 2018.

- **Luminosity, normalisation (lnN):**
<!-- TABLE_GENERATE_START -->
| Nuissance parameter                    | 2016 | 2017 | 2018  |
| -------------------------------------  | ---- | ---- | ----- |
| ``lumi_uncorrelated_13TeV_<era>``      | 1.01 | 1.02 | 1.015 |
| ``lumi_correlated_13TeV_<era>``        | 1.006| 1.009| 1.020 |
<!-- TABLE_GENERATE_END -->
Following the latest recommendation, [TWikiLUM](https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM?rev=167#LumiComb), [physics-announcements-HN](https://hypernews.cern.ch/HyperNews/CMS/get/physics-announcements/6191.html?inline=-1)

- **Pileup, (shape):** 
Pileup uncertainty is uncorrelated across years. Corrections is taken from [cms-nanoaod-integration.web](https://cms-nanoaod-integration.web.cern.ch/commonJSONSFs/LUMI_puWeights_Run2_UL/)
    - ``CMS_pileup_<era>``

- **Jet Energy Scale(JES), (shape):**
JES uncertainties are uncorrelated across years. 
    - **For resolved signal regions categories ( .i.e ``nb2 -resolved``, ``nb3 -resolved``):**
    - ``CMS_scale_j_ToTal_<era>``, `` __ToTal`` means one source/no split per eta regions.
    - **For boosted signal regions categories ( .i.e ``nb2 -boosted``, ``nb3 -boosted``):**
    - ``CMS_scale_j_fatjet_<era>``

- **Jet Rnergy resolution(JER), (shape):**
JER uncertainties are uncorrelated across years.
    - **For resolved signal regions categories ( .i.e ``nb2 -resolved``, ``nb3 -resolved``):**
    - ``CMS_res_j_Total_<era>`` , `` __ToTal`` means one source/no split per eta regions.
    - **For boosted signal regions categories ( .i.e ``nb2 -boosted``, ``nb3 -boosted``):**
    - ``CMS_res_j_fatjet_<era>``

- **Lepton identification, reconstruction and isolation, ID/ISO/RECO (shape):**
100% correlated across year, for both electrons and muons. Following latest EGamma recommendation on [ combining systematics](https://twiki.cern.ch/twiki/bin/view/CMS/EgammaUL2016To2018#A_note_on_Combining_Systematics).
    - **Electrons:**
    - ``CMS_eff_elid``
    - ``CMS_eff_elreco_lowpt``    →  RecoBelow20
    - ``CMS_eff_elreco_highpt``   →  RecoAbove20
    - **Muons:**
    - ``CMS_eff_muiso``
    - ``CMS_eff_muid``

- **2018 HEM issue, (shape):**
Treatment of the HEM15/16 region in 2018 data , see [HN](https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/2000.html)
    - ``CMS_HEM_2018``

- **MET, (shape):**
    - ``CMS_UnclusteredEn_<era>``

- **Drell-Yan reweighting, (shape):**
Uncorrelated accross year, lepton flavours, and signal regions.
``<ploy-fit-order_n>`` = 7 if ``<era>``==2017 else 6
    - **For resolved signal regions categories ( .i.e ``nb2 -resolved``, ``nb3 -resolved``):**
    - ``DYweight_resolved_elel_ployfit_lowmass<ploy-fit-order_n>_highmass5_<era>``
    - ``DYweight_resolved_mumu_ployfit_lowmass<ploy-fit-order_n>_highmass5_<era>``
    - ``DYweight_resolved_muel_ployfit_lowmass<ploy-fit-order_n>_highmass5_<era>``
    - **For boosted signal regions categories ( .i.e ``nb2 -boosted``, ``nb3 -boosted``):**
    - ``DYweight_boosted_elel_ployfit_lowmass<ploy-fit-order_n>_<era>``
    - ``DYweight_boosted_mumu_ployfit_lowmass<ploy-fit-order_n>_<era>``
    - ``DYweight_boosted_muel_ployfit_lowmass<ploy-fit-order_n>_<era>``

- **Trigger efficiencies, (shape):**
Uncorrelated per year, lepton flavours.
    - ``CMS_elel_trigSF_<era>``
    - ``CMS_mumu_trigSF_<era>``
    - ``CMS_muel_trigSF_<era>``

- **L1 pre-firing, (shape):**
Correlated, more details [here](https://twiki.cern.ch/twiki/bin/viewauth/CMS/L1PrefiringWeightRecipe), available in NanoAOD [branches](https://cms-nanoaod-integration.web.cern.ch/integration/cms-swCMSSW_10_6_19/mc106Xul17_doc.html#L1PreFiringWeight)
    - ``CMS_L1PreFiring``

- **HLT Z-vtx, (shape):**
    - ``CMS_HLTZvtx_2017``

- **B-tagging efficiencies, (shape):**
Uncorrelated per year and jet flavour.
    - **For resolved signal regions categories ( .i.e ``nb2 -resolved``, ``nb3 -resolved``):**
    - ``CMS_btag_light_<era>``
    - ``CMS_btag_heavy_<era>``
    - **For boosted signal regions categories ( .i.e ``nb2 -boosted``, ``nb3 -boosted``):** 
    - ``CMS_btag_subjet_light_<era>``
    - ``CMS_btag_subjet_heavy_<era>``

2. **Theory uncertainties:**

``_<process>`` means nuissance parameters are uncorrelated per process, for both signal and background.
- **Parton distribution functions, (shape):**
    - ``pdf_<process>``
- **Parton shower weights, (shape):**
    - ``ISR_<process>``
    - ``FSR_<process>``
- **Renormalization and factorization scale, (shape):**
    - ``qcdmuR_<process>``
    - ``qcdmuF_<process>``
- **Cross-section uncertainty, (lnN):**
    - **Signals, (lnN):**
One for each generated signal sample, correlated across year. Taken from [Sushi](https://sushi.hepforge.org/), which varies depending on the assumed ``(mH, mA)``, ``tanbeta``, and ``cos( beta-alpha)``.
    - H → ZA : ``ggH_xsc``, ``bbH_xsc``
    - A → ZH : ``ggA_xsc``, ``bbA_xsc``
    - **Backgrounds, (lnN):**
One for the main backgrounds, correlated across year. Taken from the [summary table](https://twiki.cern.ch/twiki/bin/viewauth/CMS/SummaryTable1G25ns), [cross-section database](https://cms-gen-dev.cern.ch/xsdb).
    - ``SingleTop_xsc: 0.97541``
    - ``DY_xsc: 1.00784 ``
    - ``ttbar_xsc: 1.00153``
3. **MC statistics:**

- We use [the Barlow-Beeston-lite approach](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/tutorial2020/exercise/#c-mc-statistical-uncertainties); each sample receives a NP in each bin which multiplies the bin yield and is constrained according to the pdf of the number of expected events.
