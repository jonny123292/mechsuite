"""
Fluid Mechanics & Pipe Hydraulics Solver
Calculates Reynolds number, flow regime, Darcy friction factor (Swamee-Jain / Colebrook),
major and minor head losses (Darcy-Weisbach), pressure drop, and pumping power.
"""

from typing import Dict, Any
import math

STANDARD_FLUIDS: Dict[str, Dict[str, Any]] = {
    "water_20c": {
        "name": "Water (20°C)",
        "density_kg_m3": 998.2,
        "viscosity_pa_s": 1.002e-3,
        "description": "Standard liquid water at 20°C and atmospheric pressure."
    },
    "engine_oil": {
        "name": "Engine Oil (SAE 30, 20°C)",
        "density_kg_m3": 880.0,
        "viscosity_pa_s": 0.290,
        "description": "Medium motor oil at ambient temperature."
    },
    "air_20c": {
        "name": "Air (20°C, 1 atm)",
        "density_kg_m3": 1.204,
        "viscosity_pa_s": 1.825e-5,
        "description": "Dry atmospheric air at standard temperature and pressure."
    },
    "diesel_fuel": {
        "name": "Diesel Fuel (20°C)",
        "density_kg_m3": 830.0,
        "viscosity_pa_s": 3.0e-3,
        "description": "Commercial light diesel oil."
    }
}

PIPE_ROUGHNESS: Dict[str, float] = {
    "commercial_steel": 0.045,   # mm
    "drawn_copper": 0.0015,      # mm
    "pvc_plastic": 0.0015,       # mm
    "cast_iron": 0.26,           # mm
    "galvanized_iron": 0.15,     # mm
    "concrete": 1.0              # mm
}


