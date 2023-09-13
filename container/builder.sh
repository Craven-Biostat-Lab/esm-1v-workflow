export APPTAINER_TMPDIR=/scratch/yuriy/tmp/
apptainer build --build-arg MODEL=esm1v_t33_650M_UR90S_1.pt build/model1v3.sif container.def
apptainer build --build-arg MODEL=esm1v_t33_650M_UR90S_2.pt build/model2v3.sif container.def
apptainer build --build-arg MODEL=esm1v_t33_650M_UR90S_3.pt build/model3v3.sif container.def
apptainer build --build-arg MODEL=esm1v_t33_650M_UR90S_4.pt build/model4v3.sif container.def
apptainer build --build-arg MODEL=esm1v_t33_650M_UR90S_5.pt build/model5v3.sif container.def
