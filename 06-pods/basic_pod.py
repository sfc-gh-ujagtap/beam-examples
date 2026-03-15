"""
Basic Pod Example
=================
Pods are long-running containers for persistent services.
Unlike endpoints/functions, Pods stay running continuously.

Run: python basic_pod.py
"""

from beam import Pod, Image


def create_python_pod():
    """Create a basic Python pod with a web server."""
    print("Creating Python web server pod...")
    
    pod = Pod(
        name="python-web-server",
        image=Image(python_version="python3.11").add_python_packages([
            "flask",
        ]),
        cpu=1,
        memory="512Mi",
        ports=[5000],
        entrypoint=["python3", "-c", """
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'service': 'Python Web Server',
        'status': 'running',
        'pod': True
    })

@app.route('/health')
def health():
    return jsonify({'healthy': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
"""],
        env={
            "FLASK_ENV": "production",
        },
    )
    
    result = pod.create()
    print(f"Pod created!")
    print(f"URL: {result.url}")
    return result


def create_redis_pod():
    """Create a Redis pod for caching."""
    print("\nCreating Redis pod...")
    
    pod = Pod(
        name="redis-cache",
        image=Image().from_registry("redis:7-alpine"),
        cpu=1,
        memory="256Mi",
        ports=[6379],
        entrypoint=["redis-server", "--protected-mode", "no"],
    )
    
    result = pod.create()
    print(f"Redis pod created!")
    print(f"URL: {result.url}")
    return result


def create_postgres_pod():
    """Create a PostgreSQL pod for database."""
    print("\nCreating PostgreSQL pod...")
    
    pod = Pod(
        name="postgres-db",
        image=Image().from_registry("postgres:16-alpine"),
        cpu=2,
        memory="1Gi",
        ports=[5432],
        env={
            "POSTGRES_USER": "beam",
            "POSTGRES_PASSWORD": "beam_password",
            "POSTGRES_DB": "app_db",
        },
    )
    
    result = pod.create()
    print(f"PostgreSQL pod created!")
    print(f"URL: {result.url}")
    return result


def create_gpu_pod():
    """Create a GPU-enabled pod for ML serving."""
    print("\nCreating GPU pod for ML...")
    
    pod = Pod(
        name="ml-inference-server",
        image=Image(python_version="python3.11").add_python_packages([
            "torch",
            "transformers",
            "flask",
        ]),
        cpu=2,
        memory="8Gi",
        gpu="A10G",
        ports=[8000],
        entrypoint=["python3", "-c", """
from flask import Flask, request, jsonify
from transformers import pipeline
import torch

app = Flask(__name__)

device = 0 if torch.cuda.is_available() else -1
classifier = pipeline('sentiment-analysis', device=device)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get('text', '')
    result = classifier(text)
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({
        'healthy': True,
        'gpu': torch.cuda.is_available(),
        'device': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
"""],
    )
    
    result = pod.create()
    print(f"GPU pod created!")
    print(f"URL: {result.url}")
    return result


if __name__ == "__main__":
    print("=" * 50)
    print("Pod Examples")
    print("=" * 50)
    
    python_pod = create_python_pod()
    
    print("\n" + "=" * 50)
    print("Pods are now running!")
    print("=" * 50)
