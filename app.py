"""
MechSuite - Mechanical Engineering Web Application & REST API
Built with Flask. Serves the interactive frontend and provides engineering calculation APIs.
"""

import os
from flask import Flask, jsonify, request, send_from_directory
from engine import (
    MATERIALS,
    get_material,
    calculate_section_properties,
    analyze_beam,
    analyze_pipe_flow,
    analyze_carnot_cycle,
    analyze_rankine_cycle,
    analyze_heat_exchanger
)

# Base directory for frontend static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")


# ---------------- Frontend Route ----------------
@app.route("/")
def index():
    """Serve the main frontend dashboard."""
    return send_from_directory(FRONTEND_DIR, "Index.html")


@app.route("/<path:path>")
def serve_static(path):
    """Serve static assets (CSS, JS, images, etc.)."""
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "Index.html")


# ---------------- REST API Routes ----------------
@app.route("/api/health", methods=["GET"])
def health_check():
    """Application health status."""
    return jsonify({
        "status": "healthy",
        "app": "MechSuite Mechanical Engineering Platform",
        "version": "1.0.0"
    })


@app.route("/api/materials", methods=["GET"])
def get_materials_list():
    """Retrieve catalog of standard engineering materials."""
    return jsonify({
        "success": True,
        "materials": MATERIALS
    })


@app.route("/api/section/properties", methods=["POST"])
def get_section_properties():
    """Compute geometric properties for a given cross section."""
    try:
        data = request.get_json(force=True) or {}
        section_type = data.get("type", "rectangular")
        props = calculate_section_properties(section_type, data)
        return jsonify({"success": True, "properties": props})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/beam/analyze", methods=["POST"])
def solve_beam():
    """Run beam stress, SFD, BMD, and deflection analysis."""
    try:
        data = request.get_json(force=True) or {}
        result = analyze_beam(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/fluids/pipe-flow", methods=["POST"])
def solve_pipe_flow():
    """Run pipe friction, Reynolds, head loss, and pressure drop analysis."""
    try:
        data = request.get_json(force=True) or {}
        result = analyze_pipe_flow(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/thermo/carnot", methods=["POST"])
def solve_carnot():
    """Calculate Carnot cycle limits."""
    try:
        data = request.get_json(force=True) or {}
        result = analyze_carnot_cycle(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/thermo/rankine", methods=["POST"])
def solve_rankine():
    """Calculate Rankine power cycle performance."""
    try:
        data = request.get_json(force=True) or {}
        result = analyze_rankine_cycle(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/thermo/heat-exchanger", methods=["POST"])
def solve_heat_exchanger():
    """Calculate LMTD and heat transfer duty."""
    try:
        data = request.get_json(force=True) or {}
        result = analyze_heat_exchanger(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting MechSuite on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)

