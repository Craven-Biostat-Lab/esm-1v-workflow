from argparse import ArgumentParser
from itertools import count
import hashlib
import gzip
import re

import pandas as pd
from pathlib import Path

def get_args():
    parser = ArgumentParser(
        description='Build the table describing the prediction files for IGVF submission'
    )
    parser.add_argument('-n', '--limit', type=int, default=-1)
    parser.add_argument('-m', '--mapping', default='gene-protein-map.txt', help='Tab-separated file with gene-protein mapping.')
    parser.add_argument('-s', '--filesets_table', default='esm-1v-fileset-metadata.txt')
    parser.add_argument('-f', '--files_table', default='esm-1v-files-metadata.txt')

    return parser.parse_args()


def get_description(file_path: Path, gene=None):
    name = re.match(r'ENSP[0-9]+\.[0-9]', file_path.name)[0]
    with gzip.open(file_path, 'rt') as in_handle:
        columns = in_handle.readline().strip().split('\t')

    description = f'ESM-1v predictions for all single amino acid substitutions in {name}'
    if gene is not None:
        description += f' (gene {gene})'
    description += f', contains columns: {columns}'

    return description


def main():
    args = get_args()

    limiting_iterator = count() if args.limit == -1 else range(args.limit)

    mapping_df = pd.read_table(args.mapping)
    mapping_df = mapping_df[~mapping_df['Protein stable ID version'].isna()]
    gene_mapping = (
        mapping_df
        .set_index('Protein stable ID version')['Gene stable ID']
    )

    common_fields = {
        "lab": "mark-craven",
        "award": "HG012039"
    }

    common_file_fields = {
        "file_format": "tsv",
        "content_type": "coding variant effects",
        "controlled_access": False,
        "file_format_specifications": "mark-craven:esm1v-mane-predictions-documentation-v1"
    }
    common_file_fields.update(common_fields)

    common_fileset_fields = {
        "file_set_type": "functional effect",
        "scope": "genome-wide",
        "documents": '["mark-craven:esm1v-mane-predictions-documentation-v1"]',
        #"donors": '["IGVFDO5469RVDJ"]' # The "virtual human donor" in the IGVF portal
        "donors": '["TSTDO04484973"]' # Random donor for sandbox
    }
    common_fileset_fields.update(common_fields)

    results_folder = Path('../results/processed-mane')

    metadata_df = pd.DataFrame.from_records(
        (
            (
                f'["mark-craven:esm1v-prediction-v1-{protein}"]',
                f.resolve().as_posix(),
                get_description(f),
                hashlib.md5(f.open('rb').read()).hexdigest(),
                f'mark-craven:esm1v-mane-predictions-{gene_mapping[protein]}'
            )
            for _, f in zip(limiting_iterator, results_folder.iterdir())
            for protein in (re.match(r'ENSP[0-9]+\.[0-9]+', f.name)[0],)  # Using for on singleton to mimic "let"
        ),
        columns=['aliases', 'submitted_file_name', 'description', 'md5sum', 'file_set']
    )

    for key, value in common_file_fields.items():
        metadata_df[key] = value

    metadata_df.to_csv(args.files_table, index=False, sep='\t')

    ## Build fileset metadata

    fileset_metadata_df = pd.DataFrame.from_records(
        (
            (
                f'["{alias}"]',
                f'ESM-1v predictions for all single amino acid substitutions in all MANE protein isoforms of {gene}',
                f'["{gene}"]'
            )
            for alias in metadata_df['file_set'].unique()
            for gene in (re.search(r'ENSG.+$', alias)[0],) # Using for on singleton to mimic "let"
        ),
        columns=['aliases', 'description', 'assessed_genes']
    )

    for key, value in common_fileset_fields.items():
        fileset_metadata_df[key] = value

    fileset_metadata_df.to_csv(args.filesets_table, index=False, sep='\t')

if __name__ == '__main__':
    main()
