import unittest

from calculations.cart_receiver_connector_detail_screen import (
    hardpoint_stack_candidates,
    mockup_acceptance_rules,
    profile_wall_bearing_screen,
    recommended_detail_set,
    service_access_screen,
    slot_nut_clamp_bearing_screen,
    summary,
)


class CartReceiverConnectorDetailScreenTests(unittest.TestCase):
    def test_master_locator_is_fixed_and_secondary_releases_x(self):
        rows = {row["hardpoint"]: row for row in hardpoint_stack_candidates()}
        self.assertEqual(rows["master_locator"]["constrained_axes"], ("X", "Y"))
        self.assertEqual(rows["slotted_secondary_locator"]["constrained_axes"], ("Y",))
        self.assertIn("X", rows["slotted_secondary_locator"]["released_axes"])
        self.assertIn("overconstraining", rows["slotted_secondary_locator"]["primary_role"])

    def test_rest_pad_and_latch_are_not_hidden_shear_paths(self):
        rows = {row["hardpoint"]: row for row in hardpoint_stack_candidates()}
        self.assertIn("Z", rows["rest_pad"]["constrained_axes"])
        self.assertIn("X", rows["rest_pad"]["released_axes"])
        self.assertIn("primary horizontal shear", rows["latch_keeper"]["released_axes"])

    def test_profile_wall_bearing_screen_has_margin_but_is_not_approval(self):
        result = profile_wall_bearing_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertLess(result["bearing_mpa"], 2.0)
        self.assertEqual(result["load_factor"], 3.0)

    def test_slot_nut_clamp_screen_keeps_backing_plate_conditional(self):
        result = slot_nut_clamp_bearing_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertTrue(result["backing_plate_still_conditional"])
        self.assertLess(result["clamp_contact_pressure_mpa"], 25.0)

    def test_mockup_rules_trigger_backing_plate_and_reject_overconstraint(self):
        result = mockup_acceptance_rules()
        self.assertEqual(result["cycles"], 30)
        self.assertLessEqual(result["max_measured_hardpoint_shift_mm"], 0.2)
        self.assertIn("add_backing_plate_if", result)
        self.assertIn("secondary locator blocks both X and Y", result["reject_if"])

    def test_service_access_reserves_sensor_space(self):
        result = service_access_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertTrue(result["latch_closed_sensor_required"])
        self.assertTrue(result["cart_present_sensor_required"])
        self.assertTrue(result["keep_sensor_separate_from_mechanical_stop"])

    def test_recommended_detail_set_preserves_phase_gate(self):
        result = recommended_detail_set()
        self.assertEqual(result["code"], "CR-01-H3")
        self.assertEqual(result["fabrication_status"], "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION")
        self.assertIn("Y only", result["secondary_locator"])

    def test_summary_preserves_phase_gate(self):
        result = summary()
        self.assertEqual(result["phase_gate"], "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION")
        self.assertEqual(result["recommended_detail_set"]["code"], "CR-01-H3")


if __name__ == "__main__":
    unittest.main()
