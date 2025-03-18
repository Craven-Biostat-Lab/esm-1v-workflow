#!/bin/bash

# Command for submitting results to the IGVF portal
# Must be done in an environment with igvf_utils installed
# Must have the environment variables IGVF_API_KEY and IGVF_SECRET_KEY set.

ask() {
    read -p "$1 (y/N/a): " response
    case "$response" in
        [Yy]* ) return 0;;
        [Aa]* ) echo "Abort received, exiting script."; exit 1;;
        * ) return 1;;
    esac
}

MODE=prod
#MODE=sandbox

echo "Mode is $MODE"

if ask "Submit documentation?"; then

    iu_register.py \
        -m $MODE \
        -p document \
        -i esm-1v-documentation.json
fi

if ask "Submit software?"; then

    iu_register.py \
        -m $MODE \
        -p software \
        -i esm-1v-software.json
fi

if ask "Submit software version?"; then

    iu_register.py \
        -m $MODE \
        -p software_version \
        -i esm-1v-software-version.json
fi

if ask "Submit model set?"; then

    iu_register.py \
        -m $MODE \
        -p model_set \
        -i esm-1v-model-set.json
fi

if ask "Submit model files?"; then

    iu_register.py \
        -m $MODE \
        -p model_file \
        -i esm-1v-model-files.json \
        --no-upload-file
fi

if ask "Submit workflow?"; then

    iu_register.py \
        -m $MODE \
        -p workflow \
        -i esm-1v-workflow.json
fi

if ask "Submit analysis step?"; then

    iu_register.py \
        -m $MODE \
        -p analysis_step \
        -i esm-1v-analysis-step.json
fi

if ask "Submit analysis step version?"; then

    iu_register.py \
        -m $MODE \
        -p analysis_step_version \
        -i esm-1v-analysis-step-version.json
fi

if ask "Submit prediction set?"; then

    iu_register.py \
        -m $MODE \
        -p prediction_set \
        -i esm-1v-prediction-set.json
fi

if ask "Submit prediction files?"; then

    iu_register.py \
        -m $MODE \
        -p tabular_file \
        -i esm-1v-prediction-file.json
fi

echo "Done!"

# Explanation of arguments;
# -m (mode) is either sandbox or prod (for production)
# -p (profile) is the type of object being submitted
# -i is the metadata file
# -d for dry-run
