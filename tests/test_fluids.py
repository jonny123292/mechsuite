"""
Unit tests for Fluid Mechanics module
"""

import unittest
from engine.fluid_mechanics import analyze_pipe_flow


class TestFluidMechanics(unittest.TestCase):

    def test_laminar_flow(self):
        # High viscosity engine oil in 50mm pipe at low velocity
        params = {
            "diameter_mm": 50.0,
            "length_m": 50.0,
            "flow_velocity_m_s": 0.5,
            "fluid": "engine_oil",
            "pipe_material": "commercial_steel",
            "minor_loss_k": 1.0
        }
        res = analyze_pipe_flow(params)
        self.assertTrue(res["success"])
        flow = res["flow_results"]
        # Re = 880 * 0.5 * 0.05 / 0.290 = 75.86 < 2300
        self.assertEqual(flow["flow_regime"], "Laminar")
        self.assertAlmostEqual(flow["darcy_friction_factor"], 64.0 / flow["reynolds_number"], delta=0.001)
        self.assertGreater(res["head_losses"]["total_head_loss_m"], 0.0)

    def test_turbulent_flow(self):
        # Water in 100mm pipe at 2 m/s
        params = {
            "diameter_mm": 100.0,
            "length_m": 200.0,
            "flow_velocity_m_s": 2.0,
            "fluid": "water_20c",
            "pipe_material": "commercial_steel",
            "minor_loss_k": 2.5
        }
        res = analyze_pipe_flow(params)
        self.assertTrue(res["success"])
        flow = res["flow_results"]
        # Re ~ 998.2 * 2.0 * 0.1 / 1e-3 ~ 200,000 (Turbulent)
        self.assertGreater(flow["reynolds_number"], 4000)
        self.assertEqual(flow["flow_regime"], "Turbulent")
        self.assertTrue(0.01 < flow["darcy_friction_factor"] < 0.05)
        self.assertGreater(res["pressure_drop"]["pressure_drop_kpa"], 0.0)
        self.assertGreater(res["power_requirements"]["pump_shaft_power_kw"], 0.0)


if __name__ == "__main__":
    unittest.main()
