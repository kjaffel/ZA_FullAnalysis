ROC_multiclass:
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
    - red
  weight : event_weight
  title : Multi classification
  cut : '1'
  selector :
    'TT' : 'TT'
    'DY' : 'DY'
    'ZA' : 'ZA'
