import unittest

from calculations.manual_turnbuckle_rev_m2_stability import (
    constraint_rank_audit,
    gravity_reaction_audit,
    illustrative_tipover_audit,
    self_standing_audit,
    thread_lock_audit,
)


class ManualTurnbuckleRevM2StabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.constraint = constraint_rank_audit()
        cls.gravity = gravity_reaction_audit()

    def test_three_locked_rps_legs_fully_constrain_platform(self):
        self.assertEqual(self.constraint["pose_count"], 169)
        self.assertEqual(self.constraint["minimum_rank"], 6)
        self.assertGreater(self.constraint["minimum_singular_value"], 0.35)
        self.assertLess(self.constraint["maximum_condition_number"], 5.0)

    def test_incomplete_or_all_spherical_link_sets_do_not_self_stand(self):
        self.assertEqual(self.constraint["neutral_two_rps_leg_rank"], 4)
        self.assertEqual(self.constraint["neutral_three_sps_leg_rank"], 3)

    def test_gravity_reactions_stay_compressive_with_150mm_cg_offset(self):
        self.assertEqual(self.gravity["case_count"], 12168)
        self.assertGreater(self.gravity["minimum_reaction_n"], 0.0)
        self.assertTrue(self.gravity["all_reactions_compressive"])
        self.assertLess(
            self.gravity["cg_offset_radius_mm"],
            self.gravity["minimum_projected_inradius_mm"],
        )

    def test_preliminary_leg_load_remains_below_design_screen(self):
        self.assertLess(
            self.gravity["maximum_equivalent_axial_n"],
            self.gravity["design_leg_load_n"],
        )
        self.assertGreater(self.gravity["axial_load_factor"], 1.9)

    def test_thread_friction_is_not_accepted_as_the_lock(self):
        result = thread_lock_audit()
        self.assertTrue(result["jam_nuts_required"])
        self.assertFalse(result["may_rely_on_thread_friction_alone"])
        self.assertFalse(result["supplier_self_lock_rating_published"])
        self.assertEqual(result["stb_supplied_sjn_lock_nuts_per_leg"], 2)
        self.assertEqual(result["additional_external_jam_nuts_per_leg"], 3)
        self.assertEqual(result["total_lock_nuts_per_leg"], 5)
        self.assertAlmostEqual(result["length_change_per_turn_mm"], 3.5, places=6)

    def test_whole_unit_tipover_remains_open(self):
        result = illustrative_tipover_audit()
        self.assertEqual(result["calculation_status"], "illustrative_not_verified")
        self.assertFalse(result["whole_unit_external_tip_resistance_verified"])

    def test_combined_locked_static_assessment(self):
        result = self_standing_audit()
        self.assertTrue(
            result["fully_assembled_three_leg_platform_self_stands_under_screened_gravity"]
        )
        self.assertFalse(result["central_post_required_after_all_three_links_are_locked"])
        self.assertTrue(result["temporary_support_required_during_assembly_or_loaded_adjustment"])
        self.assertFalse(result["two_leg_incomplete_assembly_self_standing"])


if __name__ == "__main__":
    unittest.main()
