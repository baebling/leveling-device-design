import unittest

from cad.assembly import actuator_lengths, components_for_pose
from cad.parameters import P, POSES


class InterferenceScreeningTests(unittest.TestCase):
    def test_central_guide_opening(self):
        guide_half = P.guide_outer_size_mm / 2
        # Nearest edges of the four upper inner rails in upper_interface.py.
        self.assertGreater(120 - P.frame_size_mm / 2, guide_half)
        self.assertGreater(160 - P.frame_size_mm / 2, guide_half)

    def test_actuator_radial_separation_from_guide(self):
        for x, y in P.base_points_xy:
            radial = (x * x + y * y) ** 0.5
            stop_corner_radius = (2 * (70.0 / 2) ** 2) ** 0.5
            self.assertGreater(radial, stop_corner_radius + P.actuator_body_radius_mm + 10)

    def test_symmetric_radial_tripod(self):
        top_radii = [round((x * x + y * y) ** 0.5, 6) for x, y in P.support_points_xy]
        base_radii = [round((x * x + y * y) ** 0.5, 6) for x, y in P.base_points_xy]
        self.assertEqual(len(set(top_radii)), 1)
        self.assertEqual(len(set(base_radii)), 1)
        self.assertGreater(P.support_radius_mm, P.base_support_radius_mm)

    def test_shapes_are_valid(self):
        for component in components_for_pose(POSES["max_pitch_roll"]):
            shape = component.shape.val() if hasattr(component.shape, "val") else component.shape
            self.assertTrue(shape.isValid(), component.name)

    def test_all_named_pose_lengths_are_physical(self):
        for pose in POSES.values():
            for length in actuator_lengths(pose):
                self.assertGreater(length, 0.0)

    def test_actuators_and_center_guide_do_not_intersect(self):
        for pose_name in ("collapsed", "neutral", "raised", "max_pitch_roll"):
            components = components_for_pose(POSES[pose_name])
            by_name = {component.name: component for component in components}
            actuators = [
                component for component in components
                if component.name in {"actuator_A1", "actuator_A2", "actuator_A3"}
            ]
            guide = by_name["keyed_guide_outer"].shape
            self.assertAlmostEqual(by_name["lower_actuator_brackets"].shape.intersect(guide).Volume(), 0.0, places=6)
            for index, actuator in enumerate(actuators):
                self.assertAlmostEqual(actuator.shape.intersect(guide).Volume(), 0.0, places=6)
                for other in actuators[index + 1:]:
                    self.assertAlmostEqual(actuator.shape.intersect(other.shape).Volume(), 0.0, places=6)

    def test_actuator_envelopes_clear_detailed_yoke_structure(self):
        for pose_name in ("collapsed", "neutral", "raised", "max_pitch_roll"):
            components = components_for_pose(POSES[pose_name])
            by_name = {component.name: component.shape for component in components}
            for index in (1, 2, 3):
                actuator = by_name[f"actuator_A{index}"]
                self.assertAlmostEqual(
                    actuator.intersect(by_name["lower_actuator_brackets"]).Volume(),
                    0.0,
                    places=6,
                )
                self.assertAlmostEqual(
                    actuator.intersect(by_name["upper_radial_clevises"]).Volume(),
                    0.0,
                    places=6,
                )


if __name__ == "__main__":
    unittest.main()
