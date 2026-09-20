import unittest

from cad.navimro_pin_lug_gimbal import components


class NavimroPinLugGimbalTests(unittest.TestCase):
    def test_assumption_seed_is_valid_and_keeps_orthogonal_axes(self):
        rows = components()
        self.assertEqual(len(rows), 5)
        for row in rows:
            self.assertTrue(row.shape.isValid(), row.name)

        by_name = {row.name: row.shape for row in rows}
        eye_pin = by_name["navimro_assumed_6mm_eye_pin"].BoundingBox()
        trunnions = by_name["navimro_opposed_m8_trunnions"].BoundingBox()
        self.assertGreater(eye_pin.ylen, eye_pin.zlen)
        self.assertGreater(trunnions.zlen, trunnions.ylen)
        self.assertAlmostEqual(
            by_name["navimro_m8_eye_adapter_assumption"].intersect(
                by_name["navimro_6mm_u_bracket_assumption"]
            ).Volume(),
            0.0,
            places=6,
        )


if __name__ == "__main__":
    unittest.main()
