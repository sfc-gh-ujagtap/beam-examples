"""
Keep Warm Example
=================
Control how long containers stay running after requests.
Reduce cold starts for frequently accessed endpoints.

Deploy: beam deploy keep_warm.py:handler
"""

from beam import endpoint, Image


@endpoint(
    name="always-warm",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
    keep_warm_seconds=3600,  # Keep warm for 1 hour
)
def always_warm_handler(**inputs):
    """
    Endpoint that stays warm for 1 hour after last request.
    
    Good for:
    - High-traffic APIs
    - Latency-sensitive applications
    - Endpoints with expensive initialization
    """
    import time
    
    return {
        "message": "Response from warm container",
        "timestamp": time.time(),
    }


@endpoint(
    name="quick-scale-down",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
    keep_warm_seconds=30,  # Scale down quickly
)
def quick_scale_handler(**inputs):
    """
    Endpoint that scales down quickly (30 seconds).
    
    Good for:
    - Infrequent traffic
    - Cost-sensitive applications
    - Batch processing endpoints
    """
    return {"message": "Response from quick-scale endpoint"}


@endpoint(
    name="balanced-warm",
    cpu=2,
    memory="1Gi",
    image=Image(python_version="python3.11"),
    keep_warm_seconds=180,  # Default: 3 minutes
    workers=2,  # 2 containers
)
def balanced_handler(**inputs):
    """
    Balanced keep-warm with multiple workers.
    
    Each worker stays warm independently.
    If one worker is cold, others may still be warm.
    """
    import os
    
    return {
        "worker_pid": os.getpid(),
        "message": "Response from balanced endpoint",
    }


def load_expensive_resource():
    """Simulate expensive initialization."""
    import time
    
    time.sleep(5)
    
    return {"initialized": True, "data": list(range(1000))}


@endpoint(
    name="expensive-init",
    cpu=2,
    memory="2Gi",
    image=Image(python_version="python3.11"),
    on_start=load_expensive_resource,
    keep_warm_seconds=600,  # Keep warm longer due to expensive init
)
def expensive_init_handler(context, **inputs):
    """
    Endpoint with expensive initialization.
    
    Keep warm longer to amortize initialization cost.
    The on_start function only runs once per container.
    """
    resource = context.on_start_value
    
    return {
        "initialized": resource["initialized"],
        "data_size": len(resource["data"]),
    }


@endpoint(
    name="gpu-warm",
    cpu=2,
    memory="8Gi",
    gpu="A10G",
    image=Image(python_version="python3.11").add_python_packages(["torch"]),
    keep_warm_seconds=300,  # 5 minutes for GPU
)
def gpu_warm_handler(**inputs):
    """
    GPU endpoint with keep-warm.
    
    GPU containers are more expensive, so balance
    keep-warm time with cost considerations.
    """
    import torch
    
    return {
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }


"""
Keep Warm Guidelines:

| Scenario                    | Recommended keep_warm_seconds |
|-----------------------------|-------------------------------|
| High traffic API            | 600-3600 (10min - 1hr)        |
| Medium traffic              | 180-300 (3-5 min)             |
| Low traffic                 | 30-60 (30s - 1min)            |
| Expensive initialization    | 300-600 (5-10 min)            |
| GPU endpoints               | 180-300 (3-5 min)             |
| Batch processing            | 30 (30s)                      |

Cost Impact:
- Longer keep_warm = More cost (container running idle)
- Shorter keep_warm = More cold starts (slower responses)
- Find the balance based on your traffic patterns
"""
