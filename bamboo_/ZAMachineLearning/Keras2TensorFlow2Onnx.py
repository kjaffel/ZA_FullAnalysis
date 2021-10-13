import sys
import os
import json
import argparse

from keras.models import model_from_json
from keras import backend as K
from tensorflow.python.framework import graph_util
from tensorflow.python.framework import graph_io

import tensorflow as tf
from preprocessing import PreprocessLayer

def KerasToTensorflowModel(path_to_json= None, path_to_h5= None, prefix= None, name=None, numout=None, outdir=None):
    # Make output dire #
    os.makedirs(outdir,exist_ok=True)

    # Import model and weights #
    with open(path_to_json,"r") as f:
        keras_model_json = f.read()
    keras_model = model_from_json(keras_model_json, custom_objects =  {'PreprocessLayer': PreprocessLayer})
    keras_model.load_weights(path_to_h5)
   
    try: 
        import keras2onnx
        #kerasmodel = load_model("/home/ucl/cp3/kjaffel/bamboodev/ZA_FullAnalysis/bamboo_/ZAMachineLearning/model/best_model/best_model_model.h5")
        onnx_model = keras2onnx.convert_keras(keras_model, keras_model.name)
        keras2onnx.save_model(onnx_model, os.path.join("outdir", numout+".onnx"))
    except Exception as ex:
        logger.exception(f"ERROR while saving to onnx:{ex}")
    
    onnxmodel = onnx.load(os.path.join("outdir", numout+".onnx"))
    output =[node.name for node in onnxmodel.graph.output]

    input_all = [node.name for node in onnxmodel.graph.input]
    input_initializer =  [node.name for node in onnx_model.graph.initializer]
    net_feed_input = list(set(input_all)  - set(input_initializer))

    print('ONNX Inputs: ', net_feed_input)
    print('ONNX Outputs:', output)

    # Alias the outputs in the model - this sometimes makes them easier to access in TF
    numout = numout+".pb"
    K.set_learning_phase(0)
    pred = [None]*numout
    pred_node_names = [None]*numout
    for i in range(numout):
        pred_node_names[i] = prefix+'_'+str(i)
        pred[i] = tf.identity(keras_model.output[i], name=pred_node_names[i])
    print('Output nodes names are: ', pred_node_names)

    sess = K.get_session()
    
    # Write the graph in human readable
    f = 'graph_def_for_reference.pb.ascii'
    tf.train.write_graph(sess.graph.as_graph_def(), outdir, f, as_text=True)
    print('Saved the graph definition in ascii format at: ', os.path.join(outdir, f))

    # Write the graph in binary .pb file
    constant_graph = graph_util.convert_variables_to_constants(sess, sess.graph.as_graph_def(), pred_node_names)
    graph_io.write_graph(constant_graph, outdir, name, as_text=False)
    print('Saved the constant graph (ready for inference) at: ', os.path.join(outdir, name))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json',required=True, type=str,help='REQUIRED: The json model file you wish to convert to .pb')
    parser.add_argument('--h5',required=True, type=str,help='REQUIRED: The h5 model model weights file you wish to convert to .pb **do not use _full.h5**')
    parser.add_argument('--numout', type=int, required=True, help='REQUIRED: The number of outputs in the model.')
    parser.add_argument('--outdir','-o', dest='outdir', required=False, default='./keras_tf_onnx_models', help='The directory to place the output files - default("./keras_tf_onnx_models")')
    parser.add_argument('--prefix','-p', dest='prefix', required=False, default='k2tf', help='The prefix for the output aliasing - default("k2tf")')
    parser.add_argument('--name', required=False, default='best_model', help='The name of the resulting output graph - default("best_model.pb and best_model.onnx") (MUST NOT forget)')
    args = parser.parse_args()

    KerasToTensorflowModel(path_to_json     = args.json,
                           path_to_h5       = args.h5,
                           prefix           = args.prefix,
                           name             = args.name,
                           numout           = args.numout,
                           outdir           = args.outdir)
