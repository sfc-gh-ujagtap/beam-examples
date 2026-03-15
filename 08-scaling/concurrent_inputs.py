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
    concurrent_inputs=10,  # Handle up to 10 inputs per container
)
def batch_handler(**inputs):
    """
    Process multiple inputs concurrently in one container.
    
    With concurrent_inputs=10, a single container can process
    up to 10 requests simultaneously using async/threading.
    
    Best for I/O-bound workloads (API calls, database queries).
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
    concurrent_inputs=20,  # High concurrency for I/O-bound work
    workers=2,  # 2 containers, each handling 20 concurrent requests
)
async def io_bound_handler(**inputs):
    """
    Async endpoint for I/O-bound operations.
    
    Total capacity: workers * concurrent_inputs = 2 * 20 = 40 concurrent requests
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
    concurrent_inputs=4,  # Lower for CPU-bound work
)
def mixed_workload_handler(**inputs):
    """
    Mixed I/O and CPU workload.
    
    For CPU-bound work, keep concurrent_inputs lower
    to avoid overloading the CPU.
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
    import concurrent.futures
    import time
    
    print("Testing concurrent inputs...")
    print("=" * 50)
    
    inputs_list = [
        {"data": [1, 2, 3]},
        {"data": [4, 5, 6]},
        {"data": [7, 8, 9]},
        {"data": [10, 11, 12]},
        {"data": [13, 14, 15]},
    ]
    
    start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(batch_handler.remote, **inp) for inp in inputs_list]
        results = [f.result() for f in futures]
    
    elapsed = time.time() - start
    
    print(f"\n5 requests processed in {elapsed:.2f}s")
    for r in results:
        print(f"  Input {r['input']}: sum={r['sum']}, thread={r['thread_id']}")
