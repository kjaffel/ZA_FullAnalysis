from __future__ import print_function
import sys
import os
import json
import h5py    
import copy
import pprint 
import pickle
import numpy as np
from sklearn import preprocessing
import parameters

class generateLwtnnNetwork():
    def __init__(self,json_file,h5_file):
        self.json_file      = json_file
        self.h5_file        = h5_file
        self.new_json_file  = "new_"+os.path.basename(json_file)
        self.new_h5_file    = "new_"+os.path.basename(h5_file)
        self.scaler_file    = self.new_h5_file.replace(".h5",".pkl")
        self.path_to_convert= "~/LWTNN/lwtnn/converters/kerasfunc2json.py"
        self.variables_json = "variables.json"
        self.neuralNet_json = "neuralNet.json"

    def removeJsonPreprocess(self):
        print ("="*80)
        print ("Modifying the json file %s"%self.json_file)
        with open(self.json_file, 'r') as f:
            arch = json.load(f)
        preprocess_layer = arch['config']['layers'][1]
        self.mean = preprocess_layer['config']['mean']
        self.std = preprocess_layer['config']['std']

        del arch['config']['layers'][1]

        arch['config']['layers'][1]['inbound_nodes'][0][0][0] = arch['config']['input_layers'][0][0]


        with open(self.new_json_file, 'w') as f:
            json.dump(arch,f)

        print ("New architecture saved in %s"%self.new_json_file)
        pprint.pprint(arch)

    def print_structure(weight_file_path):
        """
        Prints out the structure of HDF5 file.

        Args:
          weight_file_path (str) : Path to the file to analyze
        """
        f = h5py.File(weight_file_path,'r')
        try:
            if len(f.attrs.items()):
                print("{} contains: ".format(weight_file_path))
                print("Root attributes:")

            print("f.attrs.items(): ")
            for key, value in f.attrs.items():           
                print("  {}: {}".format(key, value))

            if len(f.items())==0:
                print("Terminate # len(f.items())==0: ")
                return 

            print("layer, g in f.items():")
            for layer, g in f.items():            
                print("  {}".format(layer))
                print("    g.attrs.items(): Attributes:")
                for key, value in g.attrs.items():
                    print("      {}: {}".format(key, value))

                print("    Dataset:")
                for p_name in g.keys():
                    param = g[p_name]
                    subkeys = param.keys()
                    print("    Dataset: param.keys():")
                    for k_name in param.keys():
                        print("      {}/{}: {}".format(p_name, k_name, param.get(k_name)[:]))
                print()
        finally:
            f.close()

    def removeH5Preprocess(self):
        print ("="*80)
        print ("Modifying the h5 file %s"%self.h5_file)
        f = h5py.File(self.h5_file, 'r')
        new_f = h5py.File(self.new_h5_file, 'w')

        for key, value in f.attrs.items(): # Needs to copy h5 attributes
            if isinstance(value,np.ndarray): # Need to exclude the preprocess name from list of layers
                new_value = np.ndarray(shape=(value.shape[0]-1,),dtype=value.dtype)
                j = 0
                for i in range(value.shape[0]):
                    if b'Preprocess' not in value[i]:
                        new_value[j] = value[i]
                        j += 1
                new_f.attrs[key] = new_value
            else:
                new_f.attrs[key] = value

        for layer, group in f.items():     # Loop on groups and their names 'layer)
            print ("Layer {}".format(layer))
            # Check if preprocess layer #
            if 'Preprocess' in layer:
                print ('  Skipped')
                continue
            # Empty layers (dropout, ...)
            if (len(list(group.keys())) == 0): # Does not contain subgroups of datasets
                new_g = new_f.create_group(layer)
                for key, value in group.attrs.items():
                    new_g.attrs.create(key,value)
                print ("  Empty group, has been copied")
            # Non-Empty layers (dense, ...)
            else: # Does contain something
                new_g = new_f.create_group(layer)       # Create first level group
                for key, value in group.attrs.items():  # Copy attributes of group
                    new_g.attrs.create(key,value) 
                for subname, subgroup in group.items(): # Loop through subgroups
                    print ("  Contains subgroup ",subname)
                    print ("  Group {}/{} has been added".format(layer,subname))
                    new_subg = new_f.create_group("{}/{}".format(layer,subname)) # Create subgroup
                    for dataset_name in subgroup.keys():    # Loop through datasets in the given layer and add them to new file
                        print ("    Added dataset {}/{}/{} to group".format(layer,subname,dataset_name))
                        new_f.create_dataset("{}/{}/{}".format(layer,subname,dataset_name),data=subgroup.get(dataset_name)[:])
                        
        f.close()
        new_f.close()
        print ("New h5 file saved as %s"%self.new_h5_file)

    def makeVariablesJson(self):
        print ("="*80)
        print ("Generate the variables json file")
        os.system("{} {} {} > {}".format(self.path_to_convert,self.new_json_file,self.new_h5_file,self.variables_json))
        print ("Created json file %s"%self.variables_json)

    def modifyVariablesJson(self):
        print ("="*80)
        print ("Modify the variables json script")
        with open(self.variables_json, 'r') as f:
            variables = json.load(f)
        N_var = len(variables['inputs'][0]['variables'])
        assert(N_var == len(parameters.inputs))

        # Change input names, offset and scales #
        for i in range(N_var):
            var = variables['inputs'][0]['variables'][i]
            var['name'] = parameters.inputs[i]
            var['offset'] = -self.mean[i]
            var['scale'] = 1/self.std[i]

        # Change output name #
        variables['outputs'][0]['labels'] = [parameters.outputs[0]]
        #variables['outputs'][0]['name'] = parameters.outputs[0]

        pprint.pprint (variables)
        with open(self.variables_json, 'w') as f:
            json.dump(variables,f,indent=4)

    def makeNeuralNetJson(self):
        print ("="*80)
        print ("Generate the Neural Net json file")
        os.system("{} {} {} {} > {}".format(self.path_to_convert,self.new_json_file,self.new_h5_file,self.variables_json,self.neuralNet_json))
        print ("Created json file %s"%self.neuralNet_json)

    def saveScaler(self):
        print ("="*80)
        scaler = preprocessing.StandardScaler()
        scaler.mean_ = self.mean
        scaler.scale_ = self.std
        with open(self.scaler_file, 'wb') as handle:
            pickle.dump(scaler, handle)
        print ("Created scaler file %s"%self.scaler_file)

    def cleanUp(self):
        print ("="*80)
        print ("Clean up")
        #os.system('rm -v '+self.new_json_file)
        #os.system('rm -v '+self.new_h5_file)
        #os.system('rm -v '+self.variables_json)

if __name__ == '__main__':
    instance = generateLwtnnNetwork(sys.argv[1],sys.argv[2])
    instance.removeJsonPreprocess()
    instance.removeH5Preprocess()
    instance.makeVariablesJson()
    instance.modifyVariablesJson()
    instance.makeNeuralNetJson()
    instance.saveScaler()
    instance.cleanUp()
    #print_structure(sys.argv[2])
