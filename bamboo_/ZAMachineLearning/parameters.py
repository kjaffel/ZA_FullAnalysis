#######################################################################################
    # Defines the parameters that users might need to change
    # Must be included manually in each script
    
#######################################################################################
import glob
import json
import os, sys, os.path
import multiprocessing
import collections

from tensorflow.keras.losses import binary_crossentropy, mean_squared_error, logcosh, categorical_crossentropy
from tensorflow.keras.optimizers import RMSprop, Adam, Nadam, SGD            
from tensorflow.keras.activations import relu, elu, selu, softmax, tanh, sigmoid, softmax
from tensorflow.keras.regularizers import l1,l2 

from ZAMachineLearning import get_options
opt = get_options()

##################################  Path variables ####################################

#samples_path = '/home/ucl/cp3/kjaffel/scratch/ZAFullAnalysis/2016Results/skimmedTree/ver5/'
#samples_path = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/nanov7/skimmedTree/ver0/'
#samples_path = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/nanov7/skimmedTree/ver1/'
#samples_path_ul2016 = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov8/ul2016__ver2/'
#samples_path_ul2016 = '/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov8/ul2016__ver3/'
samples_path = {'2016' :'/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/skims_nanov8/ul2016__ver5/results',
                '2017' :'',
                '2018' :'', }

main_path = os.path.abspath(os.path.dirname(__file__))
#path_out = os.path.abspath(f'/home/ucl/cp3/kjaffel/scratch/ul__results/{opt.outputs}')
path_out  = os.path.abspath('/home/ucl/cp3/kjaffel/scratch/ul__results/test__34')
if not os.path.isdir(path_out):
    os.makedirs(path_out)
print ( ' sbatch_dir :', main_path)
print ( ' path_out   :', path_out)
path_model = os.path.join(path_out,'model')

##############################  Datasets proportion   #################################
# Total must be 1 #
#######################################################################################
training_ratio = 0.7    # Training set sent to keras (contains training + evaluation)
evaluation_ratio = 0.1  # evaluation set set sent to autom8
output_ratio = 0.2      # Output set for plotting later
assert training_ratio + evaluation_ratio + output_ratio == 1 # Will only be taken into account for the masks generation, ignored after

############################### Slurm parameters ######################################

#==============================================
# For GPU #
#==============================================
#partition = 'cp3-gpu'  # Def, cp3 or cp3-gpu
#QOS = 'cp3-gpu' # cp3 or normal
#time = '5-00:00:00' # days-hh:mm:ss
#mem = '60000' # ram in MB
#tasks = '20' # Number of threads(as a string)

#==============================================
# For CPU #
#==============================================
partition = 'cp3'  # Def, cp3 or cp3-gpu
QOS = 'cp3' # cp3 or normal
time = '0-08:00:00' # days-hh:mm:ss
mem = '6900' # ram in MB
tasks = '1' # Number of threads(as a string) (not parallel training for classic mode)

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
xsec_json = os.path.join(main_path,'data/Summer20UL{era}_xsec.json')
event_weight_sum_json = os.path.join(main_path,'data/Summer20UL{era}_event_weight_sum.json')

# Training resume #
resume_model = ''

# Output #
output_batch_size = 512
split_name = 'tag' # 'sample' or 'tag' : criterion for output file splitting

##############################  Evaluation criterion   ################################
#######################################################################################

eval_criterion = "eval_error" # either val_loss or eval_error
    
##############################  Model callbacks ################################
#######################################################################################
# Early stopping to stop learning after some criterion 
early_stopping_params = {'monitor'   : 'val_loss',             # Value to monitor
                         'min_delta' : 0.,                     # Minimum delta to declare an improvement
                         'patience'  : 50,                     # How much time to wait for an improvement
                         'verbose'   : 1,                      # Verbosity level
                         'restore_best_weights': False,
                         'mode'      : 'min'           }       # Mode : 'auto', 'min', 'max'

