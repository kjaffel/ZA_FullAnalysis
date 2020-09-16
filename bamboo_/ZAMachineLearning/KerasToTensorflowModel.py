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

def KerasToTensorflowModel(path_to_json,path_to_h5,prefix,name,numout,outdir):
    # Make output dire #
    os.makedirs(outdir,exist_ok=True)

    # Import model and weights #
    with open(path_to_json,"r") as f:
        loaded_model_json = f.read()
    loaded_model = model_from_json(loaded_model_json, custom_objects =  {'PreprocessLayer': PreprocessLayer})
    loaded_model.load_weights(path_to_h5)
    
    # Alias the outputs in the model - this sometimes makes them easier to access in TF
    K.set_learning_phase(0)
    pred = [None]*numout
    pred_node_names = [None]*numout
    for i in range(numout):
        pred_node_names[i] = prefix+'_'+str(i)
        pred[i] = tf.identity(loaded_model.output[i], name=pred_node_names[i])
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
    parser.add_argument('--h5',required=True, type=str,help='REQUIRED: The h5 model model weights file you wish to convert to .pb')
    parser.add_argument('--numout', type=int, required=True, help='REQUIRED: The number of outputs in the model.')
    parser.add_argument('--outdir','-o', dest='outdir', required=False, default='./', help='The directory to place the output files - default("./")')
    parser.add_argument('--prefix','-p', dest='prefix', required=False, default='k2tfout', help='The prefix for the output aliasing - default("k2tfout")')
    parser.add_argument('--name', required=False, default='output_graph.pb', help='The name of the resulting output graph - default("output_graph.pb") (MUST NOT forget .pb)')
    args = parser.parse_args()

    KerasToTensorflowModel(path_to_json     = args.json,
                           path_to_h5       = args.h5,
                           prefix           = args.prefix,
                           name             = args.name,
                           numout           = args.numout,
                           outdir           = args.outdir)
