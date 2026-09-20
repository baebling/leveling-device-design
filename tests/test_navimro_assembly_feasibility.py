import unittest

from calculations.navimro_assembly_feasibility import (
    actuator_nonframe_collisions,
    audit_summary,
    bore_interference_results,
    cart_reference_check,
    guide_motion_collisions,
    module_envelope,
    neutral_connectivity,
    stop_clearances,
)
from cad.navimro_fabrication_parameters import N


class NavimroAssemblyFeasibilityTests(unittest.TestCase):
    def test_confirmed_actuator_stroke_is_used(self):
        self.assertEqual(N.actuator_vendor_stroke_mm, 150.0)
        self.assertEqual(
            N.actuator_max_pin_length_mm - N.actuator_min_pin_length_mm,
            150.0,
        )

    def test_guide_moves_through_full_stroke_without_fixed_structure_collision(self):
        self.assertEqual(guide_motion_collisions(), [])

    def test_actuator_envelopes_clear_central_guide_and_cardan(self):
        self.assertEqual(actuator_nonframe_collisions(), [])

    def test_shafts_pins_and_screws_pass_modeled_bores(self):
        self.assertEqual(bore_interference_results(), [])

    def test_cardan_and_carriage_have_real_attachment_contacts(self):
        values = neutral_connectivity()
        self.assertAlmostEqual(values["lower_bridge_to_carriage_mm"], 0.0, places=3)
        self.assertAlmostEqual(values["upper_bridge_to_rail_a_mm"], 0.0, places=3)
        self.assertAlmostEqual(values["upper_bridge_to_rail_b_mm"], 0.0, places=3)
        self.assertGreaterEqual(values["upper_center_rail_separation_mm"], 50.0)
        self.assertGreater(values["cardan_pin_separation_mm"], 1.0)

    def test_cart_group_is_static_separated_reference_only(self):
        values = cart_reference_check()
        self.assertTrue(values["static_reference"])
        self.assertGreater(values["collapsed_vertical_gap_mm"], 0.0)
        self.assertGreater(values["raised_vertical_gap_mm"], 0.0)

    def test_mechanical_z_stops_remain_outside_commanded_travel(self):
        values = stop_clearances()
        for pose_name in ("collapsed", "raised"):
            for value in values[pose_name]:
                self.assertGreaterEqual(value, 1.5)
                self.assertLessEqual(value, 3.0)

    def test_rev_e_audit_passes_and_keeps_cart_gate_explicit(self):
        result = audit_summary()
        self.assertTrue(result["digital_assembly_pass"])
        self.assertIn("PROVISIONAL", result["cart_coupling_status"])

    def test_disconnected_module_stays_within_height_target(self):
        envelope = module_envelope("collapsed")
        self.assertLessEqual(envelope["z_mm"], 300.0)
        self.assertGreaterEqual(envelope["z_mm"], 250.0)


if __name__ == "__main__":
    unittest.main()
