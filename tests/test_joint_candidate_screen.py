import unittest

from calculations.joint_candidate_screen import actuator_joint_screen, central_cardan_screen


class JointCandidateScreenTests(unittest.TestCase):
    def test_actuator_joint_baseline_screen(self):
        rows = {row["candidate"]: row for row in actuator_joint_screen(3.0)}
        self.assertEqual(rows["single_axis_clevis"]["screen_result"], "FAIL")
        self.assertEqual(rows["MISUMI_PHSOSM8"]["screen_result"], "FAIL")
        self.assertEqual(rows["Minebea_HRT8E"]["screen_result"], "PASS")
        self.assertEqual(rows["MISUMI_RBLD8_link_ball_style"]["screen_result"], "PASS")
        self.assertGreater(rows["Minebea_HRT8E"]["required_angle_with_margin_deg"], 12.0)

    def test_actuator_joint_stretch_screen(self):
        rows = {row["candidate"]: row for row in actuator_joint_screen(5.0)}
        self.assertEqual(rows["Minebea_HRT8E"]["screen_result"], "FAIL")
        self.assertEqual(rows["MISUMI_RBLD8_link_ball_style"]["screen_result"], "PASS")
        self.assertEqual(rows["Minebea_HRT8E"]["load_capacity_basis"], "catalog axial static limit")
        self.assertGreater(rows["Minebea_HRT8E"]["static_load_capacity_ratio_to_required_axial"], 2.0)
        self.assertLess(rows["Minebea_HRT8E"]["angle_margin_remaining_deg"], 0.0)

    def test_central_cardan_angle_screen(self):
        five_deg_rows = {row["candidate"]: row for row in central_cardan_screen(5.0)}
        self.assertEqual(five_deg_rows["current_placeholder_design_angle"]["screen_result"], "FAIL")
        self.assertEqual(five_deg_rows["current_placeholder_hard_stop"]["screen_result"], "PASS_ANGLE_ONLY")
        self.assertEqual(five_deg_rows["Ruland_single_u_joint_family"]["screen_result"], "PASS_ANGLE_ONLY")

        eight_deg_rows = {row["candidate"]: row for row in central_cardan_screen(8.0)}
        self.assertEqual(eight_deg_rows["current_placeholder_hard_stop"]["screen_result"], "FAIL")
        self.assertEqual(eight_deg_rows["Ruland_single_u_joint_family"]["screen_result"], "PASS_ANGLE_ONLY")


if __name__ == "__main__":
    unittest.main()
