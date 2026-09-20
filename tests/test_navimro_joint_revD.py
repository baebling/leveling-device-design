import unittest

from cad.navimro_detailed_assembly import detailed_components
from cad.navimro_fabrication_parameters import N, NAVIMRO_POSES
from calculations.navimro_joint_revD_screen import (
    kinematic_screen,
    local_strength_screen,
)


def _shape(part):
    return part.shape.val() if hasattr(part.shape, "val") else part.shape


def _bounding_boxes_overlap(first, second, tolerance=1e-6):
    a = _shape(first).BoundingBox()
    b = _shape(second).BoundingBox()
    return (
        a.xmin < b.xmax - tolerance
        and a.xmax > b.xmin + tolerance
        and a.ymin < b.ymax - tolerance
        and a.ymax > b.ymin + tolerance
        and a.zmin < b.zmax - tolerance
        and a.zmax > b.zmin + tolerance
    )


class NavimroJointRevDTests(unittest.TestCase):
    def test_navimro_catalog_rod_end_is_the_active_joint(self):
        self.assertEqual(N.rod_end_model, "JFT-8R")
        self.assertEqual(N.rod_end_bore_mm, 8.0)
        self.assertEqual(N.rod_end_outer_diameter_mm, 24.0)
        self.assertEqual(N.rod_end_allowable_angle_deg, 13.0)
        parts = detailed_components("neutral")
        self.assertEqual(sum(part.bom_key == "JFT8R" for part in parts), 6)
        self.assertFalse(any(part.bom_key == "UH_BRACKET_STACK" for part in parts))

    def test_full_corner_sweep_fits_length_and_articulation_windows(self):
        result = kinematic_screen()
        self.assertTrue(result["length_window_pass"])
        self.assertTrue(result["articulation_pass"])
        self.assertGreater(result["minimum_pin_center_length_mm"], 265.0)
        self.assertLess(result["maximum_pin_center_length_mm"], 415.0)
        self.assertLess(
            result["required_articulation_with_margin_deg"],
            N.rod_end_allowable_angle_deg,
        )

    def test_local_pin_lug_and_catalog_breaking_load_screen_passes(self):
        result = local_strength_screen()
        self.assertTrue(result["preliminary_pass"])
        self.assertGreater(result["yoke_clearance_mm"], 5.0)
        self.assertGreater(result["catalog_breaking_load_margin"], 4.0)

    def test_actuator_envelopes_clear_both_frames_in_z_poses(self):
        collisions = []
        for pose_name in NAVIMRO_POSES:
            parts = detailed_components(pose_name)
            actuators = [
                part
                for part in parts
                if part.name.startswith("LA2000_A2_PROVISIONAL_")
            ]
            structure = [
                part
                for part in parts
                if part.group in ("01_LOWER_FRAME", "05_UPPER_FRAME")
            ]
            for actuator in actuators:
                for frame_part in structure:
                    if not _bounding_boxes_overlap(actuator, frame_part):
                        continue
                    volume = _shape(actuator).intersect(_shape(frame_part)).Volume()
                    if volume > 0.01:
                        collisions.append(
                            (pose_name, actuator.name, frame_part.name, volume)
                        )
        self.assertEqual(collisions, [])

    def test_pin_passes_real_bores_without_solid_overlap(self):
        parts = detailed_components("neutral")
        by_name = {part.name: part for part in parts}
        collisions = []
        for index in range(1, 4):
            for end in ("LOWER", "UPPER"):
                pin = by_name[f"ACT{index}_{end}_pin"]
                mates = [
                    by_name[f"ACT{index}_{end}_JFT8R"],
                    by_name[f"ACT{index}_{end}_yoke_lug_A"],
                    by_name[f"ACT{index}_{end}_yoke_lug_B"],
                    by_name[f"ACT{index}_{end}_spacer_pair"],
                ]
                for mate in mates:
                    volume = _shape(pin).intersect(_shape(mate)).Volume()
                    if volume > 0.01:
                        collisions.append((pin.name, mate.name, volume))
        self.assertEqual(collisions, [])

    def test_disconnected_detailed_module_is_300_mm_high(self):
        parts = [
            part
            for part in detailed_components("collapsed")
            if part.group != "08_CART_COUPLING"
        ]
        boxes = [_shape(part).BoundingBox() for part in parts]
        height = max(box.zmax for box in boxes) - min(box.zmin for box in boxes)
        self.assertAlmostEqual(height, 300.0, places=3)


if __name__ == "__main__":
    unittest.main()
