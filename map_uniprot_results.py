"""
Map results produced from UniProt IDs

This simply uses an ID mapping table to take results that were using Uniprot
IDs, map those IDs to RefSeq MANE IDs (if possible), and organizes results
in one-file-per-sequence in a separate directory.
"""

from collections import defaultdict
from pathlib import Path
import json
import pandas as pd
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
        type=Path,
        required=False
    )
    parser.add_argument(
        '--file-list',
        type=Path,
        required=False
    )
    parser.add_argument(
        '--mapping',
        type=Path
    )
    return parser


def main(args):
    mapping = pd.read_csv(args.mapping, index_col = ['UniProt'])['MANE']

    files_by_id = defaultdict(list)

    # Make id: file map
    for raw_result in tqdm(args.source, 'Inspecting files'):
        result_df = pd.read_csv(raw_result, usecols=['chunk'])
        uniprot_ids = result_df['chunk'].str.split('[', expand=True, n=2)[0].unique()
        for uniprot_id in uniprot_ids:
            files_by_id[uniprot_id].append(raw_result)

    if args.file_list:
        file_list = {u: [f.as_posix() for f in l] for u, l in files_by_id.items()}
        with args.file_list.open('wt') as out_handle:
            json.dump(file_list, out_handle, indent=4)

    # Write output files
    if args.output_dir:

        args.output_dir.mkdir(parents=True, exist_ok=True)
        
        skips = set()

        for uniprot_id, result_files in tqdm(files_by_id.items(), 'Writing files'):

            if uniprot_id not in skips:
                out_df = pd.concat([pd.read_csv(raw_result) for raw_result in result_files], ignore_index=True)
            
                chunk_df = out_df['chunk'].str.split('[', expand=True, n=2)
                chunk_df.columns = ['id', 'range']
                new_id = chunk_df['id'].replace(mapping)
                out_df['chunk'] = new_id + '[' + chunk_df['range']

                for e_id in new_id.unique():
                    out_df[new_id == e_id].to_csv(args.output_dir / f'{e_id}.csv', index=False)
                
                skips = skips.union(chunk_df['id'].unique())


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)