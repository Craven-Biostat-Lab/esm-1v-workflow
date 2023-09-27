"""
Map results produced from UniProt IDs

This simply uses an ID mapping table to take results that were using Uniprot
IDs, map those IDs to RefSeq MANE IDs (if possible), and organizes results
in one-file-per-sequence in a separate directory.
"""

from collections import defaultdict
from pathlib import Path
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

    result_dfs = defaultdict(list)

    files_by_id = defaultdict(list)

    # Make id: file map
    for raw_result in tqdm(args.source, 'Inspecting files'):
        result_df = pd.read_csv(raw_result, usecols=['chunk'])
        uniprot_ids = result_df['chunk'].str.split('[', expand=True, n=2)[0].unique()
        for uniprot_id in uniprot_ids:
            files_by_id[uniprot_id].append(raw_result)

    # Write output files
    for uniprot_id, result_files in tqdm(files_by_id.items(), 'Writing files'):

        output_dfs = []

        for raw_result in result_files:
            result_df = pd.read_csv(raw_result)
            chunk_df = result_df['chunk'].str.split('[', expand=True, n=2)
            chunk_df.columns = ['id', 'range']
            new_id = chunk_df['id'].replace(mapping)
            result_df['chunk'] = new_id + '[' + chunk_df['range']

            output_dfs.append(result_df[chunk_df['id'] == uniprot_id])
        
        ens_id = mapping[uniprot_id] if uniprot_id in mapping.index else uniprot_id

        pd.concat(output_dfs, ignore_index=True).to_csv(args.output_dir / f'{ens_id}.csv', index=False)


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)