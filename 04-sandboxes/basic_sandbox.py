"""
Basic Sandbox Example
=====================
Ephemeral, ultra-fast code execution environments.
Cold boot in 1-3 seconds. Great for AI agents, code interpreters, etc.

Run: python basic_sandbox.py
"""

from beam import Sandbox, Image, PythonVersion
from textwrap import dedent


def basic_example():
    """Create a sandbox, run code, and terminate."""
    print("Creating sandbox...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311)
    )
    
    sb = sandbox.create()
    print(f"Sandbox created: {sb.sandbox_id}")
    
    result = sb.process.run_code("print('Hello from the sandbox!')")
    print(f"Output: {result.result}")
    
    system_info_code = dedent("""
        import sys
        import platform

        info = {
            'python_version': sys.version,
            'platform': platform.platform(),
            'processor': platform.processor(),
        }
        print(info)
    """).strip()
    
    result = sb.process.run_code(system_info_code)
    print(f"System info: {result.result}")
    
    sb.terminate()
    print("Sandbox terminated.")


def sandbox_with_packages():
    """Sandbox with custom Python packages."""
    print("\nCreating sandbox with packages...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311).add_python_packages([
            "numpy",
            "pandas",
        ])
    )
    
    sb = sandbox.create()
    
    data_code = dedent("""
        import numpy as np
        import pandas as pd

        arr = np.array([1, 2, 3, 4, 5])
        df = pd.DataFrame({'values': arr, 'squared': arr ** 2})
        print(df.to_string())
    """).strip()
    
    result = sb.process.run_code(data_code)
    print(f"Output:\n{result.result}")
    
    sb.terminate()


def sandbox_with_ttl():
    """Sandbox with auto-termination timeout."""
    print("\nCreating sandbox with TTL...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311)
    )
    
    sb = sandbox.create()
    
    sb.update_ttl(300)  # Auto-terminate after 5 minutes
    print(f"Sandbox will auto-terminate in 300 seconds")
    
    result = sb.process.run_code("print('This sandbox will auto-terminate!')")
    print(f"Output: {result.result}")
    
    sb.terminate()


if __name__ == "__main__":
    basic_example()
    sandbox_with_packages()
    sandbox_with_ttl()
