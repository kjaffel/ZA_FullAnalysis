import sys
import numpy as np
import tensorflow as tf

class PreprocessLayer(tf.keras.layers.Layer):
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
            raise ValueError('mean must be a list or numpy array')
        if isinstance(std,list):
            self.s = np.asarray(std)
        elif isinstance(std,np.ndarray):
            self.s = std
        else:
            raise ValueError('std must be a list or numpy array')

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
                                          initializer=tf.constant_initializer(np.tile(self.m,(self.b,1))),
                                          trainable=False)
                self.std = self.add_weight(name='std', 
                                          shape=(self.b,input_shape[1]),
                                          initializer=tf.constant_initializer(np.tile(self.s,(self.b,1))),
                                          trainable=False)
        else:
            sys.exit("Tensforflow version "+tf.__version__+" unknown for preprocessing layer")
        super(PreprocessLayer, self).build(input_shape)  # Be sure to call this at the end
    def call(self, x):
        # Due to remainder at the end of epoch, input_shape[0]<=batch_size
        # Need to slice the mean and std tensor so that they have the same shape as x
        mean = self.mean[:tf.shape(x)[0],:]
        std = self.std[:tf.shape(x)[0],:]
        return (x-mean)/(std+tf.keras.backend.epsilon())
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
