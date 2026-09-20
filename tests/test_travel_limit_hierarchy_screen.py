import unittest

from calculations.travel_limit_hierarchy_screen import (
    length_hierarchy,
    preliminary_lift_stop_load_case,
    selected_workspace_limit_check,
)


class TravelLimitHierarchyScreenTests(unittest.TestCase):
    def test_limit_sequence_keeps_switches_and_stops_independent(self):
        result = length_hierarchy()
        hard_lower, hard_upper = result["hard_stop_guarded_range_mm"]
        electrical_lower, electrical_upper = result["electrical_limit_target_range_mm"]
        command_lower, command_upper = result["commanded_soft_range_mm"]
        self.assertLess(hard_lower, electrical_lower)
        self.assertLess(electrical_lower, command_lower)
        self.assertLess(command_upper, electrical_upper)
        self.assertLess(electrical_upper, hard_upper)

    def test_selected_workspace_stays_inside_command_window(self):
        result = selected_workspace_limit_check()
        self.assertEqual(result["workspace_code"], "WS-01-H20")
        self.assertTrue(result["all_grid_points_inside_commanded_soft_range"])
        self.assertIn("independent load-bearing physical contacts", result["hard_stop_implementation_rule"])

    def test_static_stop_reference_is_not_an_impact_claim(self):
        result = preliminary_lift_stop_load_case()
        self.assertGreater(result["design_vertical_load_n"], 800.0)
        self.assertGreater(result["equal_share_reference_n_per_contact"], 400.0)
        self.assertIn("static reference only", result["warning"])


if __name__ == "__main__":
    unittest.main()
