import unittest

from calculations.user_confirmed_baseline import (
    USER_CONFIRMED_ANGLE_DEG,
    USER_CONFIRMED_EMPTY_CART_MASS_KG,
    USER_CONFIRMED_PAYLOAD_KG,
    actuator_force_screen,
    central_yaw_screen,
    summary,
)


class UserConfirmedBaselineTests(unittest.TestCase):
    def test_user_confirmed_scope_is_low_load_three_degrees(self):
        result = summary()["user_decision"]
        self.assertEqual(result["material_payload_kg"], USER_CONFIRMED_PAYLOAD_KG)
        self.assertEqual(result["empty_cart_mass_kg"], USER_CONFIRMED_EMPTY_CART_MASS_KG)
        self.assertEqual(result["pitch_roll_required_deg"], USER_CONFIRMED_ANGLE_DEG)
        self.assertEqual(result["disconnected_device_height_range_mm"], (250.0, 300.0))

    def test_baseline_actuator_force_passes_firgelli_screen(self):
        result = actuator_force_screen()
        self.assertEqual(result["material_payload_kg"], 10.0)
        self.assertEqual(result["cart_mass_kg"], 10.0)
        self.assertEqual(result["total_lifted_mass_kg"], 42.0)
        self.assertEqual(result["angle_deg"], 3.0)
        self.assertTrue(result["passes_firgelli_450_lbf"])
        self.assertGreater(result["force_margin_to_firgelli"], 3.0)

    def test_df2_and_eccentricity_sensitivities_still_pass(self):
        result = summary()
        self.assertTrue(result["df2_actuator_force_sensitivity"]["passes_firgelli_450_lbf"])
        self.assertTrue(result["ecc100_actuator_force_sensitivity"]["passes_firgelli_450_lbf"])
        self.assertTrue(result["heavy_cart_actuator_force_sensitivity"]["passes_firgelli_450_lbf"])
        self.assertEqual(result["heavy_cart_actuator_force_sensitivity"]["cart_mass_kg"], 30.0)

    def test_baseline_yaw_torque_is_much_lower_than_old_conservative_case(self):
        baseline = central_yaw_screen()
        self.assertEqual(baseline["cart_mass_kg"], 10.0)
        self.assertLess(baseline["required_design_yaw_torque_nm"], 20.0)
        self.assertLess(
            baseline["required_design_yaw_torque_nm"],
            summary()["conservative_yaw_torque_sensitivity"]["required_design_yaw_torque_nm"],
        )


if __name__ == "__main__":
    unittest.main()
