from argparse import ArgumentParser
from itertools import count
import hashlib

import pandas as pd
from pathlib import Path

def get_args():
    parser = ArgumentParser(
        description='Build the table describing the prediction files for IGVF submission'
    )
    parser.add_argument('-n', '--limit', type=int, default=-1)
    parser.add_argument('-o', '--output', default='esm-1v-files-metadata.txt')

    return parser.parse_args()


def get_description(file_path: Path):
    name = file_path.stem
    with file_path.open('rt') as in_handle:
        columns = in_handle.readline().strip().split('\t')

    return (
        f'ESM-1v predictions for all single amino acid substitutions in {name}'
        f', contains columns: {columns}'
    )


def main():
    args = get_args()

    limiting_iterator = count() if args.limit == -1 else range(args.limit)    

    common_fields = {
        "lab": "mark-craven",
        "award": "HG012039",
        "file_format": "tsv",
        "file_set": "mark-craven:esm1v-mane-predictions-v1",
        "content_type": "variant effects",
        "controlled_access": False,
        "file_format_specifications": "mark-craven:esm1v-mane-predictions-documentation-v1"
    }

    results_folder = Path('../results/processed-mane')

    metadata_df = pd.DataFrame.from_records(
        (
            (
                f'["mark-craven:esm1v-prediction-v1-{f.stem}"]',
                f.resolve().as_posix(),
                get_description(f),
                hashlib.md5(f.open('rb').read()).hexdigest()
            )
            for _, f in zip(limiting_iterator, results_folder.iterdir())
        ),
        columns=['aliases', 'submitted_file_name', 'description', 'md5sum']
    )

    for key, value in common_fields.items():
        metadata_df[key] = value

    metadata_df.to_csv(args.output, index=False, sep='\t')

if __name__ == '__main__':
    main()
