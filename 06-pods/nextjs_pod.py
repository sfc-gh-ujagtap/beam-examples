"""
Next.js Pod Example
===================
Deploy a Next.js application as a long-running Pod.
Great for full-stack JavaScript applications.

Run: python nextjs_pod.py
"""

from beam import Pod, Image
from textwrap import dedent


def create_nextjs_pod():
    """Deploy a Next.js application."""
    print("Creating Next.js pod...")
    
    nextjs_setup = dedent("""
        # Create a simple Next.js app inline
        mkdir -p /app
        cd /app

        # Create package.json
        cat > package.json << 'PACKAGE'
        {
          "name": "beam-nextjs-app",
          "version": "1.0.0",
          "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start -p 3000"
          },
          "dependencies": {
            "next": "14.0.0",
            "react": "18.2.0",
            "react-dom": "18.2.0"
          }
        }
        PACKAGE

        # Create pages directory
        mkdir -p pages

        # Create index page
        cat > pages/index.js << 'PAGE'
        export default function Home() {
          return (
            <div style={{ 
              fontFamily: 'Arial, sans-serif', 
              maxWidth: '800px', 
              margin: '50px auto', 
              padding: '20px' 
            }}>
              <h1 style={{ color: '#0070f3' }}>Next.js on Beam</h1>
              <p>Welcome to your Next.js application running on Beam.cloud!</p>
              <div style={{ 
                background: '#f5f5f5', 
                padding: '20px', 
                borderRadius: '8px',
                marginTop: '20px'
              }}>
                <h2>Features</h2>
                <ul>
                  <li>Server-side rendering</li>
                  <li>API routes</li>
                  <li>Static generation</li>
                  <li>Automatic scaling</li>
                </ul>
              </div>
            </div>
          )
        }
        PAGE

        # Create API route
        mkdir -p pages/api
        cat > pages/api/hello.js << 'API'
        export default function handler(req, res) {
          res.status(200).json({ 
            message: 'Hello from Next.js API!',
            timestamp: new Date().toISOString()
          })
        }
        API

        # Create health check API
        cat > pages/api/health.js << 'HEALTH'
        export default function handler(req, res) {
          res.status(200).json({ healthy: true })
        }
        HEALTH

        # Install dependencies and build
        npm install
        npm run build
        npm start
    """).strip()
    
    pod = Pod(
        name="nextjs-app",
        image=Image(
            base_image="node:20-alpine",
            commands=[
                "npm install -g npm@latest",
            ],
        ),
        cpu=2,
        memory="2Gi",
        ports=[3000],
        entrypoint=["sh", "-c", nextjs_setup],
        env={
            "NODE_ENV": "production",
        },
    )
    
    result = pod.create()
    print(f"Next.js pod created!")
    print(f"URL: {result.url}")
    print(f"API endpoint: {result.url}/api/hello")
    return result


def create_nextjs_with_code_mount():
    """Deploy Next.js with mounted code directory."""
    print("\nCreating Next.js pod with code mount...")
    
    pod = Pod(
        name="nextjs-dashboard",
        image=Image(
            base_image="node:20-alpine",
        ),
        cpu=2,
        memory="4Gi",
        ports=[3000],
        entrypoint=["sh", "-c", "cd /mnt/code && npm install && npm run build && npm start"],
        env={
            "NODE_ENV": "production",
        },
    )
    
    result = pod.create()
    print(f"Next.js dashboard pod created!")
    print(f"URL: {result.url}")
    return result


def create_express_pod():
    """Deploy an Express.js API server."""
    print("\nCreating Express.js pod...")
    
    express_setup = dedent("""
        mkdir -p /app
        cd /app

        cat > package.json << 'PACKAGE'
        {
          "name": "express-api",
          "version": "1.0.0",
          "main": "server.js",
          "dependencies": {
            "express": "^4.18.2",
            "cors": "^2.8.5"
          }
        }
        PACKAGE

        cat > server.js << 'SERVER'
        const express = require('express');
        const cors = require('cors');

        const app = express();
        app.use(cors());
        app.use(express.json());

        const items = [];

        app.get('/', (req, res) => {
          res.json({ 
            service: 'Express API',
            endpoints: ['/items', '/health']
          });
        });

        app.get('/health', (req, res) => {
          res.json({ healthy: true });
        });

        app.get('/items', (req, res) => {
          res.json({ items, count: items.length });
        });

        app.post('/items', (req, res) => {
          const item = { id: items.length + 1, ...req.body };
          items.push(item);
          res.status(201).json(item);
        });

        app.listen(3000, '0.0.0.0', () => {
          console.log('Express server running on port 3000');
        });
        SERVER

        npm install
        node server.js
    """).strip()
    
    pod = Pod(
        name="express-api",
        image=Image(base_image="node:20-alpine"),
        cpu=1,
        memory="512Mi",
        ports=[3000],
        entrypoint=["sh", "-c", express_setup],
        env={
            "NODE_ENV": "production",
        },
    )
    
    result = pod.create()
    print(f"Express.js pod created!")
    print(f"URL: {result.url}")
    return result


if __name__ == "__main__":
    print("=" * 50)
    print("Node.js Pod Examples")
    print("=" * 50)
    
    nextjs_pod = create_nextjs_pod()
    express_pod = create_express_pod()
    
    print("\n" + "=" * 50)
    print("Pods are now running!")
    print("=" * 50)
