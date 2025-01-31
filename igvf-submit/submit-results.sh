#!/bin/bash

# Command for submitting results to the IGVF portal
# Must be done in an environment with igvf_utils installed
# Must have the environment variables IGVF_API_KEY and IGVF_SECRET_KEY set.

confirm() {
    read -p "$1 (y/n): " response
    if [[ "$response" != "y" ]]; then
        echo "Exiting script."
        exit 1
    fi
}

MODE=prod

echo "Mode is $MODE"
confirm Continue

# Submit documentation
if false; then

    confirm "Submit documentation?"

    iu_register.py \
        -m $MODE \
        -p document \
        -i esm-1v-documentation.json
fi

# Submit software
if false; then

    confirm "Submit software?"

    iu_register.py \
        -m $MODE \
        -p software \
        -i esm-1v-software.json
fi

# Submit software version
if false; then

    confirm "Submit software version?"

    iu_register.py \
        -m $MODE \
        -p software_version \
        -i esm-1v-software-version.json
fi

# Submit model set
if false; then

    confirm "Submit model set?"

    iu_register.py \
        -m $MODE \
        -p model_set \
        -i esm-1v-model-set.json
fi

# Submit model files
if false; then

    confirm "Submit model files?"

    iu_register.py \
        -m $MODE \
        -p model_file \
        -i esm-1v-model-files.json
fi

# Submit prediction sets
if true; then

    confirm "Submit prediction set?"

    iu_register.py \
        -m $MODE \
        -p prediction_set \
        -i esm-1v-fileset-metadata.txt
fi

# Submit prediction files
if true; then

    confirm "Submit prediction files?"

    iu_register.py \
        -m $MODE \
        -p tabular_file \
        -i esm-1v-files-metadata.txt
fi

echo "Done!"

# Explanation of arguments;
# -m (mode) is either sandbox or prod (for production)
# -p (profile) is the type of object being submitted
# -i is the metadata file
# -d for dry-run
