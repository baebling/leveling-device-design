"""Regression tests for the real upper-eye/PHS6 pin centerline in Rev E."""

import math
import unittest
from itertools import product

from cad.profile_radial_reve_actual_vendor import Pose, platform_transform, upper_eye_points
from fusion_scripts.ProfileRadialRevD import revd_data


class RevEUpperPinAlignmentTests(unittest.TestCase):
    def test_tilted_pins_pass_through_both_upper_holes_without_rod_twist(self):
        """Rotating a platform-fixed 16 mm offset reproduces a pin miss."""

        for lift, pitch, roll in product(
            (0.0, 25.0, 50.0), (-3.0, 0.0, 3.0), (-3.0, 0.0, 3.0)
        ):
            pose = Pose("pin_grid", lift, pitch, roll)
            rotation, translation, solved = platform_transform(pose)
            self.assertLess(solved["residual_mm"], 1e-6)

            for lower, support, (_, tangent), eye in zip(
                revd_data.lower_eye_points(),
                revd_data.upper_support_points(),
                revd_data.support_basis(),
                upper_eye_points(pose),
            ):
                source_phs = (support[0], support[1], revd_data.P.upper_ring_z_collapsed_mm)
                phs = tuple(
                    sum(rotation[row][col] * source_phs[col] for col in range(3))
                    + translation[row]
                    for row in range(3)
                )
                eye_to_phs = tuple(phs[row] - eye[row] for row in range(3))
                along_pin = sum(eye_to_phs[row] * tangent[row] for row in range(3))
                perpendicular = math.sqrt(
                    sum((eye_to_phs[row] - along_pin * tangent[row]) ** 2 for row in range(3))
                )
                leg_tangent_error = sum(
                    (eye[row] - lower[row]) * tangent[row] for row in range(3)
                )

                with self.subTest(lift=lift, pitch=pitch, roll=roll):
                    self.assertAlmostEqual(along_pin, 16.0, places=6)
                    self.assertLess(perpendicular, 1e-6)
                    self.assertLess(abs(leg_tangent_error), 1e-6)


if __name__ == "__main__":
    unittest.main()
