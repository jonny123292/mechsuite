"""
Unit tests for Thermodynamics module
"""

import unittest
from engine.thermodynamics import analyze_carnot_cycle, analyze_rankine_cycle, analyze_heat_exchanger


class TestThermodynamics(unittest.TestCase):

    def test_carnot_cycle(self):
        params = {"th_celsius": 500.0, "tl_celsius": 30.0, "heat_input_kw": 1000.0}
        res = analyze_carnot_cycle(params)
        self.assertTrue(res["success"])
        # eta = 1 - (303.15 / 773.15) = 60.79%
        perf = res["performance"]
        self.assertAlmostEqual(perf["carnot_efficiency_percent"], 60.79, places=1)
        self.assertAlmostEqual(perf["net_power_output_kw"], 607.9, delta=5.0)

    def test_carnot_invalid_temperatures(self):
        with self.assertRaises(ValueError):
            analyze_carnot_cycle({"th_celsius": 50.0, "tl_celsius": 100.0})

    def test_rankine_cycle(self):
        params = {
            "boiler_pressure_bar": 60.0,
            "turbine_inlet_temp_c": 500.0,
            "condenser_pressure_kpa": 10.0,
            "mass_flow_rate_kg_s": 20.0,
            "turbine_isentropic_eff": 0.88,
            "pump_isentropic_eff": 0.85
        }
        res = analyze_rankine_cycle(params)
        self.assertTrue(res["success"])
        metrics = res["performance_metrics"]
        self.assertTrue(25.0 < metrics["thermal_efficiency_percent"] < 48.0)
        self.assertTrue(metrics["thermal_efficiency_percent"] < metrics["equivalent_carnot_eff_percent"])
        self.assertGreater(res["power_plant_totals"]["net_power_output_mw"], 0.0)

    def test_heat_exchanger_counter_flow(self):
        params = {
            "flow_arrangement": "counter_flow",
            "t_hot_in": 95.0,
            "t_hot_out": 65.0,
            "t_cold_in": 20.0,
            "t_cold_out": 45.0,
            "overall_u_w_m2k": 800.0,
            "area_m2": 15.0
        }
        res = analyze_heat_exchanger(params)
        self.assertTrue(res["success"])
        # dt1 = 95 - 45 = 50, dt2 = 65 - 20 = 45
        # LMTD = (50 - 45) / ln(50/45) = 5 / 0.10536 = 47.45
        self.assertAlmostEqual(res["lmtd_c"], 47.45, places=1)
        self.assertGreater(res["heat_duty_kw"], 0.0)


if __name__ == "__main__":
    unittest.main()

