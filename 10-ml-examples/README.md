# ML Examples

Production-ready machine learning inference using HuggingFace Transformers.

## Example

| File | Description |
|------|-------------|
| `huggingface_inference.py` | Sentiment analysis, NER, text generation |

## Endpoints

### 1. Sentiment Analysis
Classify text as positive or negative.

```bash
beam deploy huggingface_inference.py:sentiment
```

```bash
curl -X POST '[URL]' \
  -H 'Authorization: Bearer [TOKEN]' \
  -d '{"text": "I love this product!"}'
```

**Response:**
```json
{"results": [{"text": "I love this product!", "label": "POSITIVE", "score": 0.9999}]}
```

### 2. Named Entity Recognition (NER)
Extract entities (people, organizations, locations) from text.

```bash
beam deploy huggingface_inference.py:ner
```

```bash
curl -X POST '[URL]' \
  -d '{"text": "Apple Inc. was founded by Steve Jobs in California."}'
```

### 3. Text Generation
Generate text continuations using GPT-2.

```bash
beam deploy huggingface_inference.py:generate
```

```bash
curl -X POST '[URL]' \
  -d '{"prompt": "Once upon a time", "max_length": 50}'
```

## Key Features Demonstrated

- **`on_start`** - Pre-load models at container startup
- **`keep_warm_seconds`** - Keep containers warm to reduce cold starts
- **`Volume`** - Cache model weights across invocations
- **`gpu="A10G"`** - GPU acceleration for inference

## Best Practices

1. **Pre-load models** with `on_start` - avoids loading on each request
2. **Use volumes** to cache model weights - faster cold starts
3. **Set `keep_warm_seconds`** - reduces latency for subsequent requests
4. **Batch inputs** - pass multiple texts in one request for efficiency
