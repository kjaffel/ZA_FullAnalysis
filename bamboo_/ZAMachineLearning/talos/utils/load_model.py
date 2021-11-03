import tensorflow as tf
import tensorflow.keras.models 


def load_model(saved_model,method='json',custom_objects=None):

    '''Load a Model from local disk

    Takes as input .json and .h5 file with model
    and weights and returns a model that can be then
    used for predictions.

    saved_model :: name of the saved model without
    suffix (e.g. 'iris_model' and not 'iris_model.json')

    method :: what way to load the model ('json' or 'h5')

    '''
    if method == 'json':  # Load archi in json + weight in h5
        json_file = open(saved_model + ".json", 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = tf.keras.models.model_from_json(loaded_model_json,custom_objects=custom_objects)
        model.load_weights(saved_model + '.h5')
    elif method == 'h5':  # Load the whole model (archi + weights) in h5 file
        model = tf.keras.models.load_model(saved_model + '_full.h5',custom_objects=custom_objects) 

    return model
