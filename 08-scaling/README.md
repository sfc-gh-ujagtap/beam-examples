# Scaling

Beam provides multiple ways to scale your workloads: worker concurrency, distributed maps, and queues.

## Examples

| File | Description |
|------|-------------|
| `concurrency.py` | Scale out with multiple workers |
| `batch_processing.py` | Process batches and use async handlers |
| `distributed_map.py` | Parallel batch processing with .map() |
| `distributed_queue.py` | Producer-consumer patterns |

## Scaling Strategies

### 1. Workers (Horizontal Scaling)

Scale out by running multiple containers:

```python
@endpoint(
    workers=4,  # Run up to 4 containers in parallel
)
def handler(**inputs):
    # Each worker handles one request at a time
    # With workers=4, you can handle 4 concurrent requests
    pass
```

**When to use:** CPU-bound workloads, GPU inference, any work that benefits from parallel execution.

### 2. Batch Processing

Process multiple items in a single request:

```python
@endpoint()
def batch_handler(**inputs):
    items = inputs.get("items", [])
    results = [process(item) for item in items]
    return {"results": results}
```

**When to use:** When you have many small items to process and want to reduce HTTP overhead.

### 3. Async Handlers

Use async for I/O-bound operations:

```python
@endpoint()
async def async_handler(**inputs):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return {"status": response.status_code}
```

**When to use:** HTTP calls, database queries, file I/O - anything that waits on external resources.

### 4. Distributed Map

Process collections in parallel across multiple workers:

```python
@function()
def process_item(item):
    return item * 2

items = [1, 2, 3, 4, 5]
results = list(process_item.map(items))  # Runs in parallel!
```

**When to use:** Batch processing, ETL pipelines, any work that can be parallelized.

### 5. Distributed Queue

Coordinate work between tasks:

```python
from beam import Queue

queue = Queue(name="my-queue")

# Producer
queue.put({"task": "process"})

# Consumer
item = queue.get(timeout=5)
```

**When to use:** Pipelines, decoupling producers from consumers, rate limiting.

## Choosing the Right Strategy

| Workload Type | Strategy | Why |
|---------------|----------|-----|
| CPU-bound | Workers | Each worker gets full CPU |
| I/O-bound | Async handlers | Efficient non-blocking I/O |
| Batch processing | Map | Automatic parallelization |
| Many small items | Batch in single request | Reduce HTTP overhead |
| Pipelines | Queues | Decouple stages |

## Capacity Planning

With `workers=N`, you can handle N concurrent requests.

```
Example:
  workers=4
  = 4 concurrent requests handled in parallel
  
  If each request takes 2 seconds:
  - Sequential: 4 requests = 8 seconds
  - With workers=4: 4 requests = 2 seconds
```

## Best Practices

1. **CPU-bound work**: Use `workers` to scale horizontally
2. **I/O-bound work**: Use `async` handlers for efficiency
3. **GPU work**: One GPU per worker, scale with `workers`
4. **Batch jobs**: Use `.map()` for automatic parallelization
5. **Pipelines**: Use queues to decouple stages
6. **Many small items**: Batch them in a single request to reduce overhead
