# Beam.cloud Examples

A comprehensive collection of tested examples demonstrating Beam.cloud's serverless GPU infrastructure capabilities. Each folder contains production-ready Python code with detailed explanations and deployment commands.

## What is Beam.cloud?

Beam.cloud is a serverless platform for running Python code in the cloud with:
- **Instant GPU access** - A10G, H100, RTX4090, T4 GPUs on-demand
- **Sub-second cold starts** - Sandboxes boot in 1-3 seconds
- **Auto-scaling** - Scale from 0 to thousands of workers
- **Pay-per-use** - Only pay for compute time used

## Quick Start

```bash
# Install the Beam client
pip install beam-client

# Configure your API token (get it from https://beam.cloud)
beam configure default --token [YOUR_TOKEN]

# Deploy your first endpoint
beam deploy 01-endpoints/basic_endpoint.py:handler

# Or run in dev mode with live reload
beam serve 01-endpoints/basic_endpoint.py:handler
```

---

## Examples Overview

### 01-endpoints - REST APIs

**What it demonstrates:** Synchronous HTTP endpoints that respond within 180 seconds. Use `@endpoint` for request-response patterns like REST APIs.

| File | Description | Key Features |
|------|-------------|--------------|
| `basic_endpoint.py` | Math operations API | Input validation, error handling |
| `gpu_endpoint.py` | GPU matrix multiplication | CUDA acceleration, torch integration |
| `streaming_endpoint.py` | Server-Sent Events | Real-time streaming responses |

**Key Beam Features Used:**
- `@endpoint` decorator for HTTP APIs
- Custom `Image` with Python packages
- CPU/memory resource allocation
- GPU assignment (`gpu="A10G"`)

**Deploy & Test:**
```bash
# Deploy
beam deploy 01-endpoints/basic_endpoint.py:handler

# Test
curl -X POST "https://[DEPLOYMENT_URL]" \
  -H "Authorization: Bearer $BEAM_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"operation": "multiply", "a": 5, "b": 3}'
```

---

### 02-task-queues - Background Jobs

**What it demonstrates:** Asynchronous tasks for operations that take longer than 180 seconds or need to run in the background. Returns a task ID immediately for status polling.

| File | Description | Key Features |
|------|-------------|--------------|
| `basic_task.py` | Async data processing | Pandas/NumPy batch processing |
| `task_with_callback.py` | Webhook on completion | HTTP callbacks when done |
| `long_running_task.py` | Extended timeout tasks | Tasks running 10+ minutes |

**Key Beam Features Used:**
- `@task_queue` decorator for async jobs
- Task ID for status tracking
- Callback URLs for completion notifications
- Extended timeouts for long operations

**How Task Queues Work:**
1. Submit task → Get task ID immediately
2. Task runs in background
3. Poll status or receive webhook callback
4. Retrieve results when complete

```bash
# Submit task
curl -X POST "https://[ENDPOINT]" \
  -H "Authorization: Bearer $BEAM_API_TOKEN" \
  -d '{"rows": 10000}'
# Returns: {"task_id": "abc123"}

# Check status
curl "https://api.beam.cloud/v2/task/abc123/" \
  -H "Authorization: Bearer $BEAM_API_TOKEN"
```

---

### 03-functions - Direct Invocation

**What it demonstrates:** Functions for programmatic invocation from Python code using `.remote()` and `.map()`. No HTTP overhead - direct function calls.

| File | Description | Key Features |
|------|-------------|--------------|
| `basic_function.py` | `.remote()` calls | Direct Python invocation |
| `parallel_map.py` | `.map()` parallel processing | Fan-out across workers |
| `scheduled_job.py` | Cron-scheduled tasks | Recurring scheduled execution |

**Key Beam Features Used:**
- `@function` decorator
- `.remote()` for single invocations
- `.map()` for parallel processing across items
- `Schedule` for cron-based execution

**Usage Patterns:**
```python
from beam import function, Image

@function(cpu=2, memory="2Gi", image=Image(...))
def compute(data: list):
    return sum(data)

# Single call
result = compute.remote(data=[1, 2, 3, 4, 5])

# Parallel processing (fan-out)
items = [{"id": i} for i in range(100)]
results = list(compute.map(items))  # Runs in parallel!
```

---

### 04-sandboxes - Code Execution Environments

**What it demonstrates:** Ephemeral, isolated execution environments with ultra-fast boot times. Perfect for AI agents, code interpreters, and dynamic code execution.

| File | Description | Key Features |
|------|-------------|--------------|
| `basic_sandbox.py` | Create and run code | Dynamic code execution |
| `sandbox_with_gpu.py` | GPU-accelerated sandbox | CUDA in sandboxes |
| `file_operations.py` | Upload/download files | File I/O operations |
| `process_management.py` | Shell commands, background tasks | Process control |
| `port_exposure.py` | Expose HTTP services | Public URLs for services |
| `snapshots.py` | Save/restore filesystem state | Checkpoint/restore |

