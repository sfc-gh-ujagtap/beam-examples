"""
Pre-loading Models Example
==========================
Load models when the container starts, not on each request.
Dramatically reduces latency for ML inference.

Deploy: beam deploy preload_models.py:predict
"""

from beam import endpoint, Image


image = Image(python_version="python3.11").add_python_packages([
    "torch",
    "transformers",
])


def load_model():
    """
    This function runs ONCE when the container starts.
    The model stays in memory for all subsequent requests.
    """
    from transformers import pipeline
    import torch
    
    device = 0 if torch.cuda.is_available() else -1
    
    model = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=device,
    )
    
    return model


@endpoint(
    name="preloaded-inference",
    cpu=2,
    memory="4Gi",
    gpu="A10G",
    image=image,
    on_start=load_model,  # Called once when container starts
    keep_warm_seconds=300,  # Keep model in memory for 5 minutes
)
def predict(context, **inputs):
    """
    Fast inference with pre-loaded model.
    
    The model is available via context.on_start_value
    No loading time on each request!
    
    Example:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"text": "I love this product!"}'
    """
    model = context.on_start_value
    
    text = inputs.get("text", "Hello world")
    
    result = model(text)
    
    return {
        "text": text,
        "sentiment": result[0]["label"],
        "confidence": round(result[0]["score"], 4),
    }


def load_multiple_models():
    """Load multiple models at startup."""
    from transformers import pipeline
    import torch
    
    device = 0 if torch.cuda.is_available() else -1
    
    models = {
        "sentiment": pipeline("sentiment-analysis", device=device),
        "ner": pipeline("ner", device=device),
        "summarization": pipeline("summarization", device=device),
    }
    
    return models


@endpoint(
    name="multi-model-inference",
    cpu=4,
    memory="16Gi",
    gpu="A10G",
    image=image,
    on_start=load_multiple_models,
    keep_warm_seconds=600,
)
def multi_model_predict(context, **inputs):
    """
    Inference with multiple pre-loaded models.
    """
    models = context.on_start_value
    
    task = inputs.get("task", "sentiment")
    text = inputs.get("text", "Hello world")
    
    if task not in models:
        return {"error": f"Unknown task: {task}. Available: {list(models.keys())}"}
    
    result = models[task](text)
    
    return {
        "task": task,
        "text": text[:100],
        "result": result,
    }


def load_with_cache():
    """Load model with caching to volume."""
    from transformers import AutoModel, AutoTokenizer
    import os
    
    cache_dir = "./model_cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    model_name = "bert-base-uncased"
    
    model = AutoModel.from_pretrained(model_name, cache_dir=cache_dir)
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    
    return {"model": model, "tokenizer": tokenizer}


@endpoint(
    name="cached-model-inference",
    cpu=2,
    memory="4Gi",
    image=image,
    on_start=load_with_cache,
)
def cached_inference(context, **inputs):
    """Inference with cached model weights."""
    model = context.on_start_value["model"]
    tokenizer = context.on_start_value["tokenizer"]
    
    text = inputs.get("text", "Hello world")
    
    tokens = tokenizer(text, return_tensors="pt")
    
    return {
        "text": text,
        "token_count": len(tokens["input_ids"][0]),
    }
