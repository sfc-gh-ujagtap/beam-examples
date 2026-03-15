"""
Basic Task Queue Example
========================
Async tasks for operations that take longer than 180 seconds
or need to run in the background.

Deploy: beam deploy basic_task.py:process_data
"""

from beam import task_queue, Image


@task_queue(
    name="data-processor",
    cpu=2,
    memory="2Gi",
    image=Image(python_version="python3.11").add_python_packages([
        "pandas",
        "numpy",
    ]),
)
def process_data(**inputs):
    """
    Background data processing task.
    
    Submit task:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"rows": 10000, "columns": 50}'
    
    Response contains task_id to check status later.
    """
    import pandas as pd
    import numpy as np
    import time
    
    rows = inputs.get("rows", 1000)
    columns = inputs.get("columns", 10)
    
    start = time.time()
    
    df = pd.DataFrame(
        np.random.randn(rows, columns),
        columns=[f"col_{i}" for i in range(columns)]
    )
    
    stats = {
        "mean": df.mean().to_dict(),
        "std": df.std().to_dict(),
        "min": df.min().to_dict(),
        "max": df.max().to_dict(),
    }
    
    time.sleep(2)  # Simulate processing time
    
    elapsed = time.time() - start
    
    return {
        "rows_processed": rows,
        "columns": columns,
        "processing_time_seconds": round(elapsed, 2),
        "summary_stats": {
            "overall_mean": float(df.values.mean()),
            "overall_std": float(df.values.std()),
        },
    }


@task_queue(
    name="batch-processor",
    cpu=1,
    memory="1Gi",
    image=Image(python_version="python3.11"),
)
def batch_process(**inputs):
    """
    Process items in batch with progress tracking.
    """
    import time
    
    items = inputs.get("items", [1, 2, 3, 4, 5])
    results = []
    
    for i, item in enumerate(items):
        time.sleep(0.5)
        results.append({
            "item": item,
            "processed": item * 2,
            "index": i,
        })
    
    return {
        "total_items": len(items),
        "results": results,
    }
