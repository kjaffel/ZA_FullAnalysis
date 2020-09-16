import os
import sys
import glob
import copy
import argparse
import shutil
import yaml
import json
import pickle
from operator import add
import zipfile
import pandas
import pprint
from sklearn import preprocessing

##################################################################################################
##########################                 GetEntries                   ##########################
##################################################################################################
def GetEntries(f,cut='',treeName="tree"):
    """ Count the entries in a file, with or without a cut """
    from ROOT import TFile
    file_handle = TFile.Open(f) 
    if file_handle.GetListOfKeys().Contains(treeName):
        tree = file_handle.Get(treeName) 
        if cut=='':
            return tree.GetEntries()
        else:
            player = tree.GetPlayer()
            return [player.GetEntries(cut),tree.GetEntries()]
    else:
        print ("Could not open tree %s in file %s"%(treeName,f))
        return 0

##################################################################################################
##########################                 ListEntries                  ##########################
##################################################################################################
def ListEntries(path,part=[''],cut='',treeName="tree"):
    """ Given a path, count the entries of all the files that match part, with or without cuts """
    if cut=='':
        N_tot = 0
    else:
        N_tot = [0,0]
    list_f = glob.glob(path+'/*')
    list_f.sort()
    for f in list_f:
        skip = False
        filename = os.path.basename(f)
        for p in part:
            if filename.find(p)==-1: # Could not find part of name
                skip = True
        if skip:
            continue

        # If dir, get all the root files in it and add number of entries #
        if os.path.isdir(f):
            if cut=='':
                N = 0
            else:
                N = [0,0]
            for root, dirs, files in os.walk(f):
                for rf in files:
                    if rf.endswith('.root'):
                        if cut=='':
                            N += GetEntries(os.path.join(root,rf),treeName=treeName)
                        else:
                            N = list( map(add, N, GetEntries(os.path.join(root,rf),cut)) )
        # If root files, get N directly #
        if os.path.isfile(f) and f.endswith('.root'):
            N = GetEntries(f,cut,treeName=treeName)
        
        if cut=='':
            print (('Object : %s '%(filename)).ljust(70,'.')+('  %d'%(N)).ljust(9,' ')+' entries')    
            N_tot += N
        elif cut!='' and N[1]!=0:
            print (('Object : %s '%(filename)).ljust(70,'.')+('  %d cut / %d total = %0.2f%%'%(N[0],N[1],(N[0]*100/N[1]))).ljust(9,' ')+' entries')    
            N_tot = list( map(add, N_tot, N) )

    print ('-'*120)
    if cut=='':
            print ('All folder : '+('  %d'%(N_tot)).ljust(9,' ')+' entries')    
    else:
        print ('All folder : '+('  %d cut / %d total = %0.2f%%'%(N_tot[0],N_tot[1],(N_tot[0]*100/N_tot[1]))).ljust(9,' ')+' entries')    

##################################################################################################
##########################                 CopyZip                      ##########################
##################################################################################################

def CopyZip(path_in,path_out):
    """ Copy the zip content from path_in to path_out (useful when changin the name of an archive because it changes the names internally)"""
    if not path_in.endswith('.zip') or not path_out.endswith('.zip'):
        sys.exit('You forgot .zip at the end of the file')
    # Split paths #
    dir_in = os.path.dirname(path_in)
    name_in = os.path.basename(path_in)
    dir_out = os.path.dirname(path_out)
    name_out = os.path.basename(path_out)
    # Unzip in tmp dir #
    with zipfile.ZipFile(path_in,"r") as zip_ref:
        tmp_dir = os.path.join(dir_in,'tmp_'+name_in.replace('.zip',''))
        zip_ref.extractall(tmp_dir)
    # Loop over the tmp dir  and rename each file accordint to desired output #
    for f in glob.glob(tmp_dir+'/*'):
        base_f = os.path.basename(f)
        dir_f = os.path.dirname(f)
        new_base = base_f.replace(name_in.replace('.zip',''),name_out.replace('.zip',''))
        os.rename(f,os.path.join(dir_f,new_base))
    # Zip in new file #
    with zipfile.ZipFile(os.path.join(tmp_dir,name_out),"w") as zip_ref:
        for f in glob.glob(tmp_dir+'/*'):
            if f.endswith('.zip'):
                continue # Avoids including the zip file itself
            zip_ref.write(f,os.path.basename(f))
    # Move new zip to dit_out #
    shutil.move(os.path.join(tmp_dir,name_out),path_out)
    # Clean tmp dir #
    shutil.rmtree(tmp_dir)


