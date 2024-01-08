"""Script for uploading ESM-1v predictions on MANE transcripts to synapse"""

from pathlib import Path
from synapseclient import File, login

def get_annotations(prediction_file):
    name = prediction_file.stem
    with prediction_file.open('rt') as in_handle:
        columns = in_handle.readline().strip().split('\t')
    return {
        'protein': name,
        'columns': columns,
        'file_format': 'tsv',
        'output_type': 'functional prediction scores' 
    }

def main():

    syn = login()

    results_folder = Path('../results/processed-mane')
    synapse_dir = 'syn53240126'

    for prediction_file in results_folder.iterdir():
        entity = File(path=prediction_file.as_posix(), parent=synapse_dir)
        entity.annotations = get_annotations(prediction_file)
        syn.store(entity)


if __name__ == '__main__':
    main()