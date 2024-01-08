import pandas as pd
from pathlib import Path


def get_description(file_path: Path):
    name = file_path.stem
    with file_path.open('rt') as in_handle:
        columns = in_handle.readline().strip().split('\t')

    return (
        f'ESM-1v predictions for all single amino acid substitutions in {name}'
        f', contains columns: {columns}'
    )


def main():
    
    common_fields = {
        "lab": "mark-craven",
        "award": "HG012039",
        "file_format": "tsv",
        "file_set": "mark-craven:esm1v-mane-predictions-v1"
    }

    results_folder = Path('../results/processed-mane')

    metadata_df = pd.DataFrame.from_records(
        (
            (
                f'["mark-craven:esm1v-prediction-v1-{f.stem}"]',
                f.resolve().as_posix(),
                get_description(f)
            )
            for f in results_folder.iterdir()
        ),
        columns=['aliases', 'submitted_file_name', 'description']
    )


if __name__ == '__main__':
    main()