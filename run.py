"""
MechSuite Launcher Script
Checks dependencies, starts the Flask web application, and opens the default web browser.
"""

import sys
import webbrowser
import threading
import time


def open_browser(url: str):
    """Wait briefly for the server to start, then open the browser."""
    time.sleep(1.2)
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not automatically open browser: {e}")


def main():
    print("=" * 60)
    print("  MechSuite - Mechanical Engineering Analysis Platform")
    print("=" * 60)

    try:
        from app import app
    except ImportError as e:
        print(f"Error importing application: {e}")
        print("Please ensure required packages are installed: pip install -r requirements.txt")
        sys.exit(1)

    port = 5000
    url = f"http://127.0.0.1:{port}"
    print(f"-> Serving frontend and API at: {url}")
    print("-> Press Ctrl+C in this terminal to stop the server.\n")

    # Open browser in a separate background thread
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    # Start Flask application
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    main()

