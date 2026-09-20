import unittest

from fusion_scripts.ProfileRadialRevD.revd_data import (
    LOWER_PROFILE_CUTS,
    P,
    SUPPORT_ANGLES_DEG,
    UPPER_PROFILE_CUTS,
    adapter_audit,
    adapter_rows,
    connector_audit,
    full_audit,
    joint_axis_audit,
    solve_platform,
    stop_sweep_audit,
    upper_support_points,
    workspace_audit,
)


class ProfileRadialRevDTests(unittest.TestCase):
    def test_supports_are_true_120_degree(self):
        self.assertEqual(SUPPORT_ANGLES_DEG, (90.0, 210.0, 330.0))
        self.assertEqual(full_audit()["support_gaps_deg"], (120.0, 120.0, 120.0))

    def test_central_hub_is_removed(self):
        audit = adapter_audit()
        self.assertEqual(audit["central_hub_plate_count"], 0)
        self.assertEqual(audit["adapter_count"], 3)

    def test_adapter_mount_holes_align_with_profile_slots(self):
        audit = adapter_audit()
        self.assertTrue(audit["passes"])
        self.assertTrue(all(row["mount_holes_on_slot"] for row in audit["alignment"]))

    def test_lmb_hole_pairs_are_36_mm_and_radial(self):
        for row in adapter_rows():
            first, second = row["lmb_tapped_holes_mm"]
            vector = (second[0] - first[0], second[1] - first[1])
            self.assertAlmostEqual(vector[0], P.lmb_hole_pitch_mm * row["radial"][0], 9)
            self.assertAlmostEqual(vector[1], P.lmb_hole_pitch_mm * row["radial"][1], 9)

    def test_local_adapters_do_not_overlap(self):
        self.assertFalse(any(row["overlaps"] for row in adapter_audit()["overlaps"]))

    def test_all_adapter_holes_have_edge_margin(self):
        margins = [
            row["minimum_hole_center_edge_margin_mm"]
            for row in adapter_audit()["hole_edge_checks"]
        ]
        self.assertGreaterEqual(min(margins), 10.0)

    def test_profile_mount_bolt_sockets_clear_lmb_bases(self):
        clearances = [
            row["minimum_m8_socket_to_lmb_planar_clearance_mm"]
            for row in adapter_audit()["profile_fastener_clearance_checks"]
        ]
        self.assertGreaterEqual(min(clearances), 3.0)

    def test_all_frame_joints_are_catalog_90_degree(self):
        audit = connector_audit()
        self.assertEqual(audit["oblique_profile_joint_count"], 0)
        self.assertEqual(audit["unavailable_adjustable_bracket_count"], 0)
        self.assertEqual(audit["axes_per_bracket"], ("horizontal_X", "horizontal_Y"))

    def test_frame_bracket_corners_are_on_crossbar_outer_faces(self):
        audit = connector_audit()
        self.assertEqual(audit["bracket_corner_reference"], "crossbar_outer_face")
        self.assertEqual(
            audit["lower_crossbar_center_to_bracket_corner_mm"],
            P.lower_profile_mm / 2.0,
        )
        self.assertEqual(
            audit["upper_crossbar_center_to_bracket_corner_mm"],
            P.upper_profile_mm / 2.0,
        )

    def test_profile_lengths_are_fixed_orderable_values(self):
        self.assertEqual([row[2] for row in LOWER_PROFILE_CUTS], [700.0, 700.0, 620.0, 620.0, 620.0, 620.0])
        self.assertEqual([row[2] for row in UPPER_PROFILE_CUTS], [700.0, 700.0, 640.0, 640.0, 640.0, 640.0])

    def test_upper_phs_points_lie_on_two_crossbar_slots(self):
        y_values = tuple(round(point[1], 6) for point in upper_support_points())
        self.assertEqual(y_values, (250.0, -125.0, -125.0))

    def test_27_pose_workspace_fits_actuator(self):
        audit = workspace_audit()
        self.assertEqual(audit["pose_count"], 27)
        self.assertTrue(audit["passes"])
        self.assertGreater(audit["retract_margin_mm"], 0.0)
        self.assertGreater(audit["extend_margin_mm"], 0.0)

    def test_neutral_pose_has_no_artificial_yaw(self):
        neutral = solve_platform(0.0, 0.0)
        self.assertAlmostEqual(neutral["x_mm"], 0.0, 9)
        self.assertAlmostEqual(neutral["y_mm"], 0.0, 9)
        self.assertAlmostEqual(neutral["yaw_rad"], 0.0, 9)

    def test_joint_axes_and_phs6_articulation_pass(self):
        audit = joint_axis_audit()
        self.assertTrue(audit["passes"])
        self.assertLess(audit["maximum_perpendicular_error_deg"], 1e-6)
        self.assertLessEqual(audit["maximum_phs6_articulation_deg"], 8.0)

    def test_independent_stops_clear_tilt_and_sit_outside_command_range(self):
        audit = stop_sweep_audit()
        self.assertTrue(audit["passes"])
        self.assertGreater(audit["minimum_radial_clearance_mm"], 0.0)
        self.assertGreaterEqual(
            audit["minimum_contact_bar_to_profile_clearance_mm"], 2.0
        )
        self.assertEqual(audit["lower_mechanical_contact_lift_mm"], -2.0)
        self.assertEqual(audit["upper_mechanical_contact_lift_mm"], 52.0)

    def test_collapsed_height_is_at_most_300_mm(self):
        self.assertLessEqual(full_audit()["collapsed_height_mm"], 300.0)

    def test_release_stays_false_until_fusion_and_physical_checks(self):
        audit = full_audit()
        self.assertTrue(audit["digital_layout_passes"])
        self.assertFalse(audit["fabrication_release"])
        self.assertFalse(audit["purchase_release"])

    def test_upper_rod_reaches_the_eye_envelope(self):
        self.assertGreater(P.upper_rod_eye_overlap_mm, 0.0)
        self.assertLess(P.upper_rod_eye_overlap_mm, P.actuator_eye_outer_radius_mm)


if __name__ == "__main__":
    unittest.main()
