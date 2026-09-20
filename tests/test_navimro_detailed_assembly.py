import unittest
from collections import Counter

from cad.navimro_detailed_assembly import GROUP_OFFSETS, detailed_components
from cad.navimro_fabrication_exports import FLATBAR_PARTS
from cad.navimro_fabrication_parameters import N


class NavimroDetailedAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts = detailed_components("neutral")

    def test_component_tree_is_unique_and_bolt_level(self):
        names = [part.name for part in self.parts]
        self.assertEqual(len(names), len(set(names)))
        self.assertGreaterEqual(len(names), 450)

    def test_all_eight_groups_are_populated(self):
        self.assertEqual({part.group for part in self.parts}, set(GROUP_OFFSETS))

    def test_fastener_families_are_explicit(self):
        keys = Counter(part.bom_key for part in self.parts)
        for key in ("M8_SOCKET_SCREW", "M8_WASHER", "M8_TNUT", "M8_NYLOC", "M6_SOCKET_SCREW", "M4_SOCKET_SCREW"):
            self.assertGreater(keys[key], 0, key)

    def test_guide_riser_cut_list_matches_detailed_cad(self):
        riser = next(part for part in FLATBAR_PARTS if part.part_no == "NVR-P06")
        self.assertEqual((riser.length_mm, riser.quantity), (200.0, 2))
        modeled = [part for part in self.parts if part.bom_key == "NVR-P06"]
        self.assertEqual(len(modeled), 2)

    def test_rev_e_guide_and_cardan_cut_quantities_match(self):
        cuts = {part.part_no: (part.length_mm, part.quantity) for part in FLATBAR_PARTS}
        self.assertEqual(cuts["NVR-P07A"], (22.0, 2))
        self.assertEqual(cuts["NVR-P07B"], (24.0, 2))
        self.assertEqual(cuts["NVR-P08A"], (100.0, 1))
        self.assertEqual(cuts["NVR-P08B"], (100.0, 2))
        self.assertEqual(cuts["NVR-P08C"], (100.0, 1))
        self.assertEqual(cuts["NVR-P14"], (50.0, 4))

    def test_a2_planning_envelope_is_explicit(self):
        self.assertEqual((N.actuator_min_pin_length_mm, N.actuator_max_pin_length_mm), (265.0, 415.0))
        self.assertEqual(sum(part.bom_key == "LA2000_125150" for part in self.parts), 3)

    def test_every_shape_is_valid(self):
        invalid = []
        for part in self.parts:
            shape = part.shape.val() if hasattr(part.shape, "val") else part.shape
            if not shape.isValid():
                invalid.append(part.name)
        self.assertEqual(invalid, [])


if __name__ == "__main__":
    unittest.main()
