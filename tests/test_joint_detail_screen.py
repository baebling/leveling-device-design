import unittest

from calculations.joint_detail_screen import (
    actuator_package_screen,
    central_cardan_torque_screen,
    square_tube_torsion_screen,
    yaw_torque_case,
)


class JointDetailScreenTests(unittest.TestCase):
    def test_actuator_stud_bending_blocks_offset_package(self):
        rows = {row["candidate"]: row for row in actuator_package_screen(5.0)}
        rbld8 = rows["MISUMI_RBLD8_style_link_ball"]
        rbld12 = rows["MISUMI_RBLD12_style_link_ball"]

        self.assertTrue(rbld8["pin_shear_ok"])
        self.assertTrue(rbld8["lug_bearing_ok"])
        self.assertFalse(rbld8["cantilevered_stud_bending_ok"])
        self.assertLess(rbld8["max_cantilever_standoff_for_allowable_bending_mm"], 5.0)

        self.assertTrue(rbld12["pin_shear_ok"])
        self.assertTrue(rbld12["lug_bearing_ok"])
        self.assertTrue(rbld12["cantilevered_stud_bending_ok"])
        self.assertLess(rbld12["cantilevered_stud_bending_stress_mpa"], 150.0)
        self.assertLess(rbld12["cantilevered_stud_bending_stress_mpa"], rbld8["cantilevered_stud_bending_stress_mpa"])

    def test_small_cardan_skus_fail_conservative_yaw_torque(self):
        torque = yaw_torque_case()
        self.assertGreater(torque["yaw_torque_nm"], 120.0)
        self.assertGreater(torque["required_peak_or_design_torque_nm"], 240.0)

        rows = central_cardan_torque_screen(5.0)
        self.assertTrue(all(row["angle_ok"] for row in rows))
        self.assertTrue(all(row["screen_result"] == "FAIL_TORQUE_SCREEN" for row in rows))

    def test_square_tube_torsion_reference_is_not_primary_blocker(self):
        result = square_tube_torsion_screen()
        self.assertLess(result["thin_wall_torsional_shear_mpa"], 20.0)
        self.assertLess(result["estimated_twist_deg"], 0.5)


if __name__ == "__main__":
    unittest.main()
