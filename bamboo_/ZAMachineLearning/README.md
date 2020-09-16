# HH Machine Learning 

Software to do multi classification for HH->bbWW analysis

These scripts are used to make hyperparameter scans with Talos and learning on Keras

All scripts are **python3**

## Getting Started

This software is intended to work on Ingrid/Manneback 

### Prerequisites

Modules you will need to load
```
module load root/6.12.04-sl7_gcc73 boost/1.66.0_sl7_gcc73 gcc/gcc-7.3.0-sl7_amd64 python/python36_sl7_gcc73 slurm/slurm_utils 

```

### Installing required python packages 

Below are the required packages that can be installed with pip.

If you do not have sysadmin rights, do not forget to use ``` pipi install --user ...  ```

- [Tensorflow](https://www.tensorflow.org/install/pip) (neural networks learning)
- [Keras](https://pypi.org/project/Keras/) (wraper around Tensorflow)
- [Talos](https://pypi.org/project/talos/) (hyperparameter scans)
- [Root_numpy](https://pypi.org/project/root-numpy/) (From ROOT trees to numpy arrays)
- [Seaborn](https://pypi.org/project/seaborn/) (Data Visualization)
- [Numpy](https://pypi.org/project/numpy/) (Data manipulation)
- [Pandas](https://pypi.org/project/pandas/) (Useful to manipulate numpy arrays altogether)
- [Astetik](https://pypi.org/project/astetik/) (Simplified templates of seaborn required by Talos)
- [Enlighten](https://pypi.org/project/enlighten/) (Practical process bar)
- [Scipy](https://pypi.org/project/scipy/) (Data processing)
- [plotille]( https://pypi.org/project/plotille/)( Plot in the terminal using braille dots)
- [pynvml]( https://pypi.org/project/pynvml/)( Python Bindings for the NVIDIA Management Library)
## Usual workflow

Most of the tweaks are done in two files

    - parameters.py : Most of the parameters that will be used in the training 
    - sampleList.py : produces a dict of paths to be used to import data for the training

They will be described in details in the next subsections

Then we will detail the usual workflow of the hyperparameter scans

### Configuration script

parameters.py contains the global information required by all the scripts, all the variables are accessed via `parameters.something`

They will be decribed in the following 
- paths : where the script will be running, produce the output and models
- ratios : one part goes for training, one for evaluation of the model (used in hyperparameter scans) and one for producing an output for testing
    A check is done to make sure the total accounts to 1, cross validation is not yet included
- Slurm parameters : will be provided to submit_on_slurm.py
- Names : includes 
    - Name of the DNN model to be used in Model.py
    - suffix : used to generate the mask and scaler (see explanation below)
    - cache : to cache the data (see later)
    - json files : contain xsec and event weight sum information
    - resume : name of model to be retrained (very rare)
    - output batch size : for producing the output (just goes faster)
    - split_name : split the output root file per tag or sample name (see later)
- evaluation criterion : to select the best model (based on val_loss or evaluation error, latter better)
- Callbacks for learning :
    - early_stopping_params : see https://keras.io/api/callbacks/early_stopping/
    - reduceLR_params : see https://keras.io/api/callbacks/reduce_lr_on_plateau/
- Scan dictionary : 
    Keys are the names of the parameters we want to scan
    Values are the possible combinations (must always be a list, even for single item)
    Repetition : number of times one hyperpameter set needs to be used (almost all the time : 1)
- Variables (can use any ROOT tricks):
    - cut : cut for data importation
    - weights : what branch to use for sampling weights in the learning
    - inputs : list of branches to be used as training variables
    - outputs : list of branches to be used as training targets
        Note : for branches that are not in tree but will be added later (eg tag) : use $string ($ will be removed after)
    - other_variables : other variables you want to keep in the tree but not use as inputs not targets
- make_dtype : this is because we use root_numpy to produce the root files and it does not like '.', '(', ')', '-' or '*'

### Workflow 

After you have chosen all the parameters, the first try can be on local

Usual command : 
``` 
python ZAMachineLearning.py (args) --scan name_of_scan 
```
The args depend on what you have hardcoded in ZAMachineLearning.py

*Note* : all the hyperparameter combinations will be run sequentially, this might take time ... 

*Tip* : use one combination only (only lists with one item) and small number of epochs to check everything works

The products a the scripts are :
    - csv file : contains the parameters in the scan, loss, acc and error
    - zip file : contains model architecture+weights, results in the csv, plus other details
    
*Tip* : You can either unzip the .zip and load the json and h5 files with the classic method ([here](https://machinelearningmastery.com/save-load-keras-deep-learning-models/)).
Or you can use the `Restore` method of Talos on the zip archive directly (but you need to submit the preprocessing layer specifically, see code in NeuralNet.py)

To submit on the cluster (using the slurm parameters in parameters.py), `--scan` must be replaced by two arguments
``` 
python ZAMachineLearning.py (args) --submit name_of_jobs --split 1
```
`--submit` requires a string as name for the output dir (saved in `slurm`) 
`--split` requires the number of parameters used for each job (almost always 1)

*Note* : if using `--split N`, N! combinations will be used (might be reduncancies between different jobs) --- anyway, you will use 1 almost always
The split parameters will be saved in `split/` it is important that they remain there until the jobs jave finished running. After that they can be removed.

The output and logs will be in `slurm/name_of_jobs`

Now all the zip and csv files will be in the output directory but one needs to find the best one.

The first step is to concatenate the csv, to do that 
```
python ZAMachineLearning.py --csv slurm/name_of_jobs/output/
```
This will create a concatenated csv file in model with name `name_of_jobs`, ordered according to the eval_criterion (evaluation error is better)
Note : for classification the F1 score is used and should be ordered in descending order (aka, the higher the better)

The easy way is then to pick the best model in the csv (it is ordered so it is easy), and get the corresponding zip file (also on the same line of the csv)
Let's say the best model is `slurm/name_of_jobs/output/one_of_the_job_output.zip`, to change its name one can use 
```
python Utils.py --zip slurm/name_of_jobs/output/one_of_the_job_output.zip model/my_model.zip
```

*Warning* : just changing the zip name will not work because the content also needs to change name (hence the function in `Utils.py`)

The other option with more details is to use the report option
```
python ZAMachineLearning.py --report name_of_jobs
```
(the script automatically looks in `model` and adds the .csv extension, so you should not use it)

The script will then printout the 10 best models (according to the eval_criterion), plots on the console several histograms and produces png files.
The plot definitions are in plot_scans.py, they are [seaborn](https://seaborn.pydata.org/) based 

This will give clues on what parameters are doing better jobs. The zip file can the be dealt with the same way as before.

To then produce the test plots, one can use 
```
python ZAMachineLearning.py (args) --model my_model --test
```
(same as csv, no need to specify the directory `model` nor .zip)

This will produce the root output files (split according to `split_name` in parameters.py) on the test set.

The plotting can be done in `Plotting/` (see associated README)

If other files have to be processed, one can use 
```
python ZAMachineLearning.py (args) --model my_model --output key
``` 
Where `key` is one of the key in sampleList.py 

*Note* : There can be several keys 

*Warning* : these samples must not have been used in the training, this will cause undetected overfitting

... And that's it !!

#### Resubmission 
If some jobs failed, they can be resubmitted with the command 
```
python ZAMachineLearning.py (args) --submit name_of_jobs --split 1 --resubmit /slurm/name_of_jobs/output/
```
The script will check what hyperparameters have been processed and which ones are missing, the corresponding jobs will be in a new directory and need to be moved back to the initial one before the csv concatenation step.

*Warning* : the hyperparameter dict in parameters.py must not change in the meantime !!! (especially number of epochs)
Otherwise the parameters in the csv will have changed. But the slurm parameters and keras callbacks can change at resubmission.

### Preprocessing and training/test split

What has not been dealt with in the previous sections is how the data preparation are handled.

#### Data split 

Depending on the ratios in parameters.py, a boolean mask is generated for each dataset.
    - False -> test set
    - True -> training set
The mask is generated as a npy object based on the suffix in parameters.py.

*Note* : If they do not exist, they will be generated and saved. If they exist they will just be loaded.
Warning : If the data changes, the code will exit with an error because the masks do not fit anymore (either delete them or change suffix).  

*Tip* : the point of the mask is that for each hyperparameter the training and test data will be the same and not randomized at each trial.

#### Preprocessing
Preprocessing is very important in machine learning to give all the features of the training the same importance.
We are using here the [Standard Scaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html), the point is to apply :
```
z -> z-mean/std
```
Where mean and std are the mean and standard deviation of the *training* data.

This scaler is saved in a pickle file with suffix in parameters.py as well (same tips and warnings as masks)

The easy way to use it is to transform the training and testing inputs, and do the inverse when saving into root files.
But keeping track of both model and scaler is annoying...

So a custom layer in preprocessing.py incoorporates the mean and std as weights that are then saved in the model. No need to keep track of the scaler anymore when sharing the model.
On the ther side when loading the model, the script must be given so that Keras knows how to handle it (but already included in the machinery here).

### Learning weights

In order to represent in the training the physical significance of the training events, the event weight needs to be used ([doc](https://keras.io/guides/customizing_what_happens_in_fit/#supporting-sampleweight-amp-classweight)).

This is what is given as weight in parameters.py, the issue arises from the negative weights. They can be dealt with in several scenarios
- Use the negative weights as they are : physically makes sens, but if tone batch size contains mostly negative weights the learning will go in the wrong direction.
- Use the absolute value : all statistics, but repressed phase space regions will have more importance in the training.
- Use only the positive values (aka, cut on MC weigt > 0) : reduces the statistics a bit but avois the problem

We use the last option.

This was the events in one sample are correctly weighted wrt to each other. To weigh between samples, the learning weights is set as :
```
learning weight = event weight * Xsec / event weight sum
```
Where these values come from the json files in parameters.py

*Warning* : this is only valid for backgrounds, for signal the Xsec is unknown so better keep only the event weight

On the other side, it is possible that there is less signal statistics than background. To alleviates that, the sum of learning weights is equalized between signal and background.

Eg: learning weights (signal) /= sum(learning weights (signal)) and same for background.

In case of multiclassification (eg, ST, DY, and TT classes) all classes need to have the same sum of learning weights

This is implemented in the beginning of ZAMachineLearning.py.

### Generator
In case there is too much data in the training (rare in case of HEP) to put them in the RAM, small chunks can be loaded in turns and trained on.
The advantage is that many threads can be used to generate the training data from root files.

This will probably not be used here but can be a possibility.

### Cache
The importation from root files can be slow and if the training data is not too big it can be cached (see name in parameters.py).

Warning : whenever you change something in sampleList.py, the preprocessing or mask, the cache must be cleared !!!
Otherwise you will still run on the older cache values and not the changes you chose.


## Authors

* **Florian Bury** -- [Github](https://github.com/FlorianBury)

## Acknowledgments

