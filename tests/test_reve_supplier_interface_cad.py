import unittest

from cad.profile_radial_reve_actual_vendor import (
    LMB10_DIMENSIONS,
    TRUSCO_PHS6_DIMENSIONS,
    POSES,
    collision_audit,
    components_for_pose,
    full_pose_audit,
)


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
        self.assertEqual(1.5, TRUSCO_PHS6_DIMENSIONS["assembly_tangent_offset_mm"])

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
        self.assertIn("lower_joints__upper_assembly", pairs)
        self.assertIn("upper_joints__lower_assembly", pairs)
        self.assertIn("lower_joints__upper_joints", pairs)
        self.assertIn("actuator_1__lower_joint_1", pairs)
        self.assertIn("actuator_1__upper_joint_1", pairs)

    def test_full_pose_audit_declares_supplier_interfaces(self):
        audit = full_pose_audit()
        self.assertEqual(27, audit["pose_count"])
        self.assertEqual("LMB-10", audit["lower_joint_model"])
        self.assertEqual("TRUSCO PHS6 / 280-7599", audit["upper_joint_model"])
        self.assertTrue(audit["supplier_joint_envelopes_in_collision_audit"])
        self.assertTrue(audit["passes"])


if __name__ == "__main__":
    unittest.main()
