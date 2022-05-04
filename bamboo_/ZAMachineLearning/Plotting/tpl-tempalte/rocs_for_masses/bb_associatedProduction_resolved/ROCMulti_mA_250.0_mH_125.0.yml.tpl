ROC_mA_250.0_mH_125.0:
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
  title : ( $M_A$, $M_H$)= ( 250, 125) GeV
  cut : 'mA==250 & mH==125 & isbbH & isResolved'
  selector :
    'TT' : 'TT'
    'DY' : 'DY'
    'ZA' : 'ZA'
