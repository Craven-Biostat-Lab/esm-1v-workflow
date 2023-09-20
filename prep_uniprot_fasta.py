import gzip
from urllib.request import urlopen
from pathlib import Path
from collections import defaultdict
from itertools import chain
from Bio import SeqIO

# Destination dir
WRITE_TO = Path('chtc/proteins')

def get_sequences(url):
    with urlopen(url) as url_handle:
        with gzip.open(url_handle, 'rt') as gz_handle:
            for seq in SeqIO.parse(gz_handle, 'fasta'):
                yield seq

if __name__ == '__main__':

    # URLS
    canonical_url = 'https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz'
    isoforms_url = 'https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot_varsplic.fasta.gz'

    # Group by gene and filter to human
    groups_by_gene = defaultdict(list)
    for seq in chain(get_sequences(canonical_url), get_sequences(isoforms_url)):
        gene_name = seq.id.split('|')[2]
        if gene_name.endswith('_HUMAN'):
            groups_by_gene[gene_name].append(seq)

    # Make destination dir
    WRITE_TO.mkdir(parents=True, exist_ok=True)

    for gene_name, seqs in groups_by_gene.items():
        with (WRITE_TO / f'{gene_name}.fasta').open('wt') as out_handle:
            SeqIO.write(seqs, out_handle, 'fasta')