import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FAB = ROOT / "fabrication" / "profile_radial_revE_release_candidate_2026-09-04"
RELEASE = ROOT / "outputs" / "profile_radial_revE_poc_release_candidate"


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class RevEPocReleaseCandidateTests(unittest.TestCase):
    def test_nine_unique_fabrication_dxfs_exist(self):
        self.assertEqual(9, len(list(FAB.glob("*.dxf"))))

    def test_a3_profile_holes_have_100_mm_pitch(self):
        rows = read_csv(FAB / "RevE_custom_part_hole_table.csv")
        x_values = sorted(
            float(row["x_mm"])
            for row in rows
            if row["part_id"] == "C03"
            and row["note"] == "M8 profile clearance"
        )
        self.assertEqual(2, len(x_values))
        self.assertAlmostEqual(100.0, x_values[1] - x_values[0], places=6)

    def test_candidate_bom_has_driver_input_fusing(self):
        path = (
            RELEASE
            / "procurement"
            / "Profile_Radial_3RPS_RevE_PoC_candidate_BOM_2026-09-04.csv"
        )
        rows = read_csv(path)
        by_id = {row["bom_id"]: row for row in rows}
        self.assertEqual(61, len(rows))
        self.assertEqual("6", by_id["E09A"]["order_qty"])
        self.assertEqual("3", by_id["E09D"]["order_qty"])
        self.assertIn("10 A", by_id["E09D"]["specification"])

    def test_candidate_bom_known_subtotal_is_below_budget(self):
        path = (
            RELEASE
            / "procurement"
            / "Profile_Radial_3RPS_RevE_PoC_candidate_BOM_2026-09-04.csv"
        )
        rows = read_csv(path)
        subtotal = sum(int(row["extended_price_krw_screen"] or 0) for row in rows)
        self.assertEqual(1_278_437, subtotal)
        self.assertLess(subtotal, 4_000_000)

    def test_enclosure_layout_passes_digital_envelope(self):
        data = json.loads(
            (RELEASE / "electrical" / "RevE_enclosure_layout_validation.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(data["passes_layout_envelope"])
        self.assertGreaterEqual(data["ac_to_logic_planar_segregation_mm"], 50)
        self.assertEqual([], data["component_overlap_pairs"])
        self.assertFalse(data["mounting_release"])

    def test_electrical_tables_exist(self):
        expected = {
            "RevE_enclosure_layout.csv",
            "RevE_harness_schedule.csv",
            "RevE_io_map.csv",
            "RevE_point_to_point_wiring.csv",
            "RevE_terminal_map.csv",
        }
        self.assertTrue(expected <= {path.name for path in (RELEASE / "electrical").glob("*.csv")})

    def test_firmware_contains_fixed_pin_map_and_commands(self):
        source = (
            ROOT
            / "firmware"
            / "reve_leveling_controller"
            / "reve_leveling_controller.ino"
        ).read_text(encoding="utf-8")
        for text in (
            "ENC_A[AXES] = {2, 3, 18}",
            "ENC_B[AXES] = {22, 23, 24}",
            "MOTOR_PWM[AXES] = {5, 6, 7}",
            "MOTOR_DIR[AXES] = {30, 31, 32}",
            '"STATUS"',
            '"HOME"',
            '"JOG"',
            '"LIFT"',
            '"LEVEL"',
            '"STOP"',
            '"ZERO_IMU"',
            '"SAVE_CAL"',
        ):
            self.assertIn(text, source)
        self.assertEqual(source.count("{"), source.count("}"))

    def test_release_audit_is_digital_pass_but_not_physical_release(self):
        data = json.loads(
            (ROOT / "verification" / "RevE_PoC_release_candidate_audit_2026-09-04.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(data["digital_package_pass"])
        self.assertFalse(data["physical_tests_executed"])
        self.assertFalse(data["purchase_release"])
        self.assertFalse(data["fabrication_release"])
        self.assertFalse(data["power_release"])
        self.assertFalse(data["poc_acceptance"])

    def test_firmware_compiled_for_mega2560(self):
        build = RELEASE / "firmware_build"
        self.assertTrue((build / "compile_record.txt").exists())
        self.assertTrue(list(build.glob("*.hex")))

    def test_both_pdfs_are_nonempty(self):
        paths = (
            ROOT
            / "output"
            / "pdf"
            / "Profile_Radial_3RPS_RevE_Fabrication_Drawings_RC_2026-09-04.pdf",
            ROOT
            / "output"
            / "pdf"
            / "Profile_Radial_3RPS_RevE_Electrical_Drawings_RC_2026-09-04.pdf",
        )
        for path in paths:
            self.assertGreater(path.stat().st_size, 4_000)


if __name__ == "__main__":
    unittest.main()
