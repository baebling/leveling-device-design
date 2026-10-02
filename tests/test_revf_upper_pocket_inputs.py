"""Source gate regressions: missing evidence must never authorize fabrication."""
from dataclasses import replace
import unittest

from cad.revf_upper_pocket_inputs import load_inputs, source_complete


class PocketSourceTests(unittest.TestCase):
    def test_baseline_preserves_conflicting_bores_and_closed_release(self):
        inputs = load_inputs()
        self.assertEqual(inputs.bracket_count, 3)
        self.assertEqual(inputs.eye_hole_bounds_mm, (6.0, 6.4))
        self.assertEqual(inputs.pin_dmin_mm, 5.988)
        self.assertFalse(inputs.purchase_release)
        self.assertFalse(source_complete(inputs))

    def test_missing_shoulder_contact_cannot_be_promoted_by_other_evidence(self):
        inputs = replace(load_inputs(), profile_slot_width_mm=6.3,
                         profile_slot_verified=True, unresolved_evidence=(),
                         shoulder_contact_length_mm=None)
        self.assertFalse(source_complete(inputs))
        self.assertFalse(inputs.purchase_release)

    def test_complete_source_gate_is_separate_from_purchase_release(self):
        # Synthetic closed evidence fixture, not a supplier dimensional claim.
        inputs = replace(load_inputs(), shoulder_contact_length_mm=30.5,
                         profile_slot_width_mm=6.3,
                         profile_slot_verified=True, unresolved_evidence=())
        self.assertTrue(source_complete(inputs))
        self.assertFalse(inputs.purchase_release)
        for field, value in (("profile_slot_verified", False),
                             ("profile_slot_width_mm", None),
                             ("pin_dmin_mm", float("nan")),
                             ("shoulder_contact_length_mm", 0),
                             ("bracket_count", 4),
                             ("eye_hole_bounds_mm", (6.4, 6.0)),
                             ("unresolved_evidence", ("missing tolerance",))):
            with self.subTest(field=field):
                self.assertFalse(source_complete(replace(inputs, **{field: value})))


if __name__ == "__main__":
    unittest.main()
