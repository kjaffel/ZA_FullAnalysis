import tensorflow as tf

class OperationBase(tf.keras.layers.Layer):
    def __init__(self,**kwargs):
        super(OperationBase,self).__init__(kwargs)
    def call(self,x):
        return self.operation(x)
    def operation(self,x):
        raise NotImplementedError
    def compute_output_shape(self,input_shape):
        input_shape[1] = self.onehot_dim
        return input_shape
    def get_config(self):
        config = super(OperationBase, self).get_config()
        return config
    @classmethod
    def from_config(cls, config):
        return cls(**config)
    @property
    def onehot_dim(self):
        raise NotImplementedError

class op_pdgid(OperationBase):
    @tf.function
    def operation(self,x):
        x = tf.cast(tf.abs(x) > 11 , "int32") 
        x = tf.one_hot(tf.cast(tf.abs(x) > 11 , "int32"),2)
        return tf.reshape(x,(tf.shape(x)[0],2))
    @property
    def onehot_dim(self):
        return 2

class op_charge(OperationBase):
    @tf.function
    def operation(self,x):
        x = tf.cast(tf.abs(x) > 0, "int32")
        x = tf.one_hot(tf.cast(x > 0 , "int32"),2)
        return tf.reshape(x,(tf.shape(x)[0],2))
    @property
    def onehot_dim(self):
        return 2

class op_era(OperationBase):
    @tf.function
    def operation(self,x):
        x = tf.math.maximum(x,2016.)
        x = tf.math.minimum(x,2018.)
        x = tf.one_hot(tf.cast(x - 2016 , "int32"),3)
        return tf.reshape(x,(tf.shape(x)[0],3))
    @property
    def onehot_dim(self):
        return 3

class op_resolved_jpacat(OperationBase):
    @tf.function
    def operation(self,x):
        x = tf.math.maximum(x,1.)
        x = tf.math.minimum(x,7.)
        x = tf.one_hot(tf.cast(x - 1, "int32"),7) 
        return tf.reshape(x,(tf.shape(x)[0],7))
    @property
    def onehot_dim(self):
        return 7

class op_boosted_jpacat(OperationBase):
    @tf.function
    def operation(self,x):
        x = tf.math.maximum(x,1.)
        x = tf.math.minimum(x,3.)
        x = tf.one_hot(tf.cast(x - 1, "int32"),3)
        return tf.reshape(x,(tf.shape(x)[0],3))
    @property
    def onehot_dim(self):
        return 3
