ROC_multi:
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
    - P(DY)
    - P(TT)
    - P(ZA)
  colors:
    - '#cc7a16'
    - '#174704'
    - '#ccbf45'
  weight : ''
  title : Multiclass_learning
  cut : ''
  selector :
    'DY'   : 'DY'
    'TT'   : 'TT'
    'ZA'  : 'ZA'
