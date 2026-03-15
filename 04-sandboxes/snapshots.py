"""
Sandbox Snapshots Example
=========================
Create snapshots of sandbox state and restore from them.
Great for checkpointing, caching setup, fast restarts.

Run: python snapshots.py
"""

from beam import Sandbox, Image, PythonVersion
import time


def create_and_snapshot():
    """Create a sandbox, set it up, and take a snapshot."""
    print("Creating sandbox and setting up environment...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311).add_python_packages([
            "numpy",
            "pandas",
        ])
    )
    
    sb = sandbox.create()
    
    sb.process.run_code("""
import os
os.makedirs('/workspace/data', exist_ok=True)
os.makedirs('/workspace/models', exist_ok=True)
os.makedirs('/workspace/config', exist_ok=True)

with open('/workspace/config/settings.json', 'w') as f:
    import json
    json.dump({
        'model_version': '1.0',
        'batch_size': 32,
        'learning_rate': 0.001
    }, f)

import numpy as np
model_weights = np.random.randn(100, 50)
np.save('/workspace/models/weights.npy', model_weights)

import pandas as pd
df = pd.DataFrame({
    'id': range(1000),
    'value': np.random.randn(1000)
})
df.to_parquet('/workspace/data/dataset.parquet')

print("Environment setup complete!")
print("Files created:")
import subprocess
subprocess.run(['find', '/workspace', '-type', 'f'])
""")
    
    print("\nCreating filesystem snapshot (image)...")
    image_id = sb.create_image_from_filesystem()
    print(f"Image created: {image_id}")
    
    sb.terminate()
    
    return image_id


def restore_from_image(image_id: str):
    """Restore a sandbox from a filesystem image."""
    print(f"\nRestoring sandbox from image: {image_id}")
    
    sandbox = Sandbox(
        image=Image(image_id=image_id),  # Use Image with image_id parameter
    )
    
    sb = sandbox.create()
    print(f"Sandbox restored: {sb.container_id}")
    
    result = sb.process.run_code("""
import os
import json
import numpy as np
import pandas as pd

with open('/workspace/config/settings.json', 'r') as f:
    config = json.load(f)
print(f"Config: {config}")

weights = np.load('/workspace/models/weights.npy')
print(f"Model weights shape: {weights.shape}")

df = pd.read_parquet('/workspace/data/dataset.parquet')
print(f"Dataset shape: {df.shape}")
print(f"Dataset stats: mean={df['value'].mean():.3f}, std={df['value'].std():.3f}")
""")
    print(f"Restored data:\n{result.result}")
    
    sb.terminate()


def snapshot_workflow():
    """Complete workflow: setup -> snapshot -> modify -> restore."""
    print("=" * 50)
    print("Snapshot Workflow Demo")
    print("=" * 50)
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311)
    )
    
    sb = sandbox.create()
    
    print("\n1. Initial setup...")
    sb.process.run_code("""
with open('/workspace/counter.txt', 'w') as f:
    f.write('0')
print("Counter initialized to 0")
""")
    
    print("\n2. Taking filesystem snapshot...")
    image_id = sb.create_image_from_filesystem()
    print(f"Image ID: {image_id}")
    
    print("\n3. Modifying state...")
    sb.process.run_code("""
with open('/workspace/counter.txt', 'r') as f:
    count = int(f.read())
count += 100
with open('/workspace/counter.txt', 'w') as f:
    f.write(str(count))
print(f"Counter updated to {count}")
""")
    
    result = sb.process.run_code("""
with open('/workspace/counter.txt', 'r') as f:
    print(f"Current counter value: {f.read()}")
""")
    print(f"After modification: {result.result}")
    
    sb.terminate()
    
    print("\n4. Restoring from image...")
    sandbox_restored = Sandbox(image=Image(image_id=image_id))
    sb_restored = sandbox_restored.create()
    
    result = sb_restored.process.run_code("""
with open('/workspace/counter.txt', 'r') as f:
    print(f"Restored counter value: {f.read()}")
""")
    print(f"After restore: {result.result}")
    
    sb_restored.terminate()
    print("\nWorkflow complete!")


if __name__ == "__main__":
    snapshot_workflow()
    
    print("\n" + "=" * 50)
    print("Full Snapshot Example")
    print("=" * 50)
    
    image_id = create_and_snapshot()
    restore_from_image(image_id)
