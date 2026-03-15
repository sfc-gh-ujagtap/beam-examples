"""
S3 Bucket Mounting Example
==========================
Mount external S3 buckets for large datasets.
Access cloud storage directly from your Beam functions.

Deploy: beam deploy s3_mounting.py:process_s3_data
"""

from beam import function, Image, CloudBucket, CloudBucketConfig


S3_MOUNT_PATH = "./s3_data"


@function(
    name="s3-processor",
    cpu=2,
    memory="4Gi",
    image=Image(python_version="python3.11").add_python_packages([
        "pandas",
        "pyarrow",
    ]),
    volumes=[
        CloudBucket(
            name="my-s3-bucket",
            mount_path=S3_MOUNT_PATH,
            config=CloudBucketConfig(
                access_key="YOUR_AWS_ACCESS_KEY",
                secret_key="YOUR_AWS_SECRET_KEY",
                region="us-east-1",
            ),
        )
    ],
)
def process_s3_data(file_path: str):
    """
    Process data from an S3 bucket.
    
    Usage:
        result = process_s3_data.remote(file_path="data/sales.parquet")
    """
    import pandas as pd
    import os
    
    full_path = f"{S3_MOUNT_PATH}/{file_path}"
    
    if not os.path.exists(full_path):
        return {"error": f"File not found: {full_path}"}
    
    if file_path.endswith('.parquet'):
        df = pd.read_parquet(full_path)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(full_path)
    else:
        return {"error": "Unsupported file format"}
    
    return {
        "file": file_path,
        "rows": len(df),
        "columns": list(df.columns),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1e6, 2),
    }


@function(
    name="s3-lister",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
    volumes=[
        CloudBucket(
            name="my-s3-bucket",
            mount_path=S3_MOUNT_PATH,
            config=CloudBucketConfig(
                access_key="YOUR_AWS_ACCESS_KEY",
                secret_key="YOUR_AWS_SECRET_KEY",
            ),
        )
    ],
)
def list_s3_contents(prefix: str = ""):
    """List contents of the S3 bucket."""
    import os
    
    search_path = f"{S3_MOUNT_PATH}/{prefix}" if prefix else S3_MOUNT_PATH
    
    files = []
    for root, dirs, filenames in os.walk(search_path):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, S3_MOUNT_PATH)
            files.append({
                "path": rel_path,
                "size_bytes": os.path.getsize(filepath),
            })
    
    return {
        "prefix": prefix,
        "files": files[:100],
        "total_count": len(files),
    }


@function(
    name="s3-writer",
    cpu=1,
    memory="1Gi",
    image=Image(python_version="python3.11").add_python_packages([
        "pandas",
    ]),
    volumes=[
        CloudBucket(
            name="my-s3-bucket",
            mount_path=S3_MOUNT_PATH,
            config=CloudBucketConfig(
                access_key="YOUR_AWS_ACCESS_KEY",
                secret_key="YOUR_AWS_SECRET_KEY",
                read_only=False,
            ),
        )
    ],
)
def write_to_s3(output_path: str, data: list):
    """
    Write data to S3 bucket.
    
    Usage:
        write_to_s3.remote(
            output_path="output/results.csv",
            data=[{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        )
    """
    import pandas as pd
    import os
    
    full_path = f"{S3_MOUNT_PATH}/{output_path}"
    
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    df = pd.DataFrame(data)
    
    if output_path.endswith('.parquet'):
        df.to_parquet(full_path, index=False)
    else:
        df.to_csv(full_path, index=False)
    
    return {
        "written": output_path,
        "rows": len(df),
        "size_bytes": os.path.getsize(full_path),
    }


if __name__ == "__main__":
    print("S3 Mounting Examples")
    print("=" * 50)
    print("Note: Replace AWS credentials with your own before running")
    print("\nExample usage:")
    print("  result = list_s3_contents.remote(prefix='data/')")
    print("  result = process_s3_data.remote(file_path='data/sales.parquet')")
