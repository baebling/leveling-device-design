import unittest

from calculations.yaw_a_gimbal_kinematic_screen import (
    OPERATING_AXIS_ANGLE_DEG,
    STOP_AXIS_LIMIT_DEG,
    operating_envelope_screen,
    platform_rotation,
    stop_envelope_screen,
    total_tilt_deg,
    yaw_constraint_screen,
    zyx_heading_yaw_deg,
)


class YawAGimbalKinematicScreenTests(unittest.TestCase):
    def test_selected_axis_order_keeps_world_heading_zero(self):
        for pitch_deg in (-3.0, 0.0, 3.0):
            for roll_deg in (-3.0, 0.0, 3.0):
                self.assertAlmostEqual(
                    zyx_heading_yaw_deg(platform_rotation(pitch_deg, roll_deg)),
                    0.0,
                    places=9,
                )

    def test_operating_envelope_has_no_independent_yaw_heading(self):
        rows = operating_envelope_screen()
        self.assertEqual(len(rows), 9)
        self.assertTrue(all(row["heading_is_mechanically_constrained"] for row in rows))
        diagonal = yaw_constraint_screen(OPERATING_AXIS_ANGLE_DEG, OPERATING_AXIS_ANGLE_DEG)
        self.assertGreater(diagonal["yaw_lock_projection"], 0.99)
        self.assertLess(diagonal["coupled_pitch_roll_moment_nm"], 1.0)

    def test_stop_is_limited_as_a_total_tilt_envelope(self):
        result = stop_envelope_screen()
        self.assertTrue(result["operating_clearance_passes"])
        self.assertTrue(result["stop_envelope_passes"])
        self.assertEqual(result["selected_independent_pin_stop_deg"], 7.0)
        self.assertLess(result["maximum_diagonal_total_tilt_at_pin_stops_deg"], 10.0)
        self.assertGreater(total_tilt_deg(STOP_AXIS_LIMIT_DEG, STOP_AXIS_LIMIT_DEG), 9.0)


if __name__ == "__main__":
    unittest.main()
