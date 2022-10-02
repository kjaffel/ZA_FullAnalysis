# HIG-22-010: Search for 2HDM neutral Higgs bosons through the H/A → Z (→ ℓℓ ) A/H (→ bb ) processes

## How to run? 
More detailes about the enviroment setup can be found in [here](https://github.com/kjaffel/ZA_FullAnalysis/blob/master/ZAStatAnalysis/README.md)
```bash
cms_env
cd ${CMSSW_BASE}/src
cmsenv
```
## Systematic uncertainties naming conventions for full run2:

1. **Experimental uncertainties:**
`` _<era>`` nuissance parameter are uncorrelated per year; 2016-preVFP, 2016-postVFP, 2017, 2018.

- **Luminosity, normalisation (lnN):**
<!-- TABLE_GENERATE_START -->
| Nuissance parameter                    | 2016 | 2017 | 2018  |
| -------------------------------------  | ---- | ---- | ----- |
| ``lumi_uncorrelated_13TeV_<era>``      | 1.01 | 1.02 | 1.015 |
| ``lumi_correlated_13TeV_<era>``        | 1.006| 1.009| 1.020 |
<!-- TABLE_GENERATE_END -->
Following the latest recommendation, [TWikiLUM](https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM?rev=167#LumiComb), [/physics-announcements-HN](https://hypernews.cern.ch/HyperNews/CMS/get/physics-announcements/6191.html?inline=-1)

- **Pileup, (shape):** 
Pileup uncertainty is uncorrelated across years. Corrections is taken from[cms-nanoaod-integration.web](https://cms-nanoaod-integration.web.cern.ch/commonJSONSFs/LUMI_puWeights_Run2_UL/)
    - ``CMS_pileup_<era>``

- **Jet Energy Scale(JES), (shape):**
JES uncertainties are uncorrelated across years.
For resolved signal regions categories ( .i.e ``nb2 -resolved``, ``nb3- resolved``):
    - ``CMS_scale_j_ToTal_<era>``
`` __ToTal`` means one source/no split per eta regions.
For boosted signal regions categories ( .i.e ``nb2 -boosted``, ``nb3- boosted``):
    - ``CMS_scale_j_fatjet_<era>``

- **Jet Rnergy resolution(JER), (shape):**
JER uncertainties are uncorrelated across years.
For resolved signal regions:
    - ``CMS_res_j_Total_<era>``
`` __ToTal`` means one source/no split per eta regions.
For boosted signal regions:
    - ``CMS_res_j_fatjet_<era>``

- **Lepton identification, reconstruction and isolation, ID/ISO/RECO (shape):**
Uncorrelated across year, for both electrons and muons.
    - **Electrons:**
    - ``CMS_eff_elid_<era>``
    - ``CMS_eff_elreco_lowpt_<era>``    →  RecoBelow20
    - ``CMS_eff_elreco_highpt_<era>``   →  RecoAove20
    - **Muons:**
    - ``CMS_eff_muiso_<era>``
    - ``CMS_eff_muid_<era>``

- **2018 HEM issue:**
- **MET**
- **Drell-Yan reweighting**
- **Trigger efficiency**
- **L1 pre-firing (2016 & 2017)**
- **HLT Z_vtx ( 2017)**
- **B-tagging efficiencies:**

2. **Theory uncertainties:**
``_<process>`` the nuissance parameterts are uncorrelated per process, for both signal and background.
- **Parton distribution functions, (shape):**
    - ``pdf_<process>``
- **Parton shower weights, (shape):**
    - ``ISR_<process>``
    - ``FSR_<process>``
- **Renormalization and factorization scale, (shape):**
    - ``muR_<process>``
    - ``muF_<process>``

3. **MC statistics:**
- We use the Barlow-Beeston-lite approach; each sample receives a NP in each bin which multiplies the bin yield and is constrained according to the pdf of the number of expected events.
