import unittest

from calculations.minimal_3rps_100mm_screen import (
    ACTUATOR_STROKE_MM,
    ANGLE_TARGET_DEG,
    LIFT_TARGET_MM,
    workspace_screen,
)


class MinimalThreeRps100mmScreenTests(unittest.TestCase):
    def test_user_selected_motion_target(self):
        self.assertEqual(ACTUATOR_STROKE_MM, 100.0)
        self.assertEqual(LIFT_TARGET_MM, 50.0)
        self.assertEqual(ANGLE_TARGET_DEG, 3.0)

    def test_full_pose_grid_fits_the_100mm_actuator(self):
        result = workspace_screen()
        self.assertEqual(result["pose_count"], 27)
        self.assertTrue(result["passes_stroke"])
        self.assertLess(result["required_span_mm"], ACTUATOR_STROKE_MM)

    def test_both_end_margins_exceed_seven_mm(self):
        result = workspace_screen()
        self.assertGreater(result["retract_margin_mm"], 7.0)
        self.assertGreater(result["extend_margin_mm"], 7.0)

    def test_expected_length_envelope(self):
        result = workspace_screen()
        self.assertAlmostEqual(result["required_min_length_mm"], 212.137, places=3)
        self.assertAlmostEqual(result["required_max_length_mm"], 297.864, places=3)


if __name__ == "__main__":
    unittest.main()
