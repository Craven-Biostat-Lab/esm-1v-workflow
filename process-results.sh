# Process results shell script
# Intended to be called by condor submit file

/ua/yuriy/mambaforge/envs/esm-1v-processing/bin/python process-results.py \
    --source chtc/proteins/missing-mane/missing-mane/bundle_${1}_m*.csv \
    --output-dir results/processed-mane \
    --overwrite