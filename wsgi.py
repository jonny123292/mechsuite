"""
WSGI Entry Point for Cloud Deployment (Render, Railway, Heroku, Gunicorn, Waitress)
"""

import os
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # If run directly on Windows, use Waitress; otherwise fallback to app.run
    try:
        from waitress import serve
        print(f"Serving with Waitress WSGI on http://0.0.0.0:{port}")
        serve(app, host="0.0.0.0", port=port)
    except ImportError:
        app.run(host="0.0.0.0", port=port)

