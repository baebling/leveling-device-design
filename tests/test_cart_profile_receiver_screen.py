import unittest

from calculations.cart_profile_receiver_screen import (
    candidate_layouts,
    locator_and_latch_screen,
    preferred_receiver_zone,
    rest_pad_reaction_screen,
    summary,
)


class CartProfileReceiverScreenTests(unittest.TestCase):
    def test_preferred_two_rail_layout_preserves_mass_budget(self):
        result = summary()["preferred_layout"]
        self.assertEqual(result["layout"], "two_rail_hfs8_receiver_kit")
        self.assertTrue(result["passes_preferred_mass_budget"])
        self.assertLess(result["total_receiver_mass_kg"], 5.0)
        self.assertLess(result["fraction_of_10kg_cart"], 0.5)

    def test_rectangular_subframe_is_heavier_reserve(self):
        layouts = {row["layout"]: row for row in candidate_layouts()}
        preferred = layouts["two_rail_hfs8_receiver_kit"]
        rectangle = layouts["self_contained_hfs8_rectangular_receiver"]
        self.assertGreater(rectangle["total_receiver_mass_kg"], preferred["total_receiver_mass_kg"])
        self.assertFalse(rectangle["passes_preferred_mass_budget"])
        self.assertTrue(rectangle["passes_max_mass_budget"])

    def test_preferred_zone_fits_inside_device_footprint(self):
        zone = preferred_receiver_zone()
        self.assertLessEqual(zone["receiver_outer_length_mm"], 900.0)
        self.assertLessEqual(zone["receiver_outer_width_mm"], 800.0)
        self.assertEqual(zone["locator_x_span_mm"], 520.0)
        self.assertEqual(zone["latch_placeholder_count"], 4)

    def test_rest_pads_remain_compressive_under_active_worst_case(self):
        result = rest_pad_reaction_screen()
        self.assertTrue(result["all_pads_remain_compressive_in_screen"])
        self.assertGreater(result["min_pad_load_n"], 0.0)
        self.assertLess(result["max_pad_load_n"], 400.0)

    def test_locator_and_latch_loads_are_low_but_latches_not_shear_path(self):
        result = locator_and_latch_screen()
        self.assertFalse(result["latches_are_primary_shear_path"])
        self.assertLess(result["master_locator_single_point_shear_n"], 200.0)
        self.assertLess(result["yaw_couple_force_at_locator_span_n"], 40.0)
        self.assertLess(result["per_latch_uplift_n"], 40.0)


if __name__ == "__main__":
    unittest.main()
