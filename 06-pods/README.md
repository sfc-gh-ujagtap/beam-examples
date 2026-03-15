# Pods

Pods are long-running containers for persistent services. Unlike endpoints/functions that scale to zero, Pods stay running continuously.

## Examples

| File | Description | Status |
|------|-------------|--------|
| `basic_pod.py` | Python Flask web server | ✅ Tested |
| `nextjs_pod.py` | Next.js and Express.js apps | ✅ Tested |

## Test Results

### basic_pod.py

**Run:** `python basic_pod.py`

Creates a Flask web server pod.

---

### nextjs_pod.py

**Run:** `python nextjs_pod.py`

| Pod | URL | Result |
|-----|-----|--------|
| Next.js | `https://faa78637-...-3000.app.beam.cloud` | ✅ SSR working |
| Express | `https://bc9fc298-...-3000.app.beam.cloud` | ✅ API working |

**Express Endpoints:**
```
GET  /        → {"service":"Express API","endpoints":["/items","/health"]}
GET  /health  → {"healthy":true}
GET  /items   → {"items":[],"count":0}
POST /items   → {"id":1,"name":"Test Item","price":19.99}
```

**Next.js Endpoints:**
```
GET /           → Full SSR React page
GET /api/hello  → {"message":"Hello from Next.js API!","timestamp":"..."}
GET /api/health → {"healthy":true}
```

**Build Time:** ~60s (npm install + next build)

## Quick Start

```python
from beam import Pod, Image

pod = Pod(
    name="my-service",
    image=Image(python_version="python3.11"),
    cpu=1,
    memory="512Mi",
    ports=[8000],
    entrypoint=["python3", "server.py"],
)

result = pod.create()
print(f"Service running at: {result.url}")
```

## Use Cases

| Use Case | Why Pods |
|----------|----------|
| Databases | Need persistent connections |
| Cache servers | Low-latency requirements |
| WebSocket servers | Long-lived connections |
| Full-stack apps | Next.js, Express, etc. |
| ML model servers | Keep models loaded |

## Configuration

```python
pod = Pod(
    name="my-pod",
    image=Image().from_registry("node:20-alpine"),
    cpu=2,
    memory="4Gi",
    gpu="A10G",  # Optional GPU
    ports=[3000, 8080],  # Multiple ports
    entrypoint=["npm", "start"],
    env={
        "NODE_ENV": "production",
        "API_KEY": "xxx",
    },
)
```

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `name` | Pod identifier | `"my-service"` |
| `image` | Container image | `Image()` |
| `cpu` | CPU cores | `1`, `2`, `4` |
| `memory` | RAM | `"512Mi"`, `"4Gi"` |
| `gpu` | GPU type | `"A10G"`, `"H100"` |
| `ports` | Exposed ports | `[3000, 8080]` |
| `entrypoint` | Startup command | `["npm", "start"]` |
| `env` | Environment vars | `{"KEY": "value"}` |

## Pods vs Endpoints

| Feature | Pods | Endpoints |
|---------|------|-----------|
| Lifecycle | Always running | Scale to zero |
| Cold starts | None | 1-3 seconds |
| Cost | Pay while running | Pay per request |
| State | Can maintain state | Stateless |
| Best for | Databases, caches | APIs, functions |
