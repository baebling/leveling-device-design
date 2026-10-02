"""Catch wrong units/signs, false structural approval, and lost evidence gaps."""
from dataclasses import replace
import json
from pathlib import Path
import unittest

from cad.revf_upper_pocket_inputs import load_inputs
from calculations.revf_upper_pocket_load_screen import screen_loads, build_review


class PocketLoadTests(unittest.TestCase):
    def test_hcdgh_pin_requires_guaranteed_strength_not_hardness_conversion(self):
        result=screen_loads(load_inputs(),750)
        self.assertAlmostEqual(result['tolerance_screen']['pin_min_diameter_mm'],5.988)
        self.assertLess(abs(result['pin_bending_mpa']-569.3),1.)
        self.assertLess(abs(result['required_yield_for_bending_sf_mpa']-854.),2.)
        self.assertIsNone(result['conditional_pin_proof_mpa'])
        self.assertEqual(result['tolerance_screen']['known_tolerance_min_gap_mm'],.20)
        self.assertEqual(result['tolerance_screen']['known_tolerance_max_gap_mm'],.82)
        self.assertFalse(result['strength_gate'])
    def test_750n_pin_check_both_directions(self):
        for force_n in (-750.0, 750.0):
            result = screen_loads(load_inputs(), force_n)
            self.assertLess(abs(result["pin_bending_mpa"] - 569.3), 1.0)
            self.assertAlmostEqual(result["signed_moment_nmm"], force_n * 16)
            self.assertAlmostEqual(result["pin_shear_mpa"], 26.632, places=2)
            self.assertIsNone(result["conditional_pin_ratio"])
            self.assertIs(result["strength_gate"], False)
            self.assertIs(result["purchase_release"], False)

    def test_cubic_diameter_and_linear_force_scaling(self):
        result = screen_loads(replace(load_inputs(), pin_dmin_mm=6.0, pin_dmax_mm=6.0), 375)
        self.assertAlmostEqual(result["pin_bending_mpa"], 282.9421, places=3)

    def test_dimension_completeness_cannot_close_strength_gaps(self):
        inputs = replace(load_inputs(), shoulder_contact_length_mm=31,
                         profile_slot_width_mm=6.3, profile_slot_verified=True,
                         unresolved_evidence=(), purchase_release=True)
        result = screen_loads(inputs, 750)
        for key in ("pin_transition", "phs_contact", "m6_reversal", "slot_attachment"):
            self.assertIn(key, result["unverified"])
            self.assertIsNone(result["checks"][key]["capacity"])
        self.assertFalse(result["strength_gate"])
        for key, value in result.items():
            if key.endswith("_release"):
                self.assertIs(value, False)

    def test_adverse_bore_clearances_are_screening_bounds_not_tolerances(self):
        result = screen_loads(load_inputs(), -750)
        screen=result['tolerance_screen']
        self.assertNotIn('diametral_clearance_bounds_mm',screen)
        self.assertEqual(screen['pin_diameter_limits_mm'],[5.988,5.996])
        self.assertIsNone(screen['delivered_eye_bore_tolerance_mm'])
        for row,expected in zip(screen['conditional_clearance_by_eye_source'],([.004,.012],[.404,.412])):
            for actual,wanted in zip(row['diametral_clearance_limits_mm'],expected):
                self.assertAlmostEqual(actual,wanted)
            self.assertFalse(row['delivered_fit_verified'])
        self.assertIsNone(result["tolerance_screen"]["worst_case_effective_offset_mm"])
        self.assertIn("tolerance_stack", result["unverified"])

    def test_all_three_axes_and_eight_sign_combinations_remain_unverified(self):
        report = build_review()
        self.assertEqual({c["force_n"] for c in report["cases"]}, {-750, 750})
        self.assertEqual(len({tuple(c["forces_n"]) for c in report["simultaneous_cases"]}), 8)
        self.assertEqual(set(report["axes"]), {"A1", "A2", "A3"})
        self.assertTrue(all(c["global_equilibrium_verified"] is False
                            for c in report["simultaneous_cases"]))
        self.assertTrue(report["review_only"])

    def test_zero_load_does_not_clear_unknowns(self):
        result = screen_loads(load_inputs(), 0)
        self.assertEqual(result["pin_von_mises_mpa"], 0)
        self.assertIsNone(result["conditional_pin_ratio"])
        self.assertFalse(result["strength_gate"])

    def test_nonfinite_and_invalid_geometry_rejected(self):
        for force in (float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                screen_loads(load_inputs(), force)
        for field, value in (("pin_dmin_mm", 0), ("eye_offset_mm", -1),
                             ("eye_hole_bounds_mm", (6.4, 6.0))):
            with self.assertRaises(ValueError):
                screen_loads(replace(load_inputs(), **{field: value}), 750)

    def test_saved_review_matches_calculation(self):
        path = Path("outputs/profile_radial_revF_upper_pocket_review_2026-10-02/load_screen.json")
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), build_review())


if __name__ == "__main__":
    unittest.main()
