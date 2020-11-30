ROC_template:
  tree: tree
  classes:
    - A
    - B
    - C
  prob_branches:
    - ExpressionA
    - ExpressionB
    - ExpressionC
  labels:
    - Label_A
    - Label_B
    - Label_C
  colors:
    - navy
    - green
    - darkred
  weight : weight_branch
  title : a_title
  cut : a_cut or ''
  selector :
    - 'str_in_file' : A
    - 'str_in_file' : B
    - 'str_in_file': C

