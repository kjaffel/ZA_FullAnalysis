# ZA Machine Learning: 
This code is reabsed on the top of **Florian Bury**[ code for HH-> bbWW -Analysis](https://github.com/FlorianBury/HHbbWWAnalysis/tree/master/MachineLearning) and it was udapted to do multi-classification for **H/A-> Z(ll) A/H(bb)** analysis for full run2 data.

## Getting Started:
This software is intended to work on Ingrid/Manneback and all scripts are **python3**. It has been used to make hyperparameter scans with Talos and learning on Keras.

### Prerequisites:
Modules you will need to load:
```
module load root/6.12.04-sl7_gcc73 boost/1.66.0_sl7_gcc73 gcc/gcc-7.3.0-sl7_amd64 python/python36_sl7_gcc73 slurm/slurm_utils 
## OR simply in your ~/.bashrc add:
function dnn_env() {
    module load root/6.12.04-sl7_gcc73
    module load boost/1.66.0_sl7_gcc73
    module load gcc/gcc-7.3.0-sl7_amd64
    module load python/python36_sl7_gcc73
    module load slurm/slurm_utils
}
```
Another option is to use LCG is it's latest version [SPI LCG distribution](http://spi.web.cern.ch/): 
```
function cms_env() {
    module --force purge
    module load cp3
    module load grid/grid_environment_sl7
    /cvmfs/cms.cern.ch/cmsset_default.sh
    module load crab/crab3
    module load slurm/slurm_utils
    module load cms/cmssw
}
alias bamboo_env="source /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc10-opt/setup.sh"
```
### Installing required python packages: 
Below are the required packages that can be installed with pip. If you are working on ``ingrid-ui1`` you don't have to do any of this. If you do not have sysadmin rights, do not forget to use ``pip install --user``.
- [Tensorflow](https://www.tensorflow.org/install/pip) (neural networks learning)
- [Keras](https://pypi.org/project/Keras/) (wraper around Tensorflow)
- [Talos](https://pypi.org/project/talos/) (hyperparameter scans)
- [Root_numpy](https://pypi.org/project/root-numpy/) (From ROOT trees to numpy arrays)
- [Seaborn](https://pypi.org/project/seaborn/) (Data Visualization)
- [Numpy](https://pypi.org/project/numpy/) (Data manipulation)
- [Pandas](https://pypi.org/project/pandas/) (Useful to manipulate numpy arrays altogether)
- [Astetik](https://pypi.org/project/astetik/) (Simplified templates of seaborn required by Talos): ``pip install astetik``
- [Enlighten](https://pypi.org/project/enlighten/) (Practical process bar): ``pip install enlighten``
- [Scipy](https://pypi.org/project/scipy/) (Data processing)
- [plotille]( https://pypi.org/project/plotille/) (Plot in the terminal using braille dots): ``pip install plotille``
- [pynvml]( https://pypi.org/project/pynvml/) (Python Bindings for the NVIDIA Management Library): ``pip install pynvml``
- [wrangle](https://pypi.org/project/wrangle/) (Wrangle - Data Preparation for Deep Learning): ``pip install wrangle``
- [chances](https://pypi.org/project/chances/) (Chances provides a simple utility to access random methods in a unified manner) : ``pip install chances``

## Workflow:
All the tweaks are done in :
- ``parameters.py`` : It's a configuration script includes most of the parameters that will be used during the training.
They will be described in details in the next subsections. Then we will detail the usual workflow of the hyperparameter scans.

### Scripts Configuration:
- ``parameters.py``: contains the global information required by all the scripts, all the variables are accessed via ``parameters.something``.
    - [Path variables](https://github.com/kjaffel/ZA_FullAnalysis/blob/master/bamboo_/ZAMachineLearning/parameters.py#L17-L18): where the script will be running, produce the output and models
    - [Datasets proportion](https://github.com/kjaffel/ZA_FullAnalysis/blob/master/bamboo_/ZAMachineLearning/parameters.py#L27-L30): one part goes for training, one for evaluation of the model (used in hyperparameter scans) and one for producing an output for testing. A check is done to make sure the total accounts to 1, cross validation is not yet included.
- Slurm parameters : will be provided to ``submit_on_slurm.py``
- Names:
    - ``Name``: Name of the DNN model to be used in ``Model.py``
    - ``suffix`` : Used to generate the mask and scaler (see explanation below)
    - ``cache`` : To cache the data (see later)
    - ``json files`` : Contain xsec and event weight sum information
    - ``resume`` : Name of model to be retrained (very rare)
    - ``output batch size`` : For producing the output (just goes faster)
    - ``split_name`` : Split the output root file per tag or sample name (see later)
- Evaluation criterion : To select the best model (based on val_loss or evaluation error, latter better)
- Callbacks for learning :
    - ``early_stopping_params`` : See https://keras.io/api/callbacks/early_stopping/
    - ``reduceLR_params`` : See https://keras.io/api/callbacks/reduce_lr_on_plateau/
- Scan dictionary : 
    - Keys: The names of the parameters we want to scan
    - Values: The possible combinations (must always be a list, even for single item)
    - Repetition : Number of times one hyperpameter set needs to be used (almost all the time : 1)
- Variables:
    - cut : For data importation
    - weights : What branch to use for sampling weights in the learning
    - inputs : List of branches to be used as training variables
    - outputs : List of branches to be used as training targets. **Note :** for branches that are not in tree but will be added later (eg tag) : use $string ($ will be removed after)
    - other_variables : Other variables you want to keep in the tree but not use as inputs not targets
- make_dtype : This is because we use root_numpy to produce the root files and it does not like ``.``, ``(``, ``)``, ``-`` neither ``*``

### Local Test: 
``` python
python ZAMachineLearning.py (args) --scan name_of_scan --debug --verbose
```
- (args): ``--boosted --resolved --process``
    - ``-p/--process``: It can be a list or str ggH for gg-fusion and bbH for b-associated production. f the latest is True, this mean that 1NN is set per process.
    - ``--resolved``  :
    - ``--boosted``   : 
- *Note* : All the hyperparameter combinations will be run sequentially, this might take time ... 
- *Tip*: Use one combination only (only lists with one item) and small number of epochs to check everything works.

The products a the scripts are :
- csv file : Contains the parameters in the scan, loss, acc and error
- zip file : Contains model architecture+weights, results in the csv, plus other details
- *Tip* : You can either unzip the ``.zip`` and load the json and h5 files with the classic method ([here](https://machinelearningmastery.com/save-load-keras-deep-learning-models/)). Or you can use the ``Restore`` method of Talos on the zip archive directly (but you need to submit the preprocessing layer specifically, see code in ``NeuralNet.py``).

### Slurm Submission:
To submit on the cluster try:
``` python
python ZAMachineLearning.py (args) --submit name_of_jobs --split 1
```
- ``--submit``: Requires a string as name for the output dir (saved in ``slurm``) 
- ``--split`` : Requires the number of parameters used for each job (almost always 1)
- *Note* : If using ``--split N``, N! combinations will be used (might be reduncancies between different jobs).
- The split ``.pkl`` files will be saved in ``split/`` it is important that they remain there until the jobs have finished running. After that they can be removed.

The output and logs will be in ``slurm/name_of_jobs``.

### Best Model:
Now all the ``.zip`` and ``.csv`` files will be in the output directory but one needs to find the best one.
1.  The first step is to concatenate the csv:
```python
python ZAMachineLearning.py --csv slurm/name_of_jobs/output/
```
This will create a concatenated ``.csv`` file in model with name ``name_of_jobs``, ordered according to the ``eval_criterion/error`` (evaluation error is better).
- *Note* : For classification the F1 score is used and should be ordered in descending order ( aka the higher the better)

Another way is to use ``--report`` option, the script then will automatically looks in ``model/name_of_jobs.csv``.
```python
python ZAMachineLearning.py --report name_of_jobs
```
The script will then printout the 10 best models (according to the eval_criterion) and plot on the console several histograms and ``.png`` files. 
The plot definitions are in ``plot_scans.py`` and they are [seaborn](https://seaborn.pydata.org/) based.
This will give clues on what parameters are doing better jobs. 
The ``.zip`` file can the be dealt as the same way as step 2 .

2.  The 2nd step is to pick the best model in the ``.csv`` (ordered already), and get the corresponding ``.zip`` file (same line of the ``.csv``). Let's say the best model is ``slurm/name_of_jobs/output/one_of_the_job_output.zip``, to change its name one can use :
```python
python Utils.py --zip slurm/name_of_jobs/output/one_of_the_job_output.zip  model/my_best_model.zip
``` 

3.  To then produce the test plots, one can use (same as csv, no need to specify the directory ``model`` nor ``.zip``)
```python
python ZAMachineLearning.py (args) --model my_model --test
```
This will produce the ``.root`` output files (split according to ``split_name`` in ``parameters.py``) on the test set. The plotting can be done in ``Plotting/`` : If other files have to be processed, one can use 
```python
python ZAMachineLearning.py (args) --model my_model --output key
``` 
- *Warning* : These samples must not have been used in the training, this will cause undetected overfitting

### Resubmission:
If some jobs failed, they can be resubmitted with the command: 
```python
python ZAMachineLearning.py (args) --submit name_of_jobs --split 1 --resubmit /slurm/name_of_jobs/output/
```
The script will check what hyperparameters have been processed and which ones are missing, the corresponding jobs will be in a new directory and need to be moved back to the initial one before the csv concatenation step.

- *Warning* : The hyperparameter dict in ``parameters.py`` must not change in the meantime !(especially number of epochs)
Otherwise the parameters in the csv will have changed. But the slurm parameters and keras callbacks can change at resubmission.

## Preprocessing and Training/Test Split:
What has not been dealt with in the previous sections is how the data preparation are handled.

### Data split :
Depending on the ratios in ``parameters.py``, a boolean mask is generated for each dataset : ``False -> test set`` and ``True -> training set``.

The mask is generated as a ``.npy`` object based on the suffix in ``parameters.py``.

- *Note* : If they do not exist, they will be generated and saved. If they exist they will just be loaded.
- *Warning* : If the data changes, the code will exit with an error because the masks do not fit anymore (either delete them or change suffix).
- *Tip* : The point of the mask is that for each hyperparameter the training and test data will be the same and not randomized at each trial.

### Preprocessing :
Preprocessing is very important in machine learning to give all the features of the training the same importance. We are using here the [Standard Scaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html), the point is to apply ``z -> z-mean/std``. Where mean and std are the mean and standard deviation of the *training* data.

This scaler is saved in a pickle file with suffix in ``parameters.py`` as well. The easy way to use it is to transform the training and testing inputs, and do the inverse when saving into root files.
But keeping track of both model and scaler is annoying... 

So a custom layer in preprocessing.py incoorporates the mean and std as weights that are then saved in the model. No need to keep track of the scaler anymore when sharing the model.
On the ther side when loading the model, the script must be given so that Keras knows how to handle it (but already included in the machinery here).

## Learning Weights :
In order to represent in the training the physical significance of the training events, the event weight needs to be used ([doc](https://keras.io/guides/customizing_what_happens_in_fit/#supporting-sampleweight-amp-classweight)).

This is what is given as weight in ``parameters.py``, the issue arises from the negative weights. They can be dealt with in several scenarios
- Use the negative weights as they are : physically makes sens, but if tone batch size contains mostly negative weights the learning will go in the wrong direction.
- Use the absolute value : all statistics, but repressed phase space regions will have more importance in the training.
- Use only the positive values (aka, cut on MC weigt > 0) : reduces the statistics a bit but avois the problem

We use the last option. This was the events in one sample are correctly weighted wrt to each other. To weigh between samples, the learning weights is set as :
```
learning_weight = event_weight * Xsec / event_weight_sum
```
Where these values come from the ``.json`` files in ``parameters.py``.

- *Warning* : this is only valid for backgrounds, for signal the Xsec is not given so better keep only the event weight.

On the other side, it is possible that there is less signal statistics than background. To alleviates that, the sum of learning weights is equalized between signal and background.
```
learning weights (signal) /= sum(learning weights (signal)) and same for background.
```
In case of multiclassification (eg, ``ZA``, ``DY``, and ``TT`` classes) all classes need to have the same sum of learning weights.

## Generator:
In case there is too much data in the training (rare in case of HEP) to put them in the RAM, small chunks can be loaded in turns and trained on. The advantage is that many threads can be used to generate the training data from root files. This will not be used here but still can be a possibility.

## Cache
The importation from root files can be slow and if the training data is not too big it can be cached.
## Trouble Shotting:
- Debugging: stepping through Python script using gdb.
``bash
gdb -ex r -ex bt --args python < ZA-machine learnig command >
``
