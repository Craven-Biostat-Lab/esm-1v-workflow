"""Generate ESM-1v predictions for every amino acid substitution in a collection of sequences."""

from argparse import ArgumentParser
from pathlib import Path
import gzip
from timeit import default_timer

import pandas as pd
from tqdm import tqdm
from Bio import SeqIO
import torch
from esm import pretrained

# ESM-1v models won't handle sequences longer than 1024.
# Accounting for the start and end tokens this leaves 1022 AAs.
# To process larger proteins, we break up the sequences into chunks of 1022
# AAs, but we maintain an overlap between consecutive chunks to eliminate
# start-of-sequence and end-of-sequence biases.
MAX_SEQ_LENTH = 1022
SEQ_OVERLAP = 100

# We (maybe) need to be careful about trying to load too much into the GPU
MAX_BATCH_SIZE = 40

def create_parser():
    parser = ArgumentParser(
        description = "Generate ESM-1v predictions for every amino acid substitution in a collection of sequences."
    )

    parser.add_argument(
        '--model-location',
        type=str,
        help='PyTorch model file OR name of pretrained model to download',
        nargs='+'
    )

    parser.add_argument(
        '--sequences',
        type=Path,
        help='FASTA file of sequences to use. Can be gzipped.'
    )

    parser.add_argument(
        '--results',
        type=Path,
        help='Output file to which to write CSV-formatted results.'
    )

    parser.add_argument(
        "--scoring-strategy",
        type=str,
        default="masked-marginals",
        choices=["wt-marginals", "masked-marginals"],
        help="Choice of scoring strategy."
    )

    return parser


def chunk_sequences(seq_list):
    chunk_list = []
    for seq in seq_list:
        remainder = seq.seq
        index = 0
        while remainder:
            chunk_len = min(len(remainder), MAX_SEQ_LENTH)
            chunk_list.append(
                (f'{seq.id}[{index}:{index+chunk_len}]', remainder[0:chunk_len])
            )
            if len(remainder) > MAX_SEQ_LENTH:
                remainder = remainder[(MAX_SEQ_LENTH - SEQ_OVERLAP):]
                index += MAX_SEQ_LENTH - SEQ_OVERLAP
            else:
                remainder = None
    return chunk_list


def run_wt_marginals_model(model_location, chunk_list):

    start_time = default_timer()
    print('Loading model')

    # Get model name
    model_name = Path(model_location).stem if model_location.endswith('.pt') else model_location

    # Load model
    model, alphabet = pretrained.load_model_and_alphabet(model_location)
    model.eval()

    if torch.cuda.is_available():
        model = model.cuda()
        print("Transferred model to GPU")

    print(f'It took {default_timer() - start_time} seconds to load the model.')

    batch_converter = alphabet.get_batch_converter()

    results = []
    chunks_left = chunk_list
    while chunks_left:
        start_time = default_timer()
        processed_chunks = chunks_left[:MAX_BATCH_SIZE]
        chunks_left = chunks_left[MAX_BATCH_SIZE:]

        batch_labels, batch_strs, batch_tokens = batch_converter(processed_chunks)

        # Using the marginals scoring strategy
        with torch.no_grad():
            token_probs = torch.log_softmax(model(batch_tokens.cuda())['logits'], dim=-1)

        # Put results in a dataframe
        results.append(
            pd.DataFrame.from_records(
                [
                    [label, a, aa] + token_probs[b, a+1, :].tolist()
                    for b, label in enumerate(batch_labels)
                    for a, aa in enumerate(batch_strs[b])
                ],
                columns=['chunk', 'pos', 'ref'] + alphabet.all_toks,
                index = ['chunk', 'pos']
            )
        )

        print(
            f'It took {default_timer() - start_time} seconds '
            f'to process {len(batch_labels)} sequence chunks.'
        )

    result = pd.concat(results)
    result['model'] = model_name
    result.set_index('model', append=True)

    return result


def mask_token_tensor(token_sequence, alphabet, position):
    result = token_sequence.clone()
    result[0, position] = alphabet.mask_idx
    return result

def run_masked_marginals_model(model_location, chunk_list):

    start_time = default_timer()
    print('Loading model')

    # Get model name
    model_name = Path(model_location).stem if model_location.endswith('.pt') else model_location

    # Load model
    model, alphabet = pretrained.load_model_and_alphabet(model_location)
    model.eval()

    if torch.cuda.is_available():
        model = model.cuda()
        print("Transferred model to GPU")

    print(f'It took {default_timer() - start_time} seconds to load the model.')

    batch_converter = alphabet.get_batch_converter()

    results = {}
    # We'll compute one sequence at a time
    for seq_id, seq_aas in tqdm(chunk_list):

        batch_labels, batch_strs, batch_tokens = batch_converter([(seq_id, seq_aas)])

        # Make masked matrix
        tokens_masked = torch.cat([
            mask_token_tensor(batch_tokens, alphabet, i)
            for i in range(batch_tokens.size(1))
        ])

        if torch.cuda.is_available():
            tokens_masked = tokens_masked.cuda()
        
        with torch.no_grad():
            token_probs = torch.log_softmax(model(tokens_masked)['logits'], dim=-1)
        
        # The result is an S x S x V tensor of probabilities with
        # Sequence length S
        # Vocabulary size V
        # On row n, the nth token is masked.
        # The masked marginals scores of the substitutions of the nth token are
        # given by the tensor slice at [n,n,:] minus the value at [n,n,w] where
        # w is the vocabulary index of the original token.
        
        # Put results in a dataframe
        results[seq_id] = pd.DataFrame.from_records(
            [
                [a, aa] + (token_probs[a+1, a+1, :] - token_probs[a+1, a+1, alphabet.get_idx(aa)]).tolist()
                for a, aa in enumerate(seq_aas)
            ],
            columns=['pos', 'ref'] + alphabet.all_toks,
            index = ['pos', 'ref']
        )

    result = pd.concat(results, names = ['chunk'])

    print(f'It took {default_timer() - start_time} to generate predictions.')

    result['model'] = model_name
    result.set_index('model', append=True)

    return result


def main(args):

    # Select scoring method
    run_model = {
        'wt-marginals': run_wt_marginals_model,
        'masked-marginals': run_masked_marginals_model
    }[args.scoring_strategy]

    # Read (possibly gzipped) fasta
    if args.sequences.suffix == '.gz':
        with gzip.open(args.sequences, 'rt') as in_handle:
            seq_list = SeqIO.parse(in_handle, 'fasta')
    else:
        seq_list = SeqIO.parse(args.sequences, 'fasta')

    # Break sequences up into digestible chunks
    chunk_list = chunk_sequences(seq_list)

    # Produce results and collate:
    pd.concat([
        run_model(model_location, chunk_list)
        for model_location in args.model_location
    ]).to_csv(args.results)

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    main(args)