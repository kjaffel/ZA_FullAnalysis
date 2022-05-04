import sys
import os
import json
import glob 
import argparse

import Utils as utils
logger = utils.MLlogger(__name__)

import tensorflow as tf
from tensorflow.keras.models import model_from_json
from tensorflow.keras import backend as K
from tensorflow.python.framework import graph_util
from tensorflow.python.framework import graph_io

sys.path.append(os.path.abspath('..'))
import Operations
from preprocessing import PreprocessLayer


def load_graph(frozen_graph_filename):
    with tf.io.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def)
    return graph

def analyze_inputs_outputs(graph):
    ops = graph.get_operations()
    outputs_set = set(ops)
    inputs = []
    for op in ops:
        if len(op.inputs) == 0 and op.type != 'Const':
            inputs.append(op)
        else:
            for input_tensor in op.inputs:
                if input_tensor.op in outputs_set:
                    outputs_set.remove(input_tensor.op)
    outputs = list(outputs_set)
    return (inputs, outputs)


def KerasToTensorflowModel(path_to_all=None, job= None, path_to_json= None, path_to_h5= None, prefix= None, name=None, outdir=None):

    if path_to_all is not None:
        outdir = os.path.join(path_to_all,'keras_tf_onnx_models/')
        
        path_to_json =  glob.glob(os.path.join(path_to_all, 'model/', '*_isbest_model/', '*_model.json'))[0]
        path_to_h5   =  glob.glob(os.path.join(path_to_all, 'model/', '*_isbest_model/', '*_model.h5'))[0]
    
    os.makedirs(outdir,exist_ok=True)
    print( path_to_json, path_to_h5, outdir)
    print( {name:getattr(Operations,name) for name in dir(Operations) if name.startswith('op')})
    
    suffix = path_to_json.split('/')[-1].replace('.json', '')
    
    K.clear_session() 
    # Import model and weights #
    with open(path_to_json,"r") as f:
        keras_model_json = f.read()
    
    keras_model  = model_from_json(keras_model_json, custom_objects={name:getattr(Operations,name) for name in dir(Operations) if name.startswith('op')})
    keras_model.load_weights(path_to_h5)
    
    if job =='k2onnx':
        try: 
            import keras2onnx
            logger.info("keras2onnx version is :"+keras2onnx.__version__)
            logger.info("TensorFlow version is :"+tf.__version__)
            if not (keras2onnx.__version__ =='2.3.0' and tf.__version__=='1.7.0'):
                logger.info("This may not work !\n"
                            "TensorFlow version : 2.3.0  and keras2onnx version :1.7.0 using LCG100 defnietly works, so try to degrade your version!\n"
                            "Simply in clean shell do:\n"
                               "\tcms_env\n"
                               "\tsource /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc10-opt/setup.sh\n"
                               "\tpython -m venv ~/bamboodev/bamboovenv100 ## only the 1st time!\n"
                               "\tsource ~/bamboodev/bamboovenv100/bin/activate\n")

            onnx_model  = keras2onnx.convert_keras(keras_model, keras_model.name)
            keras2onnx.save_model(onnx_model, os.path.join(outdir, suffix+".onnx"))
            
            #onnx_model  = keras2onnx.convert_keras(keras_model_h5, keras_model_.name)
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
        
        # Write the graph in binary .pb file
        graph_io.write_graph(graph, outdir, suffix+".pb", as_text=False)
        graph_io.write_graph(graph, outdir, suffix+".pb.txt", as_text=True)
        print('Saved the constant graph (ready for inference) at: ', os.path.join(outdir, suffix+".pb"))

        frozen_graph = load_graph( os.path.join(outdir, suffix+".pb"))
        in_, out = analyze_inputs_outputs( frozen_graph)
        print( 'Inputs:' , in_)
        print( 'Outputs:', out )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', required=True, type=str, help='path where I can get : model/*_isbest_model/*_model.json && *_model.h5')
    parser.add_argument('--outdir','-o', dest='outdir', required=False, default='./keras_tf_onnx_models', help='The directory to place the output files - default("./keras_tf_onnx_models")')
    parser.add_argument('--job', required=True, type=str, choices=['k2tf', 'k2onnx'], help='What do you want: Keras -> TF or Keras -> ONNX')
   
    # If needed you can still pass .json and .h5 files instead of the full path  with --path ! 
    parser.add_argument('--json',required=False, type=str,help='The json model file you wish to convert to .pb')
    parser.add_argument('--h5',required=False, type=str,help='The h5 model model weights file you wish to convert to .pb **do not use _full.h5**')
    parser.add_argument('--name', required=False, default='best_model', help='The name of the resulting output graph will be given ad {name}.pb for TF and {name}.onnx for ONNX- default("best_model.pb and best_model.onnx")')
    args = parser.parse_args()

    if args.path is None and args.json is None and args.h5 is None:
        print(' sorry this is not gonna work , either provid --json and --h5 or --path/ to model/*_isbest_model ')
   

    # http://alexlenail.me/NN-SVG/index.html
    KerasToTensorflowModel(path_to_all      = args.path, 
                           job              = args.job,
                           path_to_json     = args.json,
                           path_to_h5       = args.h5,
                           prefix           = 'k2TF' if args.job == 'k2tf' else 'k2onnx',
                           name             = args.name,
                           outdir           = args.outdir)
