"""
GPU-Accelerated Endpoint Example
================================
An endpoint with GPU support for ML inference workloads.
Beam supports: A10G (24GB), RTX4090 (24GB), H100 (80GB).

Deploy: beam deploy gpu_endpoint.py:handler
Check GPUs: beam machine list
"""

from beam import endpoint, Image


@endpoint(
    name="gpu-inference-api",
    cpu=2,
    memory="8Gi",
    gpu="A10G",  # Options: "A10G", "RTX4090", "H100", or list for priority ["A10G", "RTX4090"]
    image=Image(python_version="python3.11").add_python_packages([
        "torch",
        "numpy",
    ]),
    keep_warm_seconds=300,  # Keep container warm for 5 minutes to reduce cold starts
)
def handler(**inputs):
    """
    GPU-accelerated computation endpoint.
    
    Example request:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"size": 1000}'
    """
    import torch
    import time
    
    size = inputs.get("size", 1000)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    start = time.time()
    
    a = torch.randn(size, size, device=device)
    b = torch.randn(size, size, device=device)
    c = torch.matmul(a, b)
    
    if device == "cuda":
        torch.cuda.synchronize()
    
    elapsed = time.time() - start
    
    return {
        "device": device,
        "gpu_name": torch.cuda.get_device_name(0) if device == "cuda" else None,
        "matrix_size": size,
        "computation_time_seconds": round(elapsed, 4),
        "result_shape": list(c.shape),
        "result_mean": float(c.mean()),
    }


@endpoint(
    name="multi-gpu-example",
    cpu=4,
    memory="16Gi",
    gpu="A10G",
    gpu_count=2,  # Request multiple GPUs (requires account approval)
    image=Image(python_version="python3.11").add_python_packages(["torch"]),
)
def multi_gpu_handler(**inputs):
    """
    Multi-GPU endpoint example.
    Note: Multiple GPUs require account approval from Beam.
    """
    import torch
    
    gpu_count = torch.cuda.device_count()
    gpu_info = []
    
    for i in range(gpu_count):
        gpu_info.append({
            "index": i,
            "name": torch.cuda.get_device_name(i),
            "memory_total_gb": round(torch.cuda.get_device_properties(i).total_memory / 1e9, 2),
        })
    
    return {
        "gpu_count": gpu_count,
        "gpus": gpu_info,
    }
