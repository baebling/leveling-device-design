import unittest

from calculations.actuator_force import summary as actuator_force_summary
from calculations.interface_loads import acrylic_strip_screening, latch_and_pin_screening


class LoadTests(unittest.TestCase):
    def test_actuator_rating_screening(self):
        result = actuator_force_summary()
        self.assertTrue(result["passes_preliminary_force_check"])
        self.assertEqual(result["maximum_required_tension_n"], 0.0)
        self.assertLess(result["worst_case"]["max_compression_n"], result["selected_dynamic_rating_n"])

    def test_latch_capacity_screening(self):
        self.assertGreater(latch_and_pin_screening()["latch_capacity_ratio"], 2.0)

    def test_acrylic_is_panel_only(self):
        short = acrylic_strip_screening(250, 100, 15, 300)
        long = acrylic_strip_screening(250, 100, 15, 800)
        self.assertTrue(short["passes_stress_only"])
        self.assertFalse(long["passes_stress_only"])
        self.assertGreater(long["deflection_mm"], 20.0)


if __name__ == "__main__":
    unittest.main()
