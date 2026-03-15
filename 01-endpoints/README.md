# Web Endpoints

Web endpoints are synchronous HTTP APIs that respond within 180 seconds. Use `@endpoint` for request-response patterns.

## Examples

| File | Description | Status |
|------|-------------|--------|
| `basic_endpoint.py` | Simple REST API with math operations | ✅ Tested |
| `gpu_endpoint.py` | GPU-accelerated inference endpoint | ✅ Tested |
| `streaming_endpoint.py` | Server-Sent Events (SSE) streaming | ✅ Tested |

## Test Results

### basic_endpoint.py

**Deployed URL:** `https://basic-math-api-903b82f-v1.app.beam.cloud`

| Metric | Value |
|--------|-------|
| CPU | 1 core |
| Memory | 512Mi |
| Cold Start | ~5-6s |
| Warm Response | <1s |

**Test Cases:**

| Operation | Input | Output | Status |
|-----------|-------|--------|--------|
| multiply | `5 × 3` | `15` | ✅ |
| add | `10 + 20` | `30` | ✅ |
| divide | `100 ÷ 4` | `25.0` | ✅ |
| divide by zero | `10 ÷ 0` | `"Error: Division by zero"` | ✅ |

---

### gpu_endpoint.py

**Deployed URL:** `https://gpu-inference-api-1ebab43-v1.app.beam.cloud`

| Metric | Value |
|--------|-------|
| CPU | 2 cores |
| Memory | 8Gi |
| GPU | NVIDIA A10 (A10G) |
| Build Time | ~108s (first deploy with torch) |
| Cold Start | ~30s |
| Warm Response | ~1s |
| Keep Warm | 300s |

**Test Cases (Matrix Multiplication):**

| Matrix Size | Computation Time | Notes |
|-------------|------------------|-------|
| 1000×1000 | 0.45s | Cold start |
| 5000×5000 | 0.015s | Warm container |

---

### streaming_endpoint.py

**Deployed URLs:**
- `stream_handler`: `https://streaming-api-294c378-v1.app.beam.cloud`
- `progress_handler`: `https://progress-stream-c48eee4-v1.app.beam.cloud`

| Metric | Value |
|--------|-------|
| CPU | 1 core |
| Memory | 512Mi |
| Cold Start | ~8-9s |
| Warm Response | ~1s |

**Test Cases:**

| Handler | Input | Output | Status |
|---------|-------|--------|--------|
| stream_handler | `"Hello streaming world from Beam!"` | 5 words streamed + `[DONE]` | ✅ |
| progress_handler | `steps: 5` | 5 progress updates (20%→100%) | ✅ |

**Sample Streaming Output:**
```
data: Hello
data: streaming
data: world
data: from
data: Beam!
data: [DONE]
```

**Sample Progress Output:**
```json
{"step": 1, "total": 5, "percent": 20.0, "status": "processing"}
{"step": 2, "total": 5, "percent": 40.0, "status": "processing"}
{"step": 3, "total": 5, "percent": 60.0, "status": "processing"}
{"step": 4, "total": 5, "percent": 80.0, "status": "processing"}
{"step": 5, "total": 5, "percent": 100.0, "status": "complete"}
```

---

## Quick Start

```bash
# Deploy to production
beam deploy basic_endpoint.py:handler

# Local development with live reload
beam serve basic_endpoint.py:handler

# Check available GPUs
beam machine list
```

## Calling Endpoints

```bash
curl -X POST 'https://[endpoint-url].app.beam.cloud' \
    -H 'Authorization: Bearer [YOUR_TOKEN]' \
    -H 'Content-Type: application/json' \
    -d '{"operation": "multiply", "a": 5, "b": 3}'
```

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `name` | Endpoint name | `"my-api"` |
| `cpu` | CPU cores | `1`, `2`, `4` |
| `memory` | RAM allocation | `"512Mi"`, `"8Gi"` |
| `gpu` | GPU type | `"A10G"`, `"H100"` |
| `keep_warm_seconds` | Container idle timeout | `300` |
| `image` | Container image config | `Image()` |

## GPU Availability (as of testing)

| GPU Type | Available |
|----------|-----------|
| A10G | ✅ |
| RTX4090 | ✅ |
| T4 | ✅ |
| H100 | ❌ |
| A100-40 | ❌ |
| A100-80 | ❌ |
