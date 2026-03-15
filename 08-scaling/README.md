# Scaling

Beam provides multiple ways to scale your workloads: worker concurrency, concurrent inputs, distributed maps, and queues.

## Examples

| File | Description |
|------|-------------|
| `concurrency.py` | Scale out with multiple workers |
| `concurrent_inputs.py` | Handle multiple requests per container |
| `distributed_map.py` | Parallel batch processing |
| `distributed_queue.py` | Producer-consumer patterns |

## Scaling Strategies

### 1. Workers (Horizontal Scaling)

Scale out by running multiple containers:

```python
@endpoint(
    workers=4,  # Run up to 4 containers
)
def handler():
    pass
```

### 2. Concurrent Inputs (Vertical Scaling)

Handle multiple requests per container:

```python
@endpoint(
    concurrent_inputs=10,  # 10 requests per container
    workers=2,  # 2 containers
    # Total capacity: 20 concurrent requests
)
def handler():
    pass
```

### 3. Distributed Map

Process collections in parallel:

```python
@function()
def process_item(item):
    return item * 2

items = [1, 2, 3, 4, 5]
results = list(process_item.map(items))
```

### 4. Distributed Queue

Coordinate work between tasks:

```python
from beam import Queue

queue = Queue(name="my-queue")

# Producer
queue.put({"task": "process"})

# Consumer
item = queue.get(timeout=5)
```

## Choosing the Right Strategy

| Workload Type | Strategy | Why |
|---------------|----------|-----|
| CPU-bound | Workers | Each worker gets full CPU |
| I/O-bound | Concurrent inputs | Efficient async handling |
| Batch processing | Map | Automatic parallelization |
| Pipelines | Queues | Decouple stages |

## Capacity Planning

```
Total Capacity = workers × concurrent_inputs

Example:
  workers=4, concurrent_inputs=10
  = 40 concurrent requests
```

## Best Practices

1. **CPU-bound work**: Use `workers`, keep `concurrent_inputs` low
2. **I/O-bound work**: Use high `concurrent_inputs`, fewer `workers`
3. **GPU work**: One GPU per worker, scale with `workers`
4. **Batch jobs**: Use `.map()` for automatic parallelization
5. **Pipelines**: Use queues to decouple stages
