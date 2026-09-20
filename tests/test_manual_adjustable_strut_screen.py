import unittest

from calculations.manual_adjustable_strut_screen import (
    ANGLE_TARGET_DEG,
    LIFT_TARGET_MM,
    MANUAL_STRUT_MAX_PIN_LENGTH_MM,
    MANUAL_STRUT_MIN_PIN_LENGTH_MM,
    manual_workspace_screen,
    tilt_only_screen,
)


class ManualAdjustableStrutScreenTests(unittest.TestCase):
    def test_active_manual_targets(self):
        self.assertEqual(LIFT_TARGET_MM, 50.0)
        self.assertEqual(ANGLE_TARGET_DEG, 3.0)
        self.assertEqual(MANUAL_STRUT_MIN_PIN_LENGTH_MM, 205.0)
        self.assertEqual(MANUAL_STRUT_MAX_PIN_LENGTH_MM, 305.0)

    def test_full_manual_workspace_fits_preliminary_envelope(self):
        result = manual_workspace_screen()
        self.assertEqual(result["pose_count"], 27)
        self.assertTrue(result["fits_preliminary_strut_envelope"])
        self.assertAlmostEqual(result["required_min_pin_length_mm"], 212.137, places=3)
        self.assertAlmostEqual(result["required_max_pin_length_mm"], 297.864, places=3)
        self.assertGreater(result["minimum_end_margin_mm"], 7.0)
        self.assertGreater(result["maximum_end_margin_mm"], 7.0)

    def test_tilt_only_variant_needs_less_than_36mm_adjustment(self):
        result = tilt_only_screen()
        self.assertEqual(result["pose_count"], 9)
        self.assertTrue(result["fits_preliminary_strut_envelope"])
        self.assertAlmostEqual(result["required_min_pin_length_mm"], 212.137, places=3)
        self.assertAlmostEqual(result["required_max_pin_length_mm"], 247.865, places=3)
        self.assertLess(result["required_adjustment_mm"], 36.0)


if __name__ == "__main__":
    unittest.main()
