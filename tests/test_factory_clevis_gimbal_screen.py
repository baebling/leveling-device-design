import unittest

import cadquery as cq

from cad.factory_clevis_gimbal import components
from calculations.factory_clevis_gimbal_screen import (
    nested_gimbal_pin_screen,
    serial_adapter_workspace_screen,
    summary,
)


class FactoryClevisGimbalScreenTests(unittest.TestCase):
    def test_serial_hrt8e_adapter_consumes_lower_workspace(self):
        result = serial_adapter_workspace_screen()
        self.assertFalse(result["passes_catalog_endpoint"])
        self.assertEqual(result["selection_status"], "reject_for_current_geometry")

    def test_nested_gimbal_preserves_pin_center_and_passes_static_seed(self):
        result = nested_gimbal_pin_screen()
        self.assertEqual(result["kinematic_center_offset_mm"], 0.0)
        self.assertTrue(result["passes_preliminary_static_screen"])
        self.assertEqual(result["factory_hole_mm"], 8.2)
        self.assertEqual(result["factory_eye_width_mockup_range_mm"], (9.0, 11.0))
        self.assertEqual(result["factory_eye_outer_diameter_mm"], 20.0)
        self.assertLess(result["pin_bending_mpa"], 100.0)

    def test_measurement_gate_remains_explicit(self):
        result = summary()
        self.assertIn("selected 450 lbf 8-inch", result["nested_gimbal"]["open_measurements"])
        self.assertEqual(result["phase_gate"], "STATIC_BENCH_POC_MEASURED_MOCKUP_REQUIRED")

    def test_cad_seed_is_valid_and_keeps_two_orthogonal_pin_axes(self):
        rows = components()
        self.assertEqual(len(rows), 5)
        for row in rows:
            self.assertTrue(row.shape.isValid(), row.name)
        by_name = {row.name: row.shape for row in rows}
        factory = by_name["jnt_cg01_factory_pin"].BoundingBox()
        trunnion = by_name["jnt_cg01_opposed_trunnions"].BoundingBox()
        self.assertGreater(factory.ylen, factory.zlen)
        self.assertGreater(trunnion.zlen, trunnion.ylen)
        self.assertAlmostEqual(
            by_name["jnt_cg01_factory_eye_reference"].intersect(
                by_name["jnt_cg01_inner_cradle"]
            ).Volume(),
            0.0,
            places=6,
        )


if __name__ == "__main__":
    unittest.main()
