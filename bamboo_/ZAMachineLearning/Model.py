import os
import re
import sys
import json
import shutil
import pickle
import yaml
import string
import logging
import random
import csv
import itertools

from collections import defaultdict 
from tensorflow.keras import utils
from tensorflow.keras.layers import Layer, Input, Dense, Concatenate, BatchNormalization, LeakyReLU, Lambda, Dropout
from tensorflow.keras.losses import binary_crossentropy, mean_squared_error
from tensorflow.keras.optimizers import RMSprop, Adam, Nadam, SGD
from tensorflow.keras.activations import relu, elu, selu, softmax, tanh
from tensorflow.keras.models import Model, model_from_json, load_model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, TensorBoard
from tensorflow.keras.regularizers import l1,l2
from tensorflow.keras.layers.experimental import preprocessing
from talos.model.layers import hidden_layers

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # removes annoying warning

import Operations
import parameters
from data_generator import DataGenerator

import IPython
tf_version = tf.__version__.split('.')
assert tf_version[0] == '2'

class LossHistory(tf.keras.callbacks.Callback):
    """ Records the history of the training per epoch and per batch """
    def on_train_begin(self, logs={}):
        self.epochs  = defaultdict(list) 
        self.batches = defaultdict(list) 
        self.pre_batch = 0

    def on_batch_end(self, batch, logs={}):
        self.batches['batch'].append(batch+self.pre_batch)
        for key,val in logs.items():
            self.batches[key].append(val)
        self.batches['lr'].append(tf.keras.backend.eval(self.model.optimizer.lr))

    def on_epoch_end(self, epoch, logs={}):
        self.epochs['epoch'].append(epoch)
        for key,val in logs.items():
            self.epochs[key].append(val)
        self.epochs['lr'].append(tf.keras.backend.eval(self.model.optimizer.lr))
        self.pre_batch = self.batches['batch'][-1] 

def PlotHistory(history,params):
    """ Takes history from Keras training and makes loss plots (batch and epoch) and learning rate plots """
    #----- Figure -----#
    variables = sorted([key for key in history.epochs.keys() if 'val' not in key and 'val_'+key in history.epochs.keys()])
    variables += ["lr"]
    N = len(variables)
    fig, ax = plt.subplots(N,2,figsize=(12,N*2),sharex='col')
    plt.subplots_adjust(left    = 0.1,
                        right   = 0.6,
                        top     = 0.9,
                        bottom  = 0.1,
                        hspace  = 0.5,
                        wspace  = 0.4)
    
    #----- Batch Plots -----#
    for i,var in enumerate(variables):
        ax[i,0].plot(history.batches['batch'],history.batches[var],'k')
        ax[i,0].set_title(var)
        ax[i,0].set_xlabel('Batch')
        
    #----- Epoch Plots -----#
    for i,var in enumerate(variables):
        ax[i,1].plot(history.epochs['epoch'],history.epochs[var],'b')
        if 'val_'+var in history.epochs.keys():
            ax_twin = ax[i,1].twinx()
            ax_twin.plot(history.epochs['epoch'],history.epochs['val_'+var],'g')
            ax[i,1].set_ylabel("Training",color='b')
            ax[i,1].tick_params(axis='y', labelcolor='b')
            ax_twin.set_ylabel("Validation",color='g')
            ax_twin.tick_params(axis='y', labelcolor='g')
        ax[i,1].set_title(var)
        ax[i,1].set_xlabel('Epoch')

    #----- Print parameters -----#
    paramStr = "Parameters\n"
    for paramName in sorted(list(params.keys())):
        line = "- {} : ".format(paramName)
        if isinstance(params[paramName],(int,float,str)):
            value = str(params[paramName])
        else:
            value = params[paramName].__name__
        line += "{}\n".format(value)
        if len(line)>25:
            line = "{}:\n    {}".format(*line.split(':'))
        paramStr += line

    plt.gcf().text(0.7, 0.5, paramStr, fontsize=14)

    # Save #
    rand_hash = ''.join(random.choice(string.ascii_uppercase) for _ in range(10)) # avoids overwritting
    png_name = 'Loss_%s.png'%rand_hash
    fig.savefig(png_name)
    logging.info('Curves saved as %s'%png_name)

