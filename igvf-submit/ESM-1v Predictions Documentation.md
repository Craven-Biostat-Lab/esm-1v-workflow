# ESM-1v predictions for all AA substitutions in all MANE proteins

This prediction set contains ESM-1v one-shot protein function predictions for all amino acid (AA) substitutions in MANE proteins.
Specifically, MANE version 1.2 ([link to AA sequence FASTA file](https://ftp.ncbi.nlm.nih.gov/refseq/MANE/MANE_human/release_1.2/MANE.GRCh38.v1.2.ensembl_protein.faa.gz)).

## File format

The predictions are provided as a collection of `.tsv` (tab-separated value) files, one file per unique Ensembl Peptide (ENSP) ID.
Each file starts with a header row.
Columns are expected but not guaranteed to appear in the order listed here.
Refer to the header row for an accurate ordering of columns within a particular file.
The columns are as follows:

* **HGVS**: A description of the AA change following the [HGVS](https://varnomen.hgvs.org/recommendations/protein/variant/substitution/) standard as closely as reasonable, specifically:
    * Values in this column are a string of the form `{sequence}:p.{ref}{pos}{alt}`, e.g. `ENSP00000005226.7:p.Val772Ala` where
        * `{sequence}` is the ENSP ID of the protein (e.g. `ENSP00000005226.7`).
        * `{ref}` is the three-letter abbreviation of the AA that appears in the reference sequence at the substitution position (e.g. `Val`).
        * `{pos}` is the one-indexed substitution position as an integer (e.g. `772`).
        * `{alt}` is the three-letter abbreviation of the substituting AA (e.g. `Ala`).
    * Contrary to HGVS recommendation, these variants are not described at the DNA level. These are in-silico predictions of protein stability that depend solely on AA sequences and are agnostic of DNA and other context.
    * The HGVS recommendation for predicted consequences is to use parentheses notation (e.g. `ENSP00000005226.7:p.(Val772Ala)`), we do not do this because the amino acid substitutions are neither predicted, nor are they consequences of anything, nor are they observed.
* **esm1v_t33_650M_UR90S_1**: the masked-marginals score for the substitution yielded by the esm1v_t33_650M_UR90S_1 model. If this position is an overlap between two segments of a long sequence, then this is the score for the *prior segment* (see "Long sequences" subsection below for details).
* **esm1v_t33_650M_UR90S_2**: (prior segment) masked-marginals score by esm1v_t33_650M_UR90S_2.
* **esm1v_t33_650M_UR90S_3**: (prior segment) masked-marginals score by esm1v_t33_650M_UR90S_3.
* **esm1v_t33_650M_UR90S_4**: (prior segment) masked-marginals score by esm1v_t33_650M_UR90S_4.
* **esm1v_t33_650M_UR90S_5**: (prior segment) masked-marginals score by esm1v_t33_650M_UR90S_5.
* **esm1v_t33_650M_UR90S_1_next**: the masked-marginals score for the substitution yielded by the esm1v_t33_650M_UR90S_1 model for the *later segment* in an overlap between two segments of a long sequence (see "Long sequences" subsection below for details). This column is only present in files of long sequences (proteins of more than 1022 amino acids). Even when this column is present, values in this column are present only in overlaps.
* **esm1v_t33_650M_UR90S_2_next**: (later segment) masked-marginals score by esm1v_t33_650M_UR90S_2.
* **esm1v_t33_650M_UR90S_3_next**: (later segment) masked-marginals score by esm1v_t33_650M_UR90S_3.
* **esm1v_t33_650M_UR90S_4_next**: (later segment) masked-marginals score by esm1v_t33_650M_UR90S_4.
* **esm1v_t33_650M_UR90S_5_next**: (later segment) masked-marginals score by esm1v_t33_650M_UR90S_5.
* **combined_score**: A combined score that represents the ultimate protein stability prediction for this set of 5 models. Outside of regions of overlap and in the first 20 positions of an overlap, this is the average of the 5 *prior segment* model scores. In the last 20 position of an overlap, this is the average of the 5 *later segment* model scores. Between the 20th and 80th position of an overlap, this is a weighted average of the two averages, governed by a cosine sigmoid (see "Combining scores" for details).

## Model information

The code to run the prediction task, generate containers for running the computation, and process the results to produce the included tables can be found in [this GitHub repository](https://github.com/Craven-Biostat-Lab/esm-1v-workflow/tree/first-run).

The trained models themselves that we used to generate the one-shot predictions downloadable here:
[esm1v_t33_650M_UR90S_1](https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_1.pt),
[esm1v_t33_650M_UR90S_2](https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_2.pt),
[esm1v_t33_650M_UR90S_3](https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_3.pt),
[esm1v_t33_650M_UR90S_4](https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_4.pt),
[esm1v_t33_650M_UR90S_5](https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_5.pt).

The ESM-1v models are described in [Language models enable zero-shot prediction of the effects of mutations on protein function. (Meier et al. 2021)](https://doi.org/10.1101/2021.07.09.450648).

### The masked-marginals score

As mentioned in Meier et al., there are several possible approaches to obtaining a score from the ESM-1v model, and the masked marginals approach was shown to be best.
We introduce the mask token at the substitution position and compute the score by considering the probability of the substitution relative to the reference amino acid:

$$ \log p( x_i = x_i^v | x_{-i} ) - \log p( x_i = x_i^r | x_{-i} ) $$

Where $x^v$ and $x^r$ are the variant and reference sequences respectively, $x_{-i}$ represents the sequence $x$ with position $i$ masked, and $i$ is the substitution position.

### Long sequences

The ESM-1v models are limited to sequences of at most 1022 AAs.
Since longer proteins comprise a non-negligible proportion of the proteome, we break up longer AA sequences into overlapping segments, make predictions at every position of each segment, and combine results.

Toy example for illustration only:
```
Full sequence:
MPLYSVTVKWGKEKFEGVELNTDEPPMVFKAQLFALTGVQP

Segments:
[        Prior Segment       ]
MPLYSVTVKWGKEKFEGVELNTDEPPMVFK
                   [ Overlap ]
                   LNTDEPPMVFKAQLFALTGVQP
                   [   Later Segment    ]                              
```
The example above shows how a protein composed of a sequence of 41 AAs would be segmented into overlapping segments of at most 30 AAs with an overlap of 11 AAs.

In reality, we segment proteins into segments of at most 1022 AAs with an overlap of 100 AAs.
In a region of overlap, we call the segment that ends with the overlap the *prior segment*, and the region that begins with the overlap the *later segment*.
The n-th segment of a sequence covers (1-indexed) positions $922\times(n-1)+1$ through $922\times(n-1) + 1022$ of the full sequence.

### Combining scores

Every possible substitution in each segment is scored by the 5 ESM models.
We take the average of these scores to be the score of the substitution in the segment.
In non-overlapping regions of segments, this is also the final score (`combined_score`) we report for the substitution.
In regions of overlap, we use a cosine sigmoid weight to combine the scores from the two overlapping segments, so that towards the beginning of the overlap we use the *prior segment*'s score, and toward the end we use the *later segment*'s score.
Specifically:

$$ S_{combined} = w(p) S_{prior} + (1-w(p)) S_{later} $$

where $w(p)$ is the cosine sigmoid weight

$$ w(p) = \begin{cases}
1 & p < 0.2 \\
\dfrac{1 + \cos \left( \frac{p - 0.2}{0.6} \pi \right)}{2} & 0.2 \leq p \leq 0.8 \\
0 & p > 0.8 \end{cases} $$

and
$$ p = \dfrac{\text{substitution position} - \text{start position of overlap}}{\text{length of overlap}} $$
is the relative position of the substitution in the overlap.
