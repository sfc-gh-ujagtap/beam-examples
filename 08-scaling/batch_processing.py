"""
Batch Processing Example
========================
Process multiple items efficiently in a single request.
Use workers parameter to scale horizontally.

Deploy: beam deploy batch_processing.py:batch_handler
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
    
    Pass multiple items as a list and process them together.
    More efficient than making separate requests for each item.
    
    Example:
        curl -X POST '[ENDPOINT_URL]' \
            -H 'Authorization: Bearer [TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}'
    """
    import numpy as np
    
    data = inputs.get("data", [1, 2, 3])
    
    arr = np.array(data)
    
    return {
        "input": data,
        "count": len(data),
        "sum": float(arr.sum()),
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


@endpoint(
    name="parallel-processor",
    cpu=2,
    memory="1Gi",
    image=Image(python_version="python3.11").add_python_packages([
        "numpy",
    ]),
    workers=4,  # Scale horizontally with 4 workers
)
def parallel_handler(**inputs):
    """
    Endpoint with multiple workers for parallel request handling.
    
    With workers=4, Beam runs 4 containers that can each handle
    one request at a time, giving you 4x throughput.
    
    Use this pattern when:
    - You have many concurrent requests
    - Each request is independent
    - You want to reduce latency under load
    """
    import numpy as np
    import os
    import time
    
    size = inputs.get("size", 100)
    
    a = np.random.randn(size, size)
    b = np.random.randn(size, size)
    result = np.dot(a, b)
    
    return {
        "worker_pid": os.getpid(),
        "matrix_size": size,
        "result_mean": float(result.mean()),
    }


@endpoint(
    name="async-io-handler",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11").add_python_packages([
        "httpx",
    ]),
    workers=2,
)
async def async_handler(**inputs):
    """
    Async endpoint for I/O-bound operations.
    
    Use async handlers when your code is I/O-bound (HTTP calls,
    database queries, file operations) to maximize efficiency.
    """
    import httpx
    
    url = inputs.get("url", "https://httpbin.org/get")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=30)
    
    return {
        "url": url,
        "status_code": response.status_code,
        "response_time_ms": response.elapsed.total_seconds() * 1000,
    }


if __name__ == "__main__":
    print("Batch Processing Examples")
    print("=" * 50)
    print("\nDeploy endpoints:")
    print("  beam deploy batch_processing.py:batch_handler")
    print("  beam deploy batch_processing.py:parallel_handler")
    print("  beam deploy batch_processing.py:async_handler")
    print("\nTest batch processing:")
    print("  curl -X POST '[URL]' -d '{\"data\": [1,2,3,4,5]}'")
