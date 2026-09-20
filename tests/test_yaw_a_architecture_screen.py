import unittest

from calculations.yaw_a_architecture_screen import (
    anti_yaw_contact_screen,
    backlash_screen,
    candidate_parameter_summary,
    constraint_rank_summary,
    gimbal_angle_screen,
    yoke_pin_screen,
)


class YawAArchitectureScreenTests(unittest.TestCase):
    def test_constraint_rank_keeps_required_dof(self):
        rows = constraint_rank_summary()
        yaw_a = rows["YAW_A_keyed_slide_with_two_axis_gimbal"]
        self.assertEqual(yaw_a["constraint_rank"], 3)
        self.assertEqual(yaw_a["passive_platform_dof"], 3)
        self.assertEqual(yaw_a["screen_result"], "PASS_MOBILITY")
        self.assertEqual(rows["rigid_keyed_slide_without_gimbal"]["screen_result"], "FAIL_BINDS_PITCH_ROLL")
        self.assertEqual(rows["loose_spherical_joint_without_yaw_lock"]["screen_result"], "FAIL_YAW_UNCONSTRAINED")

    def test_gimbal_angle_candidates_cover_user_confirmed_baseline(self):
        rows = {row["pitch_roll_case_deg"]: row for row in gimbal_angle_screen()}
        self.assertTrue(rows[3.0]["passes_design_angle"])
        self.assertFalse(rows[5.0]["passes_design_angle"])
        self.assertTrue(rows[5.0]["passes_hard_stop_angle"])
        self.assertFalse(rows[8.0]["passes_design_angle"])
        self.assertFalse(rows[8.0]["passes_hard_stop_angle"])

    def test_backlash_contact_and_pin_candidates(self):
        clearances = {row["total_clearance_mm"]: row for row in backlash_screen()}
        self.assertTrue(clearances[0.2]["meets_preferred_target"])
        self.assertTrue(clearances[0.3]["meets_maximum_limit"])
        self.assertFalse(clearances[0.5]["meets_maximum_limit"])

        contact = anti_yaw_contact_screen()
        self.assertLess(contact["contact_pressure_mpa"], 10.0)
        self.assertGreater(contact["couple_force_n"], 300.0)
        self.assertLess(contact["couple_force_n"], 350.0)

        pin = yoke_pin_screen()
        self.assertTrue(pin["pin_shear_ok"])
        self.assertTrue(pin["lug_bearing_ok"])

    def test_candidate_parameter_summary(self):
        params = candidate_parameter_summary()
        self.assertEqual(params["gimbal_design_angle_deg"], 8.0)
        self.assertEqual(params["gimbal_hard_stop_angle_deg"], 10.0)
        self.assertLessEqual(params["estimated_target_yaw_freeplay_deg"], 0.25)
        self.assertLessEqual(params["estimated_max_yaw_freeplay_deg"], 0.5)


if __name__ == "__main__":
    unittest.main()
