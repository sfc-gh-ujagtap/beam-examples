"""
Concurrent Inputs Example
=========================
Process multiple inputs within a single container.
More efficient than spawning new containers for each request.

Deploy: beam deploy concurrent_inputs.py:batch_handler
"""

from beam import endpoint, Image


@endpoint(
    name="batch-processor",
    cpu=2,
    memory="2Gi",
    image=Image(python_version="python3.11").add_python_packages([
        "numpy",
    ]),
)
def batch_handler(**inputs):
    """
    Process batch data in a single request.
    
    For handling multiple items, pass them as a list in the request
    and process them within the handler.
    
    Best for batch processing workloads.
    """
    import numpy as np
    import time
    import threading
    
    data = inputs.get("data", [1, 2, 3])
    
    time.sleep(0.1)
    
    result = np.array(data)
    
    return {
        "input": data,
        "sum": float(result.sum()),
        "mean": float(result.mean()),
        "thread_id": threading.current_thread().name,
    }


@endpoint(
    name="io-bound-processor",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11").add_python_packages([
        "httpx",
    ]),
    workers=2,  # 2 containers handling requests
)
async def io_bound_handler(**inputs):
    """
    Async endpoint for I/O-bound operations.
    
    With workers=2, can handle 2 concurrent requests.
    """
    import httpx
    import asyncio
    
    url = inputs.get("url", "https://httpbin.org/delay/1")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30)
    
    return {
        "url": url,
        "status_code": response.status_code,
        "response_time_ms": response.elapsed.total_seconds() * 1000,
    }


@endpoint(
    name="mixed-workload",
    cpu=4,
    memory="4Gi",
    image=Image(python_version="python3.11").add_python_packages([
        "numpy",
    ]),
    workers=4,  # Multiple workers for CPU-bound work
)
def mixed_workload_handler(**inputs):
    """
    Mixed I/O and CPU workload.
    
    Uses multiple workers to handle concurrent requests
    for CPU-bound work.
    """
    import numpy as np
    import time
    
    size = inputs.get("size", 500)
    io_delay = inputs.get("io_delay", 0.1)
    
    time.sleep(io_delay)
    
    a = np.random.randn(size, size)
    b = np.random.randn(size, size)
    c = np.dot(a, b)
    
    return {
        "matrix_size": size,
        "io_delay": io_delay,
        "result_mean": float(c.mean()),
    }


if __name__ == "__main__":
    print("Batch Processing Examples")
    print("=" * 50)
    print("\nTo test, deploy the endpoint:")
    print("  beam deploy concurrent_inputs.py:batch_handler")
    print("\nThen send a request with data:")
    print("  curl -X POST '[ENDPOINT_URL]' \\")
    print("    -H 'Authorization: Bearer [TOKEN]' \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"data\": [1, 2, 3, 4, 5]}'")
