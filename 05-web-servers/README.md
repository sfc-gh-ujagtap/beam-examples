# Web Servers

Host full web applications on Beam using ASGI frameworks like FastAPI.

## Examples

| File | Description | Status |
|------|-------------|--------|
| `fastapi_server.py` | FastAPI with automatic OpenAPI docs | ✅ Tested |
| `flask_server.py` | Flask web application with REST API | ✅ Tested |
| `streamlit_app.py` | Streamlit dashboard (requires Snowflake) | ⏳ Requires credentials |
| `streamlit_pod_deploy.py` | Deploy Streamlit using Pods | ⏳ Requires credentials |

## Test Results

### fastapi_server.py

**Deploy:** `python3 -m beam deploy fastapi_server.py:create_app`

**URL:** `https://fastapi-web-app-c8ad7ef-v1.app.beam.cloud`

| Endpoint | Method | Result |
|----------|--------|--------|
| `/` | GET | ✅ HTML welcome page |
| `/health` | GET | ✅ `{"status":"healthy","timestamp":"..."}` |
| `/items` | GET | ✅ List all items |
| `/items` | POST | ✅ Create item (returns 201) |
| `/items/{id}` | GET | ✅ Get item by ID |
| `/stats` | GET | ✅ Inventory statistics |
| `/docs` | GET | ✅ Swagger UI |
| `/redoc` | GET | ✅ ReDoc documentation |

**Performance:**
| Metric | Value |
|--------|-------|
| Cold Start | ~10s |
| Warm Response | ~1s |

**Example:**
```bash
# Create item
curl -X POST 'https://fastapi-web-app-c8ad7ef-v1.app.beam.cloud/items' \
  -H 'Authorization: Bearer $BEAM_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"name": "Test Item", "price": 29.99}'

# Response: {"id":1,"name":"Test Item","price":29.99,"in_stock":true,...}
```

---

### flask_server.py

**Deploy:** `python3 -m beam deploy flask_server.py:create_app`

**Note:** Flask is WSGI, requires `asgiref` for ASGI conversion.

---

## Quick Start

```bash
# Deploy FastAPI app
python3 -m beam deploy fastapi_server.py:create_app
```

## Key Features

- **Auto-scaling**: Beam handles scaling based on traffic
- **SSL/TLS**: All endpoints are HTTPS by default
- **Keep Warm**: Control container lifecycle with `keep_warm_seconds`
- **OpenAPI Docs**: FastAPI auto-generates `/docs` and `/redoc`

## Notes

- FastAPI is native ASGI - works directly with `@asgi` decorator
- Flask requires `asgiref.wsgi.WsgiToAsgi` wrapper
- Streamlit apps should use Pods for long-running hosting
- The handler function receives a `context` parameter and must return the ASGI app
