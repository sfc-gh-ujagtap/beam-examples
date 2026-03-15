"""
Parallel Map Example
====================
Distribute work across multiple workers using .map()
Great for batch processing, data pipelines, etc.

Run: python parallel_map.py
"""

from beam import function, Image


@function(
    name="parallel-processor",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
)
def process_item(item: dict):
    """
    Process a single item. Called in parallel by .map()
    """
    import time
    import hashlib
    
    time.sleep(0.5)  # Simulate work
    
    item_id = item.get("id", 0)
    data = item.get("data", "")
    
    processed = hashlib.sha256(data.encode()).hexdigest()[:16]
    
    return {
        "id": item_id,
        "original": data,
        "processed": processed,
        "status": "complete",
    }


@function(
    name="image-processor",
    cpu=2,
    memory="2Gi",
    image=Image(python_version="python3.11").add_python_packages([
        "pillow",
        "numpy",
    ]),
)
def process_image(image_config: dict):
    """
    Process images in parallel.
    """
    import numpy as np
    from PIL import Image as PILImage
    import io
    import base64
    
    width = image_config.get("width", 100)
    height = image_config.get("height", 100)
    operation = image_config.get("operation", "grayscale")
    
    img_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    img = PILImage.fromarray(img_array)
    
    if operation == "grayscale":
        img = img.convert("L")
    elif operation == "rotate":
        img = img.rotate(90)
    elif operation == "flip":
        img = img.transpose(PILImage.FLIP_LEFT_RIGHT)
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    
    return {
        "width": width,
        "height": height,
        "operation": operation,
        "size_bytes": len(buffer.getvalue()),
    }


if __name__ == "__main__":
    print("Processing items in parallel with .map()...")
    
    items = [
        {"id": 1, "data": "hello"},
        {"id": 2, "data": "world"},
        {"id": 3, "data": "beam"},
        {"id": 4, "data": "cloud"},
        {"id": 5, "data": "parallel"},
    ]
    
    results = list(process_item.map(items))
    
    print(f"\nProcessed {len(results)} items:")
    for result in results:
        print(f"  - ID {result['id']}: {result['original']} -> {result['processed']}")
    
    print("\n\nProcessing images in parallel...")
    
    image_configs = [
        {"width": 100, "height": 100, "operation": "grayscale"},
        {"width": 200, "height": 150, "operation": "rotate"},
        {"width": 150, "height": 150, "operation": "flip"},
    ]
    
    image_results = list(process_image.map(image_configs))
    
    print(f"\nProcessed {len(image_results)} images:")
    for result in image_results:
        print(f"  - {result['width']}x{result['height']} {result['operation']}: {result['size_bytes']} bytes")
