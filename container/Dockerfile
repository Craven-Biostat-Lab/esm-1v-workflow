FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

COPY predict.py /python_scripts/predict.py
COPY esm_models esm_models

RUN pip install fair-esm pandas tqdm Bio --no-warn-script-location

ENTRYPOINT ["python", "/python_scripts/predict.py", "--model-location", \
    "/esm_models/esm1v_t33_650M_UR90S_1.pt", \
    "/esm_models/esm1v_t33_650M_UR90S_2.pt" \
    "/esm_models/esm1v_t33_650M_UR90S_3.pt" \
    "/esm_models/esm1v_t33_650M_UR90S_4.pt" \
    "/esm_models/esm1v_t33_650M_UR90S_5.pt"]