**Key Beam Features Used:**
- `Sandbox` class for ephemeral environments
- `sb.process.run_code()` for Python execution
- `sb.process.exec()` for shell commands
- `sb.fs.upload_file()` / `sb.fs.download_file()`
- `sb.expose_port()` for public URLs
- `sb.create_image_from_filesystem()` for snapshots
- TTL (time-to-live) for auto-termination

**Performance Characteristics:**
- Cold boot: **1-3 seconds**
- GPU availability: NVIDIA A10G (24GB), H100 (80GB)
- Exposed URL format: `https://{sandbox-id}-{port}.app.beam.cloud`

**Example - AI Agent Code Execution:**
```python
from beam import Sandbox, Image, PythonVersion

sandbox = Sandbox(
    image=Image(python_version=PythonVersion.Python311)
        .add_python_packages(["pandas", "numpy"])
)

sb = sandbox.create()

# Execute user code safely
result = sb.process.run_code("""
import pandas as pd
df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
print(df.describe())
""")

print(result.result)
sb.terminate()
```

---

### 05-web-servers - Web Applications

**What it demonstrates:** Full web applications with ASGI/WSGI support. Deploy Flask, FastAPI, Streamlit, or any Python web framework.

| File | Description | Key Features |
|------|-------------|--------------|
| `flask_server.py` | Flask REST API | WSGI-to-ASGI conversion |
| `fastapi_server.py` | FastAPI with docs | Auto OpenAPI docs, async |
| `streamlit_app.py` | Streamlit dashboard | Interactive data apps |

**Key Beam Features Used:**
- `@asgi` decorator for web apps
- `authorized=False` for public endpoints
- `keep_warm_seconds` to reduce cold starts
- Custom HTML templates

**FastAPI with Auto-Generated Docs:**
```python
from beam import asgi, Image

@asgi(
    name="my-api",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11")
        .add_python_packages(["fastapi", "uvicorn"]),
    authorized=False,  # Public access
)
def create_app(context):
    from fastapi import FastAPI
    app = FastAPI(title="My API")
    
    @app.get("/")
    async def root():
        return {"message": "Hello World"}
    
    return app
```

---

### 06-pods - Long-Running Containers

**What it demonstrates:** Persistent containers that stay running continuously. Unlike endpoints/functions, Pods don't scale to zero - they're always on.

| File | Description | Key Features |
|------|-------------|--------------|
| `basic_pod.py` | Persistent HTTP server | Flask, Redis, PostgreSQL |
| `nextjs_pod.py` | Next.js application | Node.js, Express.js |

**Key Beam Features Used:**
- `Pod` class for long-running containers
- Custom Docker images (`from_registry`)
- Port exposure
- Environment variables
- Inline entrypoint scripts

**Use Cases:**
- Databases (Redis, PostgreSQL)
- WebSocket servers
- Full-stack web apps (Next.js, Express)
- Services requiring persistent connections

**Example - Redis Pod:**
```python
from beam import Pod, Image

pod = Pod(
    name="redis-cache",
    image=Image().from_registry("redis:7-alpine"),
    cpu=1,
    memory="256Mi",
    ports=[6379],
    entrypoint=["redis-server", "--protected-mode", "no"],
)

result = pod.create()
print(f"Redis running at: {result.url}")
```

---

### 07-storage - Persistent Storage

**What it demonstrates:** Persistent storage options for data that needs to survive across function invocations.

| File | Description | Key Features |
|------|-------------|--------------|
| `volumes.py` | Beam volumes | Persistent file storage |
| `s3_mounting.py` | Mount S3 buckets | Direct S3 access |
| `ephemeral_output.py` | Temporary output storage | Output URLs for results |

**Key Beam Features Used:**
- `Volume` for persistent storage across invocations
- S3 bucket mounting
- `Output` for ephemeral result files with URLs

**Volume Commands:**
```bash
# Create a volume
beam volume create my-data

# Upload files
beam cp ./local-file.txt beam://my-data/

# List contents
beam ls my-data

# Download files
beam cp beam://my-data/file.txt ./local/
```

**Using Volumes in Code:**
```python
from beam import function, Volume, Image

@function(
    volumes=[Volume(name="model-weights", mount_path="./models")],
    image=Image(python_version="python3.11"),
)
def load_model():
    # Files in ./models persist across invocations
    import os
    return os.listdir("./models")
```

---

### 08-scaling - Concurrency & Distribution

**What it demonstrates:** Scaling patterns for high-throughput workloads.

| File | Description | Key Features |
|------|-------------|--------------|
| `concurrency.py` | Multiple workers | Concurrent request handling |
| `batch_processing.py` | Batch and async handlers | Efficient processing |
| `distributed_map.py` | Parallel map operations | Fan-out processing |
| `distributed_queue.py` | Queue-based distribution | Work queue patterns |

**Key Beam Features Used:**
- `workers` parameter for horizontal scaling
- `.map()` for parallel fan-out
- Queue-based work distribution
- Async handlers for I/O-bound work

