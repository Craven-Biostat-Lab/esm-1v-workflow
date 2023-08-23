"""Count the sequences we have"""

from pathlib import Path
import gzip

def main():
    refseqs_dir = Path('protein-refseqs')

    ids = []
    for fasta_file in refseqs_dir.iterdir():
        with gzip.open(fasta_file.as_posix(), 'rt') as instream:
            lines = instream.readlines()
            ids += [line for line in lines if line.startswith('>')]
    
    print(len(ids))

if __name__ == "__main__":
    main()