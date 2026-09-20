import unittest

from calculations.actuator_bracket_package_screen import (
    bracket_topology_candidates,
    centered_double_shear_screen,
    hrt8e_bracket_clearance_screen,
    hrt8e_articulation_screen,
    hrt8e_axial_capacity_screen,
    mockup_acceptance_rules,
    recommended_bracket_seed,
    summary,
)


class ActuatorBracketPackageScreenTests(unittest.TestCase):
    def test_articulation_is_limited_but_passes_active_plus_minus_3_case(self):
        result = hrt8e_articulation_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertGreater(result["required_articulation_deg"], 12.0)
        self.assertLess(result["required_articulation_deg"], 14.0)
        self.assertGreater(result["residual_angle_margin_deg"], 1.0)

    def test_axial_capacity_uses_axial_not_radial_catalog_value(self):
        result = hrt8e_axial_capacity_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertEqual(result["catalog_axial_static_limit_n"], 5290.0)
        self.assertEqual(result["catalog_radial_static_limit_n"], 26770.0)
        self.assertGreater(result["axial_static_margin"], 2.5)

    def test_centered_double_shear_seed_passes(self):
        result = centered_double_shear_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertEqual(result["supported_pin_span_mm"], 18.0)
        self.assertLess(result["pin_bending_mpa"], 100.0)
        self.assertLess(result["lug_root_bending_mpa"], 50.0)

    def test_excessive_pin_span_requires_redesign_or_recalculation(self):
        result = centered_double_shear_screen(supported_pin_span_mm=32.0)
        self.assertFalse(result["passes_placeholder_screen"])
        self.assertFalse(result["supported_pin_span_ok"])

    def test_official_eye_envelope_clears_revised_eighteen_mm_gap(self):
        result = hrt8e_bracket_clearance_screen()
        self.assertTrue(result["passes_placeholder_screen"])
        self.assertEqual(result["body_diameter_mm"], 23.0)
        self.assertEqual(result["eye_width_mm"], 11.0)
        self.assertGreater(result["total_clearance_mm"], 1.0)
        self.assertLess(result["total_clearance_mm"], 2.0)

    def test_topology_rejects_single_shear_and_threaded_standoff(self):
        rows = {row["code"]: row for row in bracket_topology_candidates()}
        self.assertEqual(rows["JNT-BR-01-A"]["selection_status"], "reject")
        self.assertEqual(rows["JNT-BR-01-B"]["selection_status"], "reject")
        self.assertEqual(rows["JNT-BR-01-HRT8E"]["selection_status"], "preferred_hardware_seed")

    def test_seed_keeps_force_and_pin_centered_at_ball_center(self):
        result = recommended_bracket_seed()
        self.assertIn("intersect at J", result["load_path"])
        self.assertIn("no intentional threaded-shank standoff", result["load_path"])
        self.assertIn("full 14 deg", result["articulation_rule"])

    def test_mockup_rules_require_catalog_geometry_confirmation(self):
        result = mockup_acceptance_rules()
        self.assertEqual(result["go_no_go_articulation_deg"], 14.0)
        self.assertIn("eye bore", result["confirm_on_manufacturer_drawing"])
        self.assertIn("threaded shank acts as a bending spacer", result["reject_if"])

    def test_summary_preserves_phase_gate(self):
        result = summary()
        self.assertEqual(result["phase_gate"], "PHASE_2_DETAILED_CAD_APPROVED_NOT_FOR_FABRICATION")
        self.assertEqual(result["recommended_bracket_seed"]["code"], "JNT-BR-01-HRT8E")


if __name__ == "__main__":
    unittest.main()
