Prompt ->
A professional presenter faces the camera and speaks calmly in a measured, conversational manner. Neutral relaxed facial expression. Subtle natural lip articulation with restrained jaw movement. Minimal facial expressions, occasional natural blinking, and very small natural head movements. The head remains mostly stable and centered. Static locked camera, medium close-up, soft even studio lighting.

```python
# %% MAINTAIN JUPYTER NOTEBOOK CELLS

# Import and Define

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse


SCRIPT_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd().resolve()


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

COMFYUI_MODELS = Path(
    os.environ.get(
        "COMFYUI_MODELS_DIR",
        SCRIPT_DIR / "storage-models" / "models",
    )
).resolve()


# ---------------------------------------------------------
# Hugging Face cache on EBS
# ---------------------------------------------------------

DEFAULT_EBS_CACHE = SCRIPT_DIR / "storage" / ".hf-cache"

HF_HOME = Path(
    os.environ.get(
        "MODEL_DOWNLOAD_CACHE_DIR",
        DEFAULT_EBS_CACHE,
    )
).resolve()

HF_HUB_CACHE = HF_HOME / "hub"
HF_XET_CACHE = HF_HOME / "xet"
PIP_CACHE_DIR = HF_HOME / "pip"


HF_HUB_CACHE.mkdir(parents=True, exist_ok=True)
HF_XET_CACHE.mkdir(parents=True, exist_ok=True)
PIP_CACHE_DIR.mkdir(parents=True, exist_ok=True)


os.environ["HF_HOME"] = str(HF_HOME)
os.environ["HF_HUB_CACHE"] = str(HF_HUB_CACHE)
os.environ["HF_XET_CACHE"] = str(HF_XET_CACHE)
os.environ["PIP_CACHE_DIR"] = str(PIP_CACHE_DIR)

os.environ.setdefault("HF_XET_HIGH_PERFORMANCE", "1")
os.environ.setdefault("HF_XET_NUM_CONCURRENT_RANGE_GETS", "32")


# ---------------------------------------------------------
# Install huggingface_hub if needed
# ---------------------------------------------------------

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-U",
            "huggingface_hub[hf_xet]",
        ]
    )

    from huggingface_hub import hf_hub_download


# ---------------------------------------------------------
# Hugging Face URL parser
# ---------------------------------------------------------

@dataclass(frozen=True)
class HfUrl:
    repo_id: str
    revision: str
    filename: str


def parse_hf_url(url: str) -> HfUrl:
    parsed = urlparse(url)
    parts = unquote(parsed.path).strip("/").split("/")

    if len(parts) < 5:
        raise ValueError(f"Not a valid Hugging Face file URL: {url}")

    marker = parts[2]

    if marker not in {"resolve", "blob"}:
        raise ValueError(f"Expected '/resolve/' or '/blob/' in URL: {url}")

    return HfUrl(
        repo_id=f"{parts[0]}/{parts[1]}",
        revision=parts[3],
        filename="/".join(parts[4:]),
    )


# ---------------------------------------------------------
# Materialize cached file into ComfyUI model directory
# ---------------------------------------------------------

def materialize_file(
    cached_path: str | Path,
    output_path: str | Path,
) -> None:

    src = Path(cached_path).resolve()
    dst = Path(output_path)

    dst.parent.mkdir(parents=True, exist_ok=True)

    tmp_dst = dst.with_name(dst.name + ".tmp")

    if tmp_dst.exists():
        tmp_dst.unlink()

    try:
        os.link(src, tmp_dst)
        method = "hardlink"

    except OSError:
        shutil.copy2(src, tmp_dst)
        method = "copy"

    os.replace(tmp_dst, dst)

    if dst.stat().st_size != src.stat().st_size:
        raise RuntimeError(
            f"Size mismatch after materializing {dst}. "
            f"Expected {src.stat().st_size}, got {dst.stat().st_size}."
        )

    print(f"Materialized via {method}: {dst}")


# ---------------------------------------------------------
# Download one file
# ---------------------------------------------------------

def download_file(
    model_url: str,
    model_path: str | Path,
    filename: str | None = None,
) -> str:

    model_path = Path(model_path)
    model_path.mkdir(parents=True, exist_ok=True)

    hf_file = parse_hf_url(model_url)

    source_name = Path(hf_file.filename).name
    output_name = filename or source_name
    output_path = model_path / output_name

    if output_path.exists():
        print(f"File already exists: {output_path}")
        return str(output_path)

    print(f"Downloading: {hf_file.repo_id}/{hf_file.filename}")

    cached_path = hf_hub_download(
        repo_id=hf_file.repo_id,
        filename=hf_file.filename,
        revision=hf_file.revision,
        cache_dir=HF_HUB_CACHE,
        force_download=False,
    )

    materialize_file(
        cached_path,
        output_path,
    )

    return str(output_path)


# ---------------------------------------------------------
# SkyReels V3 workflow models
# ---------------------------------------------------------

MODELS_TO_DOWNLOAD = [

    # -----------------------------------------------------
    # 1. SkyReels V3 A2V FP8 model
    #
    # ComfyUI:
    # models/diffusion_models/SkyreelsV3/
    # -----------------------------------------------------

    {
        "directory": "diffusion_models/SkyreelsV3",
        "url": "https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/resolve/main/SkyReelsV3/Wan21-SkyReelsV3-A2V_fp8_scaled_mixed.safetensors",
    },


    # -----------------------------------------------------
    # 2. Wan 2.1 VAE
    #
    # ComfyUI:
    # models/vae/
    # -----------------------------------------------------

    {
        "directory": "vae",
        "url": "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors",
    },


    # -----------------------------------------------------
    # 3. CLIP Vision H
    #
    # ComfyUI:
    # models/clip_vision/
    # -----------------------------------------------------

    {
        "directory": "clip_vision",
        "url": "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors",
    },


    # -----------------------------------------------------
    # 4. UMT5-XXL FP16 text encoder
    #
    # ComfyUI:
    # models/text_encoders/
    # -----------------------------------------------------

    {
        "directory": "text_encoders",
        "url": "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp16.safetensors",
    },


    # -----------------------------------------------------
    # 5. Wav2Vec2 FP16
    #
    # ComfyUI:
    # models/wav2vec2/
    # -----------------------------------------------------

    {
        "directory": "wav2vec2",
        "url": "https://huggingface.co/Kijai/wav2vec2_safetensors/resolve/main/wav2vec2-chinese-base_fp16.safetensors",
    },


    # -----------------------------------------------------
    # 6. OPTIONAL: MelBandRoFormer vocal separator
    #
    # Used by:
    # ComfyUI-MelBandRoFormer
    #
    # Workflow loader:
    # MelBandRoFormerModelLoader
    #
    # ComfyUI:
    # models/diffusion_models/
    # -----------------------------------------------------

    {
        "directory": "diffusion_models",
        "url": "https://huggingface.co/Kijai/MelBandRoFormer_comfy/resolve/main/MelBandRoformer_fp16.safetensors",
    },
]


# ---------------------------------------------------------
# Parallel download settings
#
# HF/Xet already parallelizes large file transfers internally.
# Keep this moderate to avoid excessive EBS/network contention.
# ---------------------------------------------------------

MAX_PARALLEL_FILES = 3


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main() -> None:

    start_time = time.time()

    print(f"ComfyUI models: {COMFYUI_MODELS}")
    print(f"HF cache:       {HF_HOME}")
    print()

    with ThreadPoolExecutor(
        max_workers=MAX_PARALLEL_FILES
    ) as executor:

        futures = [
            executor.submit(
                download_file,
                model["url"],
                COMFYUI_MODELS / model["directory"],
                model.get("filename"),
            )
            for model in MODELS_TO_DOWNLOAD
        ]

        for future in as_completed(futures):
            downloaded_model_path = future.result()
            print(f"Downloaded model to: {downloaded_model_path}")

    end_time = time.time()

    print()
    print(f"Total Time Elapsed: {end_time - start_time:.2f}s")


# %%
# RUN MAIN

main()

# %%
```
