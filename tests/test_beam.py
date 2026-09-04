"""
Unit tests for Beam Analyzer module
"""

import unittest
from engine.beam_analyzer import analyze_beam
from engine.materials import calculate_section_properties


class TestBeamAnalyzer(unittest.TestCase):

    def test_simply_supported_point_load(self):
        # L = 6m, P = 12 kN at midspan (x = 3m)
        params = {
            "beam_type": "simply_supported",
            "length_m": 6.0,
            "material": "steel_a36",
            "section": {"type": "rectangular", "width": 50, "height": 100},
            "point_loads": [{"position_m": 3.0, "magnitude_kn": 12.0}],
            "udl_loads": []
        }
        res = analyze_beam(params)
        self.assertTrue(res["success"])
        reactions = res["reactions"]
        self.assertAlmostEqual(reactions["ra_kn"], 6.0, places=2)
        self.assertAlmostEqual(reactions["rb_kn"], 6.0, places=2)
        crit = res["critical_values"]
        # M_max = P * L / 4 = 12 * 6 / 4 = 18 kN*m
        self.assertAlmostEqual(crit["max_bending_moment_kn_m"], 18.0, delta=0.2)
        self.assertAlmostEqual(crit["max_shear_force_kn"], 6.0, places=2)

    def test_simply_supported_udl(self):
        # L = 4m, UDL = 5 kN/m over entire span
        params = {
            "beam_type": "simply_supported",
            "length_m": 4.0,
            "material": "steel_a36",
            "section": {"type": "rectangular", "width": 50, "height": 100},
            "point_loads": [],
            "udl_loads": [{"start_m": 0.0, "end_m": 4.0, "magnitude_kn_m": 5.0}]
        }
        res = analyze_beam(params)
        self.assertTrue(res["success"])
        reactions = res["reactions"]
        self.assertAlmostEqual(reactions["ra_kn"], 10.0, places=2)
        self.assertAlmostEqual(reactions["rb_kn"], 10.0, places=2)
        # M_max = w * L^2 / 8 = 5 * 16 / 8 = 10 kN*m
        crit = res["critical_values"]
        self.assertAlmostEqual(crit["max_bending_moment_kn_m"], 10.0, delta=0.2)

    def test_cantilever_end_load(self):
        # L = 2m, P = 5 kN at tip
        params = {
            "beam_type": "cantilever",
            "length_m": 2.0,
            "material": "steel_a36",
            "section": {"type": "rectangular", "width": 50, "height": 100},
            "point_loads": [{"position_m": 2.0, "magnitude_kn": 5.0}],
            "udl_loads": []
        }
        res = analyze_beam(params)
        self.assertTrue(res["success"])
        reactions = res["reactions"]
        self.assertAlmostEqual(reactions["ra_kn"], 5.0, places=2)
        self.assertAlmostEqual(reactions["moment_a_kn_m"], 10.0, places=2)
        crit = res["critical_values"]
        self.assertAlmostEqual(crit["max_bending_moment_kn_m"], 10.0, delta=0.2)

    def test_section_properties(self):
        rec = calculate_section_properties("rectangular", {"width": 100, "height": 200})
        # Area = 100 * 200 = 20000 mm^2
        self.assertEqual(rec["area_mm2"], 20000.0)
        # I = 100 * 200^3 / 12 = 66,666,666.67 mm^4
        self.assertAlmostEqual(rec["i_xx_mm4"], 100 * (200 ** 3) / 12, places=1)


if __name__ == "__main__":
    unittest.main()

