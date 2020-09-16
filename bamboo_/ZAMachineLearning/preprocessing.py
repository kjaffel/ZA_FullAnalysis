import sys
import numpy as np

from keras.layers import Layer
import keras.backend as K
import tensorflow as tf

#################################################################################################
# PreprocessLayer #
#################################################################################################
class PreprocessLayer(Layer):
    """ 
    Defines a layer that applies the preprocessing from a scaler
    Needed because lambda layers are too fragile to be saved in a model
    Also because they are defined as weights, they are saved in the h5 file
    Careful ! When using the model (ie with predict()), the batch size used should be lower than the one set here (at least 32)
    """
    def __init__(self, mean, std, batch_size=32, **kwargs):
        self.b = max(32,batch_size)
        # Since we slice will the tensors later, we need the size of the tensors to be big enough
        # The 32 is the default value when using predict(), if we set it lower we will not be able to slice the tensor
        if isinstance(mean,list):
            self.m = np.asarray(mean)
        elif isinstance(mean,np.ndarray):
            self.m = mean
        else:
            sys.exit('mean must be a list or numpy array')
        if isinstance(std,list):
            self.s = np.asarray(std)
        elif isinstance(std,np.ndarray):
            self.s = std
        else:
            sys.exit('std must be a list or numpy array')

        super(PreprocessLayer, self).__init__(**kwargs)
    def build(self, input_shape):
        if tf.__version__.startswith('1.5'):
            self.mean = self.add_weight(name='mean', 
                                        shape=(self.b,input_shape[1]),
                                        initializer=tf.constant_initializer(np.tile(self.m,(self.b,1)),verify_shape=True),
                                        trainable=False)
            self.std = self.add_weight(name='std', 
                                        shape=(self.b,input_shape[1]),
                                        initializer=tf.constant_initializer(np.tile(self.s,(self.b,1))),
                                        trainable=False)

        elif tf.__version__.startswith('2.'):
            with tf.init_scope():
                self.mean = self.add_weight(name='mean', 
                                          shape=(self.b,input_shape[1]),
                                          #initializer=tf.constant_initializer(np.tile(self.m,(self.b,1)),verify_shape=True),
                                          initializer=tf.constant_initializer(np.tile(self.m,(self.b,1))),
                                          trainable=False)
                self.std = self.add_weight(name='std', 
                                          shape=(self.b,input_shape[1]),
                                          #initializer=tf.constant_initializer(np.tile(self.s,(self.b,1)),verify_shape=True),
                                          initializer=tf.constant_initializer(np.tile(self.s,(self.b,1))),
                                          trainable=False)
        else:
            sys.exit("Tensforflow version "+tf.__version__+" unknown for preprocessing layer")
        super(PreprocessLayer, self).build(input_shape)  # Be sure to call this at the end
    def call(self, x):
        # Due to remainder at the end of epoch, input_shape[0]<=batch_size
        # Need to slice the mean and std tensor so that they have the same shape as x
        mean = self.mean[:K.shape(x)[0],:]
        std = self.std[:K.shape(x)[0],:]
        return (x-mean)/(std+K.epsilon())
    def compute_output_shape(self, input_shape):
        # Since add and sub keep the same shape, return input_shape
        return (input_shape[0],input_shape[1])
    def get_config(self): 
        # Needed so that the parameters are not asked again when loading the model
        config = super(PreprocessLayer, self).get_config()
        if isinstance(self.m,np.ndarray): # Cannot use numpy arrays in the json file
            config['mean'] = self.m.tolist() 
        else:
            config['mean'] = self.m 
        if isinstance(self.s,np.ndarray): # Cannot use numpy arrays in the json file
            config['std'] = self.s.tolist() 
        else:
            config['std'] = self.std 
        config['batch_size'] = self.b 
        # This batch size value is the maximum one can use when using the model later
        return config

#################################################################################################
# MakeArrayMultiple #
#################################################################################################
def MakeArrayMultiple(list_array,batch_size,repeat=False,crop=False):
    """
    Given that PreprocessLayer requires that the input array size is a multiple of the batch_size
    This function extends or crops the array to make it fit
    crop = true -> removes the last elements of the array, otherwise will repeat some entries
    repeat = true -> elements are taken randomly to fill the remained, if not only zeros
    """
    # If only a numpy array, put it in a list #
    if isinstance(list_array,np.ndarray):
        list_array = [list_array]
    # Check that all arrays in the list have the same length #
    N = list_array[0].shape[0]
    for arr in list_array:
        assert N == arr.shape[0]
    # Crop if requested # 
    if crop:
        cropped_size = int(N/batch_size)*batch_size
        crop_list = []
        for arr in list_array:
            crop_list.append(arr[:cropped_size])
        return crop_list 

    # If not cropping -> Replacement #
    #Get the number of missing entries #
    missing_entries = (int(N/batch_size)+1)*batch_size-N
    list_new_entries = []
    # Make the remainder of the array #
    if repeat:
        idx_new_entries = np.random.randint(N,size=(missing_entries)) # so that same entries are used for all arrays
        for arr in list_array:
            list_new_entries.append(arr[idx_new_entries])
    else:
        for arr in list_array:
            if len(arr.shape)==2: # 2d array
                list_new_entries.append(np.zeros((missing_entries,arr.shape[1])))
            elif len(arr.shape)==1: # vector
                list_new_entries.append(np.zeros((missing_entries)))
    list_concat = []
    for arr,new in zip(list_array,list_new_entries): 
        new_arr = np.concatenate((arr,new),axis=0)
        list_concat.append(new_arr)
    if len(list_concat)>1:
        return list_concat    # The list will be decoupled in the output
    else:
        return list_concat[0] # if only one item, return the array

#################################################################################################
# GenDictExtract #
#################################################################################################
def GenDictExtract(key, var):
    """ 
    Given a certain key, will try to find it in a nested dict+list
    Returns a generator
    """
    if hasattr(var,'items'):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result


