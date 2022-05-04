ROC_mH_157.77_mA_30.0:
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
  title : ( $M_H$, $M_A$)= ( 157.77, 30) GeV
  cut : 'mH==157 & mA==30 & isggH & isBoosted'
  selector :
    'TT' : 'TT'
    'DY' : 'DY'
    'ZA' : 'ZA'
