"""
Make a table of the MANE to UNIPROT mapping
"""

import json
import pandas as pd

if __name__ == '__main__':
    sequence_index_json = 'resources/sequence_index.json'
    mane_uniprot_csv = 'resources/mane_uniprot.csv'

    with open(sequence_index_json, 'rt') as in_handle:
        seq_index = json.load(in_handle)
    
    pd.DataFrame.from_records(
        [
            (record['MANE'], seq)
            for record in seq_index.values()
            if 'MANE' in record
            for seq in record['all']
            if '|' in seq
        ]
    ).to_csv(mane_uniprot_csv, index=False)