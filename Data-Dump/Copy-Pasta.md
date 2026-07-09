Prompt ->
A professional presenter faces the camera and speaks calmly in a measured, conversational manner. Neutral relaxed facial expression. Subtle natural lip articulation with restrained jaw movement. Minimal facial expressions, occasional natural blinking, and very small natural head movements. The head remains mostly stable and centered. Static locked camera, medium close-up, soft even studio lighting.

```python
# %% MAINTAIN JUPYTER NOTEBOOK CELLS
# Import and Define
from __future__ import annotations

import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd().resolve()

# Point this at your ComfyUI models directory.
COMFYUI_MODELS = Path(os.environ.get("COMFYUI_MODELS_DIR", "./ComfyUI/models"))

# Put all Hugging Face cache data on the attached EBS volume, not the root disk.
DEFAULT_EBS_CACHE = SCRIPT_DIR / ".hf-cache"
HF_HOME = Path(os.environ.get("MODEL_DOWNLOAD_CACHE_DIR", DEFAULT_EBS_CACHE)).resolve()
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

try:
    from huggingface_hub import hf_hub_download
except ImportError as exc:
    ! pip install huggingface_hub
    from huggingface_hub import hf_hub_download


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


def materialize_file(cached_path: str | Path, output_path: str | Path) -> None:
    src = Path(cached_path).resolve()
    dst = Path(output_path)
    dst.parent.mkdir(parents=True, exist_ok=True)

    tmp_dst = dst.with_name(dst.name + ".tmp")
    if tmp_dst.exists():
        tmp_dst.unlink()

    try:
        os.link(src, tmp_dst)
    except OSError:
        shutil.copy2(src, tmp_dst)

    os.replace(tmp_dst, dst)

    if dst.stat().st_size != src.stat().st_size:
        raise RuntimeError(
            f"Size mismatch after materializing {dst}. "
            f"Expected {src.stat().st_size}, got {dst.stat().st_size}."
        )


def download_file(model_url: str, model_path: str | Path, filename: str | None = None) -> str:
    model_path = Path(model_path)
    model_path.mkdir(parents=True, exist_ok=True)

    hf_file = parse_hf_url(model_url)
    source_name = Path(hf_file.filename).name
    output_name = filename or source_name
    output_path = model_path / output_name

    if output_path.exists():
        print(f"File already exists: {output_path}")
        return str(output_path)

    cached_path = hf_hub_download(
        repo_id=hf_file.repo_id,
        filename=hf_file.filename,
        revision=hf_file.revision,
        cache_dir=HF_HUB_CACHE,
        force_download=False,
    )
    materialize_file(cached_path, output_path)
    return str(output_path)


MODELS_TO_DOWNLOAD = [
    # Official INT8 sharded DiT.
    {
        "directory": "longcat/LongCat-Video-Avatar-1.5/base_model_int8",
        "url": "https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5/resolve/main/base_model_int8/config.json",
    },
    {
        "directory": "longcat/LongCat-Video-Avatar-1.5/base_model_int8",
        "url": "https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5/resolve/main/base_model_int8/quantization_config.json",
    },
    {
        "directory": "longcat/LongCat-Video-Avatar-1.5/base_model_int8",
        "url": "https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5/resolve/main/base_model_int8/quantized_model.safetensors.index.json",
    },
    {
        "directory": "longcat/LongCat-Video-Avatar-1.5/base_model_int8",
        "url": "https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5/resolve/main/base_model_int8/quantized_model-00001-of-00004.safetensors",
    },
    {
        "directory": "longcat/LongCat-Video-Avatar-1.5/base_model_int8",
        "url": "https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5/resolve/main/base_model_int8/quantized_model-00002-of-00004.safetensors",
    },
    {
        "directory": "longcat/LongCat-Video-Avatar-1.5/base_model_int8",
        "url": "https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5/resolve/main/base_model_int8/quantized_model-00003-of-00004.safetensors",
    },
    {
        "directory": "longcat/LongCat-Video-Avatar-1.5/base_model_int8",
        "url": "https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5/resolve/main/base_model_int8/quantized_model-00004-of-00004.safetensors",
    },
    # Smaller ComfyUI Load CLIP fallback text encoder.
    # In the graph, connect Load CLIP to LongCat Avatar Text Encode.
    {
        "directory": "clip",
        "url": "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
    },
    # ComfyUI dropdown files.
    {
        "directory": "loras",
        "url": "https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5/resolve/main/lora/dmd_lora.safetensors",
        "filename": "longcat-avatar-dmd_lora.safetensors",
    },
    {
        "directory": "vae",
        "url": "https://huggingface.co/meituan-longcat/LongCat-Video/resolve/main/vae/diffusion_pytorch_model.safetensors",
        "filename": "LongCat-Video-Avatar-vae.safetensors",
    },
    {
        "directory": "audio_encoders",
        "url": "https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5/resolve/main/whisper-large-v3/model.safetensors",
        "filename": "whisper-large-v3.safetensors",
    },
    {
        "directory": "longcat",
        "url": "https://huggingface.co/seanghay/uvr_models/resolve/main/Kim_Vocal_2.onnx",
    },
]


MAX_PARALLEL_FILES = 3


def main() -> None:
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_FILES) as executor:
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
    print(f"Total Time Elapsed: {end_time - start_time:.2f}s")


# %%
# RUN MAIN
main()

# %%

```
