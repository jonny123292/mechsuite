"""
Beam Stress, Shear Force, Bending Moment, and Deflection Analyzer
Supports simply supported and cantilever beams with combinations of point loads
and uniformly distributed loads (UDL). Computes reactions, SFD, BMD, elastic deflection,
maximum bending stress, and factor of safety.
"""

from typing import Dict, List, Any
import numpy as np
from .materials import calculate_section_properties, get_material


def analyze_beam(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Solves beam mechanics.
    Expected parameters:
    - beam_type: 'simply_supported' or 'cantilever'
    - length_m: float (meters)
    - material_key: str or custom material dict with 'elastic_modulus_gpa', 'yield_strength_mpa'
    - section: dict with 'type' and dimension fields (e.g. rectangular with width, height)
    - point_loads: list of dicts {'position_m': float, 'magnitude_kn': float} (downward > 0)
    - udl_loads: list of dicts {'start_m': float, 'end_m': float, 'magnitude_kn_m': float} (downward > 0)
    - num_points: int (optional, default 201)
    """
    beam_type = params.get("beam_type", "simply_supported").lower()
    length = float(params.get("length_m", 5.0))
    if length <= 0:
        raise ValueError("Beam length must be greater than 0.")

    num_points = int(params.get("num_points", 251))
    x_pts = np.linspace(0.0, length, num_points)

    # Material properties
    mat_input = params.get("material", "steel_a36")
    if isinstance(mat_input, str):
        mat = get_material(mat_input)
        if not mat:
            mat = get_material("steel_a36")
    else:
        mat = mat_input

    e_gpa = float(mat.get("elastic_modulus_gpa", 200.0))
    yield_mpa = float(mat.get("yield_strength_mpa", 250.0))
    # E in N/m^2 (Pa): E_gpa * 1e9
    e_pa = e_gpa * 1e9

    # Section properties
    section_input = params.get("section", {"type": "rectangular", "width": 50.0, "height": 100.0})
    sec_type = section_input.get("type", "rectangular")
    sec_props = calculate_section_properties(sec_type, section_input)

    # I in m^4: I_mm4 * 1e-12
    i_m4 = sec_props["i_xx_mm4"] * 1e-12
    # Z in m^3: Z_mm3 * 1e-9
    z_m3 = sec_props["z_xx_mm3"] * 1e-9

    point_loads = params.get("point_loads", [])
    udl_loads = params.get("udl_loads", [])

    # Validate loads
    cleaned_point_loads = []
    for p in point_loads:
        pos = min(max(0.0, float(p.get("position_m", 0.0))), length)
        mag = float(p.get("magnitude_kn", 0.0))
        cleaned_point_loads.append({"position_m": pos, "magnitude_kn": mag})

    cleaned_udl = []
    for u in udl_loads:
        s = min(max(0.0, float(u.get("start_m", 0.0))), length)
        e = min(max(0.0, float(u.get("end_m", length))), length)
        if s > e:
            s, e = e, s
        mag = float(u.get("magnitude_kn_m", 0.0))
        cleaned_udl.append({"start_m": s, "end_m": e, "magnitude_kn_m": mag})

    # 1. Equilibrium / Reaction Calculations
    total_load_kn = sum(p["magnitude_kn"] for p in cleaned_point_loads)
    for u in cleaned_udl:
        total_load_kn += u["magnitude_kn_m"] * (u["end_m"] - u["start_m"])

    reactions: Dict[str, float] = {}

    if beam_type == "simply_supported":
        # Sum of moments about Left Support (x = 0):
        # R_B * L = sum(P_i * x_i) + sum(w_j * L_j * x_centroid_j)
        moment_about_a = 0.0
        for p in cleaned_point_loads:
            moment_about_a += p["magnitude_kn"] * p["position_m"]
        for u in cleaned_udl:
            u_len = u["end_m"] - u["start_m"]
            u_center = (u["start_m"] + u["end_m"]) / 2.0
            moment_about_a += u["magnitude_kn_m"] * u_len * u_center

        rb_kn = moment_about_a / length
        ra_kn = total_load_kn - rb_kn
        reactions = {
            "ra_kn": round(float(ra_kn), 4),
            "rb_kn": round(float(rb_kn), 4),
            "moment_a_kn_m": 0.0
        }

    elif beam_type == "cantilever":
        # Fixed at x = 0 (Left End), Free at x = L (Right End)
        # R_A balances total downward force
        ra_kn = total_load_kn
        # M_A balances clockwise moment of downward forces
        ma_kn_m = 0.0
        for p in cleaned_point_loads:
            ma_kn_m += p["magnitude_kn"] * p["position_m"]
        for u in cleaned_udl:
            u_len = u["end_m"] - u["start_m"]
            u_center = (u["start_m"] + u["end_m"]) / 2.0
            ma_kn_m += u["magnitude_kn_m"] * u_len * u_center

        reactions = {
            "ra_kn": round(float(ra_kn), 4),
            "rb_kn": 0.0,
            "moment_a_kn_m": round(float(ma_kn_m), 4)  # Reaction moment at fixed wall
        }
    else:
        raise ValueError(f"Unsupported beam_type: {beam_type}")

    # 2. Shear Force V(x) and Bending Moment M(x)
    # Standard sign convention:
    # Shear V(x) = sum of upward forces to the left of x minus downward forces to the left of x
    # Moment M(x) = sum of clockwise moments of left forces about section x
    v_kn = np.zeros(num_points)
    m_kn_m = np.zeros(num_points)

    for i, x in enumerate(x_pts):
        v = 0.0
        m = 0.0

        if beam_type == "simply_supported":
            # Upward reaction at x=0
            v += reactions["ra_kn"]
            m += reactions["ra_kn"] * x

        elif beam_type == "cantilever":
            # Upward reaction force at x=0
            v += reactions["ra_kn"]
            # Reaction moment at wall (counterclockwise restraint)
            m += reactions["ra_kn"] * x - reactions["moment_a_kn_m"]

        # Point loads
        for p in cleaned_point_loads:
            if x >= p["position_m"]:
                v -= p["magnitude_kn"]
                m -= p["magnitude_kn"] * (x - p["position_m"])

        # UDL loads
        for u in cleaned_udl:
            if x > u["start_m"]:
                covered_len = min(x, u["end_m"]) - u["start_m"]
                load_mag = u["magnitude_kn_m"] * covered_len
                # Centroid of the portion acting up to x
                centroid = u["start_m"] + covered_len / 2.0
                v -= load_mag
                m -= load_mag * (x - centroid)

        v_kn[i] = v
        m_kn_m[i] = m

    # 3. Deflection calculation y(x) in mm
    # Differential equation: d^2y/dx^2 = M(x) / (E * I)
    # M is in kN*m -> N*m is M * 1000
    # Curvature kappa(x) = (M * 1000) / (E_pa * I_m4)  [1/m]
    curvature = (m_kn_m * 1000.0) / (e_pa * i_m4)

    dx = length / (num_points - 1)
    
    # Cumulative numerical trapezoidal integration for slope theta (radians)
    # Cantilever boundary conditions: y(0) = 0, theta(0) = 0
    # Simply supported boundary conditions: y(0) = 0, y(L) = 0
    if beam_type == "cantilever":
        # theta(x) = int_0^x curvature(s) ds
        theta = np.zeros(num_points)
        for i in range(1, num_points):
            theta[i] = theta[i - 1] + 0.5 * (curvature[i - 1] + curvature[i]) * dx
        
        # y(x) = int_0^x theta(s) ds (in meters)
        y_m = np.zeros(num_points)
        for i in range(1, num_points):
            y_m[i] = y_m[i - 1] + 0.5 * (theta[i - 1] + theta[i]) * dx
    else:
        # Simply supported:
        # Let y*(x) be integral with theta(0) = 0
        theta_star = np.zeros(num_points)
        for i in range(1, num_points):
            theta_star[i] = theta_star[i - 1] + 0.5 * (curvature[i - 1] + curvature[i]) * dx
        
        y_star = np.zeros(num_points)
        for i in range(1, num_points):
            y_star[i] = y_star[i - 1] + 0.5 * (theta_star[i - 1] + theta_star[i]) * dx
        
        # Linear correction so y(L) = 0: y(x) = y_star(x) - x * (y_star(L) / L)
        y_end = y_star[-1]
        y_m = y_star - (x_pts / length) * y_end

    # Convert deflection to mm (negative indicates downward sag)
    y_mm = y_m * 1000.0

    # 4. Critical Values & Stress Evaluation
    max_bending_moment_kn_m = float(np.max(np.abs(m_kn_m)))
    max_shear_force_kn = float(np.max(np.abs(v_kn)))
    max_deflection_mm = float(np.max(np.abs(y_mm)))
    deflection_at_max = float(y_mm[np.argmax(np.abs(y_mm))])

    # Stress sigma = M / Z
    # M in N*m = max_bending_moment_kn_m * 1e3
    # Z in m^3 = z_m3
    # sigma in Pa = (M * 1e3) / z_m3
    # sigma in MPa = sigma / 1e6
    if z_m3 > 0:
        max_stress_mpa = (max_bending_moment_kn_m * 1e3) / (z_m3 * 1e6)
    else:
        max_stress_mpa = 0.0

    # Factor of Safety
    fos = yield_mpa / max_stress_mpa if max_stress_mpa > 1e-6 else 999.0

    if fos >= 1.5:
        safety_status = "Safe"
        safety_color = "#10b981"  # Emerald green
    elif fos >= 1.0:
        safety_status = "Marginal"
        safety_color = "#f59e0b"  # Amber
    else:
        safety_status = "Yielding / Critical Risk"
        safety_color = "#ef4444"  # Red

    # Allowable deflection standard (e.g. L / 250 or L / 360)
    allowable_deflection_mm = (length * 1000.0) / 250.0

    return {
        "success": True,
        "beam_type": beam_type,
        "length_m": length,
        "reactions": reactions,
        "section_properties": sec_props,
        "material": mat,
        "critical_values": {
            "max_shear_force_kn": round(max_shear_force_kn, 3),
            "max_bending_moment_kn_m": round(max_bending_moment_kn_m, 3),
            "max_stress_mpa": round(max_stress_mpa, 2),
            "yield_strength_mpa": round(yield_mpa, 2),
            "factor_of_safety": round(fos, 2) if fos < 100 else "> 100",
            "safety_status": safety_status,
            "safety_color": safety_color,
            "max_deflection_mm": round(max_deflection_mm, 3),
            "deflection_actual_mm": round(deflection_at_max, 3),
            "allowable_deflection_mm": round(allowable_deflection_mm, 2),
            "deflection_acceptable": max_deflection_mm <= allowable_deflection_mm
        },
        "diagrams": {
            "x_m": [round(float(x), 3) for x in x_pts],
            "shear_force_kn": [round(float(v), 3) for v in v_kn],
            "bending_moment_kn_m": [round(float(m), 3) for m in m_kn_m],
            "deflection_mm": [round(float(y), 4) for y in y_mm]
        },
        "point_loads": cleaned_point_loads,
        "udl_loads": cleaned_udl
    }

