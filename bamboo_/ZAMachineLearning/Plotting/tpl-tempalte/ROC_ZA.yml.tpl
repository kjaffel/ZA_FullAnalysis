ROC_name:
  tree: tree
  variable: output 
  weight: event_weight 
  title: ROC curve 
  cut: '1'
  xlabel: Signal efficiency
  ylabel: Background efficiency
  selector:
    'Background' : 0
    'Signal' : 1
