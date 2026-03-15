"""
Sandbox File Operations Example
===============================
Upload, download, and manage files within sandboxes.
Great for processing user uploads, generating outputs, etc.

Run: python file_operations.py
"""

from beam import Sandbox, Image, PythonVersion
import tempfile
import os


def upload_and_process():
    """Upload files to sandbox, process them, download results."""
    print("Creating sandbox for file operations...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311).add_python_packages([
            "pandas",
        ])
    )
    
    sb = sandbox.create()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("name,value\n")
        f.write("alpha,10\n")
        f.write("beta,20\n")
        f.write("gamma,30\n")
        local_file = f.name
    
    print(f"Uploading {local_file} to sandbox...")
    sb.fs.upload_file(local_file, "/workspace/data.csv")
    
    result = sb.process.run_code("""
import pandas as pd

df = pd.read_csv('/workspace/data.csv')
print("Original data:")
print(df)

df['doubled'] = df['value'] * 2
df['squared'] = df['value'] ** 2

df.to_csv('/workspace/processed.csv', index=False)
print("\\nProcessed data saved to /workspace/processed.csv")
""")
    print(f"Processing output:\n{result.result}")
    
    output_file = tempfile.mktemp(suffix='.csv')
    sb.fs.download_file("/workspace/processed.csv", output_file)
    
    print(f"\nDownloaded processed file to {output_file}")
    with open(output_file, 'r') as f:
        print(f"Contents:\n{f.read()}")
    
    os.unlink(local_file)
    os.unlink(output_file)
    
    sb.terminate()


def upload_script_and_run():
    """Upload a Python script and execute it."""
    print("\nUploading and running a script...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311)
    )
    
    sb = sandbox.create()
    
    script_content = '''
import json
from datetime import datetime

def generate_report():
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "metrics": {
            "processed_items": 150,
            "success_rate": 0.98,
            "average_time_ms": 45.2,
        }
    }
    return report

if __name__ == "__main__":
    report = generate_report()
    print(json.dumps(report, indent=2))
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        script_file = f.name
    
    sb.fs.upload_file(script_file, "/workspace/report_generator.py")
    
    result = sb.process.run_code("exec(open('/workspace/report_generator.py').read())")
    print(f"Script output:\n{result.result}")
    
    os.unlink(script_file)
    sb.terminate()


def list_files():
    """List files in the sandbox filesystem."""
    print("\nListing sandbox files...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311)
    )
    
    sb = sandbox.create()
    
    sb.process.run_code("""
import os
os.makedirs('/workspace/data', exist_ok=True)
with open('/workspace/data/file1.txt', 'w') as f:
    f.write('Hello')
with open('/workspace/data/file2.txt', 'w') as f:
    f.write('World')
""")
    
    result = sb.process.run_code("""
import os
for root, dirs, files in os.walk('/workspace'):
    for file in files:
        path = os.path.join(root, file)
        size = os.path.getsize(path)
        print(f"{path}: {size} bytes")
""")
    print(f"Files in sandbox:\n{result.result}")
    
    sb.terminate()


if __name__ == "__main__":
    upload_and_process()
    upload_script_and_run()
    list_files()
