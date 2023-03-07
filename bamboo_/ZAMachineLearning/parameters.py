#######################################################################################
    # Defines the parameters that users might need to change
    # Must be included manually in each script
    
#######################################################################################
import glob
import json
import pickle
import os, sys, os.path
import multiprocessing
import collections

from tensorflow.keras.losses import binary_crossentropy, mean_squared_error, logcosh, categorical_crossentropy
from tensorflow.keras.optimizers import RMSprop, Adam, Nadam, SGD            
from tensorflow.keras.activations import relu, elu, selu, softmax, tanh, sigmoid, softmax
from tensorflow.keras.regularizers import l1,l2 

from ZAMachineLearning import get_options
opt = get_options()

def pogEraFormat(era):
    return "_UL"+era.replace("20", "")

##################################  Path variables ####################################
#######################################################################################
#samples_path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/skimmedTree/ver5/'
#samples_path = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/nanov7/skimmedTree/ver0/'
#samples_path = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/nanov7/skimmedTree/ver1/'
#samples_path_ul2016 = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov8/ul2016__ver2/'
#samples_path_ul2016 = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov8/ul2016__ver3/'
#samples_path = {'2016' :'/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov8/ul2016__ver5/results',
#samples_path = {'2016' :'/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov8/ul2016__ver6/results',
#samples_path = {'2016' :'/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov9/ul2016__ver1/results',
#samples_path = {'2016' :'/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov9/ul_fullrun2___nanov9__ver1/results',
#samples_path = {'2016' :'/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov9/ul_fullrun2___nanov9__ver2/results',
#samples_path = {'2016' :'/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov9/ul_fullrun2___nanov9__ver4/results',

samples_path = {
    '2016' :'/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov9/ul_fullrun2___nanov9__ver6/results',
    '2017' :'/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov9/ul_fullrun2___nanov9__ver6/results',
    '2018' :'/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov9/ul_fullrun2___nanov9__ver6/results'
    }

main_path  = os.path.abspath(os.path.dirname(__file__))
path_out   = os.path.abspath(f'/home/ucl/cp3/kjaffel/scratch/{opt.outputs}')

if not os.path.isdir(path_out):
    os.makedirs(path_out)

print ( ' sbatch_dir :', main_path)
print ( ' path_out   :', path_out)

path_model = os.path.join(path_out,'model')

##############################  Datasets proportion   #################################
#######################################################################################
# total must be 1 
training_ratio   = 0.7    # Training set sent to keras (contains training + evaluation)
evaluation_ratio = 0.1    # evaluation set set sent to autom8
output_ratio     = 0.2    # Output set for plotting later
# Will only be taken into account for the masks generation, ignored after
assert training_ratio + evaluation_ratio + output_ratio == 1 

# Cross-validation #
N_models = 5                        # Number of models to train
N_train  = 3                        # Number of slices on which to train
N_eval   = 1                        # Number of slices on which to evaluate the model
N_apply  = 1                        # Number of slices on which the model will be applied for uses in analysis
N_slices = N_train+N_eval+N_apply
splitbranch = 'event'               # Will split the training based on "event % N_slices" 

if N_slices % N_models != 0: # will not work otherwise
    raise RuntimeError(f"N_slices [{N_slices}] % N_models [{N_models}] should be == 0")
if N_apply != N_slices/N_models: # Otherwise the same slice can be applied on several networks
    raise RuntimeError("You have asked {N_models} models that should be applied {N_apply} times,\n"
                       "the number of slices should be {N_models*N_apply} but is {N_train}+{N_eval}+{N_apply}\n")

############################### Slurm parameters ######################################
#######################################################################################

#==============================================
# For GPU #
## scontrol show nodes --> to see what the nodes really offer.
#==============================================
if opt.GPU:
    partition  = 'gpu'        # Def, cp3 or cp3-gpu
    QOS        = 'normal'     # cp3 or normal
    time       = '0-6:00:00'  # days-hh:mm:ss
    mem        = '4000'       # ram in MB
    tasks      = '20'         # Number of threads(as a string)
    gpus       = 1            # TeslaV100 or 1 
    cpus       = 8
#==============================================
# For CPU #
#==============================================
else:
    partition = 'cp3'         # Def, cp3 or cp3-gpu
    QOS       = 'cp3'         # cp3 or normal
    time      = '2-59:00:00'  # days-hh:mm:ss
    mem       = '30G'         # ram in GB
    tasks     = '1'           # Number of threads(as a string) (not parallel training for classic mode)
    
