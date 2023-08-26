#!/bin/sh

mkdir -p resources/protein-refseqs
cd resources/protein-refseqs

for i in $(seq 1 13);
do
    wget ftp://ftp.ncbi.nih.gov/refseq/H_sapiens/mRNA_Prot/human.${i}.protein.faa.gz
done

cd ../..