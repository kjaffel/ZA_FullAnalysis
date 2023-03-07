import os
import shutil

import pandas as pd
import numpy as np
import tensorflow.keras as keras

from ..utils.best_model import best_model, activate_model

# NOTE: this has some overlap with code in evaluate.py
# and needs to be cleaned up.
# TODO: needs to also deploy the hyperparameter configuration
# and some kind of summary of the experiment and then finally
# pack everything into a zip file

class CustomLayer(keras.layers.Layer):
    def __init__(self, units=32, **kwargs):
        super(CustomLayer, self).__init__(**kwargs)
        self.units = units

    def build(self, input_shape):
        self.w = self.add_weight(
                    shape=(input_shape[-1], self.units),
                    initializer="random_normal",
                    trainable=True,
                )
        self.b = self.add_weight(
                    shape=(self.units,), initializer="random_normal", trainable=True
                )

    def call(self, inputs):
        return tf.matmul(inputs, self.w) + self.b

    def get_config(self):
        config = super(CustomLayer, self).get_config()
        config.update({"units": self.units})
        return config



class Deploy:
    '''Functionality for deploying a model to a filename'''
    def __init__(self, scan_object, model_name, custom_objects, metric='val_acc', asc=False, path_model=''):

        os.mkdir(os.path.join(path_model,model_name))
        
        self.custom_objects = custom_objects
        self.scan_object    = scan_object
        self.path           = os.path.join(path_model,model_name,model_name)
        self.model_name     = model_name
        self.metric         = metric
        self.asc            = asc
        self.data           = scan_object.data
        self.best_model     = best_model(scan_object, metric, asc)
        self.model          = activate_model(scan_object, self.best_model)
        # runtime
        self.save_model_as()
        self.save_details()
        self.save_data()
        self.save_results()
        self.save_params()
        self.save_readme()
        self.package()

    def save_model_as(self):
        '''Model Saver
        WHAT: Saves a trained model so it can be loaded later
        for predictions by predictor().
        '''
        #Retrieve the config
        config = self.model.get_config()

        # At loading time, register the custom objects with a `custom_object_scope`:
        with keras.utils.custom_object_scope(self.custom_objects):
            new_model = keras.Model.from_config(config)

        model_json = self.model.to_json()
        with open(self.path + "_model.json", "w") as json_file:
            json_file.write(model_json)

        self.model.save_weights(self.path + "_model.h5")
        self.model.save(self.path + "_model_full.h5")
        print("Deploy package" + " " + self.model_name + " " + "have been saved.")

    def save_details(self):
        self.scan_object.details.to_csv(self.path + '_details.txt')

    def save_data(self):
        x = pd.DataFrame(self.scan_object.x[:100])
        y = pd.DataFrame(self.scan_object.y[:100])
        x.to_csv(self.path + '_x.csv', header=None, index=None)
        y.to_csv(self.path + '_y.csv', header=None, index=None)

    def save_results(self):
        self.scan_object.data.to_csv(self.path + '_results.csv')

    def save_params(self):
        np.save(self.path + '_params', self.scan_object.params)

    def save_readme(self):
        txt = 'To activate the assets in the Talos deploy package: \n\n   from talos.commands.restore import Restore \n   a = Restore(\'path_to_asset\')\n\nNow you will have an object similar to the Scan object, which can be used with other Talos commands as you would be able to with the Scan object'
        text_file = open(os.path.dirname(self.path) + '/README.txt', "w")
        text_file.write(txt)
        text_file.close()

    def package(self):
        shutil.make_archive(os.path.dirname(self.path), 'zip', os.path.dirname(self.path))
        shutil.rmtree(os.path.dirname(self.path))