######################################  Names  ########################################
                        # Model name important only for scans 
#######################################################################################

model  = 'NeuralNetModel'           # Classic mode
#model = 'NeuralNetGeneratorModel'  # Generator mode

# scaler and mask names #
suffix = 'ZA_catagories' 

scaler_path = os.path.join(path_out, f'scaler_{suffix}_run2Ulegacy.pkl')
path_mask   = path_out  #mask_name -> 'mask_{suffix}_{node}.npy'

# Data cache #                                                                                       
train_cache = os.path.join(path_out,f'train_cache_{suffix}_run2Ulegacy.pkl')
test_cache  = os.path.join(path_out,f'test_cache_{suffix}_run2Ulegacy.pkl')

# Meta config info #
xsec_json = os.path.join("{json_path}",'data/ulegacy{era}_xsec.json')
event_weight_sum_json = os.path.join("{json_path}",'data/ulegacy{era}_event_weight_sum.json')

# Training resume #
resume_model = ''

# Output #
output_batch_size = 512
split_name = 'tag' # 'sample' or 'tag' : criterion for output file splitting

##############################  Evaluation criterion   ################################
#######################################################################################

eval_criterion = "val_loss" # either val_loss or eval_error
    
#####################################  Model callbacks ################################
#######################################################################################
# Early stopping to stop learning after some criterion 
early_stopping_params = {'monitor'   : 'val_loss',             # Value to monitor
                         'min_delta' : 0.,                     # Minimum delta to declare an improvement
                         'patience'  : 50,                     # How much time to wait for an improvement
                         'verbose'   : 1,                      # Verbosity level
                         'restore_best_weights': True,
                         'mode'      : 'min'           }       # Mode : 'auto', 'min', 'max'

# Reduce LR on plateau : if no improvement for some time, will reduce lr by a certain factor
reduceLR_params = {'monitor'    : 'val_loss',   # Value to monitor
                   'factor'     : 0.5,          # Multiplicative factor by which to multiply LR
                   'min_lr'     : 1e-5,         # Minnimum value for LR
                   'min_delta'  : 0.0001,       # Minimum delta to declare an improvement
                   'patience'   : 10,           # How much time to wait for an improvement
                   'cooldown'   : 5,            # How many epochs before starting again to monitor
                   'verbose'    : 1,            # Verbosity level
                   'mode'       : 'min'}         # Mode : 'auto', 'min', 'max'

#################################  Scan dictionary   ##################################
            #  !!! Lists must always contain something (even if 0, in a list !), 
            # otherwise 0 hyperparameters #
#######################################################################################
# Classification #
p = { 
    'epochs' : [200],   
    'batch_size' : [5000],  #1000 
    'lr' : [0.01], 
    'hidden_layers' : [2,3,4,5,6], 
    'first_neuron' : [16,32,64,128,256],
    'dropout' : [0,0.25,0.5],
    'l2' : [0,0.1,0.2],
    'activation' : [selu,relu],
    'output_activation' : [softmax],
    'optimizer' : [Adam],  
    'loss_function' : [categorical_crossentropy],
#    'n_particles' : [10],
}
p2 = { 
    'epochs' : [100],   
    'batch_size' : [512], 
    'lr' : [0.001], 
    'hidden_layers' : [3], 
    'first_neuron' : [64],
    'dropout' : [0],
    'l2' : [0],
    'activation' : [relu],
    'output_activation' : [softmax],
    'optimizer' : [Adam],  
    'loss_function' : [categorical_crossentropy] 
}

repetition = 1 # How many times each hyperparameter has to be used 

###################################  Variables   ######################################
#######################################################################################
cut = None
crossvalidation = False
tree_name  = 'Events'
weights    = 'total_weight'
lumidict   = {'2016':36645.514633552,'2017':41529.152060112,'2018':59740.565201546}

eras       = ['2016', '2017', '2018']
categories = ["resolved","boosted"]
channels   = ['ElEl','MuMu']
nodes      = ['DY', 'TT', 'ZA'] #'ggH', 'bbH']
# Input branches (combinations possible just as in ROOT #
inputs = [
            #'l1_charge@op_charge',
            #'l2_pdgId@op_pdgid',
            #'l2_charge@op_charge',
            #'region@op_region',
            #'process@op_process',
            'l1_pdgId@op_pdgid',
            '$era@op_era',
            'bb_M',
            'llbb_M',
            'bb_M_squared',
            'llbb_M_squared',
            'bb_M_x_llbb_M',
            '$mA',
            '$mH',
            'isResolved',
            'isBoosted',
            'isggH',
            'isbbH'
            #'nB_AK4bJets',
            #'nB_AK8bJets',
         ]
