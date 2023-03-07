import pandas as pd
import numpy as nmp
from IPython.display import display, HTML, display_html
import json
from tabulate import tabulate
import os, os.path   
base_dir="/nfs/user/kjaffel/www-eos-lxplus/hig-22-010/__ver8"

m = ["MH-500.0_MA-300.0", "MH-500.0_MA-250.0", "MH-300.0_MA-200.0","MH-510.0_MA-130.0", "MH-650.0_MA-50.0", "MH-800.0_MA-140.0",
     "MH-800.0_MA-200.0","MH-717.96_MA-577.65", "MH-516.94_MA-78.52","MH-379.0_MA-54.59", "MA-800.0_MH-140.0","MA-500.0_MH-250.0","MA-510.0_MH-130.0"]
#m = ["MH-500.0_MA-300.0"]

nb2test=pd.DataFrame([["nb2_impact_r"], ["nb2_pull-"], ["nb2_pullC"], ["nb2_pull+"]])
nb3test=pd.DataFrame([["nb3_impact_r"], ["nb3_pull-"], ["nb3_pullC"], ["nb3_pull+"]])
nb2Plus3test=pd.DataFrame([["Comb_impact_r"], ["Comb_pull-"], ["Comb_pullC"], ["Comb_pull+"]])
columns0 = pd.MultiIndex.from_frame(nb2test)
columns0_1 = pd.MultiIndex.from_frame(nb3test)
columns0_2 = pd.MultiIndex.from_frame(nb2Plus3test)

for dir in m: 
 dir_nameinImpactFile = dir.replace("-","_")
 print(dir_nameinImpactFile)
 for production in ["gg_fusion","bb_associatedProduction"]:
 #for production in ["bb_associatedProduction"]:
  for cat1 in ["resolved","boosted"]:
   for cat3 in ["OSSF_MuEl_dnn"]:
    for cat2 in ["nb2"]:
     nb2_arr_r = [] 
     nb2_arr_pullC = []
     nb2_neg_pull =[]
     nb2_pos_pull =[]
     nb2_arr_np = []
     if(os.path.isfile(base_dir+"/"+dir+"/"+production+"/"+cat2+"-"+cat1+"/impacts__HToZATo2L2B_"+production+"_"+cat2+"_"+cat1+"_"+cat3+"_"+dir_nameinImpactFile+"_realdataset.json")):   
      with open(base_dir+"/"+dir+"/"+production+"/"+cat2+"-"+cat1+"/impacts__HToZATo2L2B_"+production+"_"+cat2+"_"+cat1+"_"+cat3+"_"+dir_nameinImpactFile+"_realdataset.json") as f:
       data = json.load(f)
       for np in range(len(data['params'])):
        nb2_arr_r.append(data['params'][np]['impact_r'])
        nb2_neg_pull.append(data['params'][np]['fit'][0])
        nb2_pos_pull.append(data['params'][np]['fit'][2])
        nb2_arr_pullC.append(data['params'][np]['fit'][1])
        nb2_arr_np.append(str(data['params'][np]['name']))

     else:
      print(base_dir+"/"+dir+"/"+production+"/"+cat2+"-"+cat1+"/impacts__HToZATo2L2B_"+production+"_"+cat2+"_"+cat1+"_"+cat3+"_"+dir_nameinImpactFile+"_realdataset.json doesnt exist")

##### getting info for cat 14
    for cat2 in ["nb3"]: 
     nb3_arr_r = [] 
     nb3_arr_pullC = []
     nb3_neg_pull =[]
     nb3_pos_pull =[]
     nb3_arr_np = []
     if(os.path.isfile(base_dir+"/"+dir+"/"+production+"/"+cat2+"-"+cat1+"/impacts__HToZATo2L2B_"+production+"_"+cat2+"_"+cat1+"_"+cat3+"_"+dir_nameinImpactFile+"_realdataset.json")):   
      with open(base_dir+"/"+dir+"/"+production+"/"+cat2+"-"+cat1+"/impacts__HToZATo2L2B_"+production+"_"+cat2+"_"+cat1+"_"+cat3+"_"+dir_nameinImpactFile+"_realdataset.json") as f:
       data = json.load(f)
       for np in range(len(data['params'])):
        nb3_arr_r.append(data['params'][np]['impact_r'])
        nb3_neg_pull.append(data['params'][np]['fit'][0])
        nb3_pos_pull.append(data['params'][np]['fit'][2])
        nb3_arr_pullC.append(data['params'][np]['fit'][1])
        nb3_arr_np.append(str(data['params'][np]['name']))
     else:
      print(base_dir+"/"+dir+"/"+production+"/"+cat2+"-"+cat1+"/impacts__HToZATo2L2B_"+production+"_"+cat2+"_"+cat1+"_"+cat3+"_"+dir_nameinImpactFile+"_realdataset.json doesnt exist")

