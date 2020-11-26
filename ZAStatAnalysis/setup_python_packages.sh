#! /bin/bash

function setup_env {
    export PATH=$PWD/python_packages/bin:$PATH
    export PYTHONPATH=$PWD/python_packages/lib/python2.7/site-packages:$PYTHONPATH
    export PYTHONNOUSERSITE=true
}

if [ ! -d python_packages ]; then
    echo "Installing needed python packages..."

    mkdir python_packages

    prefix=$PWD/python_packages

    curl -O https://bootstrap.pypa.io/get-pip.py
    python get-pip.py --prefix=$prefix -I
    rm get-pip.py

    setup_env

    $PWD/python_packages/bin/pip install -I setuptools --prefix=$prefix
    $PWD/python_packages/bin/pip install -I six --prefix=$prefix --global-option=build_ext --global-option="-L$(python2.7-config --prefix)/lib"
    $PWD/python_packages/bin/pip install -I packaging --prefix=$prefix

    # Install numpy
    $PWD/python_packages/bin/pip install -I numpy --prefix=$prefix
    $PWD/python_packages/bin/pip install -I scipy --prefix=$prefix
    $PWD/python_packages/bin/pip install -I python-dateutil --prefix=$prefix
    $PWD/python_packages/bin/pip install -I matplotlib --prefix=$prefix --global-option=build_ext --global-option="-L$(python2.7-config --prefix)/lib"
else
    setup_env
fi
