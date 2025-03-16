"""Build combined result file

Takes per-protein result files and builds one common result file, ensuring IDs
consitent with a specific gencode version.

Result files are inspected and the actual refence AA sequence is inferred from
the contents. Based on this, corresponding gencode IDs are assigned.
"""

assert __name__ == '__main__', "This is a script only. Don't load it as a module."

import gzip
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from Bio import SeqIO

GENCODE_SEQUENCES = 'resources/gencode.v43.pc_translations.fa.gz'
RESULT_DIR = 'results/processed-mane'
OUT_FILE = '/scratch/yuriy/igvf-esm-1v-predictions.tsv.gz'

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
    'V': 'Val',
    'U': 'Sec',
    'O': 'Pyl'
}

AA_LOOKUP = {v: k for k, v in AA_NAMES.items()}

with gzip.open(GENCODE_SEQUENCES, 'rt') as instream:
    gencode_seq_map = {
        str(seq.seq): seq.id.split('|')
        for seq in SeqIO.parse(instream, 'fasta')
    }

def add_ids(result_df, gencode_seq_map=gencode_seq_map):

    # Infer sequence
    seq = ''.join(
        result_df.HGVS.str.
        extract(r':p\.(?P<ref>[A-Z][a-z][a-z])(?P<pos>\d+)').
        drop_duplicates().
        assign(pos=lambda df: pd.to_numeric(df.pos)).
        set_index('pos').
        sort_index()['ref'].
        map(AA_LOOKUP)
    )

    # Find sequence match
    gencode_ids = gencode_seq_map.get(seq)
    if gencode_ids is None:
        old_ensp = result_df.HGVS[0].split(':')[0]
        print(f'no match for {old_ensp}: {seq}')
        return None
    
    ensp, enst, ensg = gencode_ids[0:3]

    # Rewrite HGVS.p
    result_df['HGVS.p'] = result_df.HGVS.str.replace(
        r'ENSP.+:',
        f'{ensp}:',
        regex=True
    )

    # Attach enst, ensg
    result_df['GENCODE.v43.ENSG'] = ensg
    result_df['GENCODE.v43.ENST'] = enst
    result_df['GENCODE.v43.ENSP'] = ensp
    
    return result_df

pd.concat(
    [
        add_ids(pd.read_table(file))
        for file in tqdm(Path(RESULT_DIR).iterdir())
    ],
    ignore_index=True
)[ # Reorder columns
    [
        'GENCODE.v43.ENSG',
        'GENCODE.v43.ENST',
        'GENCODE.v43.ENSP',
        'HGVS.p',
        'esm1v_t33_650M_UR90S_1',
        'esm1v_t33_650M_UR90S_2',
        'esm1v_t33_650M_UR90S_3',
        'esm1v_t33_650M_UR90S_4',
        'esm1v_t33_650M_UR90S_5',
        'esm1v_t33_650M_UR90S_1_next',
        'esm1v_t33_650M_UR90S_2_next',
        'esm1v_t33_650M_UR90S_3_next',
        'esm1v_t33_650M_UR90S_4_next',
        'esm1v_t33_650M_UR90S_5_next',
        'combined_score'
    ]
].to_csv(OUT_FILE, sep='\t', index=False)
