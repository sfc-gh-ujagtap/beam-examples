"""
FastAPI Web Server Example
==========================
Host a FastAPI application on Beam with automatic OpenAPI docs.
Modern async Python web framework.

Deploy: beam deploy fastapi_server.py
"""

from beam import asgi, Image


image = Image(python_version="python3.11").add_python_packages([
    "fastapi",
    "uvicorn",
    "pydantic",
])


@asgi(
    name="fastapi-web-app-public",
    cpu=1,
    memory="512Mi",
    image=image,
    keep_warm_seconds=300,
    authorized=False,  # Public access - no auth token required
)
def create_app(context):
    """Create and return FastAPI ASGI application."""
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel
    from typing import Optional
    from datetime import datetime
    
    app = FastAPI(
        title="FastAPI on Beam",
        description="A FastAPI application running on Beam.cloud",
        version="1.0.0",
    )
    
    class Item(BaseModel):
        name: str
        description: Optional[str] = None
        price: float
        in_stock: bool = True
    
    class ItemResponse(BaseModel):
        id: int
        name: str
        description: Optional[str]
        price: float
        in_stock: bool
        created_at: str
    
    items_db: dict[int, ItemResponse] = {}
    item_counter = 0
    
    @app.get("/", response_class=HTMLResponse)
    async def home():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>FastAPI on Beam</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #009688; }
                a { color: #009688; }
                .card { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 8px; }
            </style>
        </head>
        <body>
            <h1>FastAPI on Beam</h1>
            <p>Welcome to your FastAPI application running on Beam.cloud!</p>
            
            <div class="card">
                <h3>Interactive API Documentation</h3>
                <p><a href="/docs">Swagger UI</a> - Interactive API explorer</p>
                <p><a href="/redoc">ReDoc</a> - Alternative documentation</p>
            </div>
            
            <div class="card">
                <h3>API Endpoints</h3>
                <ul>
                    <li>GET /health - Health check</li>
                    <li>GET /items - List all items</li>
                    <li>POST /items - Create item</li>
                    <li>GET /items/{id} - Get item by ID</li>
                    <li>DELETE /items/{id} - Delete item</li>
                </ul>
            </div>
        </body>
        </html>
        """
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    @app.get("/items", response_model=list[ItemResponse])
    async def list_items():
        return list(items_db.values())
    
    @app.post("/items", response_model=ItemResponse, status_code=201)
    async def create_item(item: Item):
        nonlocal item_counter
        item_counter += 1
        
        item_response = ItemResponse(
            id=item_counter,
            name=item.name,
            description=item.description,
            price=item.price,
            in_stock=item.in_stock,
            created_at=datetime.utcnow().isoformat(),
        )
        items_db[item_counter] = item_response
        return item_response
    
    @app.get("/items/{item_id}", response_model=ItemResponse)
    async def get_item(item_id: int):
        if item_id not in items_db:
            raise HTTPException(status_code=404, detail="Item not found")
        return items_db[item_id]
    
    @app.delete("/items/{item_id}")
    async def delete_item(item_id: int):
        if item_id not in items_db:
            raise HTTPException(status_code=404, detail="Item not found")
        del items_db[item_id]
        return {"message": "Item deleted", "id": item_id}
    
    @app.get("/stats")
    async def stats():
        total_value = sum(item.price for item in items_db.values())
        in_stock = sum(1 for item in items_db.values() if item.in_stock)
        return {
            "total_items": len(items_db),
            "in_stock": in_stock,
            "out_of_stock": len(items_db) - in_stock,
            "total_inventory_value": total_value,
        }
    
    return app
