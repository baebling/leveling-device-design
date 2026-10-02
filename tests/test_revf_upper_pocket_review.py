"""Review geometry tests; passing these does not release fabrication."""
import unittest
from dataclasses import replace
from itertools import product
import cadquery as cq

from cad.revf_upper_pocket_inputs import load_inputs
from cad.profile_radial_reve_actual_vendor import Pose, upper_eye_points
from cad.profile_radial_revf_upper_pocket_review import (
    pocket_brackets, phs_components, revf_components_for_pose,
    joint_reference, assembly_path_review, local_review_geometry,
)


class UpperPocketReviewTests(unittest.TestCase):
    def test_three_unique_brackets_and_separate_bearing_replace_old_stack(self):
        inputs = load_inputs()
        brackets = pocket_brackets(inputs)
        self.assertEqual(3, len(brackets))
        self.assertEqual(3, len({p.name for p in brackets}))
        self.assertTrue(all(len(p.shape.Solids()) == 1 for p in brackets))
        components = phs_components(1, Pose("neutral", 25, 0, 0))
        self.assertIn("housing", components)
        self.assertIn("ball", components)
        self.assertIsNot(components["housing"], components["ball"])
        self.assertLess(components["housing"].intersect(components["ball"]).Volume(), 1e-6)
        parts = revf_components_for_pose(Pose("neutral", 25, 0, 0), inputs)
        self.assertFalse(any("UPPER_PHS_FASTENER_STACK" in p.name or "PHS_M6x25" in p.name for p in parts))

    def test_pocket_supports_housing_but_does_not_clamp_ball_or_eye(self):
        geo = local_review_geometry(load_inputs())
        self.assertLess(geo["bracket"].distance(geo["housing"]), 1e-6)
        for moving in ("housing", "ball_window", "eye_envelope"):
            self.assertLess(geo["bracket"].intersect(geo[moving]).Volume(), 1e-6, moving)
        self.assertLess(geo["bracket"].BoundingBox().ylen, 31)

    def test_pin_passes_all_three_ball_and_eye_centres_in_combined_tilt(self):
        for pitch, roll in product((-3, 0, 3), repeat=2):
            pose = Pose("tilt", 25, pitch, roll)
            for axis, eye in enumerate(upper_eye_points(pose), 1):
                ref = joint_reference(axis, pose)
                delta = cq.Vector(*eye) - cq.Vector(*ref["ball_center"])
                self.assertAlmostEqual(delta.Length, 16.0, places=6)
                self.assertLess(delta.cross(cq.Vector(*ref["pin_axis"])).Length, 1e-6)
                solids = phs_components(axis, pose)
                self.assertLess(solids["pin_shoulder"].intersect(solids["ball"]).Volume(), 1e-6)

    def test_assembly_paths_record_every_stage_and_keep_unknowns_blocked(self):
        review = assembly_path_review(load_inputs())
        self.assertEqual({"housing_insertion", "m6_retention", "eye_approach", "pin_insertion", "shim_insertion", "spacer_insertion", "m5_nut", "profile_attachment", "tool_access"}, {r["stage"] for r in review["stages"]})
        self.assertTrue(all(r["samples"] > 1 for r in review["stages"]))
        self.assertTrue(all("maximum_unintended_volume_mm3" in r for r in review["stages"]))
        self.assertFalse(review["assembly_verified"])
        self.assertFalse(review["fabrication_release"])
        self.assertFalse(review["purchase_release"])
        self.assertEqual(30.5, review["nominal_grip_mm"])
        self.assertIsNone(review["continuous_shoulder_contact_length_mm"])
        self.assertTrue(review["unresolved"])

    def test_shim_path_uses_pairwise_contacts_and_tools_follow_their_axes(self):
        stages = {row["stage"]: row for row in assembly_path_review(load_inputs())["stages"]}
        self.assertLess(stages["shim_insertion"]["maximum_unintended_volume_mm3"], 1e-6)
        self.assertEqual(4, len(stages["tool_access"]["paths"]))
        self.assertLess(stages["tool_access"]["maximum_unintended_volume_mm3"], 1e-6)

    def test_invalid_axes_and_offset_change_are_not_silently_accepted(self):
        with self.assertRaises(ValueError):
            phs_components(0, Pose("bad", 25, 0, 0))
        with self.assertRaises(ValueError):
            pocket_brackets(replace(load_inputs(), eye_offset_mm=17))

    def test_eye_insertion_checks_the_full_supplier_moving_part(self):
        stage = next(r for r in assembly_path_review(load_inputs())["stages"] if r["stage"] == "eye_approach")
        # Actual NEIGUAN volume ~48133 mm3; a short cylinder eye proxy is ~5718.
        self.assertGreater(stage.get("moving_volume_mm3", 0), 40000)
        self.assertLess(stage["maximum_unintended_volume_mm3"], 1e-6)

    def test_head_seating_overlap_is_retained_with_boolean_validity(self):
        stage = next(r for r in assembly_path_review(load_inputs())["stages"] if r["stage"] == "pin_insertion")
        witness = stage.get("maximum_witness", {})
        self.assertEqual("pin_head", witness.get("moving"))
        self.assertEqual("actual_supplier_moving_part", witness.get("obstacle"))
        self.assertEqual(0, witness.get("offset_mm"))
        self.assertIn("boolean_valid", witness)
        self.assertGreater(stage["maximum_unintended_volume_mm3"], 0.1)
        self.assertFalse(stage["nominal_sample_clear"])

    def test_assembly_path_respects_solved_neutral_yaw(self):
        stage = next(r for r in assembly_path_review(load_inputs())["stages"] if r["stage"] == "pin_insertion")
        # Neutral closure includes ~0.344 degree yaw; fixed hinge tangent is
        # consequently not platform-local Y even at zero pitch and roll.
        self.assertGreater(abs(stage["approach_from_local"][0]), 0.005)


if __name__ == "__main__":
    unittest.main()
