"""
Signals Example
===============
Send events between Beam apps for coordination.
Great for triggering workflows and notifications.

NOTE: Signal feature may not be available in all Beam SDK versions.
Check beam.cloud documentation for current availability.

Deploy: beam deploy signals.py:sender
"""

try:
    from beam import endpoint, function, Image, Signal
except ImportError:
    from beam import endpoint, function, Image
    Signal = None  # Signal not available in this SDK version


@endpoint(
    name="signal-sender",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
)
def sender(**inputs):
    """
    Send a signal to trigger another app.
    
    Example:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"event": "user_signup", "user_id": 123}'
    """
    event = inputs.get("event", "default_event")
    data = inputs.get("data", {})
    
    signal = Signal(name="my-signal-channel")
    
    signal.send({
        "event": event,
        "data": data,
        "source": "signal-sender",
    })
    
    return {
        "signal_sent": True,
        "event": event,
    }


@function(
    name="signal-receiver",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
)
def receiver():
    """
    Receive signals from other apps.
    
    This function listens for signals and processes them.
    """
    signal = Signal(name="my-signal-channel")
    
    message = signal.recv(timeout=30)
    
    if message is None:
        return {"received": False, "reason": "timeout"}
    
    return {
        "received": True,
        "event": message.get("event"),
        "data": message.get("data"),
        "source": message.get("source"),
    }


@endpoint(
    name="workflow-trigger",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
)
def workflow_trigger(**inputs):
    """
    Trigger a multi-step workflow using signals.
    """
    workflow_id = inputs.get("workflow_id", "default")
    steps = inputs.get("steps", ["step1", "step2", "step3"])
    
    signal = Signal(name=f"workflow-{workflow_id}")
    
    for step in steps:
        signal.send({
            "workflow_id": workflow_id,
            "step": step,
            "action": "execute",
        })
    
    signal.send({
        "workflow_id": workflow_id,
        "step": "complete",
        "action": "finish",
    })
    
    return {
        "workflow_id": workflow_id,
        "steps_triggered": len(steps),
    }


@function(
    name="workflow-worker",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
)
def workflow_worker(workflow_id: str):
    """
    Worker that processes workflow steps.
    """
    import time
    
    signal = Signal(name=f"workflow-{workflow_id}")
    
    processed_steps = []
    
    while True:
        message = signal.recv(timeout=10)
        
        if message is None:
            break
        
        step = message.get("step")
        action = message.get("action")
        
        if action == "finish":
            break
        
        time.sleep(0.5)
        processed_steps.append(step)
    
    return {
        "workflow_id": workflow_id,
        "processed_steps": processed_steps,
    }


@endpoint(
    name="pub-sub-publisher",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
)
def publisher(**inputs):
    """
    Publish messages to multiple subscribers.
    """
    topic = inputs.get("topic", "default")
    message = inputs.get("message", {})
    
    signal = Signal(name=f"topic-{topic}")
    
    signal.send({
        "topic": topic,
        "message": message,
        "timestamp": __import__("time").time(),
    })
    
    return {
        "published": True,
        "topic": topic,
    }


@function(
    name="pub-sub-subscriber",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
)
def subscriber(topic: str, subscriber_id: str):
    """
    Subscribe to messages on a topic.
    """
    signal = Signal(name=f"topic-{topic}")
    
    messages = []
    
    for _ in range(10):
        message = signal.recv(timeout=5)
        if message is None:
            break
        messages.append(message)
    
    return {
        "subscriber_id": subscriber_id,
        "topic": topic,
        "messages_received": len(messages),
        "messages": messages,
    }


"""
Signal Use Cases:

1. Event-Driven Architecture
   - Trigger actions when events occur
   - Decouple services

2. Workflow Orchestration
   - Coordinate multi-step processes
   - Handle async workflows

3. Pub/Sub Messaging
   - Broadcast messages to subscribers
   - Fan-out patterns

4. Real-time Notifications
   - Push updates to listeners
   - Live dashboards
"""
