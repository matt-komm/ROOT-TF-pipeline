# ROOT-based preprocessing pipeline for TensorFlow

[![Build Status](https://travis-ci.com/matt-komm/ROOT-TF-pipeline.svg?branch=master)](https://travis-ci.com/matt-komm/ROOT-TF-pipeline)


## Description

This repository contains a demonstration of the preprocessing pipeline 
including a direct interface to [ROOT TTrees](https://root.cern.ch/doc/master/classTTree.html) 
developed in the context of 

> CMS Collaboration, "A deep neural network-based tagger to search for 
> new long-lived particle states decaying to jets", (*paper in preparation*).


## Dependencies

* g++ 7.3
* Python 2.7
* ROOT 6
* TensorFlow >=1.4 (incompatible with 2.X)
* Keras >=2.1.5
* cmake 3 (for building only)

We recommend to use the provided miniconda environment which can be installed
with ```source Env/setupEnv.sh Env/environment.yml <install_directory>```. After
installation, the environment can be activated with ```source Env/env.sh```.


## Building the custom operations

The custom operations in ```Ops``` can be build using cmake as follows:

```
mkdir Ops/build
cd Ops/build
cmake .. -DCMAKE_INSTALL_PREFIX=$PWD/release
make install
```

Check if everything is working by running ```ctest``` from the build directory.

The following variables need to be set to use the created python package 
system-wide:

```
export PYTHONPATH=$PWD/release:$PYTHONPATH
export LD_LIBRARY_PATH=$PWD/release:$LD_LIBRARY_PATH
```

## Samples of QCD events

Files containing flat ROOT TTrees for testing the pipeline are available
in the ```Samples``` directory. These have been produced from the following
open dataset:

CMS Collaboration (2019). Simulated dataset 
```QCD_Pt-15to7000_TuneCUETP8M1_Flat_13TeV_pythia8``` in ```MINIAODSIM``` format 
for 2016 collision data. CERN Open Data Portal. 
[DOI:10.7483/OPENDATA.CMS.J52Q.4T4E](http://opendata.cern.ch/record/12021)


## Run the pipeline example


From the top-level directory of the repository run

```
python pipeline.py 
```

---

### Authors

Matthias Komm, Vilius Cepaitis, Robert Bainbridge, Alex Tapper, 
Oliver Buchmüller.

