# Advanced Features

Advanced Beam features for optimizing performance, managing secrets, and coordinating between apps.

## Examples

| File | Description |
|------|-------------|
| `preload_models.py` | Load models at container start |
| `keep_warm.py` | Control container lifecycle |
| `secrets.py` | Secure credential management |
| `signals.py` | Inter-app communication |

## Pre-loading Models

Load expensive resources once at startup:

```python
def load_model():
    from transformers import pipeline
    return pipeline("sentiment-analysis")

@endpoint(
    on_start=load_model,  # Runs once at startup
)
def predict(context, **inputs):
    model = context.on_start_value  # Access pre-loaded model
    return model(inputs["text"])
```

## Keep Warm

Control how long containers stay running:

```python
@endpoint(
    keep_warm_seconds=300,  # Stay warm for 5 minutes
)
def handler():
    pass
```

| Traffic Level | Recommended |
|---------------|-------------|
| High | 600-3600s |
| Medium | 180-300s |
| Low | 30-60s |

## Secrets

Store sensitive credentials securely:

```bash
# Create secret
beam secret create API_KEY "sk-..."

# List secrets
beam secret list

# Delete secret
beam secret delete API_KEY
```

```python
@endpoint(
    secrets=["API_KEY", "DATABASE_URL"],
)
def handler():
    import os
    api_key = os.environ["API_KEY"]
```

## Signals

Send events between apps:

```python
from beam import Signal

# Send
signal = Signal(name="my-channel")
signal.send({"event": "user_signup", "user_id": 123})

# Receive
message = signal.recv(timeout=30)
```

## Environment Variables

Non-sensitive configuration:

```python
@endpoint(
    env_vars={
        "APP_ENV": "production",
        "LOG_LEVEL": "info",
    },
    secrets=["API_KEY"],  # Sensitive values
)
def handler():
    pass
```
