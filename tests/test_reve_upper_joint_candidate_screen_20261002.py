"""Candidate-only tests; a passing screen is not fabrication approval."""

import importlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


class UpperJointCandidateScreenTests(unittest.TestCase):
    @staticmethod
    def subject():
        try:
            return importlib.import_module("cad.reve_upper_joint_candidate_screen_20261002")
        except ModuleNotFoundError as exc:
            raise AssertionError("Candidate screen module is absent") from exc

    def test_stud_clamp_path_and_slot_floor_are_derived_from_contact_planes(self):
        # Mutation caught: treating the 5 mm SP306 body as if it starts at
        # the exposed profile face, or extending a 28 mm stud to the floor.
        stack = self.subject().candidate_stud_stack()
        self.assertEqual(39.0, stack["profile_outer_face_z_from_phs_mm"])
        self.assertEqual((35.0, 38.0), stack["thin_nut_z_from_phs_mm"])
        self.assertEqual((38.0, 39.0), stack["shim_z_from_phs_mm"])
        self.assertEqual((41.5, 46.5), stack["slot_nut_body_z_from_phs_mm"])
        self.assertEqual(48.0, stack["stud_tip_z_from_phs_mm"])
        self.assertEqual(5.0, stack["slot_nut_geometric_overlap_mm"])
        self.assertEqual(1.5, stack["tip_past_slot_nut_mm"])
        self.assertEqual(1.5, stack["slot_floor_clearance_mm"])
        self.assertFalse(stack["effective_thread_engagement_verified"])
        self.assertFalse(stack["clamp_force_verified"])

    def test_cb6_55_retention_stack_does_not_treat_max_grip_as_plain_shank(self):
        # MISUMI's JIS B1176 M6x55 table gives ls,min=26 and lg,max=31.
        # Mutation caught: using 55-24=31 as guaranteed smooth shaft.
        subject = self.subject()
        self.assertTrue(hasattr(subject, "candidate_cb6_stack"), "CB6-55 stack screen is absent")
        stack = subject.candidate_cb6_stack()
        self.assertEqual((-26.0, -6.0), stack["actuator_eye_t_from_phs_mm"])
        self.assertEqual((-6.0, -4.5), stack["shims_t_from_phs_mm"])
        self.assertEqual((-4.5, 4.5), stack["phs_ball_t_from_phs_mm"])
        self.assertEqual(26.0, stack["guaranteed_plain_shank_length_min_mm"])
        self.assertEqual(31.0, stack["max_grip_length_mm"])
        self.assertEqual(30.5, stack["stack_requires_plain_shank_mm"])
        self.assertEqual(4.5, stack["plain_shank_guarantee_shortfall_mm"])
        self.assertEqual((0.0, 5.0), stack["possible_thread_transition_t_from_phs_mm"])
        self.assertTrue(stack["thread_transition_possible_inside_phs_ball"])
        self.assertEqual((5.0, 10.0), stack["retaining_nut_t_from_phs_mm"])
        self.assertEqual((10.0, 29.0), stack["exposed_thread_tail_t_from_phs_mm"])
        self.assertEqual(0.5, stack["max_grip_minus_nominal_stack_mm_not_endplay_guarantee"])
        self.assertFalse(stack["fit_and_retention_verified"])

    def test_candidate_solids_follow_the_actual_first_upper_joint_axis(self):
        # Mutation caught: rotating the bolt with the upper platform instead
        # of the world-fixed lower R hinge, or flipping head and thread tail.
        from cad.profile_radial_reve_actual_vendor import Pose

        subject = self.subject()
        self.assertTrue(hasattr(subject, "candidate_joint_solids"), "Candidate solids are absent")
        parts = subject.candidate_joint_solids(Pose("neutral", 25.0, 0.0, 0.0), 1)
        head = parts["bolt_head"].BoundingBox()
        tail = parts["thread_tail"].BoundingBox()
        stud = parts["stud"].BoundingBox()
        # The existing solver has about +0.344 degrees neutral yaw: the
        # PHS centre is at x=-1.5, not at the untransformed support x=0.
        self.assertAlmostEqual(24.5, head.xmin, places=5)
        self.assertAlmostEqual(30.5, head.xmax, places=5)
        self.assertAlmostEqual(-30.5, tail.xmin, places=5)
        self.assertAlmostEqual(-11.5, tail.xmax, places=5)
        self.assertAlmostEqual(319.0, stud.zmax, places=5)

    def test_intersection_screen_uses_solid_overlap_not_bounding_box_only(self):
        # Mutation caught: reporting a bounding-box touch as an actual clash.
        import cadquery as cq

        subject = self.subject()
        self.assertTrue(hasattr(subject, "screened_intersection_mm3"), "Intersection screen is absent")
        first = cq.Workplane("XY").box(10, 10, 10).val()
        disjoint = first.translate((20, 0, 0))
        overlap = first.translate((5, 0, 0))
        self.assertAlmostEqual(0.0, subject.screened_intersection_mm3(first, disjoint))
        self.assertAlmostEqual(500.0, subject.screened_intersection_mm3(first, overlap))

    def test_pose_screen_lists_fastener_and_assumed_tool_approach_checks(self):
        # Mutation caught: reporting a candidate screen that silently omits
        # the CB6 thread tail or tool approach path.
        from cad.profile_radial_reve_actual_vendor import Pose

        subject = self.subject()
        self.assertTrue(hasattr(subject, "candidate_pose_screen"), "Pose screen is absent")
        result = subject.candidate_pose_screen(Pose("neutral", 25.0, 0.0, 0.0))
        pairs = {row["pair"] for row in result["solid_checks"]}
        self.assertEqual(3, result["axis_count"])
        self.assertIn("A1_thread_tail__upper_frame", pairs)
        self.assertIn("A2_bolt_head__upper_brackets", pairs)
        self.assertIn("A3_slot_nut_23x10x5_envelope__upper_frame", pairs)
        self.assertEqual(12, len(result["thin_spanner_approaches"]))
        self.assertFalse(result["assembly_release"])

    def test_grid_summary_keeps_mated_profile_overlap_separate_from_gross_clash(self):
        # Mutation caught: treating the old Fusion slot section's modeled
        # interference as proof of a real DNF3030 supplier part collision.
        from cad.profile_radial_reve_actual_vendor import Pose

        subject = self.subject()
        self.assertTrue(hasattr(subject, "candidate_grid_screen"), "Grid screen is absent")
        result = subject.candidate_grid_screen((Pose("neutral", 25.0, 0.0, 0.0),))
        self.assertEqual(1, result["pose_count"])
        self.assertEqual(0.0, result["max_gross_overlap_mm3"])
        self.assertGreater(result["max_mated_interface_overlap_mm3"], 100.0)
        self.assertIn("max_eye_face_overlap_mm3", result)
        self.assertGreater(result["max_eye_face_overlap_mm3"], 0.1)
        self.assertFalse(result["assembly_release"])
        self.assertFalse(result["purchase_release"])
        self.assertIn("MODEL_SECTION_MISMATCH", result["profile_slot_status"])
        self.assertIn("HOLD", result["head_eye_contact_status"])
        self.assertIn("REJECT_CB6_55", result["pivot_fit_status"])

    def test_review_export_refuses_any_release_flag(self):
        # Mutation caught: an output file falsely marking this screen as
        # released for purchase, machining or assembly.
        subject = self.subject()
        self.assertTrue(hasattr(subject, "save_candidate_review"), "Review export is absent")
        with TemporaryDirectory() as folder:
            path = Path(folder) / "review.json"
            with self.assertRaises(ValueError):
                subject.save_candidate_review(path, {"assembly_release": True})
            self.assertFalse(path.exists())
            subject.save_candidate_review(
                path,
                {"assembly_release": False, "purchase_release": False, "fabrication_release": False},
            )
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertFalse(saved["assembly_release"])

    def test_one_axis_review_assembly_contains_candidate_and_old_slot_context(self):
        # Mutation caught: shipping a STEP of candidate screws without the
        # legacy slot section that causes the documented model mismatch.
        subject = self.subject()
        self.assertTrue(hasattr(subject, "candidate_axis1_review_assembly"), "Review STEP assembly is absent")
        assembly = subject.candidate_axis1_review_assembly()
        names = {child.name for child in assembly.children}
        self.assertEqual(14, len(names))
        self.assertIn("A1_OLD_UPPER_CROSSBAR_SECTION_MODEL_MISMATCH", names)
        self.assertIn("A1_CB6_55_THREAD_TAIL_19MM", names)
        self.assertIn("A1_CB6_55_OUTER_ENVELOPE_NOT_SMOOTH_SHANK_PROOF", names)
        self.assertIn("A1_SP306_23X10X5_ENVELOPE", names)


if __name__ == "__main__":
    unittest.main()
