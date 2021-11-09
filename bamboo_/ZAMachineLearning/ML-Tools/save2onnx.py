import os, os.path, sys
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import tensorflow as tf
from tensorflow.keras.models import model_from_json

sys.path.append(os.path.abspath('..'))
import Operations
from preprocessing import PreprocessLayer

print("TensorFlow version is :"+tf.__version__)

#path_to_json = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/model/best_model/best_model_model.json" 
#path_to_h5   = "/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/model/best_model/best_model_model.h5"
path_to_json = "../ul__results/work__1/model/all_combined_dict_343_isbest_model/all_combined_dict_343_model.json"
path_to_h5   = "../ul__results/work__1/model/all_combined_dict_343_isbest_model/all_combined_dict_343_model.h5"

with open(path_to_json,"r") as f:
    loaded_model_json = f.read()

kerasmodel = model_from_json(loaded_model_json, custom_objects = {name:getattr(Operations,name) for name in dir(Operations) if name.startswith('op')})
kerasmodel.load_weights(path_to_h5)
try: 
    import keras2onnx
    print("keras2onnx version is :"+keras2onnx.__version__)
    #kerasmodel = load_model("/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/model/best_model/best_model_model.h5")
    onnx_model = keras2onnx.convert_keras(kerasmodel, kerasmodel.name)
    keras2onnx.save_model(onnx_model, os.path.join("keras_tf_onnx_models", "prob_model.onnx"))
except Exception as ex:
    logger.exception("ERROR while saving to onnx:{}".format(ex))

import onnx
onnx_model = onnx.load('./keras_tf_onnx_models/prob_model.onnx')
output =[node.name for node in onnx_model.graph.output]

input_all = [node.name for node in onnx_model.graph.input]
input_initializer =  [node.name for node in onnx_model.graph.initializer]
net_feed_input = list(set(input_all)  - set(input_initializer))
print('Inputs: ', net_feed_input)
print('Outputs: ', output)