**Scaling Patterns:**

1. **Horizontal Scaling** - Multiple containers handling requests:
```python
@endpoint(workers=4)  # 4 containers handling requests in parallel
def handler(**inputs):
    ...
```

2. **Fan-Out with Map** - Process items in parallel:
```python
items = [{"id": i} for i in range(1000)]
results = list(process_item.map(items))  # Distributed across workers
```

---

### 09-advanced - Advanced Features

**What it demonstrates:** Advanced Beam features for production deployments.

| File | Description | Key Features |
|------|-------------|--------------|
| `preload_models.py` | Load models on startup | `on_start` hook |
| `keep_warm.py` | Keep containers warm | Reduced cold starts |
| `secrets.py` | Environment secrets | Secure credential storage |

**Key Beam Features Used:**

**1. Model Preloading (`on_start`):**
```python
def load_model():
    from transformers import pipeline
    return pipeline("sentiment-analysis")

@endpoint(on_start=load_model)
def predict(context, **inputs):
    model = context.on_start_value  # Model loaded once, reused
    return model(inputs["text"])
```

**2. Keep Warm:**
```python
@endpoint(keep_warm_seconds=300)  # Keep container alive for 5 min
def handler(**inputs):
    ...
```

**3. Secrets Management:**
```bash
# Create secrets
beam secret create OPENAI_API_KEY "sk-..."
beam secret create DATABASE_URL "postgresql://..."
```
```python
@endpoint(secrets=["OPENAI_API_KEY", "DATABASE_URL"])
def handler(**inputs):
    import os
    api_key = os.environ["OPENAI_API_KEY"]
```

---

### 10-ml-examples - Machine Learning

**What it demonstrates:** Production ML inference patterns with popular frameworks.

| File | Description | Key Features |
|------|-------------|--------------|
| `huggingface_inference.py` | HuggingFace models | Transformers, sentiment, NER |
| `vllm_server.py` | vLLM inference server | High-throughput LLM serving |
| `whisper_transcription.py` | Audio transcription | OpenAI Whisper |

**Key Beam Features Used:**
- GPU allocation for inference
- Model caching with Volumes
- `on_start` for model preloading
- `keep_warm_seconds` for low latency

**Example - HuggingFace Sentiment Analysis:**
```python
from beam import endpoint, Image, Volume

def load_model():
    from transformers import pipeline
    return pipeline("sentiment-analysis", device=0)

@endpoint(
    gpu="A10G",
    on_start=load_model,
    keep_warm_seconds=300,
    volumes=[Volume(name="hf-cache", mount_path="./cache")],
)
def sentiment(context, **inputs):
    model = context.on_start_value
    return model(inputs["text"])
```

---

## GPU Options

| GPU | Memory | Best For | Config |
|-----|--------|----------|--------|
| T4 | 16GB | Light inference, testing | `gpu="T4"` |
| A10G | 24GB | Most ML workloads | `gpu="A10G"` |
| RTX4090 | 24GB | High-performance inference | `gpu="RTX4090"` |
| H100 | 80GB | Large models, training | `gpu="H100"` |

```bash
# Check GPU availability
beam machine list
```

---

## CLI Reference

```bash
# Deployment
beam deploy app.py:handler          # Deploy to production
beam serve app.py:handler           # Dev mode with live reload

# Management
beam deployment list                # List all deployments
beam deployment stop <id>           # Stop a deployment
beam logs <deployment-id>           # View logs

# Volumes
beam volume create <name>           # Create persistent volume
beam volume list                    # List volumes
beam cp local.txt beam://vol/       # Upload to volume
beam ls <volume-name>               # List volume contents

# Secrets
beam secret create KEY "value"      # Create secret
beam secret list                    # List secrets
beam secret delete KEY              # Delete secret

# Debugging
beam machine list                   # Available GPU types
beam task list                      # List running tasks
```

---

## Architecture Patterns

### Pattern 1: Sync API (< 180s response)
```
Client → @endpoint → Response
```

### Pattern 2: Async Processing (> 180s)
```
Client → @task_queue → Task ID
         ↓
      Background Processing
         ↓
      Callback/Poll for Result
```

### Pattern 3: Fan-Out Processing
```
Client → @function.map([items]) → Parallel Workers → Aggregated Results
```

### Pattern 4: AI Agent with Sandboxes
```
Agent → Sandbox.create() → Execute Code → Get Results → Sandbox.terminate()
```

---

## Resources

- [Beam Documentation](https://docs.beam.cloud)
- [API Reference](https://docs.beam.cloud/v2/api-reference)
- [GPU Guide](https://docs.beam.cloud/v2/environment/gpu)
- [Pricing](https://docs.beam.cloud/v2/resources/pricing-and-billing)
- [Discord Community](https://discord.gg/beam-cloud)

---

## License

MIT License - Feel free to use these examples as starting points for your own projects.