##################################################################################################
##########################                 CountVariables               ##########################
##################################################################################################
def CountVariables(path_files,var, part=[''],cut='',is_time_in_ms=False):
    """
        Loops over all the files in path_files,
        Find all the branches that match var (can be multiple),
        Add all the values of the event with the given variables (if they pass the cut)
        Returns the total value, variable by variable
    """
    from ROOT import TFile
    from root_numpy import tree2array
    var_dict = {}

    files = glob.glob(os.path.join(path_files,'*.root'))
    if len(files)==0:
        print ('No files in %s matching %s have been found'%(path_files,part))

    for f in files:
        filename = f.replace(path_files,'').replace('root','')
        skip = False 
        for p in part:
            if filename.find(p)==-1: # Could not find part of name
                skip = True
        if skip:
            continue

        print ('\t Looking at %s'%(filename))
        # Get the branch names #
        name_list = []
        root_file = TFile.Open(f)
        tree = root_file.Get("tree")
        br = tree.GetListOfBranches().Clone()
        for b in br: # Loop over branch objetcs
            name_list.append(b.GetName())

        # Only keep the ones that contain var #
        var_list = [k for k in name_list if var in k]
        for vl in var_list: # Save the branch names in the dict
            if not vl in var_dict:
                var_dict[vl] = 0

        # Get the numpy array from this tree, then pandas #
        data = tree2array(tree,branches=var_list,selection=cut)
        data = pandas.DataFrame(data)
        for name, values in data.iteritems():
            var_dict[name] += values.sum()

    # Print the results #
    total_var = 0
    print ('')
    for k,v in var_dict.items():
        if is_time_in_ms:
            print (("Branch : %s "%k).ljust(50,'.'),' Value : ',convert_time(v))        
        else:
            print (("Branch : %s "%k).ljust(50,'.'),' Value : %f'%v)        
        total_var += v
    print ('-'*80)
    if is_time_in_ms:
        print ('Total for all variables '.ljust(50,'.'),' Value : ',convert_time(total_var))
    else:
        print ('Total for all variables '.ljust(50,'.'),' Value : %f'%total_var)
    print ('')
    print ('')
    
        
def convert_time(time):
    seconds=(time/1000)%60
    seconds = int(seconds)
    minutes=(time/(1000*60))%60
    minutes = int(minutes)
    hours=(time/(1000*60*60))%24
    days = (time/(1000*60*60*24))

    return ("%6dd:%2dh:%2dm:%2ds" % (days, hours, minutes, seconds))

##################################################################################################
##########################                 ListBranches                 ##########################
##################################################################################################
def ListBranches(rootfile,treeName ='tree',verbose=False):
    from ROOT import TFile
    name_list = []
    root_file = TFile.Open(rootfile)
    tree = root_file.Get(treeName)
    br = tree.GetListOfBranches().Clone()
    for b in br: # Loop over branch objects
        name = []
        try:
            if b.GetTypeName()=='ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<double> >' or \
               b.GetTypeName()=='ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<float> >' or \
               b.GetTypeName()=='ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiE4D<double> >' or \
               b.GetTypeName()=='ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiE4D<float> >':
                name.extend([b.GetName()+'.Px()',b.GetName()+'.Py()',b.GetName()+'.Pz()',b.GetName()+'.E()'])
                name.extend([b.GetName()+'.Pt()',b.GetName()+'.Eta()',b.GetName()+'.Phi()',b.GetName()+'.M()'])
        except:
            pass
        if len(name)==0:
            name.append(b.GetName())
        name_list.extend(name)
    if verbose:
        print ('Branches from %s'%rootfile)
        for l in name_list:
            print ('\t%s'%l)

    root_file.Close()
    return name_list

##################################################################################################
##########################                 AppendTree                   ##########################
##################################################################################################
def find_rows(a, b):
    """
    Find the matching rows between a and b
    Returns numpy arrays of the matches as [idx in a,idx in b]
    """
    import numpy as np
    dt = np.dtype((np.void, a.dtype.itemsize * a.shape[1]))

    a_view = np.ascontiguousarray(a).view(dt).ravel()
    b_view = np.ascontiguousarray(b).view(dt).ravel()

    sort_b = np.argsort(b_view)
    where_in_b = np.searchsorted(b_view, a_view,
                                 sorter=sort_b)
    where_in_b = np.take(sort_b, where_in_b)
    which_in_a = np.take(b_view, where_in_b) == a_view
    where_in_b = where_in_b[which_in_a]
    which_in_a = np.nonzero(which_in_a)[0]
    return np.column_stack((which_in_a, where_in_b))

