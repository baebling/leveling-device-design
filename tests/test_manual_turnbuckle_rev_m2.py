import unittest

from calculations.manual_turnbuckle_rev_m2_screen import (
    P,
    adjustable_pin_range_mm,
    strength_audit,
    workspace_audit,
)


class ManualTurnbuckleRevM2Tests(unittest.TestCase):
    def test_scope_is_tilt_only(self):
        self.assertEqual(P.angle_deg, 3.0)
        self.assertEqual(P.upper_profile_top_z_mm, 300.0)
        self.assertEqual(P.upper_support_radius_mm, 315.0)

    def test_turnbuckle_workspace_has_thread_margin(self):
        result = workspace_audit()
        self.assertEqual(result["pose_count"], 9)
        self.assertTrue(result["passes"])
        self.assertGreater(result["lower_length_margin_mm"], 2.0)
        self.assertGreater(result["upper_length_margin_mm"], 10.0)
        self.assertGreater(result["minimum_internal_engagement_mm"], 24.0)
        self.assertLess(result["required_adjustment_mm"], 23.0)

    def test_adjustable_range_uses_symmetric_thread_withdrawal(self):
        minimum, maximum = adjustable_pin_range_mm()
        self.assertAlmostEqual(minimum, 260.0, places=6)
        self.assertAlmostEqual(maximum, 300.0, places=6)

    def test_preliminary_strength_screen(self):
        result = strength_audit()
        self.assertTrue(result["passes_preliminary_screen"])
        self.assertGreater(result["buckling_factor"], 15.0)
        self.assertGreater(result["adapter_plate_yield_factor"], 6.0)


if __name__ == "__main__":
    unittest.main()
