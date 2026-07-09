Prompt ->
A professional presenter faces the camera and speaks calmly in a measured, conversational manner. Neutral relaxed facial expression. Subtle natural lip articulation with restrained jaw movement. Minimal facial expressions, occasional natural blinking, and very small natural head movements. The head remains mostly stable and centered. Static locked camera, medium close-up, soft even studio lighting.


docker-compose.yml file
```
services:
  comfyui-longcat-base:
    image: comfyui-longcat-base:v1
    container_name: comfyui-longcat-base
    build:
      context: .
      dockerfile: Dockerfile

    ports:
      - "8188:8188"

    volumes:
      - ./storage:/workspace/storage:delegated
      - ./storage-models/models:/workspace/ComfyUI/models:delegated
      - ./storage-user/input:/workspace/ComfyUI/input:delegated
      - ./storage-user/output:/workspace/ComfyUI/output:delegated
      - ./storage-user/workflows:/workspace/ComfyUI/user/default/workflows:delegated

    environment:
      NVIDIA_VISIBLE_DEVICES: all
      NVIDIA_DRIVER_CAPABILITIES: compute,utility
      PYTORCH_CUDA_ALLOC_CONF: expandable_segments:True

    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              capabilities: [gpu]
              count: 1
```
