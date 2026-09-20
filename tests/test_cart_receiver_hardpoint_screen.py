import unittest

from calculations.cart_receiver_hardpoint_screen import (
    insert_plate_bending_screen,
    latch_keeper_screen,
    locator_insert_screen,
    profile_fastener_slip_screen,
    recommended_hardpoint_set,
    rest_pad_insert_screen,
)


class CartReceiverHardpointScreenTests(unittest.TestCase):
    def test_locator_insert_load_is_low_for_twelve_mm_pin_seed(self):
        result = locator_insert_screen()
        self.assertEqual(result["pin_diameter_mm"], 12.0)
        self.assertEqual(result["insert_thickness_mm"], 8.0)
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertLess(result["bearing_mpa"], 3.0)

    def test_rest_pad_contact_is_not_bulk_strength_limited(self):
        result = rest_pad_insert_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertLess(result["contact_pressure_mpa"], 1.0)
        self.assertTrue(result["shim_adjustment_required"])

    def test_latch_keeper_remains_retention_not_shear_path(self):
        four_latch = latch_keeper_screen(latch_count=4)
        two_latch = latch_keeper_screen(latch_count=2)
        self.assertFalse(four_latch["latch_is_primary_shear_path"])
        self.assertTrue(four_latch["secondary_lock_required"])
        self.assertGreater(two_latch["per_latch_uplift_n"], four_latch["per_latch_uplift_n"])
        self.assertTrue(two_latch["passes_placeholder_screen"])

    def test_profile_fastener_slip_screen_passes_but_requires_positive_stop(self):
        result = profile_fastener_slip_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertGreater(result["slip_margin"], 5.0)
        self.assertIn("positive stop", result["anti_slip_note"])

    def test_local_plate_bending_screen_is_not_primary_blocker(self):
        result = insert_plate_bending_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertLess(result["bending_mpa"], 20.0)

    def test_recommended_set_preserves_phase_gate(self):
        result = recommended_hardpoint_set()
        self.assertEqual(result["fabrication_status"], "PHASE_1_PRELIMINARY_NOT_FOR_FABRICATION")
        self.assertIn("dowel", result["anti_slip"])


if __name__ == "__main__":
    unittest.main()
