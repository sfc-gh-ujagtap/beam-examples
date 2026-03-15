"""
Distributed Map Example
=======================
Process collections in parallel across multiple workers.
Great for batch processing, ETL, and data pipelines.

Run: python distributed_map.py
"""

from beam import function, Image, Map


@function(
    name="item-processor",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
)
def process_item(item: dict):
    """
    Process a single item. Called by Map in parallel.
    """
    import time
    import hashlib
    
    time.sleep(0.2)
    
    item_id = item.get("id")
    data = item.get("data", "")
    
    processed = hashlib.sha256(data.encode()).hexdigest()[:8]
    
    return {
        "id": item_id,
        "original": data,
        "hash": processed,
    }


@function(
    name="image-resizer",
    cpu=2,
    memory="2Gi",
    image=Image(python_version="python3.11").add_python_packages([
        "pillow",
        "numpy",
    ]),
)
def resize_image(config: dict):
    """
    Resize images in parallel.
    """
    from PIL import Image as PILImage
    import numpy as np
    import io
    
    width = config.get("width", 100)
    height = config.get("height", 100)
    target_width = config.get("target_width", 50)
    target_height = config.get("target_height", 50)
    
    arr = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    img = PILImage.fromarray(arr)
    
    resized = img.resize((target_width, target_height), PILImage.LANCZOS)
    
    return {
        "original_size": f"{width}x{height}",
        "new_size": f"{target_width}x{target_height}",
        "reduction": f"{(1 - (target_width * target_height) / (width * height)) * 100:.1f}%",
    }


def batch_process_with_map():
    """Use .map() for parallel processing."""
    print("Processing items with .map()...")
    
    items = [
        {"id": i, "data": f"item_{i}"}
        for i in range(10)
    ]
    
    results = list(process_item.map(items))
    
    print(f"Processed {len(results)} items:")
    for r in results:
        print(f"  {r['id']}: {r['original']} -> {r['hash']}")
    
    return results


def parallel_image_processing():
    """Process multiple images in parallel."""
    print("\nProcessing images in parallel...")
    
    configs = [
        {"width": 1000, "height": 1000, "target_width": 100, "target_height": 100},
        {"width": 800, "height": 600, "target_width": 200, "target_height": 150},
        {"width": 1920, "height": 1080, "target_width": 480, "target_height": 270},
        {"width": 500, "height": 500, "target_width": 50, "target_height": 50},
    ]
    
    results = list(resize_image.map(configs))
    
    print(f"Resized {len(results)} images:")
    for r in results:
        print(f"  {r['original_size']} -> {r['new_size']} ({r['reduction']})")
    
    return results


@function(
    name="aggregator",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
)
def aggregate_results(results: list):
    """Aggregate results from parallel processing."""
    return {
        "total_items": len(results),
        "ids": [r.get("id") for r in results if r.get("id") is not None],
    }


def map_reduce_pattern():
    """Map-reduce pattern: process in parallel, then aggregate."""
    print("\nMap-Reduce pattern...")
    
    items = [{"id": i, "data": f"data_{i}"} for i in range(5)]
    mapped_results = list(process_item.map(items))
    
    final_result = aggregate_results.remote(results=mapped_results)
    
    print(f"Aggregated result: {final_result}")
    return final_result


if __name__ == "__main__":
    print("=" * 50)
    print("Distributed Map Examples")
    print("=" * 50)
    
    batch_process_with_map()
    parallel_image_processing()
    map_reduce_pattern()
