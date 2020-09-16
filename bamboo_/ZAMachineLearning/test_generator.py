import os
os.environ["CUDA_VISIBLE_DEVICES"]="0,1"
import sys
import numpy as np
import logging
import pickle

import keras
from keras import utils
from keras.layers import Layer, Input, Dense, Concatenate, BatchNormalization, LeakyReLU, Lambda, Dropout
from keras.losses import binary_crossentropy, mean_squared_error
from keras.optimizers import RMSprop, Adam, Nadam, SGD
from keras.activations import relu, elu, selu, softmax, tanh
from keras.models import Model, model_from_json, load_model
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.regularizers import l1,l2
from keras.utils import multi_gpu_model
import keras.backend as K
import tensorflow as tf
from tensorflow.python.util import deprecation
deprecation._PRINT_DEPRECATION_WARNINGS = False
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # 0 = all, 1 = no info, 2 = no warning, 3 = no error


from data_generator import DataGenerator
from preprocessing import PreprocessLayer
import parameters

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')


#from tensorflow.python.client import device_lib
#print("GPU ", K.tensorflow_backend._get_available_gpus())
#print(device_lib.list_local_devices())

with open('/home/ucl/cp3/fbury/MoMEMtaNeuralNet/scaler_gen_ME.pkl', 'rb') as handle: # Import scaler that was created before
    scaler = pickle.load(handle)
IN = Input(shape=(len(parameters.inputs),),name='IN')
L0 = PreprocessLayer(batch_size=100000,mean=scaler.mean_,std=scaler.scale_,name='Preprocess')(IN)
L1 = Dense(500,activation=relu)(L0)
B1 = BatchNormalization()(L1)
L2 = Dense(500,activation=relu)(B1)
B2 = BatchNormalization()(L2)
L3 = Dense(500,activation=relu)(B2)
B3 = BatchNormalization()(L3)
L4 = Dense(500,activation=relu)(B3)
B4 = BatchNormalization()(L4)
L5 = Dense(500,activation=relu)(B4)
B5 = BatchNormalization()(L5)
OUT = Dense(1,activation=selu,name='OUT')(B5)

preprocess = Model(inputs=[IN],outputs=[L0])

#with tf.device('/cpu:0'):
model = Model(inputs=[IN], outputs=[OUT])
#model = multi_gpu_model(model,gpus=2)
#model = multi_gpu_model(model,gpus=[0,1])
utils.print_summary(model=model) #used to print model

print('Tensorflow ',tf.__file__)
print('Keras ',keras.__file__)

model.compile(optimizer=Adam(lr=0.001),
              loss={'OUT':mean_squared_error},
              metrics=['accuracy','mse'])

#training_generator = DataGenerator(path = '/home/ucl/cp3/fbury/scratch/MoMEMta_output/ME_TTBar_generator_mix/path3',
#                                   inputs = parameters.inputs,
#                                   outputs = parameters.outputs,
#                                   batch_size = 50000)
#
#validation_generator = DataGenerator(path = '/home/ucl/cp3/fbury/scratch/MoMEMta_output/ME_TTBar_generator_mix/path0',
#                                   inputs = parameters.inputs,
#                                   outputs = parameters.outputs,
#                                   batch_size = 50000)
preprocess_generator = DataGenerator(path = '/home/ucl/cp3/fbury/scratch/MoMEMta_output/ME_TTBar_generator_mix/path3',
                                   inputs = parameters.inputs,
                                   outputs = parameters.outputs,
                                   batch_size = 10000)


out = preprocess.predict_generator(preprocess_generator, 
                  workers=0, 
                  steps=10,
                  use_multiprocessing=False, 
                  verbose=1)
#print (out)
a = np.zeros(out.shape[1])
count_tot =0
count_rep =0
for i in range(out.shape[0]):
    #print (out[i,:])
    #print (out[i,:]-a)
    count_tot+=1
    if np.sum(out[i,:]-a)==0:
        count_rep+=1
    a = out[i,:]
print (np.mean(out))
print (np.std(out))
print (count_tot,count_rep)

print("GPU ", K.tensorflow_backend._get_available_gpus())
sys.exit()
logging.info('before fit')
model.fit_generator(generator = training_generator,
                    epochs = 1,
                    verbose = 1,
                    validation_data = validation_generator,
                    workers = 20,
                    use_multiprocessing = True,
                    max_queue_size = 1000,
                    steps_per_epoch = 1,
                    )
logging.info('after fit')


