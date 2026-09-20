import unittest

from cad.minimal_radial_revc import (
    C,
    POSES,
    assembly_bounds,
    components_for_pose,
    connector_axis_audit,
    hub_mount_points,
    joint_axis_audit,
    lmb_tap_points,
    named_collision_volume,
    platform_transform,
    profile_cut_list,
    stop_sweep_audit,
    support_azimuth_audit,
    workspace_audit,
)


class MinimalRadialRevCTests(unittest.TestCase):
    def test_supports_are_exactly_120_degree_radial(self):
        audit = support_azimuth_audit()
        self.assertEqual(audit["azimuths_deg"], (90.0, 210.0, 330.0))
        self.assertEqual(audit["circular_gaps_deg"], (120.0, 120.0, 120.0))
        self.assertTrue(audit["passes"])

    def test_rps_plane_solver_closes_all_27_poses(self):
        audit = workspace_audit()
        self.assertTrue(audit["passes"])
        self.assertEqual(audit["pose_count"], 27)
        self.assertLess(audit["maximum_constraint_residual_mm"], 1e-9)
        self.assertGreater(audit["retract_margin_mm"], 12.9)
        self.assertGreater(audit["extend_margin_mm"], 26.9)

    def test_joint_axes_and_phs_articulation_pass(self):
        audit = joint_axis_audit()
        self.assertTrue(audit["passes"])
        self.assertLess(audit["maximum_perpendicular_error_deg"], 1e-9)
        self.assertLess(audit["maximum_phs_articulation_deg"], 4.1)
        self.assertEqual(audit["minimum_published_phs_allowance_deg"], 8.0)

    def test_collapsed_envelope_meets_height_target(self):
        bounds = assembly_bounds(POSES["collapsed"])
        self.assertAlmostEqual(bounds["xlen"], 700.0, places=3)
        self.assertAlmostEqual(bounds["ylen"], 700.0, places=3)
        self.assertLessEqual(bounds["zmax"], 300.0 + 1e-6)

    def test_connector_brackets_have_two_horizontal_axes(self):
        audit = connector_axis_audit()
        self.assertTrue(audit["passes"])
        self.assertEqual(audit["lower_4035_count"], 8)
        self.assertEqual(audit["upper_DCB3025_count"], 8)
        self.assertEqual(
            audit["modeled_axes_per_bracket"],
            ("horizontal_X", "horizontal_Y"),
        )

    def test_small_hub_has_complete_mount_and_lmb_patterns(self):
        self.assertEqual(len(hub_mount_points()), 8)
        self.assertEqual(len(lmb_tap_points()), 6)
        for x, y in hub_mount_points() + lmb_tap_points():
            self.assertLess(abs(x), C.lower_hub_length_mm / 2.0 - 5.0)
            self.assertLess(abs(y), C.lower_hub_width_mm / 2.0 - 5.0)

    def test_profiles_use_square_orderable_lengths(self):
        self.assertEqual(
            profile_cut_list(),
            {
                "4040 x 700": 2,
                "4040 x 620": 4,
                "3030 x 700": 2,
                "3030 x 640": 4,
            },
        )

    def test_actuator_envelopes_clear_fixed_structure(self):
        fixed = {
            "lower_frame",
            "lower_connectors",
            "lower_hub",
            "lower_joints",
            "upper_frame",
            "upper_connectors",
        }
        for name, pose in POSES.items():
            with self.subTest(pose=name):
                self.assertLess(
                    named_collision_volume(pose, {"actuators"}, fixed), 1e-6
                )
                self.assertLess(
                    named_collision_volume(
                        pose,
                        {"actuator_eyes"},
                        {"lower_frame", "lower_hub", "upper_frame"},
                    ),
                    1e-6,
                )

    def test_mechanical_stop_sweep_clears_opening(self):
        audit = stop_sweep_audit()
        self.assertTrue(audit["passes"])
        self.assertGreater(audit["minimum_clearance_mm"], 5.4)

    def test_component_manifest_retains_only_real_open_items(self):
        parts = components_for_pose(POSES["collapsed"])
        self.assertEqual(len(parts), 85)
        open_parts = [part for part in parts if part.status != "RELEASED"]
        self.assertTrue(any("EYE_WIDTH" in part.status for part in open_parts))
        self.assertTrue(any("STOP_DETAIL" in part.status for part in open_parts))
        self.assertFalse(any("REJECTED_FASTENER_AXIS" in part.status for part in parts))

    def test_pose_solver_induces_only_small_xy_yaw_correction(self):
        for pose in POSES.values():
            transform = platform_transform(pose)
            self.assertLess(abs(transform.x_mm), 0.5)
            self.assertLess(abs(transform.y_mm), 0.5)
            self.assertLess(abs(__import__("math").degrees(transform.yaw_rad)), 0.1)


if __name__ == "__main__":
    unittest.main()