##### getting info for cat 16
    for cat2 in ["nb2PLusnb3"]: 
     nb2Plus3_arr_r = [] 
     nb2Plus3_arr_pullC = []
     nb2Plus3_neg_pull =[]
     nb2Plus3_pos_pull =[]
     nb2Plus3_arr_np = []
     if(os.path.isfile(base_dir+"/"+dir+"/"+production+"/"+cat2+"-"+cat1+"/impacts__HToZATo2L2B_"+production+"_"+cat2+"_"+cat1+"_"+cat3+"_"+dir_nameinImpactFile+"_realdataset.json")):   
      with open(base_dir+"/"+dir+"/"+production+"/"+cat2+"-"+cat1+"/impacts__HToZATo2L2B_"+production+"_"+cat2+"_"+cat1+"_"+cat3+"_"+dir_nameinImpactFile+"_realdataset.json") as f:
       data = json.load(f)
       for np in range(len(data['params'])):
        nb2Plus3_arr_r.append(data['params'][np]['impact_r'])
        nb2Plus3_neg_pull.append(data['params'][np]['fit'][0])
        nb2Plus3_pos_pull.append(data['params'][np]['fit'][2])
        nb2Plus3_arr_pullC.append(data['params'][np]['fit'][1])
        nb2Plus3_arr_np.append(str(data['params'][np]['name']))
     else:
      print(base_dir+"/"+dir+"/"+production+"/"+cat2+"-"+cat1+"/impacts__HToZATo2L2B_"+production+"_"+cat2+"_"+cat1+"_"+cat3+"_"+dir_nameinImpactFile+"_realdataset.json doesnt exist")  


    nb2_rows = list(zip(nb2_arr_np, nb2_arr_r, nb2_neg_pull, nb2_arr_pullC, nb2_pos_pull)) 
    nb3_rows = list(zip(nb3_arr_np, nb3_arr_r, nb3_neg_pull, nb3_arr_pullC, nb3_pos_pull)) 
    nb2Plus3_rows = list(zip(nb3_arr_np, nb2Plus3_arr_r, nb2Plus3_neg_pull, nb2Plus3_arr_pullC, nb2Plus3_pos_pull))
    nb2_rows.sort(key = lambda x:x[1],  reverse=True)
    nb2_rows = [list(x) for x in nb2_rows]
    nb3_rows.sort(key = lambda x:x[1],  reverse=True)
    nb3_rows = [list(x) for x in nb3_rows]
    nb2Plus3_rows.sort(key = lambda x:x[1],  reverse=True)
    nb2Plus3_rows = [list(x) for x in nb2Plus3_rows]
    
    #### to produce DF and sorting wrt their NP ####
    arr_new = [0]
    #Covert list2 to numpy array
    nb2_numpy= nmp.array(nb2_rows)
    nb3_numpy= nmp.array(nb3_rows)
    nb2Plus3_numpy= nmp.array(nb2Plus3_rows)
    #Extract the specific columns from rows according to arr_new
    #print(nb2_numpy)
    nb2np_list=[]
    nb3np_list=[]
    nb2Plus3np_list = []
    if(len(nb2_numpy)): 
        nb2_np = nb2_numpy[:,arr_new]
        nb2np_list = sum(nb2_np.tolist(),[])
    if(len(nb3_numpy)): 
        nb3_np = nb3_numpy[:,arr_new]
        nb3np_list = sum(nb3_np.tolist(),[])
    if(len(nb2Plus3_numpy)): 
        nb2Plus3_np = nb2Plus3_numpy[:,arr_new]
        nb2Plus3np_list = sum(nb2Plus3_np.tolist(),[])

    #print(np_list)
    for j in nb2_rows: 
        del j[0]
    for j in nb3_rows: 
        del j[0]
    for j in nb2Plus3_rows: 
        del j[0]
    nb2_test = pd.DataFrame()
    nb3_test = pd.DataFrame()
    nb2Plus3_test = pd.DataFrame()
    if(len(nb2_rows)):    
        nb2_test = pd.DataFrame(nb2_rows, columns=columns0, index=nb2np_list)
    if(len(nb3_rows)):
        nb3_test = pd.DataFrame(nb3_rows, columns=columns0_1, index=nb3np_list)
    if(len(nb2Plus3_rows)):    
        nb2Plus3_test = pd.DataFrame(nb2Plus3_rows, columns=columns0_2, index=nb2Plus3np_list)
    
    tog = nb2_test.join(nb3_test, how='outer')
    tog2 = tog.join(nb2Plus3_test, how='outer')
    #print(tog2)
    
    file_name = dir_nameinImpactFile+"_"+production+"_"+cat3+".xlsx"
    tog2.style.format("{:.4f}").to_excel(file_name)
    
 
