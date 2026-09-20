import unittest

from cad.navimro_fabrication_assembly import components_for_pose
from cad.navimro_fabrication_parameters import NAVIMRO_POSES
from scripts.build_navimro_assembly_manual import STEPS
from scripts.render_navimro_assembly_guide import STAGES, _group_index


class NavimroAssemblyGuideTests(unittest.TestCase):
    def test_manual_has_one_page_for_each_assembly_stage(self):
        self.assertEqual(len(STAGES), 8)
        self.assertEqual(len(STEPS), len(STAGES))

    def test_every_cad_component_is_assigned_to_an_assembly_stage(self):
        components = components_for_pose(NAVIMRO_POSES["neutral"])
        assigned = [_group_index(component.name) for component in components]
        self.assertEqual(len(assigned), len(components))
        self.assertEqual(set(assigned), set(range(8)))

    def test_vendor_variant_is_not_claimed_by_the_cad_envelope_name(self):
        names = [component.name for component in components_for_pose(NAVIMRO_POSES["neutral"])]
        self.assertFalse(any("DHLA2000_A1_envelope" in name for name in names))


if __name__ == "__main__":
    unittest.main()
