"""
Map results produced from UniProt IDs

This simply uses an ID mapping table to take results that were using Uniprot
IDs, map those IDs to RefSeq MANE IDs (if possible), and organizes results
in one-file-per-sequence in a separate directory.
"""

import pandas as pd
from pathlib import Path
from tqdm import tqdm

def create_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser('Map results produced from UniProt IDs')
    parser.add_argument(
        '--source',
        type=Path,
        nargs='+'
    )
    parser.add_argument(
        '--output-dir',
        type=Path
    )
    parser.add_argument(
        '--mapping',
        type=Path
    )
    return parser


def main(args):
    mapping = pd.read_csv(args.mapping, index_col = ['UniProt'])['MANE']
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for raw_result in tqdm(args.source):
        result_df = pd.read_csv(raw_result)
        chunk_df = result_df['chunk'].str.split('[', expand=True, n=2)
        chunk_df.columns = ['id', 'range']
        new_id = chunk_df['id'].replace(mapping)
        result_df['chunk'] = new_id + '[' + chunk_df['range']

        for protein in new_id.unique():
            result_df[new_id == protein].to_csv(args.output_dir / f'{protein}.csv', index=False)


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)