import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ApprovedWorkspaceTests(unittest.TestCase):
    def test_direct_script_entrypoint_resolves_project_imports(self):
        root = Path(__file__).resolve().parents[1]
        completed = subprocess.run(
            [sys.executable, str(root / "calculations" / "reve_approved_workspace.py")],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('"release_ready": false', completed.stdout)

    def test_approved_grid_stays_inside_physical_and_software_limits(self):
        from calculations.reve_approved_workspace import software_window_audit

        result = software_window_audit()
        self.assertEqual(result["pose_count"], 27)
        self.assertGreaterEqual(result["minimum_pin_mm"], 210.0)
        self.assertLessEqual(result["maximum_pin_mm"], 280.0)
        self.assertTrue(result["passes"])

    def test_nominal_switch_values_do_not_create_release(self):
        from calculations.reve_approved_workspace import software_window_audit

        result = software_window_audit()
        self.assertEqual(result["relative_software_window_mm"], [5.0, 75.0])
        self.assertAlmostEqual(result["z0_offset_from_low_switch_mm"], 19.2075)
        self.assertEqual(result["input_status"], "NOMINAL_UNVERIFIED")
        self.assertFalse(result["release_ready"])

    def test_dense_grid_and_segment_sampling_have_declared_spacing(self):
        from calculations.reve_approved_workspace import (
            dense_pose_grid,
            sample_pose_segment,
        )

        self.assertEqual(len(dense_pose_grid()), 11 * 13 * 13)
        samples = sample_pose_segment(
            (0.0, -3.0, -3.0),
            (5.0, -2.5, -2.5),
        )
        self.assertEqual(len(samples), 6)
        self.assertEqual(samples[0], (0.0, -3.0, -3.0))
        self.assertEqual(samples[-1], (5.0, -2.5, -2.5))
        for first, second in zip(samples, samples[1:]):
            self.assertLessEqual(abs(second[0] - first[0]), 1.0 + 1e-12)
            self.assertLessEqual(abs(second[1] - first[1]), 0.1 + 1e-12)
            self.assertLessEqual(abs(second[2] - first[2]), 0.1 + 1e-12)

    def test_actuator_speed_margin_for_acceptance_vector_rate(self):
        from calculations.reve_approved_workspace import speed_screen

        result = speed_screen(
            pitch_rate_deg_s=2 ** -0.5,
            roll_rate_deg_s=2 ** -0.5,
        )
        self.assertLessEqual(result["angular_rate_vector_deg_s"], 1.0 + 1e-9)
        self.assertLessEqual(result["maximum_required_mm_s"], 3.8)
        self.assertEqual(result["screen_kind"], "ACCEPTANCE")

    def test_each_axis_one_degree_per_second_is_stress_screen_only(self):
        from calculations.reve_approved_workspace import speed_screen

        result = speed_screen(pitch_rate_deg_s=1.0, roll_rate_deg_s=1.0)
        self.assertLessEqual(result["maximum_required_mm_s"], 5.2)
        self.assertEqual(result["screen_kind"], "STRESS_ONLY")

    def test_verification_json_keeps_unverified_supplier_gate_closed(self):
        from calculations.reve_approved_workspace import write_verification_json

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "workspace.json"
            payload = write_verification_json(destination)
            loaded = json.loads(destination.read_text(encoding="utf-8"))

        self.assertEqual(payload, loaded)
        self.assertEqual(loaded["approved_27_pose_audit"]["pose_count"], 27)
        self.assertEqual(loaded["dense_grid_audit"]["pose_count"], 1859)
        self.assertEqual(loaded["dense_grid_audit"]["claim"], "FINITE_GRID_SCREEN_ONLY")
        self.assertIn("acceptance_vector_rate", loaded["speed_screens"])
        self.assertFalse(loaded["release_ready"])


if __name__ == "__main__":
    unittest.main()
