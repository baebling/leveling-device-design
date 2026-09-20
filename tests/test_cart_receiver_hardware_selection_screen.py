import unittest

from calculations.cart_receiver_hardware_selection_screen import (
    backing_plate_policy,
    implementation_open_items,
    locator_bushing_screen,
    optional_alignment_dowel_screen,
    recommended_hardware_seed,
    replaceable_stop_block_screen,
    rest_pad_hardware_screen,
    summary,
)


class CartReceiverHardwareSelectionScreenTests(unittest.TestCase):
    def test_master_and_secondary_locator_keep_h3_axis_roles(self):
        result = recommended_hardware_seed()
        self.assertEqual(result["master_locator"]["constraint"], "fixed X/Y")
        self.assertEqual(result["secondary_locator"]["constraint"], "fixed Y; released X")
        self.assertIn("Do not use a second round X/Y pin", result["secondary_locator"]["prohibition"])

    def test_hardware_seed_preserves_serviceable_replacement_path(self):
        result = recommended_hardware_seed()
        self.assertIn("removable", result["master_locator"]["hardware"])
        self.assertIn("replaceable", result["rest_pad"]["hardware"])
        self.assertIn("separate mechanical secondary lock", result["latch_keeper"]["hardware"])

    def test_master_locator_bushing_passes_local_placeholder_screen(self):
        result = locator_bushing_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertEqual(result["local_uncertainty_factor"], 3.0)
        self.assertLess(result["bearing_mpa"], 10.0)

    def test_replaceable_stop_block_passes_local_placeholder_screen(self):
        result = replaceable_stop_block_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertEqual(result["stop_thickness_mm"], 8.0)
        self.assertLess(result["bending_mpa"], 40.0)

    def test_optional_dowel_is_screened_but_not_the_default_alignment_method(self):
        result = optional_alignment_dowel_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertIn("only after", result["use_policy"])
        self.assertIn("second round X/Y locator", result["use_policy"])

    def test_rest_pad_is_z_only_and_passes_local_contact_screen(self):
        result = rest_pad_hardware_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertIn("Z seating only", result["load_path_rule"])
        self.assertIn("not primary X/Y shear", result["load_path_rule"])

    def test_backing_plate_is_evidence_triggered(self):
        self.assertFalse(backing_plate_policy()["add_backing_plate"])
        self.assertTrue(backing_plate_policy(mockup_shift_mm=0.21)["add_backing_plate"])
        self.assertTrue(backing_plate_policy(torque_relaxation_fraction=0.21)["add_backing_plate"])
        self.assertTrue(backing_plate_policy(profile_wall_marked=True)["add_backing_plate"])

    def test_summary_preserves_phase_gate_and_open_items(self):
        result = summary()
        self.assertEqual(result["phase_gate"], "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION")
        self.assertEqual(result["recommended_hardware_seed"]["code"], "CR-01-H4-S1")
        self.assertGreaterEqual(len(implementation_open_items()), 5)


if __name__ == "__main__":
    unittest.main()
