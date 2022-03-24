# TTbar estimation from data

Knowing that the ``MuEl`` region has mostly ttbar (and a small contribution from Single Top), we can compute the ttbar from data as:
```
ttbar_data = data_elmu - SingleTop.
```
Steps needed to achieve this:

1- Compare the shapes of various distributions (mll, mbb, mllbb, ...) for ttbar_data (defined above) and ttbar from MC in the MuMu and ElEl region separately.
This is done in the script ``compareShapesForTTbarEstim.py``

In the script, you can decide whether to enable the SingleTop subtraction or not, through the boolean ``**subtractSingleTop**``. 
The output files are saved in the folder ``plots_ul{era}``.
Make sure that the shapes are the same!

2- With comparing the shapes in ``MuEl`` and ``MuMu(ElEl)`` regions, you make sure that ttbar_data is actually ttbar, so that it can be used to extract the ttbar contribution in ``m_bb`` and ``m_llbb`` distributions: data_elmu can actually replace ttbar MC MuMu (ElEl) in the various distirbutions. But how to normalize?
Let's choose a CR full of ttbar: **high MET tail of MET distribution**.
In the MET distribution with inverted MET cut (high MET tail) in ``MuEl`` category, let's replace the ttbar from MC with ttbar_data. 
The normalization there is of course good!
Let's now switch to the MET distribution with inverted MET cut in ``MuMu(ElEl)`` category, and let's replace the ttbar from MC with the ttbar_data from ``MuEl``. 
So we will have three distributions to look at:

- MET with inverted MET cut, MuEl, with ttbar_data instead of ttbar MC MuEl -> perfect normalization!
- MET with inverted MET cut, MuMu, with ttbar_data instead of ttbar MC MuMu -> normalization off
- MET with inverted MET cut, ElEl, with ttbar_data instead of ttbar MC ElEl -> normalization off!

This is done with the script ``getHighMETttbarFromData.py``, and the output is a root file, same as ``MuonEG*.root`` but with MET with inverted MET cut modified as described above, called "dataMuEl_minus_SingleTop_inHighMET.root".

3- Copy this file to the folder in factories_ZA that you're using to make plots, and copy the name of the file in plotIt_ZA/ttbar_MCFiles.yml instead of the ttbar MC used. Make plots in the BTAG case and look only at the three distributions listed in 2). Make sure the normalizations are actually what you were expecting.
To get the correct normalization factors for MuMu and ElEl, get the yields of the MET with inverted MET cut for MuMu and ElEl. It has to be that:
- ``MuMu cat.:  data = DY + SINGLETOP + OTHERBKGS + k_mumu*TTBAR_DATA  -->  k_mumu = (DATA - DY - SINGLETOP - OTHERBKGS) / TTBAR_DATA``
- ``ElEl cat.:  data = DY + SINGLETOP + OTHERBKGS + k_elel*TTBAR_DATA  -->  k_elel = (DATA - DY - SINGLETOP - OTHERBKGS) / TTBAR_DATA``

N.B. Right now these numbers are computed by hand, I count on having a script to do that.

4- Once you have k_mumu and k_elel, you can apply them to the ttbar_data in the various distributions (e.g. mbb, mllbb, ...). This is done with the script "getTTbarFromData.py". The output root file is called "ttbar_from_data_final.root" and contains the ttbar estimated from data.
Again, copy this file to the folder in factories_ZA that you're using to make plots, and copy the name of the file in plotIt_ZA/ttbar_MCFiles.yml, commenting out the file copied before. Make plots!

5- After you get you ttbar estimated from data and with the right normalization, compare it to ttbar MC in the (m_bb, m_llbb) to make sure you have enough statistics to cover the plane. Should the statistics of ttbar from data be poorer than the one taken from MC, then don't go with a data-driven estimation.
The script to compare the stats is "checkStats.py" and produces the folder "checkStats" in which it stores a root file called "compareStatsTTbarMC_vs_Data.root", containing the histos to compare the stats.
