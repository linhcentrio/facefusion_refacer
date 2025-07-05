# Base image với CUDA và cuDNN
FROM nvidia/cuda:12.6.3-cudnn9-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/facefusion"
ENV CUDA_VISIBLE_DEVICES=0
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV OMP_NUM_THREADS=1

WORKDIR /facefusion

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3.10-distutils \
    python3-pip \
    build-essential \
    git \
    curl \
    wget \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Install miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh
ENV PATH="/opt/conda/bin:$PATH"

# Clone FaceFusion
RUN git clone https://github.com/facefusion/facefusion.git --branch 3.1.0 --single-branch .

# Create conda environment
RUN conda create --prefix ./venv python=3.10 -y
ENV PATH="/facefusion/venv/bin:$PATH"

# Install CUDA dependencies
RUN conda install -c conda-forge cuda-runtime=12.6.3 cudnn=9.3.0.75 -y

# Install TensorRT
RUN pip install tensorrt==10.6.0 --extra-index-url https://pypi.nvidia.com

# Install FaceFusion dependencies
RUN python install.py --onnxruntime cuda

# Install additional dependencies for RunPod
RUN pip install runpod>=1.6.0 minio>=7.0.0 requests

# Download all models
RUN python facefusion.py --command force-download

# Copy handler script
COPY facefusion_handler.py /facefusion/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import torch; assert torch.cuda.is_available()" || exit 1

# Start handler
CMD ["python", "facefusion_handler.py"]
