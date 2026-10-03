"""Contracts for the simplified direct-M6 PHS6 mounting review."""

import importlib
import importlib.util
from math import pi
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import cadquery as cq


class RevFDirectPHS6MountTests(unittest.TestCase):
    def _module(self):
        spec = importlib.util.find_spec("cad.revf_direct_phs6_mount")
        self.assertIsNotNone(spec, "direct PHS6 mount review module is missing")
        return importlib.import_module("cad.revf_direct_phs6_mount")

    def test_review_module_exists(self):
        self._module()

    def test_one_simple_plate_is_the_only_custom_upper_part(self):
        review = self._module()
        plate = review.build_direct_mount_plate()
        box = plate.BoundingBox()
        self.assertTrue(plate.isValid())
        self.assertEqual(1, len(plate.Solids()))
        self.assertAlmostEqual(60.0, box.xlen, places=6)
        self.assertAlmostEqual(30.0, box.ylen, places=6)
        self.assertAlmostEqual(9.0, box.zlen, places=6)
        self.assertEqual(1, review.DIRECT_MOUNT_SPEC["custom_part_types"])
        self.assertEqual(3, review.DIRECT_MOUNT_SPEC["order_quantity"])

        base = 60.0 * 30.0 * 9.0
        through = 3.0 * pi * 3.3**2 * 9.0
        counterbore_annulus = pi * (5.5**2 - 3.3**2) * 4.5
        self.assertAlmostEqual(base - through - counterbore_annulus, plate.Volume(), places=3)

    def test_m6x12_has_useful_engagement_without_blind_hole_bottoming(self):
        review = self._module()
        stack = review.m6_stack_screen()
        self.assertEqual([7.15, 7.85], stack["engagement_bounds_mm"])
        self.assertEqual([4.15, 4.85], stack["blind_bottom_clearance_bounds_mm"])
        self.assertGreater(stack["minimum_engagement_diameters"], 1.0)
        self.assertGreaterEqual(stack["head_flush_margin_mm"], 0.5)

    def test_750n_screen_passes_geometry_but_keeps_supplier_thread_gate_open(self):
        review = self._module()
        screen = review.direct_mount_static_screen(force_n=750.0)
        self.assertAlmostEqual(750.0 / 20.1, screen["external_axial_stress_mpa"], places=6)
        self.assertGreater(screen["minimum_preload_n"], 2500.0)
        self.assertGreater(screen["separation_margin"], 3.0)
        self.assertGreater(screen["friction_moment_margin_at_required_articulation"], 1.2)
        self.assertGreater(screen["bolt_proof_margin"], 4.0)
        self.assertTrue(screen["conditional_geometry_screen_pass"])
        self.assertFalse(screen["supplier_thread_capacity_verified"])
        self.assertFalse(screen["purchase_release"])

    def test_same_plate_places_on_all_three_axes_without_solid_overlap(self):
        review = self._module()
        rows = review.audit_direct_mount_poses()
        self.assertEqual(27, len(rows))
        self.assertTrue(all(row["same_plate_sku_all_axes"] for row in rows))
        self.assertTrue(all(row["boolean_valid"] for row in rows))
        self.assertLess(max(row["unexpected_interference_mm3"] for row in rows), 1e-6)
        self.assertLess(max(row["maximum_articulation_deg"] for row in rows), 13.0)
        self.assertTrue(all(row["actuator_length_window_pass"] for row in rows))

    def test_exported_plate_reimports_as_one_valid_solid(self):
        review = self._module()
        with TemporaryDirectory() as directory:
            manifest = review.export_direct_mount_review(Path(directory))
            plate = cq.importers.importStep(str(manifest["plate_step"])).val()
            self.assertTrue(plate.isValid())
            self.assertEqual(1, len(plate.Solids()))
            self.assertTrue(Path(manifest["audit_json"]).exists())
            note = Path(manifest["readme"]).read_text(encoding="utf-8")
            self.assertIn("CONDITIONAL GO", note)
            self.assertIn("CBS6-12", note)
            self.assertIn("3개", note)


if __name__ == "__main__":
    unittest.main()
