#!/bin/bash

SCRIPT_DIR=`dirname ${BASH_SOURCE[0]}`
STOP=""
echo "Script directory "$SCRIPT_DIR

function run_setup()
{
    if [[  -z  $2  ]] ; then
        echo 'Usage:'
        echo '  setupEnv.sh <env_file> <install_dir>'
        return 1
    fi
    
    if [[ "$1" == *.yml ]] ; then
        echo "Using enviroment file: "$1
    else
        echo "Conda enviroment file ending with .yml required"
        return 1
    fi
    
    ENV_FILE=$1
    INSTALL_DIR=$2
    
    if [[ -f "$ENV_FILE" ]]; then
        echo "Installing environment:"
        echo "--------------------------------------------"
        cat $ENV_FILE
        echo "--------------------------------------------"
    else
        echo "File $ENV_FILE does not exists"
        return 1
    fi
    
    if [ -d "$INSTALL_DIR" ]; then
        echo "Error - directory "$INSTALL_DIR" exists!"
        return 1
    fi
    echo "Setting up central environment under "$INSTALL_DIR
    
    mkdir $INSTALL_DIR || return 1
    
    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        CONDASCRIPT=Miniconda2-4.3.31-Linux-x86_64.sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        CONDASCRIPT=Miniconda2-4.3.31-MacOSX-x86_64.sh
    elif [[ "$OSTYPE" == "win32" ]]; then
        CONDASCRIPT=Miniconda2-4.3.31-Windows-x86_64.exe
    else
        echo "Unknown OS"
        return 1
    fi
    
    curl -sS -o $INSTALL_DIR/$CONDASCRIPT https://repo.anaconda.com/miniconda/$CONDASCRIPT || return 1
    bash $INSTALL_DIR/$CONDASCRIPT -b -s -p $INSTALL_DIR/miniconda || return 1

    CONDA_BIN=$INSTALL_DIR/miniconda/bin
    export PATH=$CONDA_BIN:$PATH
        
    export TMPDIR=$INSTALL_DIR/tmp
    export TMPPATH=$TMPDIR
    export TEMP=$TMPDIR
    mkdir $TMPDIR
   
    echo "Create environment"
    conda env create -f $ENV_FILE -q python=2.7 || return 1
    rm -rf $INSTALL_DIR/tmp
    
    echo "Generate setup script"
    echo "export PATH="$INSTALL_DIR"/miniconda/bin:\$PATH" > $SCRIPT_DIR/env.sh
    echo "source activate tf" >> $SCRIPT_DIR/env.sh

    echo "export TF_CPP_MIN_LOG_LEVEL=2" >> $SCRIPT_DIR/env.sh
    echo "export OMP_NUM_THREADS=16 #reduce further if out-of-memory" >> $SCRIPT_DIR/env.sh
}

run_setup $1 $2
if [ $? -eq 0 ]
then
  echo "Successfully setup environment"
else
  return 1
fi


