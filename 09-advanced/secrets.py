"""
Secrets Management Example
==========================
Securely store and access API keys, tokens, and credentials.
Secrets are encrypted and injected as environment variables.

CLI: beam secret create MY_SECRET "secret_value"
Deploy: beam deploy secrets.py:handler
"""

from beam import endpoint, Image


@endpoint(
    name="api-with-secrets",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11").add_python_packages([
        "requests",
    ]),
    secrets=["OPENAI_API_KEY"],  # Inject this secret as env var
)
def handler(**inputs):
    """
    Endpoint that uses a secret API key.
    
    First, create the secret:
        beam secret create OPENAI_API_KEY "sk-..."
    
    Then deploy:
        beam deploy secrets.py:handler
    
    The secret is available as os.environ["OPENAI_API_KEY"]
    """
    import os
    
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return {"error": "OPENAI_API_KEY not configured"}
    
    return {
        "api_key_configured": True,
        "key_prefix": api_key[:7] + "...",
    }


@endpoint(
    name="multi-secret-api",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11").add_python_packages([
        "requests",
    ]),
    secrets=["DATABASE_URL", "API_KEY", "JWT_SECRET"],  # Multiple secrets
)
def multi_secret_handler(**inputs):
    """
    Endpoint with multiple secrets.
    
    Create secrets:
        beam secret create DATABASE_URL "postgresql://..."
        beam secret create API_KEY "key_..."
        beam secret create JWT_SECRET "jwt_..."
    """
    import os
    
    secrets_status = {}
    for secret_name in ["DATABASE_URL", "API_KEY", "JWT_SECRET"]:
        value = os.environ.get(secret_name)
        secrets_status[secret_name] = "configured" if value else "missing"
    
    return {"secrets": secrets_status}


@endpoint(
    name="env-vars-api",
    cpu=1,
    memory="256Mi",
    image=Image(python_version="python3.11"),
    secrets=["API_KEY"],  # Secrets injected as env vars
)
def env_vars_handler(**inputs):
    """
    Endpoint with secrets.
    
    Secrets are injected as environment variables.
    """
    import os
    
    return {
        "api_key_configured": bool(os.environ.get("API_KEY")),
        "api_key_prefix": os.environ.get("API_KEY", "")[:10] + "..." if os.environ.get("API_KEY") else None,
    }


@endpoint(
    name="database-api",
    cpu=1,
    memory="512Mi",
    image=Image(python_version="python3.11").add_python_packages([
        "psycopg2-binary",
    ]),
    secrets=["DATABASE_URL"],
)
def database_handler(**inputs):
    """
    Endpoint that connects to a database using secret credentials.
    
    Create secret:
        beam secret create DATABASE_URL "postgresql://user:pass@host:5432/db"
    """
    import os
    
    db_url = os.environ.get("DATABASE_URL")
    
    if not db_url:
        return {"error": "DATABASE_URL not configured"}
    
    parsed = db_url.split("@")
    host_part = parsed[-1] if len(parsed) > 1 else "unknown"
    
    return {
        "database_configured": True,
        "host": host_part.split("/")[0] if "/" in host_part else host_part,
    }


"""
Secret Management Commands:

# Create a secret
beam secret create SECRET_NAME "secret_value"

# List secrets
beam secret list

# Delete a secret
beam secret delete SECRET_NAME

# Update a secret (delete + create)
beam secret delete SECRET_NAME
beam secret create SECRET_NAME "new_value"

Best Practices:
1. Never hardcode secrets in code
2. Use descriptive secret names (e.g., STRIPE_API_KEY, not KEY1)
3. Rotate secrets regularly
4. Use different secrets for dev/staging/prod
5. Audit secret access in your Beam dashboard
"""
