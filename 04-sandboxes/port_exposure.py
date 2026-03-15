"""
Sandbox Port Exposure Example
=============================
Expose ports to make services accessible over the internet.
Great for running web servers, APIs, dashboards in sandboxes.

Run: python port_exposure.py
"""

from beam import Sandbox, Image, PythonVersion
from textwrap import dedent
import time


def expose_http_server():
    """Run a simple HTTP server and expose it."""
    print("Creating sandbox with HTTP server...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311)
    )
    
    sb = sandbox.create()
    
    sb.update_ttl(300)  # Keep alive for 5 minutes
    
    sb.process.exec("python3", "-m", "http.server", "8000", cwd="/workspace")
    
    time.sleep(2)
    
    url = sb.expose_port(8000)
    print(f"HTTP server running at: {url}")
    print("Server will auto-terminate in 5 minutes")
    
    return sb, url


def expose_flask_app():
    """Run a Flask app and expose it."""
    print("\nCreating sandbox with Flask app...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311).add_python_packages([
            "flask",
        ])
    )
    
    sb = sandbox.create()
    
    flask_app_code = dedent('''
        from flask import Flask, jsonify
        import os

        app = Flask(__name__)

        @app.route("/")
        def home():
            return jsonify({
                "message": "Hello from Beam Sandbox!",
                "status": "running"
            })

        @app.route("/health")
        def health():
            return jsonify({"healthy": True})

        if __name__ == "__main__":
            app.run(host="0.0.0.0", port=5000)
    ''').strip()
    
    setup_code = dedent(f"""
        with open('/workspace/app.py', 'w') as f:
            f.write('''{flask_app_code}''')
    """).strip()
    
    sb.process.run_code(setup_code)
    
    sb.process.exec("python3", "/workspace/app.py")
    
    time.sleep(3)
    
    url = sb.expose_port(5000)
    print(f"Flask app running at: {url}")
    
    sb.update_ttl(300)
    
    return sb, url


def expose_node_server():
    """Run a Node.js server in a sandbox."""
    print("\nCreating sandbox with Node.js server...")
    
    sandbox = Sandbox(
        image=Image().from_registry("node:20-alpine")
    )
    
    sb = sandbox.create()
    
    sb.update_ttl(300)
    
    sb.process.exec("sh", "-c", "npx http-server -p 3000 -c-1")
    
    time.sleep(3)
    
    url = sb.expose_port(3000)
    print(f"Node.js server running at: {url}")
    
    return sb, url


def expose_multiple_ports():
    """Expose multiple services on different ports."""
    print("\nCreating sandbox with multiple services...")
    
    sandbox = Sandbox(
        image=Image(python_version=PythonVersion.Python311).add_python_packages([
            "flask",
        ])
    )
    
    sb = sandbox.create()
    
    api_code = dedent('''
        from flask import Flask, jsonify
        app = Flask(__name__)

        @app.route("/")
        def home():
            return jsonify({"service": "API", "port": 5000})

        if __name__ == "__main__":
            app.run(host="0.0.0.0", port=5000)
    ''').strip()
    
    admin_code = dedent('''
        from flask import Flask, jsonify
        app = Flask(__name__)

        @app.route("/")
        def home():
            return jsonify({"service": "Admin", "port": 5001})

        if __name__ == "__main__":
            app.run(host="0.0.0.0", port=5001)
    ''').strip()
    
    setup_code = dedent(f"""
        with open('/workspace/api.py', 'w') as f:
            f.write('''{api_code}''')

        with open('/workspace/admin.py', 'w') as f:
            f.write('''{admin_code}''')
    """).strip()
    
    sb.process.run_code(setup_code)
    
    sb.process.exec("python3", "/workspace/api.py")
    sb.process.exec("python3", "/workspace/admin.py")
    
    time.sleep(3)
    
    api_url = sb.expose_port(5000)
    admin_url = sb.expose_port(5001)
    
    print(f"API service: {api_url}")
    print(f"Admin service: {admin_url}")
    
    sb.update_ttl(300)
    
    return sb, api_url, admin_url


if __name__ == "__main__":
    print("=" * 50)
    print("Port Exposure Examples")
    print("=" * 50)
    
    sb1, url1 = expose_http_server()
    print(f"\nHTTP Server URL: {url1}")
    
    sb2, url2 = expose_flask_app()
    print(f"\nFlask App URL: {url2}")
    
    print("\n" + "=" * 50)
    print("Sandboxes are running. Press Ctrl+C to terminate.")
    print("=" * 50)
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nTerminating sandboxes...")
        sb1.terminate()
        sb2.terminate()
        print("Done!")
