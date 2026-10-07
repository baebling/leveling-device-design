"""User-visible regression checks for the October 7 purchase correction.

These fail if the output still routes mismatched crimps, clamps the spherical
joint, lacks sensor mounting quantities, or changes unrelated purchase rows.
"""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs' / '20261007_bom_three_issue_correction'


class PurchaseCorrectionTests(unittest.TestCase):
    def evidence(self):
        target = OUT / 'verification.json'
        self.assertTrue(target.exists(), 'Corrected purchase/assembly evidence has not been generated')
        return json.loads(target.read_text(encoding='utf-8'))

    def test_main_splice_accepts_both_individual_wire_sizes(self):
        d = self.evidence()['main_splice']
        for cross_section in (2.08, 4.0):
            self.assertLessEqual(d['minimum_mm2'], cross_section)
            self.assertGreaterEqual(d['maximum_mm2'], cross_section)
        self.assertGreaterEqual(d['rated_current_a'], 20)
        self.assertFalse(d['requires_crimp_tool'])

    def test_small_control_wires_do_not_use_the_large_main_connector(self):
        d = self.evidence()['control_splice']
        self.assertLessEqual(d['minimum_mm2'], 0.205)
        self.assertGreaterEqual(d['maximum_mm2'], 2.08)

    def test_pin_has_adjustment_without_changing_eye_to_ball_offset(self):
        d = self.evidence()['pin_stack']
        self.assertEqual(d['eye_to_ball_offset_mm'], 16)
        self.assertAlmostEqual(d['unshimmed_gap_mm'], 1.5)
        self.assertAlmostEqual(d['nominal_shim_mm'], 1.0)
        self.assertAlmostEqual(d['nominal_final_gap_mm'], 0.5)
        self.assertGreaterEqual(d['shim_adjustment_per_axis_mm'], 2.3)

    def test_sensor_has_two_complete_mounts_without_extra_metal_holes(self):
        d = self.evidence()['sensor_mount']
        self.assertEqual(d['plate_quantity'], 2)
        self.assertEqual(d['m4_sensor_fasteners'], 6)
        self.assertEqual(d['m6_profile_fasteners'], 2)
        self.assertEqual(d['m8_profile_fasteners'], 2)
        self.assertEqual(d['new_metal_machining_operations'], 0)

    def test_unrelated_purchase_rows_and_sum_are_preserved(self):
        d = self.evidence()['bom']
        self.assertEqual(d['unrelated_row_changes'], [])
        self.assertEqual(d['independent_supply_sum'], d['spreadsheet_supply_sum'])
        self.assertTrue(d['links_match_visible_urls'])
        self.assertTrue(d['vendor_blocks_contiguous'])

    def test_changed_geometry_is_checked_not_only_bom_arithmetic(self):
        d = json.loads((OUT / 'exported_parts_verification.json').read_text(encoding='utf-8'))
        self.assertEqual(d['step_reimport_count'], 4)
        self.assertEqual(d['failed'], 0)
        self.assertTrue(d['plastic_plate_analytic_volume_check'])
        s = self.evidence()['sensor_mount']
        self.assertEqual(s['pose_count'], 27)
        self.assertEqual(s['unexpected_interference_count'], 0)
        self.assertEqual(s['invalid_boolean_count'], 0)


if __name__ == '__main__':
    unittest.main()
