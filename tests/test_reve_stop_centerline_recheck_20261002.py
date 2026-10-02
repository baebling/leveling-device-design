"""Review-only centerline stop screen for the current raised Rev E frame.

This does not model an actual post, contact patch, fasteners, deformation,
internal actuator limits, or a swept collision.  It prevents reuse of the
previous 8-11 mm stop-window values from an inconsistent Z datum.
"""

from itertools import product
import unittest

import cadquery as cq

from cad.profile_radial_reve_actual_vendor import (
    Pose,
    _screened_intersection_volume,
    actuator_pin_lengths,
    group_shape,
    platform_transform,
    transform_upper_frame_shape,
)


POST_XY_MM = ((-35.0, 250.0), (-196.506, -140.0), (236.506, -110.0))
LOWER_PROFILE_TOP_Z_MM = 40.0
UPPER_PROFILE_BOTTOM_Z_MM = 285.0  # 270 mm Rev D + 15 mm Rev E frame rise
ACTUATOR_NOMINAL_HARD_PIN_MM = 205.0


def centerline_first_touch(pitch_deg: float, roll_deg: float, post_length_mm: float):
    """Return first fixed-angle Z contact and all three pin lengths there."""

    pose = Pose("screen", 0.0, pitch_deg, roll_deg)
    rotation, translation, _ = platform_transform(pose)
    post_top_z = LOWER_PROFILE_TOP_Z_MM + post_length_mm
    underside_z = [
        sum(rotation[2][axis] * point[axis] for axis in range(3))
        + translation[2]
        for x, y in POST_XY_MM
        for point in ((x, y, UPPER_PROFILE_BOTTOM_Z_MM),)
    ]
    # On a fixed-angle descent from Z=0, the highest contact Z occurs first.
    touch_z = max(post_top_z - z for z in underside_z)
    touch_pose = Pose("first_touch", touch_z, pitch_deg, roll_deg)
    return touch_z, actuator_pin_lengths(touch_pose)


class StopCenterlineRecheck(unittest.TestCase):
    def test_perimeter_post_centerline_overstates_real_clearance(self):
        post = (
            cq.Workplane("XY")
            .box(40.0, 40.0, 230.5, centered=(True, True, False))
            .translate((330.0, 0.0, LOWER_PROFILE_TOP_Z_MM))
            .val()
        )
        upper = transform_upper_frame_shape(
            group_shape("upper_frame"), Pose("Z5_corner", 5.0, 3.0, 3.0)
        )
        self.assertAlmostEqual(post.distance(upper), 0.0691183966170902, places=5)
        self.assertEqual(_screened_intersection_volume(post, upper), 0.0)

    def test_proposed_lower_4080_bridge_hits_existing_adapters(self):
        bridge = (
            cq.Workplane("XY")
            .box(620.0, 80.0, 40.0)
            .translate((0.0, -120.0, 60.0))
            .val()
        )
        overlap_mm3 = _screened_intersection_volume(
            bridge, group_shape("lower_adapters")
        )
        self.assertAlmostEqual(overlap_mm3, 8695.07362067945, places=2)

    def test_post_footprints_have_no_bearing_on_existing_lower_profiles(self):
        """The three hypothetical 40 x 40 posts lack a supporting 4040 beam."""

        profile_boxes = [solid.BoundingBox() for solid in group_shape("lower_frame").Solids()]
        for x, y in POST_XY_MM:
            with self.subTest(post_xy=(x, y)):
                contact_areas = [
                    max(0.0, min(x + 20.0, box.xmax) - max(x - 20.0, box.xmin))
                    * max(0.0, min(y + 20.0, box.ymax) - max(y - 20.0, box.ymin))
                    for box in profile_boxes
                ]
                self.assertEqual(max(contact_areas), 0.0)

    def test_full_angle_grid_centerline_window(self):
        cases = (
            (222.0, 1.7874425616076905, -11.658877519727639),
            (220.0, 0.46519448043491707, -13.658877519727639),
        )
        angles = [-3.0 + step * 0.25 for step in range(25)]
        for post_length_mm, expected_window_mm, expected_touch_z_mm in cases:
            with self.subTest(post_length_mm=post_length_mm):
                results = []
                for pitch_deg, roll_deg in product(angles, repeat=2):
                    touch_z, lengths = centerline_first_touch(
                        pitch_deg, roll_deg, post_length_mm
                    )
                    results.append(
                        (min(lengths) - ACTUATOR_NOMINAL_HARD_PIN_MM,
                         pitch_deg, roll_deg, touch_z)
                    )
                minimum = min(results)
                self.assertAlmostEqual(minimum[0], expected_window_mm, places=6)
                self.assertEqual(minimum[1:3], (3.0, -3.0))
                self.assertAlmostEqual(minimum[3], expected_touch_z_mm, places=6)
                self.assertTrue(all(row[3] < 0.0 for row in results))

    def test_old_222_mm_window_cannot_be_reused(self):
        _, lengths = centerline_first_touch(3.0, -3.0, 222.0)
        self.assertLess(lengths[0] - ACTUATOR_NOMINAL_HARD_PIN_MM, 2.0)


if __name__ == "__main__":
    unittest.main()
