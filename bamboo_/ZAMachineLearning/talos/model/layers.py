from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from .shapes import shapes
from ..utils.exceptions import TalosTypeError, TalosParamsError

class hidden_layers:
    def __init__(self,params,last_neuron,batch_normalization=False):
        self.batch_normalization = batch_normalization

        try:
            self.kernel_initializer = params['kernel_initializer']
        except KeyError:
            self.kernel_initializer = 'glorot_uniform'

        try:
            self.kernel_regularizer = params['kernel_regularizer']
        except KeyError:
            self.kernel_regularizer = None

        try:
            self.bias_initializer = params['bias_initializer']
        except KeyError:
            self.bias_initializer = 'zeros'

        try:
            self.bias_regularizer = params['bias_regularizer']
        except KeyError:
            self.bias_regularizer = None

        try:
            self.use_bias = params['use_bias']
        except KeyError:
            self.use_bias = True

        try:
            self.activity_regularizer = params['activity_regularizer']
        except KeyError:
            self.activity_regularizer = None

        try:
            self.kernel_constraint = params['kernel_constraint']
        except KeyError:
            self.kernel_constraint = None

        try:
            self.bias_constraint = params['bias_constraint']
        except KeyError:
            self.bias_constraint = None

        if isinstance(params['activation'], str) is True:
            raise TalosTypeError('When hidden_layers are used, activation needs to be an object and not string')

        try:
            params['shapes']
            self.layer_neurons = shapes(params, last_neuron)
        except KeyError:
            self.layer_neurons = [params['first_neuron']] * params['hidden_layers']

        if 'activation' in params:
            self.activation = params['activation']
        else:
            raise TalosParamsError('activation key is needed in the parameters')

        if 'hidden_layers' in params:
            self.hidden_layers = params['hidden_layers']
        else:
            raise TalosParamsError('hidden_layers key is needed in the parameters')

        if 'dropout' in params:
            self.dropout= params['dropout']
        else:
            raise TalosParamsError('dropout key is needed in the parameters')

    def sequential(self,model):

        '''HIDDEN LAYER Generator

        NOTE: 'first_neuron', 'dropout', and 'hidden_layers' need
        to be present in the params dictionary.

        Hidden layer generation for the cases where number
        of layers is used as a variable in the optimization process.
        Handles things in a way where any number of layers can be tried
        with matching hyperparameters.'''


        for i in range(self.hidden_layers):
            if self.batch_normalization:
                model.add(BatchNormalization())
            model.add(Dense(self.layer_neurons[i],
                            activation=self.activation,
                            use_bias=self.use_bias,
                            kernel_initializer=self.kernel_initializer,
                            kernel_regularizer=self.kernel_regularizer,
                            bias_initializer=self.bias_initializer,
                            bias_regularizer=self.bias_regularizer,
                            activity_regularizer=self.activity_regularizer,
                            kernel_constraint=self.kernel_constraint,
                            bias_constraint=self.bias_constraint))
            model.add(Dropout(self.dropout))
        if self.batch_normalization:
            model.add(BatchNormalization())


    def API(self,layer):

        '''HIDDEN LAYER Generator

        NOTE: 'first_neuron', 'dropout', and 'hidden_layers' need
        to be present in the params dictionary.

        Hidden layer generation for the cases where number
        of layers is used as a variable in the optimization process.
        Handles things in a way where any number of layers can be tried
        with matching hyperparameters.'''
        for i in range(self.hidden_layers):
            if self.batch_normalization:
                layer = BatchNormalization()(layer)
            layer = Dense(self.layer_neurons[i],
                            activation=self.activation,
                            use_bias=self.use_bias,
                            kernel_initializer=self.kernel_initializer,
                            kernel_regularizer=self.kernel_regularizer,
                            bias_initializer=self.bias_initializer,
                            bias_regularizer=self.bias_regularizer,
                            activity_regularizer=self.activity_regularizer,
                            kernel_constraint=self.kernel_constraint,
                            bias_constraint=self.bias_constraint)(layer)
            layer = Dropout(self.dropout)(layer)
        if self.batch_normalization:
            layer = BatchNormalization()(layer)

        return layer
