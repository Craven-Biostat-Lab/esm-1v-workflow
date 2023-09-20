"""
Process results from esm-1v models obtained on high throughput cluster.

This accomplishes several actions:

* Groups outputs by transcript
* ESM-1v is limited to sequences of at most 1022 AAs, we combine results for
  longer sequences.
* We reshape the output from a (ref AA x alt AA) matrix to one substitution per
  row.
* We express substitutions using the HGVS standard
* We summarize results across the 5 models
"""

from pathlib import Path
import pandas as pd
from tqdm import tqdm


AA_COLS = 'LAGVSERTIDPKQNFYMHWC' # This is the order of the ESM-1v vocabulary, and excluding XBUZO
AA_NAMES = {} # TODO


def create_parser():
    """Command line argument parser. This also serves as a reference."""

    from argparse import ArgumentParser
    parser = ArgumentParser('Unify results from esm-1v models')
    parser.add_argument(
        '--source',
        type=Path,
        nargs='+'
    )
    parser.add_argument(
        '--output-dir',
        type=Path
    )
    return parser


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


def main(args):

    args.output_dir.mkdir(parents=True, exist_ok=True)

    data_df = pd.concat([pd.read_csv(in_path) for in_path in args.source], ignore_index=True)

    # Separate out transcript and range
    index_df = data_df.chunk.str.spit('[:]', n=4, expand=True)
    index_df.columns = 'seq', 'start', 'end', 'blank'
    
    working_df = pd.concat([index_df.drop('blank'), data_df.drop('chunk')], axis='columns')

    for seq, df in tqdm(working_df.groupby('seq')):
        # Reshape
        # Compose HVGS string
        # Merge overlapping estimates
        # Compute final estimate
        # Write output
        pass


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)