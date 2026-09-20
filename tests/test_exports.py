import unittest
import hashlib
from pathlib import Path

import cadquery as cq
import ezdxf

from cad.parameters import ROOT


class ExportTests(unittest.TestCase):
    def test_required_exports_exist_and_are_nonempty(self):
        required = [
            ROOT / "outputs/cad/step/leveling_module_neutral.step",
            ROOT / "outputs/cad/step/leveling_module_max_pitch_roll.step",
            ROOT / "outputs/cad/step/guide_gimbal_neutral.step",
            ROOT / "outputs/cad/step/guide_gimbal_max_pitch_roll.step",
            ROOT / "outputs/cad/step/radial_actuator_joint_packages_neutral.step",
            ROOT / "outputs/cad/step/ls01_actuator_limit_package_neutral.step",
            ROOT / "outputs/cad/step/jnt_cg01_factory_clevis_gimbal_seed.step",
            ROOT / "outputs/cad/step/navimro_pin_lug_gimbal_assumption.step",
            ROOT / "outputs/cad/stl/imu_bracket.stl",
            ROOT / "outputs/cad/stl/cable_guide.stl",
            ROOT / "outputs/cad/dxf/lower_interface_plate_profile.dxf",
            ROOT / "outputs/cad/dxf/upper_acrylic_panel_profile.dxf",
            ROOT / "outputs/cad/glb/leveling_module_neutral.glb",
            ROOT / "outputs/renders/phase2_neutral.png",
            ROOT / "outputs/renders/phase2_diagonal_layout.png",
            ROOT / "outputs/renders/phase2_gimbal_detail.png",
            ROOT / "outputs/renders/phase2_gimbal_limit.png",
            ROOT / "outputs/renders/phase2_radial_tripod_detail.png",
            ROOT / "outputs/renders/phase2_actuator_joint_detail.png",
            ROOT / "outputs/renders/phase2_actuator_limit_detail.png",
            ROOT / "outputs/renders/phase2_actuator_limit_end_view.png",
            ROOT / "outputs/renders/vendor_firgelli_step_side.png",
            ROOT / "outputs/renders/vendor_firgelli_step_front.png",
            ROOT / "outputs/renders/jnt_cg01_factory_clevis_gimbal.png",
            ROOT / "outputs/renders/navimro_pin_lug_gimbal_assumption.png",
            ROOT / "outputs/renders/phase2_internal_top_off.png",
            ROOT / "outputs/renders/phase2_assembly_front.png",
            ROOT / "outputs/renders/phase2_assembly_side.png",
            ROOT / "outputs/renders/phase2_assembly_top.png",
            ROOT / "outputs/renders/phase2_exploded.png",
            ROOT / "outputs/renders/phase2_annotated_assembly.png",
            ROOT / "outputs/phase2/phase2_engineering_report.md",
            ROOT / "outputs/phase2/diagonal_design_decision.md",
            ROOT / "outputs/phase2/phase2_bom.csv",
        ]
        for path in required:
            self.assertTrue(path.is_file(), str(path))
            self.assertGreater(path.stat().st_size, 100, str(path))

    def test_neutral_step_round_trip(self):
        path = ROOT / "outputs/cad/step/leveling_module_neutral.step"
        model = cq.importers.importStep(str(path))
        self.assertTrue(model.val().isValid())
        box = model.val().BoundingBox()
        self.assertGreater(box.xlen, 850)
        self.assertGreater(box.ylen, 750)
        self.assertGreater(box.zlen, 300)

    def test_dxf_and_glb_signatures(self):
        doc = ezdxf.readfile(ROOT / "outputs/cad/dxf/upper_acrylic_panel_profile.dxf")
        self.assertGreater(len(list(doc.modelspace())), 20)
        inner_profiles = [
            entity for entity in doc.modelspace()
            if entity.dxf.layer == "CUT_INNER" and entity.dxftype() == "LWPOLYLINE"
        ]
        self.assertEqual(len(inner_profiles), 0)
        with (ROOT / "outputs/cad/glb/leveling_module_neutral.glb").open("rb") as handle:
            self.assertEqual(handle.read(4), b"glTF")

    def test_vendor_step_integrity(self):
        expected = {
            "F-SD-H-450-12v-8in.stp": "54C6267D38D44EE6F9F9F247B51460A1983C2B19D89259968ECC6A103ADC8A34",
            "Bracket_Assembly_MB-21.stp": "CB0D8D22E77FF1A4FD0FBB7C60CC4301DA3282BE7FAB3E37FB79E7DA2A9BCCF0",
            "Bracket_Assembly_MB-20.stp": "7BE1541AF76A94C975FB3D6030CCED2991736463F716F90EDB7A9D6D6FB04538",
            "MB-17_Assembly.stp": "6FE08F3228442187239E2BC1E80A9FDA65A57F215AA1D27F311DB469B6A45197",
        }
        for filename, expected_digest in expected.items():
            path = ROOT / "references/vendor/firgelli" / filename
            self.assertTrue(path.is_file())
            digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
            self.assertEqual(digest, expected_digest)

        drawing = ROOT / "references/vendor/firgelli/F-SD-H-family-mounting-end-drawing-reference.pdf"
        self.assertTrue(drawing.is_file())
        self.assertEqual(
            hashlib.sha256(drawing.read_bytes()).hexdigest().upper(),
            "77AD4AA2E69FDC1A7573B641C8251930E8FBF0317A8782BDABD9999071E0BB05",
        )


if __name__ == "__main__":
    unittest.main()
