import unittest

import cadquery as cq

from cad.assembly import components_for_pose
from cad.parameters import P, POSES
from calculations.actuator_limit_package_screen import (
    package_positions,
    static_package_screen,
    switch_candidate,
    vendor_mount_datum_screen,
)


class ActuatorLimitPackageScreenTests(unittest.TestCase):
    def test_length_hierarchy_maps_to_twin_rod_offsets(self):
        result = package_positions()
        self.assertEqual(
            (
                result["lower_mechanical_collar_offset_from_crosshead_mm"],
                result["lower_electrical_cam_offset_from_crosshead_mm"],
                result["upper_electrical_cam_offset_from_crosshead_mm"],
                result["upper_mechanical_collar_offset_from_crosshead_mm"],
            ),
            (104.0, 109.0, 293.0, 298.0),
        )
        self.assertTrue(result["upper_collar_fits_on_rod"])

    def test_mb21_envelope_fits_step_derived_body_zone(self):
        result = vendor_mount_datum_screen()
        self.assertTrue(result["mb21_inside_source_step_body_zone"])
        self.assertAlmostEqual(result["source_step_pin_span_mm"], 318.017, places=3)
        self.assertGreater(result["far_end_reserve_mm"], 15.0)
        self.assertIn("chrome rod", result["moving_adapter_rule"])

    def test_electrical_cams_keep_precontact_allowance(self):
        result = package_positions()
        self.assertEqual(result["electrical_to_mechanical_allowance_lower_mm"], 5.0)
        self.assertEqual(result["electrical_to_mechanical_allowance_upper_mm"], 5.0)
        self.assertIn("electrical cam", result["sequence"])

    def test_static_screen_does_not_claim_impact_capacity(self):
        result = static_package_screen()
        self.assertGreater(result["design_package_static_load_n"], 800.0)
        self.assertLess(result["guide_rod_axial_stress_mpa"], 5.0)
        self.assertLess(result["collar_face_contact_pressure_mpa"], 1.0)
        self.assertGreater(
            result["minimum_verified_axial_holding_per_collar_n"],
            result["equal_share_load_per_rod_n"],
        )
        self.assertIn("impact energy", result["warning"])

    def test_switch_seed_preserves_travel_and_adjustment(self):
        result = switch_candidate()
        self.assertEqual(result["family"], "Omron D4N")
        self.assertFalse(result["active_in_current_variant"])
        self.assertEqual(result["catalogue_pretravel_max_mm"], 2.0)
        self.assertEqual(result["catalogue_overtravel_min_mm"], 4.0)
        self.assertGreaterEqual(result["bracket_adjustment_each_direction_mm"], 5.0)

    def test_each_actuator_has_complete_ls01_component_set(self):
        components = components_for_pose(POSES["neutral"])
        names = {component.name for component in components}
        suffixes = {
            "limit_fixed_carrier",
            "limit_guide_bushings",
            "limit_moving_striker",
            "external_mechanical_stops",
        }
        for index in (1, 2, 3):
            self.assertTrue({f"actuator_A{index}_{suffix}" for suffix in suffixes} <= names)
            self.assertNotIn(f"actuator_A{index}_electrical_limits", names)

    def test_ls01_components_are_valid_and_symmetric(self):
        components = components_for_pose(POSES["collapsed"])
        volume_sets = []
        for index in (1, 2, 3):
            package = [
                component for component in components
                if component.name.startswith(f"actuator_A{index}_")
                and component.name != f"actuator_A{index}"
            ]
            self.assertEqual(len(package), 4)
            for component in package:
                self.assertTrue(component.shape.isValid(), component.name)
            volume_sets.append(tuple(sorted(round(component.shape.Volume(), 3) for component in package)))
        self.assertEqual(len(set(volume_sets)), 1)

    def test_ls01_package_clears_actuator_and_primary_structures(self):
        for pose_name in ("collapsed", "neutral", "raised", "max_pitch_roll"):
            components = components_for_pose(POSES[pose_name])
            by_name = {component.name: component.shape for component in components}
            for index in (1, 2, 3):
                package_shapes = [
                    shape for name, shape in by_name.items()
                    if name.startswith(f"actuator_A{index}_")
                    and name != f"actuator_A{index}"
                ]
                package = cq.Compound.makeCompound(package_shapes)
                for target in (
                    f"actuator_A{index}",
                    "keyed_guide_outer",
                    "lower_actuator_brackets",
                    "upper_radial_clevises",
                ):
                    self.assertAlmostEqual(
                        package.intersect(by_name[target]).Volume(),
                        0.0,
                        places=6,
                        msg=f"{pose_name} A{index} vs {target}",
                    )


if __name__ == "__main__":
    unittest.main()
