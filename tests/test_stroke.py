import unittest

from calculations.kinematics import summary


class StrokeTests(unittest.TestCase):
    def test_three_degree_envelope_passes(self):
        result = summary(3.0)
        self.assertTrue(result["passes_commercial_actuator"])
        self.assertGreaterEqual(result["retracted_margin_mm"], 5.0)
        self.assertGreaterEqual(result["extended_margin_mm"], 5.0)

    def test_five_degree_sensitivity_passes_but_eight_fails(self):
        self.assertTrue(summary(5.0)["passes_commercial_actuator"])
        self.assertFalse(summary(8.0)["passes_commercial_actuator"])


if __name__ == "__main__":
    unittest.main()
