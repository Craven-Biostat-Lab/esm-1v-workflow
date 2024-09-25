# Command for submitting results to the IGVF portal
# Must be done in an environment with igvf_utils installed
# Must have the environment variables IGVF_API_KEY and IGVF_SECRET_KEY set.

# Submit documentation
iu_register.py -d \
    -m sandbox \
    -p document \
    -i esm-1v-documentation.json

# Patch the already submitted prediction set
iu_register.py -d \
    -m sandbox \
    -p prediction_set \
    -i esm-1v-predictions.json \
    --patch

# Submit files
iu_register.py \
    -m sandbox \
    -p tabular_file \
    -i esm-1v-files-metadata.txt

# Explanation of arguments;
# -m (mode) is either sandbox or prod (for production)
# -p (profile) is the type of object being submitted
# -i is the metadata file
# -d for dry-run
