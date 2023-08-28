#!/bin/sh

mkdir -p container/esm_models
cd container/esm_models

for i in $(seq 1 5);
do
    wget https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_${i}.pt
done

cd ../..