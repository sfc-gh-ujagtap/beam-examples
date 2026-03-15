"""
Basic Function Example
======================
Functions for direct programmatic invocation without HTTP.
Call with .remote() from Python code.

Run: python basic_function.py
"""

from beam import function, Image


@function(
    name="compute-function",
    cpu=2,
    memory="2Gi",
    image=Image(python_version="python3.11").add_python_packages([
        "numpy",
    ]),
)
def compute(data: list, operation: str = "sum"):
    """
    Direct invocation function for computation.
    
    Usage:
        result = compute.remote(data=[1, 2, 3, 4, 5], operation="sum")
    """
    import numpy as np
    
    arr = np.array(data)
    
    operations = {
        "sum": np.sum,
        "mean": np.mean,
        "std": np.std,
        "min": np.min,
        "max": np.max,
        "median": np.median,
    }
    
    if operation not in operations:
        return {"error": f"Unknown operation: {operation}"}
    
    result = operations[operation](arr)
    
    return {
        "operation": operation,
        "input_length": len(data),
        "result": float(result),
    }


@function(
    name="text-processor",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
)
def process_text(text: str, transform: str = "upper"):
    """
    Text processing function.
    """
    transforms = {
        "upper": str.upper,
        "lower": str.lower,
        "title": str.title,
        "reverse": lambda s: s[::-1],
        "word_count": lambda s: len(s.split()),
    }
    
    if transform not in transforms:
        return {"error": f"Unknown transform: {transform}"}
    
    result = transforms[transform](text)
    
    return {
        "original": text,
        "transform": transform,
        "result": result,
    }


if __name__ == "__main__":
    print("Running compute function remotely...")
    result = compute.remote(data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], operation="mean")
    print(f"Result: {result}")
    
    print("\nRunning text processor remotely...")
    result = process_text.remote(text="hello world from beam", transform="title")
    print(f"Result: {result}")
