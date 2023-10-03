"Verify (MANE) coverage, i.e. the output set contains all the MANE ENSP ids."

assert __name__ == '__main__', "This is a script only. Don't load it as a module."

import gzip
from pathlib import Path
from Bio import SeqIO

MANE_LIST = 'resources/MANE.GRCh38.v1.2.ensembl_protein.faa.gz'
RESULT_DIR = 'results/processed-mane'

reference_set = {
    seq.id
    for seq in SeqIO.parse(gzip.open(MANE_LIST, 'rt'), 'fasta')
}

result_set = {
    file.stem
    for file in Path(RESULT_DIR).iterdir()
}

if reference_set != result_set:
    print(f'Missing from results: \n {reference_set - result_set}')
    print(f'Missing from reference: \n {result_set - reference_set}')