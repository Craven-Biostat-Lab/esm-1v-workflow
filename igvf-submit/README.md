# ESM-1v predictions submitted to the IGVF portal

Here we describe our submission of the ESM-1v predictions.

The main product of the submission is predictions for all single amino acid substitutions across all MANE transcripts.
The predictions are organized in prediction sets grouped by gene.

## Portal objects:

- **prediction file**: TSV file for all predictions on a given protein (specific ENSP ID). Links to:
    - **prediction file set**
    - **format specification**: Document describing format. We use our documentation object for this.
- **prediction file set**: Group of prediction files for a given gene (specific ENSG ID). Links to:
    - **documents**: We link to our documentation object.
- **documentation**: PDF generated from `ESM-1v Predictions Documentation.md`
- **model file**: A specific ESM-1v weight file. Link to **moel set**
- **model set**: Represents ESM-1v. Links to:
    - **software version**
    - **external input data** (do we want this?)
- **software version**: version of this repository.
    - Links to **software**.
    - Links to this repository.
    - References commit ID.
- **software**: this repository.

## Submission notes

Errored out on "'ENSG00000288626' not found"