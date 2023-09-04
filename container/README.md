# Apptainer build files

Files needed to build the apptainer containers live here.

The command to build a container with the esm1v_t33_650M_UR90S_1 model is
```
apptainer build --build-arg MODEL=esm1v_t33_650M_UR90S_1.pt container.sif container.def
```

## Details of interest in `container.def`

To avoid having to download the models every time the container is invoked, we load the model into the container explicitly (see the `%files` section). For the files to be available at container build time make sure that they are downloaded to `container/esm_models` (the `download-models.sh` script will download them there).

## Running the container

The `predict_substitution.py` is used as the runscript of the container.
When invoked as the container runscript, the `--model-location` argument is set to the model included in the container.
The other arguments are:
* `--sequences`: A path to a (optionally gzipped) FASTA file containing the sequences we wish to process.
* `--results`: A path where the results will be written as CSV.
* `--scoring-strategy`: The scoring strategy to use. Current options are `masked-marginals` (default) and `wt-marginals`.

## Troubleshooting

A "No space left on device" error can happen for various reasons when building an image.

### Lack of space in the temporary build directory

The default `/tmp` device might not have the space required.
A workaround is to set the environment variable `APPTAINER_TMPDIR` to a device with sufficient space.

### [Apptainer issue 1076](https://github.com/apptainer/singularity/issues/1076)

A workaround is to build in sandbox first:
```
apptainer build --build-arg MODEL=esm1v_t33_650M_UR90S_1.pt --sandbox sandbox/ container.def
apptainer build container.sif sandbox/
```