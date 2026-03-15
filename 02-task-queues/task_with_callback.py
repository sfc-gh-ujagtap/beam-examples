"""
Task Queue with Callback/Webhook Example
=========================================
Receive notifications when async tasks complete.
Useful for integrating with external systems.

Deploy: beam deploy task_with_callback.py:process_with_webhook
"""

from beam import task_queue, Image


@task_queue(
    name="webhook-task",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
    callback_url="https://your-server.com/webhook",  # Replace with your webhook URL
)
def process_with_webhook(**inputs):
    """
    Task that sends results to a webhook when complete.
    
    The callback_url receives a POST with:
    {
        "task_id": "...",
        "status": "COMPLETE",
        "result": { ... your return value ... }
    }
    
    Submit task:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"data": "process this"}'
    """
    import time
    
    data = inputs.get("data", "default")
    
    time.sleep(5)  # Simulate work
    
    return {
        "input": data,
        "output": f"Processed: {data.upper()}",
        "timestamp": time.time(),
    }


@task_queue(
    name="dynamic-callback-task",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
)
def process_with_dynamic_callback(**inputs):
    """
    Task where callback URL is provided per-request.
    
    Submit with callback_url in request:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{
                "data": "process this",
                "callback_url": "https://your-server.com/webhook"
            }'
    """
    import time
    
    data = inputs.get("data", "default")
    
    time.sleep(3)
    
    return {
        "processed": True,
        "result": data.upper(),
    }
