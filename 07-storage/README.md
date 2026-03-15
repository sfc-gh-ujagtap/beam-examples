# Storage

Beam provides multiple storage options for different use cases: persistent volumes, cloud bucket mounting, and ephemeral outputs.

## Examples

| File | Description |
|------|-------------|
| `volumes.py` | Persistent distributed storage |
| `s3_mounting.py` | Mount external S3 buckets |
| `ephemeral_output.py` | Temporary files with download URLs |

## Storage Types

### 1. Volumes (Persistent)

Distributed storage shared across all your Beam apps.

```python
from beam import function, Volume

@function(
    volumes=[Volume(name="my-data", mount_path="./data")],
)
def save_data():
    with open("./data/file.txt", "w") as f:
        f.write("Hello!")
```

**CLI Commands:**
```bash
# Create volume
beam volume create my-volume

# Upload files
beam cp local_file.txt beam://my-volume/

# Download files
beam cp beam://my-volume/file.txt ./local/

# List contents
beam ls my-volume

# Delete volume
beam volume delete my-volume
```

### 2. Cloud Buckets (S3)

Mount external S3 buckets for large datasets.

```python
from beam import function, CloudBucket, CloudBucketConfig

@function(
    volumes=[
        CloudBucket(
            name="my-bucket",
            mount_path="./s3",
            config=CloudBucketConfig(
                access_key="...",
                secret_key="...",
            ),
        )
    ],
)
def process():
    # Access S3 files like local files
    with open("./s3/data.csv") as f:
        pass
```

### 3. Ephemeral Output

Temporary files accessible via URL after task completion.

```python
from beam import task_queue, Output

@task_queue()
def generate():
    # Create file
    with open("/tmp/result.png", "wb") as f:
        f.write(image_data)
    
    # Save as output (creates download URL)
    Output(path="/tmp/result.png").save()
    
    return {"status": "done"}
```

## When to Use What

| Storage Type | Use Case | Persistence |
|--------------|----------|-------------|
| Volumes | Model weights, shared data | Permanent |
| S3 Buckets | Large datasets, external data | External |
| Ephemeral | Task outputs, generated files | Temporary |
| `/tmp` | Scratch space | Container lifetime |

## Volume Best Practices

1. **Sync delay**: Files written to volumes may take up to 60 seconds to sync across containers
2. **Model caching**: Store HuggingFace/PyTorch models in volumes to avoid re-downloading
3. **Shared state**: Use volumes for data that needs to be accessed by multiple functions
