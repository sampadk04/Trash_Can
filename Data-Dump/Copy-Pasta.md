Prompt ->
A professional presenter faces the camera and speaks calmly in a measured, conversational manner. Neutral relaxed facial expression. Subtle natural lip articulation with restrained jaw movement. Minimal facial expressions, occasional natural blinking, and very small natural head movements. The head remains mostly stable and centered. Static locked camera, medium close-up, soft even studio lighting.

Dockerfile
```
FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04

WORKDIR /workspace

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CUDA_HOME=/usr/local/cuda \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:/root/.local/bin:$PATH"

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    python-is-python3 \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsndfile1 \
    ninja-build \
 && rm -rf /var/lib/apt/lists/* \
 && curl -LsSf https://astral.sh/uv/install.sh | sh

RUN uv venv /opt/venv

RUN uv pip install \
    pip \
    setuptools \
    wheel \
    packaging \
    ninja

RUN uv pip install \
    --index-url https://download.pytorch.org/whl/cu128 \
    torch==2.8.0 \
    torchvision==0.23.0 \
    torchaudio==2.8.0

RUN git clone --depth=1 \
    https://github.com/Comfy-Org/ComfyUI.git \
    /workspace/ComfyUI

RUN uv pip install -r /workspace/ComfyUI/requirements.txt

# FlashAttention 2 prebuilt wheel.
# Avoids source compilation and wheel-build loops.
RUN set -eux; \
    ABI="$(python -c 'import torch; print("TRUE" if torch._C._GLIBCXX_USE_CXX11_ABI else "FALSE")')"; \
    WHEEL="flash_attn-2.8.3.post1+cu12torch2.8cxx11abi${ABI}-cp312-cp312-linux_x86_64.whl"; \
    URL="https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3.post1/${WHEEL}"; \
    uv pip install --no-deps "${URL}"

RUN mkdir -p \
    /workspace/storage \
    /workspace/ComfyUI/models \
    /workspace/ComfyUI/input \
    /workspace/ComfyUI/output \
    /workspace/ComfyUI/user/default/workflows

VOLUME [
    "/workspace/storage",
    "/workspace/ComfyUI/models",
    "/workspace/ComfyUI/input",
    "/workspace/ComfyUI/output",
    "/workspace/ComfyUI/user/default/workflows"
]

WORKDIR /workspace/ComfyUI

EXPOSE 8188

CMD [
    "python",
    "main.py",
    "--listen",
    "0.0.0.0",
    "--port",
    "8188"
]
```

docker-compose.yml file
```
services:
  skyreelsv3-comfyui:
    image: skyreelsv3-comfyui:v1
    container_name: skyreelsv3-comfyui

    build:
      context: .
      dockerfile: Dockerfile

    ports:
      - "8188:8188"

    volumes:
      - ./storage:/workspace/storage
      - ./storage-models/models:/workspace/ComfyUI/models
      - ./storage-user/input:/workspace/ComfyUI/input
      - ./storage-user/output:/workspace/ComfyUI/output
      - ./storage-user/workflows:/workspace/ComfyUI/user/default/workflows

    environment:
      NVIDIA_VISIBLE_DEVICES: all
      NVIDIA_DRIVER_CAPABILITIES: compute,utility
      PYTORCH_CUDA_ALLOC_CONF: expandable_segments:True

    stdin_open: true
    tty: true

    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities:
                - gpu
```
