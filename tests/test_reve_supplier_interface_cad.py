import unittest

from cad.profile_radial_reve_actual_vendor import (
    LMB10_DIMENSIONS,
    TRUSCO_PHS6_DIMENSIONS,
    UPPER_FRAME_RISE_MM,
    LOWER_LMB_FASTENER_STACK,
    UPPER_PHS_FASTENER_STACK,
    POSES,
    collision_audit,
    components_for_pose,
    full_pose_audit,
)
from fusion_scripts.ProfileRadialRevD import revd_data


class RevESupplierInterfaceCadTests(unittest.TestCase):
    def test_lmb10_public_drawing_dimensions_are_locked(self):
        self.assertEqual(
            {
                "base_length_mm": 56.0,
                "outside_width_mm": 26.0,
                "inside_width_mm": 20.0,
                "sheet_thickness_mm": 3.0,
                "mount_hole_diameter_mm": 8.0,
                "mount_hole_pitch_mm": 36.0,
                "pivot_hole_diameter_mm": 6.2,
                "pivot_axis_height_mm": 36.0,
                "rear_height_mm": 17.0,
                "pivot_radius_mm": 8.0,
            },
            LMB10_DIMENSIONS,
        )

    def test_misumi_trusco_phs6_order_dimensions_are_locked(self):
        self.assertEqual("PHS6", TRUSCO_PHS6_DIMENSIONS["order_code"])
        self.assertEqual("280-7599", TRUSCO_PHS6_DIMENSIONS["misumi_order_code"])
        self.assertEqual(6.0, TRUSCO_PHS6_DIMENSIONS["bore_mm"])
        self.assertEqual("M6", TRUSCO_PHS6_DIMENSIONS["female_thread"])
        self.assertEqual(13.0, TRUSCO_PHS6_DIMENSIONS["allowable_angle_deg"])
        self.assertEqual(20.0, TRUSCO_PHS6_DIMENSIONS["overall_width_mm"])
        self.assertEqual(30.0, TRUSCO_PHS6_DIMENSIONS["center_distance_mm"])
        self.assertEqual(40.0, TRUSCO_PHS6_DIMENSIONS["overall_height_mm"])
        self.assertEqual(0.0, TRUSCO_PHS6_DIMENSIONS["assembly_tangent_offset_mm"])

    def test_three_supplier_joint_parts_replace_provisional_joint_groups(self):
        parts = components_for_pose(POSES["collapsed"])
        lower = [part for part in parts if part.group == "lower_joints"]
        upper = [part for part in parts if part.group == "upper_joints"]
        self.assertEqual(3, len(lower))
        self.assertEqual(3, len(upper))
        self.assertTrue(all("LMB10" in part.name for part in lower))
        self.assertTrue(all("TRUSCO_PHS6" in part.name for part in upper))

    def test_collision_audit_includes_supplier_joint_envelopes(self):
        pairs = {row["pair"] for row in collision_audit(POSES["neutral"])["pairs"]}
        self.assertIn("upper_joints__upper_structure", pairs)
        self.assertIn("lower_lmb_bolts__lower_frame", pairs)
        self.assertIn("upper_phs_fasteners__upper_structure", pairs)
        self.assertIn("lower_joints__upper_assembly", pairs)
        self.assertIn("upper_joints__lower_assembly", pairs)
        self.assertIn("lower_joints__upper_joints", pairs)
        self.assertIn("actuator_1__lower_joint_1", pairs)
        self.assertIn("actuator_1__upper_joint_1", pairs)

    def test_upper_frame_rise_clears_actual_phs6_envelope(self):
        self.assertEqual(15.0, UPPER_FRAME_RISE_MM)
        parts = components_for_pose(POSES["neutral"])
        frame = next(part.shape for part in parts if part.group == "upper_frame")
        joints = [part.shape for part in parts if part.group == "upper_joints"]
        self.assertTrue(all(joint.intersect(frame).Volume() < 0.1 for joint in joints))

    def test_upper_clevis_shims_preserve_slot_centered_phs_stud(self):
        self.assertEqual(14.5, revd_data.P.joint_side_offset_mm)
        self.assertEqual(16.0, revd_data.P.upper_joint_side_offset_mm)
        self.assertEqual(1.5, revd_data.P.upper_joint_side_offset_mm - revd_data.P.joint_side_offset_mm)
        audit = collision_audit(POSES["collapsed"])
        stud_row = next(row for row in audit["pairs"] if row["pair"] == "upper_phs_fasteners__upper_structure")
        self.assertLess(stud_row["volume_mm3"], 0.1)

    def test_lower_lmb_bolt_has_recess_and_thread_engagement(self):
        self.assertEqual(12.0, LOWER_LMB_FASTENER_STACK["bolt_length_mm"])
        self.assertGreaterEqual(LOWER_LMB_FASTENER_STACK["thread_engagement_mm"], 6.0)
        self.assertGreaterEqual(LOWER_LMB_FASTENER_STACK["nominal_tip_recess_mm"], 2.0)

    def test_f07_stud_entry_is_not_misreported_as_full_nut_engagement(self):
        """Slot lip and external clamp gap make the present F07/F11 stack invalid."""
        stack = UPPER_PHS_FASTENER_STACK
        self.assertEqual(5.0, stack["slot_nut_body_thickness_mm"])
        self.assertEqual(2.5, stack["slot_lip_depth_mm"])
        self.assertEqual(10.5, stack["slot_floor_depth_mm"])
        self.assertAlmostEqual(
            stack["slot_nut_geometric_entry_max_mm"],
            stack["stud_length_mm"]
            - stack["phs_thread_engagement_mm"]
            - stack["jam_nut_thickness_mm"]
            - stack["exposed_stud_gap_mm"]
            - stack["slot_lip_depth_mm"],
        )
        self.assertEqual(3.5, stack["slot_nut_geometric_entry_max_mm"])
        self.assertEqual(-1.5, stack["tip_projection_beyond_nut_back_mm"])
        self.assertEqual(4.5, stack["slot_floor_clearance_mm"])
        self.assertEqual("INVALID_NO_PRELOAD", stack["assembly_status"])
        self.assertFalse(stack["effective_thread_engagement_verified"])
        self.assertFalse(stack["preload_path_closed"])
        self.assertAlmostEqual(
            stack["tip_projection_beyond_nut_back_mm"],
            stack["slot_nut_geometric_entry_max_mm"]
            - stack["slot_nut_body_thickness_mm"],
        )
        self.assertAlmostEqual(
            stack["slot_floor_clearance_mm"],
            stack["slot_floor_depth_mm"]
            - stack["slot_lip_depth_mm"]
            - stack["slot_nut_geometric_entry_max_mm"],
        )

    def test_full_pose_audit_declares_supplier_interfaces(self):
        audit = full_pose_audit()
        self.assertEqual(27, audit["pose_count"])
        self.assertEqual("LMB-10", audit["lower_joint_model"])
        self.assertEqual("TRUSCO PHS6 / 280-7599", audit["upper_joint_model"])
        self.assertTrue(audit["supplier_joint_envelopes_in_collision_audit"])
        self.assertEqual("POSE_LENGTH_AND_LISTED_SOLID_INTERSECTIONS_ONLY", audit["passes_scope"])
        self.assertFalse(audit["upper_phs_fastener_stack_valid_for_assembly"])
        self.assertEqual("INVALID_NO_PRELOAD", audit["upper_phs_fastener_stack"]["assembly_status"])
        self.assertTrue(audit["passes"])


if __name__ == "__main__":
    unittest.main()
