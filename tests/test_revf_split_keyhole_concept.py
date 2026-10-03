"""Contracts for the simplified two-piece PHS6 upper-bracket concept.

This is a concept/DFM comparison, not a fabrication release or strength proof.
"""

import importlib
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import cadquery as cq


class RevFSplitKeyholeConceptTests(unittest.TestCase):
    def _module(self):
        spec = importlib.util.find_spec("cad.revf_split_keyhole_concept")
        self.assertIsNotNone(spec, "split-keyhole concept module is missing")
        return importlib.import_module("cad.revf_split_keyhole_concept")

    def test_concept_module_exists(self):
        self._module()

    def test_two_custom_parts_are_simple_valid_single_solids(self):
        concept = self._module()
        plate = concept.build_mount_plate()
        support = concept.build_keyhole_support()

        self.assertTrue(plate.isValid())
        self.assertTrue(support.isValid())
        self.assertEqual(1, len(plate.Solids()))
        self.assertEqual(1, len(support.Solids()))

        plate_box = plate.BoundingBox()
        support_box = support.BoundingBox()
        self.assertAlmostEqual(60.0, plate_box.xlen, places=6)
        self.assertAlmostEqual(30.0, plate_box.ylen, places=6)
        self.assertAlmostEqual(10.0, plate_box.zlen, places=6)
        self.assertAlmostEqual(48.0, support_box.xlen, places=6)
        self.assertAlmostEqual(8.0, support_box.ylen, places=6)
        self.assertAlmostEqual(48.0, support_box.zlen, places=6)

    def test_interfaces_are_clearance_not_clamp_features(self):
        concept = self._module()
        d = concept.SPLIT_KEYHOLE_SPEC
        self.assertEqual(20.4, d["housing_clearance_diameter_mm"])
        self.assertGreater(d["housing_clearance_diameter_mm"], d["phs6_nominal_housing_diameter_mm"])
        self.assertEqual(14.0, d["stem_slot_width_mm"])
        self.assertEqual(8.2, d["mount_plate_groove_width_mm"])
        self.assertEqual(2, d["edge_screw_count"])
        self.assertFalse(d["approved_for_fabrication"])

        housing = concept.build_phs6_proxy()["housing"]
        nipple = concept.build_phs6_proxy()["grease_nipple_unknown"]
        support = concept.build_keyhole_support()
        self.assertLess(support.intersect(housing).Volume(), 1e-6)
        self.assertGreater(
            nipple.BoundingBox().xmax,
            support.BoundingBox().xmax,
            "unknown nipple envelope must remain visible as an unresolved interference marker",
        )

    def test_exported_steps_reimport_and_manifest_keeps_hold_notes(self):
        concept = self._module()
        with TemporaryDirectory() as directory:
            manifest = concept.export_split_keyhole_concept(Path(directory))
            self.assertEqual(3, len(manifest["step_files"]))
            for path in manifest["step_files"]:
                shape = cq.importers.importStep(str(path)).val()
                self.assertTrue(shape.isValid(), path)
                self.assertGreaterEqual(len(shape.Solids()), 1, path)
            note = Path(manifest["readme"]).read_text(encoding="utf-8")
            self.assertIn("NOT APPROVED FOR FABRICATION", note)
            self.assertIn("PHS6 grease-nipple", note)
            self.assertIn("750 N", note)


if __name__ == "__main__":
    unittest.main()
