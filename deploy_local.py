"""
Production Local WSGI Server Runner (using Waitress)
Use this to test production-grade multi-threaded serving on your local machine.
"""

import os
from waitress import serve
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 60)
    print(f"  MechSuite Production WSGI Server (Waitress)")
    print(f"  Running on http://127.0.0.1:{port}")
    print("=" * 60)
    serve(app, host="127.0.0.1", port=port, threads=6)

