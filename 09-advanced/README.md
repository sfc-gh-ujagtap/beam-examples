# Advanced Features

Advanced Beam features for optimizing performance and managing secrets.

## Examples

| File | Description |
|------|-------------|
| `preload_models.py` | Load models at container start |
| `keep_warm.py` | Control container lifecycle |
| `secrets.py` | Secure credential management |

## Pre-loading Models (on_start)

Load expensive resources once at startup instead of on every request:

```python
def load_model():
    from transformers import pipeline
    return pipeline("sentiment-analysis")

@endpoint(
    on_start=load_model,  # Runs ONCE when container starts
    keep_warm_seconds=300,  # Keep model in memory
)
def predict(context, **inputs):
    model = context.on_start_value  # Access pre-loaded model
    return model(inputs["text"])
```

**Benefits:**
- First request after cold start includes model loading time
- All subsequent requests are fast (model already in memory)
- Combined with `keep_warm_seconds`, amortizes loading cost

## Keep Warm

Control how long containers stay running after the last request:

```python
@endpoint(
    keep_warm_seconds=300,  # Stay warm for 5 minutes after last request
)
def handler(**inputs):
    pass
```

**Recommended Settings:**

| Traffic Level | keep_warm_seconds | Why |
|---------------|-------------------|-----|
| High traffic | 600-3600 (10min-1hr) | Minimize cold starts |
| Medium traffic | 180-300 (3-5min) | Balance cost/latency |
| Low traffic | 30-60 (30s-1min) | Save costs |
| Expensive init | 300-600 (5-10min) | Amortize init cost |
| GPU endpoints | 180-300 (3-5min) | GPUs are expensive |

**Cost vs Latency Trade-off:**
- Longer keep_warm = More cost (container running idle)
- Shorter keep_warm = More cold starts (slower responses)

## Secrets

Store sensitive credentials securely (encrypted at rest):

```bash
# Create a secret
beam secret create API_KEY "sk-..."

# List secrets
beam secret list

# Delete a secret
beam secret delete API_KEY
```

Use secrets in your code:

```python
@endpoint(
    secrets=["API_KEY", "DATABASE_URL"],  # Inject as env vars
)
def handler(**inputs):
    import os
    api_key = os.environ["API_KEY"]
    db_url = os.environ["DATABASE_URL"]
```

**Best Practices:**
1. Never hardcode secrets in code
2. Use descriptive names (e.g., `STRIPE_API_KEY`, not `KEY1`)
3. Rotate secrets regularly
4. Use different secrets for dev/staging/prod

## Combining Features

For ML inference, combine all features for optimal performance:

```python
def load_model():
    from transformers import pipeline
    import torch
    device = 0 if torch.cuda.is_available() else -1
    return pipeline("sentiment-analysis", device=device)

@endpoint(
    name="optimized-inference",
    gpu="A10G",
    on_start=load_model,        # Load model once
    keep_warm_seconds=300,      # Keep warm for 5 min
    secrets=["HF_TOKEN"],       # HuggingFace token
)
def predict(context, **inputs):
    model = context.on_start_value
    return model(inputs["text"])
```

This gives you:
- Fast inference (model pre-loaded)
- Low latency (container stays warm)
- Secure credentials (token not in code)
