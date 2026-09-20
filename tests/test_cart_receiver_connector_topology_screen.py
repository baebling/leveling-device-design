import unittest

from calculations.cart_receiver_connector_topology_screen import (
    connector_design_demand,
    connector_topology_candidates,
    dowel_backup_screen,
    recommended_connector_set,
    shoulder_stop_screen,
    summary,
)


class CartReceiverConnectorTopologyScreenTests(unittest.TestCase):
    def test_friction_only_has_numeric_margin_but_is_not_final_locating(self):
        result = connector_design_demand()
        self.assertGreater(result["friction_only_slip_margin"], 5.0)
        self.assertTrue(result["friction_only_passes_strength_screen"])
        self.assertTrue(result["positive_stop_required_for_final_locating"])

    def test_positive_stop_screen_is_low_stress_for_current_demand(self):
        result = shoulder_stop_screen()
        self.assertTrue(result["final_shear_path"])
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertLess(result["bearing_mpa"], 1.0)
        self.assertLess(result["bending_mpa"], 25.0)

    def test_optional_dowel_backup_is_not_current_strength_blocker(self):
        result = dowel_backup_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertLess(result["shear_mpa"], 10.0)
        self.assertLess(result["bearing_mpa"], 5.0)

    def test_preferred_candidate_is_fasteners_plus_positive_stop(self):
        candidates = connector_topology_candidates()
        preferred = [row for row in candidates if row["selection_status"] == "preferred"]
        rejected = [row for row in candidates if row["selection_status"].startswith("reject")]
        self.assertEqual(preferred[0]["code"], "CR-01-H2-B")
        self.assertEqual(rejected[0]["code"], "CR-01-H2-A")
        self.assertFalse(rejected[0]["passes_phase_policy"])

    def test_recommended_connector_set_preserves_phase_gate(self):
        result = recommended_connector_set()
        self.assertEqual(result["code"], "CR-01-H2-B")
        self.assertEqual(result["fabrication_status"], "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION")
        self.assertIn("positive stop", result["final_shear_path"])
        self.assertIn("not an approved", result["reject"])

    def test_summary_preserves_phase_gate(self):
        result = summary()
        self.assertEqual(result["phase_gate"], "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION")
        self.assertEqual(result["recommended_connector_set"]["code"], "CR-01-H2-B")


if __name__ == "__main__":
    unittest.main()
