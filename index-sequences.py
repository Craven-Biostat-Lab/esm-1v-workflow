# Load refseq and uniprot sequences and make a sequence - to - id dictionary
import gzip
import json
from pathlib import Path
from collections import defaultdict
from itertools import chain
from Bio import SeqIO

def read_gzipped_seqs(files):
    for file in files:
        with gzip.open(file, 'rt') as instream:
            for seq in SeqIO.parse(instream, 'fasta'):
                yield seq

def read_seqs(files):
    for file in files:
        for seq in SeqIO.parse(file, 'fasta'):
            yield seq

if __name__ == '__main__':

    refseqs_dir = Path('resources/protein-refseqs')
    uniprots_dir = Path('chtc/proteins/per-gene')
    mane_fasta = Path('resources/MANE.GRCh38.v1.1.refseq_protein.faa.gz')
    sequence_index_json = Path('resources/sequence_index.json')

    general_mapping = defaultdict(dict)
    for seq in chain(read_gzipped_seqs(refseqs_dir.iterdir()), read_seqs(uniprots_dir.iterdir())):
        general_mapping[str(seq.seq)].update({seq.id: seq.description})

    mapping = {seq: {'all': entries} for seq, entries in general_mapping.items()}

    for seq in read_gzipped_seqs([mane_fasta]):
        mapping[str(seq.seq)]['MANE'] = seq.id

    with sequence_index_json.open('wt') as out_handle:
        out_handle.write(json.dumps(mapping, indent=4))