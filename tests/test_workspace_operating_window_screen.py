import unittest

from calculations.workspace_operating_window_screen import summary


class WorkspaceOperatingWindowScreenTests(unittest.TestCase):
    def test_existing_250mm_baseline_is_valid_but_tight(self):
        rows = {row["code"]: row for row in summary()["candidate_rows"]}
        row = rows["WS-01-H0"]
        self.assertTrue(row["full_operating_grid_passes"])
        self.assertLess(row["worst_actuator_row"]["minimum_soft_reserve_mm"], 5.0)
        self.assertEqual(row["cad_readiness_result"], "PASS_BUT_NOT_RECOMMENDED_FOR_CAD_BASELINE")

    def test_270mm_candidate_has_operating_and_overlap_reserve(self):
        row = summary()["recommended_candidate"]
        self.assertEqual(row["code"], "WS-01-H20")
        self.assertTrue(row["full_operating_grid_passes"])
        self.assertGreaterEqual(row["worst_actuator_row"]["minimum_soft_reserve_mm"], 10.0)
        self.assertGreaterEqual(row["worst_guide_row"]["guide_overlap_reserve_mm"], 5.0)
        self.assertEqual(row["cad_readiness_result"], "RECOMMENDED_FOR_PRE_CAD_PARAMETER_REVIEW")


if __name__ == "__main__":
    unittest.main()