#################################################################################################
# NeuralNetModel#
#################################################################################################
def NeuralNetModel(x_train,y_train,x_val,y_val,params):
    """
    Keras model for the Neural Network, used to scan the hyperparameter space by Talos
    Uses the data provided as inputs
    """
    # Split y = [target,weight], Talos does not leave room for the weight so had to be included in one of the arrays
    w_train = y_train[:,-1]
    w_val   = y_val[:,-1]
    y_train = y_train[:,:-1]
    y_val   = y_val[:,:-1]

    # Scaler #
    with open(parameters.scaler_path, 'rb') as handle: # Import scaler that was created before
        scaler = pickle.load(handle)

    # Design network #
    # Left branch : classic inputs -> Preprocess -> onehot
    inputs_numeric = []
    means          = []
    variances      = []
    inputs_all     = []
    encoded_all    = []
    for idx in range(x_train.shape[1]):
        inpName = parameters.inputs[idx].replace('$','')
        input_layer = tf.keras.Input(shape=(1,), name=inpName)
        # Categorical inputs #
        if parameters.mask_op[idx]:
            operation = getattr(Operations,parameters.operations[idx])()
            encoded_all.append(operation(input_layer))
        # Numerical inputs #
        else:
            inputs_numeric.append(input_layer)
            means.append(scaler.mean_[idx])
            variances.append(scaler.var_[idx])
        inputs_all.append(input_layer)

    # Concatenate all numerical inputs #
    if int(tf_version[1]) < 4:
        normalizer = preprocessing.Normalization(name='Normalization')
        x_dummy = np.ones((10,len(means)))
        # Needs a dummy to call the adapt method before setting the weights
        normalizer.adapt(x_dummy)
        normalizer.set_weights([np.array(means),np.array(variances)])
    else:
        normalizer = preprocessing.Normalization(mean=means,variance=variances,name='Normalization')
    encoded_all.append(normalizer(tf.keras.layers.concatenate(inputs_numeric,name='Numerics')))

    if len(encoded_all) > 1:
        all_features = tf.keras.layers.concatenate(encoded_all,axis=-1,name="Features")
    else:
        all_features = encoded_all[0]
    #=================================================================================
    L1 = Dense(params['first_neuron'],
               activation=params['activation'],
               kernel_regularizer=l2(params['l2']))(all_features)
    hidden = hidden_layers(params,1,batch_normalization=True).API(L1)
    out = Dense(y_train.shape[1],activation=params['output_activation'],name='out')(hidden)
    #=================================================================================
    # Check preprocessing #
    #=================================================================================
    preprocess = Model(inputs=inputs_numeric,outputs=encoded_all[-1])
    x_numeric = x_train[:,[not m for m in parameters.mask_op]]
    out_preprocess = preprocess.predict(np.hsplit(x_numeric,x_numeric.shape[1]),batch_size=params['batch_size'])
    mean_scale = np.mean(out_preprocess)
    std_scale  = np.std(out_preprocess)
    if abs(mean_scale)>0.01 or abs((std_scale-1)/std_scale)>0.1: # Check that scaling is correct to 1%
        logging.warning("Something is wrong with the preprocessing layer (mean = %0.6f, std = %0.6f), maybe you loaded an incorrect scaler"%(mean_scale,std_scale))

    #======================================================================
    # Tensorboard logs #
    #======================================================================
    #path_board = os.path.join(parameters.main_path,"TensorBoard")
    #suffix = 0
    #while(os.path.exists(os.path.join(path_board,"Run_"+str(suffix)))):
    #    suffix += 1
    #path_board = os.path.join(path_board,"Run_"+str(suffix))
    #os.makedirs(path_board)
    #logging.info("TensorBoard log dir is at %s"%path_board)

    #======================================================================
    # Callbacks #
    # Early stopping to stop learning if val_loss plateau for too long #
    #======================================================================
    early_stopping = EarlyStopping(**parameters.early_stopping_params)
    # Reduce learnign rate in case of plateau #
    reduceLR = ReduceLROnPlateau(**parameters.reduceLR_params)
    # Custom loss function plot for debugging #
    loss_history = LossHistory()
    # Tensorboard for checking live the loss curve #
    #board = TensorBoard(log_dir=path_board, 
    #                    histogram_freq=1, 
    #                    batch_size=params['batch_size'], 
    #                    write_graph=True, 
    #                    write_grads=True, 
    #                    write_images=True)
    Callback_list = [loss_history,early_stopping,reduceLR]

    # Compile #
    if 'resume' not in params:  # Normal learning 
        # Define model #
        model_inputs = [inputs_all]
        model = Model(inputs=model_inputs, outputs=[out])
        initial_epoch = 0
    else: # a model has to be imported and resumes training
        #custom_objects =  {'PreprocessLayer': PreprocessLayer,'OneHot': OneHot.OneHot}
        logging.info("Loaded model %s"%params['resume'])
        a = Restore(params['resume'],custom_objects=custom_objects,method='h5')
        model = a.model
        initial_epoch = params['initial_epoch']

    model.compile(optimizer=Adam(lr=params['lr']),
                  loss=params['loss_function'],
                  metrics=[tf.keras.metrics.CategoricalAccuracy(),
                           tf.keras.metrics.AUC(multi_label=True),
                           tf.keras.metrics.Precision(),
                           tf.keras.metrics.Recall()])
    model.summary()
    fit_inputs = np.hsplit(x_train,x_train.shape[1])
    fit_val    = (np.hsplit(x_val,x_val.shape[1]),y_val,w_val)
    
    # Fit #
    history = model.fit(x               = fit_inputs,
                        y               = y_train,
                        sample_weight   = w_train,
                        epochs          = params['epochs'],
                        batch_size      = params['batch_size'],
                        verbose         = 1,
                        validation_data = fit_val,
                        callbacks       = Callback_list)
    # Plot history #
    PlotHistory(loss_history,params)

    return history,model

