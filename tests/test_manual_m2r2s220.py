import unittest

from calculations.manual_m2r2_slot_layout_optimization import evaluate, pose_command


class ManualM2R2S220Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sweep3 = evaluate(220.0, 3.0)

    def test_three_intended_dof_and_rigid_lock(self):
        self.assertEqual(self.sweep3["minimum_passive_rank"], 3)
        self.assertEqual(self.sweep3["minimum_locked_rank"], 6)
        self.assertTrue(self.sweep3["mobility_pass"])

    def test_plus_minus_three_degree_length_window(self):
        self.assertTrue(self.sweep3["length_window_pass"])
        self.assertGreaterEqual(self.sweep3["minimum_pin_distance_mm"], 260.0)
        self.assertLessEqual(self.sweep3["maximum_pin_distance_mm"], 300.0)
        self.assertGreater(self.sweep3["minimum_length_margin_mm"], 5.4)

    def test_larger_square_workspace_is_not_claimed(self):
        self.assertFalse(evaluate(220.0, 5.0)["length_window_pass"])
        self.assertFalse(evaluate(220.0, 8.0)["length_window_pass"])

    def test_joint_angle_is_below_conservative_iko_limit(self):
        self.assertLess(self.sweep3["maximum_required_phs_angle_deg"], 8.0)

    def test_rear_supports_keep_nominal_clearance(self):
        self.assertAlmostEqual(self.sweep3["rear_pair_shat12_foot_clearance_mm"], 18.0)

    def test_turnbuckle_command_stays_within_screened_range(self):
        row = pose_command(220.0, 3.0, 3.0)
        self.assertLessEqual(max(abs(value) for value in row["turns_from_280mm_neutral"]), 4.17)


if __name__ == "__main__":
    unittest.main()
