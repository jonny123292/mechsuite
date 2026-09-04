"""
Thermodynamics & Heat Transfer Engine
Includes Carnot cycle, Rankine steam power cycle, and Heat Exchanger LMTD analysis.
"""

from typing import Dict, Any
import math


def analyze_carnot_cycle(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes ideal Carnot cycle thermodynamic limits.
    Parameters:
    - th_celsius: High reservoir temperature (°C)
    - tl_celsius: Low reservoir temperature (°C)
    - heat_input_kw: Heat added at TH (kW)
    """
    th_c = float(params.get("th_celsius", 500.0))
    tl_c = float(params.get("tl_celsius", 30.0))

    if tl_c >= th_c:
        raise ValueError("High temperature TH must be strictly greater than low temperature TL.")

    th_k = th_c + 273.15
    tl_k = tl_c + 273.15

    if tl_k <= 0:
        raise ValueError("Absolute temperature must be above absolute zero.")

    # Thermal efficiency: eta = 1 - (TL / TH)
    efficiency = 1.0 - (tl_k / th_k)
    efficiency_pct = efficiency * 100.0

    q_in_kw = float(params.get("heat_input_kw", 1000.0))
    w_net_kw = q_in_kw * efficiency
    q_out_kw = q_in_kw - w_net_kw

    # Coefficients of Performance for inverse cycles
    delta_t = th_k - tl_k
    cop_refrigerator = tl_k / delta_t
    cop_heat_pump = th_k / delta_t

    return {
        "success": True,
        "temperatures": {
            "th_celsius": th_c,
            "th_kelvin": round(th_k, 2),
            "tl_celsius": tl_c,
            "tl_kelvin": round(tl_k, 2)
        },
        "performance": {
            "carnot_efficiency_percent": round(efficiency_pct, 2),
            "heat_input_kw": round(q_in_kw, 2),
            "net_power_output_kw": round(w_net_kw, 2),
            "heat_rejected_kw": round(q_out_kw, 2),
            "cop_refrigerator": round(cop_refrigerator, 2),
            "cop_heat_pump": round(cop_heat_pump, 2)
        },
        "description": "Carnot cycle represents the maximum theoretical efficiency achievable for any heat engine operating between two thermal reservoirs."
    }


def analyze_rankine_cycle(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes performance of a basic superheated Rankine Steam Power Cycle.
    Parameters:
    - boiler_pressure_bar: Turbine inlet pressure (bar) [e.g. 30 to 150 bar]
    - turbine_inlet_temp_c: Turbine inlet temperature (°C) [e.g. 350 to 600 °C]
    - condenser_pressure_kpa: Condenser pressure (kPa) [e.g. 5 to 50 kPa]
    - mass_flow_rate_kg_s: Steam mass flow rate (kg/s) [e.g. 10 kg/s]
    - turbine_isentropic_eff: Isentropic efficiency of turbine (0.7 to 1.0)
    - pump_isentropic_eff: Isentropic efficiency of feedwater pump (0.7 to 1.0)
    """
    p_boiler_bar = float(params.get("boiler_pressure_bar", 60.0))
    t_inlet_c = float(params.get("turbine_inlet_temp_c", 500.0))
    p_cond_kpa = float(params.get("condenser_pressure_kpa", 10.0))
    m_dot = float(params.get("mass_flow_rate_kg_s", 15.0))
    eta_turbine = float(params.get("turbine_isentropic_eff", 0.88))
    eta_pump = float(params.get("pump_isentropic_eff", 0.85))

    p_cond_bar = p_cond_kpa / 100.0

    # Thermophysical steam correlations (IAPWS approximation for standard superheated and wet steam region)
    # State 1: Turbine inlet superheated steam
    # h1 approximation (kJ/kg): h0 + cp*(T - Tsat)
    # At standard superheat: h1 approx 2700 + 1.9*(T_inlet) - 2.5*P_boiler + 400
    # Let's use standard thermodynamic formulation:
    t_sat_boiler = 100.0 * (p_boiler_bar ** 0.25)  # approx saturation temp
    h1 = 2800.0 + 2.05 * (t_inlet_c - 250.0) - 1.2 * p_boiler_bar
    s1 = 6.65 + 0.0025 * (t_inlet_c - 300.0) - 0.38 * math.log(max(1.0, p_boiler_bar / 10.0))

    # State 3: Saturated liquid leaving condenser at P_cond
    # h3 = hf at P_cond (approx 4.184 * Tsat_cond)
    # Tsat at 10 kPa is ~45.8 °C -> h3 approx 191.8 kJ/kg
    t_sat_cond = 45.0 + 12.0 * math.log(max(0.1, p_cond_bar / 0.1))
    h3 = 4.184 * t_sat_cond  # kJ/kg
    v3 = 0.00101  # m^3/kg (specific volume of liquid water)
    s3 = 4.184 * math.log((t_sat_cond + 273.15) / 273.15)  # kJ/(kg*K)

    # State 4: Feed pump exit
    # Ideal pump work w_p_ideal = v3 * (P_boiler - P_cond) in kJ/kg
    # v3 in m^3/kg, delta_P in kPa = (P_boiler_bar * 100 - P_cond_kpa)
    delta_p_kpa = (p_boiler_bar * 100.0) - p_cond_kpa
    w_pump_ideal = v3 * delta_p_kpa  # kJ/kg
    w_pump_actual = w_pump_ideal / eta_pump
    h4 = h3 + w_pump_actual

    # State 2: Turbine exhaust at P_cond
    # Saturated liquid and vapor properties at condenser
    # sf approx s3, sfg approx (2400 / (Tsat_cond + 273.15))
    s_f_cond = s3
    h_fg_cond = 2400.0 - 2.4 * t_sat_cond
    s_fg_cond = h_fg_cond / (t_sat_cond + 273.15)
    s_g_cond = s_f_cond + s_fg_cond

    # Isentropic expansion: s2s = s1
    # Vapor quality x2s
    x2s = min(1.0, max(0.6, (s1 - s_f_cond) / s_fg_cond))
    h2s = h3 + x2s * h_fg_cond

    # Ideal turbine work
    w_turb_ideal = max(100.0, h1 - h2s)
    # Actual turbine work
    w_turb_actual = w_turb_ideal * eta_turbine
    h2 = h1 - w_turb_actual
    x2_actual = min(1.0, max(0.5, (h2 - h3) / h_fg_cond))

    # Net specific work & Heat inputs
    w_net = w_turb_actual - w_pump_actual  # kJ/kg
    q_in = h1 - h4  # kJ/kg (Boiler heat input)
    q_out = h2 - h3  # kJ/kg (Condenser heat rejection)

    thermal_eff = (w_net / q_in) if q_in > 0 else 0.0
    thermal_eff_pct = thermal_eff * 100.0

    # Total plant outputs
    power_turbine_mw = (m_dot * w_turb_actual) / 1000.0
    power_pump_mw = (m_dot * w_pump_actual) / 1000.0
    power_net_mw = (m_dot * w_net) / 1000.0
    heat_input_mw = (m_dot * q_in) / 1000.0
    heat_rejected_mw = (m_dot * q_out) / 1000.0

    # Specific Steam Consumption: kg / (kW * h)
    ssc = 3600.0 / w_net if w_net > 0 else 0.0
    back_work_ratio_pct = (w_pump_actual / w_turb_actual) * 100.0 if w_turb_actual > 0 else 0.0

    # Equivalent Carnot efficiency for comparison
    carnot_eff_pct = (1.0 - (t_sat_cond + 273.15) / (t_inlet_c + 273.15)) * 100.0

    return {
        "success": True,
        "cycle_states": {
            "state_1_turbine_inlet": {"h_kj_kg": round(h1, 1), "s_kj_kg_k": round(s1, 3), "p_bar": p_boiler_bar, "t_c": t_inlet_c},
            "state_2_turbine_exit": {"h_kj_kg": round(h2, 1), "steam_quality_x": round(x2_actual, 3), "p_kpa": p_cond_kpa},
            "state_3_condenser_exit": {"h_kj_kg": round(h3, 1), "t_sat_c": round(t_sat_cond, 1), "p_kpa": p_cond_kpa},
            "state_4_boiler_inlet": {"h_kj_kg": round(h4, 1), "p_bar": p_boiler_bar}
        },
        "specific_energy_kj_kg": {
            "turbine_work_w_t": round(w_turb_actual, 2),
            "pump_work_w_p": round(w_pump_actual, 2),
            "net_work_w_net": round(w_net, 2),
            "boiler_heat_q_in": round(q_in, 2),
            "condenser_heat_q_out": round(q_out, 2)
        },
        "power_plant_totals": {
            "mass_flow_rate_kg_s": round(m_dot, 2),
            "net_power_output_mw": round(power_net_mw, 3),
            "boiler_heat_input_mw": round(heat_input_mw, 3),
            "condenser_cooling_mw": round(heat_rejected_mw, 3)
        },
        "performance_metrics": {
            "thermal_efficiency_percent": round(thermal_eff_pct, 2),
            "equivalent_carnot_eff_percent": round(carnot_eff_pct, 2),
            "specific_steam_consumption_kg_kwh": round(ssc, 3),
            "back_work_ratio_percent": round(back_work_ratio_pct, 2),
            "steam_exhaust_quality": round(x2_actual, 3)
        }
    }


def analyze_heat_exchanger(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes Log Mean Temperature Difference (LMTD) and heat transfer rate.
    Parameters:
    - flow_arrangement: 'counter_flow' or 'parallel_flow'
    - t_hot_in: Hot fluid inlet temperature (°C)
    - t_hot_out: Hot fluid outlet temperature (°C)
    - t_cold_in: Cold fluid inlet temperature (°C)
    - t_cold_out: Cold fluid outlet temperature (°C)
    - overall_u_w_m2k: Overall heat transfer coefficient U (W/m^2*K)
    - area_m2: Heat exchange area (m^2)
    """
    flow = params.get("flow_arrangement", "counter_flow").lower()
    th_in = float(params.get("t_hot_in", 95.0))
    th_out = float(params.get("t_hot_out", 65.0))
    tc_in = float(params.get("t_cold_in", 20.0))
    tc_out = float(params.get("t_cold_out", 45.0))
    u_coeff = float(params.get("overall_u_w_m2k", 800.0))
    area = float(params.get("area_m2", 12.0))

    if flow == "counter_flow":
        # Delta T1 at one end, Delta T2 at other end
        dt1 = th_in - tc_out
        dt2 = th_out - tc_in
    else:
        # Parallel flow
        dt1 = th_in - tc_in
        dt2 = th_out - tc_out

    if dt1 <= 0 or dt2 <= 0:
        raise ValueError("Temperature cross or pinch violation: temperature differences at both ends must be positive.")

    # LMTD = (dt1 - dt2) / ln(dt1 / dt2)
    if abs(dt1 - dt2) < 1e-4:
        lmtd = dt1
    else:
        lmtd = (dt1 - dt2) / math.log(dt1 / dt2)

    # Heat transfer rate Q = U * A * LMTD (W -> kW)
    heat_rate_w = u_coeff * area * lmtd
    heat_rate_kw = heat_rate_w / 1000.0

    return {
        "success": True,
        "flow_arrangement": flow,
        "delta_t1_c": round(dt1, 2),
        "delta_t2_c": round(dt2, 2),
        "lmtd_c": round(lmtd, 2),
        "overall_u_w_m2k": u_coeff,
        "heat_exchange_area_m2": area,
        "heat_duty_kw": round(heat_rate_kw, 2)
    }

