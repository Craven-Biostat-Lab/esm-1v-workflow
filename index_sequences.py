"""Count the sequences we have"""

from collections import defaultdict
from pathlib import Path
import gzip
import json

def main():
    refseqs_dir = Path('resources/protein-refseqs')
    sequence_index_json = Path('resources/sequence_index.json')

    mapping = defaultdict(dict)
    for fasta_file in refseqs_dir.iterdir():
        with gzip.open(fasta_file.as_posix(), 'rt') as instream:
            seq_id = None
            name = None
            for line in instream.readlines():
                if line.startswith('>'):
                    if seq_id is not None:
                        mapping[seq].update({seq_id: name})
                    seq = ''
                    seq_id, name = line.split(maxsplit=1)
                    seq_id = seq_id[1:] # strip leading >
                    name = name.rstrip()
                else:
                    seq += line.strip()

            # Add Last line
            mapping[seq].update({seq_id: name})

    with sequence_index_json.open('wt') as outstream:
        outstream.write(json.dumps(mapping, indent=4))
    
    print(f'There are {len(mapping)} unique sequences.')
    print(f'The longest sequence is {max(len(seq) for seq in mapping.keys())} acids long.')
    print(f'The total length of all sequences combined is {sum(len(seq) for seq in mapping.keys())} acids.')
    print(f'There are {sum(len(ids) for ids in mapping.values())} unique IDs.')
    print(f'There are {sum(len(seq) > 1022 for seq in mapping.keys())} sequences longer than 1022.')

if __name__ == "__main__":
    main()
