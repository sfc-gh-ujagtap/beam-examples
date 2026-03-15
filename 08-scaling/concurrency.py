"""
Concurrency Example
===================
Scale out workers to handle multiple requests simultaneously.
Control how many containers run in parallel.

Deploy: beam deploy concurrency.py:handler
"""

from beam import endpoint, Image


@endpoint(
    name="concurrent-api",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
    workers=4,  # Run up to 4 containers in parallel
)
def handler(**inputs):
    """
    Endpoint with multiple workers for concurrent requests.
    
    Each worker handles one request at a time.
    With workers=4, you can handle 4 simultaneous requests.
    """
    import time
    import os
    
    delay = inputs.get("delay", 1)
    
    time.sleep(delay)
    
    return {
        "worker_id": os.getpid(),
        "delay": delay,
        "message": "Request processed",
    }


@endpoint(
    name="auto-scaling-api",
    cpu=2,
    memory="1Gi",
    image=Image(python_version="python3.11"),
    workers=10,  # Scale up to 10 workers based on demand
    keep_warm_seconds=60,  # Keep containers warm for 60s
)
def auto_scaling_handler(**inputs):
    """
    Auto-scaling endpoint that scales based on traffic.
    
    Beam automatically:
    - Spins up new workers when requests queue up
    - Scales down when traffic decreases
    - Keeps containers warm to reduce cold starts
    """
    import time
    import os
    
    work_time = inputs.get("work_time", 0.5)
    
    time.sleep(work_time)
    
    return {
        "worker_pid": os.getpid(),
        "work_time": work_time,
        "status": "complete",
    }


@endpoint(
    name="gpu-concurrent",
    cpu=2,
    memory="8Gi",
    gpu="A10G",
    workers=2,  # 2 GPU workers
    image=Image(python_version="python3.11").add_python_packages([
        "torch",
    ]),
)
def gpu_concurrent_handler(**inputs):
    """
    GPU endpoint with multiple workers.
    
    Note: Each worker gets its own GPU.
    With workers=2, you need 2 GPUs available.
    """
    import torch
    import os
    
    size = inputs.get("size", 1000)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    a = torch.randn(size, size, device=device)
    b = torch.randn(size, size, device=device)
    c = torch.matmul(a, b)
    
    if device == "cuda":
        torch.cuda.synchronize()
    
    return {
        "worker_pid": os.getpid(),
        "device": device,
        "gpu_name": torch.cuda.get_device_name(0) if device == "cuda" else None,
        "matrix_size": size,
    }


if __name__ == "__main__":
    print("Concurrency Examples")
    print("=" * 50)
    print("\nTo test concurrent workers, deploy the endpoint:")
    print("  beam deploy concurrency.py:handler")
    print("\nThen send multiple concurrent requests:")
    print("  for i in {1..4}; do")
    print("    curl -X POST '[ENDPOINT_URL]' \\")
    print("      -H 'Authorization: Bearer [TOKEN]' \\")
    print("      -H 'Content-Type: application/json' \\")
    print("      -d '{\"delay\": 2}' &")
    print("  done")
    print("\nWith workers=4, all 4 requests should complete in ~2s total.")
