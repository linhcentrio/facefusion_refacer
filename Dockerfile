# Sử dụng base image mới nhất với CUDA và cuDNN
FROM nvidia/cuda:12.9.1-cudnn-runtime-ubuntu24.04

# Thiết lập biến môi trường cho FaceFusion
ARG FACEFUSION_VERSION=3.3.0
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV PIP_BREAK_SYSTEM_PACKAGES=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/facefusion"
ENV CUDA_VISIBLE_DEVICES=0
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV OMP_NUM_THREADS=1

# Thiết lập thư mục làm việc
WORKDIR /facefusion

# Cài đặt các phụ thuộc hệ thống
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-dev \
    python3-distutils \
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

# Clone FaceFusion từ GitHub
RUN git clone https://github.com/facefusion/facefusion.git --branch ${FACEFUSION_VERSION} --single-branch .

# Cài đặt các phụ thuộc cho FaceFusion
RUN python3 install.py --onnxruntime cuda --skip-conda

# Cài đặt các phụ thuộc bổ sung cho RunPod
RUN pip install runpod>=1.6.0 minio>=7.0.0 requests

# Tải xuống tất cả các mô hình cần thiết
RUN python3 facefusion.py --command force-download

# Sao chép script xử lý
COPY facefusion_handler.py /facefusion/

# Kiểm tra sức khỏe
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import torch; assert torch.cuda.is_available()" || exit 1

# Khởi động handler
CMD ["python3", "facefusion_handler.py"]
