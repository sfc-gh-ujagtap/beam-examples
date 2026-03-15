# Task Queues

Task queues handle async/background processing for tasks >180 seconds or when you don't need immediate responses.

## Examples

| File | Description | Status |
|------|-------------|--------|
| `basic_task.py` | Simple async data processing | ✅ Tested |
| `task_with_callback.py` | Webhook notifications on completion | ⏳ Pending |
| `long_running_task.py` | Extended tasks (training, video processing) | ⏳ Pending |

## Test Results

### basic_task.py - `process_data`

**Deployed URL:** `https://data-processor-6decdd8-v1.app.beam.cloud`

| Metric | Value |
|--------|-------|
| CPU | 2 cores |
| Memory | 2Gi |
| Cold Start | ~12s |
| Task Execution | ~2.6s |

**Test Case:**

| Input | Output | Duration |
|-------|--------|----------|
| `rows: 5000, columns: 20` | DataFrame stats computed | 2.63s |

**How Task Queues Work:**

1. **Submit task** → Returns immediately with `task_id`
2. **Task runs in background** → Status: PENDING → RUNNING → COMPLETE
3. **Poll for results** → GET `/v2/task/{task_id}/`

```
Submit: POST → {"task_id": "46ebf823-13ae-4105-85d3-62be588fa132"}
Status: PENDING → RUNNING → COMPLETE (2.63s)
```

---

### basic_task.py - `batch_process`

**Deployed URL:** `https://batch-processor-17382d1-v1.app.beam.cloud`

| Metric | Value |
|--------|-------|
| CPU | 1 core |
| Memory | 1Gi |
| Task Execution | ~2.5s |

**Test Case:**

| Input | Output | Duration |
|-------|--------|----------|
| `items: [10, 20, 30, 40, 50]` | Each item doubled | 2.5s |

---

## Quick Start

```bash
# Deploy
beam deploy basic_task.py:process_data

# Submit a task
curl -X POST 'https://[endpoint-url].app.beam.cloud' \
    -H 'Authorization: Bearer [YOUR_TOKEN]' \
    -H 'Content-Type: application/json' \
    -d '{"rows": 10000}'
```

## Checking Task Status

Tasks return a `task_id`. Poll for results:

```bash
curl -X GET 'https://api.beam.cloud/v2/task/{TASK_ID}/' \
    -H 'Authorization: Bearer [YOUR_TOKEN]'
```

Response:
```json
{
    "task_id": "abc123",
    "status": "COMPLETE",
    "result": { ... }
}
```

## Task States

| Status | Description |
|--------|-------------|
| `PENDING` | Task queued, waiting to run |
| `RUNNING` | Task currently executing |
| `COMPLETE` | Task finished successfully |
| `FAILED` | Task encountered an error |
| `CANCELLED` | Task was cancelled |

## Webhooks

Add `callback_url` to receive results automatically:

```python
@task_queue(
    callback_url="https://your-server.com/webhook",
)
def handler():
    pass
```
