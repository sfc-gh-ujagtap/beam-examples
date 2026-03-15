"""
Ephemeral Output Example
========================
Store temporary files (images, audio, etc.) that are
accessible via URL after task completion.

Deploy: beam deploy ephemeral_output.py:generate_image
"""

from beam import task_queue, Image, Output


@task_queue(
    name="image-generator",
    cpu=1,
    memory="1Gi",
    image=Image(python_version="python3.11").add_python_packages([
        "pillow",
        "numpy",
    ]),
)
def generate_image(**inputs):
    """
    Generate an image and save it as ephemeral output.
    The output URL is included in the task result.
    
    Submit:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"width": 512, "height": 512, "pattern": "gradient"}'
    """
    from PIL import Image as PILImage
    import numpy as np
    
    width = inputs.get("width", 256)
    height = inputs.get("height", 256)
    pattern = inputs.get("pattern", "noise")
    
    if pattern == "noise":
        arr = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    elif pattern == "gradient":
        x = np.linspace(0, 255, width, dtype=np.uint8)
        y = np.linspace(0, 255, height, dtype=np.uint8)
        arr = np.zeros((height, width, 3), dtype=np.uint8)
        arr[:, :, 0] = x
        arr[:, :, 1] = y.reshape(-1, 1)
        arr[:, :, 2] = 128
    elif pattern == "checkerboard":
        arr = np.zeros((height, width, 3), dtype=np.uint8)
        block_size = 32
        for i in range(0, height, block_size):
            for j in range(0, width, block_size):
                if (i // block_size + j // block_size) % 2 == 0:
                    arr[i:i+block_size, j:j+block_size] = 255
    else:
        arr = np.zeros((height, width, 3), dtype=np.uint8)
        arr[:, :] = [100, 149, 237]
    
    img = PILImage.fromarray(arr)
    
    output_path = "/tmp/generated_image.png"
    img.save(output_path)
    
    Output(path=output_path).save()
    
    return {
        "width": width,
        "height": height,
        "pattern": pattern,
        "output_file": "generated_image.png",
    }


@task_queue(
    name="report-generator",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11").add_python_packages([
        "pandas",
    ]),
)
def generate_report(**inputs):
    """
    Generate a CSV report and save as ephemeral output.
    """
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    rows = inputs.get("rows", 100)
    
    dates = [datetime.now() - timedelta(days=i) for i in range(rows)]
    df = pd.DataFrame({
        "date": dates,
        "sales": np.random.randint(100, 1000, rows),
        "customers": np.random.randint(10, 100, rows),
        "revenue": np.random.uniform(1000, 10000, rows).round(2),
    })
    
    output_path = "/tmp/sales_report.csv"
    df.to_csv(output_path, index=False)
    
    Output(path=output_path).save()
    
    return {
        "rows": rows,
        "columns": list(df.columns),
        "output_file": "sales_report.csv",
        "total_revenue": float(df["revenue"].sum()),
    }


@task_queue(
    name="multi-output",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11").add_python_packages([
        "pillow",
        "pandas",
    ]),
)
def generate_multiple_outputs(**inputs):
    """
    Generate multiple output files from a single task.
    """
    from PIL import Image as PILImage
    import pandas as pd
    import numpy as np
    import json
    
    arr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    img = PILImage.fromarray(arr)
    img.save("/tmp/thumbnail.png")
    Output(path="/tmp/thumbnail.png").save()
    
    df = pd.DataFrame({
        "id": range(10),
        "value": np.random.randn(10),
    })
    df.to_csv("/tmp/data.csv", index=False)
    Output(path="/tmp/data.csv").save()
    
    metadata = {
        "generated_at": str(datetime.now()) if 'datetime' in dir() else "now",
        "files": ["thumbnail.png", "data.csv"],
    }
    with open("/tmp/metadata.json", "w") as f:
        json.dump(metadata, f)
    Output(path="/tmp/metadata.json").save()
    
    return {
        "outputs": ["thumbnail.png", "data.csv", "metadata.json"],
        "status": "complete",
    }


if __name__ == "__main__":
    print("Ephemeral Output Examples")
    print("=" * 50)
    print("\nSubmit tasks to generate outputs:")
    print("  generate_image.remote(width=512, height=512, pattern='gradient')")
    print("  generate_report.remote(rows=1000)")
