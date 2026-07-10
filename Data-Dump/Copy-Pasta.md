Prompt ->
A professional presenter faces the camera and speaks calmly in a measured, conversational manner. Neutral relaxed facial expression. Subtle natural lip articulation with restrained jaw movement. Minimal facial expressions, occasional natural blinking, and very small natural head movements. The head remains mostly stable and centered. Static locked camera, medium close-up, soft even studio lighting.

```Dockerfile
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


# ---------------------------------------------------------
# Custom nodes
# ---------------------------------------------------------

RUN git clone --depth=1 \
    https://github.com/kijai/ComfyUI-WanVideoWrapper.git \
    /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper \
 && git clone --depth=1 \
    https://github.com/rgthree/rgthree-comfy.git \
    /workspace/ComfyUI/custom_nodes/rgthree-comfy \
 && git clone --depth=1 \
    https://github.com/kijai/ComfyUI-KJNodes.git \
    /workspace/ComfyUI/custom_nodes/ComfyUI-KJNodes \
 && git clone --depth=1 \
    https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git \
    /workspace/ComfyUI/custom_nodes/ComfyUI-VideoHelperSuite \
 && git clone --depth=1 \
    https://github.com/DemonGatanjieu/Anomalous_Model_Browser.git \
    /workspace/ComfyUI/custom_nodes/Anomalous_Model_Browser


# ---------------------------------------------------------
# Custom node dependencies
# ---------------------------------------------------------

RUN uv pip install \
    -r /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/requirements.txt \
 && uv pip install \
    -r /workspace/ComfyUI/custom_nodes/rgthree-comfy/requirements.txt \
 && uv pip install \
    -r /workspace/ComfyUI/custom_nodes/ComfyUI-KJNodes/requirements.txt \
 && uv pip install \
    -r /workspace/ComfyUI/custom_nodes/ComfyUI-VideoHelperSuite/requirements.txt


# ---------------------------------------------------------
# FlashAttention 2 prebuilt wheel
# Avoids source compilation and wheel-build loops.
# ---------------------------------------------------------

RUN set -eux; \
    ABI="$(python -c 'import torch; print("TRUE" if torch._C._GLIBCXX_USE_CXX11_ABI else "FALSE")')"; \
    WHEEL="flash_attn-2.8.3.post1+cu12torch2.8cxx11abi${ABI}-cp312-cp312-linux_x86_64.whl"; \
    URL="https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3.post1/${WHEEL}"; \
    uv pip install --no-deps "${URL}"; \
    python -c "import torch, flash_attn; print('Torch:', torch.__version__); print('CUDA:', torch.version.cuda); print('FlashAttention:', flash_attn.__version__)"


RUN mkdir -p \
    /workspace/storage \
    /workspace/ComfyUI/models \
    /workspace/ComfyUI/input \
    /workspace/ComfyUI/output \
    /workspace/ComfyUI/user/default/workflows

VOLUME ["/workspace/storage", "/workspace/ComfyUI/models", "/workspace/ComfyUI/input", "/workspace/ComfyUI/output", "/workspace/ComfyUI/user/default/workflows"]

WORKDIR /workspace/ComfyUI

EXPOSE 8188

CMD ["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"]
```
