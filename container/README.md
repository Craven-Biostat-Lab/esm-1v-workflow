# Apptainer build files

Files needed to build the apptainer container live here.

The command to build the container is
```
apptainer build container.sif container.def
```

For those running into the "No space left on device" error during build ([apptainer issue 1076](https://github.com/apptainer/singularity/issues/1076)), a workaround is to build in sandbox first:
```
apptainer build --sandbox sandbox/ container.def
apptainer build container.sif sandbox/
```

## Details of interest in `container.def`

To avoid having to download the models every time the container is invoked, make sure that downloaded models are copied to the container (in the `%files` section) and correctly specified in the arguments in `%runscript`.

## Running the container

The `predict.py` script from the [zero shot variant prediction example](https://github.com/facebookresearch/esm/tree/main/examples/variant-prediction) is copied here and used as the runscript of the container.
The command arguments (other than the model locations) are passed directly to the script.