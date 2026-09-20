import unittest

from cad.navimro_fabrication_parameters import N, NAVIMRO_POSES, actuator_lengths
from cad.navimro_fabrication_exports import FLATBAR_PARTS, flatbar_usage_mm
from cad.navimro_fabrication_assembly import components_for_pose


class NavimroFabricationTests(unittest.TestCase):
    def test_disconnected_height_matches_user_window(self):
        self.assertGreaterEqual(N.disconnected_height_mm, 250.0)
        self.assertLessEqual(N.disconnected_height_mm, 300.0)

    def test_all_named_pose_lengths_fit_provisional_pin_envelope(self):
        for name, pose in NAVIMRO_POSES.items():
            with self.subTest(name=name):
                for length in actuator_lengths(pose):
                    self.assertGreaterEqual(length, N.actuator_min_pin_length_mm)
                    self.assertLessEqual(length, N.actuator_max_pin_length_mm)

    def test_full_workspace_corners_fit_provisional_pin_envelope(self):
        pose_type = type(NAVIMRO_POSES["neutral"])
        for lift in (0.0, N.lift_mm):
            for pitch in (-N.max_angle_deg, N.max_angle_deg):
                for roll in (-N.max_angle_deg, N.max_angle_deg):
                    pose = pose_type("corner", lift, pitch, roll)
                    for length in actuator_lengths(pose):
                        self.assertGreaterEqual(length, N.actuator_min_pin_length_mm)
                        self.assertLessEqual(length, N.actuator_max_pin_length_mm)

    def test_angle_and_lift_are_user_confirmed_values(self):
        self.assertEqual(N.max_angle_deg, 3.0)
        self.assertEqual(N.lift_mm, 100.0)
        self.assertEqual(N.payload_kg, 10.0)
        self.assertEqual(N.cart_mass_kg, 10.0)

    def test_flatbar_parts_fit_purchased_stock(self):
        cut, kerf, reserve = flatbar_usage_mm()
        self.assertGreater(cut, 0.0)
        self.assertGreaterEqual(reserve, 6000.0)
        self.assertLessEqual(cut + kerf, N.flatbar_stock_length_mm * N.flatbar_stock_count)

    def test_vendor_interfaces_are_transfer_drilled(self):
        transfer_parts = {part.part_no for part in FLATBAR_PARTS if part.vendor_holes == "YES"}
        self.assertEqual(transfer_parts, {"NVR-P06", "NVR-P09", "NVR-P11", "NVR-P12"})

    def test_moving_shafts_remain_fully_engaged_in_fixed_bushings(self):
        for lift in (0.0, N.lift_mm):
            platform_z = N.collapsed_joint_z_mm + lift
            shaft_top = platform_z + N.guide_shaft_top_offset_mm
            shaft_bottom = shaft_top - N.guide_shaft_length_mm
            for center in (N.fixed_bushing_lower_z_mm, N.fixed_bushing_upper_z_mm):
                self.assertLessEqual(shaft_bottom, center - 15.0)
                self.assertGreaterEqual(shaft_top, center + 15.0)

    def test_independent_Z_stops_match_command_endpoints(self):
        self.assertEqual(N.collapsed_joint_z_mm - 165.0, 70.0)
        self.assertEqual(N.collapsed_joint_z_mm + N.lift_mm - 125.0, 210.0)

    def test_collapsed_component_shapes_are_valid(self):
        for component in components_for_pose(NAVIMRO_POSES["collapsed"]):
            shape = component.shape.val() if hasattr(component.shape, "val") else component.shape
            self.assertTrue(shape.isValid(), component.name)


if __name__ == "__main__":
    unittest.main()
