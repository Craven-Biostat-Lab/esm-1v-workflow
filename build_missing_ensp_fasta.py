"""
Needed for generating any MANE results missing from existing results

Take in a file listing ENSP IDs of existing results, cross-check against the
MANE FASTA file and generate FASTA files of at most 50 sequences each that
contain the sequences missing from existing results.
"""

from pathlib import Path
from itertools import count
import gzip
from Bio import SeqIO
from tqdm import tqdm


def create_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser('Make FASTA files for missing IDs')
    parser.add_argument(
        '--mane-fasta',
        type=Path
    )
    parser.add_argument(
        '--existing',
        type=Path
    )
    parser.add_argument(
        '--output-dir',
        type=Path
    )
    parser.add_argument(
        '--output-size',
        type=int,
        default=50
    )
    return parser


def read_gzipped_seqs(file):
    with gzip.open(file, 'rt') as instream:
        for seq in SeqIO.parse(instream, 'fasta'):
            yield seq


def main(args):
    
    # Result IDs
    with args.existing.open('rt') as in_handle:
        result_ids = {line.strip() for line in in_handle.readlines()}

    # Prepare for output
    args.output_dir.mkdir(exist_ok=True, parents=True)

    # Get needed sequences
    out_seqs = [
        seq
        for seq in tqdm(
            read_gzipped_seqs(args.mane_fasta),
            'reading sequences'
        )
        if seq.id not in result_ids
    ]

    # Write output
    for n in tqdm(count(), 'writing sequences'):
        if not out_seqs:
            break
        with gzip.open(args.output_dir / f'bundle_{n}.fasta.gz', 'wt') as out_handle:
            SeqIO.write(out_seqs[:args.output_size], out_handle, 'fasta')
        out_seqs = out_seqs[args.output_size:]


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)