# Reduce LR on plateau : if no improvement for some time, will reduce lr by a certain factor
reduceLR_params = {'monitor'    : 'val_loss',   # Value to monitor
                   'factor'     : 0.5,          # Multiplicative factor by which to multiply LR
                   'min_lr'     : 1e-5,         # Minnimum value for LR
                   'min_delta'  : 0.0001,       # Minimum delta to declare an improvement
                   'patience'   : 10,           # How much time to wait for an improvement
                   'cooldown'   : 5,            # How many epochs before starting again to monitor
                   'verbose'    : 1,            # Verbosity level
                   'mode'      : 'min'}         # Mode : 'auto', 'min', 'max'

#################################  Scan dictionary   ##################################
# /!\ Lists must always contain something (even if 0, in a list !), otherwise 0 hyperparameters #
#######################################################################################
# Classification #
p = { 
    'epochs' : [2],   
    'batch_size' : [1000], 
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
            'l1_pdgId@op_pdgid',
            '$era@op_era',
            'bb_M',
            'llbb_M',
            'bb_M_squared',
            'llbb_M_squared',
            'bb_M_x_llbb_M',
            '$mA',
            '$mH',
#           'nB_AK4bJets',
#           'nB_AK8bJets',
#           'l1_charge@op_charge',
#           'l2_pdgId@op_pdgid',
#           'l2_charge@op_charge',
         ]
# Output branches #
outputs = [
            '$DY',
            '$TT',
            '$ZA',
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

operations = [inp.split('@')[1] if '@' in inp else None  for inp  in  inputs]
check_op   = [(o is not None)*1 for o in operations]

if check_op != sorted(check_op,reverse=True):
    raise RuntimeError('Onehot inputs need to be at the beginning of the inputs list')

mask_op = [len(inp.split('@'))==2 for inp  in  inputs]
inputs  = [inp.split('@')[0] for inp  in  inputs]

TTree   = []
if opt.resolved:
    TTree.extend([f"LepPlusJetsSel_{opt.process}_resolved_{channel.lower()}_deepcsvm" for channel in channels])
if opt.boosted:
    TTree.extend([f"LepPlusJetsSel_{opt.process}_boosted_{channel.lower()}_deepcsvm" for channel in channels])

samples_dict_run2UL = collections.defaultdict(dict)
for era in eras:
    samples_dict_run2UL[era] = {}
    for node in nodes:
        samples_dict_run2UL[era][f"combined_{node}_nodes"] = []
        for i_f, fn in enumerate(glob.glob(os.path.join(samples_path[era],'*.root'))):
            smp   = fn.split('/')[-1]
            subnodes = {"DY": ["DYJetsToLL"], "TT": ["TT", "ST"], "ZA":["HToZATo2L2B"]} 
            if '__skeleton__' in smp:
                continue
            for node_ in subnodes[node]:
                if smp.startswith(node_):
                    samples_dict_run2UL[era][f"combined_{node}_nodes"].append(f"{smp}")

sampleList_full = [f"{samples_path[era]}/{smp}" for era in eras for node in nodes for smp in samples_dict_run2UL[era][f"combined_{node}_nodes"]]
print( " List of samples : ", samples_dict_run2UL )
print( " TTree :         : ", TTree )  


xsec_dict             = dict()
event_weight_sum_dict = dict()
for era in eras:
    if os.path.isfile(xsec_json.format(era=era)): 
        with open(xsec_json.format(era=era),'r') as handle:
            xsec_dict[era] = json.load(handle)
    else:
        xsec_dict[era] = {}
    if os.path.isfile( event_weight_sum_json.format(era=era)):
        with open(event_weight_sum_json.format(era=era),'r') as handle:
            event_weight_sum_dict[era] = json.load(handle)
    else:
        event_weight_sum_dict[era] = {}

################################  dtype operation ##############################
# root_numpy does not like some operators very much #
#######################################################################################
def make_dtype(list_names): 
    list_dtype = [(name.replace('.','_').replace('(','').replace(')','').replace('-','_minus_').replace('*','_times_')) for name in list_names]
    return list_dtype
