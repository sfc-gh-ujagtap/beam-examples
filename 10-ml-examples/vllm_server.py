"""
vLLM Server Example
===================
Run an OpenAI-compatible LLM server using vLLM.
High-throughput inference with PagedAttention.

Deploy: beam deploy vllm_server.py
"""

from beam import endpoint, Image, Volume


MODEL_CACHE = "./models"

image = Image(
    python_version="python3.11",
    base_image="nvcr.io/nvidia/cuda:12.1.0-devel-ubuntu22.04",
).add_python_packages([
    "vllm",
    "torch",
    "transformers",
])


def load_vllm_model():
    """Load vLLM model at startup."""
    from vllm import LLM
    import os
    
    os.makedirs(MODEL_CACHE, exist_ok=True)
    
    model = LLM(
        model="meta-llama/Llama-2-7b-chat-hf",
        download_dir=MODEL_CACHE,
        dtype="float16",
        gpu_memory_utilization=0.9,
    )
    
    return model


@endpoint(
    name="vllm-inference",
    cpu=4,
    memory="32Gi",
    gpu="A10G",
    image=image,
    on_start=load_vllm_model,
    keep_warm_seconds=600,
    volumes=[Volume(name="llm-models", mount_path=MODEL_CACHE)],
    secrets=["HF_TOKEN"],
)
def generate(context, **inputs):
    """
    vLLM text generation endpoint.
    
    Example:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{
                "prompt": "What is machine learning?",
                "max_tokens": 100,
                "temperature": 0.7
            }'
    """
    from vllm import SamplingParams
    
    model = context.on_start_value
    
    prompt = inputs.get("prompt", "Hello")
    max_tokens = inputs.get("max_tokens", 100)
    temperature = inputs.get("temperature", 0.7)
    top_p = inputs.get("top_p", 0.9)
    
    sampling_params = SamplingParams(
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    
    outputs = model.generate([prompt], sampling_params)
    
    generated_text = outputs[0].outputs[0].text
    
    return {
        "prompt": prompt,
        "generated": generated_text,
        "usage": {
            "prompt_tokens": len(outputs[0].prompt_token_ids),
            "completion_tokens": len(outputs[0].outputs[0].token_ids),
        },
    }


@endpoint(
    name="vllm-chat",
    cpu=4,
    memory="32Gi",
    gpu="A10G",
    image=image,
    on_start=load_vllm_model,
    keep_warm_seconds=600,
    volumes=[Volume(name="llm-models", mount_path=MODEL_CACHE)],
    secrets=["HF_TOKEN"],
)
def chat(context, **inputs):
    """
    Chat completion endpoint (OpenAI-compatible format).
    
    Example:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is Python?"}
                ],
                "max_tokens": 100
            }'
    """
    from vllm import SamplingParams
    
    model = context.on_start_value
    
    messages = inputs.get("messages", [])
    max_tokens = inputs.get("max_tokens", 100)
    temperature = inputs.get("temperature", 0.7)
    
    prompt = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt += f"[INST] <<SYS>>\n{content}\n<</SYS>>\n\n"
        elif role == "user":
            prompt += f"{content} [/INST]"
        elif role == "assistant":
            prompt += f" {content} </s><s>[INST] "
    
    sampling_params = SamplingParams(
        max_tokens=max_tokens,
        temperature=temperature,
    )
    
    outputs = model.generate([prompt], sampling_params)
    
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": outputs[0].outputs[0].text.strip(),
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": len(outputs[0].prompt_token_ids),
            "completion_tokens": len(outputs[0].outputs[0].token_ids),
        },
    }


@endpoint(
    name="vllm-batch",
    cpu=4,
    memory="32Gi",
    gpu="A10G",
    image=image,
    on_start=load_vllm_model,
    keep_warm_seconds=600,
    volumes=[Volume(name="llm-models", mount_path=MODEL_CACHE)],
    secrets=["HF_TOKEN"],
)
def batch_generate(context, **inputs):
    """
    Batch generation for multiple prompts.
    vLLM efficiently batches requests for higher throughput.
    """
    from vllm import SamplingParams
    
    model = context.on_start_value
    
    prompts = inputs.get("prompts", ["Hello"])
    max_tokens = inputs.get("max_tokens", 50)
    
    sampling_params = SamplingParams(max_tokens=max_tokens)
    
    outputs = model.generate(prompts, sampling_params)
    
    results = []
    for prompt, output in zip(prompts, outputs):
        results.append({
            "prompt": prompt,
            "generated": output.outputs[0].text,
        })
    
    return {"results": results}
