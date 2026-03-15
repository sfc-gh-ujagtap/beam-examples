# Sandboxes

Sandboxes are ultra-fast, ephemeral code execution environments. Cold boot in 1-3 seconds. Perfect for AI agents, code interpreters, and dynamic workloads.

## Examples

| File | Description | Status |
|------|-------------|--------|
| `basic_sandbox.py` | Create, run code, terminate | ✅ Tested |
| `sandbox_with_gpu.py` | GPU-accelerated sandboxes | ✅ Tested |
| `file_operations.py` | Upload, download, manage files | ✅ Tested |
| `process_management.py` | Shell commands, background processes | ✅ Tested |
| `port_exposure.py` | Expose services to the internet | ✅ Tested |
| `snapshots.py` | Save and restore sandbox state | ✅ Tested |

## Test Results

### basic_sandbox.py

**Run:** `python basic_sandbox.py`

| Test | Description | Result |
|------|-------------|--------|
| `basic_example()` | Create sandbox, run code | ✅ "Hello from the sandbox!" |
| `sandbox_with_packages()` | Sandbox with numpy/pandas | ✅ DataFrame created |
| `sandbox_with_ttl()` | Auto-termination | ✅ TTL set to 300s |

**System Info from Sandbox:**
```
Python: 3.11.11
Platform: Linux-5.15.0-164-generic-x86_64-with-glibc2.35
Processor: x86_64
```

| Metric | Value |
|--------|-------|
| Sandbox Creation | ~3-5s (cached image) |
| Code Execution | <1s |
| Default Timeout | 600s |

---

### file_operations.py

**Run:** `python file_operations.py`

| Test | Description | Result |
|------|-------------|--------|
| `upload_and_process()` | Upload CSV, process with pandas, download | ✅ |
| `upload_script_and_run()` | Upload Python script, execute | ✅ |
| `list_files()` | Create and list files | ✅ |

**File Processing Example:**
```
Input CSV:
  name,value
  alpha,10
  beta,20
  gamma,30

Output CSV (processed in sandbox):
  name,value,doubled,squared
  alpha,10,20,100
  beta,20,40,400
  gamma,30,60,900
```

---

### port_exposure.py

**Run:** `python port_exposure.py`

| Test | Description | Result |
|------|-------------|--------|
| HTTP Server | Expose port 8000 | ✅ Status 200 |

**Exposed URL Format:**
```
https://{sandbox-id}-{port}.app.beam.cloud
```

**Example:**
```
https://8b6d71ce-2857-4fab-8988-1c2f69cdbf79-8000.app.beam.cloud
```

---

### process_management.py

**Run:** `python process_management.py`

| Test | Description | Result |
|------|-------------|--------|
| Shell commands | Run `ls -la /`, `echo`, `cat /etc/os-release` | ✅ Ubuntu 22.04.5 LTS |
| Background process | Run long task, stream logs | ✅ Processed 10/10 items |
| Working directory | Run commands in specific dirs | ✅ "Hello from src directory!" |
| Runtime packages | Install requests, make HTTP call | ✅ Status 200, fetched data |

**OS Info from Sandbox:**
```
PRETTY_NAME="Ubuntu 22.04.5 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
```

---

### sandbox_with_gpu.py

**Run:** `python sandbox_with_gpu.py`

| Test | Description | Result |
|------|-------------|--------|
| GPU detection | Check CUDA availability | ✅ NVIDIA A10 detected |
| Matrix multiplication | 5000x5000 matmul benchmark | ✅ 0.434s on CUDA |
| ML inference | Sentiment analysis with transformers | ✅ 3 texts classified |

**GPU Info:**
```
Device: cuda
GPU: NVIDIA A10
Memory: 23.7 GB
```

**Benchmark:**
```
Matrix multiplication (5000x5000): 0.434s on cuda
```

**Sentiment Analysis Results:**
```
POSITIVE (0.99): I love using Beam for ML inference!
NEGATIVE (1.00): This is terrible and I hate it.
POSITIVE (1.00): The weather is okay today.
```

| Metric | Value |
|--------|-------|
| GPU Sandbox Creation | ~3-5s (cached image) |
| ML Model Loading | ~10-15s (first time) |
| Inference Time | <1s per batch |

---

### snapshots.py

**Run:** `python snapshots.py`

| Test | Description | Result |
|------|-------------|--------|
| Create snapshot | `create_image_from_filesystem()` | ✅ Image ID returned |
| Restore from snapshot | Create new sandbox from image | ✅ State restored |
| Workflow demo | Init→Snapshot→Modify→Restore | ✅ Counter reset to 0 |

**Snapshot Workflow:**
```
1. Initial setup: Counter = 0
2. Take filesystem snapshot → Image ID: xxx-1773592573
3. Modify state: Counter = 100
4. Restore from snapshot
5. Verify: Counter = 0 ✅ (state restored!)
```

**API Notes:**
- Use `sb.create_image_from_filesystem()` to snapshot filesystem state
- Use `Image(image_id=image_id)` to restore from snapshot
- Filesystem snapshots don't include installed packages (use base image for that)

---

## Quick Start

```python
from beam import Sandbox, Image, PythonVersion

# Create a sandbox
sandbox = Sandbox(
    image=Image(python_version=PythonVersion.Python311)
)
sb = sandbox.create()

# Run code
result = sb.process.run_code("print('Hello!')")
print(result.result)

# Clean up
sb.terminate()
```

## Key Features

### Process Management
```python
# Run Python code
result = sb.process.run_code("print('Hello!')")

# Execute shell commands
process = sb.process.exec("ls", "-la")
print(process.logs.read())

# Run in specific directory
process = sb.process.exec("python", "main.py", cwd="/workspace/src")
```

### File Operations
```python
# Upload files
sb.fs.upload_file("local.py", "/workspace/script.py")

# Download files
sb.fs.download_file("/workspace/output.csv", "local_output.csv")
```

### Port Exposure
```python
# Start a server
sb.process.exec("python3", "-m", "http.server", "8000")

# Expose to internet
url = sb.expose_port(8000)
print(f"Server at: {url}")
```

### Snapshots (Filesystem Images)
```python
# Save filesystem state
image_id = sb.create_image_from_filesystem()

# Restore later
sandbox_restored = Sandbox(image=Image(image_id=image_id))
sb_restored = sandbox_restored.create()
```

### TTL (Auto-termination)
```python
# Auto-terminate after 5 minutes
sb.update_ttl(300)
```

## Configuration Options

| Parameter | Description | Example |
|-----------|-------------|---------|
| `image` | Container image | `Image(python_version=...)` |
| `cpu` | CPU cores | `1`, `2`, `4` |
| `memory` | RAM | `"512Mi"`, `"8Gi"` |
| `gpu` | GPU type | `"A10G"`, `"H100"` |
