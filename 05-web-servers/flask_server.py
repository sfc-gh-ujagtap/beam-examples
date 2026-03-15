"""
Flask Web Server Example
========================
Host a Flask application on Beam with ASGI support.
Full web server with routes, templates, and static files.

Deploy: beam deploy flask_server.py
"""

from beam import asgi, Image
from textwrap import dedent


image = Image(python_version="python3.11").add_python_packages([
    "flask",
    "asgiref",
])


@asgi(
    name="flask-web-app",
    cpu=1,
    memory="512Mi",
    image=image,
    keep_warm_seconds=300,
)
def create_app(context):
    """Create and return Flask WSGI application."""
    from flask import Flask, jsonify, request, render_template_string
    from asgiref.wsgi import WsgiToAsgi
    
    app = Flask(__name__)
    
    HTML_TEMPLATE = dedent("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Flask on Beam</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #333; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                code { background: #e0e0e0; padding: 2px 6px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>Flask on Beam</h1>
            <p>Welcome to your Flask application running on Beam.cloud!</p>
            
            <h2>Available Endpoints</h2>
            <div class="endpoint">
                <strong>GET /</strong> - This page
            </div>
            <div class="endpoint">
                <strong>GET /api/health</strong> - Health check
            </div>
            <div class="endpoint">
                <strong>GET /api/info</strong> - Server info
            </div>
            <div class="endpoint">
                <strong>POST /api/echo</strong> - Echo JSON payload
            </div>
            <div class="endpoint">
                <strong>GET /api/items</strong> - List items
            </div>
            <div class="endpoint">
                <strong>POST /api/items</strong> - Create item
            </div>
        </body>
        </html>
    """).strip()
    
    items_db = []
    
    @app.route("/")
    def home():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route("/api/health")
    def health():
        return jsonify({"status": "healthy", "service": "flask-web-app"})
    
    @app.route("/api/info")
    def info():
        import platform
        import sys
        return jsonify({
            "python_version": sys.version,
            "platform": platform.platform(),
            "flask_version": __import__('flask').__version__,
        })
    
    @app.route("/api/echo", methods=["POST"])
    def echo():
        data = request.get_json() or {}
        return jsonify({
            "received": data,
            "method": request.method,
            "content_type": request.content_type,
        })
    
    @app.route("/api/items", methods=["GET"])
    def list_items():
        return jsonify({"items": items_db, "count": len(items_db)})
    
    @app.route("/api/items", methods=["POST"])
    def create_item():
        data = request.get_json() or {}
        item = {
            "id": len(items_db) + 1,
            "name": data.get("name", "Unnamed"),
            "description": data.get("description", ""),
        }
        items_db.append(item)
        return jsonify(item), 201
    
    @app.route("/api/items/<int:item_id>", methods=["GET"])
    def get_item(item_id):
        for item in items_db:
            if item["id"] == item_id:
                return jsonify(item)
            return jsonify({"error": "Item not found"}), 404
    
    return WsgiToAsgi(app)
