import unittest

from cad.minimal_profile_only_revb import (
    B,
    POSES,
    actuation_jacobian_audit,
    actuator_pin_lengths,
    assembly_bounds,
    components_for_pose,
    lower_support_points,
    named_collision_volume,
    profile_cut_list,
    stop_sweep_audit,
    upper_support_points,
    workspace_audit,
)


class MinimalProfileOnlyRevBTests(unittest.TestCase):
    def test_cut_list_uses_orderable_lengths(self):
        self.assertEqual(
            profile_cut_list(),
            {
                "4040 x 700": 2,
                "4040 x 620": 3,
                "4040 x 300": 1,
                "3030 x 700": 2,
                "3030 x 640": 4,
            },
        )

    def test_support_triangles_are_non_collinear(self):
        for points in (lower_support_points(), upper_support_points()):
            (x1, y1), (x2, y2), (x3, y3) = points
            twice_area = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
            self.assertGreater(twice_area, 1.0)

    def test_published_lmb_and_phs_heights_are_applied(self):
        self.assertEqual(B.lower_joint_z_mm, 40.0 + 36.0)
        self.assertEqual(B.upper_profile_bottom_local_z_mm, 30.0 + 5.0)

    def test_workspace_has_twenty_mm_or_better_nominal_margin(self):
        audit = workspace_audit()
        self.assertTrue(audit["passes_stroke"])
        self.assertGreaterEqual(audit["retract_margin_mm"], 20.0)
        self.assertGreater(audit["extend_margin_mm"], 24.0)
        self.assertEqual(audit["pose_count"], 27)

    def test_collapsed_height_is_below_300_mm(self):
        bounds = assembly_bounds(POSES["collapsed"])
        self.assertLessEqual(bounds["zmax"], 296.0 + 1e-6)
        self.assertAlmostEqual(bounds["xlen"], 700.0, places=3)
        self.assertAlmostEqual(bounds["ylen"], 700.0, places=3)

    def test_actuation_jacobian_is_full_rank(self):
        audit = actuation_jacobian_audit()
        self.assertTrue(audit["full_rank"])
        self.assertGreater(abs(audit["determinant"]), 40000.0)

    def test_actuator_envelopes_clear_frames_and_lmb(self):
        fixed = {
            "lower_frame", "lower_connectors", "lower_joints",
            "upper_frame", "upper_connectors",
        }
        for name, pose in POSES.items():
            with self.subTest(pose=name):
                self.assertLess(
                    named_collision_volume(pose, {"actuators"}, fixed),
                    1e-6,
                )
                self.assertLess(
                    named_collision_volume(
                        pose, {"actuator_eyes"}, {"lower_frame", "upper_frame"}
                    ),
                    1e-6,
                )

    def test_mechanical_stop_sweep_clears_opening(self):
        audit = stop_sweep_audit()
        self.assertTrue(audit["passes"])
        self.assertGreater(audit["minimum_clearance_mm"], 7.5)

    def test_component_manifest_keeps_open_vendor_items_visible(self):
        parts = components_for_pose(POSES["collapsed"])
        self.assertEqual(len(parts), 80)
        open_parts = [part for part in parts if part.status != "RELEASED"]
        self.assertTrue(any("EYE_WIDTH" in part.status for part in open_parts))
        self.assertTrue(any("STOP" in part.bom_key for part in open_parts))

    def test_common_lift_increases_all_three_lengths(self):
        collapsed = actuator_pin_lengths(POSES["collapsed"])
        raised = actuator_pin_lengths(POSES["raised"])
        for low, high in zip(collapsed, raised):
            self.assertGreater(high - low, 35.0)


if __name__ == "__main__":
    unittest.main()
