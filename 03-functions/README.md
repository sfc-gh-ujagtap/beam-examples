# Functions

Functions are for direct programmatic invocation without HTTP. Call with `.remote()` or distribute work with `.map()`.

## Examples

| File | Description | Status |
|------|-------------|--------|
| `basic_function.py` | Direct invocation with `.remote()` | ✅ Tested |
| `scheduled_job.py` | Cron-style scheduled tasks | ✅ Tested |
| `parallel_map.py` | Parallel processing with `.map()` | ✅ Tested |

## Test Results

### basic_function.py

**Run:** `python basic_function.py`

| Function | Input | Output | Status |
|----------|-------|--------|--------|
| `compute` | `data=[1..10], operation="mean"` | `{"result": 5.5}` | ✅ |
| `process_text` | `text="hello world from beam", transform="title"` | `"Hello World From Beam"` | ✅ |

| Metric | Value |
|--------|-------|
| First run (build image) | ~46s |
| Subsequent runs | ~5s |

---

### parallel_map.py

**Run:** `python parallel_map.py`

| Function | Items | Parallel Execution | Status |
|----------|-------|-------------------|--------|
| `process_item` | 5 items | All 5 ran simultaneously | ✅ |
| `process_image` | 3 images | All 3 ran simultaneously | ✅ |

**Key observation:** `.map()` distributes work across multiple containers:
```
=> Running function: <parallel_map:process_item>  (x5 at once!)
```

**Results:**
```
ID 1: hello -> 2cf24dba5fb0a30e
ID 2: world -> 486ea46224d1bb4f
ID 3: beam  -> ae4b867cf2eeb128
ID 4: cloud -> 56681010b753e1ab
ID 5: parallel -> 83a00300ad6a2502
```

---

### scheduled_job.py

**Deploy:** `beam deploy scheduled_job.py:hourly_report`

| Schedule | Cron Expression | Next Runs |
|----------|-----------------|-----------|
| `hourly_report` | `0 * * * *` | Every hour at :00 |
| `daily_cleanup` | `0 2 * * *` | Daily at 2 AM UTC |
| `weekly_digest` | `0 9 * * 1` | Mondays at 9 AM UTC |

**Upcoming executions (hourly_report):**
```
1. 2026-03-15 17:00:00 UTC
2. 2026-03-15 18:00:00 UTC
3. 2026-03-15 19:00:00 UTC
```

---

## Quick Start

```python
from beam import function, Image

@function(cpu=1, memory="512Mi")
def my_function(x: int):
    return x * 2

# Call remotely
result = my_function.remote(x=5)
print(result)  # 10
```

## Parallel Processing with .map()

```python
items = [1, 2, 3, 4, 5]
results = list(my_function.map(items))
```

## Scheduled Jobs

```python
from beam import schedule

@schedule(
    when="0 * * * *",  # Every hour
)
def hourly_task():
    pass
```

### Cron Format

| Expression | Description |
|------------|-------------|
| `0 * * * *` | Every hour |
| `*/15 * * * *` | Every 15 minutes |
| `0 0 * * *` | Daily at midnight |
| `0 9 * * 1-5` | Weekdays at 9 AM |
| `0 0 1 * *` | First of every month |

Format: `minute hour day month weekday`
