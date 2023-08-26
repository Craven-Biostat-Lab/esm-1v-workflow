#!/bin/sh

mkdir -p resources/
cd resources

for i in $(seq 1 5);
do
    wget https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_${i}.pt
done

cd ..