"""
GPU Sandbox Example
===================
Sandboxes with GPU acceleration for ML workloads.
Run inference, fine-tuning, or any GPU computation.

Run: python sandbox_with_gpu.py
"""

from beam import Sandbox, Image, PythonVersion
from textwrap import dedent


def gpu_sandbox():
    """Create a GPU-enabled sandbox for ML inference."""
    print("Creating GPU sandbox...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311).add_python_packages([
            "torch",
            "numpy",
        ]),
        cpu=2,
        memory="8Gi",
        gpu="A10G",
    )
    
    sb = sandbox.create()
    print(f"GPU Sandbox created: {sb.container_id}")
    
    gpu_info_code = dedent("""
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Device: {device}")

        if device == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    """).strip()
    
    result = sb.process.run_code(gpu_info_code)
    print(f"GPU Info:\n{result.result}")
    
    benchmark_code = dedent("""
        import torch
        import time

        device = "cuda" if torch.cuda.is_available() else "cpu"
        size = 5000

        start = time.time()
        a = torch.randn(size, size, device=device)
        b = torch.randn(size, size, device=device)
        c = torch.matmul(a, b)
        if device == "cuda":
            torch.cuda.synchronize()
        elapsed = time.time() - start

        print(f"Matrix multiplication ({size}x{size}): {elapsed:.3f}s on {device}")
    """).strip()
    
    result = sb.process.run_code(benchmark_code)
    print(f"Benchmark:\n{result.result}")
    
    sb.terminate()
    print("GPU sandbox terminated.")


def ml_inference_sandbox():
    """Run ML inference in a GPU sandbox."""
    print("\nCreating ML inference sandbox...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311).add_python_packages([
            "torch",
            "transformers",
        ]),
        cpu=2,
        memory="16Gi",
        gpu="A10G",
    )
    
    sb = sandbox.create()
    
    inference_code = dedent("""
        from transformers import pipeline
        import torch

        device = 0 if torch.cuda.is_available() else -1
        classifier = pipeline("sentiment-analysis", device=device)

        texts = [
            "I love using Beam for ML inference!",
            "This is terrible and I hate it.",
            "The weather is okay today.",
        ]

        results = classifier(texts)
        for text, result in zip(texts, results):
            print(f"{result['label']} ({result['score']:.2f}): {text[:50]}")
    """).strip()
    
    result = sb.process.run_code(inference_code)
    print(f"Inference results:\n{result.result}")
    
    sb.terminate()


if __name__ == "__main__":
    gpu_sandbox()
    ml_inference_sandbox()
