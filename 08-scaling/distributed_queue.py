"""
Distributed Queue Example
=========================
Coordinate work between tasks using distributed queues.
Great for producer-consumer patterns and pipelines.

Run: python distributed_queue.py
"""

from beam import function, Image, Queue


@function(
    name="producer",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
)
def producer(queue_name: str, items: list):
    """
    Produce items and add them to a queue.
    """
    queue = Queue(name=queue_name)
    
    for item in items:
        queue.put(item)
    
    return {
        "queue": queue_name,
        "items_added": len(items),
    }


@function(
    name="consumer",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
)
def consumer(queue_name: str, max_items: int = 10):
    """
    Consume items from a queue.
    """
    queue = Queue(name=queue_name)
    
    processed = []
    for _ in range(max_items):
        item = queue.get(timeout=5)
        if item is None:
            break
        
        result = {"original": item, "processed": str(item).upper()}
        processed.append(result)
    
    return {
        "queue": queue_name,
        "items_processed": len(processed),
        "results": processed,
    }


@function(
    name="pipeline-stage-1",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
)
def stage_1(input_queue: str, output_queue: str, batch_size: int = 5):
    """
    First stage of a processing pipeline.
    Reads from input queue, processes, writes to output queue.
    """
    in_q = Queue(name=input_queue)
    out_q = Queue(name=output_queue)
    
    processed = 0
    for _ in range(batch_size):
        item = in_q.get(timeout=5)
        if item is None:
            break
        
        result = {"stage": 1, "data": item, "transformed": item * 2}
        out_q.put(result)
        processed += 1
    
    return {"stage": 1, "processed": processed}


@function(
    name="pipeline-stage-2",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
)
def stage_2(input_queue: str, output_queue: str, batch_size: int = 5):
    """
    Second stage of a processing pipeline.
    """
    in_q = Queue(name=input_queue)
    out_q = Queue(name=output_queue)
    
    processed = 0
    for _ in range(batch_size):
        item = in_q.get(timeout=5)
        if item is None:
            break
        
        result = {
            "stage": 2,
            "input": item,
            "final": item.get("transformed", 0) + 100,
        }
        out_q.put(result)
        processed += 1
    
    return {"stage": 2, "processed": processed}


def simple_queue_example():
    """Basic producer-consumer pattern."""
    print("Simple Queue Example")
    print("=" * 50)
    
    queue_name = "simple-queue"
    items = [1, 2, 3, 4, 5]
    
    print(f"Producing {len(items)} items...")
    prod_result = producer.remote(queue_name=queue_name, items=items)
    print(f"Producer result: {prod_result}")
    
    print("\nConsuming items...")
    cons_result = consumer.remote(queue_name=queue_name, max_items=10)
    print(f"Consumer result: {cons_result}")


def pipeline_example():
    """Multi-stage pipeline using queues."""
    print("\nPipeline Example")
    print("=" * 50)
    
    input_q = "pipeline-input"
    stage1_q = "pipeline-stage1"
    output_q = "pipeline-output"
    
    print("Seeding input queue...")
    producer.remote(queue_name=input_q, items=[1, 2, 3, 4, 5])
    
    print("Running stage 1...")
    s1_result = stage_1.remote(input_queue=input_q, output_queue=stage1_q)
    print(f"Stage 1: {s1_result}")
    
    print("Running stage 2...")
    s2_result = stage_2.remote(input_queue=stage1_q, output_queue=output_q)
    print(f"Stage 2: {s2_result}")
    
    print("Collecting results...")
    results = consumer.remote(queue_name=output_q, max_items=10)
    print(f"Final results: {results}")


@function(
    name="parallel-consumer",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
)
def parallel_consumer(queue_name: str, worker_id: int):
    """
    Consumer that can run in parallel with other consumers.
    Multiple workers can consume from the same queue.
    """
    import time
    
    queue = Queue(name=queue_name)
    
    processed = []
    while True:
        item = queue.get(timeout=2)
        if item is None:
            break
        
        time.sleep(0.1)
        processed.append({
            "worker": worker_id,
            "item": item,
        })
    
    return {
        "worker_id": worker_id,
        "items_processed": len(processed),
        "items": processed,
    }


def parallel_consumers_example():
    """Multiple consumers processing from the same queue."""
    print("\nParallel Consumers Example")
    print("=" * 50)
    
    queue_name = "parallel-queue"
    
    print("Producing 20 items...")
    producer.remote(queue_name=queue_name, items=list(range(20)))
    
    print("Starting 4 parallel consumers...")
    consumer_configs = [{"queue_name": queue_name, "worker_id": i} for i in range(4)]
    results = list(parallel_consumer.map(consumer_configs))
    
    total_processed = sum(r["items_processed"] for r in results)
    print(f"\nTotal items processed: {total_processed}")
    for r in results:
        print(f"  Worker {r['worker_id']}: {r['items_processed']} items")


if __name__ == "__main__":
    simple_queue_example()
    pipeline_example()
    parallel_consumers_example()
