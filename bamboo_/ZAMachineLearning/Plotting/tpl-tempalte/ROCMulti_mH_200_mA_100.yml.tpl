ROC_mH_200_mA_100:
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
    - purple
    - orange
    - blue
  weight : event_weight
  title : Mass points $M_{H}=200 \ GeV$ and $M_{A}=100 \ GeV$
  cut : 'mH==200 & mA==100 & isBoosted & isggH'
  selector :
    'TT' : 'TT'
    'DY' : 'DY'
    'ZA' : 'ZA'