def analyze_pipe_flow(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes hydraulics in a pressurized pipe.
    Input parameters:
    - diameter_mm: float (internal diameter in mm)
    - length_m: float (pipe length in meters)
    - flow_rate_m3_h: float (volumetric flow rate in m^3/hr) OR flow_velocity_m_s: float (m/s)
    - fluid: str key or dict with 'density_kg_m3' and 'viscosity_pa_s'
    - pipe_material: str key or roughness_mm: float
    - minor_loss_k: float (sum of minor loss coefficients K)
    - pump_efficiency: float (0.1 to 1.0, default 0.75)
    """
    d_mm = float(params.get("diameter_mm", 50.0))
    if d_mm <= 0:
        raise ValueError("Pipe diameter must be greater than 0.")
    d_m = d_mm / 1000.0

    l_m = float(params.get("length_m", 100.0))
    if l_m < 0:
        raise ValueError("Pipe length must be non-negative.")

    # Fluid properties
    fluid_in = params.get("fluid", "water_20c")
    if isinstance(fluid_in, str):
        fluid_data = STANDARD_FLUIDS.get(fluid_in, STANDARD_FLUIDS["water_20c"])
    else:
        fluid_data = fluid_in

    rho = float(fluid_data.get("density_kg_m3", 998.2))
    mu = float(fluid_data.get("viscosity_pa_s", 1.002e-3))
    if rho <= 0 or mu <= 0:
        raise ValueError("Density and dynamic viscosity must be positive.")

    # Pipe roughness
    roughness_in = params.get("roughness_mm")
    if roughness_in is not None:
        roughness_mm = float(roughness_in)
    else:
        pipe_mat = params.get("pipe_material", "commercial_steel")
        roughness_mm = PIPE_ROUGHNESS.get(pipe_mat, 0.045)
    roughness_m = roughness_mm / 1000.0

    # Cross-sectional area
    area_m2 = (math.pi / 4.0) * (d_m ** 2)

    # Velocity and Flow Rate
    if "flow_velocity_m_s" in params and params["flow_velocity_m_s"] is not None:
        velocity = float(params["flow_velocity_m_s"])
        flow_rate_m3_s = velocity * area_m2
        flow_rate_m3_h = flow_rate_m3_s * 3600.0
    else:
        flow_rate_m3_h = float(params.get("flow_rate_m3_h", 18.0))  # Default 18 m^3/h (5 L/s)
        flow_rate_m3_s = flow_rate_m3_h / 3600.0
        velocity = flow_rate_m3_s / area_m2

    flow_rate_l_s = flow_rate_m3_s * 1000.0

    # Reynolds Number: Re = rho * v * D / mu
    reynolds = (rho * velocity * d_m) / mu if mu > 0 else 0.0

    # Flow regime classification
    if reynolds < 2300:
        flow_regime = "Laminar"
        regime_badge = "info"
    elif reynolds < 4000:
        flow_regime = "Transition"
        regime_badge = "warning"
    else:
        flow_regime = "Turbulent"
        regime_badge = "primary"

    # Darcy friction factor calculation
    # Laminar: f = 64 / Re
    # Turbulent: Swamee-Jain explicit equation
    relative_roughness = roughness_m / d_m

    if reynolds < 1e-3:
        friction_factor = 0.0
    elif reynolds < 2300:
        friction_factor = 64.0 / reynolds
    else:
        # Swamee-Jain formula
        term = (relative_roughness / 3.7) + (5.74 / (reynolds ** 0.9))
        term = max(1e-9, term)
        friction_factor = 0.25 / (math.log10(term) ** 2)

    g = 9.80665  # m/s^2

    # Dynamic head (velocity head): v^2 / (2g)
    velocity_head_m = (velocity ** 2) / (2.0 * g)

    # Major head loss (friction): h_f = f * (L / D) * (v^2 / 2g)
    major_loss_m = friction_factor * (l_m / d_m) * velocity_head_m

    # Minor head loss: h_m = sum(K) * (v^2 / 2g)
    minor_k = float(params.get("minor_loss_k", 2.5))
    minor_loss_m = minor_k * velocity_head_m

    total_head_loss_m = major_loss_m + minor_loss_m

    # Pressure Drop: delta_P = rho * g * h_total
    delta_p_pa = rho * g * total_head_loss_m
    delta_p_kpa = delta_p_pa / 1000.0
    delta_p_bar = delta_p_pa / 100000.0

    # Pumping Power
    # Hydraulic power: P_hyd = Q * delta_P (in Watts)
    hydraulic_power_w = flow_rate_m3_s * delta_p_pa
    hydraulic_power_kw = hydraulic_power_w / 1000.0

    pump_efficiency = float(params.get("pump_efficiency", 0.75))
    pump_efficiency = min(max(0.1, pump_efficiency), 1.0)
    electrical_power_kw = hydraulic_power_kw / pump_efficiency

    return {
        "success": True,
        "input_summary": {
            "diameter_mm": round(d_mm, 2),
            "length_m": round(l_m, 2),
            "roughness_mm": round(roughness_mm, 4),
            "relative_roughness": round(relative_roughness, 6),
            "fluid": fluid_data.get("name", "Custom"),
            "density_kg_m3": round(rho, 2),
            "viscosity_pa_s": mu,
            "minor_loss_k": round(minor_k, 2)
        },
        "flow_results": {
            "flow_rate_m3_h": round(flow_rate_m3_h, 3),
            "flow_rate_l_s": round(flow_rate_l_s, 3),
            "flow_velocity_m_s": round(velocity, 3),
            "reynolds_number": round(reynolds, 1),
            "flow_regime": flow_regime,
            "regime_badge": regime_badge,
            "darcy_friction_factor": round(friction_factor, 5),
            "velocity_head_m": round(velocity_head_m, 4)
        },
        "head_losses": {
            "major_friction_loss_m": round(major_loss_m, 3),
            "minor_fitting_loss_m": round(minor_loss_m, 3),
            "total_head_loss_m": round(total_head_loss_m, 3)
        },
        "pressure_drop": {
            "pressure_drop_pa": round(delta_p_pa, 1),
            "pressure_drop_kpa": round(delta_p_kpa, 2),
            "pressure_drop_bar": round(delta_p_bar, 4)
        },
        "power_requirements": {
            "hydraulic_power_kw": round(hydraulic_power_kw, 3),
            "pump_efficiency_percent": round(pump_efficiency * 100, 1),
            "pump_shaft_power_kw": round(electrical_power_kw, 3)
        }
    }

