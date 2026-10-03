"""Fabrication-package contracts for the six Rev F custom metal parts.

These tests protect dimensions that a quotation upload or hand drilling relies
on.  They do not certify strength, tolerances, or field safety.
"""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import cadquery as cq
from pypdf import PdfReader

from cad.revf_quote_package import (
    LOWER_PLATE_SPECS,
    UPPER_BRACKET_SPEC,
    build_lower_plate,
    build_upper_bracket,
    export_quote_package,
)


class RevFQuotePackageTests(unittest.TestCase):
    def test_lower_plate_hole_coordinates_match_the_approved_drill_plan(self):
        expected = {
            "A1": {
                "profile_through": ((-48.0, 12.0), (48.0, 12.0)),
                "lmb_tap_m8": ((14.5, -24.0), (14.5, 12.0)),
            },
            "A2": {
                "profile_through": ((-48.0, -18.557), (48.0, -18.557)),
                "lmb_tap_m8": ((23.927, 12.0), (-7.25, -6.0)),
            },
            "A3": {
                "profile_through": ((-50.0, 6.557), (50.0, 6.557)),
                "lmb_tap_m8": ((-18.427, 12.0), (12.75, -6.0)),
            },
        }
        self.assertEqual(expected, {
            key: {
                "profile_through": spec["profile_through"],
                "lmb_tap_m8": spec["lmb_tap_m8"],
            }
            for key, spec in LOWER_PLATE_SPECS.items()
        })

    def test_lower_plates_are_single_valid_120_by_70_by_8_solids(self):
        for part_id in ("A1", "A2", "A3"):
            shape = build_lower_plate(part_id, model_threads=False)
            box = shape.BoundingBox()
            self.assertTrue(shape.isValid(), part_id)
            self.assertEqual(1, len(shape.Solids()), part_id)
            self.assertAlmostEqual(120.0, box.xlen, places=6)
            self.assertAlmostEqual(70.0, box.ylen, places=6)
            self.assertAlmostEqual(8.0, box.zlen, places=6)
            # 2 x D9 and 2 x D6.8 pilot holes must remove material.
            expected = 120 * 70 * 8 - 2 * 3.141592653589793 * (4.5**2 + 3.4**2) * 8
            self.assertAlmostEqual(expected, shape.Volume(), places=3)

    def test_lower_plate_detailed_model_contains_material_removed_by_m8_threads(self):
        """Removing the helical groove must distinguish a tapped hole from a D6.8 bore."""
        for part_id in ("A1", "A2", "A3"):
            pilot_only = build_lower_plate(part_id, model_threads=False)
            threaded = build_lower_plate(part_id, model_threads=True)
            self.assertTrue(threaded.isValid(), part_id)
            self.assertEqual(1, len(threaded.Solids()), part_id)
            self.assertLess(threaded.Volume(), pilot_only.Volume() - 1.0, part_id)
            self.assertGreater(threaded.Volume(), pilot_only.Volume() - 100.0, part_id)

    def test_upper_bracket_has_quote_dimensions_and_clearance_bore(self):
        self.assertEqual(20.2, UPPER_BRACKET_SPEC["saddle_diameter_mm"])
        self.assertEqual(44.0, UPPER_BRACKET_SPEC["mount_pitch_mm"])
        self.assertEqual(6.6, UPPER_BRACKET_SPEC["mount_hole_diameter_mm"])
        self.assertEqual(11.0, UPPER_BRACKET_SPEC["counterbore_diameter_mm"])
        self.assertEqual(6.0, UPPER_BRACKET_SPEC["counterbore_depth_mm"])
        for axis in (1, 2, 3):
            shape = build_upper_bracket(axis)
            self.assertTrue(shape.isValid(), axis)
            self.assertEqual(1, len(shape.Solids()), axis)
            # The clearance cylinder through the saddle must be empty.
            bore = cq.Solid.makeCylinder(10.1, 8.75, cq.Vector(0, -4.375, 0), cq.Vector(0, 1, 0))
            self.assertLess(shape.intersect(bore).Volume(), 1e-6, axis)

    def test_exported_steps_reimport_as_six_single_solids(self):
        with TemporaryDirectory() as directory:
            manifest = export_quote_package(Path(directory), include_pdf=False)
            self.assertEqual(6, len(manifest["step_files"]))
            self.assertEqual(3, len(manifest["quote_simplified_step_files"]))
            self.assertEqual(6, len(manifest["dxf_files"]))
            for step in manifest["step_files"]:
                imported = cq.importers.importStep(str(step)).val()
                self.assertTrue(imported.isValid(), step)
                self.assertEqual(1, len(imported.Solids()), step)
            for step in manifest["quote_simplified_step_files"]:
                imported = cq.importers.importStep(str(step)).val()
                self.assertTrue(imported.isValid(), step)
                self.assertEqual(1, len(imported.Solids()), step)

            readme = Path(manifest["readme"]).read_text(encoding="utf-8")
            self.assertIn("상면에서 Ø11×깊이 6 mm", readme)
            self.assertNotIn("아래쪽 Ø11", readme)
            self.assertIn("M8×1.25 실제 나사산", readme)

    def test_dimensioned_pdf_contains_each_custom_part_and_limit_notes(self):
        from scripts.build_revf_quote_package import build_drawing_pdf

        with TemporaryDirectory() as directory:
            pdf = build_drawing_pdf(Path(directory))
            reader = PdfReader(pdf)
            self.assertEqual(8, len(reader.pages))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            normalized_text = " ".join(text.split())
            for part_id in ("A1 LOWER", "A2 LOWER", "A3 LOWER", "UP-A1", "UP-A2", "UP-A3"):
                self.assertIn(part_id, text)
            self.assertIn("STEP controls the 3D pocket", text)
            self.assertIn("counterbore x 6 deep from top", text)
            self.assertIn("Detailed STEP models M8x1.25 threads", normalized_text)
            self.assertNotIn("The STEP models threads as D6.8 pilot holes", text)
            self.assertIn("No cart, payload, or person", text)


if __name__ == "__main__":
    unittest.main()
