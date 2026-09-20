import unittest

from cad.actuator_placeholder import make_radial_limit_components
from cad.actuator_joint import articulation_clearance_mm, lower_components, upper_components
from cad.common import platform_center_z, transform_point
from cad.guide_mechanism import compact_cardan_components
from cad.parameters import P, POSES


class RadialTripodGeometryTests(unittest.TestCase):
    def test_active_variant_is_clean_three_actuator_radial_layout(self):
        self.assertEqual(P.design_variant, "RADIAL_3_CLEAN")
        self.assertEqual(len(P.support_points_xy), 3)
        self.assertEqual(len(P.base_points_xy), 3)

    def test_compact_cardan_keeps_required_motion_bodies(self):
        pose = POSES["max_pitch_roll"]
        components = compact_cardan_components(pose, platform_center_z(pose))
        self.assertEqual(
            [component.name for component in components],
            [
                "compact_cardan_lower",
                "compact_cardan_cross",
                "compact_cardan_upper",
                "compact_cardan_angle_stops",
            ],
        )
        for component in components:
            self.assertTrue(component.shape.isValid(), component.name)
        upper_box = components[2].shape.BoundingBox()
        self.assertLessEqual(upper_box.xlen, 125.0)
        self.assertLessEqual(upper_box.ylen, 125.0)

    def test_gimbal_stop_definition_preserves_total_tilt_envelope(self):
        diagonal_tilt_deg = (2.0 * P.gimbal_pin_stop_angle_deg ** 2) ** 0.5
        self.assertLess(diagonal_tilt_deg, P.cardan_hard_stop_angle_deg)

    def test_static_bench_variant_keeps_mechanical_stops_without_external_d4n(self):
        pose = POSES["collapsed"]
        platform_z = platform_center_z(pose)
        volumes = []
        for index, ((x, y), (bx, by)) in enumerate(
            zip(P.support_points_xy, P.base_points_xy), start=1
        ):
            base = (bx, by, P.base_joint_z_mm)
            top = transform_point((x, y, 0.0), pose, platform_z)
            components = make_radial_limit_components(base, top, f"actuator_A{index}")
            names = {component.name for component in components}
            self.assertIn(f"actuator_A{index}_external_mechanical_stops", names)
            self.assertNotIn(f"actuator_A{index}_electrical_limits", names)
            for component in components:
                self.assertTrue(component.shape.isValid(), component.name)
            volumes.append(tuple(round(component.shape.Volume(), 6) for component in components))
        self.assertEqual(len(set(volumes)), 1)
        self.assertEqual(P.prototype_operating_mode, "STATIC_BENCH_LOW_SPEED")
        self.assertFalse(P.external_electrical_limit_package_enabled)
        self.assertTrue(P.external_mechanical_stops_enabled)

    def test_detailed_actuator_joint_packages_are_valid_and_retained(self):
        lower = lower_components()
        upper = upper_components(POSES["max_pitch_roll"])
        expected = {
            "lower_actuator_brackets",
            "lower_actuator_bushings",
            "lower_actuator_misalignment_spacers",
            "lower_actuator_pins_retention",
            "upper_radial_clevises",
            "upper_actuator_bushings",
            "upper_actuator_misalignment_spacers",
            "upper_actuator_pins_retention",
        }
        self.assertEqual({c.name for c in lower + upper}, expected)
        for component in lower + upper:
            self.assertTrue(component.shape.isValid(), component.name)
        self.assertGreater(articulation_clearance_mm(), 1.0)


if __name__ == "__main__":
    unittest.main()
