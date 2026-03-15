"""
Streaming/Realtime Endpoint Example
===================================
Server-Sent Events (SSE) for streaming responses.
Useful for LLM token streaming, progress updates, etc.

Deploy: beam deploy streaming_endpoint.py:stream_handler
"""

from beam import endpoint, Image
import time


@endpoint(
    name="streaming-api",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
)
def stream_handler(**inputs):
    """
    Streaming response endpoint using generator.
    
    Example request:
        curl -N 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"message": "Hello, streaming world!"}'
    """
    message = inputs.get("message", "Hello from Beam!")
    delay = inputs.get("delay", 0.1)  # Delay between tokens
    
    def generate():
        words = message.split()
        for i, word in enumerate(words):
            yield f"data: {word}\n\n"
            time.sleep(delay)
        yield "data: [DONE]\n\n"
    
    return generate()


@endpoint(
    name="progress-stream",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
)
def progress_handler(**inputs):
    """
    Stream progress updates for long-running operations.
    
    Example request:
        curl -N 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"steps": 10}'
    """
    import json
    
    steps = inputs.get("steps", 5)
    
    def generate():
        for i in range(steps):
            progress = {
                "step": i + 1,
                "total": steps,
                "percent": round((i + 1) / steps * 100, 1),
                "status": "processing" if i < steps - 1 else "complete",
            }
            yield f"data: {json.dumps(progress)}\n\n"
            time.sleep(0.5)
    
    return generate()