# Output branches #
outputs = [
            '$DY',
            '$TT',
            '$ZA'
            #'$ggH',
            #'$bbH',
          ] 
# Other variables you might want to save in the tree #
other_variables = [
            'event',
            'luminosityBlock',
            'run',
            'MC_weight',
        ]

# Input plots options #
node_colors = {
        'DY'     : '#600070',
        'TT'     : '#89cff0',
        'ZA'     : '#ce7e00',
    }


#######################################################################################
#######################################################################################
operations = [inp.split('@')[1] if '@' in inp else None  for inp  in  inputs]
check_op   = [(o is not None)*1 for o in operations]

if check_op != sorted(check_op,reverse=True):
    raise RuntimeError('Onehot inputs need to be at the beginning of the inputs list')

mask_op = [len(inp.split('@'))==2 for inp  in  inputs]
inputs  = [inp.split('@')[0] for inp  in  inputs]

#######################################################################################
#######################################################################################
TTree   = []
process_nodes = []
for proc in opt.process:
    if opt.resolved:
        TTree.extend([f"LepPlusJetsSel_{proc}_resolved_{channel.lower()}_deepflavourm" for channel in channels])
    if opt.boosted:
        TTree.extend([f"LepPlusJetsSel_{proc}_boosted_{channel.lower()}_deepcsvm" for channel in channels])
    if 'ggH' in opt.process: process_nodes = ["GluGluToHToZATo2L2B"]
    if 'bbH' in opt.process: process_nodes += ["HToZATo2L2B"]

#######################################################################################
#######################################################################################
if not opt.report:
    # allow to save whenever ZA args are passed
    with open(f'{path_out}/list_catagories.ob', 'wb') as fp:
        pickle.dump(TTree, fp)
else:
    # avoid to overwrite not in scan/submit model ==> will turn this obj to an empty array!
    with open (f'{opt.outputs}/list_catagories.ob', 'rb') as fp:
        TTree = pickle.load(fp)
print ( ' TTree      :', TTree )  

#######################################################################################
#######################################################################################
subnodes = {"DY": ["DYJetsToLL"], "TT": ["TT", "ST"], "ZA":process_nodes} 
samples_dict_run2UL = collections.defaultdict(dict)
for era in eras:
    samples_dict_run2UL[era] = {}
    for node in nodes:
        samples_dict_run2UL[era][f"combined_{node}_nodes"] = []
        for i_f, fn in enumerate(glob.glob(os.path.join(samples_path[era],'*.root'))):
            smp   = fn.split('/')[-1]

            if '__skeleton__' in smp: continue
            if 'tb_20p00_TuneCP5_bbH4F_13TeV_amcatnlo_pythia8' in smp:continue
            if not pogEraFormat(era) in smp: continue 
            # this will prevent from mixing samples when the path given to the skims is the same for the 3 yeras
            
            for node_ in subnodes[node]:
                if not smp.startswith(node_): continue
                samples_dict_run2UL[era][f"combined_{node}_nodes"].append(smp)

sampleList_full = [f"{samples_path[era]}/{smp}" for era in eras for node in nodes for smp in samples_dict_run2UL[era][f"combined_{node}_nodes"]]
#print( " List of samples : ", samples_dict_run2UL )

#######################################################################################
#######################################################################################
xsec_dict             = dict()
event_weight_sum_dict = dict()
for era in eras:
    json_path = samples_path[era]
    if json_path =='':
        continue
    xscjson   = xsec_json.format(json_path=json_path, era=era)
    sumWjson  = event_weight_sum_json.format(json_path=json_path, era=era)
    
    if not os.path.exists(xscjson):
        raise RuntimeError(f'File not found: {xscjson}')
    with open(xscjson,'r') as handle:
        xsec_dict[era] = json.load(handle)
    
    if not os.path.exists(sumWjson):
        raise RuntimeError(f'File not found: {sumWjson}')
    with open(sumWjson,'r') as handle:
        event_weight_sum_dict[era] = json.load(handle)

#print (xsec_dict)
#print(event_weight_sum_dict)
#######################################  dtype operation ##############################
                # root_numpy does not like some operators very much #
#######################################################################################
def make_dtype(list_names): 
    list_dtype = [(name.replace('.','_').replace('(','').replace(')','').replace('-','_minus_').replace('*','_times_')) for name in list_names]
    return list_dtype
