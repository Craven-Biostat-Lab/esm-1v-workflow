#!/bin/sh

mkdir -p protein-refseqs
cd protein-refseqs

for i in $(seq 1 13);
do
    wget ftp://ftp.ncbi.nih.gov/refseq/H_sapiens/mRNA_Prot/human.${i}.protein.faa.gz
done

cd ..