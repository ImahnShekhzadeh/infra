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

# Add `conda` to path; initialize `conda`, install specific python version, 
# update `conda` and install `pip` via `conda`
ENV PATH /opt/conda/bin:$PATH
RUN conda init bash && \
    conda install -y python=3.10.3 && \
    conda update -n base -c defaults conda && \
    conda install -c conda-forge pip

# Install PyTorch with CUDA support for 12.1 using `conda`
RUN conda install -y pytorch=2.1.* torchvision torchaudio pytorch-cuda=12.1 \
    -c pytorch -c nvidia

# Install JAX with CUDA support using `pip`
RUN pip install --upgrade\
    jax==0.4.23\
    jaxlib==0.4.23+cuda12.cudnn89\
    -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

# Set the working directory
WORKDIR /app

# Copy files into docker container
COPY setup.py .
COPY pyproject.toml .
COPY run_scripts.sh .

# Install packages in `pyproject.toml` via `pip`
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e .

# Ensure `run_scripts.sh` is executable
RUN chmod +x ./run_scripts.sh

# Execute `run_scripts.sh` as the entrypoint
ENTRYPOINT ["./run_scripts.sh"]