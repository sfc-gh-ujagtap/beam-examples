"""
Basic Web Endpoint Example
==========================
A synchronous HTTP API that responds within 180 seconds.
Use @endpoint for request-response patterns like REST APIs.

Deploy: beam deploy basic_endpoint.py:handler
Serve (dev): beam serve basic_endpoint.py:handler
"""

from beam import endpoint, Image


@endpoint(
    name="basic-math-api",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11"),
)
def handler(**inputs):
    """
    Simple math operations endpoint.
    
    Example request:
        curl -X POST 'https://[endpoint-url].app.beam.cloud' \
            -H 'Authorization: Bearer [YOUR_TOKEN]' \
            -H 'Content-Type: application/json' \
            -d '{"operation": "multiply", "a": 5, "b": 3}'
    """
    operation = inputs.get("operation", "add")
    a = inputs.get("a", 0)
    b = inputs.get("b", 0)
    
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero",
    }
    
    if operation not in operations:
        return {"error": f"Unknown operation: {operation}. Use: add, subtract, multiply, divide"}
    
    result = operations[operation](a, b)
    return {
        "operation": operation,
        "a": a,
        "b": b,
        "result": result,
    }