def AppendTree(rootfile1,rootfile2,branches,event_filter=None,rename=None,treeName='tree'):
    """
    Append the branches of rootfile2 to rootfile1
    If event_filter=None : All the common branches must be identical (make sure events are the same)
    if not None : only append events in rootfile2 that are in rootfile1 
        -> event_filt = list of variable to compare events
        /!\ len(rootfile1)<len(rootfile2) in this case
    """
    # Get the arrays #
    import root_numpy
    import pandas as pd
    data1 = pd.DataFrame(root_numpy.root2array(rootfile1,treeName,branches=ListBranches(rootfile1,treeName)))
    # Check that the requested branches are in rootfile2 #
    list_branches2 = ListBranches(rootfile2,treeName)
    for b in branches:
        if not b in list_branches2:
            print ('Branch %s not present in file %s'%(b,rootfile2))
    if event_filter is None:
        data2 = pd.DataFrame(root_numpy.root2array(rootfile2,treeName,branches=branches))
    else:
        data2 = pd.DataFrame(root_numpy.root2array(rootfile2,treeName,branches=branches+event_filter))

    if data1.shape[0] != data2.shape[0] and event_filter is None:
        sys.exit('The two files do not have the same number of events')
    print ('Number of branches in first file : %d'%data1.shape[1])
    print ('Number of branches in second file to append : %d'%data2.shape[1])

    # Event filtering #
    if event_filter is not None:
        indexes = find_rows(data1[event_filter].values,data2[event_filter].values)[:,1]
            # [:,0] indexes in first array, [:,1] indexes in second array
        data2 = data2[branches].iloc[indexes].reset_index(drop=True)

    # Renaming columns #
    if rename is not None:
        data2.columns = rename

    # Concatenate them #
    all_df = pd.concat((data1,data2),axis=1)
    all_data  = all_df.to_records(index=False,column_dtypes='float64')
    all_data.dtype.names = [s.replace('(','').replace(')','').replace('.','_') for s in all_data.dtype.names] #root_numpy issues
    
    # Save them #
    root_numpy.array2root(all_data,rootfile1.replace('.root','_new.root'),mode='recreate',treename=treeName)
    print ('New file saved as %s'%rootfile1.replace('.root','_new.root'))

