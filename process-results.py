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
import numpy as np
from tqdm import tqdm


AA_COLS = 'LAGVSERTIDPKQNFYMHWC' # This is the order of the ESM-1v vocabulary, and excluding XBUZO
AA_NAMES = {
    'A': 'Ala',
    'R': 'Arg',
    'N': 'Asn',
    'D': 'Asp',
    'C': 'Cys',
    'Q': 'Gln',
    'E': 'Glu',
    'G': 'Gly',
    'H': 'His',
    'I': 'Ile',
    'L': 'Leu',
    'K': 'Lys',
    'M': 'Met',
    'F': 'Phe',
    'P': 'Pro',
    'S': 'Ser',
    'T': 'Thr',
    'W': 'Trp',
    'Y': 'Tyr',
    'V': 'Val'
}
SEQ_OVERLAP = 100 # Sequence overlap for long sequences. Should match value used in prediction script.


def create_parser():
    """Command line argument parser. This also serves as a reference."""

    from argparse import ArgumentParser
    parser = ArgumentParser('Process results from esm-1v models')
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


def merge_estimates(df: pd.DataFrame):
    if df.shape[0] == 1:
        result = df.reset_index(['pos', 'start', 'end'], drop=True)
        result['combined_score'] = result.mean(axis='columns')
        return result
    elif df.shape[0] == 2:
        sorted = df.sort_values('start')

        line = sorted.iloc[:,[0]].reset_index(['pos', 'start', 'end'], drop=True)
        next_line = (
            sorted.iloc[:,[1]]
            .reset_index(['pos', 'start', 'end'], drop=True)
            .rename(columns = lambda s: f'{s}_next')
        )

        result = pd.concat((line, next_line), axis='columns')

        # Merging calculation
        # This uses a cosine sigmoid to smoothly transition from the leading
        # sequence to the trailing sequence. Specifically, the score is
        # s0 * w + s1 * (1 - w)
        # where s0 and s1 are the means of the scores for the leading and
        # trailing sequences respectively. For a position that is p
        # (proportionally) into the overlap,
        # w = { 1 for p < 0.2
        #     { 0 for p > 0.8
        #     { (1 + cos( pi * (p - 0.2) / 0.6 )) / 2 for p in [0.2, 0.8]

        overlap_start = sorted.index['end'][0]
        overlap_end = sorted.index['start'][1]
        pos = sorted.index['pos'][0]
        relative_pos = pos - overlap_start / (overlap_end - overlap_start)

        means = sorted.mean(axis='columns')
        if relative_pos < 0.2:
            score = means[0]
        elif relative_pos > 0.8:
            score = means[1]
        else:
            weight = (1 + np.cos(np.pi * (relative_pos - 0.2) / 0.6)) / 2
            score = means[0] * weight + means[1] * (1-weight)
        
        result['combined_score'] = score

    else:
        raise ValueError(f'Unexpected frame shape: {df.shape}; expected 1 or 2 rows. DF: {df}')


def hgvs_order(ind: pd.Index):
    """Key for ordering hgvs variants (by sequence ID, then position, then alternate AA)"""

    return pd.Index([
        (seq, int(pos), alt)
        for seq, pos, alt in ind.str.extract(r'^([^:]+)[:]p[.][a-zA-Z]{3}(\d+)([a-zA-Z]{3})$').itertuples(index=False)
    ])


def main(args):

    args.output_dir.mkdir(parents=True, exist_ok=True)

    data_df = pd.concat([pd.read_csv(in_path) for in_path in args.source], ignore_index=True)

    # Separate out transcript and range
    index_df = data_df.chunk.str.split(r'[][:]', n=4, expand=True, regex=True)
    index_df.columns = 'seq', 'start', 'end', 'blank'
    
    working_df = pd.concat([index_df.drop('blank', axis='columns'), data_df.drop('chunk', axis='columns')], axis='columns')

    for seq, df in tqdm(working_df.groupby('seq')):
        # Predictions are in the shape of reference AA x alternate AA,
        # end result should have one variant per row.
        (
            df
            # Pivot longer on alt AAs:
            .melt(
                id_vars=['seq', 'start', 'end', 'pos', 'ref', 'model'],
                value_vars=list(AA_COLS),
                var_name='alt',
                value_name='score',
                ignore_index=True
            )
            # Compose HVGS string, i.e. {seq}:p.{ref}{pos}{alt}
            .assign(
                HGVS=lambda df: df.seq + ':p.' + df.ref.map(AA_NAMES) + df.pos.astype(str) + df.alt.map(AA_NAMES)
            )
            # Pivot wider on models
            .pivot(
                index=['HGVS', 'pos', 'start', 'end'],
                columns='model',
                values='score'
            )
            # Merge overlapping estimates
            .groupby('HGVS', group_keys=False).apply(merge_estimates)
            # Sort nicely, i.e.
            # by sequence ID, then position, then alternate AA
            .sort_index(key=hgvs_order)
            # Write output
            .to_csv(args.output_dir / f'{seq}.tsv', sep='\t')
        )


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)