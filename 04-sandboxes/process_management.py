"""
Sandbox Process Management Example
==================================
Execute shell commands, run background processes,
and stream logs in real-time.

Run: python process_management.py
"""

from beam import Sandbox, Image, PythonVersion
from textwrap import dedent
import time


def run_shell_commands():
    """Execute shell commands in sandbox."""
    print("Running shell commands...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311)
    )
    
    sb = sandbox.create()
    
    process = sb.process.exec("ls", "-la", "/")
    print(f"Root directory:\n{process.logs.read()}")
    process.wait()
    
    process = sb.process.exec("sh", "-c", "echo 'Hello' && sleep 1 && echo 'World'")
    print(f"Command output:\n{process.logs.read()}")
    process.wait()
    
    process = sb.process.exec("sh", "-c", "cat /etc/os-release | head -5")
    print(f"OS info:\n{process.logs.read()}")
    process.wait()
    
    sb.terminate()


def background_process():
    """Run a background process and monitor it."""
    print("\nRunning background process...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311)
    )
    
    sb = sandbox.create()
    
    server_code = dedent('''
        import time
        import sys

        for i in range(10):
            print(f"Processing item {i+1}/10...", flush=True)
            time.sleep(0.5)
        print("Done!", flush=True)
    ''').strip()
    
    setup_code = dedent(f"""
        with open('/workspace/server.py', 'w') as f:
            f.write('''{server_code}''')
    """).strip()
    
    sb.process.run_code(setup_code)
    
    process = sb.process.exec("python3", "/workspace/server.py")
    
    print("Streaming logs from background process:")
    for line in process.logs:
        print(f"  > {line}", end="")
    
    process.wait()
    print(f"\nProcess completed with exit code: {process.exit_code}")
    
    sb.terminate()


def run_with_working_directory():
    """Run commands in specific directories."""
    print("\nRunning commands in specific directories...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311)
    )
    
    sb = sandbox.create()
    
    sb.process.exec("mkdir", "-p", "/workspace/project/src")
    
    setup_code = dedent("""
        with open('/workspace/project/src/main.py', 'w') as f:
            f.write('print("Hello from src directory!")')
    """).strip()
    
    sb.process.run_code(setup_code)
    
    process = sb.process.exec("python3", "main.py", cwd="/workspace/project/src")
    print(f"Output: {process.logs.read()}")
    process.wait()
    
    sb.terminate()


def install_and_run():
    """Install packages at runtime and use them."""
    print("\nInstalling packages at runtime...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311)
    )
    
    sb = sandbox.create()
    
    print("Installing requests package...")
    process = sb.process.exec("pip", "install", "requests", "-q")
    process.wait()
    
    request_code = dedent("""
        import requests
        response = requests.get('https://httpbin.org/json')
        print(f"Status: {response.status_code}")
        print(f"Data: {response.json()['slideshow']['title']}")
    """).strip()
    
    result = sb.process.run_code(request_code)
    print(f"Output:\n{result.result}")
    
    sb.terminate()


if __name__ == "__main__":
    run_shell_commands()
    background_process()
    run_with_working_directory()
    install_and_run()