##################################################################################################
##################           ExtractXsecAndEventWeightSumFromYaml              ###################
##################################################################################################
def ExtractXsecAndEventWeightSumFromYaml(yaml_path,suffix):
    xsec_dict = {}
    ews_dict = {}
    # Load YAML file #
    with open(yaml_path, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    # Save Xsec and event weight sum in dict #
    files  = data["files"]
    for sample, dico in files.items():
        if dico["type"] != 'data':
            xsec_dict[sample] = dico["cross-section"]
            ews_dict[sample] = dico["generated-events"]

    with open("%s_xsec.json"%suffix, "w") as handle:
        json.dump(xsec_dict,handle,indent=4)

    with open("%s_event_weight_sum.json"%suffix, "w") as handle:
        json.dump(ews_dict,handle,indent=4)

    print ("Generated file %s_xsec.json"%suffix)
    print ("Generated file %s_event_weight_sum.json"%suffix)

##################################################################################################
#####################           RemovePreprocessingLayer             #############################
##################################################################################################
def RemovePreprocessingLayer(json_file,h5_file,suffix):
    # Remove Preprocess layer from json file #
    print ("Modifying the json file content %s"%json_file)
    with open(json_file, 'r') as f:
        arch = json.load(f)
    preprocess_layer = arch['config']['layers'][1]
    mean = preprocess_layer['config']['mean']
    std = preprocess_layer['config']['std']
    del arch['config']['layers'][1]
    arch['config']['layers'][1]['inbound_nodes'][0][0][0] = arch['config']['input_layers'][0][0]

    with open("%s%s"%(suffix,json_file), 'w') as f:
        json.dump(arch,f)
    print ("New architecture saved in %s%s"%(suffix,json_file))
    pprint.pprint(arch)

    # Save scaler #
    scaler = preprocessing.StandardScaler()
    scaler.mean_ = mean
    scaler.std_= std
    with open("%sscaler.pkl"%suffix, 'wb') as handle:
        pickle.dump(scaler, handle)

    # Remove Preprocess layer from h5 file #
    print ("Modifying the h5 file content %s"%h5_file)
    f = h5py.File(h5_file, 'r')
    new_f = h5py.File("%s%s"%(suffix,h5_file), 'w')

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
    print ("New h5 file saved as %s%s"%(suffix,h5_file))

##################################################################################################
##########################                 Main                         ##########################
##################################################################################################

if __name__=='__main__':
    parser = argparse.ArgumentParser('Several useful tools in the context of MoMEMtaNeuralNet',conflict_handler='resolve')

    countArgs = parser.add_argument_group('Count tree events in multiple root files')
    countArgs.add_argument('--path', action='store', required=False, 
        help='Path for the count')
    countArgs.add_argument('--input', action='append', nargs='+', required=False, 
        help='List of strings that must be contained in the filename')
    countArgs.add_argument('--cut', action='store', default='', type=str, required=False, 
        help='Cuts to be applied')
    countArgs.add_argument('--tree', action='store', default='tree', type=str, required=False, 
        help='Name of the tree (default="tree")')

    zipArgs = parser.add_argument_group('Concatenate zip files (also modifying names of files inside the archive')
    zipArgs.add_argument('--zip', action='append', nargs=2, required=False, 
        help='path to input .zip + path to output .zip')

    CountVar = parser.add_argument_group('Counts the sum of variables in all files')
    CountVar.add_argument('--variable', action='store', required=False, type=str, 
        help='Partial name of the branches to include in the count (--path must have been provided)')
    CountVar.add_argument('--list', action='store', required=False, type=str, 
        help='Lists all the branches of a given file')

    appendArgs = parser.add_argument_group('Concatenate branches of one root file to the other')
    appendArgs.add_argument('--append', action='append', nargs='+', required=False, 
        help='Name of first root file + Name of second root file + list of branches to be taken from second and appended to first')
    appendArgs.add_argument('--append_filter', action='append', nargs='+', required=False, 
        help='List of branches that must be used in the filter to append files')
    appendArgs.add_argument('--append_rename', action='append', nargs='+', required=False, 
        help='List of names that should replace the appended column names (must have the same number of entries)')

    yamlExtract = parser.add_argument_group('Parse a YAML file produced by bamboo to extract Xsec and event weight sum')
    yamlExtract.add_argument("--yaml", action='store', type=str, required=False,                                                                                                                            
        help='Name of the YAML file used by plotIt containign Xsec and event weight sum')
    yamlExtract.add_argument("--suffix", action='store', type=str, required=False, default='',
        help='Will produce {suffix}_xsec.json and {suffix}_event_weight_sum.json (default = "")')

    removePreProcess = parser.add_argument_group('Remove Preprocess layer from a model in json (architecture) and h5 files (weights)')
    removePreProcess.add_argument("--json", action='store', type=str, required=False,
        help='Name of the json file containing the network architecture')
    removePreProcess.add_argument("--h5", action='store', type=str, required=False,
        help='Name of the h5 file containing the network weights')
    removePreProcess.add_argument("--suffix", action='store', type=str, required=False, default='',
        help='Suffix to be added in from of the new files ({suffix}file.json, {suffix}file.h5 and {suffix}scaler.pkl which contains the extracted preprocessing parameters)')

    #----- Execution -----#
    args = parser.parse_args()
    if args.path is not None:
        if args.input is not None:
            if args.variable is not None:
                CountVariables(args.path,args.variable,is_time_in_ms=True,part=args.input[0])
            ListEntries(path=args.path,part=args.input[0],cut=args.cut,treeName=args.tree)
        else:
            if args.variable is not None:
                CountVariables(args.path,args.variable,is_time_in_ms=True)
            ListEntries(path=args.path,cut=args.cut,treeName=args.tree)

    if args.zip is not None:
        CopyZip(args.zip[0][0],args.zip[0][1])

    if args.list is not None:
        _ = ListBranches(args.list,verbose=True)

    if args.append is not None:
        if len(args.append[0])<=2:
            print ('Not enough arguments to append')
        else:
            file1 = args.append[0][0]
            file2 = args.append[0][1]
            branches = args.append[0][2:]
            print ('File to be appended : %s'%file1)
            print ('File to append      : %s'%file2)
            print ('Branches to append :')
            for b in branches:
                print ('..... %s'%b)
            if args.append_filter is not None:
                filter_events = args.append_filter[0]
                print ('Branches for filtering : ')
                for fe in filter_events:
                    print ('..... %s'%fe)
            else:
                filter_events = None
            if args.append_rename is not None:
                list_names = args.append_rename[0]
                print ('Branches renaming : ')
                for ln in list_names:
                    print ('..... %s'%ln)
                if len(branches) != len(list_names):
                    print ('Number of names not consistent with appended branches')
                    sys.exit(1)
            else:
                list_names = None
            treeName = args.tree if args.tree is not None else 'tree'
            AppendTree(file1,file2,branches,event_filter=filter_events,rename=list_names,treeName=treeName)

    if args.yaml is not None:
        ExtractXsecAndEventWeightSumFromYaml(args.yaml,args.suffix)

    if args.json is not None and args.h5 is not None:
        RemovePreprocessingLayer(args.json,args.h5,args.suffix)


