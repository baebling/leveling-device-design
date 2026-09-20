import unittest

from cad.guide_mechanism import overlap_mm
from cad.parameters import P


class DimensionTests(unittest.TestCase):
    def test_inclined_actuator_meets_collapsed_height(self):
        self.assertAlmostEqual(P.commercial_collapsed_height_mm, P.target_collapsed_height_mm)
        self.assertAlmostEqual(P.commercial_collapsed_height_mm, 270.0)
        self.assertAlmostEqual(P.commercial_raised_height_mm, 370.0)
        self.assertGreater(P.actuator_incline_from_horizontal_deg, 20.0)
        self.assertLess(P.actuator_incline_from_horizontal_deg, 35.0)

    def test_guide_overlap(self):
        self.assertGreaterEqual(overlap_mm(P.platform_joint_z_collapsed_mm + P.target_lift_mm), P.guide_min_overlap_mm)

    def test_allowed_degrees_of_freedom(self):
        self.assertEqual(("Z", "pitch", "roll"), ("Z", "pitch", "roll"))
        self.assertLessEqual(P.recommended_angle_deg, P.cardan_design_angle_deg)
        self.assertLess(P.cardan_design_angle_deg, P.cardan_hard_stop_angle_deg)
        self.assertAlmostEqual(P.gimbal_pin_stop_angle_deg, 7.0)

    def test_phase_two_concept_approval_is_recorded(self):
        self.assertEqual(P.concept_approval_date, "2026-08-26")
        self.assertEqual(P.phase_status, "PHASE_2_DETAILED_CAD_APPROVED")

    def test_jnt_br_01_seed_dimensions(self):
        self.assertEqual(P.actuator_yoke_pin_diameter_mm, 8.0)
        self.assertEqual(P.actuator_yoke_lug_thickness_mm, 8.0)
        self.assertEqual(P.actuator_yoke_inner_gap_mm, 18.0)
        self.assertEqual(P.actuator_rod_end_outer_diameter_mm, 23.0)
        self.assertEqual(P.actuator_rod_end_eye_width_mm, 11.0)


if __name__ == "__main__":
    unittest.main()
