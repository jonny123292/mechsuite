"""
Integration and End-to-End API tests for MechSuite
"""

import unittest
import json
from app import app


class TestMechSuiteAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_frontend_index(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"MechSuite", res.data)
        self.assertIn(b"Beam Mechanics", res.data)

    def test_frontend_static_assets(self):
        css_res = self.client.get("/css/style.css")
        self.assertEqual(css_res.status_code, 200)
        js_res = self.client.get("/javascript/app.js")
        self.assertEqual(js_res.status_code, 200)

    def test_api_materials(self):
        res = self.client.get("/api/materials")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("steel_a36", data["materials"])

    def test_api_beam_analyze(self):
        payload = {
            "beam_type": "simply_supported",
            "length_m": 5.0,
            "material": "steel_a36",
            "section": {"type": "rectangular", "width": 50, "height": 100},
            "point_loads": [{"position_m": 2.5, "magnitude_kn": 10.0}],
            "udl_loads": []
        }
        res = self.client.post("/api/beam/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("diagrams", data)
        self.assertEqual(len(data["diagrams"]["shear_force_kn"]), 251)

    def test_api_fluids(self):
        payload = {
            "diameter_mm": 50.0,
            "length_m": 100.0,
            "flow_rate_m3_h": 15.0,
            "fluid": "water_20c",
            "pipe_material": "commercial_steel"
        }
        res = self.client.post("/api/fluids/pipe-flow", json=payload)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("flow_results", data)
        self.assertEqual(data["flow_results"]["flow_regime"], "Turbulent")

    def test_api_thermo_carnot(self):
        payload = {"th_celsius": 600.0, "tl_celsius": 25.0, "heat_input_kw": 500.0}
        res = self.client.post("/api/thermo/carnot", json=payload)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertGreater(data["performance"]["carnot_efficiency_percent"], 60.0)

    def test_api_thermo_rankine(self):
        payload = {
            "boiler_pressure_bar": 50.0,
            "turbine_inlet_temp_c": 450.0,
            "condenser_pressure_kpa": 10.0,
            "mass_flow_rate_kg_s": 12.0
        }
        res = self.client.post("/api/thermo/rankine", json=payload)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertGreater(data["power_plant_totals"]["net_power_output_mw"], 0.0)


if __name__ == "__main__":
    unittest.main()

