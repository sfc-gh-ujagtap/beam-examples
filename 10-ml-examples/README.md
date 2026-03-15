# ML Examples

Production-ready machine learning examples using popular frameworks and models.

## Examples

| File | Description |
|------|-------------|
| `huggingface_inference.py` | HuggingFace models (sentiment, NER, generation) |
| `vllm_server.py` | High-throughput LLM serving with vLLM |
| `whisper_transcription.py` | Audio transcription with Whisper |

## HuggingFace Inference

```python
from transformers import pipeline

def load_model():
    return pipeline("sentiment-analysis", device=0)

@endpoint(on_start=load_model, gpu="A10G")
def predict(context, **inputs):
    model = context.on_start_value
    return model(inputs["text"])
```

**Deploy:**
```bash
beam deploy huggingface_inference.py:sentiment
```

## vLLM Server

High-throughput LLM inference with PagedAttention:

```python
from vllm import LLM, SamplingParams

def load_model():
    return LLM(model="meta-llama/Llama-2-7b-chat-hf")

@endpoint(on_start=load_model, gpu="A10G", memory="32Gi")
def generate(context, **inputs):
    model = context.on_start_value
    outputs = model.generate([inputs["prompt"]], SamplingParams())
    return {"text": outputs[0].outputs[0].text}
```

**Features:**
- OpenAI-compatible API format
- Efficient batching
- PagedAttention for memory efficiency

## Whisper Transcription

```python
import whisper

def load_model():
    return whisper.load_model("base")

@endpoint(on_start=load_model, gpu="A10G")
def transcribe(context, **inputs):
    model = context.on_start_value
    result = model.transcribe(audio_path)
    return {"text": result["text"]}
```

**Features:**
- Multiple model sizes (tiny, base, small, medium, large)
- Language detection
- Timestamp segments

## Best Practices

1. **Pre-load models** with `on_start` to avoid loading on each request
2. **Use volumes** to cache model weights across containers
3. **Set `keep_warm_seconds`** to reduce cold starts for ML endpoints
4. **Use task queues** for long-running inference (>180s)
5. **Match GPU to model size**:
   - A10G (24GB): Most models up to 13B parameters
   - H100 (80GB): Large models, training

## GPU Selection

| Model Size | Recommended GPU |
|------------|-----------------|
| <7B params | A10G (24GB) |
| 7B-13B params | A10G or RTX4090 |
| 13B-70B params | H100 (80GB) |
| Training | H100 |
