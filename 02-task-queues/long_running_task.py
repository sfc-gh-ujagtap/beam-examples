"""
Long-Running Task Example
=========================
Tasks that run for extended periods (minutes to hours).
Use task_queue for anything >180 seconds.

Deploy: beam deploy long_running_task.py:train_model
"""

from beam import task_queue, Image, Output


@task_queue(
    name="model-trainer",
    cpu=4,
    memory="8Gi",
    gpu="A10G",
    timeout=3600,  # 1 hour timeout
    image=Image(python_version="python3.11").add_python_packages([
        "torch",
        "numpy",
    ]),
)
def train_model(**inputs):
    """
    Long-running model training task.
    
    Submit:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"epochs": 10, "batch_size": 32}'
    
    Check status:
        curl -X GET 'https://api.beam.cloud/v2/task/{TASK_ID}/' \
            -H 'Authorization: Bearer [YOUR_TOKEN]'
    """
    import torch
    import torch.nn as nn
    import time
    
    epochs = inputs.get("epochs", 5)
    batch_size = inputs.get("batch_size", 32)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    model = nn.Sequential(
        nn.Linear(100, 256),
        nn.ReLU(),
        nn.Linear(256, 128),
        nn.ReLU(),
        nn.Linear(128, 10),
    ).to(device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    
    training_log = []
    
    for epoch in range(epochs):
        epoch_start = time.time()
        
        x = torch.randn(batch_size * 100, 100, device=device)
        y = torch.randint(0, 10, (batch_size * 100,), device=device)
        
        total_loss = 0
        for i in range(0, len(x), batch_size):
            batch_x = x[i:i+batch_size]
            batch_y = y[i:i+batch_size]
            
            optimizer.zero_grad()
            output = model(batch_x)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        epoch_time = time.time() - epoch_start
        avg_loss = total_loss / (len(x) // batch_size)
        
        training_log.append({
            "epoch": epoch + 1,
            "loss": round(avg_loss, 4),
            "time_seconds": round(epoch_time, 2),
        })
    
    torch.save(model.state_dict(), "/tmp/model.pt")
    Output(path="/tmp/model.pt").save()
    
    return {
        "status": "complete",
        "device": device,
        "epochs_trained": epochs,
        "training_log": training_log,
        "model_saved": "model.pt",
    }


@task_queue(
    name="video-processor",
    cpu=2,
    memory="4Gi",
    timeout=7200,  # 2 hour timeout
    image=Image(python_version="python3.11").add_commands([
        "apt-get update",
        "apt-get install -y ffmpeg",
    ]).add_python_packages(["numpy"]),
)
def process_video(**inputs):
    """
    Long-running video processing task.
    """
    import subprocess
    import time
    
    duration = inputs.get("duration_seconds", 60)
    
    time.sleep(duration)  # Simulate video processing
    
    return {
        "status": "complete",
        "processed_duration": duration,
    }
