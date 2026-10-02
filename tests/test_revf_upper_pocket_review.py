"""Review geometry tests; passing these does not release fabrication."""
import unittest
from dataclasses import replace
from itertools import product
from unittest.mock import patch
import cadquery as cq
import cad.profile_radial_revf_upper_pocket_review as review_module

from cad.revf_upper_pocket_inputs import load_inputs
from cad.profile_radial_reve_actual_vendor import Pose, upper_eye_points, platform_transform, _rigid_transform
from cad.profile_radial_revf_upper_pocket_review import (
    pocket_brackets, phs_components, revf_components_for_pose,
    joint_reference, assembly_path_review, local_review_geometry,
)


class UpperPocketReviewTests(unittest.TestCase):
    def test_trusco_foot_blind_thread_and_m6_candidate_are_explicit(self):
        geo=local_review_geometry(load_inputs())
        # Probe the widened foot outside the old radius5 neck.
        probe=review_module._box(.2,.2,1,(6,0,27))
        self.assertGreater(geo['housing'].intersect(probe).Volume(),.03)
        self.assertLess(geo['housing'].intersect(review_module._cylinder(2.9,11.9,(0,0,18.1))).Volume(),1e-6)
        bolt=geo['m6_retainer_envelope'].BoundingBox()
        self.assertAlmostEqual(bolt.zmin,21.)
        self.assertAlmostEqual(bolt.zmax,39.)
        review=review_module.hardware_review(load_inputs())
        self.assertEqual(review['m6_retainer']['nominal_engagement_mm'],9.)
        self.assertEqual(review['m6_retainer']['status'],'UNKNOWN/HOLD')
        self.assertFalse(review['grease_nipple']['supplier_bound_verified'])
        for axis in (1,2,3):
            g=local_review_geometry(load_inputs(),axis)
            for offset in (0,.1,1,5,10,20,40):
                for key in ('housing','grease_nipple_unknown_envelope'):
                    common=g[key].translate((0,offset,0)).intersect(g['bracket'])
                    self.assertTrue(common.isValid());self.assertLess(common.Volume(),1e-6)

    def test_stock_ring_pin_has_head_washer_then_eye_shims_ball_ring(self):
        geo=local_review_geometry(load_inputs())
        self.assertFalse(any('m5' in key for key in geo))
        self.assertEqual(len(geo['shim'].Solids()),1)
        self.assertAlmostEqual(geo['shim'].BoundingBox().xlen,10.)
        head=geo['pin_head'].BoundingBox();washer=geo['spacer'].BoundingBox()
        self.assertAlmostEqual(head.xlen,9.)
        self.assertAlmostEqual(head.ylen,1.5)
        self.assertAlmostEqual(washer.ymin,-30.)
        self.assertAlmostEqual(washer.ymax,-26.)
        self.assertAlmostEqual(geo['e5_ring_envelope'].BoundingBox().ymin,5.)
        review=review_module.hardware_review(load_inputs())
        self.assertAlmostEqual(review['pin_stack']['nominal_groove_gap_mm'],.5)
        self.assertAlmostEqual(review['pin_stack']['known_tolerance_max_gap_mm'],.82)
        self.assertAlmostEqual(review['pin_stack']['known_tolerance_min_gap_mm'],.20)
        self.assertEqual(review['pin_stack']['fit_status'],'UNKNOWN')
        self.assertEqual(review['pin_transition_coverage']['status'],'EXCLUDED/UNKNOWN')
        self.assertFalse(review['pin_transition_coverage']['exact_geometry_checked'])

    def test_ball_side_stock_washer_clears_neck_at_all_representative_poses(self):
        for lift,pitch,roll in product((0,25,50),(-3,0,3),(-3,0,3)):
            for axis in (1,2,3):
                g=phs_components(axis,Pose('washer',lift,pitch,roll))
                common=g['shim'].intersect(g['housing'])
                self.assertTrue(common.isValid())
                self.assertLess(common.Volume(),1e-6)

    def test_composite_paths_do_not_turn_all_invalid_children_into_zero(self):
        self.assertTrue(callable(getattr(review_module, '_aggregate_paths', None)))
        invalid = cq.Workplane('XY').box(1, 1, 1).val()
        with patch.object(cq.Shape, 'isValid', return_value=False), patch.object(cq.Shape, 'Volume', return_value=0):
            child = review_module._path_measurements({'a': invalid, 'b': invalid}, ['a'], (0, 0, 1), ['b'], 0)
        aggregate = review_module._aggregate_paths([child, child])
        self.assertIsNone(aggregate['maximum_unintended_volume_mm3'])
        self.assertIsNone(aggregate['maximum_valid_volume_mm3'])
        self.assertEqual(18, aggregate['invalid_boolean_count'])
        self.assertEqual(18, len(aggregate['invalid_witnesses']))
        self.assertEqual('UNKNOWN', aggregate['status'])
        self.assertFalse(aggregate['nominal_sample_clear'])
        # Exercise both real composite-stage consumers under the same fault.
        with patch.object(review_module, '_path_measurements', side_effect=lambda *a, **k: dict(child)):
            stages = review_module._axis_assembly_path_review(load_inputs(), 1)
        for row in stages:
            if row['stage'] in ('tnut_end_insertion', 'tool_access'):
                self.assertIsNone(row['maximum_unintended_volume_mm3'])
                self.assertEqual(9 * len(row['paths']), row['invalid_boolean_count'])
                self.assertEqual(row['invalid_boolean_count'], len(row['invalid_witnesses']))
                self.assertEqual('UNKNOWN', row['status'])

    def test_mounts_follow_crossmember_x_while_holes_and_tools_remain_z(self):
        # Catches radial bolt patterns, rotated pin cores and world-fixed mounts.
        for pose in (Pose('collapsed', 0, 0, 0), Pose('tilted', 25, 3, -3)):
            rotation, _, _ = platform_transform(pose)
            inverse = tuple(zip(*rotation))
            parts = revf_components_for_pose(pose, load_inputs())
            for axis in (1, 2, 3):
                center = joint_reference(axis, pose)['ball_center']
                translation = tuple(-sum(row[k] * center[k] for k in range(3)) for row in inverse)
                for index, x in ((1, -22), (2, 22)):
                    bolt = next(p.shape for p in parts if p.name == f'A{axis}_REVF_mount_bolt_{index}_envelope')
                    local = _rigid_transform(bolt, inverse, translation)
                    bb = local.BoundingBox()
                    self.assertAlmostEqual(x, (bb.xmin + bb.xmax)/2, places=6)
                    self.assertAlmostEqual(0, (bb.ymin + bb.ymax)/2, places=6)
                    self.assertAlmostEqual(24, bb.zmin, places=6)
                    self.assertAlmostEqual(46.5, bb.zmax, places=6)
                    self.assertAlmostEqual(10, bb.xlen, places=6)
                    self.assertAlmostEqual(10, bb.ylen, places=6)
                    bracket = next(p.shape for p in parts if p.name == f'A{axis}_REVF_POCKET_REVIEW_NOT_FOR_FABRICATION')
                    hole_clearance = bolt.intersect(bracket)
                    self.assertTrue(hole_clearance.isValid())
                    self.assertLess(hole_clearance.Volume(), 1e-6)
                    tool = review_module._place(local_review_geometry(load_inputs(), axis)[f'mount_tool_{index}_envelope'], axis, pose)
                    tb = _rigid_transform(tool, inverse, translation).BoundingBox()
                    self.assertAlmostEqual(x, (tb.xmin + tb.xmax)/2, places=6)
                    self.assertAlmostEqual(0, (tb.ymin + tb.ymax)/2, places=6)
                    self.assertAlmostEqual(40, tb.zlen, places=6)
                    self.assertAlmostEqual(6, tb.xlen, places=6)
                    self.assertAlmostEqual(6, tb.ylen, places=6)
                    nut = next(p.shape for p in parts if p.name == f'A{axis}_REVF_tnut_{index}_UNVERIFIED_SLOT')
                    nb = _rigid_transform(nut, inverse, translation).BoundingBox()
                    self.assertAlmostEqual(23, nb.xlen, places=6)
                    self.assertAlmostEqual(10, nb.ylen, places=6)

    def test_reoriented_brackets_are_connected_and_coposed_to_frame(self):
        for pose in (Pose('collapsed', 0, 0, 0), Pose('tilt', 50, -3, 3)):
            parts = revf_components_for_pose(pose, load_inputs())
            for bracket in (p for p in parts if p.group == 'upper_pockets'):
                self.assertTrue(bracket.shape.isValid())
                self.assertEqual(1, len(bracket.shape.Solids()))
                for frame in (p for p in parts if p.group in ('upper_frame', 'upper_brackets')):
                    common = bracket.shape.intersect(frame.shape)
                    self.assertTrue(common.isValid())
                    self.assertLess(common.Volume(), 1e-6)
                self.assertLess(bracket.shape.distance(next(p.shape for p in parts if p.group == 'upper_frame')), 1e-6)

    def test_axis_assembly_stages_respect_frame_and_eye_installation_order(self):
        report = assembly_path_review(load_inputs())
        self.assertEqual({1, 2, 3}, {r.get('axis') for r in report['stages']})
        for axis in (1, 2, 3):
            stages = [r for r in report['stages'] if r['axis'] == axis]
            by_name = {r['stage']: r for r in stages}
            self.assertNotIn('upper_frame', by_name['m6_retention']['obstacles'])
            self.assertIn('upper_frame', by_name['eye_approach']['obstacles'])
            self.assertIn('upper_frame', by_name['profile_attachment']['obstacles'])
            self.assertLess(stages.index(by_name['profile_attachment']), stages.index(by_name['eye_approach']))
            route = by_name['tnut_end_insertion']
            self.assertEqual('BEFORE_CROSSMEMBER_ENDS_CLOSED', route['assembly_phase'])
            self.assertIn('isolated_crossmember', route['obstacles'])
            self.assertEqual('UNKNOWN', route['status'])
            self.assertEqual('UNKNOWN', by_name['pin_insertion']['status'])
            mount_tools = [p for p in by_name['tool_access']['paths'] if p['moving'][0].startswith('mount_tool')]
            self.assertTrue(all(p['approach_from_local'] == (0, 0, -1) for p in mount_tools))
            self.assertTrue(all('actual_supplier_moving_part' not in p['obstacles'] for p in mount_tools))
        self.assertEqual('UNKNOWN/HOLD', report['slot_review']['status'])
        self.assertAlmostEqual(0.6, report['slot_review']['model_floor_overlap_mm'])

    def test_any_invalid_boolean_prevents_nominal_clear_even_when_volume_zero(self):
        # OCC invalid common with zero reported volume must not become clear.
        invalid = cq.Workplane('XY').box(1, 1, 1).val()
        self.assertTrue(callable(getattr(review_module, '_path_measurements', None)))
        with patch.object(cq.Shape, 'isValid', return_value=False), patch.object(cq.Shape, 'Volume', return_value=0):
            row = review_module._path_measurements({'a': invalid, 'b': invalid}, ['a'], (0, 0, 1), ['b'], 0)
        self.assertEqual(0, row['maximum_unintended_volume_mm3'])
        self.assertFalse(row['nominal_sample_clear'])
        self.assertGreater(row['invalid_boolean_count'], 0)
        self.assertEqual('UNKNOWN', row['status'])

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
        # A1 mounting base now runs tangent/frame X, while its saddle stays fixed.
        self.assertAlmostEqual(60, geo["bracket"].BoundingBox().ylen, places=6)

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
        self.assertEqual({"tnut_end_insertion", "bracket_approach", "housing_insertion", "m6_retention", "eye_approach", "pin_insertion", "shim_insertion", "head_washer_preload", "e5_ring_installation", "profile_attachment", "tool_access"}, {r["stage"] for r in review["stages"]})
        self.assertTrue(all(r["samples"] > 1 for r in review["stages"]))
        self.assertTrue(all("maximum_unintended_volume_mm3" in r for r in review["stages"]))
        self.assertFalse(review["assembly_verified"])
        self.assertFalse(review["fabrication_release"])
        self.assertFalse(review["purchase_release"])
        self.assertEqual(34.5, review["nominal_grip_mm"])
        self.assertEqual(30.5, review['nominal_eye_shim_ball_stack_mm'])
        self.assertIsNone(review["continuous_shoulder_contact_length_mm"])
        self.assertTrue(review["unresolved"])

    def test_shim_path_uses_pairwise_contacts_and_tools_follow_their_axes(self):
        stages = {row["stage"]: row for row in assembly_path_review(load_inputs())["stages"]}
        self.assertLess(stages["shim_insertion"]["maximum_unintended_volume_mm3"], 1e-6)
        self.assertEqual(4, len(stages["tool_access"]["paths"]))
        self.assertEqual(stages['tool_access']['status'],'UNKNOWN')

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
        self.assertIn(witness.get('moving'),('pin_head','spacer','pin_shoulder'))
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
