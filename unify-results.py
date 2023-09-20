"""
Unify results from esm-1v models obtained on high throughput cluster.
Each container generates results for some subset of our full list of sequences.
Moreover, esm-1v is limited to sequences of at most 1022 AAs, hence we need to
combine results for longer sequences.
"""

from pathlib import Path
import pandas as pd


def load_data_and_metadata(in_path):
    """
    Get two dataframes indexed by our pre-defined indexing columns:
    The "data" dataframe is all columns that are not the index columns.
    The "metadata" dataframe is all index columns
    """
    index_col = ['chunk', 'pos', 'ref', 'model']
    df = pd.read_csv(in_path)
    data = df.set_index(index_col, drop=True)
    metadata = df[index_col].set_index(index_col, drop=False)

    return data, metadata


def create_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser('Unify results from esm-1v models')
    parser.add_argument(
        '--input'
    )
    parser.add_argument(
        '--output-dir',
        type=Path
    )
    return parser


def main(args):
    input_files = Path().glob(args.input)
    data_df, metadata_df = zip(*(load_data_and_metadata(file) for file in input_files))

    # Parse out ID components
    

    print('--output-dir')


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)