#################################################################################################
# NeuralNetGeneratorModel#
#################################################################################################
def NeuralNetGeneratorModel(x_train,y_train,x_val,y_val,params):
    """
    Keras model for the Neural Network, used to scan the hyperparameter space by Talos
    Uses the generator rather than the input data (which are dummies)
    """
    # Scaler #
    with open(parameters.scaler_path, 'rb') as handle: # Import scaler that was created before
        scaler = pickle.load(handle)

    # Design network #

    # Left branch : classic inputs -> Preprocess -> onehot
    inputs_numeric = []
    means          = []
    variances      = []
    inputs_all     = []
    encoded_all    = []
    for idx in range(x_train.shape[1]):
        inpName = parameters.inputs[idx].replace('$','').replace(' ','').replace('_','')
        input_layer = tf.keras.Input(shape=(1,), name=inpName)
        # Categorical inputs #
        if parameters.mask_op[idx]:
            operation = getattr(Operations,parameters.operations[idx])()
            encoded_all.append(operation(input_layer))
        # Numerical inputs #
        else:
            inputs_numeric.append(input_layer)
            means.append(scaler.mean_[idx])
            variances.append(scaler.var_[idx])
        inputs_all.append(input_layer)

    # Concatenate all numerical inputs #
    if int(tf_version[1]) < 4:
        normalizer = preprocessing.Normalization(name='Normalization')
        x_dummy = np.ones((10,len(means)))
        # Needs a dummy to call the adapt method before setting the weights
        normalizer.adapt(x_dummy)
        normalizer.set_weights([np.array(means),np.array(variances)])
    else:
        normalizer = preprocessing.Normalization(mean=means,variance=variances,name='Normalization')
    encoded_all.append(normalizer(tf.keras.layers.concatenate(inputs_numeric,name='Numerics')))

    if len(encoded_all) > 1:
        all_features = tf.keras.layers.concatenate(encoded_all,axis=-1,name="Features")
    else:
        all_features = encoded_all[0]

    # Concatenation of left and right #
    L1 = Dense(params['first_neuron'],
               activation=params['activation'],
               kernel_regularizer=l2(params['l2']))(all_features)
    hidden = hidden_layers(params,1,batch_normalization=True).API(L1)
    out = Dense(y_train.shape[1],activation=params['output_activation'],name='out')(hidden)

    # Tensorboard logs #
