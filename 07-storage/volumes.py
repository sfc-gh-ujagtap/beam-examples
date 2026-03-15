"""
Distributed Volumes Example
===========================
Persistent storage that can be shared across tasks.
Great for model weights, datasets, and shared files.

Deploy: beam deploy volumes.py:save_to_volume
CLI: beam volume create my-volume
"""

from beam import function, Volume, Image


VOLUME_PATH = "./data"


@function(
    name="volume-writer",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11").add_python_packages([
        "pandas",
        "numpy",
    ]),
    volumes=[Volume(name="shared-data", mount_path=VOLUME_PATH)],
)
def save_to_volume(filename: str, data: dict):
    """
    Save data to a persistent volume.
    
    Usage:
        save_to_volume.remote(filename="config.json", data={"key": "value"})
    """
    import json
    import os
    
    os.makedirs(VOLUME_PATH, exist_ok=True)
    
    filepath = f"{VOLUME_PATH}/{filename}"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    
    return {
        "saved": filepath,
        "size_bytes": os.path.getsize(filepath),
    }


@function(
    name="volume-reader",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
    volumes=[Volume(name="shared-data", mount_path=VOLUME_PATH)],
)
def read_from_volume(filename: str):
    """
    Read data from a persistent volume.
    
    Usage:
        data = read_from_volume.remote(filename="config.json")
    """
    import json
    
    filepath = f"{VOLUME_PATH}/{filename}"
    
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        return {"data": data, "filepath": filepath}
    except FileNotFoundError:
        return {"error": f"File not found: {filepath}"}


@function(
    name="volume-list",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
    volumes=[Volume(name="shared-data", mount_path=VOLUME_PATH)],
)
def list_volume_contents():
    """List all files in the volume."""
    import os
    
    files = []
    for root, dirs, filenames in os.walk(VOLUME_PATH):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            files.append({
                "path": filepath,
                "size_bytes": os.path.getsize(filepath),
            })
    
    return {"files": files, "total_count": len(files)}


MODEL_VOLUME_PATH = "./models"


@function(
    name="model-loader",
    cpu=2,
    memory="8Gi",
    gpu="A10G",
    image=Image(python_version="python3.11").add_python_packages([
        "torch",
        "transformers",
    ]),
    volumes=[Volume(name="model-weights", mount_path=MODEL_VOLUME_PATH)],
)
def load_model_from_volume(model_name: str = "bert-base-uncased"):
    """
    Load ML model weights from a volume.
    First run downloads, subsequent runs load from cache.
    """
    from transformers import AutoModel, AutoTokenizer
    import os
    
    cache_dir = f"{MODEL_VOLUME_PATH}/{model_name.replace('/', '_')}"
    os.makedirs(cache_dir, exist_ok=True)
    
    model = AutoModel.from_pretrained(model_name, cache_dir=cache_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    
    files = os.listdir(cache_dir)
    total_size = sum(
        os.path.getsize(os.path.join(cache_dir, f)) 
        for f in files 
        if os.path.isfile(os.path.join(cache_dir, f))
    )
    
    return {
        "model": model_name,
        "cache_dir": cache_dir,
        "files_cached": len(files),
        "total_size_mb": round(total_size / 1e6, 2),
    }


if __name__ == "__main__":
    print("Saving data to volume...")
    result = save_to_volume.remote(
        filename="test_data.json",
        data={"name": "test", "values": [1, 2, 3, 4, 5]}
    )
    print(f"Save result: {result}")
    
    print("\nReading from volume...")
    result = read_from_volume.remote(filename="test_data.json")
    print(f"Read result: {result}")
    
    print("\nListing volume contents...")
    result = list_volume_contents.remote()
    print(f"Contents: {result}")
