import unittest

from cad.parameters import P, Pose
from calculations.actuator_geometry import actuator_lengths, transform_point


class ActuatorGeometryTests(unittest.TestCase):
    def test_level_collapsed_lengths_match_selected_geometry(self):
        lengths = actuator_lengths(Pose(0.0, 0.0, 0.0, True, "level"))
        self.assertEqual(len(lengths), 3)
        for length in lengths:
            self.assertAlmostEqual(length, P.actuator_level_length_at_lift0_mm, places=8)

    def test_transform_uses_project_roll_then_pitch_convention(self):
        result = transform_point((0.0, 1.0, 0.0), Pose(0.0, 0.0, 90.0), 0.0)
        self.assertAlmostEqual(result[0], 0.0, places=9)
        self.assertAlmostEqual(result[1], 0.0, places=9)
        self.assertAlmostEqual(result[2], 1.0, places=9)

    def test_lengths_stay_positive_in_user_operating_grid(self):
        for pitch in (-3.0, 0.0, 3.0):
            for roll in (-3.0, 0.0, 3.0):
                self.assertTrue(all(length > 0.0 for length in actuator_lengths(Pose(100.0, pitch, roll))))


if __name__ == "__main__":
    unittest.main()
