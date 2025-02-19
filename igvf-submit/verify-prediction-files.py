"""
Script to verify that all prediction files from the specified MANE version are present.
"""

from pathlib import Path
from argparse import ArgumentParser
import gzip
import re
from Bio import SeqIO

def get_args():
    parser = ArgumentParser(
        description='Verify that predictions for all proteins from the specified FASTA file are present.'
    )
    parser.add_argument(
        '-f', '--fasta', type=Path,
        default='../resources/MANE.GRCh38.v1.4.ensembl_protein.faa.gz',
        help='FASTA file with all sequences to check.'
    )
    parser.add_argument(
        '-r', '--results', type=Path,
        default='../results/processed-mane',
        help='Results dir where scores should be found'
    )
    parser.add_argument(
        '-w', '--write',
        help='If supplied, all missing sequences will be written to this destination in FASTA format.'
    )

    return parser.parse_args()

def main(args):

    with gzip.open(args.fasta, 'rt') as instream:
        seqs = list(SeqIO.parse(instream, 'fasta'))

    versioned_targets = {seq.name for seq in seqs}
    
    unversioned_targets = {name.split('.')[0] for name in versioned_targets}

    results = [file.name.split('.')[0:2] for file in args.results.iterdir()]

    unversioned_results = {ensp for ensp, _ in results}

    completely_missing = unversioned_targets - unversioned_results

    def get_versioned_target(ensp, versioned_targets=versioned_targets):
        for target in versioned_targets:
            if target.split('.')[0] == ensp:
                return target

    mismatched_versions = {
        (result, get_versioned_target(ensp))
        for ensp, version in results
        for result in (f'{ensp}.{version}', )
        if ensp in unversioned_targets and result not in versioned_targets
    }

    extra_results = unversioned_results - unversioned_targets

    print('IDs missing from results: \n' + '\n'.join(completely_missing))
    print('IDs with version mismatch: \n' + '\n'.join(' - '.join(parts) for parts in mismatched_versions))
    print('Extra IDs in results: \n' + '\n'.join(extra_results))

    if args.write:
        print(f'Writing make-up FASTA to {args.write}')
        with open(args.write, 'wt') as ostream:
            SeqIO.write(
                (
                    seq for seq in seqs
                    if seq.name in
                        {get_versioned_target(ensp) for ensp in completely_missing} |
                        {t for _, t in mismatched_versions}
                ),
                ostream,
                'fasta'
            )

if __name__ == '__main__':
    args = get_args()
    main(args)
