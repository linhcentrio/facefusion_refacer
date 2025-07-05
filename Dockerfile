FROM nvidia/cuda:12.9.1-cudnn-runtime-ubuntu24.04

ARG FACEFUSION_VERSION=3.1.0
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV PIP_BREAK_SYSTEM_PACKAGES=1
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
RUN ln -sf /usr/bin/python3.10 /usr/bin/python

# Clone FaceFusion
RUN git clone https://github.com/facefusion/facefusion.git --branch ${FACEFUSION_VERSION} --single-branch .

# Install FaceFusion dependencies
RUN python install.py --onnxruntime cuda --skip-conda

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
