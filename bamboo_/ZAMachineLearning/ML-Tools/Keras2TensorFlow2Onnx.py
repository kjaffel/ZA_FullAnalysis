import sys
import os
import json
import glob 
import argparse
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import keras2onnx
#import efficientnet
#from keras.models import model_from_json
from tensorflow.keras.models import model_from_json

import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.python.framework import graph_util
from tensorflow.python.framework import graph_io

sys.path.append(os.path.abspath('..'))
import Operations
from preprocessing import PreprocessLayer

print("TensorFlow version is "+tf.__version__)
print("keras2onnx version is "+keras2onnx.__version__)

def KerasToTensorflowModel(path_to_all=None, job= None, path_to_json= None, path_to_h5= None, prefix= None, name=None, numout=None, outdir=None):

    if path_to_all is not None:
        outdir = os.path.join(path_to_all,'keras_tf_onnx_models/')
        
        path_to_json =  glob.glob(os.path.join(path_to_all, 'model/*', '*.json'))[0]
        path_to_h5   =  glob.glob(os.path.join(path_to_all, 'model/*', '*_model.h5'))[0]
    
    os.makedirs(outdir,exist_ok=True)
    print( path_to_json, path_to_h5, outdir)
    print( {name:getattr(Operations,name) for name in dir(Operations) if name.startswith('op')})
    
    suffix = path_to_json.split('/')[-1].replace('.json', '')
    
    K.clear_session() 
    # Import model and weights #
    with open(path_to_json,"r") as f:
        keras_model_json = f.read()
    
    #keras_model = model_from_json(keras_model_json, custom_objects =  {'PreprocessLayer': PreprocessLayer})
    keras_model  = model_from_json(keras_model_json, custom_objects={name:getattr(Operations,name) for name in dir(Operations) if name.startswith('op')})
    
    #keras_model_h5 = tf.keras.models.load_model( path_to_h5)
    keras_model.load_weights(path_to_h5)
    
    if job =='k2onnx':
        try: 
            print( os.path.join(outdir, suffix+".onnx") )
            onnx_model  = keras2onnx.convert_keras(keras_model, keras_model.name)
            keras2onnx.save_model(onnx_model, os.path.join(outdir, suffix+".onnx"))
            
            #onnx_model  = keras2onnx.convert_keras(keras_model_, keras_model_.name)
            #keras2onnx_ = open(s.path.join(outdir, suffix+".onnx"), "wb")
            #keras2onnx_.write(onnx_model.SerializeToString())
            #keras2onnx_.close()
        except Exception as ex:
            logger.exception(f"ERROR while saving to onnx:{ex}")
        
        import onnx 
        onnxmodel = onnx.load(os.path.join(outdir, suffix+".onnx"))
        output    = [node.name for node in onnxmodel.graph.output]
    
        input_all = [node.name for node in onnxmodel.graph.input]
        input_initializer =  [node.name for node in onnx_model.graph.initializer]
        net_feed_input = list(set(input_all)  - set(input_initializer))
    
        print('ONNX Inputs :', net_feed_input)
        print('ONNX Outputs:', output)
    
    else:
        # Alias the outputs in the model - this sometimes makes them easier to access in TF
        #K.set_learning_phase(0)
        #pred = [None]*numout
        #pred_node_names = [None]*numout
        #for i in range(numout):
        #    pred_node_names[i] = prefix+'_'+ suffix +'_'+str(i)
        #    pred[i] = tf.identity(keras_model.output[i], name=pred_node_names[i])
        #print('Output nodes names are: ', pred_node_names)
    
        txtfile = os.path.join(outdir,suffix+'_inputs.txt')
        with open(txtfile,"w") as f:
            for layer in keras_model.layers:
                if 'InputLayer' in  str(type(layer)):
                    f.write("{:50} -> {}\n".format(layer.name,str(layer.input_shape)))
        print ("Saved input txt file as {}".format(txtfile))
        
        from tensorflow.python.keras.saving import saving_utils
        from tensorflow.python.eager.def_function import Function
        from tensorflow.python.eager.function import ConcreteFunction

        assert isinstance(keras_model, tf.keras.Model)
        learning_phase_orig = tf.keras.backend.learning_phase()
        tf.keras.backend.set_learning_phase(False)
        model_func = saving_utils.trace_model_call(keras_model)
        if model_func.function_spec.arg_names and not model_func.input_signature:
            raise ValueError("when model is a keras model callable accepting arguments, its "
                            "input signature must be frozen by building the model")
        model = model_func.get_concrete_function()
        tf.keras.backend.set_learning_phase(learning_phase_orig)
        
        # convert variables to constants
        assert isinstance(model, ConcreteFunction)

        from tensorflow.python.framework import convert_to_constants
        model = convert_to_constants.convert_variables_to_constants_v2(model)
        graph = model.graph
        
        #sess = K.get_session()
        # Write the graph in human readable
        #f = 'graph_def_for_reference.pb.ascii'
        #tf.train.write_graph(sess.graph.as_graph_def(), outdir, f, as_text=True)
        #print('Saved the graph definition in ascii format at: ', os.path.join(outdir, f))
    
        # Write the graph in binary .pb file
        #constant_graph = graph_util.convert_variables_to_constants(sess, sess.graph.as_graph_def(), pred_node_names)
        graph_io.write_graph(graph, outdir, suffix+".pb", as_text=False)
        graph_io.write_graph(graph, outdir, suffix+".pb.txt", as_text=True)
        print('Saved the constant graph (ready for inference) at: ', os.path.join(outdir, suffix+".pb"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', required=True, type=str, help='path where I an get the model/*_isbest_model/*.json && *.h5')
    parser.add_argument('--outdir','-o', dest='outdir', required=False, default='./keras_tf_onnx_models', help='The directory to place the output files - default("./keras_tf_onnx_models")')
    parser.add_argument('--job', required=False, type=str, choices=['k2tf', 'k2onnx'], help='What do you want: Keras -> TF or Keras -> ONNX')
    
    parser.add_argument('--json',required=False, type=str,help='The json model file you wish to convert to .pb')
    parser.add_argument('--h5',required=False, type=str,help='The h5 model model weights file you wish to convert to .pb **do not use _full.h5**')
    parser.add_argument('--numout', type=int, required=False, default=3, help='The number of outputs in the model. default [DY, TT, ZA ] 3 nodes output')
    parser.add_argument('--prefix',dest='prefix', required=False, default='k2tf', help='The prefix for the output aliasing - default("k2tf")')
    parser.add_argument('--name', required=False, default='best_model', help='The name of the resulting output graph - default("best_model.pb and best_model.onnx") (MUST NOT forget)')
    args = parser.parse_args()

    if args.path is None and args.json is None and args.h5 is None:
        print(' sorry this is not gonna work , either provid --json and --h5 or --path/ to model/*_isbest_model ')

    KerasToTensorflowModel(path_to_all      = args.path, 
                           job              = args.job,
                           path_to_json     = args.json,
                           path_to_h5       = args.h5,
                           prefix           = args.prefix,
                           name             = args.name,
                           numout           = args.numout,
                           outdir           = args.outdir)
