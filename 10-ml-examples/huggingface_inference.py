"""
HuggingFace Inference Example
=============================
Serve HuggingFace models for various NLP tasks.
Optimized for production with model caching.

Deploy: beam deploy huggingface_inference.py:sentiment
"""

from beam import endpoint, Image, Volume


MODEL_CACHE = "./hf_cache"

image = Image(python_version="python3.11").add_python_packages([
    "torch",
    "transformers",
    "accelerate",
])


def load_sentiment_model():
    """Load sentiment analysis model at startup."""
    from transformers import pipeline
    import torch
    import os
    
    os.makedirs(MODEL_CACHE, exist_ok=True)
    
    device = 0 if torch.cuda.is_available() else -1
    
    model = pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=device,
        model_kwargs={"cache_dir": MODEL_CACHE},
    )
    
    return model


@endpoint(
    name="sentiment-analysis",
    cpu=2,
    memory="4Gi",
    gpu="A10G",
    image=image,
    on_start=load_sentiment_model,
    keep_warm_seconds=300,
    volumes=[Volume(name="hf-models", mount_path=MODEL_CACHE)],
)
def sentiment(context, **inputs):
    """
    Sentiment analysis endpoint.
    
    Example:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"text": "I love this product!"}'
    """
    model = context.on_start_value
    
    text = inputs.get("text", "")
    
    if not text:
        return {"error": "No text provided"}
    
    if isinstance(text, list):
        results = model(text)
    else:
        results = model([text])
    
    return {
        "results": [
            {
                "text": t if isinstance(text, str) else text[i],
                "label": r["label"],
                "score": round(r["score"], 4),
            }
            for i, (t, r) in enumerate(zip([text] if isinstance(text, str) else text, results))
        ]
    }


def load_ner_model():
    """Load Named Entity Recognition model."""
    from transformers import pipeline
    import torch
    import os
    
    os.makedirs(MODEL_CACHE, exist_ok=True)
    
    device = 0 if torch.cuda.is_available() else -1
    
    model = pipeline(
        "ner",
        model="dbmdz/bert-large-cased-finetuned-conll03-english",
        device=device,
        aggregation_strategy="simple",
        model_kwargs={"cache_dir": MODEL_CACHE},
    )
    
    return model


@endpoint(
    name="named-entity-recognition",
    cpu=2,
    memory="8Gi",
    gpu="A10G",
    image=image,
    on_start=load_ner_model,
    keep_warm_seconds=300,
    volumes=[Volume(name="hf-models", mount_path=MODEL_CACHE)],
)
def ner(context, **inputs):
    """
    Named Entity Recognition endpoint.
    
    Example:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"text": "Apple Inc. was founded by Steve Jobs in California."}'
    """
    model = context.on_start_value
    
    text = inputs.get("text", "")
    
    if not text:
        return {"error": "No text provided"}
    
    results = model(text)
    
    entities = [
        {
            "entity": r["entity_group"],
            "word": r["word"],
            "score": round(r["score"], 4),
            "start": r["start"],
            "end": r["end"],
        }
        for r in results
    ]
    
    return {
        "text": text,
        "entities": entities,
    }


def load_text_generation_model():
    """Load text generation model."""
    from transformers import pipeline
    import torch
    import os
    
    os.makedirs(MODEL_CACHE, exist_ok=True)
    
    device = 0 if torch.cuda.is_available() else -1
    
    model = pipeline(
        "text-generation",
        model="gpt2",
        device=device,
        model_kwargs={"cache_dir": MODEL_CACHE},
    )
    
    return model


@endpoint(
    name="text-generation",
    cpu=2,
    memory="4Gi",
    gpu="A10G",
    image=image,
    on_start=load_text_generation_model,
    keep_warm_seconds=300,
    volumes=[Volume(name="hf-models", mount_path=MODEL_CACHE)],
)
def generate(context, **inputs):
    """
    Text generation endpoint.
    
    Example:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"prompt": "Once upon a time", "max_length": 50}'
    """
    model = context.on_start_value
    
    prompt = inputs.get("prompt", "Hello")
    max_length = inputs.get("max_length", 50)
    temperature = inputs.get("temperature", 0.7)
    
    results = model(
        prompt,
        max_length=max_length,
        temperature=temperature,
        num_return_sequences=1,
        do_sample=True,
    )
    
    return {
        "prompt": prompt,
        "generated": results[0]["generated_text"],
        "max_length": max_length,
        "temperature": temperature,
    }