#    path_board = os.path.join(parameters.main_path,"TensorBoard")
#    suffix = 0
#    while(os.path.exists(os.path.join(path_board,"Run_"+str(suffix)))):
#        suffix += 1
#    path_board = os.path.join(path_board,"Run_"+str(suffix))
#    os.makedirs(path_board)
#    logging.info("TensorBoard log dir is at %s"%path_board)

    # Callbacks #
    # Early stopping to stop learning if val_loss plateau for too long #
    early_stopping = EarlyStopping(**parameters.early_stopping_params)
    # Reduce learnign rate in case of plateau #
    reduceLR = ReduceLROnPlateau(**parameters.reduceLR_params)
    # Custom loss function plot for debugging #
    loss_history = LossHistory()
    # Tensorboard for checking live the loss curve #
#    board = TensorBoard(log_dir=path_board, 
#                        histogram_freq=1, 
#                        batch_size=params['batch_size'], 
#                        write_graph=True, 
#                        write_grads=True, 
#                        write_images=True)
#    Callback_list = [loss_history,early_stopping,reduceLR,board]
    Callback_list = [loss_history,early_stopping,reduceLR]

    # Compile #
    if 'resume' not in params:  # Normal learning 
        # Define model #
        model_inputs = [inputs_all]
        model = Model(inputs=model_inputs, outputs=[out])
        initial_epoch = 0
    else: # a model has to be imported and resumes training
        #custom_objects =  {'PreprocessLayer': PreprocessLayer,'OneHot': OneHot.OneHot}
        logging.info("Loaded model %s"%params['resume'])
        a = Restore(params['resume'],custom_objects=custom_objects,method='h5')
        model = a.model
        initial_epoch = params['initial_epoch']

    model.compile(optimizer=Adam(lr=params['lr']),
                  loss=params['loss_function'],
                  metrics=[tf.keras.metrics.CategoricalAccuracy(),
                           tf.keras.metrics.AUC(multi_label=True),
                           tf.keras.metrics.Precision(),
                           tf.keras.metrics.Recall()])
    model.summary()

    # Generator #
    training_generator   = DataGenerator( path       = parameters.config,
                                          inputs     = parameters.inputs,
                                          outputs    = parameters.outputs,
                                          cut        = parameters.cut,
                                          weight     = parameters.weight,
                                          batch_size = params['batch_size'],
                                          state_set  = 'training',
                                          model_idx  = params['model_idx'] if parameters.crossvalidation else None)
    
    validation_generator = DataGenerator( path       = parameters.config,
                                          inputs     = parameters.inputs,
                                          outputs    = parameters.outputs,
                                          cut        = parameters.cut,
                                          weight     = parameters.weight,
                                          batch_size = params['batch_size'],
                                          state_set  = 'validation',
                                          model_idx  = params['model_idx'] if parameters.crossvalidation else None)

    # Some verbose logging #
    logging.info("Will use %d workers"%parameters.workers)
    logging.warning("Tensorflow location "+ tf.__file__)
    if len(tf.config.experimental.list_physical_devices('XLA_GPU')) > 0:
        logging.info("GPU detected")
    #logging.warning(K.tensorflow_backend._get_available_gpus())
    # Fit #
    history = model.fit_generator(generator             = training_generator,   # Training data from generator instance
                                  validation_data       = validation_generator, # Validation data from generator instance
                                  epochs                = params['epochs'],     # Number of epochs
                                  verbose               = 1,
                                  max_queue_size        = parameters.workers*2,   # Length of batch queue
                                  callbacks             = Callback_list,        # Callbacks
                                  initial_epoch         = initial_epoch,        # In case of resumed training will be different from 0
                                  workers               = parameters.workers,   # Number of threads for batch generation (0 : all in same)
                                  shuffle               = True,                 # Shuffle order at each epoch
                                  use_multiprocessing   = True)                 # Needs to be turned on for queuing batches
    # Plot history #
    PlotHistory(loss_history)

    return history,model
