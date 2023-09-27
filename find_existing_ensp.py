"""
Find ENSP IDs for UniProt IDs in existing result files and append to a file
"""

from pathlib import Path
from tqdm import tqdm
import pandas as pd


def create_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser('Find ENSP IDs for UniProt IDs in existing result files and append to a file')
    parser.add_argument(
        '--source',
        type=Path,
        nargs='+'
    )
    parser.add_argument(
        '--output-file',
        type=Path
    )
    parser.add_argument(
        '--mapping',
        type=Path
    )
    return parser


def main(args):
    mapping = pd.read_csv(args.mapping, index_col = ['UniProt'])['MANE']

    ensp_ids = set()

    for raw_result in tqdm(args.source):
        df = pd.read_csv(raw_result, usecols=['chunk'])
        uniprot_ids = df['chunk'].str.split('[', expand=True, n=2)[0].unique()
        ensp_ids |= {
            mapping[uniprot_id]
            for uniprot_id in uniprot_ids
            if uniprot_id in mapping.index
        }
    
    with args.output_file.open('at') as out_handle:
        out_handle.writelines([f'{i}\n' for i in ensp_ids])


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)