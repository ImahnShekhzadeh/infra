# Start from a CUDA image with full development environment
FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04

# Install `conda` (not present in CUDA image)
# Use of miniconda since full anaconda distribution not needed
ENV MINICONDA_VERSION Miniconda3-latest-Linux-x86_64.sh
ENV MINICONDA_SHA_256 \
43651393236cb8bb4219dcd429b3803a60f318e5507d8d84ca00dafa0c69f1bb

RUN apt-get update && apt-get install -y curl && \
    curl -O https://repo.anaconda.com/miniconda/$MINICONDA_VERSION && \
    /bin/bash $MINICONDA_VERSION -b -p /opt/conda && \
    rm $MINICONDA_VERSION && \
    apt-get clean

# Add `conda` to path
# Initialize `conda`
# Install specific python version
# Update `conda`
# Install `pip` via `conda`
ENV PATH /opt/conda/bin:$PATH
RUN conda init bash
RUN conda install -y python=3.10.3
RUN conda update -n base -c defaults conda
RUN conda install -c conda-forge pip

# Install PyTorch (with CUDA support for 12.1) using `conda`
# CUDA 12.1 is the latest version supported by PyTorch, 
# should also work for CUDA 12.2
RUN conda install -y pytorch=2.1.* torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia

# Install JAX with CUDA support using `pip` via `conda`
# `-v` flag is for verbose output
# When I use "jax[cuda12_pip]", I get a version mismatch with cuPI
#RUN python --version && pip install -v --upgrade\
#    jax\
#    jaxlib==0.4.20+cuda11.cudnn86\
#    -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
RUN pip install --upgrade "jax[cuda11_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

# Set the working directory
WORKDIR /app

# Copy all python scripts in `test_scripts_nbs` and `pyproject.toml` into
# docker container
COPY setup.py .
COPY pyproject.toml .
COPY run_scripts.sh .

# Install packages in `pyproject.toml` via `pip`
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e .

# Make port 80 available to the world outside this container
EXPOSE 80

# Ensure `run_scripts.sh` is executable
RUN chmod +x ./run_scripts.sh

# Execute `run_scripts.sh` as the entrypoint
ENTRYPOINT ["./run_scripts.sh"]

# Run the script (explicitly use `python3` to avoid any confusion)
# Script is only run when the container is run
# CMD ["python3", "-B", "test_script.py"]