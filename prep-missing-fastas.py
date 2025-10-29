"""Prep missing FASTA

Build a FASTA file that contains sequences in the updated MANE proteins list that
are currently missing from results. Useful for MANE version update.
"""

assert __name__ == '__main__', "This is a script only. Don't load it as a module."

import gzip
from pathlib import Path
from Bio import SeqIO

MANE_LIST = 'MANE.GRCh38.v1.4.ensembl_protein.faa.gz'
RESULT_DIR = 'results/processed-mane'
FASTA_FILE = 'chtc/proteins/gencode.v43.diff.fasta'

result_set = {
    file.stem[:-4] # Assuming files are .tsv.gz
    for file in Path(RESULT_DIR).iterdir()
}

sequences_to_run = [
    seq
    for seq in SeqIO.parse(gzip.open(MANE_LIST, 'rt'), 'fasta')
    if seq.id not in result_set
]

print(f'{len(sequences_to_run)} additional sequences to run')

with open(FASTA_FILE, "w") as output_handle:
    SeqIO.write(sequences_to_run, output_handle, "fasta")