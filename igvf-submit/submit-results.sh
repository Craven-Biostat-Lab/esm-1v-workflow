# Command for submitting results to the IGVF portal
# Must be done in an environment with igvf_utils installed
# Must have the environment variables IGVF_API_KEY and IGVF_SECRET_KEY set.

# Submit documentation
if false; then
    iu_register.py \
        -m sandbox \
        -p document \
        -i esm-1v-documentation.json
fi

# Submit software
if false; then
    iu_register.py \
        -m sandbox \
        -p software \
        -i esm-1v-software.json
fi

# Submit software version
if false; then
    iu_register.py \
        -m sandbox \
        -p software_version \
        -i esm-1v-software-version.json
fi

# Submit model set
if false; then
    iu_register.py \
        -m sandbox \
        -p model_set \
        -i esm-1v-model-set.json
fi

# Submit model files
if false; then
    iu_register.py \
        -m sandbox \
        -p model_file \
        -i esm-1v-model-files-test.json
fi

# Submit prediction sets
if false; then
    iu_register.py \
        -m sandbox \
        -p prediction_set \
        -i esm-1v-fileset-metadata.txt
fi

# Submit prediction files
if true; then
    iu_register.py \
        -m sandbox \
        -p tabular_file \
        -i esm-1v-files-metadata.txt
fi

# Explanation of arguments;
# -m (mode) is either sandbox or prod (for production)
# -p (profile) is the type of object being submitted
# -i is the metadata file
# -d for dry-run
