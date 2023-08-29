#!/bin/sh

MODEL_LOCATION='container/esm_models'
OWD=$(pwd)

mkdir -p $MODEL_LOCATION
cd $MODEL_LOCATION

for i in $(seq 1 5);
do
    wget https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_${i}.pt
done

cd $OWD