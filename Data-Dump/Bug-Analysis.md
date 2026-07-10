Bug Report ->
```
(python3) [ec2-user@ip-172-16-16-153 docker-root]$ docker-compose up
[+] Running 1/1
 ! skyreelsv3-comfyui Warning                                                                                                                                                                                                                              2.0s 
[+] Building 27.1s (17/17) FINISHED                                                                                                                                                                                                                             
 => [skyreelsv3-comfyui internal] load build definition from Dockerfile                                                                                                                                                                                    0.0s
 => => transferring dockerfile: 3.72kB                                                                                                                                                                                                                     0.0s
 => [skyreelsv3-comfyui internal] load metadata for docker.io/nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04                                                                                                                                                   1.1s
 => [skyreelsv3-comfyui internal] load .dockerignore                                                                                                                                                                                                       0.0s
 => => transferring context: 2B                                                                                                                                                                                                                            0.0s
 => [skyreelsv3-comfyui  1/13] FROM docker.io/nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04@sha256:24c8e3581ea6330038b0d374920721983312627f8adbfcf390bdb4b399d280ed                                                                                           0.0s
 => CACHED [skyreelsv3-comfyui  2/13] WORKDIR /workspace                                                                                                                                                                                                   0.0s
 => CACHED [skyreelsv3-comfyui  3/13] RUN apt-get update  && apt-get install -y --no-install-recommends     git     curl     build-essential     python3     python3-dev     python3-pip     python3-venv     python-is-python3     ffmpeg     libgl1      0.0s
 => CACHED [skyreelsv3-comfyui  4/13] RUN uv venv /opt/venv                                                                                                                                                                                                0.0s
 => CACHED [skyreelsv3-comfyui  5/13] RUN uv pip install     pip     setuptools     wheel     packaging     ninja                                                                                                                                          0.0s
 => CACHED [skyreelsv3-comfyui  6/13] RUN uv pip install     --index-url https://download.pytorch.org/whl/cu128     torch==2.8.0     torchvision==0.23.0     torchaudio==2.8.0                                                                             0.0s
 => CACHED [skyreelsv3-comfyui  7/13] RUN git clone --depth=1     https://github.com/Comfy-Org/ComfyUI.git     /workspace/ComfyUI                                                                                                                          0.0s
 => CACHED [skyreelsv3-comfyui  8/13] RUN uv pip install -r /workspace/ComfyUI/requirements.txt                                                                                                                                                            0.0s
 => [skyreelsv3-comfyui  9/13] RUN git clone --depth=1     https://github.com/kijai/ComfyUI-WanVideoWrapper.git     /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper  && git clone --depth=1     https://github.com/rgthree/rgthree-comfy.git       6.3s
 => [skyreelsv3-comfyui 10/13] RUN uv pip install     -r /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/requirements.txt  && uv pip install     -r /workspace/ComfyUI/custom_nodes/rgthree-comfy/requirements.txt  && uv pip install     -r /wor  4.3s
 => [skyreelsv3-comfyui 11/13] RUN set -eux;     ABI="$(python -c 'import torch; print("TRUE" if torch._C._GLIBCXX_USE_CXX11_ABI else "FALSE")')";     WHEEL="flash_attn-2.8.3.post1+cu12torch2.8cxx11abi${ABI}-cp312-cp312-linux_x86_64.whl";     URL="  13.1s 
 => [skyreelsv3-comfyui 12/13] RUN mkdir -p     /workspace/storage     /workspace/ComfyUI/models     /workspace/ComfyUI/input     /workspace/ComfyUI/output     /workspace/ComfyUI/user/default/workflows                                                  0.4s 
 => [skyreelsv3-comfyui 13/13] WORKDIR /workspace/ComfyUI                                                                                                                                                                                                  0.0s 
 => [skyreelsv3-comfyui] exporting to image                                                                                                                                                                                                                1.8s 
 => => exporting layers                                                                                                                                                                                                                                    1.8s 
 => => writing image sha256:e294f92147cf913eaec6093d313639692e4d4306a8e7b1a0d2fb514a555b0266                                                                                                                                                               0.0s 
 => => naming to docker.io/library/skyreelsv3-comfyui:v1                                                                                                                                                                                                   0.0s 
WARN[0029] Found orphan containers ([skyreels-v3 comfyui-longcat-base]) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up. 
[+] Running 1/1
 ✔ Container skyreelsv3-comfyui  Recreated                                                                                                                                                                                                                 0.2s 
Attaching to skyreelsv3-comfyui
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | ==========
skyreelsv3-comfyui  | == CUDA ==
skyreelsv3-comfyui  | ==========
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | CUDA Version 12.8.1
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | Container image Copyright (c) 2016-2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | This container image and its contents are governed by the NVIDIA Deep Learning Container License.
skyreelsv3-comfyui  | By pulling and using the container, you accept the terms and conditions of this license:
skyreelsv3-comfyui  | https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | A copy of this license is made available in this container at /NGC-DL-CONTAINER-LICENSE for your convenience.
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] setup plugin alembic.autogenerate.schemas
skyreelsv3-comfyui  | [INFO] setup plugin alembic.autogenerate.tables
skyreelsv3-comfyui  | [INFO] setup plugin alembic.autogenerate.types
skyreelsv3-comfyui  | [INFO] setup plugin alembic.autogenerate.constraints
skyreelsv3-comfyui  | [INFO] setup plugin alembic.autogenerate.defaults
skyreelsv3-comfyui  | [INFO] setup plugin alembic.autogenerate.comments
skyreelsv3-comfyui  | [INFO] 
skyreelsv3-comfyui  | Prestartup times for custom nodes:
skyreelsv3-comfyui  | [INFO]    0.0 seconds: /workspace/ComfyUI/custom_nodes/rgthree-comfy
skyreelsv3-comfyui  | [INFO] 
skyreelsv3-comfyui  | [WARNING] WARNING: You need pytorch with cu130 or higher to use optimized CUDA operations.
skyreelsv3-comfyui  | [INFO] Found comfy_kitchen backend eager: {'available': True, 'disabled': False, 'unavailable_reason': None, 'capabilities': ['adaln', 'apply_rope', 'apply_rope1', 'apply_rope_split_half', 'apply_rope_split_half1', 'dequantize_int8_convrot_weight', 'dequantize_int8_convrot_weight_dtype', 'dequantize_int8_simple', 'dequantize_int8_simple_dtype', 'dequantize_mxfp8', 'dequantize_nvfp4', 'dequantize_per_tensor_fp8', 'gemv_awq_w4a16', 'int8_linear', 'quantize_and_rotate_rowwise', 'quantize_int8_convrot_weight', 'quantize_int8_rowwise', 'quantize_int8_tensorwise', 'quantize_mxfp8', 'quantize_nvfp4', 'quantize_per_tensor_fp8', 'quantize_svdquant_w4a4', 'scaled_mm_mxfp8', 'scaled_mm_nvfp4', 'scaled_mm_svdquant_w4a4', 'stochastic_rounding_fp8']}
skyreelsv3-comfyui  | [INFO] Found comfy_kitchen backend cuda: {'available': True, 'disabled': True, 'unavailable_reason': None, 'capabilities': ['adaln', 'apply_rope', 'apply_rope1', 'apply_rope_split_half', 'apply_rope_split_half1', 'dequantize_int8_convrot_weight', 'dequantize_int8_convrot_weight_dtype', 'dequantize_int8_simple', 'dequantize_int8_simple_dtype', 'dequantize_nvfp4', 'dequantize_per_tensor_fp8', 'gemv_awq_w4a16', 'int8_linear', 'quantize_and_rotate_rowwise', 'quantize_int8_convrot_weight', 'quantize_int8_rowwise', 'quantize_int8_tensorwise', 'quantize_mxfp8', 'quantize_nvfp4', 'quantize_per_tensor_fp8', 'quantize_svdquant_w4a4', 'scaled_mm_nvfp4', 'scaled_mm_svdquant_w4a4', 'stochastic_rounding_fp8']}
skyreelsv3-comfyui  | [INFO] Found comfy_kitchen backend triton: {'available': True, 'disabled': True, 'unavailable_reason': None, 'capabilities': ['adaln', 'apply_rope', 'apply_rope1', 'apply_rope_split_half', 'apply_rope_split_half1', 'dequantize_nvfp4', 'dequantize_per_tensor_fp8', 'int8_linear', 'quantize_and_rotate_rowwise', 'quantize_int8_rowwise', 'quantize_mxfp8', 'quantize_nvfp4', 'quantize_per_tensor_fp8']}
skyreelsv3-comfyui  | [INFO] Checkpoint files will always be loaded safely.
skyreelsv3-comfyui  | [INFO] Total VRAM 22590 MB, total RAM 191168 MB
skyreelsv3-comfyui  | [INFO] pytorch version: 2.8.0+cu128
skyreelsv3-comfyui  | [INFO] Set vram state to: NORMAL_VRAM
skyreelsv3-comfyui  | [INFO] Device: cuda:0 NVIDIA A10G : cudaMallocAsync
skyreelsv3-comfyui  | [INFO] Device: cuda:1 NVIDIA A10G : cudaMallocAsync
skyreelsv3-comfyui  | [INFO] Device: cuda:2 NVIDIA A10G : cudaMallocAsync
skyreelsv3-comfyui  | [INFO] Device: cuda:3 NVIDIA A10G : cudaMallocAsync
skyreelsv3-comfyui  | [INFO] Using async weight offloading with 2 streams
skyreelsv3-comfyui  | [INFO] Enabled pinned memory 172051.0
skyreelsv3-comfyui  | [INFO] Using pytorch attention
skyreelsv3-comfyui  | aimdo: /project/src-posix/cuda-funchooks.c:52:DEBUG:aimdo_setup_hooks: hooks successfully installed
skyreelsv3-comfyui  | aimdo: /project/src/control.c:247:INFO:comfy-aimdo inited for GPU: NVIDIA A10G (VRAM: 22589 MB)
skyreelsv3-comfyui  | aimdo: /project/src/control.c:247:INFO:comfy-aimdo inited for GPU: NVIDIA A10G (VRAM: 22589 MB)
skyreelsv3-comfyui  | aimdo: /project/src/control.c:247:INFO:comfy-aimdo inited for GPU: NVIDIA A10G (VRAM: 22589 MB)
skyreelsv3-comfyui  | aimdo: /project/src/control.c:247:INFO:comfy-aimdo inited for GPU: NVIDIA A10G (VRAM: 22589 MB)
skyreelsv3-comfyui  | [INFO] DynamicVRAM support detected and enabled
skyreelsv3-comfyui  | [INFO] Python version: 3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]
skyreelsv3-comfyui  | [INFO] ComfyUI version: 0.27.0
skyreelsv3-comfyui  | [INFO] comfy-aimdo version: 0.4.10
skyreelsv3-comfyui  | [INFO] comfy-kitchen version: 0.2.16
skyreelsv3-comfyui  | [INFO] comfyui-frontend-package version: 1.45.20
skyreelsv3-comfyui  | [INFO] comfyui-workflow-templates version: 0.11.6
skyreelsv3-comfyui  | [INFO] comfyui-embedded-docs version: 0.5.7
skyreelsv3-comfyui  | [INFO] comfy-kitchen version: 0.2.16
skyreelsv3-comfyui  | [INFO] comfy-aimdo version: 0.4.10
skyreelsv3-comfyui  | [INFO] [Prompt Server] web root: /opt/venv/lib/python3.12/site-packages/comfyui_frontend_package/static
skyreelsv3-comfyui  | [INFO] Asset seeder disabled
skyreelsv3-comfyui  | [INFO] No OpenGL_accelerate module loaded: No module named 'OpenGL_accelerate'
skyreelsv3-comfyui  | [WARNING] Warning: Could not load sageattention: No module named 'sageattention'
skyreelsv3-comfyui  | [WARNING] sageattention package is not installed, sageattention will not be available
skyreelsv3-comfyui  | [WARNING] WanVideoWrapper WARNING: FantasyPortrait nodes not available: No module named 'onnx'
skyreelsv3-comfyui  | [INFO] 
skyreelsv3-comfyui  | Import times for custom nodes:
skyreelsv3-comfyui  | [INFO]    0.0 seconds: /workspace/ComfyUI/custom_nodes/websocket_image_save.py
skyreelsv3-comfyui  | [INFO]    0.1 seconds: /workspace/ComfyUI/custom_nodes/rgthree-comfy
skyreelsv3-comfyui  | [INFO]    0.1 seconds: /workspace/ComfyUI/custom_nodes/ComfyUI-VideoHelperSuite
skyreelsv3-comfyui  | [INFO]    0.2 seconds: /workspace/ComfyUI/custom_nodes/ComfyUI-KJNodes
skyreelsv3-comfyui  | [INFO]    1.6 seconds: /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper
skyreelsv3-comfyui  | [INFO] 
skyreelsv3-comfyui  | [INFO] Context impl SQLiteImpl.
skyreelsv3-comfyui  | [INFO] Will assume non-transactional DDL.
skyreelsv3-comfyui  | [INFO] Context impl SQLiteImpl.
skyreelsv3-comfyui  | [INFO] Will assume non-transactional DDL.
skyreelsv3-comfyui  | [INFO] Running upgrade  -> 0001_assets, Initial assets schema
skyreelsv3-comfyui  | Revision ID: 0001_assets
skyreelsv3-comfyui  | Revises: None
skyreelsv3-comfyui  | Create Date: 2025-12-10 00:00:00
skyreelsv3-comfyui  | [INFO] Running upgrade 0001_assets -> 0002_merge_to_asset_references, Merge AssetInfo and AssetCacheState into unified asset_references table.
skyreelsv3-comfyui  | [INFO] Running upgrade 0002_merge_to_asset_references -> 0003_add_metadata_job_id, Add system_metadata and job_id columns to asset_references.
skyreelsv3-comfyui  | Change preview_id FK from assets.id to asset_references.id.
skyreelsv3-comfyui  | [INFO] Running upgrade 0003_add_metadata_job_id -> 0004_drop_tag_type, Drop the vestigial tags.tag_type column.
skyreelsv3-comfyui  | [INFO] Running upgrade 0004_drop_tag_type -> 0005_allow_case_sensitive_tags, Allow case-sensitive tag names.
skyreelsv3-comfyui  | [INFO] Running upgrade 0005_allow_case_sensitive_tags -> 0006_add_loader_path, Add loader_path column to asset_references.
skyreelsv3-comfyui  | [INFO] Database upgraded from None to 0006_add_loader_path
skyreelsv3-comfyui  | [INFO] Using RAM pressure cache.
skyreelsv3-comfyui  | [INFO] Starting server
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] To see the GUI go to: http://0.0.0.0:8188
skyreelsv3-comfyui  | [WARNING] [DEPRECATION WARNING] Detected import of deprecated legacy API: /extensions/core/widgetInputs.js. This is likely caused by a custom node extension using outdated APIs. Please update your extensions or contact the extension author for an updated version.
skyreelsv3-comfyui  | [INFO] got prompt
skyreelsv3-comfyui  | [INFO] Downloading Qwen model to: /workspace/ComfyUI/models/transformers/TencentGameMate/chinese-wav2vec2-base
skyreelsv3-comfyui  | /opt/venv/lib/python3.12/site-packages/huggingface_hub/utils/_validators.py:205: UserWarning: The `local_dir_use_symlinks` argument is deprecated and ignored in `snapshot_download`. Downloading to a local directory does not use symlinks anymore.
skyreelsv3-comfyui  |   warnings.warn(
skyreelsv3-comfyui  | [INFO] HTTP Request: GET https://huggingface.co/api/models/TencentGameMate/chinese-wav2vec2-base/revision/main "HTTP/1.1 200 OK"
skyreelsv3-comfyui  | [INFO] HTTP Request: GET https://huggingface.co/api/models/TencentGameMate/chinese-wav2vec2-base/tree/3991242c806928916fff4a8c0e4f76acf661b743?recursive=true&expand=false "HTTP/1.1 200 OK"
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [rgthree-comfy] Loaded 48 exciting nodes. 🎉
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [rgthree-comfy] ComfyUI's new Node 2.0 rendering may be incompatible with some rgthree-comfy nodes and features, breaking some rendering as well as losing the ability to access a node's properties (a vital part of many nodes). It also appears to run MUCH more slowly spiking CPU usage and causing jankiness and unresponsiveness, especially with large workflows. Personally I am not planning to use the new Nodes 2.0 and, unfortunately, am not able to invest the time to investigate and overhaul rgthree-comfy where needed. If you have issues when Nodes 2.0 is enabled, I'd urge you to switch it off as well and join me in hoping ComfyUI is not planning to deprecate the existing, stable canvas rendering all together.
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] HTTP Request: HEAD https://huggingface.co/TencentGameMate/chinese-wav2vec2-base/resolve/3991242c806928916fff4a8c0e4f76acf661b743/config.json "HTTP/1.1 307 Temporary Redirect"
skyreelsv3-comfyui  | Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
skyreelsv3-comfyui  | [WARNING] Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
skyreelsv3-comfyui  | [INFO] HTTP Request: HEAD https://huggingface.co/TencentGameMate/chinese-wav2vec2-base/resolve/3991242c806928916fff4a8c0e4f76acf661b743/README.md "HTTP/1.1 307 Temporary Redirect"
skyreelsv3-comfyui  | [INFO] HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/TencentGameMate/chinese-wav2vec2-base/3991242c806928916fff4a8c0e4f76acf661b743/config.json "HTTP/1.1 200 OK"
skyreelsv3-comfyui  | [INFO] HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/TencentGameMate/chinese-wav2vec2-base/3991242c806928916fff4a8c0e4f76acf661b743/README.md "HTTP/1.1 200 OK"
skyreelsv3-comfyui  | [INFO] HTTP Request: GET https://huggingface.co/api/resolve-cache/models/TencentGameMate/chinese-wav2vec2-base/3991242c806928916fff4a8c0e4f76acf661b743/config.json "HTTP/1.1 200 OK"
skyreelsv3-comfyui  | [INFO] HTTP Request: GET https://huggingface.co/api/resolve-cache/models/TencentGameMate/chinese-wav2vec2-base/3991242c806928916fff4a8c0e4f76acf661b743/README.md "HTTP/1.1 200 OK"
skyreelsv3-comfyui  | [INFO] HTTP Request: HEAD https://huggingface.co/TencentGameMate/chinese-wav2vec2-base/resolve/3991242c806928916fff4a8c0e4f76acf661b743/preprocessor_config.json "HTTP/1.1 307 Temporary Redirect"
skyreelsv3-comfyui  | [INFO] HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/TencentGameMate/chinese-wav2vec2-base/3991242c806928916fff4a8c0e4f76acf661b743/preprocessor_config.json "HTTP/1.1 200 OK"
skyreelsv3-comfyui  | [INFO] HTTP Request: GET https://huggingface.co/api/resolve-cache/models/TencentGameMate/chinese-wav2vec2-base/3991242c806928916fff4a8c0e4f76acf661b743/preprocessor_config.json "HTTP/1.1 200 OK"
skyreelsv3-comfyui  | [INFO] HTTP Request: HEAD https://huggingface.co/TencentGameMate/chinese-wav2vec2-base/resolve/3991242c806928916fff4a8c0e4f76acf661b743/.gitattributes "HTTP/1.1 307 Temporary Redirect"
skyreelsv3-comfyui  | [INFO] HTTP Request: HEAD https://huggingface.co/api/resolve-cache/models/TencentGameMate/chinese-wav2vec2-base/3991242c806928916fff4a8c0e4f76acf661b743/.gitattributes "HTTP/1.1 200 OK"
skyreelsv3-comfyui  | [INFO] HTTP Request: GET https://huggingface.co/api/resolve-cache/models/TencentGameMate/chinese-wav2vec2-base/3991242c806928916fff4a8c0e4f76acf661b743/.gitattributes "HTTP/1.1 200 OK"
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [transformers] Wav2Vec2Model LOAD REPORT from: /workspace/ComfyUI/models/transformers/TencentGameMate/chinese-wav2vec2-base
skyreelsv3-comfyui  | Key                          | Status     |  | 
skyreelsv3-comfyui  | -----------------------------+------------+--+-
skyreelsv3-comfyui  | project_q.weight             | UNEXPECTED |  | 
skyreelsv3-comfyui  | project_hid.weight           | UNEXPECTED |  | 
skyreelsv3-comfyui  | quantizer.weight_proj.weight | UNEXPECTED |  | 
skyreelsv3-comfyui  | quantizer.weight_proj.bias   | UNEXPECTED |  | 
skyreelsv3-comfyui  | quantizer.codevectors        | UNEXPECTED |  | 
skyreelsv3-comfyui  | project_hid.bias             | UNEXPECTED |  | 
skyreelsv3-comfyui  | project_q.bias               | UNEXPECTED |  | 
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | Notes:
skyreelsv3-comfyui  | - UNEXPECTED:     can be ignored when loading from different task/architecture; not ok if you expect identical arch.
skyreelsv3-comfyui  | [transformers] `use_return_dict` is deprecated! Use `return_dict` instead!
skyreelsv3-comfyui  | [INFO] [MultiTalk] --- Raw speaker lengths (samples) ---
skyreelsv3-comfyui  | [INFO]   speaker 1: 129440 samples (shape: torch.Size([1, 1, 129440]))
skyreelsv3-comfyui  | [INFO] [MultiTalk] Audio duration (202 frames) is shorter than requested (500 frames). Using 202 frames.
skyreelsv3-comfyui  | [INFO] [MultiTalk] total raw duration = 8.090s
skyreelsv3-comfyui  | [INFO] [MultiTalk] multi_audio_type=para | final waveform shape=torch.Size([1, 1, 129440]) | length=129440 samples | seconds=8.090s (expected max of raw)
skyreelsv3-comfyui  | [INFO] Converting T5 text encoder model to the expected format...
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | /opt/venv/lib/python3.12/site-packages/torch/_tensor.py:1129: UserWarning: backend:cudaMallocAsync ignores max_split_size_mb,roundup_power2_divisions, and garbage_collect_threshold. (Triggered internally at /pytorch/c10/cuda/CUDAAllocatorConfig.cpp:387.)
skyreelsv3-comfyui  |   return self.detach().item().__format__(format_spec)
skyreelsv3-comfyui  | prompt token count: tensor([5], device='cuda:0')
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] Saved prompt embeds to cache: /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/text_embed_cache/370b966c1c18a8f09e8b50e05a21a27894210c2ac8246565df58ecbe98b013a0.pt
skyreelsv3-comfyui  | [INFO] Saved prompt embeds to cache: /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/text_embed_cache/411bdbdd98002bf986513c4a8315de7311114cf36140c519842d00492f25fd2c.pt
skyreelsv3-comfyui  | [INFO] ------- Scheduler info -------
skyreelsv3-comfyui  | [INFO] Total timesteps: tensor([999.7998, 937.5000, 833.3333, 625.0000], device='cuda:0')
skyreelsv3-comfyui  | [INFO] Using timesteps: tensor([999.7998, 937.5000, 833.3333, 625.0000], device='cuda:0')
skyreelsv3-comfyui  | [INFO] Using sigmas: tensor([0.9998, 0.9375, 0.8333, 0.6250, 0.0000], device='cuda:0')
skyreelsv3-comfyui  | [INFO] ------------------------------
skyreelsv3-comfyui  | [INFO] generated new fontManager
skyreelsv3-comfyui  | [INFO] Requested to load CLIPVisionModelProjection
skyreelsv3-comfyui  | [INFO] Model CLIPVisionModelProjection prepared for dynamic VRAM loading. 1205MB Staged. 0 patches attached. Force pre-loaded 132 weights: 330 KB.
skyreelsv3-comfyui  | [INFO] Clip embeds shape: torch.Size([1, 257, 1280]), dtype: torch.float32
skyreelsv3-comfyui  | [INFO] Combined clip embeds shape: torch.Size([1, 257, 1280])
skyreelsv3-comfyui  | [INFO] Loading prompt embeds from cache: /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/text_embed_cache/411bdbdd98002bf986513c4a8315de7311114cf36140c519842d00492f25fd2c.pt
skyreelsv3-comfyui  | [INFO] Converting T5 text encoder model to the expected format...
skyreelsv3-comfyui  | [INFO] Loading prompt embeds from cache: /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/text_embed_cache/411bdbdd98002bf986513c4a8315de7311114cf36140c519842d00492f25fd2c.pt
skyreelsv3-comfyui  | prompt token count: tensor([98], device='cuda:0')
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] Saved prompt embeds to cache: /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/text_embed_cache/f9108203165921ff601650bce9c5e361f03812f06c048308a602efa30a280d6e.pt
skyreelsv3-comfyui  | prompt token count: tensor([24], device='cuda:0')
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] CUDA Compute Capability: 8.6
skyreelsv3-comfyui  | [INFO] Detected model in_channels: 36
skyreelsv3-comfyui  | [INFO] Model cross attention type: i2v, num_heads: 40, num_layers: 40
skyreelsv3-comfyui  | [INFO] Model variant detected: i2v_480
skyreelsv3-comfyui  | [INFO] Loading and assigning model weights to device...
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] -------------------------
skyreelsv3-comfyui  | [INFO] Transformer weights loaded:
skyreelsv3-comfyui  | [INFO] Device: cuda:0   | Memory: 15,254,709.96 MB
skyreelsv3-comfyui  | [INFO] Multitalk audio features shapes (per speaker): [(202, 12, 768)]
skyreelsv3-comfyui  | [INFO] Rope function: comfy
skyreelsv3-comfyui  | [INFO] ---------- Sampling start ----------
skyreelsv3-comfyui  | [INFO] 81 frames at 832x480 (Input sequence length: 32760) with 4 steps
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] ---------- Sampling end ------------
skyreelsv3-comfyui  | [INFO] [Sampling] Max allocated memory: max_memory=20.679 GB
skyreelsv3-comfyui  | [INFO] [Sampling] Max reserved memory: max_reserved=21.594 GB
skyreelsv3-comfyui  | Generated new RoPE frequencies
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] Loading and assigning model weights to device...
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] -------------------------
skyreelsv3-comfyui  | [INFO] Transformer weights loaded:
skyreelsv3-comfyui  | [INFO] Device: cuda:0   | Memory: 15,254,709.96 MB
skyreelsv3-comfyui  | [INFO] Multitalk audio features shapes (per speaker): [(202, 12, 768)]
skyreelsv3-comfyui  | [INFO] Rope function: comfy
skyreelsv3-comfyui  | [INFO] Multitalk mode: skyreelsv3
skyreelsv3-comfyui  | [INFO] Reference video (81 frames) mapped to target (202 frames). Keyframe indices: [32, 57, 80]
skyreelsv3-comfyui  | [INFO] Extracted 3 keyframes from provided reference video at indices [32, 57, 80], shape: torch.Size([1, 3, 3, 480, 832])
skyreelsv3-comfyui  | [INFO] Reference video total frames: 81, will generate 202 total frames with 4 windows
skyreelsv3-comfyui  | [INFO] Sampling 202 frames in 4 windows, at 832x480 with 4 steps
skyreelsv3-comfyui  | [INFO] Window 0: using keyframe 0/2 for pseudo frames.
skyreelsv3-comfyui  | [ERROR] Error during sampling: Allocation on device 
skyreelsv3-comfyui  | [ERROR] !!! Exception during processing !!! Allocation on device 
skyreelsv3-comfyui  | [ERROR] Traceback (most recent call last):
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/execution.py", line 542, in execute
skyreelsv3-comfyui  |     output_data, output_ui, has_subgraph, has_pending_tasks = await get_output_data(prompt_id, unique_id, obj, input_data_all, execution_block_cb=execution_block_cb, pre_execute_cb=pre_execute_cb, v3_data=v3_data)
skyreelsv3-comfyui  |                                                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/execution.py", line 341, in get_output_data
skyreelsv3-comfyui  |     return_values = await _async_map_node_over_list(prompt_id, unique_id, obj, input_data_all, obj.FUNCTION, allow_interrupt=True, execution_block_cb=execution_block_cb, pre_execute_cb=pre_execute_cb, v3_data=v3_data)
skyreelsv3-comfyui  |                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/execution.py", line 315, in _async_map_node_over_list
skyreelsv3-comfyui  |     await process_inputs(input_dict, i)
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/execution.py", line 303, in process_inputs
skyreelsv3-comfyui  |     result = f(**inputs)
skyreelsv3-comfyui  |              ^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/nodes_sampler.py", line 2734, in process
skyreelsv3-comfyui  |     return super().process(**args_dict)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/nodes_sampler.py", line 2051, in process
skyreelsv3-comfyui  |     return multitalk_loop(**locals())
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/multitalk/multitalk_loop.py", line 272, in multitalk_loop
skyreelsv3-comfyui  |     y = vae.encode(padding_frames_pixels_values, device=device, tiled=tiled_vae, pbar=False).to(dtype)[0]
skyreelsv3-comfyui  |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 1398, in encode
skyreelsv3-comfyui  |     hidden_state = self.single_encode(video, device, pbar=pbar, sample=sample)
skyreelsv3-comfyui  |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 1366, in single_encode
skyreelsv3-comfyui  |     x = self.model.encode(video, pbar=pbar, sample=sample)
skyreelsv3-comfyui  |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 1074, in encode
skyreelsv3-comfyui  |     out_ = self.encoder(x[:, :, 1 + 4 * (i - 1):1 + 4 * i, :, :],
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1773, in _wrapped_call_impl
skyreelsv3-comfyui  |     return self._call_impl(*args, **kwargs)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1784, in _call_impl
skyreelsv3-comfyui  |     return forward_call(*args, **kwargs)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 606, in forward
skyreelsv3-comfyui  |     x = layer(x, feat_cache, feat_idx)
skyreelsv3-comfyui  |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1773, in _wrapped_call_impl
skyreelsv3-comfyui  |     return self._call_impl(*args, **kwargs)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1784, in _call_impl
skyreelsv3-comfyui  |     return forward_call(*args, **kwargs)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 279, in forward
skyreelsv3-comfyui  |     return self._forward(x, feat_cache, feat_idx)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 294, in _forward
skyreelsv3-comfyui  |     x = layer(x, feat_cache[idx])
skyreelsv3-comfyui  |         ^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1773, in _wrapped_call_impl
skyreelsv3-comfyui  |     return self._call_impl(*args, **kwargs)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1784, in _call_impl
skyreelsv3-comfyui  |     return forward_call(*args, **kwargs)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 41, in forward
skyreelsv3-comfyui  |     x = F.pad(x, padding)
skyreelsv3-comfyui  |         ^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/functional.py", line 5290, in pad
skyreelsv3-comfyui  |     return torch._C._nn.pad(input, pad, mode, value)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  | torch.OutOfMemoryError: Allocation on device 
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] Memory summary:
skyreelsv3-comfyui  | |===========================================================================|
skyreelsv3-comfyui  | |                  PyTorch CUDA memory summary, device ID 0                 |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | |            CUDA OOMs: 0            |        cudaMalloc retries: 0         |
skyreelsv3-comfyui  | |===========================================================================|
skyreelsv3-comfyui  | |        Metric         | Cur Usage  | Peak Usage | Tot Alloc  | Tot Freed  |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Allocated memory      |   3116 MiB |  21865 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from large pool |      0 MiB |      0 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from small pool |      0 MiB |      0 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Active memory         |   3116 MiB |  21865 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from large pool |      0 MiB |      0 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from small pool |      0 MiB |      0 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Requested memory      |      0 B   |      0 B   |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from large pool |      0 B   |      0 B   |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from small pool |      0 B   |      0 B   |      0 B   |      0 B   |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | GPU reserved memory   |   3424 MiB |  22208 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from large pool |      0 MiB |      0 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from small pool |      0 MiB |      0 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Non-releasable memory |      0 B   |      0 B   |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from large pool |      0 B   |      0 B   |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from small pool |      0 B   |      0 B   |      0 B   |      0 B   |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Allocations           |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from large pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from small pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Active allocs         |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from large pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from small pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | GPU reserved segments |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from large pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from small pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Non-releasable allocs |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from large pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from small pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Oversize allocations  |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Oversize GPU segments |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |===========================================================================|
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [ERROR] Got an OOM, unloading all loaded models.
skyreelsv3-comfyui  | [INFO] Prompt executed in 174.35 seconds
^CGracefully stopping... (press Ctrl+C again to force)
Aborting on container exit...
[+] Stopping 1/1
 ✔ Container skyreelsv3-comfyui  Stopped                                                                                                                                                                                                                  12.6s 
canceled
(python3) [ec2-user@ip-172-16-16-153 docker-root]$ docker-compose up
[+] Building 0.0s (0/0)                                                                                                                                                                                                                                         
WARN[0000] Found orphan containers ([skyreels-v3 comfyui-longcat-base]) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up. 
[+] Running 1/0
 ✔ Container skyreelsv3-comfyui  Created                                                                                                                                                                                                                   0.0s 
Attaching to skyreelsv3-comfyui
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | ==========
skyreelsv3-comfyui  | == CUDA ==
skyreelsv3-comfyui  | ==========
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | CUDA Version 12.8.1
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | Container image Copyright (c) 2016-2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | This container image and its contents are governed by the NVIDIA Deep Learning Container License.
skyreelsv3-comfyui  | By pulling and using the container, you accept the terms and conditions of this license:
skyreelsv3-comfyui  | https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | A copy of this license is made available in this container at /NGC-DL-CONTAINER-LICENSE for your convenience.
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] setup plugin alembic.autogenerate.schemas
skyreelsv3-comfyui  | [INFO] setup plugin alembic.autogenerate.tables
skyreelsv3-comfyui  | [INFO] setup plugin alembic.autogenerate.types
skyreelsv3-comfyui  | [INFO] setup plugin alembic.autogenerate.constraints
skyreelsv3-comfyui  | [INFO] setup plugin alembic.autogenerate.defaults
skyreelsv3-comfyui  | [INFO] setup plugin alembic.autogenerate.comments
skyreelsv3-comfyui  | [INFO] 
skyreelsv3-comfyui  | Prestartup times for custom nodes:
skyreelsv3-comfyui  | [INFO]    0.0 seconds: /workspace/ComfyUI/custom_nodes/rgthree-comfy
skyreelsv3-comfyui  | [INFO] 
skyreelsv3-comfyui  | [WARNING] WARNING: You need pytorch with cu130 or higher to use optimized CUDA operations.
skyreelsv3-comfyui  | [INFO] Found comfy_kitchen backend eager: {'available': True, 'disabled': False, 'unavailable_reason': None, 'capabilities': ['adaln', 'apply_rope', 'apply_rope1', 'apply_rope_split_half', 'apply_rope_split_half1', 'dequantize_int8_convrot_weight', 'dequantize_int8_convrot_weight_dtype', 'dequantize_int8_simple', 'dequantize_int8_simple_dtype', 'dequantize_mxfp8', 'dequantize_nvfp4', 'dequantize_per_tensor_fp8', 'gemv_awq_w4a16', 'int8_linear', 'quantize_and_rotate_rowwise', 'quantize_int8_convrot_weight', 'quantize_int8_rowwise', 'quantize_int8_tensorwise', 'quantize_mxfp8', 'quantize_nvfp4', 'quantize_per_tensor_fp8', 'quantize_svdquant_w4a4', 'scaled_mm_mxfp8', 'scaled_mm_nvfp4', 'scaled_mm_svdquant_w4a4', 'stochastic_rounding_fp8']}
skyreelsv3-comfyui  | [INFO] Found comfy_kitchen backend cuda: {'available': True, 'disabled': True, 'unavailable_reason': None, 'capabilities': ['adaln', 'apply_rope', 'apply_rope1', 'apply_rope_split_half', 'apply_rope_split_half1', 'dequantize_int8_convrot_weight', 'dequantize_int8_convrot_weight_dtype', 'dequantize_int8_simple', 'dequantize_int8_simple_dtype', 'dequantize_nvfp4', 'dequantize_per_tensor_fp8', 'gemv_awq_w4a16', 'int8_linear', 'quantize_and_rotate_rowwise', 'quantize_int8_convrot_weight', 'quantize_int8_rowwise', 'quantize_int8_tensorwise', 'quantize_mxfp8', 'quantize_nvfp4', 'quantize_per_tensor_fp8', 'quantize_svdquant_w4a4', 'scaled_mm_nvfp4', 'scaled_mm_svdquant_w4a4', 'stochastic_rounding_fp8']}
skyreelsv3-comfyui  | [INFO] Found comfy_kitchen backend triton: {'available': True, 'disabled': True, 'unavailable_reason': None, 'capabilities': ['adaln', 'apply_rope', 'apply_rope1', 'apply_rope_split_half', 'apply_rope_split_half1', 'dequantize_nvfp4', 'dequantize_per_tensor_fp8', 'int8_linear', 'quantize_and_rotate_rowwise', 'quantize_int8_rowwise', 'quantize_mxfp8', 'quantize_nvfp4', 'quantize_per_tensor_fp8']}
skyreelsv3-comfyui  | [INFO] Checkpoint files will always be loaded safely.
skyreelsv3-comfyui  | [INFO] Total VRAM 22590 MB, total RAM 191168 MB
skyreelsv3-comfyui  | [INFO] pytorch version: 2.8.0+cu128
skyreelsv3-comfyui  | [INFO] Set vram state to: NORMAL_VRAM
skyreelsv3-comfyui  | [INFO] Device: cuda:0 NVIDIA A10G : cudaMallocAsync
skyreelsv3-comfyui  | [INFO] Device: cuda:1 NVIDIA A10G : cudaMallocAsync
skyreelsv3-comfyui  | [INFO] Device: cuda:2 NVIDIA A10G : cudaMallocAsync
skyreelsv3-comfyui  | [INFO] Device: cuda:3 NVIDIA A10G : cudaMallocAsync
skyreelsv3-comfyui  | [INFO] Using async weight offloading with 2 streams
skyreelsv3-comfyui  | [INFO] Enabled pinned memory 172051.0
skyreelsv3-comfyui  | [INFO] Using pytorch attention
skyreelsv3-comfyui  | aimdo: /project/src-posix/cuda-funchooks.c:52:DEBUG:aimdo_setup_hooks: hooks successfully installed
skyreelsv3-comfyui  | aimdo: /project/src/control.c:247:INFO:comfy-aimdo inited for GPU: NVIDIA A10G (VRAM: 22589 MB)
skyreelsv3-comfyui  | aimdo: /project/src/control.c:247:INFO:comfy-aimdo inited for GPU: NVIDIA A10G (VRAM: 22589 MB)
skyreelsv3-comfyui  | aimdo: /project/src/control.c:247:INFO:comfy-aimdo inited for GPU: NVIDIA A10G (VRAM: 22589 MB)
skyreelsv3-comfyui  | aimdo: /project/src/control.c:247:INFO:comfy-aimdo inited for GPU: NVIDIA A10G (VRAM: 22589 MB)
skyreelsv3-comfyui  | [INFO] DynamicVRAM support detected and enabled
skyreelsv3-comfyui  | [INFO] Python version: 3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]
skyreelsv3-comfyui  | [INFO] ComfyUI version: 0.27.0
skyreelsv3-comfyui  | [INFO] comfy-aimdo version: 0.4.10
skyreelsv3-comfyui  | [INFO] comfy-kitchen version: 0.2.16
skyreelsv3-comfyui  | [INFO] comfyui-frontend-package version: 1.45.20
skyreelsv3-comfyui  | [INFO] comfyui-workflow-templates version: 0.11.6
skyreelsv3-comfyui  | [INFO] comfyui-embedded-docs version: 0.5.7
skyreelsv3-comfyui  | [INFO] comfy-kitchen version: 0.2.16
skyreelsv3-comfyui  | [INFO] comfy-aimdo version: 0.4.10
skyreelsv3-comfyui  | [INFO] [Prompt Server] web root: /opt/venv/lib/python3.12/site-packages/comfyui_frontend_package/static
skyreelsv3-comfyui  | [INFO] Asset seeder disabled
skyreelsv3-comfyui  | [INFO] No OpenGL_accelerate module loaded: No module named 'OpenGL_accelerate'
skyreelsv3-comfyui  | [WARNING] Warning: Could not load sageattention: No module named 'sageattention'
skyreelsv3-comfyui  | [WARNING] sageattention package is not installed, sageattention will not be available
skyreelsv3-comfyui  | [WARNING] WanVideoWrapper WARNING: FantasyPortrait nodes not available: No module named 'onnx'
skyreelsv3-comfyui  | [INFO] 
skyreelsv3-comfyui  | Import times for custom nodes:
skyreelsv3-comfyui  | [INFO]    0.0 seconds: /workspace/ComfyUI/custom_nodes/websocket_image_save.py
skyreelsv3-comfyui  | [INFO]    0.0 seconds: /workspace/ComfyUI/custom_nodes/rgthree-comfy
skyreelsv3-comfyui  | [INFO]    0.0 seconds: /workspace/ComfyUI/custom_nodes/ComfyUI-KJNodes
skyreelsv3-comfyui  | [INFO]    0.1 seconds: /workspace/ComfyUI/custom_nodes/ComfyUI-VideoHelperSuite
skyreelsv3-comfyui  | [INFO]    0.7 seconds: /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper
skyreelsv3-comfyui  | [INFO] 
skyreelsv3-comfyui  | [INFO] Context impl SQLiteImpl.
skyreelsv3-comfyui  | [INFO] Will assume non-transactional DDL.
skyreelsv3-comfyui  | [INFO] Using RAM pressure cache.
skyreelsv3-comfyui  | [INFO] Starting server
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] To see the GUI go to: http://0.0.0.0:8188
skyreelsv3-comfyui  | [INFO] got prompt
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [rgthree-comfy] Loaded 48 extraordinary nodes. 🎉
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [rgthree-comfy] ComfyUI's new Node 2.0 rendering may be incompatible with some rgthree-comfy nodes and features, breaking some rendering as well as losing the ability to access a node's properties (a vital part of many nodes). It also appears to run MUCH more slowly spiking CPU usage and causing jankiness and unresponsiveness, especially with large workflows. Personally I am not planning to use the new Nodes 2.0 and, unfortunately, am not able to invest the time to investigate and overhaul rgthree-comfy where needed. If you have issues when Nodes 2.0 is enabled, I'd urge you to switch it off as well and join me in hoping ComfyUI is not planning to deprecate the existing, stable canvas rendering all together.
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [transformers] Wav2Vec2Model LOAD REPORT from: /workspace/ComfyUI/models/transformers/TencentGameMate/chinese-wav2vec2-base
skyreelsv3-comfyui  | Key                          | Status     |  | 
skyreelsv3-comfyui  | -----------------------------+------------+--+-
skyreelsv3-comfyui  | project_q.bias               | UNEXPECTED |  | 
skyreelsv3-comfyui  | quantizer.codevectors        | UNEXPECTED |  | 
skyreelsv3-comfyui  | quantizer.weight_proj.bias   | UNEXPECTED |  | 
skyreelsv3-comfyui  | project_hid.bias             | UNEXPECTED |  | 
skyreelsv3-comfyui  | quantizer.weight_proj.weight | UNEXPECTED |  | 
skyreelsv3-comfyui  | project_hid.weight           | UNEXPECTED |  | 
skyreelsv3-comfyui  | project_q.weight             | UNEXPECTED |  | 
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | Notes:
skyreelsv3-comfyui  | - UNEXPECTED:     can be ignored when loading from different task/architecture; not ok if you expect identical arch.
skyreelsv3-comfyui  | [transformers] `use_return_dict` is deprecated! Use `return_dict` instead!
skyreelsv3-comfyui  | [INFO] [MultiTalk] --- Raw speaker lengths (samples) ---
skyreelsv3-comfyui  | [INFO]   speaker 1: 129440 samples (shape: torch.Size([1, 1, 129440]))
skyreelsv3-comfyui  | [INFO] [MultiTalk] Audio duration (202 frames) is shorter than requested (500 frames). Using 202 frames.
skyreelsv3-comfyui  | [INFO] [MultiTalk] total raw duration = 8.090s
skyreelsv3-comfyui  | [INFO] [MultiTalk] multi_audio_type=para | final waveform shape=torch.Size([1, 1, 129440]) | length=129440 samples | seconds=8.090s (expected max of raw)
skyreelsv3-comfyui  | [INFO] Loading prompt embeds from cache: /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/text_embed_cache/370b966c1c18a8f09e8b50e05a21a27894210c2ac8246565df58ecbe98b013a0.pt
skyreelsv3-comfyui  | [INFO] Loading prompt embeds from cache: /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/text_embed_cache/411bdbdd98002bf986513c4a8315de7311114cf36140c519842d00492f25fd2c.pt
skyreelsv3-comfyui  | [INFO] ------- Scheduler info -------
skyreelsv3-comfyui  | /opt/venv/lib/python3.12/site-packages/torch/_tensor_str.py:154: UserWarning: backend:cudaMallocAsync ignores max_split_size_mb,roundup_power2_divisions, and garbage_collect_threshold. (Triggered internally at /pytorch/c10/cuda/CUDAAllocatorConfig.cpp:387.)
skyreelsv3-comfyui  |   nonzero_finite_vals = torch.masked_select(
skyreelsv3-comfyui  | [INFO] Total timesteps: tensor([999.7998, 937.5000, 833.3333, 625.0000], device='cuda:0')
skyreelsv3-comfyui  | [INFO] Using timesteps: tensor([999.7998, 937.5000, 833.3333, 625.0000], device='cuda:0')
skyreelsv3-comfyui  | [INFO] Using sigmas: tensor([0.9998, 0.9375, 0.8333, 0.6250, 0.0000], device='cuda:0')
skyreelsv3-comfyui  | [INFO] ------------------------------
skyreelsv3-comfyui  | [INFO] Requested to load CLIPVisionModelProjection
skyreelsv3-comfyui  | [INFO] Model CLIPVisionModelProjection prepared for dynamic VRAM loading. 1205MB Staged. 0 patches attached. Force pre-loaded 132 weights: 330 KB.
skyreelsv3-comfyui  | [INFO] Clip embeds shape: torch.Size([1, 257, 1280]), dtype: torch.float32
skyreelsv3-comfyui  | [INFO] Combined clip embeds shape: torch.Size([1, 257, 1280])
skyreelsv3-comfyui  | [INFO] Loading prompt embeds from cache: /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/text_embed_cache/f9108203165921ff601650bce9c5e361f03812f06c048308a602efa30a280d6e.pt
skyreelsv3-comfyui  | [INFO] Loading prompt embeds from cache: /workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/text_embed_cache/411bdbdd98002bf986513c4a8315de7311114cf36140c519842d00492f25fd2c.pt
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] CUDA Compute Capability: 8.6
skyreelsv3-comfyui  | [INFO] Detected model in_channels: 36
skyreelsv3-comfyui  | [INFO] Model cross attention type: i2v, num_heads: 40, num_layers: 40
skyreelsv3-comfyui  | [INFO] Model variant detected: i2v_480
skyreelsv3-comfyui  | [INFO] Loading and assigning model weights to device...
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] -------------------------
skyreelsv3-comfyui  | [INFO] Transformer weights loaded:
skyreelsv3-comfyui  | [INFO] Device: cuda:0   | Memory: 15,254,709.96 MB
skyreelsv3-comfyui  | [INFO] Multitalk audio features shapes (per speaker): [(202, 12, 768)]
skyreelsv3-comfyui  | [INFO] Rope function: comfy
skyreelsv3-comfyui  | [INFO] ---------- Sampling start ----------
skyreelsv3-comfyui  | [INFO] 81 frames at 832x480 (Input sequence length: 32760) with 4 steps
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] ---------- Sampling end ------------
skyreelsv3-comfyui  | [INFO] [Sampling] Max allocated memory: max_memory=20.679 GB
skyreelsv3-comfyui  | [INFO] [Sampling] Max reserved memory: max_reserved=21.625 GB
skyreelsv3-comfyui  | Generated new RoPE frequencies
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] Loading and assigning model weights to device...
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] -------------------------
skyreelsv3-comfyui  | [INFO] Transformer weights loaded:
skyreelsv3-comfyui  | [INFO] Device: cuda:0   | Memory: 15,254,709.96 MB
skyreelsv3-comfyui  | [INFO] Multitalk audio features shapes (per speaker): [(202, 12, 768)]
skyreelsv3-comfyui  | [INFO] Rope function: comfy
skyreelsv3-comfyui  | [INFO] Multitalk mode: skyreelsv3
skyreelsv3-comfyui  | [INFO] Reference video (81 frames) mapped to target (202 frames). Keyframe indices: [32, 57, 80]
skyreelsv3-comfyui  | [INFO] Extracted 3 keyframes from provided reference video at indices [32, 57, 80], shape: torch.Size([1, 3, 3, 480, 832])
skyreelsv3-comfyui  | [INFO] Reference video total frames: 81, will generate 202 total frames with 4 windows
skyreelsv3-comfyui  | [INFO] Sampling 202 frames in 4 windows, at 832x480 with 4 steps
skyreelsv3-comfyui  | [INFO] Window 0: using keyframe 0/2 for pseudo frames.
skyreelsv3-comfyui  | [ERROR] Error during sampling: Allocation on device 
skyreelsv3-comfyui  | [ERROR] !!! Exception during processing !!! Allocation on device 
skyreelsv3-comfyui  | [ERROR] Traceback (most recent call last):
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/execution.py", line 542, in execute
skyreelsv3-comfyui  |     output_data, output_ui, has_subgraph, has_pending_tasks = await get_output_data(prompt_id, unique_id, obj, input_data_all, execution_block_cb=execution_block_cb, pre_execute_cb=pre_execute_cb, v3_data=v3_data)
skyreelsv3-comfyui  |                                                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/execution.py", line 341, in get_output_data
skyreelsv3-comfyui  |     return_values = await _async_map_node_over_list(prompt_id, unique_id, obj, input_data_all, obj.FUNCTION, allow_interrupt=True, execution_block_cb=execution_block_cb, pre_execute_cb=pre_execute_cb, v3_data=v3_data)
skyreelsv3-comfyui  |                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/execution.py", line 315, in _async_map_node_over_list
skyreelsv3-comfyui  |     await process_inputs(input_dict, i)
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/execution.py", line 303, in process_inputs
skyreelsv3-comfyui  |     result = f(**inputs)
skyreelsv3-comfyui  |              ^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/nodes_sampler.py", line 2734, in process
skyreelsv3-comfyui  |     return super().process(**args_dict)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/nodes_sampler.py", line 2051, in process
skyreelsv3-comfyui  |     return multitalk_loop(**locals())
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/multitalk/multitalk_loop.py", line 272, in multitalk_loop
skyreelsv3-comfyui  |     y = vae.encode(padding_frames_pixels_values, device=device, tiled=tiled_vae, pbar=False).to(dtype)[0]
skyreelsv3-comfyui  |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 1398, in encode
skyreelsv3-comfyui  |     hidden_state = self.single_encode(video, device, pbar=pbar, sample=sample)
skyreelsv3-comfyui  |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 1366, in single_encode
skyreelsv3-comfyui  |     x = self.model.encode(video, pbar=pbar, sample=sample)
skyreelsv3-comfyui  |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 1074, in encode
skyreelsv3-comfyui  |     out_ = self.encoder(x[:, :, 1 + 4 * (i - 1):1 + 4 * i, :, :],
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1773, in _wrapped_call_impl
skyreelsv3-comfyui  |     return self._call_impl(*args, **kwargs)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1784, in _call_impl
skyreelsv3-comfyui  |     return forward_call(*args, **kwargs)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 606, in forward
skyreelsv3-comfyui  |     x = layer(x, feat_cache, feat_idx)
skyreelsv3-comfyui  |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1773, in _wrapped_call_impl
skyreelsv3-comfyui  |     return self._call_impl(*args, **kwargs)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1784, in _call_impl
skyreelsv3-comfyui  |     return forward_call(*args, **kwargs)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 279, in forward
skyreelsv3-comfyui  |     return self._forward(x, feat_cache, feat_idx)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 294, in _forward
skyreelsv3-comfyui  |     x = layer(x, feat_cache[idx])
skyreelsv3-comfyui  |         ^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1773, in _wrapped_call_impl
skyreelsv3-comfyui  |     return self._call_impl(*args, **kwargs)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/modules/module.py", line 1784, in _call_impl
skyreelsv3-comfyui  |     return forward_call(*args, **kwargs)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/workspace/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/wanvideo/wan_video_vae.py", line 41, in forward
skyreelsv3-comfyui  |     x = F.pad(x, padding)
skyreelsv3-comfyui  |         ^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  |   File "/opt/venv/lib/python3.12/site-packages/torch/nn/functional.py", line 5290, in pad
skyreelsv3-comfyui  |     return torch._C._nn.pad(input, pad, mode, value)
skyreelsv3-comfyui  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
skyreelsv3-comfyui  | torch.OutOfMemoryError: Allocation on device 
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [INFO] Memory summary:
skyreelsv3-comfyui  | |===========================================================================|
skyreelsv3-comfyui  | |                  PyTorch CUDA memory summary, device ID 0                 |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | |            CUDA OOMs: 0            |        cudaMalloc retries: 0         |
skyreelsv3-comfyui  | |===========================================================================|
skyreelsv3-comfyui  | |        Metric         | Cur Usage  | Peak Usage | Tot Alloc  | Tot Freed  |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Allocated memory      |   3116 MiB |  21865 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from large pool |      0 MiB |      0 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from small pool |      0 MiB |      0 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Active memory         |   3116 MiB |  21865 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from large pool |      0 MiB |      0 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from small pool |      0 MiB |      0 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Requested memory      |      0 B   |      0 B   |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from large pool |      0 B   |      0 B   |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from small pool |      0 B   |      0 B   |      0 B   |      0 B   |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | GPU reserved memory   |   3392 MiB |  22208 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from large pool |      0 MiB |      0 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from small pool |      0 MiB |      0 MiB |      0 B   |      0 B   |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Non-releasable memory |      0 B   |      0 B   |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from large pool |      0 B   |      0 B   |      0 B   |      0 B   |
skyreelsv3-comfyui  | |       from small pool |      0 B   |      0 B   |      0 B   |      0 B   |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Allocations           |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from large pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from small pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Active allocs         |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from large pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from small pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | GPU reserved segments |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from large pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from small pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Non-releasable allocs |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from large pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |       from small pool |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Oversize allocations  |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |---------------------------------------------------------------------------|
skyreelsv3-comfyui  | | Oversize GPU segments |       0    |       0    |       0    |       0    |
skyreelsv3-comfyui  | |===========================================================================|
skyreelsv3-comfyui  | 
skyreelsv3-comfyui  | [ERROR] Got an OOM, unloading all loaded models.
skyreelsv3-comfyui  | [INFO] Prompt executed in 154.80 seconds
```
