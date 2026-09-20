import unittest

from calculations.central_yaw_path_comparison import (
    comparison_rows,
    conservative_required_central_path_case,
    required_central_path_case,
)


class CentralYawPathComparisonTests(unittest.TestCase):
    def test_required_case_matches_user_confirmed_low_load_screen(self):
        case = required_central_path_case()
        self.assertLess(case["operating_yaw_torque_nm"], 12.0)
        self.assertLess(case["peak_or_design_yaw_torque_nm"], 20.0)
        self.assertGreater(case["required_articulation_angle_deg"], 6.0)
        self.assertLess(case["required_articulation_angle_deg"], 7.0)

    def test_conservative_case_is_archived_sensitivity(self):
        case = conservative_required_central_path_case()
        self.assertGreater(case["operating_yaw_torque_nm"], 120.0)
        self.assertGreater(case["peak_or_design_yaw_torque_nm"], 240.0)
        self.assertIn("archived conservative", case["case_basis"])

    def test_yaw_path_ranking_and_results(self):
        rows = {row["concept_id"]: row for row in comparison_rows()}
        self.assertEqual(rows["YAW-A"]["phase0_rank"], 1)
        self.assertEqual(rows["YAW-D"]["phase0_rank"], 2)
        self.assertEqual(rows["YAW-C"]["phase0_rank"], 3)
        self.assertEqual(rows["YAW-B"]["phase0_rank"], 4)
        self.assertEqual(rows["YAW-A"]["load_screen_result"], "PASS_PRELIM")
        self.assertEqual(rows["YAW-B"]["load_screen_result"], "PASS_TORQUE_ANGLE")
        self.assertEqual(rows["YAW-C"]["load_screen_result"], "PASS_TORQUE_ONLY")
        self.assertEqual(rows["YAW-D"]["load_screen_result"], "PASS_LOAD_ONLY")

    def test_yaw_a_contact_and_torsion_are_plausible_not_final(self):
        yaw_a = {row["concept_id"]: row for row in comparison_rows()}["YAW-A"]
        self.assertLess(yaw_a["peak_tube_shear_mpa"], 25.0)
        self.assertLess(yaw_a["peak_estimated_twist_deg"], 0.5)
        self.assertLess(yaw_a["key_contact_pressure_mpa"], 10.0)
        self.assertGreater(yaw_a["key_couple_force_n"], 300.0)
        self.assertLess(yaw_a["key_couple_force_n"], 350.0)


if __name__ == "__main__":
    unittest.main()
