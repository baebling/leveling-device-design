import unittest

from calculations.profile_only_vendor_interface_audit import build_audit
from cad.minimal_profile_only_assembly import (
    POSES,
    actuator_pin_lengths,
    assembly_bounds,
    components_for_pose,
    named_collision_volume,
    profile_cut_list,
    stop_sweep_audit,
    workspace_audit,
)


class MinimalProfileOnlyAssemblyTests(unittest.TestCase):
    def test_structural_members_are_extrusion_only(self):
        parts = components_for_pose(POSES["collapsed"])
        structural = [part for part in parts if part.group in {"lower_frame", "upper_frame"}]
        self.assertEqual(len(structural), 13)
        self.assertTrue(all("extrusion" in part.material for part in structural))
        self.assertFalse(any("plate" in part.material.lower() for part in parts))

    def test_profile_cut_list_is_complete(self):
        self.assertEqual(
            profile_cut_list(),
            {
                "4040 x 700": 2,
                "4040 x 620": 3,
                "4040 x 297": 2,
                "3030 x 700": 2,
                "3030 x 640": 4,
            },
        )

    def test_100_mm_actuator_covers_full_workspace(self):
        audit = workspace_audit()
        self.assertTrue(audit["passes_stroke"])
        self.assertGreater(audit["retract_margin_mm"], 6.0)
        self.assertGreater(audit["extend_margin_mm"], 6.0)
        self.assertEqual(len(audit["rows"]), 27)

    def test_collapsed_envelope_meets_height_target(self):
        bounds = assembly_bounds(POSES["collapsed"])
        self.assertLessEqual(bounds["zmax"], 300.0)
        self.assertAlmostEqual(bounds["xlen"], 700.0, places=3)
        self.assertAlmostEqual(bounds["ylen"], 700.0, places=3)

    def test_nominal_lift_tracks_50_mm(self):
        collapsed = actuator_pin_lengths(POSES["collapsed"])
        raised = actuator_pin_lengths(POSES["raised"])
        for lower, upper in zip(collapsed, raised):
            self.assertAlmostEqual(upper - lower, 49.9186, places=3)

    def test_mechanical_stop_slot_clears_tilt_sweep(self):
        audit = stop_sweep_audit()
        self.assertTrue(audit["passes_slot_clearance"])
        self.assertGreater(audit["minimum_radial_clearance_mm"], 1.5)

    def test_actuators_clear_profile_frames(self):
        moving = {"actuators", "actuator_eyes"}
        fixed = {"lower_frame", "lower_connectors", "upper_frame", "upper_connectors"}
        for name in ("collapsed", "max_pitch_roll"):
            with self.subTest(pose=name):
                self.assertLess(
                    named_collision_volume(POSES[name], moving, fixed),
                    1e-6,
                )

    def test_vendor_interface_audit_blocks_invalid_rev_a_release(self):
        audit = build_audit()
        self.assertFalse(audit["fabrication_release"])
        self.assertEqual(audit["status"], "BLOCKED_VENDOR_INTERFACE_MISMATCH")
        self.assertEqual(audit["failed_4035_joint_count"], 4)
        self.assertAlmostEqual(audit["phs6_vertical_stack"]["cad_shortfall_mm"], 15.0)
        self.assertEqual(
            audit["lmb10_mount"]["base_feature_spacing_mm"],
            36.0,
        )


if __name__ == "__main__":
    unittest.main()
