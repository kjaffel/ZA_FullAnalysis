ROC_mH_250_mA_100:
  tree: tree
  classes:
    - DY
    - TT
    - ZA
  prob_branches:
    - output_DY
    - output_TT
    - output_ZA
  labels:
    - P(DY | x,$\theta$)
    - P($t\bar{t}$ | x,$\theta$)
    - P($H\rightarrow ZA$ | x,$\theta$)
  colors:
    - navy
    - darkred
    - green
  weight : event_weight
  title : Mass points $M_{H}=250 \ GeV$ and $M_{A}=100 \ GeV$
  cut : 'mH==250 & mA==100'
  selector :
    'TT' : 'TT'
    'DY' : 'DY'
    'ZA' : 'ZA'
