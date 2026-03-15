# Beam.cloud Examples

Tested examples for Beam.cloud features. Each folder contains working Python files with detailed test results.

## Setup

```bash
pip install beam-client
beam configure default --token [YOUR_TOKEN]
```

## Examples Tested

### 01-endpoints - REST APIs

| File | Description | Command |
|------|-------------|---------|
| `basic_endpoint.py` | Math operations API | `beam deploy 01-endpoints/basic_endpoint.py:handler` |
| `gpu_endpoint.py` | GPU matrix multiplication | `beam deploy 01-endpoints/gpu_endpoint.py:matrix_multiply` |
| `streaming_endpoint.py` | Server-Sent Events | `beam deploy 01-endpoints/streaming_endpoint.py:stream_words` |

**Test with curl:**
```bash
curl -X POST "https://[DEPLOYMENT_URL]" \
  -H "Authorization: Bearer $BEAM_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"operation": "add", "x": 5, "y": 3}'
```

---

### 02-task-queues - Background Jobs

| File | Description | Command |
|------|-------------|---------|
| `basic_task.py` | Async data processing | `beam deploy 02-task-queues/basic_task.py:process_data` |
| `task_with_callback.py` | Webhook on completion | `beam deploy 02-task-queues/task_with_callback.py:process_with_callback` |
| `long_running_task.py` | Extended timeout tasks | `beam deploy 02-task-queues/long_running_task.py:long_task` |

**Check task status:**
```bash
curl -X GET "https://api.beam.cloud/v2/task/{TASK_ID}/" \
  -H "Authorization: Bearer $BEAM_API_TOKEN"
```

---

### 03-functions - Direct Invocation

| File | Description | Command |
|------|-------------|---------|
| `basic_function.py` | `.remote()` calls | `python 03-functions/basic_function.py` |
| `parallel_map.py` | `.map()` parallel processing | `python 03-functions/parallel_map.py` |
| `scheduled_job.py` | Cron-scheduled tasks | `beam deploy 03-functions/scheduled_job.py:hourly_report` |

---

### 04-sandboxes - Code Execution Environments

| File | Description | Command |
|------|-------------|---------|
| `basic_sandbox.py` | Create and run code | `python 04-sandboxes/basic_sandbox.py` |
| `sandbox_with_gpu.py` | GPU-accelerated sandbox | `python 04-sandboxes/sandbox_with_gpu.py` |
| `file_operations.py` | Upload/download files | `python 04-sandboxes/file_operations.py` |
| `process_management.py` | Shell commands, background tasks | `python 04-sandboxes/process_management.py` |
| `port_exposure.py` | Expose HTTP services | `python 04-sandboxes/port_exposure.py` |
| `snapshots.py` | Save/restore filesystem state | `python 04-sandboxes/snapshots.py` |

**Key results:**
- Cold boot: 3-5 seconds
- GPU: NVIDIA A10 (23.7GB)
- Exposed URL format: `https://{sandbox-id}-{port}.app.beam.cloud`

---

### 05-web-servers - Web Applications

| File | Description | Command |
|------|-------------|---------|
| `flask_server.py` | Flask REST API | `beam deploy 05-web-servers/flask_server.py` |
| `fastapi_server.py` | FastAPI with docs | `beam deploy 05-web-servers/fastapi_server.py` |
| `streamlit_app.py` | Streamlit dashboard | `beam deploy 05-web-servers/streamlit_app.py` |

---

### 06-pods - Long-Running Containers

| File | Description | Command |
|------|-------------|---------|
| `basic_pod.py` | Persistent HTTP server | `python 06-pods/basic_pod.py` |
| `nextjs_pod.py` | Next.js application | `python 06-pods/nextjs_pod.py` |

---

### 07-storage - Persistent Storage

| File | Description | Command |
|------|-------------|---------|
| `volumes.py` | Beam volumes | `python 07-storage/volumes.py` |
| `s3_mounting.py` | Mount S3 buckets | `python 07-storage/s3_mounting.py` |
| `ephemeral_output.py` | Temporary output storage | `beam deploy 07-storage/ephemeral_output.py:generate_report` |

**Volume commands:**
```bash
beam volume create my-volume
beam cp file.txt beam://my-volume/
beam ls my-volume
```

---

### 08-scaling - Concurrency & Distribution

| File | Description | Command |
|------|-------------|---------|
| `concurrency.py` | Multiple workers | `beam deploy 08-scaling/concurrency.py:handler` |
| `distributed_map.py` | Parallel map operations | `python 08-scaling/distributed_map.py` |
| `distributed_queue.py` | Queue-based distribution | `beam deploy 08-scaling/distributed_queue.py:process_item` |

---

### 09-advanced - Advanced Features

| File | Description | Command |
|------|-------------|---------|
| `preload_models.py` | Load models on startup | `beam deploy 09-advanced/preload_models.py:predict` |
| `keep_warm.py` | Keep containers warm | `beam deploy 09-advanced/keep_warm.py:handler` |
| `secrets.py` | Environment secrets | `beam deploy 09-advanced/secrets.py:handler` |
| `signals.py` | Inter-app communication | `beam deploy 09-advanced/signals.py:sender` |

**Secrets commands:**
```bash
beam secret create API_KEY "your-secret-value"
beam secret list
```

---

### 10-ml-examples - Machine Learning

| File | Description | Command |
|------|-------------|---------|
| `huggingface_inference.py` | HuggingFace models | `beam deploy 10-ml-examples/huggingface_inference.py:classify` |
| `vllm_server.py` | vLLM inference server | `beam deploy 10-ml-examples/vllm_server.py:generate` |
| `whisper_transcription.py` | Audio transcription | `beam deploy 10-ml-examples/whisper_transcription.py:transcribe` |

---

## GPU Options

| GPU | Memory | Command |
|-----|--------|---------|
| A10G | 24GB | `gpu="A10G"` |
| RTX4090 | 24GB | `gpu="RTX4090"` |
| T4 | 16GB | `gpu="T4"` |
| H100 | 80GB | `gpu="H100"` |

Check availability: `beam machine list`

## Useful Commands

```bash
beam deploy app.py:handler      # Deploy
beam serve app.py:handler       # Local dev with live reload
beam deployment list            # List deployments
beam logs <deployment-id>       # View logs
```

## Resources

- [Beam Documentation](https://docs.beam.cloud)
- [GPU Guide](https://docs.beam.cloud/v2/environment/gpu)
- [Pricing](https://docs.beam.cloud/v2/resources/pricing-and-billing)
